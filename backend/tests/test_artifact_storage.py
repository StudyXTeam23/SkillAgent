"""
Unit Tests for ArtifactStorage

测试 Context Offloading 的核心模块：
- 文件保存和加载
- 引用创建
- Metadata 管理
- Session 清理
"""

import json
import shutil
import time
from pathlib import Path

import pytest

from app.core.artifact_storage import ArtifactStorage, generate_session_id


@pytest.fixture
def temp_artifact_dir(tmp_path):
    """临时 artifact 目录"""
    artifact_dir = tmp_path / "artifacts"
    yield artifact_dir
    # Cleanup
    if artifact_dir.exists():
        shutil.rmtree(artifact_dir)


@pytest.fixture
def storage(temp_artifact_dir):
    """ArtifactStorage 实例"""
    return ArtifactStorage(base_dir=str(temp_artifact_dir))


class TestArtifactStorage:
    """ArtifactStorage 基础功能测试"""
    
    def test_init_creates_base_dir(self, temp_artifact_dir):
        """测试：初始化时创建 base_dir"""
        storage = ArtifactStorage(base_dir=str(temp_artifact_dir))
        assert temp_artifact_dir.exists()
        assert storage.base_dir == temp_artifact_dir
    
    def test_save_step_result(self, storage):
        """测试：保存 step 结果到文件"""
        session_id = "test_session_001"
        step_id = "explain"
        result = {
            "concept": "光合作用",
            "intuition": "植物的食物工厂",
            "examples": [
                {"example": "例子1", "explanation": "说明1"}
            ]
        }
        metadata = {
            "skill_id": "explain_skill",
            "tokens_used": 1500
        }
        
        # 保存
        file_path = storage.save_step_result(
            session_id=session_id,
            step_id=step_id,
            result=result,
            metadata=metadata
        )
        
        # 验证返回的相对路径
        assert file_path == f"{session_id}/step_{step_id}.json"
        
        # 验证文件存在
        full_path = storage.base_dir / file_path
        assert full_path.exists()
        
        # 验证文件内容
        with open(full_path, "r", encoding="utf-8") as f:
            saved_artifact = json.load(f)
        
        assert saved_artifact["step_id"] == step_id
        assert saved_artifact["session_id"] == session_id
        assert saved_artifact["result"] == result
        assert saved_artifact["metadata"] == metadata
        assert "timestamp" in saved_artifact
    
    def test_load_step_result(self, storage):
        """测试：加载 step 结果"""
        session_id = "test_session_002"
        step_id = "quiz"
        result = {
            "quiz_set_id": "quiz_001",
            "questions": [
                {"question_text": "问题1", "correct_answer": "A"}
            ]
        }
        
        # 先保存
        storage.save_step_result(session_id, step_id, result)
        
        # 再加载
        loaded_result = storage.load_step_result(session_id, step_id)
        
        # 验证内容一致
        assert loaded_result == result
    
    def test_load_nonexistent_artifact(self, storage):
        """测试：加载不存在的 artifact 应该抛出异常"""
        with pytest.raises(FileNotFoundError):
            storage.load_step_result("nonexistent_session", "nonexistent_step")
    
    def test_create_reference(self, storage):
        """测试：创建轻量级引用"""
        session_id = "test_session_003"
        step_id = "explain"
        fields = ["concept", "examples"]
        
        # 创建引用
        reference = storage.create_reference(
            session_id=session_id,
            step_id=step_id,
            fields=fields
        )
        
        # 验证引用结构
        assert reference["type"] == "artifact_reference"
        assert reference["session_id"] == session_id
        assert reference["step_id"] == step_id
        assert reference["fields"] == fields
        assert reference["file_path"] == f"{session_id}/step_{step_id}.json"
        
        # 验证引用大小（应该远小于实际内容）
        reference_size = len(json.dumps(reference, ensure_ascii=False))
        assert reference_size < 200  # < 200 bytes (vs 2000+ tokens)
    
    def test_create_reference_without_fields(self, storage):
        """测试：创建引用时不指定 fields（加载完整内容）"""
        reference = storage.create_reference(
            session_id="test_session",
            step_id="quiz",
            fields=None
        )
        
        assert reference["fields"] is None
    
    def test_save_plan_metadata(self, storage):
        """测试：保存 Plan 元数据"""
        session_id = "test_session_004"
        plan_config = {
            "id": "learning_plan_skill",
            "display_name": "学习包规划器",
            "execution_plan": [
                {"step_id": "explain", "skill_id": "explain_skill", "name": "概念讲解"},
                {"step_id": "quiz", "skill_id": "quiz_skill", "name": "练习题"}
            ]
        }
        user_input = {
            "subject": "生物",
            "topic": "光合作用",
            "difficulty": "medium"
        }
        
        # 保存 metadata
        file_path = storage.save_plan_metadata(
            session_id=session_id,
            plan_config=plan_config,
            user_input=user_input
        )
        
        # 验证文件存在
        full_path = storage.base_dir / file_path
        assert full_path.exists()
        
        # 验证内容
        with open(full_path, "r", encoding="utf-8") as f:
            saved_metadata = json.load(f)
        
        assert saved_metadata["session_id"] == session_id
        assert saved_metadata["plan_config"]["skill_id"] == "learning_plan_skill"
        assert len(saved_metadata["plan_config"]["steps"]) == 2
        assert saved_metadata["user_input"] == user_input
    
    def test_load_plan_metadata(self, storage):
        """测试：加载 Plan 元数据"""
        session_id = "test_session_005"
        plan_config = {"id": "learning_plan_skill"}
        user_input = {"topic": "测试主题"}
        
        # 先保存
        storage.save_plan_metadata(session_id, plan_config, user_input)
        
        # 再加载
        loaded_metadata = storage.load_plan_metadata(session_id)
        
        # 验证
        assert loaded_metadata["session_id"] == session_id
        assert loaded_metadata["user_input"] == user_input
    
    def test_cleanup_session(self, storage):
        """测试：清理 session 的所有 artifacts"""
        session_id = "test_session_006"
        
        # 创建一些 artifacts
        storage.save_step_result(session_id, "explain", {"content": "test1"})
        storage.save_step_result(session_id, "quiz", {"content": "test2"})
        storage.save_plan_metadata(session_id, {}, {})
        
        # 验证 session 目录存在
        session_dir = storage.base_dir / session_id
        assert session_dir.exists()
        assert len(list(session_dir.iterdir())) == 3  # 2 steps + 1 metadata
        
        # 清理
        storage.cleanup_session(session_id)
        
        # 验证已删除
        assert not session_dir.exists()
    
    def test_cleanup_nonexistent_session(self, storage):
        """测试：清理不存在的 session 不应该报错"""
        # 不应该抛出异常
        storage.cleanup_session("nonexistent_session")
    
    def test_list_sessions(self, storage):
        """测试：列出所有 session"""
        # 创建多个 sessions
        session1 = "test_session_007"
        session2 = "test_session_008"
        
        storage.save_plan_metadata(
            session1,
            {"id": "plan1", "display_name": "测试计划1", "execution_plan": []},
            {"topic": "主题1"}
        )
        storage.save_step_result(session1, "explain", {"content": "test"})
        
        storage.save_plan_metadata(
            session2,
            {"id": "plan2", "display_name": "测试计划2", "execution_plan": []},
            {"topic": "主题2"}
        )
        storage.save_step_result(session2, "quiz", {"content": "test"})
        storage.save_step_result(session2, "flashcard", {"content": "test"})
        
        # 列出所有 sessions
        sessions = storage.list_sessions()
        
        # 验证
        assert len(sessions) == 2
        
        session1_info = next(s for s in sessions if s["session_id"] == session1)
        assert session1_info["step_count"] == 1
        assert session1_info["plan_name"] == "测试计划1"
        
        session2_info = next(s for s in sessions if s["session_id"] == session2)
        assert session2_info["step_count"] == 2
        assert session2_info["plan_name"] == "测试计划2"


