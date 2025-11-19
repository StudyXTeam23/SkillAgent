# Memory Storage - 本地存储

这个目录用于存储用户的学习记忆（Memory）数据，方便查看和调试。

## 📁 文件结构

```
memory_storage/
├── profile_demo-user.json      # 用户学习画像（长期记忆）
├── session_demo-session.json   # 会话上下文（短期记忆）
└── README.md                    # 本文件
```

---

## 📄 文件说明

### 1. `profile_<user_id>.json` - 用户学习画像

**内容**：用户的长期学习记录

```json
{
  "user_id": "demo-user",
  "mastery": {
    "数学-微积分": 0.75,
    "历史-二战": 0.60
  },
  "preferences": {
    "preferred_artifact": "flashcard",
    "difficulty": "medium"
  },
  "learning_history": [],
  "created_at": "2025-11-18T16:00:00",
  "updated_at": "2025-11-18T16:30:00",
  "_last_updated": "2025-11-18T16:30:00.123456"
}
```

**说明**：
- `mastery`: 用户对各学科主题的掌握程度（0-1）
- `preferences`: 用户偏好（如喜欢闪卡、题目难度）
- `learning_history`: 学习历史记录
- `_last_updated`: 文件最后更新时间（调试用）

---

### 2. `session_<session_id>.json` - 会话上下文

**内容**：当前会话的短期记忆

```json
{
  "session_id": "demo-session",
  "current_topic": "二战历史的",
  "recent_intents": ["quiz_request", "explain_request"],
  "last_artifact": "Type: quiz_set | Topic: 二战历史的",
  "last_artifact_content": {
    "quiz_set_id": "quiz_20251118_001",
    "subject": "历史",
    "topic": "二战历史的",
    "questions": [
      {
        "question_id": "q1",
        "question_text": "珍珠港事件发生在哪一年？",
        "question_type": "multiple_choice",
        "options": ["A. 1939年", "B. 1941年", "C. 1943年", "D. 1945年"],
        "correct_answer": "B",
        "explanation": "珍珠港事件发生在1941年12月7日..."
      },
      {
        "question_id": "q2",
        "question_text": "诺曼底登陆发生在哪一年？",
        ...
      }
    ]
  },
  "last_user_message": "解释一下第一道题",
  "created_at": "2025-11-18T16:15:00",
  "updated_at": "2025-11-18T16:30:00",
  "_last_updated": "2025-11-18T16:30:00.123456"
}
```

**说明**：
- `current_topic`: 当前学习主题（用于上下文继承）
- `recent_intents`: 最近的意图历史（最多保留10个）
- `last_artifact`: 上一轮生成的学习内容类型和主题
- `last_artifact_content`: **完整的上一轮学习内容**（如quiz题目、解释内容等）
  - 这是实现上下文引用的关键！
  - 当用户说"解释一下第一道题"时，系统从这里提取第1题的内容
- `last_user_message`: 用户最后一条消息
- `_last_updated`: 文件最后更新时间（调试用）

---

## 🔍 如何使用

### 1. **实时查看 Memory 更新**

```bash
# 实时监控 session 文件变化
watch -n 1 cat memory_storage/session_demo-session.json

# 或使用 jq 格式化查看（如果安装了 jq）
watch -n 1 "cat memory_storage/session_demo-session.json | jq"
```

### 2. **查看具体内容**

```bash
# 查看用户画像
cat memory_storage/profile_demo-user.json | jq

# 查看会话上下文
cat memory_storage/session_demo-session.json | jq

# 查看上一轮生成的题目内容
cat memory_storage/session_demo-session.json | jq '.last_artifact_content.questions'

# 查看第1题的具体内容
cat memory_storage/session_demo-session.json | jq '.last_artifact_content.questions[0]'
```

### 3. **验证上下文引用是否生效**

测试序列：
```
1️⃣ 给我5道二战历史的题
   → 查看 session_demo-session.json
   → 应该看到 last_artifact_content 包含5道题

2️⃣ 解释一下第一道题
   → 后端会从 last_artifact_content.questions[0] 提取第1题
   → 作为 source_content 传递给 explain_skill
   → 生成针对该题的解释
```

---

## 🎯 调试技巧

### 问题1: 上下文引用失败

**检查**：
```bash
# 1. 确认 last_artifact_content 是否被正确保存
cat memory_storage/session_demo-session.json | jq '.last_artifact_content'

# 2. 确认题目数组是否存在
cat memory_storage/session_demo-session.json | jq '.last_artifact_content.questions | length'

# 3. 查看第1题的内容
cat memory_storage/session_demo-session.json | jq '.last_artifact_content.questions[0].question_text'
```

### 问题2: Topic 继承失败

**检查**：
```bash
# 1. 确认 current_topic 是否被正确设置
cat memory_storage/session_demo-session.json | jq '.current_topic'

# 2. 查看最近的意图历史
cat memory_storage/session_demo-session.json | jq '.recent_intents'
```

### 问题3: 用户偏好不生效

**检查**：
```bash
# 查看用户偏好设置
cat memory_storage/profile_demo-user.json | jq '.preferences'
```

---

## 📊 示例：完整的多轮对话 Memory 变化

### 第1轮: "给我5道二战历史的题"

**session_demo-session.json 变化**：
```json
{
  "current_topic": "二战历史的",  // ← 新设置
  "recent_intents": ["quiz_request"],  // ← 添加
  "last_artifact": "Type: quiz_set | Topic: 二战历史的",  // ← 新设置
  "last_artifact_content": {  // ← 保存完整题目内容
    "questions": [
      { "question_text": "珍珠港事件发生在哪一年？", ... },
      { "question_text": "诺曼底登陆发生在哪一年？", ... },
      ...
    ]
  }
}
```

### 第2轮: "解释一下第一道题"

**系统处理流程**：
1. 规则引擎识别：`explain_request` + `use_last_artifact=True`
2. Topic Fallback：从 `current_topic` 获取 "二战历史的"
3. 内容提取：从 `last_artifact_content.questions[0]` 提取第1题
4. 生成解释：基于第1题的具体内容

**session_demo-session.json 变化**：
```json
{
  "current_topic": "二战历史的",  // ← 保持不变
  "recent_intents": ["quiz_request", "explain_request"],  // ← 添加新意图
  "last_artifact": "Type: explanation | Topic: 二战历史的",  // ← 更新
  "last_artifact_content": {  // ← 更新为解释内容
    "concept": "珍珠港事件",
    "explanation": "...",
    ...
  }
}
```

---

## 🚀 下一步

1. **实时监控**：在一个终端窗口中运行 `watch` 命令
2. **测试对话**：在浏览器中进行多轮对话
3. **查看变化**：观察 memory 文件的实时更新
4. **验证逻辑**：确认上下文引用和 topic 继承是否正确

---

Good luck debugging! 🎉

