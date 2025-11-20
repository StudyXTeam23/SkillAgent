# Skill Agent - 测试指南

快速测试 Phase 3 架构和澄清机制的核心功能。

---

## 1. 快速开始（5分钟）

### 启动服务

```bash
# 终端1: 后端
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 终端2: 前端  
cd frontend
python3 -m http.server 3000
```

访问: `http://localhost:3000/public/demo.html`

### 基础测试

```
1. 给我5道二战历史的题   → ✅ 生成5道选择题
2. 解释一下珍珠港事件     → ✅ 生成结构化解释
3. 给我10张闪卡          → ✅ 生成10张记忆卡片
```

---

## 2. Phase 3 架构测试（10分钟）

### 规则引擎测试（0 Token）

```
测试1: 给我5道二战历史的题
✅ 规则引擎命中 (0 tokens, <0.01s)
✅ Intent: quiz_request, Topic: "二战历史", Quantity: 5

测试2: 出题目
✅ 规则引擎命中 (0 tokens)
✅ Intent: quiz_request, Topic: None
✅ 触发 Clarification 卡片
```

### 多轮对话测试

```
1️⃣ 给我5道二战历史的题      → 规则引擎 (0 tokens)
2️⃣ 解释一下第一道题          → 规则引擎 (0 tokens)
3️⃣ 根据这道题再出3道类似的   → LLM fallback (~1,500 tokens)
4️⃣ 学习一下珍珠港事件        → LLM fallback (~1,500 tokens)
5️⃣ 给我10张闪卡              → 规则引擎 (0 tokens)

平均 Token/轮: ~450 (vs Phase 1: 3,132) → 节省 85.6% ✅
```

---

## 3. 澄清机制测试（15分钟）

### Onboarding 测试（首次访问）

```bash
# 清空 session
rm backend/memory_storage/session_demo-session.json

# 测试
输入: "出题目"
✅ 显示 Onboarding 卡片
✅ 5大类推荐主题（物理、数学、历史、生物、计算机）
✅ 点击任意主题 → 自动填充消息并发送
```

### Multi-Topic Clarification 测试

```
步骤1: 讲讲机器学习       → 生成内容
步骤2: 做笔记              → ✅ 触发 Clarification
       "您想对哪个主题做笔记呢？"
       [机器学习]
步骤3: 点击 [机器学习]     → 自动填充并生成笔记
```

### Topic 提取测试

```
测试1: 做牛顿第二定律的笔记
✅ Topic: "牛顿第二定律" (不是 "做牛顿第二定律的" ❌)

测试2: 给我光合作用的闪卡
✅ Topic: "光合作用" (不是 "光合作用的" ❌)

测试3: 出题目
✅ Topic: None → 触发 Clarification
```

---

## 4. 调试技巧

### 查看后端日志

```bash
# 实时查看
tail -f backend/log/token_cost_optimized.log

# 过滤 Intent Router
tail -f backend/log/token_cost_optimized.log | grep -E "Rule-based|Token Usage"
```

### 查看 Memory 文件

```bash
# Session Context
cat backend/memory_storage/session_demo-session.json | jq .current_topic
cat backend/memory_storage/session_demo-session.json | jq '.artifact_history | length'

# Intent Router 输出（Phase 3）
cat backend/memory_storage/intent_router_output.json | jq .latest
cat backend/memory_storage/intent_router_output.json | jq .stats

# 实时监控 Intent Router
watch -n 1 'cat backend/memory_storage/intent_router_output.json | jq ".latest | {method, tokens_used}"'
```

### 浏览器调试

按 `F12` 打开开发者工具，查看：
- **Console**: 查看前端日志（📤 Sending message, 📥 Response status）
- **Network**: 查看 API 请求和响应
- **Application**: 查看 localStorage

---

## 5. 常见问题

### 后端问题

**端口被占用**:
```bash
# 查找占用端口的进程
lsof -i :8000
# 杀死进程
kill -9 <PID>
```