class TestTokenSavings:
    """Token 节省效果测试"""
    
    def test_reference_vs_full_content_size(self, storage):
        """测试：引用大小 vs 完整内容大小"""
        session_id = "test_token_savings"
        step_id = "explain"
        
        # 模拟一个大的 explain 结果（~2000 tokens）
        large_result = {
            "concept": "光合作用",
            "intuition": "光合作用是植物的'食物制造工厂'..." * 20,
            "formal_definition": "光合作用是绿色植物..." * 30,
            "why_it_matters": "光合作用是地球生态系统..." * 20,
            "examples": [
                {
                    "example": f"例子{i}",
                    "explanation": "这是一个详细的例子说明..." * 10
                }
                for i in range(3)
            ],
            "common_mistakes": [
                {"mistake": f"错误{i}", "correction": "正确的是..." * 10}
                for i in range(2)
            ]
        }
        
        # 保存完整内容
        storage.save_step_result(session_id, step_id, large_result)
        
        # 创建引用
        reference = storage.create_reference(session_id, step_id, fields=["concept", "examples"])
        
        # 计算大小
        full_content_size = len(json.dumps(large_result, ensure_ascii=False))
        reference_size = len(json.dumps(reference, ensure_ascii=False))
        
        # 验证：引用远小于完整内容
        assert reference_size < 200  # 引用 < 200 bytes
        assert full_content_size > 1500  # 完整内容 > 1500 bytes
        
        savings_ratio = 1 - (reference_size / full_content_size)
        assert savings_ratio > 0.9  # 节省 > 90%


