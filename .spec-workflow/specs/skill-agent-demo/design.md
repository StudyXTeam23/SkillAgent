# Design Document - Skill Agent Demo

## Overview

本文档描述 StudyX Skill Agent Demo 的完整技术设计。该系统采用前后端分离架构，通过智能意图识别、记忆管理和技能编排，实现从"工具箱模式"到"智能学习助手模式"的升级。

**核心技术栈：**
- **后端**：Python 3.11+ + FastAPI + Pydantic V2 + Google Gemini 2.5 Flash
- **前端**：React 18 + TypeScript + TailwindCSS + Vite
- **存储**：内存存储（demo 阶段，接口支持扩展到 Redis/MongoDB）

**关键设计原则：**
- 模块化：每个核心组件独立封装，职责单一
- 可扩展：新增 Skill 只需配置文件 + handler 实现
- 类型安全：后端 Pydantic 模型 + 前端 TypeScript 接口
- 成本优化：按需加载 Prompt，避免大上下文浪费 token

## Steering Document Alignment

### Technical Standards

虽然本 demo 没有预先存在的 `tech.md` 指导文档，但我们遵循以下技术标准：

1. **后端标准（FastAPI）**：
   - 使用 FastAPI 依赖注入管理共享逻辑
   - 采用 Pydantic V2 进行数据验证和序列化
   - 遵循 RESTful API 设计规范
   - 使用异步 (async/await) 处理 I/O 密集操作

2. **前端标准（React）**：
   - 使用函数组件 + Hooks（useState, useReducer, useContext）
   - 采用 Context + Reducer 模式管理复杂状态
   - 组件按功能拆分，单一职责
   - 使用 TypeScript 确保类型安全

3. **代码组织标准**：
   - 后端：按功能模块划分目录（routers, services, models, skills）
   - 前端：按功能划分组件（components, hooks, contexts, types）
   - 配置与代码分离（Skill 定义使用 YAML 配置）

### Project Structure

```
skill_agent_demo/
├── backend/                      # FastAPI 后端
│   ├── app/
│   │   ├── main.py              # FastAPI 应用入口
│   │   ├── config.py            # 配置管理（环境变量、API Key）
│   │   ├── api/                 # API 路由层
│   │   │   ├── __init__.py
│   │   │   ├── agent.py         # 统一 Agent 入口 API
│   │   │   ├── intent.py        # Intent Router API
│   │   │   ├── memory.py        # Memory Manager API
│   │   │   └── skills.py        # Skill Registry API
│   │   ├── core/                # 核心模块
│   │   │   ├── __init__.py
│   │   │   ├── intent_router.py     # 意图识别模块
│   │   │   ├── memory_manager.py    # 记忆管理模块
│   │   │   ├── skill_orchestrator.py # 技能编排模块
│   │   │   └── skill_registry.py    # 技能注册表
│   │   ├── models/              # Pydantic 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── intent.py        # 意图相关模型
│   │   │   ├── memory.py        # 记忆相关模型
│   │   │   ├── skill.py         # Skill 相关模型
│   │   │   └── artifact.py      # Artifact 输出模型
│   │   ├── skills/              # 技能实现
│   │   │   ├── __init__.py
│   │   │   ├── base.py          # Skill 基类
│   │   │   ├── quiz/
│   │   │   │   ├── skill.yaml   # QuizSkill 配置
│   │   │   │   ├── handler.py   # QuizSkill 实现
│   │   │   │   └── prompts/
│   │   │   │       └── generate.txt
│   │   │   └── explain/
│   │   │       ├── skill.yaml   # ExplainSkill 配置
│   │   │       ├── handler.py   # ExplainSkill 实现
│   │   │       └── prompts/
│   │   │           └── generate.txt
│   │   ├── services/            # 外部服务封装
│   │   │   ├── __init__.py
│   │   │   └── gemini.py        # Gemini API 封装
│   │   └── utils/               # 工具函数
│   │       ├── __init__.py
│   │       └── validation.py    # JSON Schema 验证
│   ├── tests/                   # 测试代码
│   │   ├── test_intent_router.py
│   │   ├── test_memory_manager.py
│   │   └── test_skills.py
│   ├── requirements.txt         # Python 依赖
│   └── .env.example            # 环境变量模板
│
├── frontend/                    # React 前端
│   ├── src/
│   │   ├── main.tsx            # 应用入口
│   │   ├── App.tsx             # 根组件
│   │   ├── components/         # UI 组件
│   │   │   ├── chat/
│   │   │   │   ├── ChatInterface.tsx     # 聊天主界面
│   │   │   │   ├── MessageList.tsx       # 消息列表
│   │   │   │   ├── MessageBubble.tsx     # 单条消息气泡
│   │   │   │   ├── InputArea.tsx         # 输入框组件
│   │   │   │   └── LoadingIndicator.tsx  # 加载动画
│   │   │   ├── artifacts/
│   │   │   │   ├── QuizCard.tsx          # 练习题卡片
│   │   │   │   └── ExplainCard.tsx       # 讲解卡片
│   │   │   ├── layout/
│   │   │   │   ├── Sidebar.tsx           # 侧边栏
│   │   │   │   └── TopNavBar.tsx         # 顶部导航栏
│   │   │   └── common/
│   │   │       ├── Button.tsx
│   │   │       └── ProgressBar.tsx
│   │   ├── contexts/           # React Context
│   │   │   ├── ChatContext.tsx      # 聊天状态管理
│   │   │   └── ThemeContext.tsx     # 主题管理
│   │   ├── hooks/              # 自定义 Hooks
│   │   │   ├── useChat.ts           # 聊天逻辑 Hook
│   │   │   ├── useAgent.ts          # Agent API 调用 Hook
│   │   │   └── useTheme.ts          # 主题切换 Hook
│   │   ├── services/           # API 调用服务
│   │   │   └── api.ts               # Axios 封装
│   │   ├── types/              # TypeScript 类型定义
│   │   │   ├── message.ts
│   │   │   ├── artifact.ts
│   │   │   └── api.ts
│   │   ├── styles/             # 样式文件
│   │   │   └── index.css
│   │   └── utils/              # 工具函数
│   │       └── formatters.ts
│   ├── public/                 # 静态资源
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
└── README.md                    # 项目说明
```

