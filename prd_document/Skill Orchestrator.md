Skill Orchestrator（功能编排模块设计文档）
📘 Skill Orchestrator Pipeline.md
# Skill Orchestrator Pipeline 设计文档

Skill Orchestrator 是整个 Skill Agent 的调度核心。  
负责：**intent → skill 选择 → 参数构建 → 执行技能 → 结果封装 → 更新记忆**。

---

# 1. 模块职责

Skill Orchestrator 主要承担以下任务：

## 1.1 Intent → Skill 映射
- 根据 Intent Router 解析结果（intent/topic/artifact）
- 从 Skill Registry 查找所有可处理该意图的技能

## 1.2 技能选择策略  
从多个技能候选中选择“最合适”的技能，依据：
- 能力匹配（intent_tags）
- 成本（model_class）
- Skill 依赖的上下文是否可用
- 用户偏好（例如喜欢 quiz 或 flashcards）
- 历史行为（例如“最近常做练习题”）

## 1.3 Skill 输入参数构建
为 Skill 生成标准化输入，包括：
- topic（来自 Intent/Memory）
- user_profile（长期记忆）
- session_context（短期记忆）
- content_context（题目 / 文档上下文）
- difficulty / num_questions 等业务参数

## 1.4 执行单技能或多技能 pipeline
- 调用 Skill 的统一执行接口  
- 负责 pipeline（BundleSkill）的多技能顺序执行  

## 1.5 输出封装  
所有 Skill 结果被封装为统一 artifact 格式，返回给 UI。

## 1.6 通知 Memory Manager 更新记忆  
Skill 执行后生成事件 event，推送到 Memory Manager 进行长期/短期记忆更新。

---

# 2. 输入结构

```json
{
  "intent_result": {
    "intent": "quiz",
    "topic": "微积分-极限",
    "target_artifact": "quiz_set",
    "confidence": 0.86
  },
  "user_profile": { ... },     // 来自 Memory Manager
  "session_context": { ... },  // 来自 Memory Manager
  "user_message": "string"
}

---
1. 输出结构
{
  "type": "quiz_set",
  "payload": {},
  "meta": {
    "source_skill": "QuizSkill",
    "topic": "微积分-极限"
  }
}

---
2. Pipeline 调度流程（核心）
Skill Orchestrator 的工作流程可以拆为 7 个阶段：

---
Step 1: Intent → Candidate Skills
candidate_skills = registry.find_by_intent(intent_result.intent)
例如：
intent = "quiz"
→ ["QuizSkill"]
若是 bundle 意图：
intent = "bundle"
→ ["BundleSkill"]

---
Step 2: 技能选择策略（Skill Selection）
策略排序建议：
1. 可用技能（context.need_user_memory 等需求满足）
2. 成本最低（model_class: small < medium < large）
3. 用户偏好匹配
4. Pipeline 依赖是否完整
示例：
selected_skill = choose_best_skill(candidate_skills, user_profile)

---
Step 3: 获取技能定义（通过 Registry）
skill_def = registry.get(selected_skill)
技能定义包括：
- input_schema
- output_schema
- models
- context 需求（memory? content store?）
- composable & dependencies

---
Step 4: 构建 Skill 输入参数
构建统一输入：
{
  "params": {
    "topic": "微积分-极限",
    "difficulty": "easy",
    "num_questions": 5
  },
  "context": {
    "user_profile": { ... },
    "session_context": { ... },
    "memory_summary": "...",
    "content_context": [...]
  }
}
参数构建来源：
- intent_result（如 topic）
- user_profile（如 mastery → 推断 difficulty）
- session_context（如最近正在讨论的主题）
- content_store（获取相关题目/文档）

---
Step 5: 执行技能
统一调用接口：
POST /skills/{skill_id}/execute
执行流程：
1. Validate params using input_schema
2. 执行 Skill 的 implement.py
3. 调用模型（skill_def.models.primary）
4. 解析模型返回
5. 校验 output_schema
6. 返回结果

---
Step 6: 封装成统一 Artifact
例如：
{
  "type": "quiz_set",
  "payload": { "questions": [...] },
  "meta": {
    "source_skill": "QuizSkill",
    "topic": "微积分-极限"
  }
}
Artifact 类型例子：
- answer_card
- notes_document
- flashcard_set
- quiz_set
- explanation
- learning_bundle

---
Step 7: 更新 Memory Manager
生成事件 event：
{
  "intent": "quiz",
  "topic": "微积分-极限",
  "artifact": "quiz_set",
  "skill_id": "QuizSkill",
  "timestamp": "2025-11-13T10:00:00Z"
}
调用：
POST /memory/user/update
POST /memory/session/update

---
3. 多技能 Pipeline（BundleSkill）
如果一个技能定义中：
"dependencies": ["notes", "flashcards", "quiz"]
Orchestrator 执行逻辑：
result_notes = execute(SkillNotes)
result_flashcards = execute(SkillFlashcards, input=notes)
result_quiz = execute(SkillQuiz, input=flashcards)
final_output = merge(results) 
Bundled 技能适用于：
- “生成学习包”
- “讲解 + 练习题 + 抽认卡”
- “复习笔记 → 重点 → 练习 → 测验”

---
4. 错误处理机制
错误类型：
1. Skill 找不到
2. input_schema 校验失败
3. Skill 执行超时
4. 模型输出格式错误
5. output_schema 校验失败
处理策略：
- fallback 模型（primary → fallback）
- fallback Skill（如 quiz → explain）
- 降级返回自然语言解释
- 上报日志

---
5. 成本优化策略（可选）
Pipeline 的成本优化包括：
- 优先 small 模型（mini）
- 只有需要内容检索时才加载 content_context
- memory_summary 不超过 2–3 句话
- 禁止短时间重复生成大 artifact（如生成学习包）

---
6. 单元测试要求
- intent → skill 映射正确
- pipeline 顺序正确
- input/output schema 通过
- fallback 正常工作
- content_context 读取正确