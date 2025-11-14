# 🚀 Quick Start - 纯静态 HTML Demo

## ✅ 已创建 100% 设计稿还原版本

**文件位置：** `frontend/public/demo.html`

### 特点：
- ✅ **100% 照搬设计稿 HTML**（完全不修改）
- ✅ **使用 Tailwind CDN**（无需构建）
- ✅ **完整交互功能**（与后端 API 集成）
- ✅ **无需 React**，直接用浏览器打开

---

## 🎯 启动步骤

### 1️⃣ 启动后端

```bash
cd /Users/mac/Desktop/kimi_playground/skill_agent_demo/backend

# 激活虚拟环境
source venv/bin/activate

# 启动 FastAPI 服务器
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**检查后端是否运行：** 浏览器访问 http://localhost:8000/docs

---

### 2️⃣ 打开静态 HTML

**方法 A: 直接打开（推荐）**

```bash
open /Users/mac/Desktop/kimi_playground/skill_agent_demo/frontend/public/demo.html
```

**方法 B: 通过 Vite（如果需要热更新）**

```bash
cd /Users/mac/Desktop/kimi_playground/skill_agent_demo/frontend
npm run dev
```

然后访问: http://localhost:5173/demo.html

---

## 🔍 后端错误排查

如果前端显示 **"No response from server"**：

### 1. 检查后端是否运行

```bash
curl http://localhost:8000/api/health
```

应该返回：`{"status":"healthy",...}`

### 2. 查看后端日志

```bash
# 如果后端在运行，查看日志
cd backend
tail -f app.log

# 或查看终端输出
```

### 3. 检查浏览器控制台

按 **F12** 打开开发者工具，查看：
- **Console** 标签：JavaScript 错误
- **Network** 标签：API 请求是否成功

### 4. 常见错误

**错误：CORS 问题**
- 原因：后端未配置 CORS
- 解决：检查 `backend/main.py` 是否有 CORS 中间件

**错误：Connection refused**
- 原因：后端未启动
- 解决：按步骤 1️⃣ 启动后端

**错误：500 Internal Server Error**
- 原因：后端代码错误
- 解决：查看后端日志 `tail -f backend/app.log`

---

## 📸 效果检查清单

打开 demo.html 后，应该看到：

### ✅ Sidebar（左侧）
- [ ] StudyX logo（圆形，蓝色）
- [ ] "Calculus Practice" 有蓝色背景
- [ ] Material Symbols 图标清晰显示
- [ ] 蓝色 "New Chat" 按钮

### ✅ TopNavBar（顶部）
- [ ] "Calculus Practice Session" 标题
- [ ] 通知/闪电按钮（浅蓝色背景）
- [ ] 圆形用户头像（右上角）

### ✅ Chat Area（聊天区）
- [ ] 圆形 Agent 头像（蓝色）
- [ ] 欢迎消息（白色背景，灰色边框）
- [ ] 输入框：白色背景，灰色边框
- [ ] 蓝色发送按钮（右侧）

### ✅ 交互功能
- [ ] 输入消息后，点击发送
- [ ] 用户消息显示为蓝色气泡（右侧）
- [ ] 显示加载中动画（三个跳动的点）
- [ ] Agent 响应显示为白色气泡（左侧）

---

## 🐛 如果样式还是不对

如果样式和设计稿不匹配，可能是：

1. **Tailwind CDN 未加载**
   - 检查网络连接
   - 打开 F12 → Network，查看是否加载了 `cdn.tailwindcss.com`

2. **Google Fonts 未加载**
   - 检查 F12 → Network，查看 `fonts.googleapis.com`

3. **图片未加载**
   - 头像图片来自 Google Cloud，需要网络连接

---

## 📞 获取帮助

如果还有问题，请提供：

1. **浏览器控制台截图**（F12 → Console）
2. **后端日志输出**
3. **页面实际效果截图**

这样我才能精确定位问题！🙏

