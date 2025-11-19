# Skill Agent - 测试指南

本文档提供完整的测试方案、调试技巧和问题排查方法。

---

## 📋 目录

- [快速测试](#快速测试)
- [Phase 3 架构测试](#phase-3-架构测试)
- [澄清机制测试](#澄清机制测试)
- [功能测试清单](#功能测试清单)
- [调试技巧](#调试技巧)
- [常见问题](#常见问题)

---

## 1. 快速测试

### 1.1 环境检查

```bash
# 检查Python版本
python3 --version  # 需要 3.11+

# 检查Node版本
node --version     # 需要 18+

# 检查依赖安装
cd backend && pip list | grep -E "fastapi|uvicorn|google-generativeai"
cd frontend && npm list mind-elixir
```

### 1.2 启动服务

```bash
# 终端1: 后端
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 终端2: 前端  
cd frontend
python3 -m http.server 3000

# 终端3: 日志监控
cd backend
tail -f log/token_cost_optimized.log
```

### 1.3 基础功能测试

访问 `http://localhost:3000/public/demo.html`

```
测试1: 题目生成
👤: 给我5道二战历史的题
✅ 期望: 生成5道选择题

测试2: 概念讲解
👤: 解释一下珍珠港事件
✅ 期望: 生成结构化解释

测试3: 闪卡生成
👤: 给我10张闪卡
✅ 期望: 生成10张记忆卡片
```

---

## 2. Phase 3 架构测试

### 2.1 规则引擎测试（0 Token）

**目标**: 验证规则引擎对明确请求的识别

```
测试1: 明确请求（带主题+数量）
👤: 给我5道二战历史的题
✅ 规则引擎命中 (0 tokens, <0.01s)
✅ Intent: quiz_request
✅ Topic: "二战历史"
✅ Quantity: 5

测试2: 明确请求（带主题）
👤: 解释光合作用
✅ 规则引擎命中 (0 tokens)
✅ Intent: explain_request
✅ Topic: "光合作用"

测试3: 无主题请求（触发澄清）
👤: 出题目
✅ 规则引擎命中 (0 tokens)
✅ Intent: quiz_request
✅ Topic: None → 触发 Clarification
```

### 2.2 多轮对话测试

**目标**: 验证上下文引用、topic 继承、token 优化

```
1️⃣ 给我5道二战历史的题
   ✅ 规则引擎 (0 tokens)
   ✅ 生成5道题
   ✅ Memory: current_topic = "二战历史"
   ✅ Memory: last_artifact_content = {questions: [...]}

2️⃣ 解释一下第一道题
   ✅ 规则引擎 (0 tokens)
   ✅ Context reference detected: '第一道'
   ✅ Topic fallback: "二战历史的"
   ✅ Extracted question #1
   ✅ 生成针对第1题的解释

3️⃣ 根据这道题再出3道类似的
   ✅ LLM fallback (~1,500 tokens) - 复杂语义
   ✅ use_last_artifact = True
   ✅ 基于第1题内容生成3道新题

4️⃣ 学习一下珍珠港事件
   ✅ 规则引擎 (0 tokens)
   ✅ Memory: current_topic = "珍珠港事件"
   ✅ 生成珍珠港事件解释

5️⃣ 给我10张闪卡
   ✅ 规则引擎 (0 tokens)
   ✅ Ambiguous intent → 根据用户偏好选择
   ✅ Topic继承: "珍珠港事件"
   ✅ 生成10张珍珠港相关闪卡

6️⃣ 做笔记
   ✅ 规则引擎 (0 tokens)
   ✅ Topic继承: "珍珠港事件"
   ✅ 生成结构化笔记

7️⃣ 给我思维导图
   ✅ 规则引擎 (0 tokens)
   ✅ Topic继承: "珍珠港事件"
   ✅ 生成思维导图

8️⃣ 根据这些笔记再出5道题
   ✅ LLM fallback (~1,500 tokens)
   ✅ 基于笔记内容生成题目

9️⃣ 这次太难了，简单点
   ✅ LLM fallback (~1,500 tokens) - 对话
   ✅ 友好回应并引导

🔟 给我5道基础题
   ✅ 规则引擎 (0 tokens)
   ✅ Topic继承 + 难度调整
   ✅ 生成基础难度题目
```

### 2.2 预期Token消耗

| 轮次 | Intent Router | Skill Execution | 总计 |
|------|--------------|----------------|------|
| 1 | 0 | ~7,000 | 7,000 |
| 2 | 0 | ~6,200 | 6,200 |
| 3 | ~1,500 | ~6,500 | 8,000 |
| 4 | 0 | ~5,500 | 5,500 |
| 5 | 0 | ~6,000 | 6,000 |
| 6 | 0 | ~5,800 | 5,800 |
| 7 | 0 | ~6,200 | 6,200 |
| 8 | ~1,500 | ~6,500 | 8,000 |
| 9 | ~1,500 | ~1,000 | 2,500 |
| 10 | 0 | ~7,000 | 7,000 |
| **总计** | **~4,500** | **~58,000** | **~62,500** |

**平均**: 6,250 tokens/轮

**对比 Phase 1**: 31,320 tokens (Intent Router) → 节省 **86%** ✅

---

## 3. 澄清机制测试

### 3.1 Onboarding 测试（首次访问）

**目标**: 验证首次访问时的引导体验（0 Token）

```
前置条件:
- 清空 session: rm backend/memory_storage/session_demo-session.json
- 或使用浏览器隐身模式

测试序列:
1️⃣ 出题目
   ✅ Intent: quiz_request
   ✅ Topic: None
   ✅ artifact_history: [] (空)
   ✅ 触发 Onboarding (0 tokens)
   
   期望响应:
   👋 欢迎使用 StudyX Agent！
   我注意到您还没有开始学习任何主题。
   
   [5大类推荐主题卡片]
   - 物理: [牛顿定律] [光学] [电磁学] ...
   - 数学: [微积分] [线性代数] ...
   - 历史: [二战历史] [文艺复兴] ...
   - 生物: [光合作用] [细胞结构] ...
   - 计算机: [数据结构] [算法] ...

2️⃣ 点击任意推荐主题（如"牛顿定律"）
   ✅ 自动填充: "讲讲牛顿定律"
   ✅ 发送并生成内容

3️⃣ 再次说"出题目"
   ✅ 不再显示 Onboarding
   ✅ 触发 Clarification（有历史主题）
```

### 3.2 Multi-Topic Clarification 测试

**目标**: 验证多主题时的澄清机制（0 Token）

```
前置条件:
- 已学习过至少 1 个主题

测试序列 1: 单主题场景
1️⃣ 讲讲机器学习
   ✅ 生成内容
   ✅ Memory: artifact_history += {topic: "机器学习", ...}

2️⃣ 做笔记
   ✅ Intent: notes, Topic: None
   ✅ len(learned_topics) = 1 (去重后)
   ✅ 触发 Clarification (0 tokens)
   
   期望响应:
   您想对哪个主题做笔记呢？
   [机器学习]
   
   请告诉我您想选择的主题，例如：「做机器学习的笔记」

3️⃣ 点击 [机器学习]
   ✅ 自动填充: "做机器学习的笔记"
   ✅ 发送并生成笔记

测试序列 2: 多主题场景
1️⃣ 讲讲牛顿定律
   ✅ 生成内容

2️⃣ 讲讲光合作用
   ✅ 生成内容

3️⃣ 出题目
   ✅ Intent: quiz_request, Topic: None
   ✅ len(learned_topics) = 3 (机器学习、牛顿定律、光合作用)
   ✅ 触发 Clarification (0 tokens)
   
   期望响应:
   您想对哪个主题生成题目呢？
   [机器学习] [牛顿定律] [光合作用]
   
   (最多显示5个主题，按最新顺序)

4️⃣ 点击 [光合作用]
   ✅ 自动填充: "生成光合作用的题目"
   ✅ 生成题目
```

### 3.3 Topic 提取测试

**目标**: 验证 Topic 提取的准确性

```
测试1: 保留有意义的数字
👤: 做牛顿第二定律的笔记
✅ Topic: "牛顿第二定律" (不是 "牛顿第定律" ❌)

测试2: 移除动词和助词
👤: 给我光合作用的闪卡
✅ Topic: "光合作用" (不是 "光合作用的" ❌)

测试3: 无明确主题
👤: 出题目
✅ Topic: None (不是 "出 目" ❌)
✅ 触发 Clarification

测试4: 保留"二战"等含数字的名词
👤: 讲讲二战历史
✅ Topic: "二战历史" (不是 "战历史" ❌)
```

### 3.4 验证方法

**查看 Intent Router 输出**:
```bash
cat backend/memory_storage/intent_router_output.json | jq .latest
```

期望输出:
```json
{
  "user_message": "做牛顿第二定律的笔记",
  "method": "rule_engine",
  "tokens_used": 0,
  "results": [{
    "intent": "notes",
    "topic": "牛顿第二定律",  ← ✅ 正确
    "confidence": 0.95
  }]
}
```

---

## 4. 功能测试清单

### 3.1 核心技能测试

```markdown
## Quiz Skill
- [ ] 生成5道题（默认）
- [ ] 生成10道题（自定义数量）
- [ ] 基于内容生成题目（source_content）
- [ ] 难度调整（easy/medium/hard）
- [ ] 各种题型（选择/填空/判断）

## Explain Skill  
- [ ] 概念讲解
- [ ] 基于题目的针对性解释
- [ ] 包含示例
- [ ] 包含常见误解

## Flashcard Skill
- [ ] 生成10张闪卡
- [ ] 自定义数量（1-20）
- [ ] Topic继承
- [ ] 难度分级

## Notes Skill
- [ ] 生成结构化笔记
- [ ] Notebook UI渲染
- [ ] 编辑功能
- [ ] 添加/删除要点

## MindMap Skill
- [ ] 生成思维导图
- [ ] Mind Elixir渲染
- [ ] 交互式展开/折叠

## Learning Bundle
- [ ] 生成综合学习包
- [ ] 包含多种材料
- [ ] 混合响应渲染
```

### 3.2 智能Agent测试

```markdown
## Intent Recognition
- [ ] 规则引擎命中（显式请求）
- [ ] LLM fallback（复杂语义）
- [ ] 上下文引用检测
- [ ] 多意图并行识别

## Memory Management
- [ ] current_topic 记录
- [ ] last_artifact_content 保存
- [ ] 用户偏好学习
- [ ] 本地文件持久化

## Context Reference
- [ ] "解释一下第一道题" → 提取第1题
- [ ] "根据这些例子出题" → 使用examples
- [ ] Topic继承
- [ ] Topic fallback

## Personalization
- [ ] 模糊意图 → 根据偏好选择
- [ ] 偏好权重计算
- [ ] 历史行为统计
```

---

## 4. 调试技巧

### 4.1 查看后端日志

```bash
# 实时查看所有日志
tail -f backend/log/token_cost_optimized.log

# 过滤特定信息
tail -f backend/log/token_cost_optimized.log | grep -E "(Rule-based|Token Usage|Context reference)"

# 查看最近100行
tail -n 100 backend/log/token_cost_optimized.log

# 搜索特定关键词
grep "Topic fallback" backend/log/token_cost_optimized.log
```

### 4.2 查看Memory文件

```bash
# 查看 Session Context（含 artifact_history）
cat backend/memory_storage/session_demo-session.json | jq .
cat backend/memory_storage/session_demo-session.json | jq '.current_topic'
cat backend/memory_storage/session_demo-session.json | jq '.artifact_history | length'

# 🆕 查看 Intent Router 实时输出（Phase 3 新增）
cat backend/memory_storage/intent_router_output.json | jq .latest
cat backend/memory_storage/intent_router_output.json | jq .stats

# 查看用户画像
cat backend/memory_storage/profile_demo-user.json | jq .

# 实时监控 Intent Router
watch -n 1 'cat backend/memory_storage/intent_router_output.json | jq ".latest | {method, tokens_used, intent: .results[0].intent, topic: .results[0].topic}"'
```

**Memory 文件说明**:

| 文件 | 用途 | 关键字段 |
|------|------|---------|
| `session_demo-session.json` | 会话上下文 | `current_topic`, `artifact_history`, `last_artifact_id` |
| `profile_demo-user.json` | 用户画像 | `preferences`, `mastery_levels` |
| `intent_router_output.json` 🆕 | Intent Router 输出 | `latest`, `history`, `stats` |

**intent_router_output.json 结构**:
```json
{
  "latest": {
    "user_message": "给我5道题",
    "method": "rule_engine",        ← 识别方法
    "tokens_used": 0,                ← Token 消耗
    "results": [{
      "intent": "quiz_request",
      "topic": null,
      "confidence": 0.95
    }]
  },
  "stats": {
    "total_requests": 10,
    "rule_based_success": 7,         ← 规则引擎命中数
    "llm_fallback": 3,               ← LLM fallback 数
    "rule_success_rate": "70.0%"     ← 命中率
  }
}
```

### 4.3 浏览器调试

**打开开发者工具** (F12)

```javascript
// 控制台日志
📤 Sending message: xxx
🌐 API Base: http://localhost:8000
📥 Response status: 200
✅ Response data: {...}

// 网络请求
- 查看 Network 标签
- 筛选 XHR 请求
- 检查 Request/Response

// 错误调试
- 查看 Console 错误
- 检查 Sources 断点
```

### 4.4 API测试

```bash
# 使用curl测试API
curl -X POST http://localhost:8000/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "session_id": "test-session",
    "message": "给我5道数学题"
  }' | python3 -m json.tool

# 健康检查
curl http://localhost:8000/api/agent/health

# 查看API文档
open http://localhost:8000/docs
```

---

## 5. 常见问题

### 5.1 后端问题

#### 问题1: 端口已被占用

```bash
Error: Address already in use

# 解决方案1: 查找并杀死进程
lsof -i :8000
kill -9 <PID>

# 解决方案2: 使用不同端口
python3 -m uvicorn app.main:app --port 8001
```

#### 问题2: Gemini API连接失败

```
ConnectionError: Failed to resolve 'generativelanguage.googleapis.com'

# 原因:
- 网络断开
- 防火墙阻止
- DNS解析失败

# 解决方案:
1. 检查网络连接: ping google.com
2. 检查API Key: cat backend/.env
3. 测试DNS: nslookup generativelanguage.googleapis.com
4. 使用VPN（如需要）
```

#### 问题3: Memory文件未生成

```bash
# 检查目录是否存在
ls -la backend/memory_storage/

# 检查权限
chmod 755 backend/memory_storage/

# 检查日志
grep "Saved.*to" backend/log/token_cost_optimized.log
```

#### 问题4: 规则引擎未命中

```bash
# 查看日志
grep "Rule-based classification" backend/log/token_cost_optimized.log

# 期望看到:
✅ 🎯 Rule-based classification: xxx

# 如果看到:
⚠️  Rule-based classification failed
→ 说明消息不匹配规则，会fallback到LLM
```

---

### 5.2 前端问题

#### 问题1: 页面加载失败

```bash
Error: Failed to fetch

# 原因: 后端未启动或端口不对

# 解决方案:
1. 确认后端运行: curl http://localhost:8000/api/agent/health
2. 检查API_BASE: 打开demo.html，搜索 "API_BASE"
3. 检查CORS: 查看浏览器Console错误
```

#### 问题2: Mind Elixir加载失败

```
Failed to resolve module specifier "mind-elixir"

# 解决方案:
1. 确认使用IIFE版本: MindElixir.iife.js
2. 检查文件路径: /node_modules/mind-elixir/dist/
3. 重新安装: cd frontend && npm install mind-elixir
```

#### 问题3: WebSocket断开

```bash
# 查看Network标签的WS连接
# 确认后端支持WebSocket

# 当前: WebSocket未完全实现
# 临时方案: 使用HTTP轮询
```

---

### 5.3 Memory问题

#### 问题1: 上下文丢失

```bash
# 症状: "解释一下第一道题" 返回错误

# 检查步骤:
1. 查看session文件: cat backend/memory_storage/session_demo-session.json
2. 确认 last_artifact_content 存在
3. 确认 questions 数组不为空
4. 查看日志: grep "Extracted question" backend/log/*.log

# 常见原因:
- 刷新了浏览器页面 → session重置
- 后端重启（--reload模式）→ 内存清空
- session_id 不一致 → 查看demo.html中的SESSION_ID

# 解决方案:
- 不要刷新页面
- 连续发送消息
- 确认session_id固定为 "demo-session"
```

#### 问题2: Topic未继承

```bash
# 症状: "给我10张闪卡" 生成通用内容而非当前主题

# 检查:
cat backend/memory_storage/session_demo-session.json | jq '.current_topic'

# 应该看到: "二战历史的" 或当前学习主题

# 如果为null:
→ 上一轮请求可能失败
→ topic未正确设置
→ 查看日志: grep "current_topic" backend/log/*.log
```

---

## 6. 性能测试

### 6.1 Token消耗测试

```bash
# 测试序列
1. 给我5道题
2. 解释一下第一道题
3. 给我10张闪卡

# 统计token
grep "📊 Token Usage" backend/log/token_cost_optimized.log | tail -10

# 预期结果:
第1轮 Intent Router: 0 tokens
第2轮 Intent Router: 0 tokens  
第3轮 Intent Router: 0 tokens

# 如果不是0:
→ 规则引擎未命中
→ 检查关键词匹配
→ 查看 "Rule-based classification failed"
```

### 6.2 响应时间测试

```bash
# 使用curl测试
time curl -X POST http://localhost:8000/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "session_id": "test", "message": "给我5道题"}'

# 预期:
Intent Router: <0.01s
Skill Execution: 5-15s (取决于LLM)
Total: 5-15s
```

### 6.3 压力测试

```bash
# 使用ab (Apache Bench)
ab -n 100 -c 10 -p request.json -T application/json \
  http://localhost:8000/api/agent/chat

# request.json:
{
  "user_id": "stress-test",
  "session_id": "stress-test",
  "message": "给我5道题"
}

# 监控:
- 并发处理能力
- 平均响应时间
- 错误率
```

---

## 7. 高级调试

### 7.1 Python调试器

```python
# 在代码中添加断点
import pdb; pdb.set_trace()

# 或使用ipdb
import ipdb; ipdb.set_trace()

# 运行时:
(Pdb) p intent_result  # 打印变量
(Pdb) n               # 下一行
(Pdb) s               # 进入函数
(Pdb) c               # 继续执行
```

### 7.2 日志级别调整

```python
# backend/app/main.py
import logging

# 设置为DEBUG查看详细日志
logging.basicConfig(level=logging.DEBUG)

# 只调试特定模块
logging.getLogger("app.core.intent_router").setLevel(logging.DEBUG)
```

### 7.3 Prompt调试

```bash
# 查看完整prompt
# 在 skill_orchestrator.py 的 _format_prompt 添加日志

logger.debug(f"Full prompt:\n{formatted_prompt}")

# 或在Gemini调用前打印
# backend/app/services/gemini.py
logger.info(f"Prompt length: {len(prompt)} chars")
```

---

## 8. 测试最佳实践

### 8.1 测试前准备

```bash
# 1. 清理旧日志
rm backend/log/*.log

# 2. 清理memory文件
rm backend/memory_storage/*.json

# 3. 重启后端
cd backend && python3 -m uvicorn app.main:app --reload

# 4. 打开3个终端窗口:
#    - 终端1: 后端运行
#    - 终端2: 日志监控
#    - 终端3: memory监控
```

### 8.2 测试中注意事项

1. **不要刷新浏览器** - 会导致session重置
2. **连续发送消息** - 避免后端自动重启
3. **观察日志** - 确认每一步都正确执行
4. **记录token** - 统计实际消耗

### 8.3 测试后验证

```bash
# 1. 检查memory文件
ls -lh backend/memory_storage/

# 2. 统计token消耗
grep "📊 Token Usage" backend/log/*.log | awk '{sum+=$9} END {print "Total:", sum}'

# 3. 统计规则引擎命中率
total=$(grep "Rule-based classification" backend/log/*.log | wc -l)
success=$(grep "Rule-based classification" backend/log/*.log | grep -v "failed" | wc -l)
echo "Success rate: $((success * 100 / total))%"
```

---

## 📞 获取帮助

### 问题反馈

- **GitHub Issues**: https://github.com/StudyXTeam23/SkillAgent/issues
- **Email**: studyx@example.com

### 提供信息

报告问题时请附上:
1. 错误日志（`backend/log/*.log`）
2. Memory文件（`backend/memory_storage/*.json`）
3. 复现步骤
4. 环境信息（Python/Node版本）

---

<div align="center">
  📚 更多信息请参考 <a href="README.md">README.md</a> 和 <a href="FEATURES.md">FEATURES.md</a>
</div>

