"""
Task 2.1 测试 - Intent Router 核心逻辑测试

测试内容：
1. IntentRouter 初始化
2. Prompt 模板加载
3. 意图识别功能（使用 mock）
4. 置信度阈值逻辑
5. 错误处理
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

from app.core.intent_router import IntentRouter
from app.models.intent import IntentResult, MemorySummary


class TestIntentRouterInitialization:
    """测试 IntentRouter 初始化"""
    
    def test_router_initialization(self):
        """测试路由器初始化"""
        router = IntentRouter()
        
        assert router is not None
        assert router.gemini_client is not None
        assert router.prompt_template is not None
        assert len(router.prompt_template) > 0
    
    def test_prompt_template_loaded(self):
        """测试 prompt 模板加载"""
        router = IntentRouter()
        
        # 验证模板包含必要的占位符
        assert "{message}" in router.prompt_template
        assert "{topic_hint}" in router.prompt_template
        assert "{recent_behavior}" in router.prompt_template
        
        # 验证模板包含关键说明
        assert "INTENT" in router.prompt_template.upper()
        assert "JSON" in router.prompt_template.upper()
    
    def test_confidence_threshold_constant(self):
        """测试置信度阈值常量"""
        assert IntentRouter.CONFIDENCE_THRESHOLD == 0.6


class TestPromptFormatting:
    """测试 Prompt 格式化"""
    
    def test_format_prompt_without_memory(self):
        """测试无记忆摘要的 prompt 格式化"""
        router = IntentRouter()
        
        formatted = router._format_prompt("给我几道练习题")
        
        assert "给我几道练习题" in formatted
        assert "None" in formatted  # 默认值
    
    def test_format_prompt_with_memory(self):
        """测试带记忆摘要的 prompt 格式化"""
        router = IntentRouter()
        
        memory = MemorySummary(
            topic_hint="微积分-极限",
            user_mastery_hint="weak",
            recent_behavior="用户刚做过练习题"
        )
        
        formatted = router._format_prompt("再来几道", memory)
        
        assert "再来几道" in formatted
        assert "微积分-极限" in formatted
        assert "用户刚做过练习题" in formatted


class TestIntentParsing:
    """测试意图识别（使用 mock）"""
    
    @pytest.mark.asyncio
    async def test_parse_quiz_intent(self):
        """测试识别 quiz 意图"""
        router = IntentRouter()
        
        # Mock Gemini API 响应
        with patch.object(router.gemini_client, 'generate', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = '''{
                "intent": "quiz",
                "topic": "微积分-极限",
                "target_artifact": "quiz_set",
                "confidence": 0.92
            }'''
            
            result = await router.parse("给我几道微积分极限的练习题")
            
            assert isinstance(result, IntentResult)
            assert result.intent == "quiz"
            assert result.topic == "微积分-极限"
            assert result.target_artifact == "quiz_set"
            assert result.confidence == 0.92
            assert result.raw_text == "给我几道微积分极限的练习题"
    
    @pytest.mark.asyncio
    async def test_parse_explain_intent(self):
        """测试识别 explain 意图"""
        router = IntentRouter()
        
        with patch.object(router.gemini_client, 'generate', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = '''{
                "intent": "explain",
                "topic": "微积分-导数",
                "target_artifact": "explanation",
                "confidence": 0.88
            }'''
            
            result = await router.parse("解释一下什么是导数")
            
            assert result.intent == "explain"
            assert result.topic == "微积分-导数"
            assert result.target_artifact == "explanation"
            assert result.confidence == 0.88
    
    @pytest.mark.asyncio
    async def test_parse_other_intent(self):
        """测试识别 other 意图"""
        router = IntentRouter()
        
        with patch.object(router.gemini_client, 'generate', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = '''{
                "intent": "other",
                "topic": null,
                "target_artifact": null,
                "confidence": 0.85
            }'''
            
            result = await router.parse("你好")
            
            assert result.intent == "other"
            assert result.topic is None
            assert result.target_artifact is None


class TestConfidenceThreshold:
    """测试置信度阈值逻辑"""
    
    @pytest.mark.asyncio
    async def test_low_confidence_fallback_to_other(self):
        """测试低置信度回退到 other"""
        router = IntentRouter()
        
        with patch.object(router.gemini_client, 'generate', new_callable=AsyncMock) as mock_generate:
            # 返回低置信度的 quiz 意图
            mock_generate.return_value = '''{
                "intent": "quiz",
                "topic": "physics",
                "target_artifact": "quiz_set",
                "confidence": 0.45
            }'''
            
            result = await router.parse("不太清楚的消息")
            
            # 应该回退到 other，且 target_artifact 为 None
            assert result.intent == "other"
            assert result.target_artifact is None
            assert result.confidence == 0.45  # 保留原始置信度
    
    @pytest.mark.asyncio
    async def test_high_confidence_accepted(self):
        """测试高置信度被接受"""
        router = IntentRouter()
        
        with patch.object(router.gemini_client, 'generate', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = '''{
                "intent": "quiz",
                "topic": "math",
                "target_artifact": "quiz_set",
                "confidence": 0.85
            }'''
            
            result = await router.parse("给我数学题")
            
            # 高置信度应该保持原意图
            assert result.intent == "quiz"
            assert result.target_artifact == "quiz_set"
            assert result.confidence == 0.85
    
    @pytest.mark.asyncio
    async def test_threshold_boundary(self):
        """测试阈值边界情况"""
        router = IntentRouter()
        
        with patch.object(router.gemini_client, 'generate', new_callable=AsyncMock) as mock_generate:
            # 刚好等于阈值 0.6
            mock_generate.return_value = '''{
                "intent": "explain",
                "topic": "test",
                "target_artifact": "explanation",
                "confidence": 0.6
            }'''
            
            result = await router.parse("边界测试")
            
            # 等于阈值应该被接受
            assert result.intent == "explain"
            assert result.confidence == 0.6


class TestErrorHandling:
    """测试错误处理"""
    
    @pytest.mark.asyncio
    async def test_invalid_json_response(self):
        """测试 JSON 解析错误"""
        router = IntentRouter()
        
        with patch.object(router.gemini_client, 'generate', new_callable=AsyncMock) as mock_generate:
            # 返回无效 JSON
            mock_generate.return_value = "This is not JSON"
            
            result = await router.parse("测试消息")
            
            # 应该返回默认的 other 意图
            assert result.intent == "other"
            assert result.confidence == 0.0
            assert result.topic is None
    
    @pytest.mark.asyncio
    async def test_missing_fields_in_response(self):
        """测试响应缺少字段"""
        router = IntentRouter()
        
        with patch.object(router.gemini_client, 'generate', new_callable=AsyncMock) as mock_generate:
            # 返回不完整的 JSON（缺少 confidence，会使用默认值 0.5）
            mock_generate.return_value = '{"intent": "quiz"}'
            
            result = await router.parse("测试消息")
            
            # 默认置信度 0.5 < 0.6 阈值，应该回退到 "other"
            assert result.intent == "other"
            assert result.confidence == 0.5  # 保留原始默认值
            assert result.target_artifact is None  # 低置信度时清除 artifact
    
    @pytest.mark.asyncio
    async def test_api_failure(self):
        """测试 API 调用失败"""
        router = IntentRouter()
        
        with patch.object(router.gemini_client, 'generate', new_callable=AsyncMock) as mock_generate:
            mock_generate.side_effect = Exception("API Error")
            
            with pytest.raises(Exception) as exc_info:
                await router.parse("测试消息")
            
            assert "API Error" in str(exc_info.value)


class TestParseWithMemory:
    """测试带记忆摘要的解析"""
    
    @pytest.mark.asyncio
    async def test_parse_with_memory_context(self):
        """测试使用记忆上下文进行解析"""
        router = IntentRouter()
        
        memory = MemorySummary(
            topic_hint="微积分-极限",
            user_mastery_hint="weak",
            recent_behavior="刚做过极限练习"
        )
        
        with patch.object(router.gemini_client, 'generate', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = '''{
                "intent": "quiz",
                "topic": "微积分-极限",
                "target_artifact": "quiz_set",
                "confidence": 0.90
            }'''
            
            result = await router.parse("再来几道", memory)
            
            # 验证 generate 被调用时包含了记忆信息
            call_args = mock_generate.call_args
            prompt_used = call_args[1]['prompt']
            
            assert "微积分-极限" in prompt_used
            assert "刚做过极限练习" in prompt_used
            
            assert result.intent == "quiz"
            assert result.topic == "微积分-极限"


class TestBatchParsing:
    """测试批量解析"""
    
    @pytest.mark.asyncio
    async def test_parse_batch(self):
        """测试批量解析多个消息"""
        router = IntentRouter()
        
        messages = [
            "给我几道练习题",
            "解释一下概念",
            "你好"
        ]
        
        with patch.object(router.gemini_client, 'generate', new_callable=AsyncMock) as mock_generate:
            # 为每个消息返回不同的响应
            mock_generate.side_effect = [
                '{"intent": "quiz", "topic": "math", "target_artifact": "quiz_set", "confidence": 0.9}',
                '{"intent": "explain", "topic": "physics", "target_artifact": "explanation", "confidence": 0.85}',
                '{"intent": "other", "topic": null, "target_artifact": null, "confidence": 0.8}'
            ]
            
            results = await router.parse_batch(messages)
            
            assert len(results) == 3
            assert results[0].intent == "quiz"
            assert results[1].intent == "explain"
            assert results[2].intent == "other"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