## Architecture

### System Architecture Diagram

```mermaid
graph TB
    subgraph Frontend["前端 - React"]
        UI[ChatInterface 统一聊天界面]
        QuizUI[QuizCard 练习题组件]
        ExplainUI[ExplainCard 讲解组件]
    end

    subgraph Backend["后端 - FastAPI"]
        AgentAPI[/agent/chat<br/>统一 Agent API]
        
        subgraph Core["核心模块"]
            IR[Intent Router<br/>意图识别]
            MM[Memory Manager<br/>记忆管理]
            SO[Skill Orchestrator<br/>技能编排]
            SR[Skill Registry<br/>技能注册表]
        end
        
        subgraph Skills["技能层"]
            QuizSkill[QuizSkill<br/>练习题生成]
            ExplainSkill[ExplainSkill<br/>概念讲解]
        end
    end

    subgraph External["外部服务"]
        Gemini[Google Gemini 2.5 Flash<br/>大语言模型]
    end

    UI -->|POST /agent/chat| AgentAPI
    AgentAPI --> IR
    IR -->|获取记忆摘要| MM
    IR -->|意图结果| SO
    SO -->|查询技能定义| SR
    SO -->|获取用户画像| MM
    SO -->|调用技能| QuizSkill
    SO -->|调用技能| ExplainSkill
    QuizSkill -->|生成内容| Gemini
    ExplainSkill -->|生成内容| Gemini
    SO -->|更新状态| MM
    SO -->|返回 Artifact| AgentAPI
    AgentAPI -->|JSON 响应| UI
    UI -->|渲染| QuizUI
    UI -->|渲染| ExplainUI

    style Frontend fill:#e1f5fe
    style Backend fill:#fff3e0
    style Core fill:#f3e5f5
    style Skills fill:#e8f5e9
    style External fill:#fce4ec
```

### Request Flow Sequence

**场景：用户说"给我几道极限练习题"**

```mermaid
sequenceDiagram
    participant User as 用户
    participant UI as ChatInterface
    participant API as Agent API
    participant IR as Intent Router
    participant MM as Memory Manager
    participant SO as Skill Orchestrator
    participant SR as Skill Registry
    participant QS as QuizSkill
    participant Gemini as Gemini API

    User->>UI: 输入："给我几道极限练习题"
    UI->>API: POST /agent/chat {user_id, session_id, message}
    
    API->>MM: 获取记忆摘要
    MM-->>API: {topic_hint, mastery, recent_behavior}
    
    API->>IR: 解析意图 + 记忆摘要
    IR->>Gemini: 轻量 Prompt（< 200 tokens）
    Gemini-->>IR: 结构化意图 JSON
    IR-->>API: {intent: "quiz", topic: "微积分-极限", confidence: 0.86}
    
    API->>SO: 编排技能执行
    SO->>SR: 查找 intent="quiz" 的技能
    SR-->>SO: QuizSkill 定义
    
    SO->>MM: 获取用户画像
    MM-->>SO: {mastery["微积分-极限"]: "weak"}
    
    SO->>QS: execute(params={topic, difficulty="easy"}, context={user_profile})
    QS->>Gemini: 生成题目 Prompt（< 500 tokens）
    Gemini-->>QS: 题目 JSON
    QS-->>SO: {questions: [...]}
    
    SO->>MM: 更新学习状态
    MM-->>SO: 更新成功
    
    SO-->>API: Artifact {type: "quiz_set", payload: {...}}
    API-->>UI: JSON 响应
    UI->>UI: 渲染 QuizCard
    UI-->>User: 显示练习题
```

### Modular Design Principles

1. **单一职责（Single Responsibility）**：
   - Intent Router：只负责意图识别，不做内容生成
   - Memory Manager：只负责状态管理，不做推理
   - Skill Orchestrator：只负责编排调度，不实现具体 Skill
   - Skill：只负责内容生成，不管理状态

2. **依赖注入（Dependency Injection）**：
   - 使用 FastAPI 的 `Depends` 管理共享依赖（如 Gemini 客户端）
   - Skill 通过构造函数接收依赖（LLM 客户端、Registry）

3. **接口抽象（Interface Abstraction）**：
   - 所有 Skill 实现统一的 `BaseSkill` 抽象类
   - 所有 Skill 必须定义 `execute(params, context)` 方法
   - 输入输出遵循 JSON Schema 定义

4. **配置驱动（Configuration Driven）**：
   - Skill 定义使用 YAML 配置文件
   - 支持动态加载和热更新（未来扩展）

## Components and Interfaces

### 1. Agent API（统一入口）

**Purpose:** 提供统一的聊天 API，封装整个 Skill Agent 流程。

**Endpoint:** `POST /agent/chat`

**Request Schema:**
```python
# models/api.py
from pydantic import BaseModel, Field

class AgentChatRequest(BaseModel):
    user_id: str = Field(..., description="用户 ID")
    session_id: str = Field(..., description="会话 ID")
    message: str = Field(..., min_length=1, description="用户消息")

class AgentChatResponse(BaseModel):
    artifact: Artifact = Field(..., description="生成的结果")
    intent: IntentResult = Field(..., description="识别的意图")
    processing_time: float = Field(..., description="处理时间（秒）")
```

**Dependencies:**
- Intent Router
- Memory Manager
- Skill Orchestrator

