"""
记忆管理相关的 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime


class UserLearningProfile(BaseModel):
    """用户长期学习画像"""
    user_id: str = Field(..., description="用户唯一标识")
    
    mastery: Dict[str, str] = Field(
        default_factory=dict,
        description="知识点掌握度映射，格式：{topic: weak/medium/strong}"
    )
    
    preferences: Dict[str, str] = Field(
        default_factory=dict,
        description="用户偏好设置"
    )
    
    history: Dict[str, Any] = Field(
        default_factory=lambda: {
            "quiz_sessions": 0,
            "homework_help_count": 0,
            "topics_visited": []
        },
        description="学习历史统计"
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="最后更新时间"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "user_123",
                "mastery": {
                    "微积分-极限": "weak",
                    "微积分-导数": "medium"
                },
                "preferences": {
                    "preferred_artifact": "quiz",
                    "difficulty_preference": "medium"
                },
                "history": {
                    "quiz_sessions": 5,
                    "homework_help_count": 3,
                    "topics_visited": ["微积分-极限", "微积分-导数"]
                },
                "updated_at": "2025-01-13T10:00:00"
            }
        }
    }


class SessionContext(BaseModel):
    """会话短期记忆"""
    session_id: str = Field(..., description="会话唯一标识")
    
    current_topic: Optional[str] = Field(
        None,
        description="当前讨论的主题"
    )
    
    recent_intents: List[str] = Field(
        default_factory=list,
        description="最近的意图序列，用于追踪对话流程"
    )
    
    last_artifact: Optional[str] = Field(
        None,
        description="上一轮生成的产物类型"
    )
    
    last_user_message: str = Field(
        default="",
        description="用户最后一条消息"
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="最后更新时间"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "session_456",
                "current_topic": "微积分-极限",
                "recent_intents": ["quiz", "explain"],
                "last_artifact": "quiz_set",
                "last_user_message": "给我几道练习题",
                "updated_at": "2025-01-13T10:05:00"
            }
        }
    }

