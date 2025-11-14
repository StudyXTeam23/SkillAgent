"""
Task 2.2 测试 - Intent Router API 端点测试

测试内容：
1. POST /intent/parse 端点
2. 请求验证
3. 依赖注入
4. 错误处理
5. 健康检查
"""
import pytest
from unittest.mock import patch, AsyncMock

from app.models.intent import IntentResult, MemorySummary


class TestIntentParseEndpoint:
    """测试 /intent/parse 端点"""
    
    @pytest.mark.asyncio
    async def test_parse_intent_success(self, test_app):
        """测试成功解析意图"""
        # Mock IntentRouter.parse
        with patch('app.api.intent.IntentRouter') as MockRouter:
            mock_instance = MockRouter.return_value
            mock_instance.parse = AsyncMock(return_value=IntentResult(
                intent="quiz",
                topic="微积分-极限",
                target_artifact="quiz_set",
                confidence=0.92,
                raw_text="给我几道练习题"
            ))
            
            response = await test_app.post(
                "/intent/parse",
                json={
                    "message": "给我几道练习题"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert "result" in data
            assert data["result"]["intent"] == "quiz"
            assert data["result"]["topic"] == "微积分-极限"
            assert data["result"]["confidence"] == 0.92
    
    @pytest.mark.asyncio
    async def test_parse_intent_with_memory(self, test_app):
        """测试带记忆摘要的意图解析"""
        with patch('app.api.intent.IntentRouter') as MockRouter:
            mock_instance = MockRouter.return_value
            mock_instance.parse = AsyncMock(return_value=IntentResult(
                intent="quiz",
                topic="微积分-极限",
                target_artifact="quiz_set",
                confidence=0.95,
                raw_text="再来几道"
            ))
            
            response = await test_app.post(
                "/intent/parse",
                json={
                    "message": "再来几道",
                    "memory_summary": {
                        "topic_hint": "微积分-极限",
                        "user_mastery_hint": "weak",
                        "recent_behavior": "刚做过练习"
                    }
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["result"]["intent"] == "quiz"
            assert data["result"]["confidence"] == 0.95
            
            # 验证 parse 被调用时传入了 memory_summary
            mock_instance.parse.assert_called_once()
            call_args = mock_instance.parse.call_args
            assert call_args[1]["memory_summary"] is not None
    
    @pytest.mark.asyncio
    async def test_parse_explain_intent(self, test_app):
        """测试 explain 意图"""
        with patch('app.api.intent.IntentRouter') as MockRouter:
            mock_instance = MockRouter.return_value
            mock_instance.parse = AsyncMock(return_value=IntentResult(
                intent="explain",
                topic="微积分-导数",
                target_artifact="explanation",
                confidence=0.88,
                raw_text="解释一下导数"
            ))
            
            response = await test_app.post(
                "/intent/parse",
                json={
                    "message": "解释一下导数"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["result"]["intent"] == "explain"


class TestRequestValidation:
    """测试请求验证"""
    
    @pytest.mark.asyncio
    async def test_empty_message(self, test_app):
        """测试空消息"""
        response = await test_app.post(
            "/intent/parse",
            json={
                "message": ""
            }
        )
        
        # 应该返回 422 验证错误
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_missing_message(self, test_app):
        """测试缺少消息字段"""
        response = await test_app.post(
            "/intent/parse",
            json={}
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_message_too_long(self, test_app):
        """测试消息过长"""
        response = await test_app.post(
            "/intent/parse",
            json={
                "message": "x" * 1001  # 超过 1000 字符
            }
        )
        
        assert response.status_code == 422


class TestErrorHandling:
    """测试错误处理"""
    
    @pytest.mark.asyncio
    async def test_internal_server_error(self, test_app):
        """测试服务器内部错误"""
        with patch('app.api.intent.IntentRouter') as MockRouter:
            mock_instance = MockRouter.return_value
            mock_instance.parse = AsyncMock(side_effect=Exception("Test error"))
            
            response = await test_app.post(
                "/intent/parse",
                json={
                    "message": "测试消息"
                }
            )
            
            # 应该返回 500 错误
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "Test error" in data["detail"]


class TestHealthCheck:
    """测试健康检查"""
    
    @pytest.mark.asyncio
    async def test_intent_health_check(self, test_app):
        """测试 Intent Router 健康检查"""
        response = await test_app.get("/intent/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "ok"
        assert data["service"] == "Intent Router"
        assert "message" in data


class TestDependencyInjection:
    """测试依赖注入"""
    
    @pytest.mark.asyncio
    async def test_router_dependency_injection(self, test_app):
        """测试 IntentRouter 依赖注入"""
        with patch('app.api.intent.IntentRouter') as MockRouter:
            mock_instance = MockRouter.return_value
            mock_instance.parse = AsyncMock(return_value=IntentResult(
                intent="other",
                topic=None,
                target_artifact=None,
                confidence=0.85,
                raw_text="测试"
            ))
            
            # 发送多个请求，验证每次都创建新实例
            await test_app.post("/intent/parse", json={"message": "测试1"})
            await test_app.post("/intent/parse", json={"message": "测试2"})
            
            # 验证 IntentRouter 被多次调用（每次请求都创建新实例）
            assert MockRouter.call_count >= 2


class TestResponseFormat:
    """测试响应格式"""
    
    @pytest.mark.asyncio
    async def test_response_structure(self, test_app):
        """测试响应结构"""
        with patch('app.api.intent.IntentRouter') as MockRouter:
            mock_instance = MockRouter.return_value
            mock_instance.parse = AsyncMock(return_value=IntentResult(
                intent="quiz",
                topic="math",
                target_artifact="quiz_set",
                confidence=0.9,
                raw_text="test"
            ))
            
            response = await test_app.post(
                "/intent/parse",
                json={"message": "test"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # 验证响应包含 result 字段
            assert "result" in data
            
            # 验证 result 的结构
            result = data["result"]
            assert "intent" in result
            assert "topic" in result
            assert "target_artifact" in result
            assert "confidence" in result
            assert "raw_text" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