**Implementation:**
```python
# api/agent.py
from fastapi import APIRouter, Depends, HTTPException
from ..core import IntentRouter, MemoryManager, SkillOrchestrator

router = APIRouter(prefix="/agent", tags=["agent"])

@router.post("/chat", response_model=AgentChatResponse)
async def chat(
    request: AgentChatRequest,
    intent_router: IntentRouter = Depends(get_intent_router),
    memory_manager: MemoryManager = Depends(get_memory_manager),
    orchestrator: SkillOrchestrator = Depends(get_orchestrator)
):
    try:
        # 1. 获取记忆摘要
        memory_summary = await memory_manager.get_summary(
            request.user_id, 
            request.session_id
        )
        
        # 2. 识别意图
        intent_result = await intent_router.parse(
            request.message,
            memory_summary
        )
        
        # 3. 编排执行
        artifact = await orchestrator.execute(
            intent_result,
            request.user_id,
            request.session_id
        )
        
        # 4. 更新记忆
        await memory_manager.update(
            request.user_id,
            request.session_id,
            intent_result,
            artifact
        )
        
        return AgentChatResponse(
            artifact=artifact,
            intent=intent_result,
            processing_time=timer.elapsed()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 2. Intent Router（意图识别器）

**Purpose:** 解析用户自然语言输入，输出结构化意图。

**Interface:**
```python
# core/intent_router.py
from typing import Optional
from ..models.intent import IntentResult, MemorySummary
from ..services.gemini import GeminiClient

class IntentRouter:
    def __init__(self, gemini_client: GeminiClient):
        self.gemini = gemini_client
        self.prompt_template = self._load_prompt()
    
    async def parse(
        self, 
        message: str, 
        memory_summary: Optional[MemorySummary] = None
    ) -> IntentResult:
        """
        解析用户输入，返回结构化意图
        
        Args:
            message: 用户消息
            memory_summary: 记忆摘要（可选）
        
        Returns:
            IntentResult: {intent, topic, target_artifact, confidence}
        """
        prompt = self._build_prompt(message, memory_summary)
        
        response = await self.gemini.generate(
            prompt=prompt,
            model="gemini-2.5-flash",
            response_format="json",
            max_tokens=200
        )
        
        intent_result = self._parse_response(response)
        return intent_result
    
    def _build_prompt(self, message: str, memory: Optional[MemorySummary]) -> str:
        return self.prompt_template.format(
            message=message,
            topic_hint=memory.topic_hint if memory else "",
            recent_context=memory.recent_behavior if memory else ""
        )
```

**Models:**
```python
# models/intent.py
from pydantic import BaseModel, Field
from typing import Optional, List

class IntentResult(BaseModel):
    intent: str | List[str] = Field(..., description="意图标签，如 quiz, explain")
    topic: Optional[str] = Field(None, description="主题，如 微积分-极限")
    target_artifact: Optional[str] = Field(None, description="目标产物类型")
    confidence: float = Field(..., ge=0, le=1, description="置信度")
    raw_text: str = Field(..., description="原始输入")

class MemorySummary(BaseModel):
    topic_hint: Optional[str] = Field(None, description="当前主题提示")
    user_mastery_hint: Optional[str] = Field(None, description="掌握度提示")
    recent_behavior: str = Field("", description="最近行为描述")
```

**Prompt Template:**
```text
# prompts/intent_router.txt
You are an intent classifier for a learning assistant. Analyze the user's message and output JSON.

User Message: {message}

Context:
- Current Topic: {topic_hint}
- Recent Activity: {recent_context}

Supported Intents:
- quiz: User wants practice questions
- explain: User wants concept explanation
- other: Unclear intent

Output JSON:
{{
  "intent": "quiz" | "explain" | "other",
  "topic": "<extracted topic>",
  "confidence": 0.0-1.0
}}
```

**Reuses:** Gemini API 客户端（共享服务）

### 3. Memory Manager（记忆管理器）

**Purpose:** 管理用户长期学习画像和会话短期记忆。

**Interface:**
```python
# core/memory_manager.py
from typing import Dict, Optional
from ..models.memory import UserLearningProfile, SessionContext, MemorySummary

class MemoryManager:
    def __init__(self):
        # Demo 阶段使用内存存储
        self.profiles: Dict[str, UserLearningProfile] = {}
        self.sessions: Dict[str, SessionContext] = {}
    
    async def get_summary(
        self, 
        user_id: str, 
        session_id: str
    ) -> MemorySummary:
        """生成简短的记忆摘要供 Intent Router 使用"""
        profile = self._get_or_create_profile(user_id)
        session = self._get_or_create_session(session_id)
        
        return MemorySummary(
            topic_hint=session.current_topic,
            user_mastery_hint=self._infer_mastery(profile, session.current_topic),
            recent_behavior=self._summarize_recent(session)
        )
    
    async def get_profile(self, user_id: str) -> UserLearningProfile:
        """获取完整的用户学习画像"""
        return self._get_or_create_profile(user_id)
    
    async def update(
        self,
        user_id: str,
        session_id: str,
        intent: IntentResult,
        artifact: Artifact
    ):
        """更新学习状态"""
        profile = self._get_or_create_profile(user_id)
        session = self._get_or_create_session(session_id)
        
        # 更新会话上下文
        session.current_topic = intent.topic
        session.recent_intents.append(intent.intent)
        session.last_artifact = artifact.type
        
        # 更新用户画像（简化版）
        if intent.topic:
            profile.history["topics_visited"].append(intent.topic)
            if intent.intent == "quiz":
                profile.history["quiz_sessions"] += 1
```

**Models:**
```python
# models/memory.py
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