**Gemini API 连接失败**:
```bash
# 检查 API Key
echo $GEMINI_API_KEY
# 或检查 .env 文件
cat backend/.env | grep GEMINI_API_KEY
```

**规则引擎未命中**:
```bash
# 查看 Intent Router 输出
cat backend/memory_storage/intent_router_output.json | jq '.latest.method'
# 如果是 "llm_fallback"，检查用户输入是否明确
```

### 前端问题

**页面加载失败**:
- 检查前端服务是否启动: `lsof -i :3000`
- 确认访问 `http://localhost:3000/public/demo.html` (不是 `/demo.html`)

**Clarification 按钮不工作**:
- 打开浏览器控制台检查错误
- 确认 `messageInput` 元素存在
- 检查 `selectTopic` 函数是否正确定义

### Memory 问题

**上下文丢失**:
- **原因**: 后端重启（`uvicorn --reload`）
- **解决**: 测试时不要修改代码，或使用生产模式启动

**Topic 未继承**:
```bash
# 检查 current_topic
cat backend/memory_storage/session_demo-session.json | jq .current_topic
# 如果为空，检查规则引擎的 topic 提取逻辑
```

---

## 6. 性能验证

### Token 消耗

```bash
# 查看 Intent Router 统计
cat backend/memory_storage/intent_router_output.json | jq .stats

# 期望结果:
# - rule_success_rate >= 70%
# - total_requests > 0
# - llm_fallback < 30%
```

### 响应时间

- 规则引擎命中: **<0.01s** ✅
- LLM Fallback: **~1.6s** ✅
- Skill Execution: **~5-10s** (取决于 LLM)

---

## 7. 流式输出测试（Phase 4.5）

### 后端验证

**检查 LLM Client 选择**:
```bash
# 启动后端，观察日志
cd backend
python3 -m uvicorn app.main:app --reload

# 期望看到：
# ✅ Kimi client initialized via Novita AI
# 📍 Base URL: https://api.novita.ai/openai
# 🤖 Model: moonshotai/kimi-k2-thinking
# ✅ Using Kimi Client for LLM operations
```

### 前端流式验证

**测试步骤**:
```
1. 打开浏览器开发者工具（F12）
2. 切换到 Console 标签
3. 输入: "什么是光合作用"
4. 观察日志输出
```

**期望结果**:
```javascript
// ✅ 应该看到多个流式 chunks
[Stream] status {type: 'status', message: '正在分析您的请求...'}
[Stream] status {type: 'status', message: '开始explain_request...'}
[Stream] thinking {type: 'thinking', text: 'The user wants...', ...}
[Stream] thinking {type: 'thinking', text: 'Let me analyze...', ...}
[Stream] content {type: 'content', text: '{\n  "concept":', ...}
[Stream] content {type: 'content', text: ' "光合作用"', ...}
[Stream] done {type: 'done', ...}

// ✅ 应该看到多个 overview 变化
[DEBUG] Overview #1: 正在理解问题...
[DEBUG] Overview #2: 评估为基础概念，准备清晰讲解
[DEBUG] Overview #3: 计划侧重直觉理解
[DEBUG] Overview #4: 正在设计具体示例
[DEBUG] Overview #5: 正在组织内容结构
[DEBUG] Overview #6: 正在完善细节...
[DEBUG] Overview #7: ⏳ 准备生成内容...
```

**失败诊断**:
```javascript
// ❌ 如果只看到：
[Stream] status {...}
[Stream] done {...}

// 可能的问题：
// 1. 后端未使用 Kimi Client（检查启动日志）
// 2. 前端缓存（Ctrl+Shift+R 强制刷新）
// 3. API 配置错误（检查 config.py）
```

### Network 面板验证

```
1. 打开开发者工具 → Network 标签
2. 输入测试消息
3. 找到 /api/agent/chat-stream 请求
4. 查看响应（应该是持续的数据流）
```

