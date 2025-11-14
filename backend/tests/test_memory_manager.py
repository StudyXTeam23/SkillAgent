"""
Task 2.3 测试 - Memory Manager 测试

测试内容：
1. MemoryManager 初始化
2. 用户画像管理（get/update）
3. 会话上下文管理（get/update）
4. 记忆摘要生成
"""
import pytest
from datetime import datetime

from app.core.memory_manager import MemoryManager
from app.models.memory import UserLearningProfile, SessionContext
from app.models.intent import MemorySummary


class TestMemoryManagerInitialization:
    """测试 MemoryManager 初始化"""
    
    def test_manager_initialization_in_memory(self):
        """测试内存模式初始化"""
        manager = MemoryManager(use_s3=False)
        
        assert manager is not None
        assert manager.use_s3 is False
        assert isinstance(manager._user_profiles, dict)
        assert isinstance(manager._session_contexts, dict)
    
    def test_manager_initialization_with_s3(self):
        """测试 S3 模式初始化"""
        manager = MemoryManager(use_s3=True)
        
        assert manager.use_s3 is True


class TestUserProfileManagement:
    """测试用户画像管理"""
    
    @pytest.mark.asyncio
    async def test_get_new_user_profile(self):
        """测试获取新用户画像（自动创建）"""
        manager = MemoryManager(use_s3=False)
        
        profile = await manager.get_user_profile("user_001")
        
        assert profile.user_id == "user_001"
        assert profile.mastery == {}
        assert profile.preferences == {}
        assert profile.history["quiz_sessions"] == 0
        assert isinstance(profile.updated_at, datetime)
    
    @pytest.mark.asyncio
    async def test_get_existing_user_profile(self):
        """测试获取已存在的用户画像"""
        manager = MemoryManager(use_s3=False)
        
        # 第一次获取（创建）
        profile1 = await manager.get_user_profile("user_002")
        
        # 第二次获取（应该返回同一个对象）
        profile2 = await manager.get_user_profile("user_002")
        
        assert profile1.user_id == profile2.user_id
    
    @pytest.mark.asyncio
    async def test_update_user_profile(self):
        """测试更新用户画像"""
        manager = MemoryManager(use_s3=False)
        
        # 获取初始画像
        profile = await manager.get_user_profile("user_003")
        
        # 修改画像
        profile.mastery["math"] = "strong"
        profile.preferences["preferred_artifact"] = "quiz"
        profile.history["quiz_sessions"] = 5
        
        # 更新
        updated_profile = await manager.update_user_profile("user_003", profile)
        
        assert updated_profile.mastery["math"] == "strong"
        assert updated_profile.preferences["preferred_artifact"] == "quiz"
        assert updated_profile.history["quiz_sessions"] == 5
        
        # 验证更新时间被刷新
        assert isinstance(updated_profile.updated_at, datetime)
    
    @pytest.mark.asyncio
    async def test_multiple_users(self):
        """测试管理多个用户"""
        manager = MemoryManager(use_s3=False)
        
        user1 = await manager.get_user_profile("user_a")
        user2 = await manager.get_user_profile("user_b")
        
        # 修改 user1
        user1.mastery["topic1"] = "weak"
        await manager.update_user_profile("user_a", user1)
        
        # user2 应该不受影响
        user2_check = await manager.get_user_profile("user_b")
        assert "topic1" not in user2_check.mastery


class TestSessionContextManagement:
    """测试会话上下文管理"""
    
    @pytest.mark.asyncio
    async def test_get_new_session_context(self):
        """测试获取新会话上下文（自动创建）"""
        manager = MemoryManager(use_s3=False)
        
        context = await manager.get_session_context("session_001")
        
        assert context.session_id == "session_001"
        assert context.current_topic is None
        assert context.recent_intents == []
        assert context.last_artifact is None
        assert context.last_user_message == ""
    
    @pytest.mark.asyncio
    async def test_update_session_context(self):
        """测试更新会话上下文"""
        manager = MemoryManager(use_s3=False)
        
        # 获取初始上下文
        context = await manager.get_session_context("session_002")
        
        # 修改上下文
        context.current_topic = "微积分-极限"
        context.recent_intents = ["quiz", "explain"]
        context.last_artifact = "quiz_set"
        context.last_user_message = "给我几道题"
        
        # 更新
        updated_context = await manager.update_session_context("session_002", context)
        
        assert updated_context.current_topic == "微积分-极限"
        assert updated_context.recent_intents == ["quiz", "explain"]
        assert updated_context.last_artifact == "quiz_set"
    
    @pytest.mark.asyncio
    async def test_multiple_sessions(self):
        """测试管理多个会话"""
        manager = MemoryManager(use_s3=False)
        
        session1 = await manager.get_session_context("session_a")
        session2 = await manager.get_session_context("session_b")
        
        # 修改 session1
        session1.current_topic = "topic_a"
        await manager.update_session_context("session_a", session1)
        
        # session2 应该不受影响
        session2_check = await manager.get_session_context("session_b")
        assert session2_check.current_topic is None