class UserLearningProfile(BaseModel):
    user_id: str
    mastery: Dict[str, str] = Field(default_factory=dict)  # topic -> weak/medium/strong
    preferences: Dict[str, str] = Field(default_factory=dict)
    history: Dict[str, any] = Field(default_factory=lambda: {
        "quiz_sessions": 0,
        "homework_help_count": 0,
        "topics_visited": []
    })
    updated_at: datetime = Field(default_factory=datetime.now)

class SessionContext(BaseModel):
    session_id: str
    current_topic: Optional[str] = None
    recent_intents: List[str] = Field(default_factory=list)
    last_artifact: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.now)
```

**Reuses:** 无外部依赖（纯状态管理）

### 4. Skill Registry（技能注册表）

**Purpose:** 管理所有 Skill 的定义和元数据。

**Interface:**
```python
# core/skill_registry.py
from typing import List, Optional, Dict
import yaml
from pathlib import Path
from ..models.skill import SkillDefinition

class SkillRegistry:
    def __init__(self, skills_dir: Path):
        self.skills_dir = skills_dir
        self.skills: Dict[str, SkillDefinition] = {}
        self._load_skills()
    
    def _load_skills(self):
        """从 skills/ 目录加载所有 skill.yaml"""
        for skill_dir in self.skills_dir.iterdir():
            if skill_dir.is_dir():
                config_file = skill_dir / "skill.yaml"
                if config_file.exists():
                    with open(config_file) as f:
                        config = yaml.safe_load(f)
                        skill_def = SkillDefinition(**config)
                        self.skills[skill_def.id] = skill_def
    
    def get_by_intent(self, intent: str) -> List[SkillDefinition]:
        """根据意图标签查找匹配的 Skill"""
        return [
            skill for skill in self.skills.values()
            if intent in skill.intent_tags
        ]
    
    def get_by_id(self, skill_id: str) -> Optional[SkillDefinition]:
        """根据 ID 获取 Skill 定义"""
        return self.skills.get(skill_id)
    
    def validate_params(self, skill_id: str, params: Dict) -> bool:
        """验证输入参数是否符合 Skill 的 input_schema"""
        skill = self.get_by_id(skill_id)
        if not skill:
            return False
        # 使用 jsonschema 验证
        from jsonschema import validate
        validate(instance=params, schema=skill.input_schema)
        return True
```

**Models:**
```python
# models/skill.py
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class SkillDefinition(BaseModel):
    id: str = Field(..., description="技能唯一标识")
    display_name: str = Field(..., description="显示名称")
    version: str = Field(default="1.0.0")
    intent_tags: List[str] = Field(..., description="支持的意图标签")
    input_schema: Dict = Field(..., description="输入参数 JSON Schema")
    output_schema: Dict = Field(..., description="输出结果 JSON Schema")
    models: Dict[str, str] = Field(..., description="使用的模型配置")
    context: Dict[str, any] = Field(default_factory=dict)
    cost: Dict[str, any] = Field(default_factory=dict)
    composable: bool = Field(default=True)
    dependencies: List[str] = Field(default_factory=list)
```

**Configuration Example:**
```yaml
# skills/quiz/skill.yaml
id: quiz
display_name: 练习题生成
version: 1.0.0

intent_tags:
  - quiz

input_schema:
  type: object
  properties:
    topic:
      type: string
      description: 主题名称
    difficulty:
      type: string
      enum: [easy, medium, hard]
      default: medium
    num_questions:
      type: integer
      minimum: 1
      maximum: 10
      default: 5
  required:
    - topic

output_schema:
  type: object
  properties:
    questions:
      type: array
      items:
        type: object

models:
  primary: gemini-2.5-flash
  fallback: gemini-2.0-flash-lite

context:
  need_user_memory: true
  need_content_store: false

cost:
  model_class: small
  context_size: small
  expected_rounds: 1

composable: true
dependencies: []
```

### 5. Skill Orchestrator（技能编排器）

**Purpose:** 根据意图选择合适的 Skill，构建参数并执行。

**Interface:**
```python
# core/skill_orchestrator.py
from typing import Dict
from ..models.intent import IntentResult
from ..models.artifact import Artifact
from ..core.skill_registry import SkillRegistry
from ..core.memory_manager import MemoryManager
from ..skills.base import BaseSkill

class SkillOrchestrator:
    def __init__(
        self,
        registry: SkillRegistry,
        memory_manager: MemoryManager,
        skill_instances: Dict[str, BaseSkill]
    ):
        self.registry = registry
        self.memory = memory_manager
        self.skills = skill_instances
    
    async def execute(
        self,
        intent: IntentResult,
        user_id: str,
        session_id: str
    ) -> Artifact:
        """执行技能并返回 Artifact"""
        
        # 1. 选择 Skill
        skill_def = self._select_skill(intent)
        if not skill_def:
            raise ValueError(f"No skill found for intent: {intent.intent}")
        
        # 2. 构建参数
        params = self._build_params(intent, skill_def)
        
        # 3. 构建上下文
        context = await self._build_context(user_id, session_id, skill_def)
        
        # 4. 执行 Skill
        skill_instance = self.skills[skill_def.id]
        result = await skill_instance.execute(params, context)
        
        # 5. 封装为 Artifact
        artifact = Artifact(
            type=self._infer_artifact_type(skill_def.id, result),
            payload=result,
            meta={
                "source_skill": skill_def.id,
                "topic": intent.topic
            }
        )
        
        return artifact
    
    def _select_skill(self, intent: IntentResult) -> Optional[SkillDefinition]:
        """选择最合适的 Skill（策略：第一个匹配 + 成本最低）"""
        candidates = self.registry.get_by_intent(intent.intent)
        if not candidates:
            return None
        
        # Demo 简化：选择第一个
        # 未来可以根据 cost、用户偏好等排序
        return candidates[0]
    
    def _build_params(self, intent: IntentResult, skill_def: SkillDefinition) -> Dict:
        """根据意图和 Skill 定义构建输入参数"""
        params = {"topic": intent.topic}
        
        # 从 input_schema 提取默认值
        schema = skill_def.input_schema
        for prop, prop_schema in schema.get("properties", {}).items():
            if "default" in prop_schema and prop not in params:
                params[prop] = prop_schema["default"]
        
        return params
    
    async def _build_context(
        self, 
        user_id: str, 
        session_id: str, 
        skill_def: SkillDefinition
    ) -> Dict:
        """构建 Skill 执行上下文"""
        context = {}
        
        if skill_def.context.get("need_user_memory"):
            profile = await self.memory.get_profile(user_id)
            context["user_profile"] = profile.dict()
        
        # 未来扩展：content_store
        
        return context
