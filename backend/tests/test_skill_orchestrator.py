"""
Task 2.5 测试 - Skill Orchestrator 测试

测试内容：
1. SkillOrchestrator 初始化
2. 技能选择
3. 上下文构建
4. 输入参数构建
5. Prompt 加载和格式化
6. 错误处理
7. 完整编排流程（集成测试）
"""
import pytest
import os
import tempfile
import yaml
from unittest.mock import Mock, AsyncMock, patch

from app.core.skill_orchestrator import SkillOrchestrator
from app.core.skill_registry import SkillRegistry
from app.core.memory_manager import MemoryManager
from app.models.intent import IntentResult, MemorySummary
from app.models.skill import SkillDefinition
from app.services.gemini import GeminiClient


# 测试用的简单 Skill 配置
SIMPLE_SKILL = {
    "id": "test_skill",
    "display_name": "测试技能",
    "version": "1.0.0",
    "intent_tags": ["test"],
    "input_schema": {"type": "object"},
    "output_schema": {"type": "object"},
    "models": {"primary": "gemini-2.5-flash"},
    "context": {"need_user_memory": True},
    "cost": {"model_class": "small"},
    "composable": False,
    "dependencies": [],
    "prompt_file": "test_prompt.txt"
}


@pytest.fixture
def temp_skill_config():
    """创建临时 Skill 配置"""
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_path = os.path.join(tmpdir, "test_skill.yaml")
        with open(skill_path, 'w', encoding='utf-8') as f:
            yaml.dump(SIMPLE_SKILL, f)
        yield tmpdir