class TestMemorySummaryGeneration:
    """测试记忆摘要生成"""
    
    @pytest.mark.asyncio
    async def test_generate_summary_for_new_user(self):
        """测试为新用户生成摘要"""
        manager = MemoryManager(use_s3=False)
        
        summary = await manager.generate_memory_summary("user_new", "session_new")
        
        assert isinstance(summary, MemorySummary)
        assert summary.topic_hint is None
        assert summary.user_mastery_hint is None
        assert summary.recent_behavior == "新用户"
    
    @pytest.mark.asyncio
    async def test_generate_summary_with_topic(self):
        """测试带主题的摘要生成"""
        manager = MemoryManager(use_s3=False)
        
        # 设置会话上下文
        context = await manager.get_session_context("session_with_topic")
        context.current_topic = "微积分-极限"
        await manager.update_session_context("session_with_topic", context)
        
        # 生成摘要
        summary = await manager.generate_memory_summary("user_topic", "session_with_topic")
        
        assert summary.topic_hint == "微积分-极限"
    
    @pytest.mark.asyncio
    async def test_generate_summary_with_mastery(self):
        """测试带掌握度的摘要生成"""
        manager = MemoryManager(use_s3=False)
        
        # 设置用户画像
        profile = await manager.get_user_profile("user_mastery")
        profile.mastery["微积分-极限"] = "weak"
        await manager.update_user_profile("user_mastery", profile)
        
        # 设置会话上下文
        context = await manager.get_session_context("session_mastery")
        context.current_topic = "微积分-极限"
        await manager.update_session_context("session_mastery", context)
        
        # 生成摘要
        summary = await manager.generate_memory_summary("user_mastery", "session_mastery")
        
        assert summary.topic_hint == "微积分-极限"
        assert summary.user_mastery_hint == "weak"
    
    @pytest.mark.asyncio
    async def test_generate_summary_with_recent_behavior(self):
        """测试带最近行为的摘要生成"""
        manager = MemoryManager(use_s3=False)
        
        # 设置会话上下文
        context = await manager.get_session_context("session_behavior")
        context.recent_intents = ["quiz", "explain"]
        await manager.update_session_context("session_behavior", context)
        
        # 设置用户画像
        profile = await manager.get_user_profile("user_behavior")
        profile.history["quiz_sessions"] = 3
        await manager.update_user_profile("user_behavior", profile)
        
        # 生成摘要
        summary = await manager.generate_memory_summary("user_behavior", "session_behavior")
        
        assert "练习" in summary.recent_behavior or "讲解" in summary.recent_behavior
    
    @pytest.mark.asyncio
    async def test_generate_summary_with_preferences(self):
        """测试带用户偏好的摘要生成"""
        manager = MemoryManager(use_s3=False)
        
        # 设置用户画像
        profile = await manager.get_user_profile("user_pref")
        profile.preferences["preferred_artifact"] = "quiz"
        await manager.update_user_profile("user_pref", profile)
        
        # 生成摘要
        summary = await manager.generate_memory_summary("user_pref", "session_pref")
        
        assert "练习" in summary.recent_behavior


class TestBehaviorDescription:
    """测试行为描述生成"""
    
    def test_behavior_description_with_quiz_intent(self):
        """测试带 quiz 意图的行为描述"""
        manager = MemoryManager(use_s3=False)
        
        profile = UserLearningProfile(user_id="test", mastery={}, preferences={}, history={})
        context = SessionContext(
            session_id="test",
            current_topic=None,
            recent_intents=["quiz"],
            last_artifact=None,
            last_user_message=""
        )
        
        description = manager._generate_behavior_description(profile, context)
        
        assert "练习" in description
    
    def test_behavior_description_with_explain_intent(self):
        """测试带 explain 意图的行为描述"""
        manager = MemoryManager(use_s3=False)
        
        profile = UserLearningProfile(user_id="test", mastery={}, preferences={}, history={})
        context = SessionContext(
            session_id="test",
            current_topic=None,
            recent_intents=["explain"],
            last_artifact=None,
            last_user_message=""
        )
        
        description = manager._generate_behavior_description(profile, context)
        
        assert "讲解" in description
    
    def test_behavior_description_new_user(self):
        """测试新用户行为描述"""
        manager = MemoryManager(use_s3=False)
        
        profile = UserLearningProfile(user_id="test", mastery={}, preferences={}, history={})
        context = SessionContext(
            session_id="test",
            current_topic=None,
            recent_intents=[],
            last_artifact=None,
            last_user_message=""
        )
        
        description = manager._generate_behavior_description(profile, context)
        
        assert description == "新用户"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