```

### 6. Base Skill（技能基类）

**Purpose:** 定义所有 Skill 的统一接口。

**Interface:**
```python
# skills/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any
from pathlib import Path

class BaseSkill(ABC):
    def __init__(self, skill_dir: Path, gemini_client):
        self.skill_dir = skill_dir
        self.gemini = gemini_client
        self.prompt_template = self._load_prompt()
    
    @abstractmethod
    async def execute(self, params: Dict, context: Dict) -> Dict:
        """
        执行技能逻辑
        
        Args:
            params: 输入参数（符合 input_schema）
            context: 执行上下文（user_profile, content_context 等）
        
        Returns:
            Dict: 输出结果（符合 output_schema）
        """
        pass
    
    def _load_prompt(self) -> str:
        """加载 Prompt 模板"""
        prompt_file = self.skill_dir / "prompts" / "generate.txt"
        if prompt_file.exists():
            return prompt_file.read_text()
        return ""
    
    def _validate_output(self, result: Dict, schema: Dict) -> bool:
        """验证输出是否符合 output_schema"""
        from jsonschema import validate
        validate(instance=result, schema=schema)
        return True
```

### 7. Quiz Skill（练习题生成技能）

**Implementation:**
```python
# skills/quiz/handler.py
from ..base import BaseSkill
from typing import Dict
import json

class QuizSkill(BaseSkill):
    async def execute(self, params: Dict, context: Dict) -> Dict:
        # 1. 提取参数
        topic = params["topic"]
        difficulty = params.get("difficulty", "medium")
        num_questions = params.get("num_questions", 5)
        
        # 2. 根据用户掌握度调整难度
        if context.get("user_profile"):
            mastery = context["user_profile"].get("mastery", {}).get(topic)
            if mastery == "weak" and difficulty == "medium":
                difficulty = "easy"
        
        # 3. 构建 Prompt
        prompt = self.prompt_template.format(
            topic=topic,
            difficulty=difficulty,
            num_questions=num_questions
        )
        
        # 4. 调用 Gemini
        response = await self.gemini.generate(
            prompt=prompt,
            model="gemini-2.5-flash",
            response_format="json",
            max_tokens=1500
        )
        
        # 5. 解析结果
        result = json.loads(response)
        
        # 6. 验证输出
        self._validate_output(result, self.output_schema)
        
        return result
```

**Prompt Template:**
```text
# skills/quiz/prompts/generate.txt
You are a quiz generator for calculus students.

Topic: {topic}
Difficulty: {difficulty}
Number of Questions: {num_questions}

Generate {num_questions} multiple-choice questions on the topic "{topic}" at {difficulty} difficulty level.

Output JSON format:
{{
  "questions": [
    {{
      "id": "q1",
      "stem": "What is the derivative of x²?",
      "options": ["2x", "x", "x²/2", "2"],
      "answer": "2x",
      "explanation": "Using the power rule..."
    }}
  ]
}}

Ensure:
- Questions are clear and accurate
- Options include common misconceptions
- Explanations are educational
```

### 8. Explain Skill（概念讲解技能）

**Implementation:**
```python
# skills/explain/handler.py
from ..base import BaseSkill
from typing import Dict
import json

class ExplainSkill(BaseSkill):
    async def execute(self, params: Dict, context: Dict) -> Dict:
        topic = params["topic"]
        depth = params.get("depth", "basic")
        
        # 根据用户掌握度调整讲解深度
        if context.get("user_profile"):
            mastery = context["user_profile"].get("mastery", {}).get(topic)
            if mastery == "strong":
                depth = "advanced"
        
        prompt = self.prompt_template.format(
            topic=topic,
            depth=depth
        )
        
        response = await self.gemini.generate(
            prompt=prompt,
            model="gemini-2.5-flash",
            response_format="json",
            max_tokens=2000
        )
        
        result = json.loads(response)
        self._validate_output(result, self.output_schema)
        
        return result
```

**Prompt Template:**
```text
# skills/explain/prompts/generate.txt
You are a calculus tutor explaining concepts clearly.

Topic: {topic}
Depth: {depth}

Explain the concept "{topic}" at {depth} level.

Output JSON format:
{{
  "title": "The Chain Rule",
  "content": "The chain rule is a formula...",
  "formula": "d/dx [f(g(x))] = f'(g(x)) * g'(x)",
  "examples": [
    {{
      "problem": "Find derivative of (x² + 1)³",
      "solution": "Step-by-step solution...",
      "steps": ["Step 1...", "Step 2..."]
    }}
  ]
}}

Ensure:
- Clear and structured explanation
- 2-3 worked examples
- Step-by-step solutions
```

## Data Models

### API Request/Response Models

```python
# models/api.py
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from .intent import IntentResult
from .artifact import Artifact

class AgentChatRequest(BaseModel):
    user_id: str = Field(..., description="用户 ID")
    session_id: str = Field(..., description="会话 ID")
    message: str = Field(..., min_length=1, max_length=1000)

class AgentChatResponse(BaseModel):
    artifact: Artifact
    intent: IntentResult
    processing_time: float
```

### Artifact Models（输出产物）

```python
# models/artifact.py
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

