# Skill Agent Demo 测试指南

## 📋 测试概览

本测试指南涵盖以下功能模块：
- ✅ **核心Skills测试**（Quiz、Explain、Flashcard、Learning Bundle）
- ✅ **数量控制测试**（精确数量、默认数量）
- ✅ **偏好系统测试**（建立偏好、偏好生效、偏好切换）
- ✅ **意图识别测试**（明确意图 vs 模糊意图）
- ✅ **边界情况测试**（错误处理、特殊场景）

---

## 1️⃣ 核心Skills测试

### 1.1 Quiz Skill（练习题生成）

#### 测试目标
验证系统能够正确生成练习题，并支持不同学科和数量。

#### 测试步骤

**步骤1：基础测试（默认数量）**
```
输入："给我几道微积分练习题"
预期：
- ✅ 识别为 quiz_request
- ✅ 生成 5 道微积分题目（默认值）
- ✅ 题目包含：题干、选项、正确答案、解析
```

**步骤2：指定数量测试**
```
输入："给我3道二元一次方程练习题"
预期：
- ✅ 识别为 quiz_request
- ✅ 生成恰好 3 道题（不是5道）
- ✅ 后端日志显示："📊 Extracted quantity: 3 for quiz_skill"
```

**步骤3：大数量测试**
```
输入："出10道物理力学的题"
预期：
- ✅ 生成恰好 10 道题
- ✅ 后端日志显示："📊 Extracted quantity: 10 for quiz_skill"
```

**步骤4：不同学科测试**
```
输入："给我几道历史练习题"
预期：
- ✅ 生成历史相关题目
- ✅ 题目适合历史学科特点（如选择题、问答题）
```

---

### 1.2 Explain Skill（概念讲解）

#### 测试目标
验证系统能够清晰讲解概念，包含直观理解、正式定义、例子。

#### 测试步骤

**步骤1：基础概念讲解**
```
输入："解释一下什么是导数"
预期：
- ✅ 识别为 explain_request
- ✅ 返回结构化讲解，包含：
  - concept（概念名称）
  - intuition（直观理解）
  - formal_definition（正式定义）
  - examples（至少2-3个例子）
  - common_mistakes（常见错误）
```

**步骤2：检查例子部分**
```
输入："讲解一下光合作用"
预期：
- ✅ examples 数组不为空
- ✅ 每个例子包含 "example" 和 "explanation" 字段
- ✅ 前端UI正确渲染例子（带序号、缩进）
```

**步骤3：不同学科概念**
```
输入："什么是化学反应"
预期：
- ✅ 生成化学相关讲解
- ✅ 包含化学领域的例子和公式
```

---

### 1.3 Flashcard Skill（抽认卡生成）

#### 测试目标
验证系统能够生成Anki风格的闪卡，包含front/back、hints。

#### 测试步骤

**步骤1：基础闪卡生成**
```
输入："给我一些光合作用的闪卡"
预期：
- ✅ 识别为 flashcard_request
- ✅ 生成 5 张闪卡（默认值）
- ✅ 每张卡包含：front（问题）、back（答案）、hints（提示）
```

**步骤2：指定数量**
```
输入："给我3张牛顿定律的闪卡"
预期：
- ✅ 生成恰好 3 张闪卡
- ✅ 后端日志："📊 Extracted quantity: 3 for flashcard_skill"
```

**步骤3：不同闪卡类型**
```
输入："帮我准备细胞结构的闪卡"
预期：
- ✅ 生成basic类型的闪卡
- ✅ 前端UI正确渲染闪卡（可翻转查看答案）
```

---

### 1.4 Learning Bundle Skill（学习包生成，这步时间稍微久一点）

#### 测试目标
验证系统能够生成综合学习包，包含多种学习组件。

#### 测试步骤

**步骤1：完整学习包**
```
输入："帮我准备电磁学的完整学习资料"
预期：
- ✅ 识别为 learning_bundle
- ✅ 返回学习包，包含：
  - explanation（概念讲解）
  - flashcard_set（闪卡）
  - quiz_set（练习题）
- ✅ 不报错（datetime已导入）
```

