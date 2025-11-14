Intent Router（意图分类模块设计文档）
# Intent Router API 设计文档

## 1. 模块概述
Intent Router 是 Skill Agent 的前置分类器。  
负责：**解析用户输入 → 输出结构化意图 JSON**。  
目标：轻量、低成本、高准确度。

---

## 2. 输入结构（Input Schema）

```json
{
  "user_id": "string",
  "session_id": "string",
  "current_message": "string",
  "recent_turns": ["string"],
  "memory_summary": "string"
}
说明：
- current_message：用户的自然语言输入
- recent_turns：Memory Manager 生成的简要最近上下文（1–3 句）
- memory_summary：长期 + 短期学习画像摘要（1–2 句）

---
3. 输出结构（Output Schema）
{
  "intent": "string | string[]",
  "topic": "string | null",
  "target_artifact": "string | null",
  "confidence": "number",
  "raw_text": "string"
}
字段说明：
- intent：如 homework_help / quiz / explain / note_taking
- topic：如“微积分-极限”
- target_artifact：如 quiz_set / flashcard_set
- confidence：识别置信度，0–1
- raw_text：原始输入

---
4. 支持意图列表（初始版）
- homework_help
- explain
- note_taking
- quiz
- flashcards
- tutor
- bundle
- other

---
5. API 接口定义
/intent_router/parse
Method: POST
Body: Input Schema
Return: Output Schema
示例：
{
  "user_id": "u123",
  "current_message": "给我几道极限练习题",
  "recent_turns": ["上一轮讨论过极限定义"],
  "memory_summary": "用户在极限掌握度偏弱"
}

---
6. 内部流程（简化版）
1. 小模型分类（轻量 LLM / 分类器）
2. 关键字增强匹配（rule-based）
3. 利用 memory 补全 topic
4. 返回结构化格式

---
7. 置信度策略
- ≥ 0.6：接受该意图
- 0.3–0.6：intent = "other"，建议反问
- < 0.3：fallback 至默认 explain

---
8. 错误处理
- 输入缺失字段 → 400
- 模型超时 → 使用备选 rule-based

---
9. 单元测试要求
- 意图分类准确性
- topic 抽取准确性
- 多轮上下文一致性