@pytest.fixture
def temp_prompt_dir():
    """创建临时 Prompt 目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        prompt_path = os.path.join(tmpdir, "test_prompt.txt")
        with open(prompt_path, 'w', encoding='utf-8') as f:
            f.write("Test prompt template\nInput: {params}")
        yield tmpdir


class TestOrchestratorInitialization:
    """测试 Orchestrator 初始化"""
    
    def test_orchestrator_initialization(self):
        """测试基本初始化"""
        orchestrator = SkillOrchestrator()
        
        assert orchestrator is not None
        assert orchestrator.skill_registry is not None
        assert orchestrator.gemini_client is not None
        assert orchestrator.memory_manager is not None
    
    def test_orchestrator_with_custom_components(self, temp_skill_config):
        """测试使用自定义组件初始化"""
        registry = SkillRegistry(config_dir=temp_skill_config)
        gemini = GeminiClient()
        memory = MemoryManager(use_s3=False)
        
        orchestrator = SkillOrchestrator(
            skill_registry=registry,
            gemini_client=gemini,
            memory_manager=memory
        )
        
        assert orchestrator.skill_registry is registry
        assert orchestrator.gemini_client is gemini
        assert orchestrator.memory_manager is memory


class TestSkillSelection:
    """测试技能选择"""
    
    def test_select_skill_with_valid_intent(self, temp_skill_config):
        """测试选择有效的技能"""
        registry = SkillRegistry(config_dir=temp_skill_config)
        orchestrator = SkillOrchestrator(skill_registry=registry)
        
        intent_result = IntentResult(
            intent="test",
            topic="测试主题",
            confidence=0.9,
            raw_text="测试文本"
        )
        
        skill = orchestrator._select_skill(intent_result)
        
        assert skill is not None
        assert skill.id == "test_skill"
    
    def test_select_skill_with_invalid_intent(self, temp_skill_config):
        """测试选择不存在的意图"""
        registry = SkillRegistry(config_dir=temp_skill_config)
        orchestrator = SkillOrchestrator(skill_registry=registry)
        
        intent_result = IntentResult(
            intent="nonexistent",
            topic=None,
            confidence=0.5,
            raw_text=""
        )
        
        skill = orchestrator._select_skill(intent_result)
        
        assert skill is None
    
    def test_select_skill_with_multiple_intents(self, temp_skill_config):
        """测试多意图选择"""
        registry = SkillRegistry(config_dir=temp_skill_config)
        orchestrator = SkillOrchestrator(skill_registry=registry)
        
        intent_result = IntentResult(
            intent=["test", "other"],  # 多个意图
            topic=None,
            confidence=0.8,
            raw_text=""
        )
        
        skill = orchestrator._select_skill(intent_result)
        
        # 应该选择第一个匹配的
        assert skill is not None
        assert skill.id == "test_skill"


class TestContextBuilding:
    """测试上下文构建"""
    
    @pytest.mark.asyncio
    async def test_build_context_with_memory(self, temp_skill_config):
        """测试构建包含记忆的上下文"""
        registry = SkillRegistry(config_dir=temp_skill_config)
        memory_manager = MemoryManager(use_s3=False)
        orchestrator = SkillOrchestrator(
            skill_registry=registry,
            memory_manager=memory_manager
        )
        
        skill = registry.get_skill("test_skill")
        
        context = await orchestrator._build_context(skill, "user_1", "session_1")
        
        assert "user_profile" in context
        assert "session_context" in context
        assert "memory_summary" in context
    
    @pytest.mark.asyncio
    async def test_build_context_without_memory_requirement(self):
        """测试不需要记忆的上下文构建"""
        # 创建一个不需要记忆的 skill
        skill = SkillDefinition(
            id="no_memory_skill",
            display_name="无记忆技能",
            version="1.0.0",
            intent_tags=["test"],
            input_schema={},
            output_schema={},
            models={"primary": "gemini-2.5-flash"},
            context={"need_user_memory": False},  # 不需要记忆
            cost={},
            composable=False,
            dependencies=[]
        )
        
        orchestrator = SkillOrchestrator()
        
        context = await orchestrator._build_context(skill, "user_1", "session_1")
        
        # 不应该包含记忆相关的内容
        assert "user_profile" not in context
        assert "memory_summary" not in context


class TestInputParamsBuilding:
    """测试输入参数构建"""
    
    def test_build_input_params_basic(self):
        """测试基本参数构建"""
        orchestrator = SkillOrchestrator()
        
        intent_result = IntentResult(
            intent="test",
            topic="数学-微积分-极限",
            confidence=0.9,
            raw_text=""
        )
        
        context = {"memory_summary": "用户正在学习极限"}
        
        skill = SkillDefinition(
            id="test",
            display_name="测试",
            version="1.0.0",
            intent_tags=["test"],
            input_schema={},
            output_schema={},
            models={},
            context={},
            cost={},
            composable=False,
            dependencies=[]
        )
        
        params = orchestrator._build_input_params(skill, intent_result, context, None)
        
        assert params["topic"] == "数学-微积分-极限"
        assert params["memory_summary"] == "用户正在学习极限"
    
    def test_build_input_params_with_additional(self):
        """测试包含额外参数"""
        orchestrator = SkillOrchestrator()
        
        intent_result = IntentResult(
            intent="quiz",
            topic="数学",
            confidence=0.9,
            raw_text=""
        )
        
        context = {}
        
        skill = SkillDefinition(
            id="test",
            display_name="测试",
            version="1.0.0",
            intent_tags=["test"],
            input_schema={},
            output_schema={},
            models={},
            context={},
            cost={},
            composable=False,
            dependencies=[]
        )
        
        additional = {"difficulty": "easy", "num_questions": 5}
        
        params = orchestrator._build_input_params(skill, intent_result, context, additional)
        
        assert params["topic"] == "数学"
        assert params["difficulty"] == "easy"
        assert params["num_questions"] == 5


class TestPromptHandling:
    """测试 Prompt 处理"""
    
    def test_load_prompt_success(self, temp_skill_config, temp_prompt_dir):
        """测试成功加载 Prompt"""
        registry = SkillRegistry(config_dir=temp_skill_config)
        orchestrator = SkillOrchestrator(skill_registry=registry)
        orchestrator.prompts_dir = temp_prompt_dir
        
        skill = registry.get_skill("test_skill")
        
        prompt_content = orchestrator._load_prompt(skill)
        
        assert "Test prompt template" in prompt_content
    
    def test_load_prompt_file_not_found(self):
        """测试 Prompt 文件不存在"""
        orchestrator = SkillOrchestrator()
        
        skill = SkillDefinition(
            id="test",
            display_name="测试",
            version="1.0.0",
            intent_tags=["test"],
            input_schema={},
            output_schema={},
            models={},
            context={},
            cost={},
            composable=False,
            dependencies=[],
            prompt_file="nonexistent.txt"
        )
        
        with pytest.raises(FileNotFoundError):
            orchestrator._load_prompt(skill)
    
    def test_format_prompt(self):
        """测试 Prompt 格式化"""
        orchestrator = SkillOrchestrator()
        
        prompt_template = "Generate a quiz about {topic}"
        params = {"topic": "数学", "difficulty": "easy"}
        context = {}
        
        formatted = orchestrator._format_prompt(prompt_template, params, context)
        
        assert "Generate a quiz about {topic}" in formatted
        assert '"topic": "数学"' in formatted
        assert '"difficulty": "easy"' in formatted


class TestOutputWrapping:
    """测试输出封装"""
    
    def test_wrap_output(self):
        """测试封装输出"""
        orchestrator = SkillOrchestrator()
        
        skill = SkillDefinition(
            id="quiz_skill",
            display_name="练习题生成",
            version="1.0.0",
            intent_tags=["quiz"],
            input_schema={},
            output_schema={},
            models={},
            context={},
            cost={},
            composable=False,
            dependencies=[]
        )
        
        result = {"questions": [{"question": "测试题目"}]}
        
        wrapped = orchestrator._wrap_output(skill, result)
        
        assert wrapped["success"] is True
        assert wrapped["skill_id"] == "quiz_skill"
        assert wrapped["skill_name"] == "练习题生成"
        assert wrapped["result"] == result


class TestMemoryUpdate:
    """测试记忆更新"""
    
    @pytest.mark.asyncio
    async def test_update_memory_success(self):
        """测试成功更新记忆"""
        memory_manager = MemoryManager(use_s3=False)
        orchestrator = SkillOrchestrator(memory_manager=memory_manager)
        
        intent_result = IntentResult(
            intent="quiz",
            topic="数学-微积分-极限",
            confidence=0.9,
            raw_text=""
        )
        
        skill_result = {"questions": []}
        
        # 应该不会抛出异常
        await orchestrator._update_memory("user_1", "session_1", intent_result, skill_result)
        
        # 验证记忆已更新
        session = await memory_manager.get_session_context("session_1")
        assert session.current_topic == "数学-微积分-极限"
        assert "quiz" in session.recent_intents


class TestErrorHandling:
    """测试错误处理"""
    
    def test_create_error_response(self):
        """测试创建错误响应"""
        orchestrator = SkillOrchestrator()
        
        error_response = orchestrator._create_error_response(
            "no_skill_found",
            "未找到匹配的技能"
        )
        
        assert error_response["success"] is False
        assert error_response["error"] == "no_skill_found"
        assert error_response["message"] == "未找到匹配的技能"
    
    @pytest.mark.asyncio
    async def test_execute_with_invalid_intent(self, temp_skill_config):
        """测试无效意图的执行"""
        registry = SkillRegistry(config_dir=temp_skill_config)
        orchestrator = SkillOrchestrator(skill_registry=registry)
        
        intent_result = IntentResult(
            intent="invalid_intent",
            topic=None,
            confidence=0.5,
            raw_text=""
        )
        
        result = await orchestrator.execute(intent_result, "user_1", "session_1")
        
        assert result["success"] is False
        assert result["error"] == "no_skill_found"


class TestFullOrchestration:
    """测试完整编排流程（集成测试）"""
    
    @pytest.mark.asyncio
    async def test_full_orchestration_flow(self, temp_skill_config, temp_prompt_dir):
        """测试完整的编排流程"""
        # 设置组件
        registry = SkillRegistry(config_dir=temp_skill_config)
        memory_manager = MemoryManager(use_s3=False)
        gemini_client = Mock(spec=GeminiClient)
        gemini_client.generate_json = AsyncMock(return_value={"result": "success"})
        
        orchestrator = SkillOrchestrator(
            skill_registry=registry,
            gemini_client=gemini_client,
            memory_manager=memory_manager
        )
        orchestrator.prompts_dir = temp_prompt_dir
        
        # 执行
        intent_result = IntentResult(
            intent="test",
            topic="测试主题",
            confidence=0.9,
            raw_text="测试输入"
        )
        
        result = await orchestrator.execute(
            intent_result,
            "user_test",
            "session_test",
            additional_params={"param1": "value1"}
        )
        
        # 验证结果
        assert result["success"] is True
        assert result["skill_id"] == "test_skill"
        assert result["result"]["result"] == "success"
        
        # 验证 Gemini 被调用
        assert gemini_client.generate_json.called


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

