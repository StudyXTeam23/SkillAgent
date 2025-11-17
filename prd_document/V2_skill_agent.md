Skill Agent v2 进阶开发设计
基于现有 Skill Agent Prototype（FastAPI + React + Gemini + YAML Skills）
目标：在不推翻架构的前提下，增强 模糊问题处理能力 / 多步任务跳跃 / 并行 & API 复用 三个核心能力。

---
1. 当前 Prototype 能力小结（作为 v2 起点）
当前版本已经具备的核心能力：
- 统一入口：POST /api/agent/chat，前端 React Chat UI + 各种卡片组件（QuizCard / ExplainCard / Flashcard 等）。
- 四大核心模块：
  - Intent Router：意图识别 + 混合请求解析
  - Memory Manager：学习画像 + 会话上下文 + 偏好学习
  - Skill Registry：YAML 驱动，5 个技能（Quiz / Explain / Flashcard / Learning Bundle / MindMap）
  - Skill Orchestrator：按意图选择、执行技能，支持混合请求（quiz + flashcards）
- Prompts 系统：backend/app/prompts/ 下已存在 intent_router / memory_summary / 各 Skill Prompt。
- 测试完备：Intent / Memory / Skill Orchestrator / Registry / Skills 集成都有测试用例。
换句话说：v1 已经把“Agent 基础骨架”搭好了，v2 要做的是「让骨架动起来更聪明」，而不是重建。

---
2. v2 设计目标
围绕提出的三个问题，我们给 v2 的设计目标拆成三块：
1. 模糊问题处理
  - 从「一次性命中某个 Skill」升级为「支持模糊意图 + 多候选 Skill + 链式试探」。
  - Search / Memory / Intent Router / Orchestrator 之间打通信息流。
2. 架构简洁 & 任务跳跃
  - 在保持 “大脑（Planner）+ 躯干（Skills）+ 裁判（Memory/Coordinator）” 模型下，
让「解题 → 讲解 → 做题 → 笔记 → 再出题」这样的跳跃无需写一堆 if else。
3. API & 并行 & Manus 模式
  - 保留/复用现有 code/API，只是在其上包一层 Skill。
  - 支持“一次内容解析 → 多 Skill 并行生成不同学习材料”的模式，降低整体 token 成本。

---
3. 模糊问题处理：Search → Intent → Skill 链式决策
3.1 新增轻量 ContextCollector
在 backend/app/core/ 增加一个模块：
- 文件：context_collector.py
- 作用：聚合所有可用的上下文信息，输出统一的 analysis_context：
@dataclass
class AnalysisContext:
    user_profile: UserLearningProfile | None
    session_context: SessionContext | None
    recent_turns: list[str]
    uploads_summary: str | None  # 未来接入课程资料/文件
在 agent.py 里调用顺序变为：
analysis_context = ContextCollector.collect(user_id, session_id)
intent_result = IntentRouter.route(message, analysis_context)
result = SkillOrchestrator.execute(intent_result, analysis_context)
✅ 这样可以把「能拿到的用户信息」先收齐，再统一交给意图判断。

---
3.2 扩展 Intent Router：支持“意图分布 + 主意图 + 备选意图”
在现有 intent_router.py 的输出模型上做小改动：
class IntentCandidate(BaseModel):
    intent: str
    score: float

class IntentResult(BaseModel):
    primary_intent: str
    candidates: list[IntentCandidate]  # 排好序
    topic: str | None
    target_artifact: str | None
    confidence: float
Prompt 级改动（prompts/intent_router.txt）：
- 从“单一 intent”改为“返回一个排序列表（top3 intents + score）”。
- 同时返回 primary_intent（score 最高那个），但 candidates 保留备用。
✅ 这让模糊输入可以合理地表示成「homework 0.7, explain 0.6, quiz 0.3」。

---
3.3 Orchestrator 支持 “探索式 Skill 路径”
在 skill_orchestrator.py 中扩展接口，让其接收 IntentResult 的候选列表，并选择：
1. 当前轮主 Skill
2. 可选的“下一步候选 Skill”列表（用于 UI 推荐 / 下一轮 Planner 参考）
伪代码：
def plan_skills(intent_result: IntentResult, analysis_context: AnalysisContext) -> ExecutionPlan:
    primary = choose_primary_skill(intent_result.primary_intent)
    next_candidates = suggest_followup_skills(intent_result.candidates, analysis_context)

    return ExecutionPlan(
        current_skill=primary,
        suggested_next_skills=next_candidates  # 非强制执行，只是 plan
    )
