"""
Task 1.3 测试 - 测试 Gemini API 服务

测试内容：
1. Gemini 客户端初始化
2. 文本生成
3. JSON 格式化输出
4. 错误处理
5. JSON 提取逻辑
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.gemini import GeminiClient


class TestGeminiClientInitialization:
    """测试 Gemini 客户端初始化"""
    
    def test_client_initialization_with_default_key(self):
        """测试使用默认 API Key 初始化"""
        client = GeminiClient()
        assert client is not None
        assert client.api_key is not None
    
    def test_client_initialization_with_custom_key(self):
        """测试使用自定义 API Key 初始化"""
        custom_key = "test_api_key_12345"
        client = GeminiClient(api_key=custom_key)
        assert client.api_key == custom_key


class TestJSONExtraction:
    """测试 JSON 提取逻辑"""
    
    def test_extract_json_from_plain_json(self):
        """测试从纯 JSON 文本提取"""
        client = GeminiClient()
        
        text = '{"key": "value", "number": 42}'
        result = client._extract_json(text)
        
        assert result == '{"key": "value", "number": 42}'
    
    def test_extract_json_from_markdown_code_block(self):
        """测试从 markdown 代码块提取 JSON"""
        client = GeminiClient()
        
        text = """```json
{"key": "value"}
```"""
        result = client._extract_json(text)
        
        assert '{"key": "value"}' in result
        assert "```" not in result
    
    def test_extract_json_with_surrounding_text(self):
        """测试从包含前后文本的内容中提取 JSON"""
        client = GeminiClient()
        
        text = """Here is the JSON response:
{"intent": "quiz", "confidence": 0.9}
That's the result."""
        
        result = client._extract_json(text)
        
        assert result == '{"intent": "quiz", "confidence": 0.9}'
    
    def test_extract_json_array(self):
        """测试提取 JSON 数组"""
        client = GeminiClient()
        
        text = '[{"id": 1}, {"id": 2}]'
        result = client._extract_json(text)
        
        assert result == '[{"id": 1}, {"id": 2}]'


class TestJSONPromptEnhancement:
    """测试 JSON prompt 增强"""
    
    def test_enhance_prompt_without_json_mention(self):
        """测试增强不包含 JSON 的 prompt"""
        client = GeminiClient()
        
        prompt = "Generate a quiz question"
        enhanced = client._enhance_json_prompt(prompt)
        
        assert "JSON" in enhanced
        assert "valid JSON only" in enhanced
        assert prompt in enhanced
    
    def test_dont_enhance_prompt_with_json_mention(self):
        """测试已包含 JSON 的 prompt 不被重复增强"""
        client = GeminiClient()
        
        prompt = "Generate JSON output: {}"
        enhanced = client._enhance_json_prompt(prompt)
        
        # 应该返回原始 prompt（已经包含 JSON 指示）
        assert enhanced == prompt


class TestGeminiAPIGeneration:
    """测试 Gemini API 生成功能（使用 mock）"""
    
    @pytest.mark.asyncio
    async def test_generate_text_success(self):
        """测试成功生成文本"""
        client = GeminiClient()
        
        # Mock Gemini API 响应
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            mock_instance = Mock()
            mock_response = Mock()
            mock_response.text = "This is a test response"
            mock_instance.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_instance
            
            result = await client.generate(
                prompt="Test prompt",
                model="gemini-2.5-flash",
                response_format="text"
            )
            
            assert result == "This is a test response"
            mock_instance.generate_content.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_json_success(self):
        """测试成功生成 JSON"""
        client = GeminiClient()
        
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            mock_instance = Mock()
            mock_response = Mock()
            mock_response.text = '{"intent": "quiz", "confidence": 0.9}'
            mock_instance.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_instance
            
            result = await client.generate(
                prompt="Test prompt",
                response_format="json"
            )
            
            # 验证返回的是有效 JSON 字符串
            import json
            parsed = json.loads(result)
            assert parsed["intent"] == "quiz"
            assert parsed["confidence"] == 0.9
    
    @pytest.mark.asyncio
    async def test_generate_with_retry_on_empty_response(self):
        """测试空响应时的重试逻辑"""
        client = GeminiClient()
        
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            mock_instance = Mock()
            mock_response_empty = Mock()
            mock_response_empty.text = ""
            mock_response_success = Mock()
            mock_response_success.text = "Success after retry"
            
            # 第一次调用返回空，第二次成功
            mock_instance.generate_content.side_effect = [
                mock_response_empty,
                mock_response_success
            ]
            mock_model_class.return_value = mock_instance
            
            with patch('time.sleep'):  # Mock sleep 加速测试
                result = await client.generate(
                    prompt="Test",
                    max_retries=2
                )
            
            assert result == "Success after retry"
            assert mock_instance.generate_content.call_count == 2
    
    @pytest.mark.asyncio
    async def test_generate_failure_after_max_retries(self):
        """测试达到最大重试次数后失败"""
        client = GeminiClient()
        
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            mock_instance = Mock()
            mock_instance.generate_content.side_effect = Exception("API Error")
            mock_model_class.return_value = mock_instance
            
            with patch('time.sleep'):
                with pytest.raises(Exception) as exc_info:
                    await client.generate(
                        prompt="Test",
                        max_retries=2
                    )
            
            assert "API Error" in str(exc_info.value) or "Failed to generate" in str(exc_info.value)


class TestGeminiBatchGeneration:
    """测试批量生成"""
    
    @pytest.mark.asyncio
    async def test_generate_batch(self):
        """测试批量生成功能"""
        client = GeminiClient()
        
        prompts = ["Prompt 1", "Prompt 2", "Prompt 3"]
        
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            mock_instance = Mock()
            
            # 为每个 prompt 返回不同的响应
            responses = [
                Mock(text="Response 1"),
                Mock(text="Response 2"),
                Mock(text="Response 3")
            ]
            mock_instance.generate_content.side_effect = responses
            mock_model_class.return_value = mock_instance
            
            results = await client.generate_batch(prompts)
            
            assert len(results) == 3
            assert results[0] == "Response 1"
            assert results[1] == "Response 2"
            assert results[2] == "Response 3"


class TestGeminiModelInfo:
    """测试模型信息获取"""
    
    def test_get_model_info(self):
        """测试获取模型信息"""
        client = GeminiClient()
        
        with patch('google.generativeai.get_model') as mock_get_model:
            mock_model = Mock()
            mock_model.name = "models/gemini-2.5-flash"
            mock_model.display_name = "Gemini 2.5 Flash"
            mock_model.description = "Fast model"
            mock_model.input_token_limit = 32000
            mock_model.output_token_limit = 8192
            mock_model.supported_generation_methods = ["generateContent"]
            
            mock_get_model.return_value = mock_model
            
            info = client.get_model_info("gemini-2.5-flash")
            
            assert info["name"] == "models/gemini-2.5-flash"
            assert info["display_name"] == "Gemini 2.5 Flash"
            assert info["input_token_limit"] == 32000


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