class TestGenerateSessionId:
    """Session ID 生成测试"""
    
    def test_generate_unique_ids(self):
        """测试：生成的 ID 应该唯一"""
        id1 = generate_session_id()
        time.sleep(0.01)  # 确保时间戳不同
        id2 = generate_session_id()
        
        assert id1 != id2
        assert id1.startswith("plan_")
        assert id2.startswith("plan_")
    
    def test_id_format(self):
        """测试：ID 格式正确"""
        session_id = generate_session_id()
        
        # 格式: plan_{timestamp}_{uuid}
        parts = session_id.split("_")
        assert parts[0] == "plan"
        assert parts[1].isdigit()  # timestamp
        assert len(parts[2]) == 8  # uuid前8位


class TestEdgeCases:
    """边界情况测试"""
    
    def test_save_empty_result(self, storage):
        """测试：保存空结果"""
        session_id = "test_edge_001"
        step_id = "empty"
        result = {}
        
        file_path = storage.save_step_result(session_id, step_id, result)
        loaded_result = storage.load_step_result(session_id, step_id)
        
        assert loaded_result == result
    
    def test_save_large_result(self, storage):
        """测试：保存大结果（模拟 10000+ tokens）"""
        session_id = "test_edge_002"
        step_id = "large"
        result = {
            "data": "A" * 10000  # 10000 字符
        }
        
        file_path = storage.save_step_result(session_id, step_id, result)
        loaded_result = storage.load_step_result(session_id, step_id)
        
        assert loaded_result == result
    
    def test_unicode_content(self, storage):
        """测试：Unicode 内容（中文、emoji）"""
        session_id = "test_edge_003"
        step_id = "unicode"
        result = {
            "text": "这是中文测试 🎉",
            "concept": "光合作用 ✨",
            "emoji": "🌱🌞💧→🍃+🌬️"
        }
        
        file_path = storage.save_step_result(session_id, step_id, result)
        loaded_result = storage.load_step_result(session_id, step_id)
        
        assert loaded_result == result
    
    def test_special_characters_in_session_id(self, storage):
        """测试：Session ID 包含特殊字符（应该被路径处理正确）"""
        # 注意：在实际使用中应该避免特殊字符，但测试确保不会崩溃
        session_id = "test-session-004"  # 使用 - 分隔符
        step_id = "test"
        result = {"data": "test"}
        
        file_path = storage.save_step_result(session_id, step_id, result)
        loaded_result = storage.load_step_result(session_id, step_id)
        
        assert loaded_result == result