前端可以用 suggested_next_skills 来展示：
“要不要顺便帮你讲解这个概念 / 出几道练习题？”
✅ 回答核心问题：
处理模糊问题时，我们不是强求一次命中，而是让 Orchestrator 拿到意图分布后：先选主 Skill，再设计“后续可能 Skill 的路线图”。

---
4. 架构简洁 & 任务跳跃：Planner / Skills / Memory 三层协作
4.1 显式抽象出 Planner（大脑）
在现有 skill_orchestrator.py 上面再加一层轻薄的 Planner：
- 文件：planner.py
- 职责：
  - 接收 IntentResult + AnalysisContext
  - 生成一个简单的 ExecutionPlan：
    - 当前要用的 Skill
    - 是否需要 pipeline（例如：先 Explain 再 Quiz）
    - 有无预期的后续技能
Planner 伪代码：
class Planner:
    def make_plan(self, intent_result: IntentResult, ctx: AnalysisContext) -> ExecutionPlan:
        # 根据 primary_intent + 用户偏好 做决策
        # e.g. 用户强偏好 flashcards，则在 explain 后追加 flashcards
然后：
plan = Planner.make_plan(intent_result, analysis_context)
result = SkillOrchestrator.run_plan(plan, analysis_context)
✅ “大脑只决定下一步用哪个 Skill / 是否要 pipeline”，不参与 Skill 内部实现。

---
4.2 Skill 之间不直接通信，只通过 Memory & Plan
关键设计点：
- 每个 Skill 执行结束后，必须发一个简单的 SkillEvent 给 Memory：
class SkillEvent(BaseModel):
    skill_id: str
    intent: str
    topic: str | None
    artifact_type: str
    artifact_id: str | None
- Memory Manager 根据 SkillEvent 更新：
  - UserLearningProfile（知识点掌握度、偏好等）
  - SessionContext（current_topic、last_artifact、recent_intents）
下一轮 Planner & Orchestrator 再根据 Memory 决定 Skill。
✅ 这样“解题 → 讲解 → 做题 → 笔记 → 再做题”的跳跃，
都只是重复：“新输入 + 新记忆 → 新计划 → 新 Skill”
Skill 之间永远不互相 import / 调用。

---
4.3 任务跳跃的 v2 示例落地
在你现有 demo 基础上增加一个「学习链」示范：
1. 用户：
1. “给我 3 道极限练习题。”
  - Planner → intent = quiz
  - Orchestrator → QuizSkill
  - Memory 记录：topic=极限，artifact=quiz_set
2. 用户：
1. “第 2 题我不会，讲一下。”
  - Intent Router → explain
  - Planner → 选择 ExplainSkill
  - ExplainSkill 从 Memory 中拿到上一轮 quiz 的第二题，进行讲解。
3. 用户：
1. “顺便整理成一份笔记。”
  - Intent Router → note_taking
  - Planner → NotesSkill（可以在 v2 新增）
  - NotesSkill 同样只看 Memory 中的 quiz + explain 结果，无需知道 Skill 之间关系。
✅ 用这个链式 Demo，展示“大脑/躯干/裁判”分工清晰 & 跳跃自然。

---
5. API & 并行：Manus 式“一次解析，多 Skill 复用”
5.1 API 不变：继续使用统一聊天入口
现有统一入口：
- POST /api/agent/chat
已经非常适合作为 Skill Agent 的唯一入口，无需额外增加多个 API。
在内部，我们在 Orchestrator 层新增两个能力：
1. Content Analysis Skill（重解析 Skill）
2. Parallel Skill Execution（并行执行器）

---
5.2 新增 ContentAnalysisSkill（一次重解析）
- 新增一个技能配置：content_analysis_skill.yaml
- 提供功能：
  - 对长文本 / 视频转写 / 多文件内容做一次统一解析：
    - 主题
    - 知识点列表
    - 章节结构
    - 重要示例 / 练习题候选
