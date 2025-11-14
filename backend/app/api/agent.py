"""
Agent API - 统一的聊天端点

提供 /api/agent/chat 端点，完整编排 Intent Router, Memory Manager, 和 Skill Orchestrator
"""
import logging
import time
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field, field_validator

from app.core import MemoryManager, SkillOrchestrator
from app.services.gemini import GeminiClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agent", tags=["agent"])


# ============= Request/Response Models =============

class AgentChatRequest(BaseModel):
    """Agent 聊天请求"""
    user_id: str = Field(..., description="用户 ID", min_length=1, max_length=100)
    session_id: str = Field(..., description="会话 ID", min_length=1, max_length=100)
    message: str = Field(..., description="用户消息", min_length=1, max_length=5000)

    @field_validator('message')
    @classmethod
    def validate_message(cls, v: str) -> str:
        """验证消息不为空且不只包含空格"""
        if not v.strip():
            raise ValueError("消息不能为空")
        return v.strip()


class AgentChatResponse(BaseModel):
    """Agent 聊天响应"""
    user_id: str = Field(..., description="用户 ID")
    session_id: str = Field(..., description="会话 ID")
    response_content: Dict[str, Any] = Field(..., description="响应内容（Quiz, Explain 等）")
    content_type: str = Field(..., description="内容类型：quiz_set, explanation, error 等")
    intent: str = Field(..., description="识别的意图")
    skill_id: str = Field(..., description="使用的技能 ID")
    processing_time_ms: int = Field(default=0, description="处理时间（毫秒）")


# ============= Dependency Functions =============

def get_memory_manager() -> MemoryManager:
    """获取 Memory Manager 单例"""
    if not hasattr(get_memory_manager, "_instance"):
        get_memory_manager._instance = MemoryManager(use_s3=False)
    return get_memory_manager._instance


def get_gemini_client() -> GeminiClient:
    """获取 Gemini Client 单例"""
    if not hasattr(get_gemini_client, "_instance"):
        get_gemini_client._instance = GeminiClient()
    return get_gemini_client._instance


def get_skill_orchestrator(
    memory_manager: MemoryManager = Depends(get_memory_manager),
    gemini_client: GeminiClient = Depends(get_gemini_client)
) -> SkillOrchestrator:
    """获取 Skill Orchestrator 实例"""
    return SkillOrchestrator(
        memory_manager=memory_manager,
        gemini_client=gemini_client
    )


# ============= API Endpoints =============

