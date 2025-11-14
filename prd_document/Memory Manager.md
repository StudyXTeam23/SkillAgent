Memory Manager（记忆管理模块设计文档）

---
# Memory Manager 数据结构设计文档

Memory Manager 是 Skill Agent 的记忆中枢，用于管理：
- 用户长期学习画像（UserLearningProfile）
- 当前对话的短期记忆（SessionContext）
- 供意图判断使用的 memory_summary

---

# 1. 模块职责

## Memory Manager 负责：
- 提供用于 Intent Router 的「记忆摘要」
- 提供用户学习状态给 Skill Orchestrator
- 在 Skill 执行后更新长期/短期记忆
- 为所有 Skills 提供统一的用户上下文

## 不负责：
- 不做推理和生成
- 不做知识库检索
- 不维护向量数据库（由 Problem/Content Store 管理）

---

# 2. 数据结构定义

## 2.1 UserLearningProfile（长期学习画像）

```json
{
  "user_id": "string",
  "mastery": {
    "topic_subtopic": "weak | medium | strong"
  },
  "preferences": {
    "preferred_artifact": "quiz | explanation | notes | flashcards",
    "difficulty_preference": "easy | medium | hard"
  },
  "history": {
    "quiz_sessions": "number",
    "homework_help_count": "number",
    "topics_visited": ["string"]
  },
  "updated_at": "string"
}
字段说明：
- mastery：按主题存储掌握度，如“微积分-极限: weak”
- preferences：用户偏好，用于 artifacts 类型选择
- history：各种学习行为的累计统计

---
2.2 SessionContext（短期记忆）
{
  "session_id": "string",
  "current_topic": "string | null",
  "recent_intents": ["string"],
  "last_artifact": "string | null",
  "last_user_message": "string",
  "updated_at": "string"
}
字段说明：
- current_topic：当前对话主题，如“微积分-极限”
- recent_intents：最近意图序列
- last_artifact：上一轮生成的内容，如 quiz_set、notes_document

---
2.3 Memory Summary（提供给 Intent Router）
Memory Manager 会生成：
{
  "topic_hint": "string | null",
  "user_mastery_hint": "weak | medium | strong",
  "recent_behavior": "string"
}
示例：
{
  "topic_hint": "微积分-极限",
  "user_mastery_hint": "weak",
  "recent_behavior": "用户刚做过极限练习题"
}

---
3. API 设计
3.1 获取长期记忆
GET /memory/user/{user_id}
返回 UserLearningProfile
3.2 获取短期记忆
GET /memory/session/{session_id}
返回 SessionContext
3.3 更新长期记忆
POST /memory/user/update
Body 示例：
{
  "user_id": "u123",
  "event": {
    "intent": "quiz",
    "topic": "微积分-极限",
    "artifact": "quiz_set",
    "metadata": {
      "difficulty": "easy",
      "correct_rate": 0.4
    }
  }
}
更新逻辑：
- mastery["微积分-极限"] → 调整（可能从 weak → medium）
- history.quiz_sessions++
- topics_visited 添加相关主题

---
3.4 更新短期记忆
POST /memory/session/update
Body:
{
  "session_id": "s456",
  "intent": "quiz",
  "topic": "微积分-极限",
  "artifact": "quiz_set"
}
更新逻辑：
- recent_intents 更新
- current_topic 覆盖
- last_artifact 修改

---
4. Memory Summary 生成逻辑
每次 Intent Router 调用前：
1. 提取 SessionContext.current_topic → topic_hint
2. 提取 UserLearningProfile.mastery[topic_hint] → user_mastery_hint
3. 读取历史行为生成 recent_behavior 文本
返回结构化摘要（用于意图判断增强）。

---
5. 状态更新机制
更新时机：
- 每次 Skill Orchestrator 执行完成后
- 在返回 UI 之前
更新步骤：
1. 根据 event 更新 SessionContext
2. 根据 event 更新 UserLearningProfile
3. 写入数据库或缓存

---
6. 持久化方案建议
- SessionContext → Redis（短期、频繁变动）
- UserLearningProfile → DynamoDB / MongoDB（长期稳定记录）

---
7. 单元测试要求
- mastery 更新正确性
- topic 流转正确性
- session 垃圾累积控制
- 状态读写稳定性