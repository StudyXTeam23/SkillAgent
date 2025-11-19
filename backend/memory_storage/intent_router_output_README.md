# 🎯 Intent Router 实时输出说明

## 📁 文件位置

```
backend/memory_storage/intent_router_output.json
```

## 📊 文件结构

```json
{
  "description": "Intent Router 实时输出记录 (Phase 3 架构)",
  "latest": {
    "timestamp": "2024-11-18T18:30:45.123456",
    "user_message": "给我5道牛顿第二定律的题",
    "method": "rule_engine",
    "tokens_used": 0,
    "results": [
      {
        "intent": "quiz_request",
        "topic": "牛顿第二定律",
        "confidence": 0.95,
        "parameters": {
          "quantity": 5,
          "context_type": "clear"
        }
      }
    ]
  },
  "history": [
    // 最近10条请求历史
  ],
  "stats": {
    "total_requests": 15,
    "rule_based_success": 12,
    "llm_fallback": 3,
    "rule_success_rate": "80.0%"
  }
}
```

## 🔍 字段说明

### latest (最新一次请求)

| 字段 | 类型 | 说明 |
|------|------|------|
| `timestamp` | string | ISO 格式时间戳 |
| `user_message` | string | 用户输入的原始消息 |
| `method` | string | 识别方法: `"rule_engine"` 或 `"llm_fallback"` |
| `tokens_used` | number | Token 消耗量 (规则引擎为 0) |
| `results` | array | Intent 识别结果列表 |

### results (识别结果)

| 字段 | 类型 | 说明 |
|------|------|------|
| `intent` | string | 识别的意图类型 |
| `topic` | string/null | 提取的主题 |
| `confidence` | number | 置信度 (0.0-1.0) |
| `parameters` | object | 额外参数 (quantity, difficulty 等) |

### stats (统计信息)

| 字段 | 类型 | 说明 |
|------|------|------|
| `total_requests` | number | 总请求数 |
| `rule_based_success` | number | 规则引擎成功次数 |
| `llm_fallback` | number | LLM Fallback 次数 |
| `rule_success_rate` | string | 规则引擎命中率 |

## 📈 使用场景

### 1. 调试 Intent Router

查看用户输入是如何被识别的：
```json
{
  "user_message": "根据这些内容帮我巩固",
  "method": "llm_fallback",
  "results": [
    {
      "intent": "contextual",
      "topic": null,
      "confidence": 0.85,
      "parameters": {
        "needs_last_artifact": true,
        "reference_type": "content"
      }
    }
  ]
}
```

### 2. 监控 Token 消耗

对比规则引擎和 LLM 的 token 消耗：
```json
{
  "stats": {
    "rule_based_success": 12,  // 12 × 0 tokens = 0
    "llm_fallback": 3,          // 3 × 1,487 tokens = 4,461
    "rule_success_rate": "80.0%"
  }
}
```

### 3. 分析用户行为

通过 history 查看最近的用户交互模式：
- 明确请求 vs 模糊请求的比例
- 常见的主题和意图类型
- 参数提取的准确性

## 🔄 更新机制

- ✅ **实时更新**: 每次 Intent Router 运行后立即保存
- ✅ **自动维护**: 只保留最近 10 条历史记录
- ✅ **统计累积**: stats 统计从系统启动开始累积

## 🎯 Phase 3 架构优化指标

通过这个文件可以实时监控：

| 指标 | 目标 | 监控方式 |
|------|------|---------|
| 规则引擎命中率 | 70-80% | `stats.rule_success_rate` |
| Token 节省率 | 90%+ | 对比 `rule_based_success` 和 `llm_fallback` |
| 平均 Token 消耗 | <500 tokens/次 | `(llm_fallback × 1487) / total_requests` |

## 🛠️ 配置

如果需要禁用 Intent Router 输出保存：

```python
# backend/app/core/intent_router.py
intent_router = IntentRouter(
    use_rule_engine=True,
    save_output=False  # 禁用保存
)
```

## 📝 注意事项

1. **文件大小**: 只保留最近 10 条历史，自动控制文件大小
2. **性能影响**: 文件保存是同步操作，但非常快速（< 1ms）
3. **隐私**: 包含用户消息，注意数据隐私保护
4. **重启后**: 统计数据会重置，但历史记录会保留

---

💡 **提示**: 结合 `session_demo-session.json` 和 `intent_router_output.json` 可以完整追踪用户的学习历程和系统的响应过程！

