"""
Task 2.4 测试 - Skill Registry 测试

测试内容：
1. SkillRegistry 初始化和加载
2. 根据 ID 获取 Skill
3. 根据 intent 获取 Skills
4. 列出所有 Skills
5. 依赖验证
6. 错误处理
"""
import pytest
import os
import tempfile
import yaml

from app.core.skill_registry import SkillRegistry
from app.models.skill import SkillDefinition


# 测试用的 Skill 配置
SAMPLE_QUIZ_SKILL = {
    "id": "test_quiz_skill",
    "display_name": "测试练习题",
    "version": "1.0.0",
    "intent_tags": ["quiz", "practice"],
    "input_schema": {"type": "object", "properties": {}},
    "output_schema": {"type": "object", "properties": {}},
    "models": {"primary": "gemini-2.5-flash", "fallback": "gemini-2.0-flash-exp"},
    "context": {"need_user_memory": True, "need_content_store": True, "retrieve_top_k": 3},
    "cost": {"model_class": "medium", "context_size": "medium", "expected_rounds": 1},
    "composable": True,
    "dependencies": [],
    "prompt_file": "quiz_generation_skill.txt"
}

SAMPLE_EXPLAIN_SKILL = {
    "id": "test_explain_skill",
    "display_name": "测试讲解",
    "version": "1.0.0",
    "intent_tags": ["explain", "concept"],
    "input_schema": {"type": "object", "properties": {}},
    "output_schema": {"type": "object", "properties": {}},
    "models": {"primary": "gemini-2.5-flash"},
    "context": {"need_user_memory": True},
    "cost": {"model_class": "small", "context_size": "small", "expected_rounds": 1},
    "composable": False,
    "dependencies": [],
    "prompt_file": "concept_explain_skill.txt"
}


