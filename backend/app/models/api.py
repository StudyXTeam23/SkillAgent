"""
API 请求/响应相关的 Pydantic 模型
"""
from pydantic import BaseModel, Field
from .intent import IntentResult
from .artifact import Artifact


class AgentChatRequest(BaseModel):
    """Agent 聊天请求"""
    user_id: str = Field(
        ...,
        description="用户 ID"
    )
    
    session_id: str = Field(
        ...,
        description="会话 ID，用于追踪对话上下文"
    )
    
    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="用户消息内容"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "user_123",
                "session_id": "session_456",
                "message": "给我几道微积分极限的练习题"
            }
        }
    }


class AgentChatResponse(BaseModel):
    """Agent 聊天响应"""
    artifact: Artifact = Field(
        ...,
        description="生成的产物"
    )
    
    intent: IntentResult = Field(
        ...,
        description="识别的意图结果"
    )
    
    processing_time: float = Field(
        ...,
        description="处理时间（秒）"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "artifact": {
                    "type": "quiz_set",
                    "payload": {
                        "title": "微积分·极限练习",
                        "questions": []
                    },
                    "meta": {
                        "source_skill": "quiz",
                        "topic": "微积分-极限"
                    }
                },
                "intent": {
                    "intent": "quiz",
                    "topic": "微积分-极限",
                    "target_artifact": "quiz_set",
                    "confidence": 0.92,
                    "raw_text": "给我几道微积分极限的练习题"
                },
                "processing_time": 2.34
            }
        }
    }

