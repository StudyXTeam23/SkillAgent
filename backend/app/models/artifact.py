"""
产物（Artifact）相关的 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any


class Artifact(BaseModel):
    """通用产物封装"""
    type: str = Field(
        ...,
        description="产物类型：quiz_set, explanation, error, loading"
    )
    
    payload: Dict[str, Any] = Field(
        ...,
        description="实际内容载荷"
    )
    
    meta: Dict[str, Any] = Field(
        default_factory=dict,
        description="元数据，如 source_skill, topic 等"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "quiz_set",
                "payload": {
                    "title": "微积分·极限练习",
                    "questions": []
                },
                "meta": {
                    "source_skill": "quiz",
                    "topic": "微积分-极限"
                }
            }
        }
    }


class Question(BaseModel):
    """练习题问题"""
    id: str = Field(..., description="题目唯一标识")
    
    stem: str = Field(..., description="题干")
    
    options: List[str] = Field(..., min_length=2, description="选项列表")
    
    answer: str = Field(..., description="正确答案")
    
    explanation: str = Field(..., description="解析说明")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "q1",
                "stem": "What is the derivative of f(x) = x²?",
                "options": ["2x", "x", "x²/2", "2"],
                "answer": "2x",
                "explanation": "使用幂规则：d/dx(x^n) = n·x^(n-1)"
            }
        }
    }


class QuizSetArtifact(BaseModel):
    """练习题集合产物"""
    type: str = Field(default="quiz_set", description="产物类型")
    
    title: str = Field(..., description="题集标题")
    
    questions: List[Question] = Field(..., description="题目列表")
    
    meta: Dict[str, Any] = Field(
        default_factory=dict,
        description="元数据"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "quiz_set",
                "title": "微积分·极限基础练习",
                "questions": [
                    {
                        "id": "q1",
                        "stem": "What is lim(x→0) (sin x)/x?",
                        "options": ["0", "1", "∞", "undefined"],
                        "answer": "1",
                        "explanation": "这是一个重要极限"
                    }
                ],
                "meta": {
                    "difficulty": "easy",
                    "topic": "微积分-极限"
                }
            }
        }
    }


class Example(BaseModel):
    """概念讲解中的例子"""
    problem: str = Field(..., description="例题描述")
    
    solution: str = Field(..., description="解答")
    
    steps: List[str] = Field(
        default_factory=list,
        description="解题步骤"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "problem": "Find the derivative of y = (x² + 1)³",
                "solution": "dy/dx = 6x(x² + 1)²",
                "steps": [
                    "Let u = x² + 1",
                    "Then y = u³",
                    "dy/du = 3u²",
                    "du/dx = 2x",
                    "Apply chain rule: dy/dx = (dy/du)(du/dx) = 3u² · 2x = 6x(x² + 1)²"
                ]
            }
        }
    }


class ExplanationArtifact(BaseModel):
    """概念讲解产物"""
    type: str = Field(default="explanation", description="产物类型")
    
    title: str = Field(..., description="概念标题")
    
    content: str = Field(..., description="讲解内容")
    
    formula: Optional[str] = Field(None, description="关键公式")
    
    examples: List[Example] = Field(
        default_factory=list,
        description="示例列表"
    )
    
    meta: Dict[str, Any] = Field(
        default_factory=dict,
        description="元数据"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "explanation",
                "title": "The Chain Rule",
                "content": "The chain rule is a formula to compute...",
                "formula": "d/dx [f(g(x))] = f'(g(x)) * g'(x)",
                "examples": [
                    {
                        "problem": "Find derivative of (x² + 1)³",
                        "solution": "6x(x² + 1)²",
                        "steps": ["Step 1...", "Step 2..."]
                    }
                ],
                "meta": {
                    "depth": "basic",
                    "topic": "微积分-链式法则"
                }
            }
        }
    }

