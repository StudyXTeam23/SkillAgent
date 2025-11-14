# Skill Agent Demo

一个基于 FastAPI + React 的智能学习助手演示系统，展示从"工具箱"到"智能 Agent"的架构转型。

## 🏗️ 架构概览

```
User → Frontend (React) → Backend API (FastAPI) → Skill Orchestrator
                                                      ↓
                                     ┌────────────────┼────────────────┐
                                     ↓                ↓                ↓
                              Intent Router    Memory Manager   Skill Registry
                                     ↓                ↓                ↓
                                     └────────────────┼────────────────┘
                                                      ↓
                                               Gemini API (LLM)
```

### 核心特性

- **Intent Recognition**: 智能意图识别，理解用户学习需求
- **Memory Management**: 用户学习画像和会话上下文管理
- **Skill Orchestration**: 动态技能编排和执行
- **Multi-subject Support**: 支持所有学科的学习内容生成
- **Interactive UI**: 现代化聊天界面，实时反馈

## 📦 技术栈

### Backend
- **FastAPI** 0.115+ - 高性能 Web 框架
- **Pydantic** 2.0+ - 数据验证
- **Google Gemini API** - 大语言模型
- **Python** 3.11+

### Frontend
- **React** 18 - UI 框架
- **TypeScript** 5.0+ - 类型安全
- **Vite** 7 - 构建工具
- **Tailwind CSS** 3 - 样式框架

## 🚀 快速开始

### 前置要求

- Python 3.11+
- Node.js 18+
- Gemini API Key ([获取地址](https://ai.google.dev/))

### 1. 克隆项目

```bash
git clone <your-repo>
cd skill_agent_demo
```

### 2. 启动后端

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，添加你的 GEMINI_API_KEY

# 启动服务器
python -m uvicorn app.main:app --reload
```

后端将在 `http://localhost:8000` 启动

### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 `http://localhost:5173` 启动

### 4. 访问应用

打开浏览器访问 `http://localhost:5173`

## 📚 API 文档

后端启动后，访问以下地址查看 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 主要 API 端点

#### POST /api/agent/chat
统一的聊天端点，处理用户消息并返回 AI 生成的内容。

**请求体**:
```json
{
  "user_id": "demo-user",
  "session_id": "demo-session",
  "message": "给我几道微积分极限的练习题"
}
```

**响应**:
```json
{
  "user_id": "demo-user",
  "session_id": "demo-session",
  "response_content": { ... },
  "content_type": "quiz_set",
  "intent": "quiz",
  "skill_id": "quiz_skill",
  "processing_time_ms": 1234
}
```

#### GET /api/agent/info
获取系统信息和可用技能列表。

#### GET /api/agent/health
健康检查端点。

## 🧪 运行测试

### 后端测试

```bash
cd backend
python -m pytest tests/ -v
```

测试覆盖：
- 146 个测试用例
- ~90%+ 代码覆盖率
- 0.21秒 执行时间

## 📁 项目结构

```
skill_agent_demo/
├── backend/
│   ├── app/
│   │   ├── api/           # API 端点
│   │   ├── core/          # 核心业务逻辑
│   │   ├── models/        # Pydantic 模型
│   │   ├── prompts/       # Prompt 模板 (11个文件, 111KB)
│   │   └── services/      # 外部服务封装
│   ├── skills_config/     # 技能配置 YAML
│   ├── tests/             # 测试文件
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/           # API 客户端
│   │   ├── components/    # React 组件
│   │   ├── contexts/      # React Context
│   │   ├── hooks/         # 自定义 Hooks
│   │   └── types/         # TypeScript 类型
│   └── package.json
└── README.md
```

## 🎨 使用示例

### 1. 生成练习题

```
用户: 给我几道微积分极限的练习题
AI: [生成 QuizCard 组件，包含选择题、答案和解析]
```

### 2. 概念讲解

```
用户: 什么是牛顿第二定律？
AI: [生成 ExplainCard 组件，包含定义、公式、示例和相关概念]
```

### 3. 多学科支持

支持所有学科：
- 数学 (微积分、线性代数、统计学...)
- 物理 (力学、电磁学、热力学...)
- 化学 (有机化学、无机化学...)
- 生物 (细胞生物学、遗传学...)
- 历史、文学、编程等

## 🔧 环境变量

创建 `backend/.env` 文件：

```bash
# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# Server
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# AWS S3 (可选，Demo 使用内存存储)
USE_S3_STORAGE=false
```

## 📊 性能指标

- **后端响应时间**: < 5秒 (端到端)
- **LLM 调用**: Gemini 2.5 Flash (快速模型)
- **前端加载**: < 1秒 (生产构建)
- **测试执行**: 0.21秒 (146 个测试)

## 🛠️ 开发指南

### 添加新技能

1. 在 `backend/skills_config/` 创建 YAML 配置
2. 在 `backend/app/prompts/` 创建 Prompt 模板
3. Skill Registry 会自动加载新技能

### 技能配置示例

```yaml
id: quiz_skill
display_name: "练习题生成"
version: "1.0.0"
intent_tags:
  - quiz
input_schema:
  type: object
  properties:
    topic:
      type: string
    difficulty:
      type: string
      enum: [easy, medium, hard]
output_schema:
  type: object
  properties:
    quiz_set:
      type: object
models:
  primary: gemini-2.5-flash
prompt_file: quiz_generation_skill.txt
```

## 📝 待办事项

- [x] Backend Core Modules (Phase 1-4)
- [x] Frontend Core Components (Phase 5)
- [ ] E2E Integration Tests (Phase 6)
- [ ] Dark Mode Support
- [ ] User Authentication
- [ ] Session Persistence
- [ ] More Skills (Flashcards, Notes, Tutor Dialogue)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 License

MIT License

## 👏 致谢

- Google Gemini API
- FastAPI
- React
- Tailwind CSS
