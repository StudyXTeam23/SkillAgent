# StudyX Skill Agent Demo - Frontend

React + TypeScript + Vite 前端应用，提供智能学习助手聊天界面。

## 技术栈

- **React 18** - UI 框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **Tailwind CSS** - 样式框架
- **Axios** - HTTP 客户端
- **React Markdown** - Markdown 渲染
- **Lucide React** - 图标库

## 项目结构

```
frontend/
├── src/
│   ├── api/              # API 客户端
│   ├── components/       # React 组件
│   │   ├── chat/        # 聊天相关组件
│   │   ├── artifacts/   # 产物展示组件
│   │   └── common/      # 通用组件
│   ├── context/         # React Context
│   ├── hooks/           # 自定义 Hooks
│   ├── types/           # TypeScript 类型定义
│   ├── utils/           # 工具函数
│   ├── App.tsx          # 主应用组件
│   └── main.tsx         # 入口文件
├── public/              # 静态资源
└── package.json
```

## 开发

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

前端将运行在 `http://localhost:5173`

### 构建生产版本

```bash
npm run build
```

### 预览生产版本

```bash
npm run preview
```

## 环境变量

创建 `.env` 文件：

```env
VITE_API_BASE_URL=http://localhost:8000
```

## API 代理

开发模式下，`/api/*` 请求会被代理到 `http://localhost:8000`。

## 功能特性

- ✅ 实时聊天界面
- ✅ 智能意图识别反馈
- ✅ 多种产物类型展示（Quiz, Explanation）
- ✅ Markdown 渲染支持
- ✅ 响应式设计
- ✅ 深色模式支持
- ✅ 加载状态和错误处理
- ✅ TypeScript 类型安全

## 组件说明

### Chat 组件
- `ChatInterface` - 主聊天界面
- `MessageList` - 消息列表
- `MessageInput` - 消息输入框

### Artifact 组件
- `QuizCard` - 练习题展示
- `ExplainCard` - 概念讲解展示
- `LoadingCard` - 加载状态
- `ErrorCard` - 错误提示

### Common 组件
- `Button` - 按钮
- `Input` - 输入框
- `Card` - 卡片容器
- `Badge` - 标签

## 开发指南

1. 所有组件使用 TypeScript 编写
2. 使用 Tailwind CSS 进行样式设计
3. 遵循 React Hooks 最佳实践
4. API 调用统一通过 `api/` 目录封装
5. 使用 Context + Reducer 管理全局状态

## License

MIT