执行模式：
analysis = ContentAnalysisSkill.execute(params, context)
# 把 analysis 结果写入 Content Store 或 Memory 的一个字段
✅ 重 token 成本集中在一次调用上。

---
5.3 在 Orchestrator 中支持并行执行多个 Skill
在 skill_orchestrator.py 中增加一个并行执行函数：
async def execute_skills_parallel(skills: list[SkillCall], shared_ctx: AnalysisContext) -> list[SkillResult]:
    tasks = [
        run_single_skill(call, shared_ctx)
        for call in skills
    ]
    return await asyncio.gather(*tasks)
结合 ContentAnalysisSkill，可以做到：
1. 一次解析：ContentAnalysisSkill 输出 analysis_ctx
2. 复用 analysis_ctx 并行调用：
  - NotesSkill
  - QuizSkill
  - FlashcardSkill
  - PodcastSkill（未来接现有 TTS API）

---
5.4 Manus 风格 Demo：一次讲座，多产物输出
在现有 demo UI 上加一个新场景：
输入示例：
“这是我今天的微积分课笔记内容（或者上传后的转写），帮我生成学习材料。”
内部流程：
1. Planner 识别 intent = bundle（学习包）
2. Execution Plan：
  - Step 1：ContentAnalysisSkill（串行）
  - Step 2：[NotesSkill, QuizSkill, FlashcardSkill]（并行）
  - Step 3：LearningBundleSkill（汇总）
3. 前端展示一个完整「学习包卡片」：
  - 上面“学习路线（先看笔记，再做题，再复习卡片）”
  - 下面展开各个子卡片（Explain / Quiz / Flashcards）
✅ 这样可以非常直观地展示：
- 我们是一次理解内容，多 Skill 共享
- Skill 之间通过 shared context & plan 复用结果
- 并行执行 Skill，整体延迟和 token 成本可控
- 现有 Quiz / Explain / Flashcard / Learning Bundle Skill 全部复用，无浪费

---
6. v2 开发任务拆解（面向现在的仓库）
结合当前项目结构，可以把 v2 进阶开发拆成几条很清晰的任务：
6.1 Core 层改动（/backend/app/core）
1. 新增 context_collector.py
2. 扩展 intent_router.py：支持意图分布 & topic 输出
3. 新增 planner.py：生成 ExecutionPlan
4. 扩展 skill_orchestrator.py：
  - 接受 ExecutionPlan
  - 支持并行执行
  - 支持 ContentAnalysisSkill → 多 Skill pipeline
5. 扩展 memory_manager.py：支持接收 SkillEvent 更新 Profile & Session
6.2 Skill 增强（skills_config + prompts）
1. 新增 content_analysis_skill.yaml + 对应 Prompt
2. 预留 NotesSkill（笔记生成）：
  - YAML + prompt + 简单 handler
3. 对现有 learning_bundle_skill 做小改造：支持吃多个子产物汇总。
6.3 前端改造（frontend/src）
1. 在 Chat UI 加一个“推荐下一步”区域：
  - 使用 Orchestrator 返回的 suggested_next_skills
2. 为学习包场景增加一个「LearningBundleCard」组件：
  - 卡片内嵌 QuizCard / ExplainCard / FlashcardCard
6.4 Demo 场景脚本
准备三条可现场演示的对话脚本：
1. 模糊意图 + Skill 探索（解题 → 讲解 / 出题的拉扯）
2. 多步任务跳跃（解题 → 讲解 → 笔记 → 测验）
3. Manus 式并行学习包（一次内容 → 多 Skill 并行输出）

---
7. 总结：v2 的定位
- 不推倒现有 prototype，而是自然进化：
  - 利用现有 Intent Router / Memory Manager / Orchestrator / Registry / Skills。
- 解决核心的三个问题的方式是“用架构 + Demo 同时回答”：
  - 模糊 → 意图分布 + Skill 链
  - 跳跃 → Planner + Skills + Memory 解耦
  - 并行 → ContentAnalysisSkill + 并行 Orchestrator + API 封装
换句话说：
v1 证明了我们能做一个 Skill Agent；
v2 要证明的是：这个 Agent 架构是可以「真正在 StudyX 里规模落地」的。