**期望**:
- ✅ Type: `text/event-stream`
- ✅ 持续接收数据（不是一次性返回）
- ✅ 每个数据块以 `data: ` 开头

### Thinking Overview 质量测试

```bash
# 查看调试数据
cat backend/memory_storage/thinking_overview_debug.json | jq '.samples[-1]'

# 检查字段：
# - all_overviews: 应该有 5+ 个不同的阶段
# - overview_changes_count: 应该 >= 5
# - full_thinking: 完整思考过程（2000+ 字符）
```

---

## 8. 性能基准测试

### 流式延迟测试

```bash
# 测试首字节时间（TTFB）
curl -w "@curl-format.txt" -o /dev/null -s \
  -X POST http://localhost:8000/api/agent/chat-stream \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","session_id":"test","message":"什么是光合作用"}'

# 期望：
# time_connect: < 0.5s
# time_starttransfer: < 1.0s  ← TTFB
```

### Token 消耗验证

```bash
# Phase 4.5 应该保持 Phase 4 的 token 效率
cat backend/memory_storage/intent_router_output.json | jq '.stats'

# 期望：
# - rule_success_rate: >= 70%
# - avg_tokens_per_request: <= 500
```

---

## 🎯 完整测试清单

```
快速测试（5分钟）
  ✅ 环境检查
  ✅ 启动服务
  ✅ 3个基础功能测试

Phase 3 架构（10分钟）
  ✅ 规则引擎测试（0 Token）
  ✅ 多轮对话测试（5轮）
  ✅ Token 节省验证

澄清机制（15分钟）
  ✅ Onboarding 测试
  ✅ Clarification 测试
  ✅ Topic 提取测试

流式输出（10分钟）- Phase 4.5 🆕
  ✅ 后端 LLM Client 验证
  ✅ 前端 Console 流式日志检查
  ✅ Network 面板数据流验证
  ✅ Thinking Overview 质量检查（5+ 阶段）
  ✅ 性能基准测试

调试验证（5分钟）
  ✅ 查看 Intent Router 输出
  ✅ 验证规则命中率 >= 70%
```

**总时间**: ~45分钟

---

## 🐛 故障排除

### 流式输出相关问题

**问题：前端没有收到流式 chunks**

解决步骤：
```bash
# 1. 检查后端使用的 Client
cd backend
python3 -m uvicorn app.main:app --reload | grep "Using"
# 应该看到：✅ Using Kimi Client

# 2. 检查 API 配置
cat backend/app/config.py | grep "KIMI"
# 确认 KIMI_API_KEY 和 KIMI_MODEL 已设置

# 3. 清除前端缓存
# 浏览器：Ctrl+Shift+R（强制刷新）

# 4. 检查 Network 请求
# 开发者工具 → Network → 查看 /chat-stream 请求
# 确认 Content-Type: text/event-stream
```

**问题：Overview 只有 3 个阶段**

解决步骤：
```bash
# 1. 确认前端代码已更新
grep "fullText.length % 80" frontend/public/demo.html
# 应该看到：const shouldUpdate = fullText.length % 80 < 5

# 2. 清除浏览器缓存
# Ctrl+Shift+R 强制刷新

# 3. 查看 thinking 长度
cat backend/memory_storage/thinking_overview_debug.json | jq '.samples[-1].thinking_length'
# 应该 > 2000 字符
```

**问题：后端报错 "Kimi client not found"**

解决步骤：
```bash
# 检查 kimi.py 是否存在
ls backend/app/services/kimi.py

# 检查导入
grep "from.*kimi import" backend/app/core/skill_orchestrator.py

# 重启后端
cd backend
python3 -m uvicorn app.main:app --reload
```

---

更多详细信息请参考:
- [FEATURES.md](FEATURES.md) - 功能详解（包含 Phase 4.5 修复说明）
- [README.md](README.md) - 快速开始
- [STREAMING_FIX_GUIDE.md](STREAMING_FIX_GUIDE.md) - 流式修复完整指南（如需创建）