@router.post("/chat", response_model=AgentChatResponse, status_code=status.HTTP_200_OK)
async def agent_chat(
    request: AgentChatRequest,
    orchestrator: SkillOrchestrator = Depends(get_skill_orchestrator)
) -> AgentChatResponse:
    """
    统一的 Agent 聊天端点
    
    完整流程：
    1. 解析用户意图 (Intent Router)
    2. 选择合适的技能 (Skill Registry)
    3. 执行技能 (Skill Orchestrator)
    4. 更新用户记忆 (Memory Manager)
    5. 返回结构化结果
    
    Args:
        request: 包含 user_id, session_id, message 的请求
        orchestrator: 技能编排器（依赖注入）
    
    Returns:
        AgentChatResponse: 包含生成内容、意图、技能ID等信息
        
    Raises:
        HTTPException: 当发生错误时返回相应的HTTP错误
    """
    start_time = time.time()
    
    logger.info(
        f"📩 Agent chat request from user={request.user_id}, "
        f"session={request.session_id}, message_len={len(request.message)}"
    )
    
    try:
        # 1. 先通过 Intent Router 识别意图
        from ..core.intent_router import IntentRouter
        intent_router = IntentRouter(gemini_client=orchestrator.gemini_client)
        
        # 获取记忆摘要
        memory_summary = await orchestrator.memory_manager.generate_memory_summary(
            request.user_id,
            request.session_id
        )
        
        # 解析意图（支持混合请求，返回列表）
        intent_results = await intent_router.parse(
            message=request.message,
            memory_summary=memory_summary
        )
        
        # 2. 特殊处理：如果意图是 "other"，进行友好对话和引导
        if len(intent_results) == 1 and intent_results[0].intent == "other":
            # 调用 Gemini 进行友好对话
            from app.config import settings
            gemini_client = orchestrator.gemini_client
            
            conversation_prompt = f"""你是一个智能学习助手 StudyX Agent。用户向你提问了一个与学习无关的问题。

用户问题：{request.message}

请友好地回应用户，然后引导用户使用你的学习功能。你可以：
1. 简短回应用户的问题（1-2句话）
2. 介绍你的核心学习功能：
   - 📝 练习题生成（Quiz）：生成各学科的练习题
   - 📖 概念讲解（Explain）：清晰讲解学习概念
   - 🎴 闪卡生成（Flashcard）：帮助记忆的Anki风格闪卡
   - 📦 学习包（Learning Bundle）：综合学习资料包
3. 给出1-2个具体的使用示例

保持回复友好、简洁、鼓励性，不要太长（最多150字）。"""
            
            try:
                friendly_response = await gemini_client.generate(
                    prompt=conversation_prompt,
                    model=settings.GEMINI_MODEL,
                    max_tokens=300,
                    temperature=0.7
                )
                
                # 计算处理时间
                processing_time = time.time() - start_time
                
                response = AgentChatResponse(
                    user_id=request.user_id,
                    session_id=request.session_id,
                    response_content={"text": friendly_response},
                    content_type="text",
                    intent="other",
                    skill_id="conversation",
                    processing_time_ms=int(processing_time * 1000)
                )
            except Exception as e:
                logger.error(f"❌ Failed to generate friendly response: {e}")
                # 如果生成失败，使用预设的友好回复
                default_response = """你好！我是 StudyX Agent，你的智能学习助手 🎓

我专注于帮助你学习，可以为你提供：
• 📝 **练习题**：各学科的针对性练习（例如："给我几道微积分题"）
• 📖 **概念讲解**：清晰的知识点讲解（例如："解释一下什么是导数"）
• 🎴 **学习闪卡**：帮助记忆的卡片（例如："给我一些光合作用的闪卡"）
• 📦 **学习资料包**：综合学习材料（例如："帮我准备电磁学的学习资料"）

试试问我一个学习相关的问题吧！😊"""
                
                processing_time = time.time() - start_time
                
                response = AgentChatResponse(
                    user_id=request.user_id,
                    session_id=request.session_id,
                    response_content={"text": default_response},
                    content_type="text",
                    intent="other",
                    skill_id="conversation",
                    processing_time_ms=int(processing_time * 1000)
                )
        else:
            # 正常的学习意图，执行完整的技能编排管道
            # 支持混合请求：循环执行多个 intents
            all_results = []
            
            for idx, intent_result in enumerate(intent_results):
                logger.info(f"🎯 Executing intent {idx+1}/{len(intent_results)}: {intent_result.intent}")
                
                orchestrator_response = await orchestrator.execute(
                    intent_result=intent_result,
                    user_id=request.user_id,
                    session_id=request.session_id
                )
                
                all_results.append(orchestrator_response)
            
            # 计算处理时间
            processing_time = time.time() - start_time
            
            # 构建响应
            if len(all_results) == 1:
                # 单个结果
                response = AgentChatResponse(
                    user_id=request.user_id,
                    session_id=request.session_id,
                    response_content=all_results[0].get("content", {}),
                    content_type=all_results[0].get("content_type", "unknown"),
                    intent=all_results[0].get("intent", "unknown"),
                    skill_id=all_results[0].get("skill_id", "unknown"),
                    processing_time_ms=int(processing_time * 1000)
                )
            else:
                # 混合请求：多个结果
                response = AgentChatResponse(
                    user_id=request.user_id,
                    session_id=request.session_id,
                    response_content={"results": all_results},
                    content_type="mixed_response",
                    intent="mixed",
                    skill_id="multiple",
                    processing_time_ms=int(processing_time * 1000)
                )
        
        logger.info(
            f"✅ Agent response generated: intent={response.intent}, "
            f"skill_id={response.skill_id}, processing_time={processing_time:.2f}s"
        )
        
        return response
        
    except ValueError as e:
        # 业务逻辑错误（如意图不明确）
        logger.warning(f"❌ Validation error for user {request.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "ValidationError",
                "message": str(e),
                "user_id": request.user_id,
                "session_id": request.session_id
            }
        )
        
    except FileNotFoundError as e:
        # Prompt 文件缺失
        logger.error(f"❌ File not found error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "PromptFileNotFound",
                "message": f"系统配置错误：{str(e)}",
                "user_id": request.user_id,
                "session_id": request.session_id
            }
        )
        
    except Exception as e:
        # 未预期的系统错误
        logger.exception(f"❌ Unexpected error in agent_chat for user {request.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "InternalServerError",
                "message": "系统内部错误，请稍后再试",
                "user_id": request.user_id,
                "session_id": request.session_id
            }
        )


@router.get("/health", status_code=status.HTTP_200_OK)
async def agent_health() -> Dict[str, Any]:
    """
    Agent API 健康检查
    
    Returns:
        健康状态信息
    """
    try:
        # 检查关键组件是否可用
        memory_manager = get_memory_manager()
        gemini_client = get_gemini_client()
        
        return {
            "status": "healthy",
            "components": {
                "memory_manager": "ok" if memory_manager else "error",
                "gemini_client": "ok" if gemini_client else "error"
            },
            "message": "Agent API is operational"
        }
    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "message": str(e)
            }
        )


@router.get("/info", status_code=status.HTTP_200_OK)
async def agent_info(
    orchestrator: SkillOrchestrator = Depends(get_skill_orchestrator)
) -> Dict[str, Any]:
    """
    Agent 系统信息
    
    返回可用的技能、意图等信息
    
    Returns:
        系统信息和可用技能列表
    """
    try:
        all_skills = orchestrator.skill_registry.list_all_skills()
        all_intents = orchestrator.skill_registry.get_all_intents()
        
        skills_info = [
            {
                "id": skill.id,
                "display_name": skill.display_name,
                "intent_tags": skill.intent_tags,
                "version": skill.version
            }
            for skill in all_skills
        ]
        
        return {
            "total_skills": len(all_skills),
            "available_intents": all_intents,
            "skills": skills_info,
            "api_version": "1.0.0",
            "message": "Skill Agent Demo API"
        }
    except Exception as e:
        logger.error(f"❌ Failed to get agent info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "InfoRetrievalError",
                "message": str(e)
            }
        )

