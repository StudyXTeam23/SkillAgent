Skill Registry Schema（功能注册数据模块设计文档）
# Skill Registry Schema 设计文档

Skill Registry 是 Skill Agent 的“技能声明中心”。  
它提供统一的、结构化的技能定义，供 Skill Orchestrator 进行技能发现、参数校验和执行决策。

---

# 1. 模块职责

Skill Registry 负责：

- 注册 / 管理所有技能（Skills）
- 提供技能的输入输出 schema
- 提供模型配置（primary/fallback）
- 声明技能对上下文的依赖（memory、content store）
- 声明技能是否可组合（pipeline）
- 为 Skill Orchestrator 提供查询接口

Skill Registry **不负责**执行技能，也不生成内容。

---

# 2. Registry 存储结构

建议文件存储结构（可 JSON / YAML）：
/skills/
  /quiz/
     skill.json
  /homework_help/
     skill.json
  /explain/
     skill.json
  /notes/
     skill.json
  /flashcards/
     skill.json
  /tutor/
     skill.json
  /bundle/
     skill.json

每个文件代表一个 Skill 的声明。

---

# 3. Skill Definition Schema（完整版）

下面是每个技能 JSON 的统一 schema：

```json
{
  "id": "string",
  "display_name": "string",
  "version": "string",

  "intent_tags": ["string"],

  "input_schema": {
    "type": "object",
    "properties": {},
    "required": []
  },

  "output_schema": {
    "type": "object",
    "properties": {}
  },

  "models": {
    "primary": "string",
    "fallback": "string"
  },

  "context": {
    "need_user_memory": "boolean",
    "need_content_store": "boolean",
    "retrieve_top_k": "number"
  },

  "cost": {
    "model_class": "small | medium | large",
    "context_size": "small | medium | large",
    "expected_rounds": "number"
  },

  "composable": "boolean",
  "dependencies": ["string"]
}

---
1. 字段解释（核心）
id
技能唯一标识，如 "quiz"。
display_name
用户可见名称，如 "练习题生成"。
intent_tags
此技能可处理的意图，比如：
- quiz
- explain
- homework_help
用于 Intent → Skill 选择。
input_schema
该 Skill 接受哪些参数（JSON Schema 标准）。
output_schema
Skill 返回的结构是什么（统一规范）。
models
声明：
- primary: 主用模型，如 gpt-4o-mini
- fallback: 备用模型，如 gpt-4o
context
Skill 是否需要 Memory 或 Content Store 作为输入。
字段：
- need_user_memory：是否需要 Memory Manager 信息
- need_content_store：是否需要查题库或文档
- retrieve_top_k：最多要几条上下文
cost
技能的成本概览（用于 Orchestrator 策略）：
- model_class: small / medium / large
- context_size: small / medium / large
- expected_rounds: 预估调用次数（pipeline 中使用）
composable
是否允许被其他技能作为 pipeline 组成部分。
如：
- LectureNotesSkill → FlashcardSkill → QuizSkill
dependencies
若是组合技能，这里声明依赖的技能 ID 列表。

---
2. 示例：QuizSkill 声明
{
  "id": "quiz",
  "display_name": "练习题生成",
  "version": "1.0.0",

  "intent_tags": ["quiz"],

  "input_schema": {
    "type": "object",
    "properties": {
      "topic": { "type": "string" },
      "difficulty": { "type": "string" },
      "num_questions": { "type": "number" }
    },
    "required": ["topic"]
  },

  "output_schema": {
    "type": "object",
    "properties": {
      "questions": { "type": "array" }
    }
  },

  "models": {
    "primary": "gpt-4o-mini",
    "fallback": "gpt-4o"
  },

  "context": {
    "need_user_memory": true,
    "need_content_store": true,
    "retrieve_top_k": 5
  },

  "cost": {
    "model_class": "small",
    "context_size": "small",
    "expected_rounds": 1
  },

  "composable": true,
  "dependencies": []
}

---
3. Registry API 设计
6.1 获取全量技能列表
GET /skills
6.2 获取指定技能定义
GET /skills/{id}
6.3 校验输入输出 schema
POST /skills/validate
Body:
{
  "skill_id": "quiz",
  "params": {
    "topic": "微积分-极限",
    "difficulty": "easy"
  }
}

---
4. 运行时行为
Orchestrator 会通过：
registry.get_skills_by_intent(intent)
查找技能列表。
若多个技能满足条件，则按：
1. 成本（cost.model_class）
2. 用户偏好
3. 上下文需求满足度
进行排序选择。

---
5. 单元测试要求
- schema 加载正确
- input/output 校验通过
- intent → skill 匹配正确
- dependencies 可解析