Skills 的统一实现接口说明文档
# Skill Implementation Signature 设计文档

本规范定义所有 Skills 的统一实现接口（execute signature），确保 Skill Orchestrator 可以以标准方式调用任意技能。

---

# 1. 设计目标

Skill 实现必须：

- 具有统一的输入与输出接口（与 Skill Registry 对齐）
- 支持参数校验（input_schema / output_schema）
- 内部逻辑可控、可测试、可扩展
- 能被 Orchestrator 低耦合调用
- 支持 pipeline 组合调用

---

# 2. Skill 目录结构（建议）

每个 Skill 是一个独立模块，推荐结构如下：
/skills/
  /skill_id/                    # 每个 Skill 一个独立文件夹
     skill.yaml                 # Skill Registry 声明（id / schema / model / dependencies）
     handler.py                 # Skill 的主执行逻辑（execute 实现）
     templates/
        prompt.jinja            # Prompt 模板（可选）
     schemas/
        input.schema.json       # 输入参数结构
        output.schema.json      # 输出参数结构
     resources/                 # 可选，例如 sample 数据、domain 参考资料
     tests/
        test_skill.py           # Skill 单元测试

---

# 3. Skill 执行函数签名（核心）

每个 Skill 必须实现以下类与方法：

```python
class Skill:
    def execute(self, params, context):
        """
        params: dict
            - 输入参数，必须符合 Skill Registry 的 input_schema

        context: dict
            - user_profile: dict（长期记忆）
            - session_context: dict（短期上下文）
            - memory_summary: string
            - content_context: list

        return: dict
            - 必须符合 output_schema
        """

---
1. 输入参数（params）
来自 Skill Registry 的 input_schema，例如 QuizSkill：
{
  "topic": "微积分-极限",
  "difficulty": "easy",
  "num_questions": 5
}
验证方式（伪代码）：
validate_schema(params, skill_json["input_schema"])

---
2. 上下文参数（context）
每个 Skill 的执行环境：
{
  "user_profile": {...},
  "session_context": {...},
  "memory_summary": "...",
  "content_context": [...]
}
说明：
- user_profile：用于个性化，比如难度选择
- session_context：用于理解当前对话主题
- memory_summary：用于增强 Skill 内部提示词
- content_context：从 Problem / Content Store 获取（题库、文档、用户上传内容）

---
3. Skill 返回格式（output_schema）
Skill 必须输出标准化 JSON，不允许随意返回文本。
例如 QuizSkill 的 output_schema：
{
  "questions": [
    {
      "id": "string",
      "stem": "string",
      "options": ["string"],
      "answer": "string",
      "explanation": "string"
    }
  ]
}
Skill 实现必须确保：
validate_schema(result, skill_json["output_schema"])

---
4. Skill 内部执行流程（模板）
通用执行逻辑：
execute():
    1. validate input params
    2. load prompt template (optional)
    3. build final prompt with:
        - params
        - memory_summary
        - content_context
        - template variables
    4. call LLM (primary model)
    5. parse structured output
    6. validate output_schema
    7. return structured result

---
5. 模型调用规范
所有 Skill 内部调用模型必须使用统一接口：
llm.call(model=skill_json["models"]["primary"], messages=[...])
若失败：
- fallback 到 models.fallback
- 若仍失败 → 返回错误并记录日志

---
6. Prompt 模板规范（可选）
建议每个 Skill 使用一个 prompt.txt 文件：
You are a Quiz generation agent.
Topic: {{topic}}
Difficulty: {{difficulty}}
Please return JSON:
{
   "questions": [...]
}
Skill 内部在执行时做变量替换。

---
7. Skill 单元测试要求
每个 Skill 需包含 tests 文件夹，测试用例包括：
✔ 输入参数校验
- 缺失字段（必填字段缺失）
- 类型错误（string → number）
✔ 模型输出结构解析
- 非 JSON 返回
- 字段缺失
- 嵌套结构错误
✔ output_schema 校验
确保输出符合 Skill Registry 要求。
✔ pipeline 兼容性
对组合技能依赖的上游输出进行测试。

---
8. Skill 实现示例（QuizSkill）
class QuizSkill(Skill):
    def execute(self, params, context):

        # Step 1: Validate input
        validate_schema(params, skill_json["input_schema"])

        # Step 2: Build prompt
        prompt = load_prompt("prompt.txt").format(
            topic=params["topic"],
            difficulty=params.get("difficulty", "medium"),
            content_context=context.get("content_context", [])
        )

        # Step 3: Call LLM
        raw_output = llm.call(
            model=skill_json["models"]["primary"],
            messages=[{"role": "user", "content": prompt}]
        )

        # Step 4: Parse structured output
        result = json.loads(raw_output)

        # Step 5: Validate output_schema
        validate_schema(result, skill_json["output_schema"])

        return result

---
9. 总结
Skill Implementation Signature 统一了：
- 输入与输出规则
- 模型调用方式
- 上下文管理方式
- pipeline 组合的可扩展性
它是 Skill Agent 可维护与可扩展性的核心基础设施。