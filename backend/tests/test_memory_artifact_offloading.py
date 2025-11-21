"""
测试 Memory System 的 Artifact Offloading 功能（Phase 2.5）

测试范围：
1. S3 Storage 集成
2. ArtifactRecord 模型（content_reference）
3. MemoryManager 自动卸载
4. 按需加载
5. 降级机制
6. 数据验证 + Quarantine
"""
import json
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

from app.core.s3_storage import S3StorageManager
from app.core.artifact_storage import ArtifactStorage
from app.core.memory_manager import MemoryManager
from app.models.memory import ArtifactRecord


class TestS3StorageManager:
    """测试 S3 存储管理器"""
    
    def test_init_with_s3_disabled(self):
        """测试 S3 禁用时的初始化"""
        with patch('app.core.s3_storage.settings') as mock_settings:
            mock_settings.USE_S3_STORAGE = False
            
            s3_manager = S3StorageManager()
            
            assert s3_manager.s3_client is None
            assert not s3_manager.is_available()
    
    def test_validate_content_success(self):
        """测试内容验证 - 成功"""
        with patch('app.core.s3_storage.settings') as mock_settings:
            mock_settings.USE_S3_STORAGE = False
            s3_manager = S3StorageManager()
            
            valid_content = {
                "concept": "光合作用",
                "examples": ["example1", "example2"]
            }
            
            assert s3_manager._validate_content(valid_content)
    
    def test_validate_content_too_large(self):
        """测试内容验证 - 内容过大"""
        with patch('app.core.s3_storage.settings') as mock_settings:
            mock_settings.USE_S3_STORAGE = False
            s3_manager = S3StorageManager()
            
            # 创建超过 10MB 的内容
            large_content = {"data": "x" * (11 * 1024 * 1024)}
            
            assert not s3_manager._validate_content(large_content)
    
    def test_validate_content_not_dict(self):
        """测试内容验证 - 不是字典"""
        with patch('app.core.s3_storage.settings') as mock_settings:
            mock_settings.USE_S3_STORAGE = False
            s3_manager = S3StorageManager()
            
            assert not s3_manager._validate_content("not a dict")
            assert not s3_manager._validate_content(["list"])


class TestArtifactStorageS3Integration:
    """测试 ArtifactStorage 的 S3 集成"""
    
    def test_init_with_s3_manager(self):
        """测试带 S3Manager 的初始化"""
        mock_s3_manager = Mock()
        mock_s3_manager.is_available.return_value = True
        
        storage = ArtifactStorage(base_dir="test_artifacts", s3_manager=mock_s3_manager)
        
        assert storage.use_s3 is True
        assert storage.s3_manager == mock_s3_manager
    
    def test_save_step_result_s3_priority(self):
        """测试保存时优先使用 S3"""
        mock_s3_manager = Mock()
        mock_s3_manager.is_available.return_value = True
        mock_s3_manager.save_artifact.return_value = "s3://bucket/artifacts/user_alice/step_test.json"
        
        storage = ArtifactStorage(base_dir="test_artifacts", s3_manager=mock_s3_manager)
        
        result = storage.save_step_result(
            session_id="user_alice_123456",
            step_id="test_step",
            result={"data": "test"},
            metadata={}
        )
        
        assert result.startswith("s3://")
        mock_s3_manager.save_artifact.assert_called_once()
    
    def test_save_step_result_fallback_to_local(self):
        """测试 S3 失败时降级到本地"""
        mock_s3_manager = Mock()
        mock_s3_manager.is_available.return_value = True
        mock_s3_manager.save_artifact.return_value = None  # S3 失败
        
        storage = ArtifactStorage(base_dir="test_artifacts", s3_manager=mock_s3_manager)
        
        result = storage.save_step_result(
            session_id="user_alice_123456",
            step_id="test_step",
            result={"data": "test"},
            metadata={}
        )
        
        assert not result.startswith("s3://")
        assert "user_alice_123456" in result
    
    def test_extract_user_id(self):
        """测试从 session_id 提取 user_id"""
        storage = ArtifactStorage()
        
        assert storage._extract_user_id("user_alice_123456") == "alice"
        assert storage._extract_user_id("plan_123456_abcd1234") == "anonymous"
    
    def test_load_artifact_by_reference_s3(self):
        """测试从 S3 URI 加载"""
        mock_s3_manager = Mock()
        mock_s3_manager.is_available.return_value = True
        mock_s3_manager.load_artifact.return_value = {"data": "loaded from S3"}
        
        storage = ArtifactStorage(base_dir="test_artifacts", s3_manager=mock_s3_manager)
        
        content = storage.load_artifact_by_reference("s3://bucket/artifacts/user_alice/step_test.json")
        
        assert content == {"data": "loaded from S3"}
        mock_s3_manager.load_artifact.assert_called_once()
    
    def test_load_artifact_by_reference_s3_not_available(self):
        """测试 S3 不可用时加载 S3 URI"""
        storage = ArtifactStorage(base_dir="test_artifacts", s3_manager=None)
        
        with pytest.raises(RuntimeError, match="S3 not available"):
            storage.load_artifact_by_reference("s3://bucket/artifacts/user_alice/step_test.json")