**步骤2：不同主题**
```
输入："给我化学反应的学习包"
预期：
- ✅ 生成化学相关的综合学习包
- ✅ 各个组件内容相关联
```

---

## 2️⃣ 数量控制测试

### 测试目标
验证系统能够精确控制题目和闪卡的数量。

### 测试矩阵

| 输入 | 预期Skill | 预期数量 | 备注 |
|------|----------|---------|------|
| "给我几道微积分题" | quiz_skill | 5 | 默认值 |
| "给我2道物理题" | quiz_skill | 2 | 用户指定 |
| "出10道化学题" | quiz_skill | 10 | 用户指定 |
| "给我一些光合作用的闪卡" | flashcard_skill | 5 | 默认值 |
| "给我3张牛顿定律的闪卡" | flashcard_skill | 3 | 用户指定 |
| "化学反应"（建立quiz偏好后） | quiz_skill | 5 | 默认值 + 偏好 |

### 验证方法

**后端日志检查：**
```
✅ "📊 Extracted quantity parameter: X"
✅ "📊 Extracted quantity: X for quiz_skill/flashcard_skill"
```

**前端UI检查：**
```
✅ 数量与输入完全一致
✅ 不多不少
```

---

## 3️⃣ 偏好系统测试

### 3.1 建立Flashcard偏好

#### 步骤1：连续使用Flashcard（建立80%偏好）
```
1. "给我一些光合作用的闪卡"
2. "帮我准备细胞结构的闪卡"
3. "闪卡：牛顿定律"
4. "化学反应的闪卡"
```

**预期后端日志：**
```
✅ "✨ User preference detected: [User Preference: Strongly prefers flashcards for learning (80% of recent activities)]"
```

#### 步骤2：测试模糊意图（偏好应生效）
```
输入："电磁学"
预期：
- ✅ 识别为 flashcard_request（不是 explain_request）
- ✅ confidence: 0.70-0.80
- ✅ 生成闪卡
```

```
输入："帮我准备一下化学反应"
预期：
- ✅ 识别为 flashcard_request
- ✅ 生成闪卡
```

#### 步骤3：测试明确意图（偏好不应覆盖）
```
输入："解释一下化学反应"
预期：
- ✅ 识别为 explain_request（尊重明确意图）
- ✅ confidence: 0.85-0.90
- ✅ 生成概念讲解（不是闪卡）
```

---

### 3.2 建立Quiz偏好

#### 步骤1：连续做题（建立70%偏好）
```
1. "给我几道微积分练习题"
2. "给我几道二战历史练习题"
3. "给我几道化学练习题"
4. "给我3道二元一次方程练习题"
```

**预期后端日志：**
```
✅ "✨ User preference detected: [User Preference: Strongly prefers quiz practice for learning (75% of recent activities)]"
```

#### 步骤2：测试模糊意图
```
输入："化学反应"
预期：
- ✅ 识别为 quiz_request（不是 explain_request）
- ✅ 生成练习题（默认5道）
```

```
输入："电磁学"
预期：
- ✅ 识别为 quiz_request
- ✅ 生成练习题
```

---

### 3.3 偏好动态切换测试

#### 测试目标
验证偏好系统能够根据用户最近行为动态更新。

#### 步骤1：建立Flashcard偏好（80%）
```
1-4. 连续4次使用闪卡（见3.1）
```

#### 步骤2：切换到Quiz（建立新偏好）
```
5. "给我几道微积分题"
6. "给我几道物理题"
7. "给我几道化学题"
8. "给我几道历史题"
9. "给我几道生物题"
10. "给我几道地理题"
```

**预期：**
```
✅ 最近10次中：flashcard=4次，quiz=6次
✅ quiz占比 = 6/10 = 60%
✅ 偏好切换为："Strongly prefers quiz practice for learning (60%)"
```

#### 步骤3：测试新偏好
```
输入："电磁学"
预期：
- ✅ 识别为 quiz_request（不再是 flashcard_request）
- ✅ 生成练习题
```

---

## 4️⃣ 意图识别测试

### 4.1 明确意图 vs 模糊意图