class Artifact(BaseModel):
    type: str = Field(..., description="产物类型：quiz_set, explanation, etc.")
    payload: Dict[str, Any] = Field(..., description="实际内容")
    meta: Dict[str, Any] = Field(default_factory=dict, description="元数据")

class QuizSetArtifact(BaseModel):
    """练习题集合"""
    type: str = "quiz_set"
    title: str = Field(..., description="题集标题")
    questions: List["Question"]
    meta: Dict[str, Any] = Field(default_factory=dict)

class Question(BaseModel):
    id: str
    stem: str = Field(..., description="题干")
    options: List[str] = Field(..., min_items=2)
    answer: str = Field(..., description="正确答案")
    explanation: str = Field(..., description="解析")

class ExplanationArtifact(BaseModel):
    """概念讲解"""
    type: str = "explanation"
    title: str
    content: str = Field(..., description="讲解内容")
    formula: Optional[str] = None
    examples: List["Example"] = Field(default_factory=list)
    meta: Dict[str, Any] = Field(default_factory=dict)

class Example(BaseModel):
    problem: str
    solution: str
    steps: List[str] = Field(default_factory=list)
```

### Frontend TypeScript Types

```typescript
// types/message.ts
export interface Message {
  id: string;
  role: 'user' | 'agent';
  content: string;
  artifact?: Artifact;
  timestamp: Date;
}

export interface Artifact {
  type: 'quiz_set' | 'explanation' | 'loading' | 'error';
  payload: QuizSetPayload | ExplanationPayload | any;
  meta?: Record<string, any>;
}

export interface QuizSetPayload {
  title: string;
  questions: Question[];
}

export interface Question {
  id: string;
  stem: string;
  options: string[];
  answer: string;
  explanation: string;
}

export interface ExplanationPayload {
  title: string;
  content: string;
  formula?: string;
  examples: Example[];
}

export interface Example {
  problem: string;
  solution: string;
  steps: string[];
}
```

## Frontend Architecture

### Component Hierarchy

```
App
├── ThemeProvider
│   └── ChatProvider
│       └── Layout
│           ├── Sidebar
│           ├── MainContent
│           │   ├── TopNavBar
│           │   ├── ChatInterface
│           │   │   ├── MessageList
│           │   │   │   └── MessageBubble
│           │   │   │       ├── QuizCard
│           │   │   │       └── ExplainCard
│           │   │   ├── LoadingIndicator
│           │   │   └── InputArea
│           │   └── ...
│           └── ...
└── ...
```

### State Management Pattern

采用 **Context + Reducer** 模式管理聊天状态：

```typescript
// contexts/ChatContext.tsx
import React, { createContext, useContext, useReducer } from 'react';

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
}

type ChatAction =
  | { type: 'ADD_MESSAGE'; payload: Message }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null };

function chatReducer(state: ChatState, action: ChatAction): ChatState {
  switch (action.type) {
    case 'ADD_MESSAGE':
      return { ...state, messages: [...state.messages, action.payload] };
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    default:
      return state;
  }
}

const ChatContext = createContext<ChatState | undefined>(undefined);
const ChatDispatchContext = createContext<React.Dispatch<ChatAction> | undefined>(undefined);

export function ChatProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(chatReducer, {
    messages: [],
    isLoading: false,
    error: null,
  });

  return (
    <ChatContext.Provider value={state}>
      <ChatDispatchContext.Provider value={dispatch}>
        {children}
      </ChatDispatchContext.Provider>
    </ChatDispatchContext.Provider>
  );
}

export function useChat() {
  const context = useContext(ChatContext);
  if (!context) throw new Error('useChat must be used within ChatProvider');
  return context;
}

export function useChatDispatch() {
  const context = useContext(ChatDispatchContext);
  if (!context) throw new Error('useChatDispatch must be used within ChatProvider');
  return context;
}
```

### Custom Hook for Agent API

```typescript
// hooks/useAgent.ts
import { useState } from 'react';
import { useChatDispatch } from '../contexts/ChatContext';
import { api } from '../services/api';
import type { Message } from '../types/message';

export function useAgent() {
  const dispatch = useChatDispatch();
  const [sessionId] = useState(() => generateSessionId());

  async function sendMessage(message: string) {
    // 1. 添加用户消息
    dispatch({
      type: 'ADD_MESSAGE',
      payload: {
        id: generateId(),
        role: 'user',
        content: message,
        timestamp: new Date(),
      },
    });

    // 2. 显示加载状态
    dispatch({ type: 'SET_LOADING', payload: true });

    try {
      // 3. 调用 Agent API
      const response = await api.post('/agent/chat', {
        user_id: 'demo_user',
        session_id: sessionId,
        message,
      });

      // 4. 添加 Agent 响应
      dispatch({
        type: 'ADD_MESSAGE',
        payload: {
          id: generateId(),
          role: 'agent',
          content: '',
          artifact: response.data.artifact,
          timestamp: new Date(),
        },
      });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }

  return { sendMessage };
}
```

### Artifact Rendering Logic

```typescript
// components/chat/MessageBubble.tsx
import React from 'react';
import { QuizCard } from '../artifacts/QuizCard';
import { ExplainCard } from '../artifacts/ExplainCard';
import type { Message } from '../../types/message';

export function MessageBubble({ message }: { message: Message }) {
  if (message.role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="bg-primary text-white rounded-xl px-4 py-3 max-w-2xl">
          {message.content}
        </div>
      </div>
    );
  }

  // Agent message with artifact
  return (
    <div className="flex justify-start">
      {message.artifact ? (
        renderArtifact(message.artifact)
      ) : (
        <div className="bg-surface-light border rounded-xl px-4 py-3 max-w-2xl">
          {message.content}
        </div>
      )}
    </div>
  );
}

