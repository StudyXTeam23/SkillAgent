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


class ArtifactRecord(BaseModel):
    """单个Artifact记录"""
    artifact_id: str = Field(..., description="Artifact唯一标识")
    turn_number: int = Field(..., description="第几轮对话")
    timestamp: datetime = Field(default_factory=datetime.now, description="生成时间")
    artifact_type: str = Field(..., description="产物类型: quiz_set, explanation, flashcard_set等")
    topic: Optional[str] = Field(None, description="主题")
    summary: str = Field(..., description="内容摘要，用于显示和搜索")
    content: Dict[str, Any] = Field(..., description="完整内容")


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
    
    # 🆕 改为历史记录列表
    artifact_history: List[ArtifactRecord] = Field(
        default_factory=list,
        description="所有历史Artifact记录，按时间顺序"
    )
    
    # 🆕 只保存引用，不保存完整内容（避免冗余）
    last_artifact_id: Optional[str] = Field(
        None,
        description="最后一个artifact的ID（用于快速访问）"
    )
    
    # 🔧 向后兼容：提供属性访问器
    @property
    def last_artifact(self) -> Optional[str]:
        """获取最后一个artifact的类型（向后兼容）"""
        if self.artifact_history:
            return self.artifact_history[-1].artifact_type
        return None
    
    @property
    def last_artifact_content(self) -> Optional[Dict[str, Any]]:
        """获取最后一个artifact的内容（向后兼容）"""
        if self.artifact_history:
            return self.artifact_history[-1].content
        return None
    
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
                "current_topic": "全球变暖",
                "recent_intents": ["explain", "quiz", "flashcard"],
                "artifact_history": [
                    {
                        "artifact_id": "artifact_1",
                        "turn_number": 1,
                        "timestamp": "2025-11-18T17:00:00",
                        "artifact_type": "explanation",
                        "topic": "全球变暖",
                        "summary": "全球变暖的概念解释，包含3个例子",
                        "content": {"concept": "全球变暖", "examples": [...]}
                    },
                    {
                        "artifact_id": "artifact_2",
                        "turn_number": 2,
                        "timestamp": "2025-11-18T17:01:00",
                        "artifact_type": "quiz_set",
                        "topic": "全球变暖",
                        "summary": "5道关于全球变暖的题目",
                        "content": {"quiz_set_id": "...", "questions": [...]}
                    }
                ],
                "last_artifact_id": "artifact_2",
                "last_user_message": "给我几道练习题",
                "updated_at": "2025-01-13T10:05:00"
            }
        }
    }

