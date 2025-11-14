"""
Task 1.2 测试 - 测试 Pydantic 数据模型

测试内容：
1. Intent 模型（IntentResult, MemorySummary）
2. Memory 模型（UserLearningProfile, SessionContext）
3. Skill 模型（SkillDefinition）
4. Artifact 模型（Artifact, QuizSetArtifact, ExplanationArtifact）
5. API 模型（AgentChatRequest, AgentChatResponse）
"""
import pytest
from pydantic import ValidationError
from datetime import datetime

from app.models import (
    IntentResult, MemorySummary,
    UserLearningProfile, SessionContext,
    SkillDefinition,
    Artifact, QuizSetArtifact, Question, ExplanationArtifact, Example,
    AgentChatRequest, AgentChatResponse
)


class TestIntentModels:
    """测试意图相关模型"""
    
    def test_memory_summary_creation(self):
        """测试 MemorySummary 创建"""
        summary = MemorySummary(
            topic_hint="微积分-极限",
            user_mastery_hint="weak",
            recent_behavior="用户刚做过练习"
        )
        
        assert summary.topic_hint == "微积分-极限"
        assert summary.user_mastery_hint == "weak"
        assert summary.recent_behavior == "用户刚做过练习"
    
    def test_memory_summary_defaults(self):
        """测试 MemorySummary 默认值"""
        summary = MemorySummary()
        
        assert summary.topic_hint is None
        assert summary.user_mastery_hint is None
        assert summary.recent_behavior == ""
    
    def test_intent_result_creation(self):
        """测试 IntentResult 创建"""
        intent = IntentResult(
            intent="quiz",
            topic="微积分-极限",
            target_artifact="quiz_set",
            confidence=0.92,
            raw_text="给我几道练习题"
        )
        
        assert intent.intent == "quiz"
        assert intent.topic == "微积分-极限"
        assert intent.confidence == 0.92
    
    def test_intent_result_validation(self):
        """测试 IntentResult 字段验证"""
        # 置信度超出范围
        with pytest.raises(ValidationError):
            IntentResult(
                intent="quiz",
                confidence=1.5,  # 超过 1.0
                raw_text="test"
            )
        
        # 置信度为负数
        with pytest.raises(ValidationError):
            IntentResult(
                intent="quiz",
                confidence=-0.1,  # 小于 0.0
                raw_text="test"
            )
    
    def test_intent_result_multiple_intents(self):
        """测试多个意图"""
        intent = IntentResult(
            intent=["quiz", "explain"],
            topic="微积分",
            confidence=0.75,
            raw_text="给我讲讲然后出几道题"
        )
        
        assert isinstance(intent.intent, list)
        assert len(intent.intent) == 2


class TestMemoryModels:
    """测试记忆相关模型"""
    
    def test_user_learning_profile_creation(self):
        """测试 UserLearningProfile 创建"""
        profile = UserLearningProfile(
            user_id="user_123",
            mastery={"微积分-极限": "weak"},
            preferences={"preferred_artifact": "quiz"}
        )
        
        assert profile.user_id == "user_123"
        assert profile.mastery["微积分-极限"] == "weak"
        assert profile.preferences["preferred_artifact"] == "quiz"
        assert isinstance(profile.updated_at, datetime)
    
    def test_user_learning_profile_defaults(self):
        """测试 UserLearningProfile 默认值"""
        profile = UserLearningProfile(user_id="test_user")
        
        assert profile.mastery == {}
        assert profile.preferences == {}
        assert profile.history["quiz_sessions"] == 0
        assert profile.history["topics_visited"] == []
    
    def test_session_context_creation(self):
        """测试 SessionContext 创建"""
        session = SessionContext(
            session_id="session_456",
            current_topic="微积分-极限",
            recent_intents=["quiz", "explain"]
        )
        
        assert session.session_id == "session_456"
        assert session.current_topic == "微积分-极限"
        assert len(session.recent_intents) == 2
        assert isinstance(session.updated_at, datetime)


class TestSkillModels:
    """测试技能相关模型"""
    
    def test_skill_definition_creation(self):
        """测试 SkillDefinition 创建"""
        skill = SkillDefinition(
            id="quiz",
            display_name="练习题生成",
            intent_tags=["quiz"],
            input_schema={"type": "object", "properties": {}},
            output_schema={"type": "object", "properties": {}},
            models={"primary": "gemini-2.5-flash"}
        )
        
        assert skill.id == "quiz"
        assert skill.display_name == "练习题生成"
        assert "quiz" in skill.intent_tags
        assert skill.version == "1.0.0"  # 默认值
        assert skill.composable is True  # 默认值
    
    def test_skill_definition_validation(self):
        """测试 SkillDefinition 必填字段"""
        with pytest.raises(ValidationError):
            SkillDefinition(
                id="test"
                # 缺少其他必填字段
            )