function renderArtifact(artifact: Artifact) {
  switch (artifact.type) {
    case 'quiz_set':
      return <QuizCard data={artifact.payload} />;
    case 'explanation':
      return <ExplainCard data={artifact.payload} />;
    case 'loading':
      return <LoadingIndicator />;
    case 'error':
      return <ErrorMessage message={artifact.payload.message} />;
    default:
      return <div>Unknown artifact type: {artifact.type}</div>;
  }
}
```

## API Specifications

### Complete API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/agent/chat` | 统一聊天入口 |
| POST | `/intent/parse` | 意图识别（内部调试用） |
| GET | `/memory/user/{user_id}` | 获取用户学习画像 |
| GET | `/memory/session/{session_id}` | 获取会话上下文 |
| GET | `/skills` | 获取所有技能列表 |
| GET | `/skills/{skill_id}` | 获取指定技能定义 |
| GET | `/health` | 健康检查 |

### API Request/Response Examples

#### POST /agent/chat

**Request:**
```json
{
  "user_id": "demo_user",
  "session_id": "sess_12345",
  "message": "给我几道微积分极限的练习题"
}
```

**Response (Success):**
```json
{
  "artifact": {
    "type": "quiz_set",
    "payload": {
      "title": "微积分·极限基础练习",
      "questions": [
        {
          "id": "q1",
          "stem": "What is the limit of (x² - 1)/(x - 1) as x approaches 1?",
          "options": ["0", "1", "2", "undefined"],
          "answer": "2",
          "explanation": "Factor the numerator: (x+1)(x-1)/(x-1) = x+1. As x→1, limit is 2."
        }
      ]
    },
    "meta": {
      "source_skill": "quiz",
      "topic": "微积分-极限"
    }
  },
  "intent": {
    "intent": "quiz",
    "topic": "微积分-极限",
    "target_artifact": "quiz_set",
    "confidence": 0.92,
    "raw_text": "给我几道微积分极限的练习题"
  },
  "processing_time": 2.34
}
```

**Response (Error):**
```json
{
  "detail": "Intent recognition confidence too low. Please clarify your request."
}
```

## Error Handling

### Error Scenarios

#### 1. Intent Recognition Failure

**Scenario:** Intent Router 置信度 < 0.6

**Handling:**
```python
if intent_result.confidence < 0.6:
    return AgentChatResponse(
        artifact=Artifact(
            type="error",
            payload={
                "message": "抱歉，我没太理解你的问题。你是想要练习题还是概念讲解？",
                "suggestions": ["练习题", "概念讲解"]
            }
        ),
        intent=intent_result,
        processing_time=timer.elapsed()
    )
```

**User Impact:** 用户看到友好的澄清问题

#### 2. Gemini API Failure

**Scenario:** Gemini API 调用超时或返回错误

**Handling:**
```python
try:
    response = await self.gemini.generate(...)
except GeminiAPIError as e:
    logger.error(f"Gemini API error: {e}")
    if "rate_limit" in str(e):
        raise HTTPException(status_code=429, detail="请稍后再试")
    else:
        raise HTTPException(status_code=500, detail="AI 服务暂时不可用")
```

**User Impact:** 显示错误消息 + 重试按钮

#### 3. Skill Execution Failure

**Scenario:** Skill 内部逻辑错误（如 JSON 解析失败）

**Handling:**
```python
try:
    result = await skill.execute(params, context)
except Exception as e:
    logger.error(f"Skill execution failed: {skill_def.id}, error: {e}")
    # Fallback 到默认响应
    return Artifact(
        type="error",
        payload={
            "message": "抱歉，生成内容时遇到了问题。请换个方式提问。"
        }
    )
```

**User Impact:** 友好的错误提示，不暴露技术细节

#### 4. Invalid Input

**Scenario:** 用户输入为空或超长

**Handling:**
```python
class AgentChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)

# FastAPI 自动验证，返回 422 错误
```

**User Impact:** 前端禁用发送按钮（空输入），或显示字数限制

### Error Response Format

统一错误响应格式：

```typescript
interface ErrorArtifact {
  type: 'error';
  payload: {
    message: string;          // 用户友好的错误消息
    code?: string;            // 错误代码（可选）
    suggestions?: string[];   // 建议操作（可选）
    retryable?: boolean;      // 是否可重试
  };
}
```

## Testing Strategy

### Unit Testing

#### Backend Unit Tests

**测试目标：** 独立测试每个模块的核心逻辑

**测试工具：** pytest + pytest-asyncio

**测试用例示例：**

```python
# tests/test_intent_router.py
import pytest
from app.core.intent_router import IntentRouter
from app.models.intent import MemorySummary

@pytest.mark.asyncio
async def test_intent_router_quiz_intent():
    """测试练习题意图识别"""
    router = IntentRouter(gemini_client=mock_gemini_client)
    
    result = await router.parse(
        message="给我几道极限练习题",
        memory_summary=MemorySummary(topic_hint="微积分")
    )
    
    assert result.intent == "quiz"
    assert "极限" in result.topic
    assert result.confidence > 0.7

@pytest.mark.asyncio
async def test_intent_router_low_confidence():
    """测试低置信度场景"""
    router = IntentRouter(gemini_client=mock_gemini_client)
    
    result = await router.parse(message="帮帮我")
    
    assert result.confidence < 0.6
    assert result.intent == "other"
```

```python
# tests/test_memory_manager.py
import pytest
from app.core.memory_manager import MemoryManager

@pytest.mark.asyncio
async def test_memory_update():
    """测试记忆更新逻辑"""
    mm = MemoryManager()
    
    await mm.update(
        user_id="test_user",
        session_id="test_session",
        intent=IntentResult(intent="quiz", topic="微积分-极限"),
        artifact=Artifact(type="quiz_set")
    )
    
    profile = await mm.get_profile("test_user")
    assert profile.history["quiz_sessions"] == 1
    assert "微积分-极限" in profile.history["topics_visited"]
```

