"""
Intent Router API 端点

提供意图识别的 REST API，用于调试和测试。
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from ..core.intent_router import IntentRouter
from ..models.intent import IntentResult, MemorySummary

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/intent", tags=["Intent Recognition"])


# ============= Request/Response Models =============

class ParseIntentRequest(BaseModel):
    """意图解析请求"""
    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="用户消息",
        examples=["给我几道微积分极限的练习题"]
    )
    
    memory_summary: Optional[MemorySummary] = Field(
        None,
        description="可选的记忆摘要，用于增强识别准确度"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "给我几道微积分极限的练习题",
                "memory_summary": {
                    "topic_hint": "微积分-极限",
                    "user_mastery_hint": "weak",
                    "recent_behavior": "用户刚做过极限练习题，正确率40%"
                }
            }
        }
    }


class ParseIntentResponse(BaseModel):
    """意图解析响应"""
    result: IntentResult = Field(..., description="意图识别结果")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "result": {
                    "intent": "quiz",
                    "topic": "微积分-极限",
                    "target_artifact": "quiz_set",
                    "confidence": 0.92,
                    "raw_text": "给我几道微积分极限的练习题"
                }
            }
        }
    }


# ============= Dependency Injection =============

def get_intent_router() -> IntentRouter:
    """
    获取 IntentRouter 实例（依赖注入）
    
    Returns:
        IntentRouter: 意图路由器实例
    """
    return IntentRouter()


# ============= API Endpoints =============

@router.post(
    "/parse",
    response_model=ParseIntentResponse,
    summary="解析用户意图",
    description="分析用户消息并识别学习意图，返回结构化的意图信息",
    responses={
        200: {
            "description": "成功识别意图",
            "content": {
                "application/json": {
                    "example": {
                        "result": {
                            "intent": "quiz",
                            "topic": "微积分-极限",
                            "target_artifact": "quiz_set",
                            "confidence": 0.92,
                            "raw_text": "给我几道微积分极限的练习题"
                        }
                    }
                }
            }
        },
        422: {
            "description": "输入验证失败"
        },
        500: {
            "description": "服务器内部错误"
        }
    }
)
async def parse_intent(
    request: ParseIntentRequest,
    intent_router: IntentRouter = Depends(get_intent_router)
) -> ParseIntentResponse:
    """
    解析用户意图
    
    Args:
        request: 意图解析请求
        intent_router: IntentRouter 实例（依赖注入）
    
    Returns:
        ParseIntentResponse: 意图识别结果
    
    Raises:
        HTTPException: 如果解析失败
    """
    try:
        logger.info(f"📨 Received intent parse request: {request.message[:50]}...")
        
        # 调用 IntentRouter 进行解析
        result = await intent_router.parse(
            message=request.message,
            memory_summary=request.memory_summary
        )
        
        logger.info(
            f"✅ Intent parsed successfully: {result.intent} "
            f"(confidence: {result.confidence:.2f})"
        )
        
        return ParseIntentResponse(result=result)
        
    except Exception as e:
        logger.error(f"❌ Failed to parse intent: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Intent parsing failed: {str(e)}"
        )


@router.get(
    "/health",
    summary="健康检查",
    description="检查 Intent Router 服务是否正常运行"
)
async def health_check():
    """Intent Router 健康检查"""
    return {
        "status": "ok",
        "service": "Intent Router",
        "message": "Intent recognition service is running"
    }