class TestArtifactModels:
    """测试产物相关模型"""
    
    def test_artifact_creation(self):
        """测试通用 Artifact 创建"""
        artifact = Artifact(
            type="quiz_set",
            payload={"questions": []},
            meta={"source_skill": "quiz"}
        )
        
        assert artifact.type == "quiz_set"
        assert artifact.payload == {"questions": []}
        assert artifact.meta["source_skill"] == "quiz"
    
    def test_question_creation(self):
        """测试 Question 创建"""
        question = Question(
            id="q1",
            stem="What is 2+2?",
            options=["3", "4", "5"],
            answer="4",
            explanation="Basic math"
        )
        
        assert question.id == "q1"
        assert question.stem == "What is 2+2?"
        assert len(question.options) == 3
        assert question.answer == "4"
    
    def test_question_validation(self):
        """测试 Question 选项数量验证"""
        with pytest.raises(ValidationError):
            Question(
                id="q1",
                stem="Question?",
                options=["Only one"],  # 少于 2 个选项
                answer="Only one",
                explanation="Test"
            )
    
    def test_quiz_set_artifact_creation(self):
        """测试 QuizSetArtifact 创建"""
        quiz_set = QuizSetArtifact(
            title="微积分练习",
            questions=[
                Question(
                    id="q1",
                    stem="Question 1",
                    options=["A", "B"],
                    answer="A",
                    explanation="Explanation"
                )
            ]
        )
        
        assert quiz_set.type == "quiz_set"
        assert quiz_set.title == "微积分练习"
        assert len(quiz_set.questions) == 1
    
    def test_example_creation(self):
        """测试 Example 创建"""
        example = Example(
            problem="Find derivative of x²",
            solution="2x",
            steps=["Step 1", "Step 2"]
        )
        
        assert example.problem == "Find derivative of x²"
        assert example.solution == "2x"
        assert len(example.steps) == 2
    
    def test_explanation_artifact_creation(self):
        """测试 ExplanationArtifact 创建"""
        explanation = ExplanationArtifact(
            title="Chain Rule",
            content="The chain rule is...",
            formula="d/dx[f(g(x))] = f'(g(x)) * g'(x)",
            examples=[
                Example(
                    problem="Example problem",
                    solution="Solution",
                    steps=[]
                )
            ]
        )
        
        assert explanation.type == "explanation"
        assert explanation.title == "Chain Rule"
        assert explanation.formula is not None
        assert len(explanation.examples) == 1


class TestAPIModels:
    """测试 API 相关模型"""
    
    def test_agent_chat_request_creation(self):
        """测试 AgentChatRequest 创建"""
        request = AgentChatRequest(
            user_id="user_123",
            session_id="session_456",
            message="给我几道练习题"
        )
        
        assert request.user_id == "user_123"
        assert request.session_id == "session_456"
        assert request.message == "给我几道练习题"
    
    def test_agent_chat_request_validation(self):
        """测试 AgentChatRequest 字段验证"""
        # 消息为空
        with pytest.raises(ValidationError):
            AgentChatRequest(
                user_id="user_123",
                session_id="session_456",
                message=""  # 空消息
            )
        
        # 消息过长
        with pytest.raises(ValidationError):
            AgentChatRequest(
                user_id="user_123",
                session_id="session_456",
                message="x" * 1001  # 超过 1000 字符
            )
    
    def test_agent_chat_response_creation(self):
        """测试 AgentChatResponse 创建"""
        response = AgentChatResponse(
            artifact=Artifact(
                type="quiz_set",
                payload={"questions": []},
                meta={}
            ),
            intent=IntentResult(
                intent="quiz",
                topic="test",
                confidence=0.9,
                raw_text="test"
            ),
            processing_time=2.5
        )
        
        assert response.artifact.type == "quiz_set"
        assert response.intent.intent == "quiz"
        assert response.processing_time == 2.5


class TestModelSerialization:
    """测试模型序列化"""
    
    def test_intent_result_json_serialization(self):
        """测试 IntentResult JSON 序列化"""
        intent = IntentResult(
            intent="quiz",
            topic="test",
            confidence=0.9,
            raw_text="test message"
        )
        
        # 序列化为 JSON
        json_data = intent.model_dump()
        
        assert json_data["intent"] == "quiz"
        assert json_data["topic"] == "test"
        assert json_data["confidence"] == 0.9
        
        # 从 JSON 反序列化
        reconstructed = IntentResult(**json_data)
        assert reconstructed.intent == intent.intent
        assert reconstructed.confidence == intent.confidence
    
    def test_user_profile_json_serialization(self):
        """测试 UserLearningProfile JSON 序列化"""
        profile = UserLearningProfile(
            user_id="test_user",
            mastery={"topic1": "weak"}
        )
        
        json_data = profile.model_dump()
        
        assert json_data["user_id"] == "test_user"
        assert "updated_at" in json_data
        
        # 注意：datetime 需要特殊处理
        json_data_str = profile.model_dump_json()
        assert isinstance(json_data_str, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