```python
# tests/test_skills.py
import pytest
from app.skills.quiz.handler import QuizSkill

@pytest.mark.asyncio
async def test_quiz_skill_output_format():
    """测试 QuizSkill 输出格式"""
    skill = QuizSkill(skill_dir=Path("skills/quiz"), gemini_client=mock_gemini_client)
    
    result = await skill.execute(
        params={"topic": "微积分-极限", "difficulty": "easy", "num_questions": 3},
        context={}
    )
    
    assert "questions" in result
    assert len(result["questions"]) == 3
    assert all("stem" in q and "options" in q for q in result["questions"])
```

#### Frontend Unit Tests

**测试工具：** Vitest + React Testing Library

**测试用例示例：**

```typescript
// __tests__/hooks/useAgent.test.ts
import { renderHook, act } from '@testing-library/react';
import { useAgent } from '../../hooks/useAgent';

test('sendMessage should add user and agent messages', async () => {
  const { result } = renderHook(() => useAgent());

  await act(async () => {
    await result.current.sendMessage('给我几道练习题');
  });

  // 验证消息被添加
  // ...
});
```

```typescript
// __tests__/components/QuizCard.test.tsx
import { render, screen } from '@testing-library/react';
import { QuizCard } from '../../components/artifacts/QuizCard';

test('QuizCard renders questions correctly', () => {
  const mockData = {
    title: '微积分练习',
    questions: [
      {
        id: 'q1',
        stem: 'What is 2+2?',
        options: ['3', '4', '5'],
        answer: '4',
        explanation: 'Basic math',
      },
    ],
  };

  render(<QuizCard data={mockData} />);

  expect(screen.getByText('微积分练习')).toBeInTheDocument();
  expect(screen.getByText('What is 2+2?')).toBeInTheDocument();
});
```

### Integration Testing

**测试目标：** 测试模块间交互和完整流程

**测试用例：**

```python
# tests/integration/test_agent_flow.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_agent_chat_quiz_flow():
    """测试完整的练习题生成流程"""
    response = client.post("/agent/chat", json={
        "user_id": "test_user",
        "session_id": "test_session",
        "message": "给我几道微积分极限的练习题"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["artifact"]["type"] == "quiz_set"
    assert data["intent"]["intent"] == "quiz"
    assert "极限" in data["intent"]["topic"]
    assert len(data["artifact"]["payload"]["questions"]) > 0
```

### End-to-End Testing

**测试工具：** Playwright（未来扩展）

**测试场景：**
1. 用户打开应用 → 输入练习题请求 → 查看题目 → 提交答案 → 查看解析
2. 用户请求概念讲解 → 查看讲解内容 → 继续请求练习题

### Performance Testing

**测试指标：**
- Intent Router 响应时间 < 500ms
- QuizSkill 执行时间 < 3s
- 端到端响应时间 < 5s

**测试工具：** Locust（负载测试）

## Deployment Considerations

### Environment Variables

```bash
# backend/.env
GEMINI_API_KEY=AIzaSyCDfi8XPJFR_v-3zgL9FDf5HtfeDF14HVs
GEMINI_MODEL=gemini-2.5-flash
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:5173
```

### Docker Setup（未来扩展）

```dockerfile
# Dockerfile (backend)
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Development Workflow

1. **后端启动：**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```

2. **前端启动：**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **访问：**
   - 前端：http://localhost:5173
   - 后端 API：http://localhost:8000
   - API 文档：http://localhost:8000/docs

## Future Extensibility

### 1. 多技能 Pipeline（BundleSkill）

支持一次请求调用多个 Skill：

```python
class BundleSkill(BaseSkill):
    async def execute(self, params: Dict, context: Dict) -> Dict:
        results = {}
        
        # 依次调用：笔记 → 抽认卡 → 测验
        results["notes"] = await self.orchestrator.execute_skill("notes", params, context)
        results["flashcards"] = await self.orchestrator.execute_skill("flashcards", params, context)
        results["quiz"] = await self.orchestrator.execute_skill("quiz", params, context)
        
        return {"bundle": results}
```

### 2. 持久化存储

替换内存存储为 Redis（会话）+ MongoDB（用户画像）：

```python
class RedisMemoryManager(MemoryManager):
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def get_profile(self, user_id: str):
        data = await self.redis.get(f"profile:{user_id}")
        return UserLearningProfile(**json.loads(data))
```

### 3. 实时 WebSocket 更新

支持流式输出和进度推送：

```python
@router.websocket("/agent/ws")
async def websocket_agent(websocket: WebSocket):
    await websocket.accept()
    async for message in websocket.iter_text():
        async for chunk in orchestrator.execute_stream(message):
            await websocket.send_json(chunk)
```

### 4. 成本监控与预算控制

记录每次 LLM 调用的 token 消耗：

```python
class CostTracker:
    def __init__(self):
        self.costs = {}
    
    def track(self, user_id: str, tokens: int, model: str):
        cost = self._calculate_cost(tokens, model)
        self.costs[user_id] = self.costs.get(user_id, 0) + cost
```

## Summary

本设计文档完整描述了 Skill Agent Demo 的技术架构，涵盖：

✅ **4 个核心模块**：Intent Router、Memory Manager、Skill Orchestrator、Skill Registry  
✅ **2 个示例技能**：QuizSkill、ExplainSkill  
✅ **完整的 API 设计**：RESTful 接口 + Pydantic 模型  
✅ **前端架构**：React + Context/Reducer + TypeScript  
✅ **错误处理策略**：友好的用户提示 + 完善的 fallback  
✅ **测试策略**：单元测试 + 集成测试 + E2E 测试  

下一步将创建 **Tasks 文档**，将设计拆解为可执行的开发任务。