| 输入 | 意图类型 | 应识别为 | Confidence | 理由 |
|------|---------|---------|-----------|------|
| "解释一下导数" | 明确 | explain_request | 0.85-0.95 | 有明确"解释"关键词 |
| "我想要学习化学反应" | 明确 | explain_request | 0.85-0.90 | 有明确"学习"关键词 |
| "给我讲讲光合作用" | 明确 | explain_request | 0.85-0.90 | 有明确"讲"关键词 |
| "给我几道题" | 明确 | quiz_request | 0.90-0.95 | 有明确"题"关键词 |
| "化学反应" | 模糊 | 根据偏好 | 0.70-0.80 | 只有主题，无动词 |
| "电磁学" | 模糊 | 根据偏好 | 0.70-0.80 | 只有主题，无动词 |
| "帮我准备一下光合作用" | 模糊 | 根据偏好 | 0.70-0.75 | 动词不明确 |

### 4.2 测试步骤

#### 无偏好场景
```
步骤1：清空session（或使用新session）
步骤2：测试模糊意图
输入："化学反应"
预期：
- ✅ 默认识别为 explain_request（无偏好时的默认行为）
```

#### 有偏好场景
```
步骤1：建立quiz偏好（见3.2）
步骤2：测试相同的模糊意图
输入："化学反应"
预期：
- ✅ 识别为 quiz_request（偏好生效）
```

---

## 5️⃣ 边界情况测试

### 5.1 无主题输入

```
输入："你好"
预期：
- ✅ 识别为 other
- ✅ 不触发任何skill
- ✅ 返回友好提示
```

```
输入："帮我学习"
预期：
- ✅ 识别为 other（主题缺失）
- ✅ 提示用户指定学习主题
```

---

### 5.2 超大数量

```
输入："给我100道题"
预期：
- ✅ Quiz Skill返回错误："题目数量不合理"
- ✅ 建议生成 3-20 道题目
```

---

### 5.3 无效主题

```
输入："给我几道xyz的题"
预期：
- ✅ Gemini尝试理解主题
- ✅ 如果无法理解，返回友好错误
```

---

### 5.4 混合请求

```
输入："给我5道化学题和3张物理闪卡"
预期：
- ✅ Intent Router识别主要意图（quiz或flashcard）
- ✅ 或识别为 learning_bundle
- ✅ 系统处理复杂请求
```

---

## 6️⃣ 完整测试流程（推荐）

### 流程1：全功能快速测试（15分钟）

#### Phase 1：基础Skills测试（5分钟）
```
1. "给我几道微积分练习题" → Quiz Skill
2. "解释一下什么是导数" → Explain Skill
3. "给我一些光合作用的闪卡" → Flashcard Skill
4. "帮我准备电磁学的完整学习资料" → Learning Bundle Skill
```

#### Phase 2：数量控制测试（3分钟）
```
5. "给我3道二元一次方程练习题" → 恰好3道题
6. "给我2张牛顿定律的闪卡" → 恰好2张卡
```

#### Phase 3：偏好系统测试（7分钟）
```
7. "给我2道历史题" → 建立quiz偏好
8. "给我2道化学题"
9. "给我2道物理题"
10. "化学反应" → 应触发quiz（偏好生效）
11. "我想要学习化学反应" → 应触发explain（明确意图）
```

---

### 流程2：偏好系统深度测试（20分钟）

#### Phase 1：建立Flashcard偏好（5分钟）
```
1-4. 连续使用闪卡（见3.1）
检查：后端日志显示 "80% flashcards"
```

#### Phase 2：测试Flashcard偏好（5分钟）
```
5. "电磁学" → flashcard_request ✅
6. "光合作用" → flashcard_request ✅
7. "我想要学习电磁学" → explain_request ✅
```

#### Phase 3：切换到Quiz偏好（5分钟）
```
8-13. 连续使用quiz（见3.3）
检查：后端日志显示偏好切换为 "60% quiz"
```

#### Phase 4：测试Quiz偏好（5分钟）
```
14. "化学反应" → quiz_request ✅
15. "电磁学" → quiz_request ✅
16. "解释一下化学反应" → explain_request ✅
```

