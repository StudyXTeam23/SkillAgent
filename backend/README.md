# Skill Agent Demo - Backend

智能学习助手后端服务，基于 FastAPI 框架。

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.template` 为 `.env` 并填写配置：

```bash
cp .env.template .env
```

编辑 `.env` 文件，填写以下必需配置：

```env
# Google Gemini API Key（必需）
GEMINI_API_KEY=your_gemini_api_key_here

# AWS S3 配置（可选，用于存储数据）
USE_S3_STORAGE=true
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET=skill-agent-demo
```

### 3. 启动服务器

```bash
# 开发模式（热重载）
uvicorn app.main:app --reload --port 8000

# 或使用 Python 直接运行
python -m app.main
```

### 4. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理
│   ├── api/                 # API 路由
│   ├── core/                # 核心模块（Intent Router, Memory Manager 等）
│   ├── models/              # Pydantic 数据模型
│   ├── services/            # 外部服务封装（Gemini API）
│   ├── skills/              # 技能实现
│   └── utils/               # 工具函数
├── tests/                   # 测试代码
├── requirements.txt         # Python 依赖
└── .env                     # 环境变量配置
```

## S3 存储说明

本 demo 使用 AWS S3 来存储应该放在数据库的数据：

- **Memory Profiles**: `s3://skill-agent-demo/memory_profiles/{user_id}.json`
- **Session Contexts**: `s3://skill-agent-demo/session_contexts/{session_id}.json`
- **Skill Configs**: `s3://skill-agent-demo/skills/{skill_id}/skill.yaml`

如果不想使用 S3，将 `USE_S3_STORAGE=false`，系统会使用内存存储（重启后数据丢失）。

## API 端点

### 核心端点

- `POST /agent/chat` - 统一聊天入口
- `POST /intent/parse` - 意图识别（调试用）
- `GET /memory/user/{user_id}` - 获取用户学习画像
- `GET /memory/session/{session_id}` - 获取会话上下文
- `GET /skills` - 获取所有技能列表
- `GET /skills/{skill_id}` - 获取指定技能定义

### 健康检查

```bash
curl http://localhost:8000/health
```

## 开发指南

### 添加新的 Skill

1. 在 `app/skills/{skill_id}/` 创建文件夹
2. 创建 `skill.yaml` 配置文件
3. 创建 `handler.py` 实现文件
4. 在 `prompts/generate.txt` 中编写 prompt

### 运行测试

```bash
pytest tests/
```

## 故障排除

### Gemini API 错误

- 检查 `GEMINI_API_KEY` 是否正确
- 确认 API Key 有足够的配额
- 查看日志了解具体错误信息

### S3 连接错误

- 验证 AWS 凭证是否正确
- 检查 S3 bucket 是否存在
- 确认 IAM 权限是否足够（需要 s3:GetObject, s3:PutObject, s3:ListBucket）

## 技术栈

- **Web 框架**: FastAPI 0.115+
- **数据验证**: Pydantic 2.9+
- **AI 模型**: Google Gemini 2.5 Flash
- **存储**: AWS S3 (boto3)
- **配置管理**: pydantic-settings

