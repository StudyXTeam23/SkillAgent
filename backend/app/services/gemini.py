"""
Google Gemini API 服务封装

提供统一的 LLM API 调用接口，支持：
- 文本生成
- JSON 格式化输出
- 错误处理和重试
- Token 限制
"""
import logging
import json
import time
from typing import Optional, Dict, Any, List
from google import genai
from google.genai import types

from ..config import settings

logger = logging.getLogger(__name__)


class GeminiClient:
    """Gemini API 客户端封装（使用最新 SDK）"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 Gemini 客户端
        
        Args:
            api_key: Gemini API Key，如果不提供则从 settings 读取
        """
        self.api_key = api_key or settings.GEMINI_API_KEY
        
        # 创建客户端（使用最新 SDK）
        self.client = genai.Client(api_key=self.api_key)
        self.async_client = self.client.aio
        
        logger.info("✅ Gemini client initialized with new SDK")
    
    async def generate(
        self,
        prompt: str,
        model: str = "gemini-2.0-flash-exp",  # 使用可用的模型
        response_format: str = "text",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        max_retries: int = 3
    ) -> str:
        """
        生成文本内容（异步）
        
        Args:
            prompt: 提示词
            model: 模型名称，默认 gemini-1.5-flash
            response_format: 响应格式，"text" 或 "json"
            max_tokens: 最大 token 数
            temperature: 温度参数（0-1），越高越随机
            max_retries: 最大重试次数
        
        Returns:
            str: 生成的文本或 JSON 字符串
        
        Raises:
            Exception: API 调用失败
        """
        # 如果请求 JSON 格式，在 prompt 中明确说明
        if response_format == "json":
            prompt = self._enhance_json_prompt(prompt)
        
        # 配置生成参数
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        
        # 重试逻辑
        for attempt in range(max_retries):
            try:
                logger.info(f"🤖 Calling Gemini API: model={model}, tokens<={max_tokens}")
                start_time = time.time()
                
                # 使用异步客户端调用 API
                response = await self.async_client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=config
                )
                
                # 检查响应
                if not response.text:
                    raise ValueError("Empty response from Gemini API")
                
                result = response.text.strip()
                elapsed = time.time() - start_time
                
                # ============= Token 使用统计 =============
                usage_metadata = getattr(response, 'usage_metadata', None)
                if usage_metadata:
                    input_tokens = getattr(usage_metadata, 'prompt_token_count', 0)
                    output_tokens = getattr(usage_metadata, 'candidates_token_count', 0)
                    total_tokens = getattr(usage_metadata, 'total_token_count', 0)
                    
                    logger.info(
                        f"📊 Token Usage | Input: {input_tokens:,} | Output: {output_tokens:,} | "
                        f"Total: {total_tokens:,} | Time: {elapsed:.2f}s | Model: {model}"
                    )
                else:
                    logger.info(f"✅ Gemini response received in {elapsed:.2f}s, length={len(result)}")
                
                # 如果是 JSON 格式，尝试解析验证
                if response_format == "json":
                    result = self._extract_json(result)
                    try:
                        # 验证是否为有效 JSON
                        json.loads(result)
                        return result
                    except json.JSONDecodeError as json_err:
                        # JSON解析失败，尝试修复
                        if attempt == max_retries - 1:
                            logger.warning(f"⚠️ JSON parsing failed, attempting to fix...")
                            try:
                                fixed_result = self._try_fix_json(result)
                                json.loads(fixed_result)
                                logger.info(f"✅ JSON auto-fixed successfully")
                                return fixed_result
                            except:
                                logger.error(f"❌ Failed to fix JSON")
                                raise ValueError(f"Invalid JSON response: {str(json_err)}")
                        else:
                            raise json_err
                
                return result
                
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ JSON parsing failed (attempt {attempt + 1}/{max_retries}): {e}")
                logger.debug(f"Raw result (last 200 chars): ...{result[-200:]}")
                if attempt == max_retries - 1:
                    logger.error("❌ Failed to parse JSON after all retries")
                    raise ValueError(f"Invalid JSON response: {str(e)}")
                time.sleep(2 * (attempt + 1))  # 指数退避
                
            except Exception as e:
                logger.error(f"❌ Gemini API error (attempt {attempt + 1}/{max_retries}): {type(e).__name__}: {e}")
                if attempt == max_retries - 1:
                    raise
                
                # 指数退避
                wait_time = 2 ** attempt
                logger.info(f"⏳ Retrying in {wait_time}s...")
                time.sleep(wait_time)
        
        raise Exception("Failed to generate content after all retries")
    
    def _enhance_json_prompt(self, prompt: str) -> str:
        """
        增强 prompt 以获得 JSON 格式输出
        
        Args:
            prompt: 原始 prompt
        
        Returns:
            str: 增强后的 prompt
        """
        if "JSON" in prompt.upper() or "json" in prompt:
            # 已经包含 JSON 指示
            return prompt
        
        return f"""{prompt}

IMPORTANT: You must respond with valid JSON only. Do not include any text before or after the JSON object.
Example format: {{"key": "value"}}

Your JSON response:"""
    
    def _try_fix_json(self, text: str) -> str:
        """
        尝试修复常见的 JSON 错误
        """
        import re
        
        # 移除可能的 markdown 代码块
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        # 尝试移除 JSON 中的注释（// 和 /* */）
        # 移除单行注释
        text = re.sub(r'//[^\n]*\n', '\n', text)
        # 移除多行注释
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        
        # 移除尾随逗号（JSON 中最常见的错误）
        # 1. 对象中的尾随逗号: , }
        text = re.sub(r',(\s*})', r'\1', text)
        # 2. 数组中的尾随逗号: , ]
        text = re.sub(r',(\s*\])', r'\1', text)
        
        # 修复单引号为双引号（如果有的话）
        # 但要小心不要改变字符串内部的单引号
        # 简单策略：只替换键名的单引号
        text = re.sub(r"'([^']*)'(\s*):", r'"\1"\2:', text)
        
        # 尝试找到最后一个完整的 JSON 对象或数组
        # 从后往前找最后一个 } 或 ]
        last_brace = text.rfind('}')
        last_bracket = text.rfind(']')
        
        if last_brace > last_bracket:
            # 对象
            text = text[:last_brace + 1]
        elif last_bracket > last_brace:
            # 数组
            text = text[:last_bracket + 1]
        
        return text
    
    def _extract_json(self, text: str) -> str:
        """
        从文本中提取 JSON 内容（改进版，处理多余内容）
        
        Args:
            text: 可能包含 JSON 的文本
        
        Returns:
            str: 提取的 JSON 字符串
        """
        text = text.strip()
        
        # 移除可能的 markdown 代码块标记
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        text = text.strip()
        
        # 尝试找到完整的 JSON 对象或数组
        # 使用简单的括号匹配来找到完整的 JSON
        
        # 优先检查对象
        if "{" in text:
            start = text.find("{")
            depth = 0
            in_string = False
            escape_next = False
            
            for i in range(start, len(text)):
                char = text[i]
                
                # 处理字符串中的引号
                if char == '"' and not escape_next:
                    in_string = not in_string
                elif char == '\\' and not escape_next:
                    escape_next = True
                    continue
                
                if not in_string:
                    if char == '{':
                        depth += 1
                    elif char == '}':
                        depth -= 1
                        if depth == 0:
                            # 找到完整的 JSON 对象
                            return text[start:i+1]
                
                escape_next = False
        
        # 如果没有找到对象，检查数组
        if "[" in text:
            start = text.find("[")
            depth = 0
            in_string = False
            escape_next = False
            
            for i in range(start, len(text)):
                char = text[i]
                
                if char == '"' and not escape_next:
                    in_string = not in_string
                elif char == '\\' and not escape_next:
                    escape_next = True
                    continue
                
                if not in_string:
                    if char == '[':
                        depth += 1
                    elif char == ']':
                        depth -= 1
                        if depth == 0:
                            # 找到完整的 JSON 数组
                            return text[start:i+1]
                
                escape_next = False
        
        # 如果都没找到，返回原始文本
        return text
    
    async def generate_json(
        self,
        prompt: str,
        model: str = "gemini-2.0-flash-exp",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        max_retries: int = 3
    ) -> str:
        """
        生成 JSON 格式内容（快捷方法）
        
        Args:
            prompt: 提示词
            model: 模型名称
            max_tokens: 最大 token 数
            temperature: 温度参数
            max_retries: 最大重试次数
        
        Returns:
            str: JSON 字符串
        """
        return await self.generate(
            prompt=prompt,
            model=model,
            response_format="json",
            max_tokens=max_tokens,
            temperature=temperature,
            max_retries=max_retries
        )
    
    async def generate_batch(
        self,
        prompts: List[str],
        model: str = "gemini-2.0-flash-exp",
        **kwargs
    ) -> List[str]:
        """
        批量生成（串行执行）
        
        Args:
            prompts: prompt 列表
            model: 模型名称
            **kwargs: 其他参数
        
        Returns:
            List[str]: 生成结果列表
        """
        results = []
        for i, prompt in enumerate(prompts):
            logger.info(f"📝 Processing batch {i + 1}/{len(prompts)}")
            result = await self.generate(prompt, model=model, **kwargs)
            results.append(result)
        
        return results
    
    def get_model_info(self, model_name: str = "gemini-2.0-flash-exp") -> Dict[str, Any]:
        """
        获取模型信息
        
        Args:
            model_name: 模型名称
        
        Returns:
            Dict: 模型信息
        """
        try:
            # 使用新 SDK 的方式
            return {
                "name": model_name,
                "status": "available",
                "note": "Using new google.genai SDK"
            }
        except Exception as e:
            logger.error(f"❌ Failed to get model info: {e}")
            return {"error": str(e)}
    
    async def close(self):
        """关闭异步客户端"""
        try:
            if hasattr(self, 'async_client') and hasattr(self.async_client, 'aclose'):
                await self.async_client.aclose()
                logger.info("✅ Async client closed")
            else:
                logger.info("ℹ️  Async client does not require explicit close")
        except Exception as e:
            logger.warning(f"⚠️ Error closing async client: {e}")