---

## 7️⃣ 验证清单

### 后端日志检查

#### Intent Router日志
```
✅ "🔍 Parsing intent for message: ..."
✅ "✅ Intent parsed: {intent} (confidence: X.XX, topic: {topic})"
✅ "📊 Extracted quantity parameter: X"（当有数量时）
✅ "✨ User preference detected: [User Preference: ...]"（当有偏好时）
```

#### Skill Orchestrator日志
```
✅ "🎯 Orchestrating: intent={intent}, topic={topic}"
✅ "📦 Selected skill: {skill_id} ({skill_name})"
✅ "📊 Extracted quantity: X for {skill_id}"
✅ "✅ Orchestration complete for {skill_id}"
```

#### Memory Manager日志
```
✅ "📊 Generated memory summary: recent_behavior='...'"
✅ "✨ User preference detected: [User Preference: ...]"
✅ "✅ Updated session context for demo-session"
```

---

### 前端UI检查

#### Quiz Card
```
✅ 题目编号显示正确（1/5, 2/5, ...）
✅ 选项可以选择
✅ 提交后显示正确/错误状态
✅ 解析部分正确显示
✅ 进度条工作正常
```

#### Explain Card
```
✅ 概念名称清晰显示
✅ 直观理解部分显示
✅ 正式定义部分显示
✅ 例子部分不为空，每个例子有序号
✅ 公式正确渲染（如有）
```

#### Flashcard Card
```
✅ 闪卡可以翻转查看答案
✅ 提示部分正确显示
✅ 导航按钮工作正常（上一张、下一张）
```

#### Learning Bundle
```
✅ 各个组件正确渲染
✅ 组件之间有明确分隔
✅ 每个组件可以独立交互
```

---

## 8️⃣ 常见问题排查

### 问题1：偏好系统不生效

**症状：** 用户有80%偏好，但模糊意图仍识别为默认explain

**排查步骤：**
1. 检查后端日志是否有 "✨ User preference detected"
2. 检查 memory_summary 是否包含偏好信息
3. 检查用户输入是否真的模糊（无明确关键词）
4. 重启后端确保prompt已更新

**解决方法：**
- 确保 `intent_router.txt` 包含偏好处理指令
- 确保 Memory Manager 正确生成偏好提示

---

### 问题2：数量控制不准确

**症状：** 请求3道题，生成了5道

**排查步骤：**
1. 检查后端日志是否有 "📊 Extracted quantity parameter: X"
2. 检查后端日志是否有 "📊 Extracted quantity: X for quiz_skill"
3. 检查 IntentResult 是否有 parameters 字段

**解决方法：**
- 确保 `intent_router.txt` 包含 quantity 提取示例
- 确保 `IntentResult` 模型有 `parameters` 字段
- 确保 Skill Orchestrator 正确提取和传递 quantity

---

### 问题3：Learning Bundle报错

**症状：** `NameError: name 'datetime' is not defined`

**排查步骤：**
1. 检查 `skill_orchestrator.py` 是否导入 datetime

**解决方法：**
```python
from datetime import datetime
```

---

## 9️⃣ 性能基准

### 响应时间（参考值）

| 操作 | 预期响应时间 | 备注 |
|------|------------|------|
| Intent Router | 1-2s | Gemini API调用 |
| Quiz Generation | 8-12s | 生成5道题 |
| Explain | 6-8s | 生成讲解 |
| Flashcard | 5-8s | 生成5张卡 |
| Learning Bundle | 14-20s | 综合多个组件 |

---

## 🎯 总结

### 必测功能（优先级P0）
- ✅ 各个Skill基础功能
- ✅ 数量控制（指定数量 vs 默认数量）
- ✅ 偏好系统（模糊意图+偏好生效）
- ✅ 明确意图不被偏好覆盖

### 建议测试（优先级P1）
- ✅ 偏好动态切换
- ✅ 不同学科支持
- ✅ 边界情况处理

### 可选测试（优先级P2）
- ✅ 性能测试
- ✅ 并发测试
- ✅ 复杂场景测试

---
