"""
Artifact Storage - Context Offloading 核心模块

负责将 Plan Skill 的 step 结果持久化到文件系统，
实现真正的上下文卸载（而不是内存累积）。

设计原则：
- 独立模块，零侵入
- 完全可选，默认不使用
- 降级友好，文件操作失败时不影响主流程
"""

import json
import logging
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ArtifactStorage:
    """
    Artifact 存储管理器
    
    职责：
    1. 保存 step 结果到文件系统
    2. 按需加载 artifact
    3. 创建轻量级引用（artifact_reference）
    4. 管理 artifact 生命周期
    
    使用场景：
    - Plan Skill 中的 step 结果持久化
    - 跨 step 的上下文传递（通过引用而不是完整内容）
    
    不影响：
    - Single Skill 执行（完全独立）
    - Intent Router（不涉及）
    - Memory System（不同存储目录）
    """
    
    def __init__(self, base_dir: str = "artifacts"):
        """
        初始化 Artifact Storage
        
        Args:
            base_dir: artifact 存储根目录（相对于项目根目录）
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ ArtifactStorage initialized: {self.base_dir.absolute()}")
    
    def save_step_result(
        self,
        session_id: str,
        step_id: str,
        result: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        保存 step 结果到文件
        
        Args:
            session_id: Plan 执行的唯一 session ID
            step_id: Step 标识符（如 "explain", "notes", "quiz"）
            result: Step 执行结果（完整内容）
            metadata: 可选的元数据（如 skill_id, tokens_used）
        
        Returns:
            文件相对路径（相对于 base_dir）
            
        Raises:
            IOError: 文件写入失败时
        """
        try:
            # 创建 session 目录
            session_dir = self.base_dir / session_id
            session_dir.mkdir(parents=True, exist_ok=True)
            
            # 文件路径
            file_path = session_dir / f"step_{step_id}.json"
            
            # 构建 artifact 结构
            artifact = {
                "step_id": step_id,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "result": result,
                "metadata": metadata or {}
            }
            
            # 保存到文件
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(artifact, f, ensure_ascii=False, indent=2)
            
            # 返回相对路径
            relative_path = file_path.relative_to(self.base_dir)
            
            # 统计信息
            file_size = file_path.stat().st_size
            result_size = len(json.dumps(result, ensure_ascii=False))
            
            logger.info(
                f"💾 Saved artifact: {relative_path} "
                f"(result: {result_size} bytes, file: {file_size} bytes)"
            )
            
            return str(relative_path)
            
        except Exception as e:
            logger.error(f"❌ Failed to save artifact: {e}")
            raise
    
    def load_step_result(
        self,
        session_id: str,
        step_id: str
    ) -> Dict[str, Any]:
        """
        按需加载 step 结果（完整内容）
        
        Args:
            session_id: Plan 执行的 session ID
            step_id: Step 标识符
        
        Returns:
            Step 执行结果（result 字段）
            
        Raises:
            FileNotFoundError: artifact 不存在
            json.JSONDecodeError: JSON 解析失败
        """
        file_path = self.base_dir / session_id / f"step_{step_id}.json"
        
        if not file_path.exists():
            raise FileNotFoundError(
                f"Artifact not found: {file_path.relative_to(self.base_dir)}"
            )
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                artifact = json.load(f)
            
            logger.debug(
                f"🔍 Loaded artifact: {session_id}/step_{step_id}.json "
                f"({len(json.dumps(artifact['result'], ensure_ascii=False))} bytes)"
            )
            
            return artifact["result"]
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse artifact JSON: {e}")
            raise
    
    def create_reference(
        self,
        session_id: str,
        step_id: str,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        创建轻量级 artifact 引用（而不是传递完整内容）
        
        这是 Context Offloading 的核心：
        - 不传递 2000+ tokens 的完整内容
        - 只传递 ~100 bytes 的引用
        - 按需加载（_format_prompt 时）
        
        Args:
            session_id: Plan 执行的 session ID
            step_id: Step 标识符
            fields: 可选的字段列表（只加载这些字段，进一步节省）
        
        Returns:
            Artifact 引用对象（type="artifact_reference"）
        """
        reference = {
            "type": "artifact_reference",
            "session_id": session_id,
            "step_id": step_id,
            "fields": fields,
            "file_path": f"{session_id}/step_{step_id}.json"
        }
        
        reference_size = len(json.dumps(reference, ensure_ascii=False))
        logger.debug(
            f"📝 Created reference: {step_id} "
            f"({reference_size} bytes, fields: {fields or 'all'})"
        )
        
        return reference
    
    def save_plan_metadata(
        self,
        session_id: str,
        plan_config: Dict[str, Any],
        user_input: Dict[str, Any]
    ) -> str:
        """
        保存 Plan 整体元数据
        
        用于追溯和恢复：
        - Plan 配置
        - 用户输入
        - 执行时间
        
        Args:
            session_id: Plan 执行的 session ID
            plan_config: Plan 配置（来自 YAML）
            user_input: 用户输入参数
        
        Returns:
            metadata 文件相对路径
        """
        try:
            session_dir = self.base_dir / session_id
            session_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = session_dir / "plan_metadata.json"
            
            metadata = {
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "plan_config": {
                    "skill_id": plan_config.get("id"),
                    "display_name": plan_config.get("display_name"),
                    "steps": [
                        {
                            "step_id": step.get("step_id"),
                            "skill_id": step.get("skill_id"),
                            "name": step.get("name")
                        }
                        for step in plan_config.get("execution_plan", [])
                    ]
                },
                "user_input": user_input
            }
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            relative_path = file_path.relative_to(self.base_dir)
            logger.info(f"📋 Saved plan metadata: {relative_path}")
            
            return str(relative_path)
            
        except Exception as e:
            logger.error(f"❌ Failed to save plan metadata: {e}")
            raise
    
    def load_plan_metadata(self, session_id: str) -> Dict[str, Any]:
        """
        加载 Plan 元数据
        
        Args:
            session_id: Plan 执行的 session ID
        
        Returns:
            Plan 元数据
            
        Raises:
            FileNotFoundError: metadata 不存在
        """
        file_path = self.base_dir / session_id / "plan_metadata.json"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Plan metadata not found: {session_id}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def cleanup_session(self, session_id: str) -> None:
        """
        清理 session 的所有 artifacts（可选）
        
        Args:
            session_id: Plan 执行的 session ID
        """
        session_dir = self.base_dir / session_id
        
        if not session_dir.exists():
            logger.warning(f"⚠️  Session dir not found: {session_id}")
            return
        
        try:
            import shutil
            shutil.rmtree(session_dir)
            logger.info(f"🗑️  Cleaned up session: {session_id}")
        except Exception as e:
            logger.error(f"❌ Failed to cleanup session {session_id}: {e}")
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        列出所有 session（用于调试和管理）
        
        Returns:
            Session 列表（包含 session_id, timestamp, step_count）
        """
        sessions = []
        
        for session_dir in self.base_dir.iterdir():
            if not session_dir.is_dir():
                continue
            
            session_id = session_dir.name
            
            try:
                # 读取 metadata
                metadata = self.load_plan_metadata(session_id)
                
                # 统计 step 数量
                step_files = list(session_dir.glob("step_*.json"))
                
                sessions.append({
                    "session_id": session_id,
                    "timestamp": metadata.get("timestamp"),
                    "step_count": len(step_files),
                    "plan_name": metadata.get("plan_config", {}).get("display_name")
                })
            except Exception as e:
                logger.warning(f"⚠️  Failed to load session {session_id}: {e}")
        
        return sessions


def generate_session_id() -> str:
    """
    生成唯一的 session ID
    
    格式: plan_{timestamp}_{uuid}
    
    Returns:
        Session ID 字符串
    """
    timestamp = int(time.time())
    unique_id = uuid.uuid4().hex[:8]
    return f"plan_{timestamp}_{unique_id}"

