"""
Pydantic 数据模型

定义整个系统的数据结构，包括：
- intent: 意图识别相关模型
- memory: 记忆管理相关模型
- skill: 技能定义相关模型
- artifact: 输出产物相关模型
- api: API 请求/响应模型
"""
from .intent import IntentResult, MemorySummary
from .memory import UserLearningProfile, SessionContext
from .skill import SkillDefinition
from .artifact import (
    Artifact,
    QuizSetArtifact,
    Question,
    ExplanationArtifact,
    Example
)
from .api import AgentChatRequest, AgentChatResponse

__all__ = [
    # Intent models
    "IntentResult",
    "MemorySummary",
    
    # Memory models
    "UserLearningProfile",
    "SessionContext",
    
    # Skill models
    "SkillDefinition",
    
    # Artifact models
    "Artifact",
    "QuizSetArtifact",
    "Question",
    "ExplanationArtifact",
    "Example",
    
    # API models
    "AgentChatRequest",
    "AgentChatResponse",
]