@pytest.fixture
def temp_config_dir():
    """创建临时配置目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 写入测试配置文件
        quiz_path = os.path.join(tmpdir, "quiz_skill.yaml")
        with open(quiz_path, 'w', encoding='utf-8') as f:
            yaml.dump(SAMPLE_QUIZ_SKILL, f)
        
        explain_path = os.path.join(tmpdir, "explain_skill.yaml")
        with open(explain_path, 'w', encoding='utf-8') as f:
            yaml.dump(SAMPLE_EXPLAIN_SKILL, f)
        
        yield tmpdir


class TestSkillRegistryInitialization:
    """测试 SkillRegistry 初始化"""
    
    def test_registry_initialization(self, temp_config_dir):
        """测试正常初始化"""
        registry = SkillRegistry(config_dir=temp_config_dir)
        
        assert registry is not None
        assert len(registry.get_skill_ids()) == 2
        assert "test_quiz_skill" in registry.get_skill_ids()
        assert "test_explain_skill" in registry.get_skill_ids()
    
    def test_registry_with_nonexistent_dir(self):
        """测试不存在的配置目录"""
        registry = SkillRegistry(config_dir="/nonexistent/path")
        
        assert len(registry.get_skill_ids()) == 0


class TestSkillRetrieval:
    """测试 Skill 检索"""
    
    def test_get_skill_by_id(self, temp_config_dir):
        """测试根据 ID 获取 Skill"""
        registry = SkillRegistry(config_dir=temp_config_dir)
        
        skill = registry.get_skill("test_quiz_skill")
        
        assert skill is not None
        assert skill.id == "test_quiz_skill"
        assert skill.display_name == "测试练习题"
        assert isinstance(skill, SkillDefinition)
    
    def test_get_nonexistent_skill(self, temp_config_dir):
        """测试获取不存在的 Skill"""
        registry = SkillRegistry(config_dir=temp_config_dir)
        
        skill = registry.get_skill("nonexistent_skill")
        
        assert skill is None
    
    def test_get_skills_by_intent(self, temp_config_dir):
        """测试根据 intent 获取 Skills"""
        registry = SkillRegistry(config_dir=temp_config_dir)
        
        # 获取 quiz intent 的 skills
        quiz_skills = registry.get_skills_by_intent("quiz")
        
        assert len(quiz_skills) == 1
        assert quiz_skills[0].id == "test_quiz_skill"
    
    def test_get_skills_by_shared_intent(self, temp_config_dir):
        """测试多个 Skills 共享同一 intent"""
        registry = SkillRegistry(config_dir=temp_config_dir)
        
        # practice 只有 quiz_skill 有
        practice_skills = registry.get_skills_by_intent("practice")
        assert len(practice_skills) == 1
        
        # explain 只有 explain_skill 有
        explain_skills = registry.get_skills_by_intent("explain")
        assert len(explain_skills) == 1
    
    def test_get_skills_by_nonexistent_intent(self, temp_config_dir):
        """测试不存在的 intent"""
        registry = SkillRegistry(config_dir=temp_config_dir)
        
        skills = registry.get_skills_by_intent("nonexistent")
        
        assert len(skills) == 0


class TestSkillListing:
    """测试 Skill 列表功能"""
    
    def test_list_all_skills(self, temp_config_dir):
        """测试列出所有 Skills"""
        registry = SkillRegistry(config_dir=temp_config_dir)
        
        all_skills = registry.list_all_skills()
        
        assert len(all_skills) == 2
        skill_ids = [s.id for s in all_skills]
        assert "test_quiz_skill" in skill_ids
        assert "test_explain_skill" in skill_ids
    
    def test_get_skill_ids(self, temp_config_dir):
        """测试获取所有 Skill IDs"""
        registry = SkillRegistry(config_dir=temp_config_dir)
        
        skill_ids = registry.get_skill_ids()
        
        assert len(skill_ids) == 2
        assert "test_quiz_skill" in skill_ids
        assert "test_explain_skill" in skill_ids
    
    def test_get_all_intents(self, temp_config_dir):
        """测试获取所有 intents"""
        registry = SkillRegistry(config_dir=temp_config_dir)
        
        intents = registry.get_all_intents()
        
        # 应该有 quiz, practice, explain, concept
        assert len(intents) >= 3
        assert "quiz" in intents
        assert "explain" in intents


class TestSkillProperties:
    """测试 Skill 属性"""
    
    def test_composable_skills(self, temp_config_dir):
        """测试获取可组合的 Skills"""
        registry = SkillRegistry(config_dir=temp_config_dir)
        
        composable = registry.get_composable_skills()
        
        # 只有 quiz_skill 是可组合的
        assert len(composable) == 1
        assert composable[0].id == "test_quiz_skill"
    
    def test_skill_models(self, temp_config_dir):
        """测试 Skill 的模型配置"""
        registry = SkillRegistry(config_dir=temp_config_dir)
        
        skill = registry.get_skill("test_quiz_skill")
        
        assert skill.models["primary"] == "gemini-2.5-flash"
        assert skill.models["fallback"] == "gemini-2.0-flash-exp"
    
    def test_skill_context_requirements(self, temp_config_dir):
        """测试 Skill 的上下文需求"""
        registry = SkillRegistry(config_dir=temp_config_dir)
        
        quiz_skill = registry.get_skill("test_quiz_skill")
        explain_skill = registry.get_skill("test_explain_skill")
        
        assert quiz_skill.context["need_user_memory"] is True
        assert quiz_skill.context["need_content_store"] is True
        assert quiz_skill.context["retrieve_top_k"] == 3
        
        assert explain_skill.context["need_user_memory"] is True
        # explain_skill 使用默认值
        assert explain_skill.context.get("need_content_store", False) is False


class TestSkillDependencies:
    """测试 Skill 依赖"""
    
    def test_validate_skill_without_dependencies(self, temp_config_dir):
        """测试没有依赖的 Skill 验证"""
        registry = SkillRegistry(config_dir=temp_config_dir)
        
        is_valid = registry.validate_skill_dependencies("test_quiz_skill")
        
        assert is_valid is True
    
    def test_validate_nonexistent_skill(self, temp_config_dir):
        """测试不存在的 Skill 验证"""
        registry = SkillRegistry(config_dir=temp_config_dir)
        
        is_valid = registry.validate_skill_dependencies("nonexistent")
        
        assert is_valid is False
    
    def test_skill_with_missing_dependency(self, temp_config_dir):
        """测试缺少依赖的 Skill"""
        # 创建一个有依赖的 skill
        dependent_skill = {
            "id": "dependent_skill",
            "display_name": "依赖测试",
            "version": "1.0.0",
            "intent_tags": ["test"],
            "input_schema": {"type": "object"},
            "output_schema": {"type": "object"},
            "models": {"primary": "gemini-2.5-flash"},
            "context": {},
            "cost": {"model_class": "small"},
            "composable": False,
            "dependencies": ["missing_skill"],  # 依赖一个不存在的 skill
            "prompt_file": "test.txt"
        }
        
        # 写入文件
        dep_path = os.path.join(temp_config_dir, "dependent.yaml")
        with open(dep_path, 'w', encoding='utf-8') as f:
            yaml.dump(dependent_skill, f)
        
        registry = SkillRegistry(config_dir=temp_config_dir)
        
        # 验证应该失败
        is_valid = registry.validate_skill_dependencies("dependent_skill")
        assert is_valid is False


class TestSkillReload:
    """测试 Skill 重新加载"""
    
    def test_reload_skills(self, temp_config_dir):
        """测试重新加载 Skills"""
        registry = SkillRegistry(config_dir=temp_config_dir)
        
        # 初始应该有 2 个 skills
        assert len(registry.get_skill_ids()) == 2
        
        # 添加一个新的 skill 文件
        new_skill = {
            "id": "new_skill",
            "display_name": "新 Skill",
            "version": "1.0.0",
            "intent_tags": ["new"],
            "input_schema": {"type": "object"},
            "output_schema": {"type": "object"},
            "models": {"primary": "gemini-2.5-flash"},
            "context": {},
            "cost": {"model_class": "small"},
            "composable": False,
            "dependencies": [],
            "prompt_file": "new.txt"
        }
        
        new_path = os.path.join(temp_config_dir, "new_skill.yaml")
        with open(new_path, 'w', encoding='utf-8') as f:
            yaml.dump(new_skill, f)
        
        # 重新加载
        registry.reload()
        
        # 现在应该有 3 个 skills
        assert len(registry.get_skill_ids()) == 3
        assert "new_skill" in registry.get_skill_ids()


class TestRealSkillsConfig:
    """测试实际的 Skills 配置"""
    
    def test_load_real_quiz_skill(self):
        """测试加载真实的 quiz_skill.yaml"""
        # 使用实际的配置目录
        registry = SkillRegistry()
        
        quiz_skill = registry.get_skill("quiz_skill")
        
        # 如果配置文件存在，验证其内容
        if quiz_skill:
            assert quiz_skill.id == "quiz_skill"
            assert "quiz" in quiz_skill.intent_tags
            assert quiz_skill.prompt_file == "quiz_generation_skill.txt"
    
    def test_load_real_explain_skill(self):
        """测试加载真实的 explain_skill.yaml"""
        registry = SkillRegistry()
        
        explain_skill = registry.get_skill("explain_skill")
        
        # 如果配置文件存在，验证其内容
        if explain_skill:
            assert explain_skill.id == "explain_skill"
            assert "explain" in explain_skill.intent_tags
            assert explain_skill.prompt_file == "concept_explain_skill.txt"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