class TestArtifactRecordModel:
    """测试 ArtifactRecord 模型"""
    
    def test_artifact_record_with_content(self):
        """测试 inline 存储的 ArtifactRecord"""
        record = ArtifactRecord(
            artifact_id="test_001",
            turn_number=1,
            artifact_type="explanation",
            topic="Physics",
            summary="Test explanation",
            content={"concept": "Test"},
            content_reference=None
        )
        
        assert record.storage_type == "inline"
        assert not record.has_external_storage
        assert record.get_content_size_estimate() > 0
    
    def test_artifact_record_with_s3_reference(self):
        """测试 S3 存储的 ArtifactRecord"""
        record = ArtifactRecord(
            artifact_id="test_002",
            turn_number=2,
            artifact_type="quiz_set",
            topic="Math",
            summary="Test quiz",
            content=None,
            content_reference="s3://bucket/artifacts/user_alice/step_001.json"
        )
        
        assert record.storage_type == "s3"
        assert record.has_external_storage
        assert record.get_content_size_estimate() == 0
    
    def test_artifact_record_with_local_reference(self):
        """测试本地存储的 ArtifactRecord"""
        record = ArtifactRecord(
            artifact_id="test_003",
            turn_number=3,
            artifact_type="flashcard_set",
            topic="History",
            summary="Test flashcards",
            content=None,
            content_reference="user_alice/step_002.json"
        )
        
        assert record.storage_type == "local"
        assert record.has_external_storage


class TestMemoryManagerArtifactOffloading:
    """测试 MemoryManager 的 Artifact Offloading 功能"""
    
    @pytest.fixture
    def mock_memory_manager(self):
        """创建带 mock ArtifactStorage 的 MemoryManager"""
        with patch('app.core.memory_manager.S3StorageManager') as mock_s3:
            mock_s3.return_value.is_available.return_value = False
            
            manager = MemoryManager(use_s3=False, local_storage_dir="test_memory_storage")
            
            # Mock artifact_storage
            manager.artifact_storage = Mock()
            manager.artifact_storage.save_step_result = Mock(return_value="test/artifact_001.json")
            manager.artifact_storage.load_artifact_by_reference = Mock(return_value={"data": "test"})
            
            yield manager
    
    @pytest.mark.asyncio
    async def test_save_artifact_small_content_inline(self, mock_memory_manager):
        """测试小内容 inline 存储"""
        small_artifact = {"concept": "Test"}  # < 500 bytes
        
        record = await mock_memory_manager.save_artifact(
            session_id="test_session",
            artifact=small_artifact,
            artifact_type="explanation",
            topic="Test",
            user_id="test_user"
        )
        
        assert record.content is not None
        assert record.content_reference is None
        assert record.storage_type == "inline"
        
        # 不应该调用 artifact_storage
        mock_memory_manager.artifact_storage.save_step_result.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_save_artifact_large_content_offload(self, mock_memory_manager):
        """测试大内容卸载"""
        # 创建一个超过 500 bytes 的内容
        large_artifact = {
            "concept": "Test",
            "examples": ["example " + str(i) for i in range(100)]
        }
        
        record = await mock_memory_manager.save_artifact(
            session_id="test_session",
            artifact=large_artifact,
            artifact_type="explanation",
            topic="Test",
            user_id="test_user"
        )
        
        assert record.content is None
        assert record.content_reference is not None
        assert record.storage_type == "local"
        
        # 应该调用 artifact_storage
        mock_memory_manager.artifact_storage.save_step_result.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_artifact_inline(self, mock_memory_manager):
        """测试获取 inline artifact"""
        # 先保存一个小 artifact
        small_artifact = {"concept": "Test"}
        record = await mock_memory_manager.save_artifact(
            session_id="test_session",
            artifact=small_artifact,
            artifact_type="explanation",
            topic="Test",
            user_id="test_user"
        )
        
        # 然后获取
        content = await mock_memory_manager.get_artifact(record.artifact_id)
        
        assert content == small_artifact
        # 不应该调用 artifact_storage
        mock_memory_manager.artifact_storage.load_artifact_by_reference.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_validate_artifact_content_invalid(self, mock_memory_manager):
        """测试无效内容验证"""
        invalid_artifact = "not a dict"
        
        with pytest.raises(ValueError, match="Invalid artifact content"):
            await mock_memory_manager.save_artifact(
                session_id="test_session",
                artifact=invalid_artifact,
                artifact_type="explanation",
                topic="Test",
                user_id="test_user"
            )
    
    def test_generate_artifact_id(self, mock_memory_manager):
        """测试生成 artifact ID"""
        artifact_id = mock_memory_manager._generate_artifact_id("explanation", "Physics")
        
        assert artifact_id.startswith("artifact_explanation_")
        assert "Physics" in artifact_id or "physics" in artifact_id.lower()
    
    def test_generate_summary(self, mock_memory_manager):
        """测试生成摘要"""
        explanation = {"concept": "Photosynthesis"}
        summary = mock_memory_manager._generate_summary(explanation, "explanation")
        assert "Photosynthesis" in summary
        
        quiz = {"questions": [{"q": "Q1"}, {"q": "Q2"}]}
        summary = mock_memory_manager._generate_summary(quiz, "quiz_set")
        assert "2 questions" in summary
        
        flashcards = {"cards": [{"front": "F1"}, {"front": "F2"}, {"front": "F3"}]}
        summary = mock_memory_manager._generate_summary(flashcards, "flashcard_set")
        assert "3 cards" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

