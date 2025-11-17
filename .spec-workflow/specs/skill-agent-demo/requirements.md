# Requirements Document - Skill Agent Demo

## Introduction

这是一个 StudyX Skill Agent 系统的可演示 MVP（最小可行产品），用于展示从"工具箱模式"到"智能学习助手模式"的架构升级。该 demo 将实现核心的意图识别、记忆管理、技能编排和技能执行功能，通过一个统一的聊天界面为用户提供无缝的学习体验。

**核心价值：**
- 用户无需在多个工具间跳转，一个对话框完成所有学习任务
- 系统自动理解用户意图并选择合适的技能
- 记住学习进度和用户偏好，提供个性化体验
- 降低 token 成本（按需加载 Skill Prompt，而非大杂烩）

**Demo 场景：** 微积分学习助手，支持练习题生成和概念讲解两个核心技能。

## Alignment with Product Vision

根据 `General.md` PRD 文档，本 demo 实现了以下核心目标：

1. **用户体验提升**：从支离破碎的多工具跳转，升级为连续流畅的对话式学习
2. **高效意图分析**：轻量级 Intent Router 准确识别用户需求
3. **成本控制**：按需加载 Skill Prompt，避免大量无关上下文消耗 token
4. **可扩展架构**：通过 Skill Registry 实现技能的插件化管理

## Requirements

### Requirement 1: 统一聊天界面

**User Story:** 作为学生，我希望在一个对话界面中完成所有学习任务（解题、讲解、练习），而不是在多个工具间跳转，从而获得连续流畅的学习体验。

#### Acceptance Criteria

1. WHEN 用户打开应用 THEN 系统 SHALL 显示一个统一的聊天界面
2. WHEN 用户输入学习请求（如"给我几道极限练习题"）THEN 系统 SHALL 在同一界面中返回结构化结果
3. WHEN 用户在同一会话中提出不同类型的请求（练习 → 讲解）THEN 系统 SHALL 在同一对话流中响应，无需页面跳转
4. WHEN 系统返回不同类型的内容（练习题、文字讲解）THEN 界面 SHALL 根据内容类型自动选择合适的渲染组件

### Requirement 2: 智能意图识别

**User Story:** 作为学生，我希望系统能理解我的自然语言请求（如"帮我练习极限"），并自动判断我需要什么类型的帮助，而不需要我手动选择工具。

#### Acceptance Criteria

1. WHEN 用户输入自然语言请求 THEN Intent Router SHALL 解析出结构化意图（intent, topic, confidence）
2. WHEN 意图识别置信度 >= 0.6 THEN 系统 SHALL 接受该意图并继续执行
3. WHEN 意图识别置信度 < 0.6 THEN 系统 SHALL 返回澄清性问题（如"你是想要练习题还是概念讲解？"）
4. WHEN 用户输入包含明确关键词（如"练习题"、"讲解"）THEN 系统 SHALL 正确识别对应的意图标签（quiz、explain）
5. WHEN 识别失败 THEN 系统 SHALL fallback 到 explain 意图（默认讲解模式）

### Requirement 3: 学习记忆管理

**User Story:** 作为学生，我希望系统能记住我的学习进度和偏好（如我在哪些知识点薄弱、更喜欢练习题还是讲解），从而提供个性化的学习建议。

#### Acceptance Criteria

1. WHEN 用户首次使用 THEN Memory Manager SHALL 创建空的 UserLearningProfile 和 SessionContext
2. WHEN 用户完成一次练习 THEN 系统 SHALL 更新 mastery_map（知识点掌握度）
3. WHEN 用户多次使用某种学习方式（如连续做题）THEN 系统 SHALL 记录用户偏好（preferred_artifact）
4. WHEN Intent Router 需要上下文 THEN Memory Manager SHALL 提供简短的记忆摘要（≤ 100 tokens）
5. WHEN 会话结束 THEN SessionContext SHALL 被清理，UserLearningProfile SHALL 被持久化

### Requirement 4: 技能注册与发现

**User Story:** 作为系统开发者，我希望通过标准化的 Skill Registry 管理所有技能定义，从而快速添加新技能而不影响核心系统。

#### Acceptance Criteria

1. WHEN 系统启动 THEN Skill Registry SHALL 加载所有技能定义文件（JSON/YAML）
2. WHEN Orchestrator 需要查找技能 THEN Registry SHALL 根据 intent_tags 返回匹配的技能列表
3. WHEN 查询技能定义 THEN Registry SHALL 返回完整的 input_schema、output_schema、models 配置
4. WHEN 验证技能输入参数 THEN Registry SHALL 使用 JSON Schema 验证参数有效性
5. WHEN 添加新技能 THEN 只需创建新的 skill.json 文件，无需修改核心代码

### Requirement 5: 技能智能编排

**User Story:** 作为学生，我希望系统能自动选择最合适的技能来响应我的请求，并智能地构建执行参数（如根据我的掌握度选择练习题难度）。

#### Acceptance Criteria

1. WHEN Intent Router 返回意图结果 THEN Skill Orchestrator SHALL 从 Registry 查找匹配的技能
2. WHEN 多个技能匹配同一意图 THEN Orchestrator SHALL 根据成本、用户偏好选择最优技能
3. WHEN 构建技能输入参数 THEN Orchestrator SHALL 结合 intent、memory、user_profile 生成完整的 params + context
4. WHEN 技能执行完成 THEN Orchestrator SHALL 封装结果为统一的 artifact 格式
5. WHEN 技能执行失败 THEN Orchestrator SHALL 尝试 fallback 模型或 fallback 技能
6. WHEN 结果返回前 THEN Orchestrator SHALL 调用 Memory Manager 更新学习状态

### Requirement 6: Quiz Skill（练习题生成技能）

**User Story:** 作为学生，我希望通过说"给我几道极限练习题"来获得符合我当前掌握度的练习题，从而巩固知识点。

#### Acceptance Criteria

1. WHEN QuizSkill 被调用 THEN 它 SHALL 接收参数：topic, difficulty, num_questions
2. WHEN difficulty 未指定 THEN 系统 SHALL 根据用户 mastery_map 推断难度（weak → easy, strong → hard）
3. WHEN 调用 Gemini API THEN QuizSkill SHALL 使用 gemini-2.5-flash 模型
4. WHEN LLM 返回结果 THEN QuizSkill SHALL 验证输出符合 output_schema（questions 数组结构）
5. WHEN 输出验证通过 THEN QuizSkill SHALL 返回结构化题目列表（包含 stem, options, answer, explanation）

### Requirement 7: Explain Skill（概念讲解技能）

**User Story:** 作为学生，我希望通过说"讲讲极限的定义"来获得清晰的概念讲解，从而理解理论知识。

#### Acceptance Criteria

1. WHEN ExplainSkill 被调用 THEN 它 SHALL 接收参数：topic, depth（可选）
2. WHEN depth 未指定 THEN 系统 SHALL 根据用户 mastery 推断讲解深度（weak → basic, strong → advanced）
3. WHEN 调用 Gemini API THEN ExplainSkill SHALL 使用 gemini-2.5-flash 模型
4. WHEN LLM 返回结果 THEN ExplainSkill SHALL 返回结构化讲解内容（包含 title, content, examples）

### Requirement 8: 端到端集成流程

**User Story:** 作为学生，我希望从输入问题到获得结果的整个流程无缝衔接，感受不到系统内部的复杂性。

#### Acceptance Criteria

1. WHEN 用户发送消息 THEN 前端 SHALL 调用统一的 `/agent/chat` API
2. WHEN 后端收到请求 THEN 流程 SHALL 依次执行：Intent Router → Memory Manager → Skill Orchestrator → Skill Execute → Memory Update
3. WHEN 任一步骤失败 THEN 系统 SHALL 返回友好的错误提示（如"抱歉，我没太理解你的问题，能换个方式说吗？"）
4. WHEN 流程完成 THEN 前端 SHALL 根据 artifact 类型渲染对应的 UI 组件
5. WHEN 响应时间超过 3 秒 THEN 前端 SHALL 显示加载状态

## UI/UX Requirements

**参考设计文件：** `prd_document/ui_designs/`

本 demo 采用现代化的聊天式界面设计，遵循以下 UI/UX 原则。

### Requirement 9: 主聊天界面布局

**User Story:** 作为学生，我希望界面简洁现代，能快速找到功能入口，并且在聊天时不受干扰。

#### Acceptance Criteria

1. WHEN 用户打开应用 THEN 界面 SHALL 采用三栏布局：
   - 左侧：导航侧边栏（宽度 256px）
   - 中间：聊天主区域（自适应宽度）
   - 右侧：无（为未来扩展预留）

2. WHEN 显示侧边栏 THEN 侧边栏 SHALL 包含以下元素：
   - 顶部：StudyX Logo + "Skill Agent Demo" 标识
   - 中部：课程/场景列表（如 Dashboard、Calculus Practice、Concept Explanation）
   - 底部：New Chat 按钮、Settings、Help 入口

3. WHEN 显示顶部导航栏 THEN 顶栏 SHALL 包含：
   - 左侧：当前会话标题（如 "Calculus Practice Session"）
   - 右侧：通知图标、快捷操作图标、用户头像

4. WHEN 显示聊天区域 THEN 聊天区 SHALL 支持：
   - 垂直滚动查看历史消息
   - Agent 消息左对齐（带头像、浅色背景）
   - 用户消息右对齐（带头像、蓝色背景）
   - 加载状态显示（三个跳动的圆点动画）

5. WHEN 显示输入区域 THEN 输入框 SHALL 固定在底部，包含：
   - 文本输入框（placeholder: "Ask a calculus question or type your answer..."）
   - 发送按钮（蓝色圆形，Material Icons "send" 图标）

**设计规范：**
- **字体**：Space Grotesk（主界面）、Lexend（卡片组件）
- **配色**：
  - Primary: `#137fec`（品牌蓝）
  - Background Light: `#f6f7f8`
  - Surface Light: `#ffffff`
  - Text Primary: `#0d141b`
  - Border: `#e7edf3`
- **圆角**：默认 `0.25rem`，卡片 `0.75rem`
- **间距**：使用 Tailwind 标准间距（4px 基准）

### Requirement 10: QuizCard 组件设计

**User Story:** 作为学生，我希望练习题展示清晰，能看到进度条、选项反馈和详细解析，从而更好地学习。

#### Acceptance Criteria

1. WHEN 渲染 QuizCard THEN 卡片 SHALL 包含以下区域：
   - 顶部：主题标签（如"微积分练习"）+ 进度条 + 进度文字（Question 1 of 5）
   - 中部：题目标题（大字号加粗）
   - 选项区：单选按钮 + 选项文字
   - 底部：提交按钮（或"再来一组练习"按钮）

2. WHEN 题目未提交 THEN 选项 SHALL 显示为：
   - 未选中：灰色边框，鼠标悬停变浅蓝背景
   - 已选中：蓝色边框 + 浅蓝背景
   - 可点击切换选择

3. WHEN 用户提交答案 THEN 界面 SHALL 更新为：
   - 正确答案：绿色边框 + 绿色背景 + 绿色对勾图标
   - 错误答案（用户选择）：红色边框 + 红色背景 + 红色叉号图标
   - 其他选项：灰色边框 + 60% 透明度，禁止点击
   - 底部显示 Explanation 区域（浅灰背景，包含详细解析）

4. WHEN 显示进度条 THEN 进度条 SHALL：
   - 背景：浅灰色 `#e5e7eb`
   - 进度：蓝色渐变填充，根据 `currentQuestion / totalQuestions` 计算宽度
   - 高度：8px，圆角

5. WHEN 渲染 Explanation THEN 解析区 SHALL：
   - 标题："Explanation" 加粗
   - 内容：分段文字说明，支持数学公式展示
   - 背景：浅灰 `bg-slate-50`

**组件参考：** `prd_document/ui_designs/quizcard_(练习题)_组件/`

### Requirement 11: ExplainCard 组件设计

**User Story:** 作为学生，我希望概念讲解结构清晰、易读，包含公式和例子，从而快速理解知识点。

#### Acceptance Criteria

1. WHEN 渲染 ExplainCard THEN 卡片 SHALL 包含以下结构：
   - 标题区：概念名称（如 "The Chain Rule"），大标题加粗
   - 内容区：
     - 概念定义段落
     - 公式展示区域（居中、等宽字体、浅色背景）
     - 解释性文字
   - 例子区：
     - "Examples" 标题
     - 多个编号例子（序号圆形蓝色背景）

2. WHEN 显示公式 THEN 公式区域 SHALL：
   - 背景：浅灰 `bg-background-light`
   - 文字：等宽字体（font-mono）、加粗
   - 居中对齐
   - 上下间距 16px

3. WHEN 显示代码片段 THEN 代码 SHALL：
   - 浅蓝背景 `bg-primary/10`
   - 蓝色文字 `text-primary`
   - 内边距 4px
   - 圆角 4px

4. WHEN 显示例子列表 THEN 每个例子 SHALL：
   - 序号：蓝色圆形背景 + 白色数字（直径 24px）
   - 标题：加粗，描述例子目标
   - 步骤列表：左侧蓝色竖线，每步文字左对齐

5. WHEN 例子包含步骤 THEN 步骤列表 SHALL：
   - 左侧：2px 蓝色半透明竖线
   - 缩进：32px
   - 行间距：8px
   - 文字颜色：次要文字色 `text-secondary`

**组件参考：** `prd_document/ui_designs/explaincard_(概念讲解)_组件/`

### Requirement 12: 响应式设计与暗黑模式

**User Story:** 作为学生，我希望界面在不同设备上都能良好显示，并支持暗黑模式，从而在任何环境下舒适使用。

#### Acceptance Criteria

1. WHEN 在移动设备（< 768px）THEN 界面 SHALL：
   - 隐藏侧边栏（点击菜单图标展开）
   - 聊天区域占满屏幕宽度
   - 顶部导航栏高度不变
   - 卡片组件调整内边距为 16px（桌面为 32px）

2. WHEN 在平板设备（768px - 1024px）THEN 侧边栏 SHALL：
   - 宽度缩小至 200px
   - 导航项文字保持可读

3. WHEN 在桌面设备（> 1024px）THEN 界面 SHALL：
   - 侧边栏固定宽度 256px
   - 聊天区域最大宽度 1200px，居中显示
   - 卡片组件最大宽度 800px

4. WHEN 用户切换到暗黑模式 THEN 配色 SHALL 更新为：
   - Background Dark: `#101922`
   - Surface Dark: `#1a2632`
   - Text Dark Primary: `#f6f7f8`
   - Border Dark: `#2a3b4d`
   - 所有组件自动适配暗黑配色

5. WHEN 检测系统主题偏好 THEN 应用 SHALL 自动应用对应主题

**实现方式：**
- 使用 Tailwind CSS `dark:` 前缀定义暗黑模式样式
- 使用 CSS 变量存储主题颜色
- 使用 `prefers-color-scheme` 媒体查询检测系统偏好

### Requirement 13: 加载状态与错误提示

**User Story:** 作为学生，我希望在等待响应时看到明确的加载状态，遇到错误时看到友好的提示，从而了解系统当前状态。

#### Acceptance Criteria

1. WHEN Agent 正在思考 THEN 界面 SHALL 显示：
   - Agent 头像 + "StudyX Agent" 标签
   - 三个跳动圆点动画（bounce 动画，延迟 0.1s/0.2s/0.3s）
   - 浅色消息气泡背景

2. WHEN API 调用失败 THEN 界面 SHALL 显示：
   - Agent 消息气泡，内容为友好错误提示
   - 例如："抱歉，我遇到了一些问题。请稍后再试或换个问题。"
   - 可选：重试按钮

3. WHEN 输入框为空 THEN 发送按钮 SHALL 禁用（灰色、不可点击）

4. WHEN 用户输入内容 THEN 发送按钮 SHALL 启用（蓝色、hover 效果）

5. WHEN 提交练习题答案 THEN 提交按钮 SHALL：
   - 显示加载状态（按钮文字变为"提交中..."）
   - 禁用防止重复点击
   - 收到响应后恢复正常状态

**动画规范：**
- 跳动动画：translateY(-4px)，持续时间 1s，无限循环
- 按钮 hover：背景色 90% 透明度，过渡时间 200ms
- 选项点击：背景色过渡 150ms

### Requirement 14: 用户认证与Session持久化

**User Story:** 作为学生，我希望系统能记住我的身份，每次重新登录后自动加载我的学习偏好、历史聊天记录和知识掌握度，从而获得连续的个性化学习体验。

#### Acceptance Criteria

1. WHEN 用户首次访问应用 THEN 系统 SHALL 显示登录/注册界面
2. WHEN 用户注册新账户 THEN 系统 SHALL：
   - 验证用户名唯一性（用户名长度 3-20 字符）
   - 验证密码强度（至少 6 字符）
   - 创建用户记录并生成 JWT token
   - 自动登录并跳转到聊天界面
3. WHEN 用户登录 THEN 系统 SHALL：
   - 验证用户名和密码
   - 生成 JWT token（有效期 7 天）
   - 返回 token 和用户基本信息
   - 前端存储 token 到 localStorage
4. WHEN 已登录用户刷新页面 THEN 系统 SHALL：
   - 从 localStorage 读取 token
   - 验证 token 有效性
   - 自动加载用户的 UserLearningProfile 和历史聊天记录
5. WHEN 用户发送消息 THEN 系统 SHALL：
   - 从 token 中提取 user_id
   - 关联消息到该用户的 session
   - 持久化聊天记录到存储
6. WHEN 用户退出登录 THEN 系统 SHALL：
   - 清除前端 localStorage 中的 token
   - 清除当前会话状态
   - 返回登录界面
7. WHEN Memory Manager 需要用户数据 THEN 系统 SHALL：
   - 从持久化存储加载 UserLearningProfile
   - 加载最近 N 条历史消息作为 SessionContext
   - 分析历史记录生成用户偏好摘要
8. WHEN 用户完成一次交互 THEN 系统 SHALL：
   - 更新 UserLearningProfile（mastery_map, preferred_artifact）
   - 持久化更新到存储
   - 保存聊天记录（user message + agent response）

**存储方案：**
- **Backend**: 使用 SQLite（轻量级，无需额外服务）
- **数据表**:
  - `users` 表：user_id, username, password_hash, created_at
  - `learning_profiles` 表：user_id, mastery_map (JSON), preferred_artifact, last_active
  - `chat_history` 表：id, user_id, session_id, role, content, artifact (JSON), timestamp

**认证方式：**
- 使用 JWT (JSON Web Token) 无状态认证
- Token payload: {user_id, username, exp}
- 前端每次请求在 Authorization header 中携带 token

## Non-Functional Requirements

### Code Architecture and Modularity

- **单一职责原则**：每个模块（Intent Router、Memory Manager、Skill Orchestrator、Skills）独立实现，职责明确
- **模块化设计**：
  - 后端：每个核心模块独立的 Python 文件/包
  - 前端：UI 组件按功能拆分（ChatInterface、MessageRenderer、QuizCard、ExplainCard）
- **依赖管理**：模块间通过明确的 API 接口通信，避免循环依赖
- **清晰接口**：所有 Skill 实现统一的 `execute(params, context)` 签名

### Performance

- **Intent Router 响应时间**：≤ 500ms（使用轻量级 Gemini Flash 模型）
- **Skill 执行时间**：QuizSkill ≤ 3s，ExplainSkill ≤ 2s
- **端到端响应时间**：用户发送消息到前端渲染结果 ≤ 5s
- **Token 优化**：Intent Router prompt ≤ 200 tokens，单个 Skill prompt ≤ 500 tokens

### Security

- **API Key 保护**：Gemini API Key 存储在后端环境变量中，不暴露给前端
- **输入验证**：所有用户输入经过 Pydantic 模型验证，防止注入攻击
- **错误处理**：敏感错误信息（如 API Key 错误）不直接返回前端

### Reliability

- **Fallback 机制**：
  - Intent Router：置信度低时返回澄清问题
  - Skill 执行：主模型失败时尝试 fallback 模型
  - 网络错误：显示重试选项
- **错误日志**：所有模块异常记录到日志文件，便于调试
- **优雅降级**：当 Memory 服务不可用时，使用空上下文继续执行

### Usability

- **对话式交互**：用户只需自然语言输入，无需学习复杂操作
- **即时反馈**：加载状态、进度提示清晰可见
- **响应式设计**：界面适配桌面和移动端
- **错误提示友好**：避免技术术语，用学生能理解的语言解释问题

### Scalability & Extensibility

- **技能可扩展**：添加新 Skill 只需：
  1. 创建 `skills/{skill_id}/skill.json` 配置
  2. 实现 `skills/{skill_id}/handler.py`
  3. Registry 自动加载
- **意图可扩展**：Intent Router 支持动态添加新 intent 标签
- **存储可替换**：当前使用内存存储，接口设计支持无缝切换到 Redis/MongoDB

---

## V2 进阶需求 (Advanced Requirements)

以下需求基于 V1 完成后的架构进阶，旨在提升模糊问题处理、任务跳跃能力和并行执行效率。

### Requirement 15: 意图分布与多候选识别

**User Story:** 作为学生，当我提出模糊请求（如"帮我学习极限"）时，我希望系统不仅给出一个答案，还能推荐其他可能的学习方式，从而让我有更多选择。

#### Acceptance Criteria

1. WHEN Intent Router 解析模糊意图 THEN 系统 SHALL 返回意图分布（primary_intent + candidates list）
2. WHEN candidates list 包含多个意图 THEN 每个候选 SHALL 包含 {intent: str, score: float}
3. WHEN primary_intent score >= 0.7 THEN 系统 SHALL 直接执行该意图
4. WHEN primary_intent score < 0.7 且 candidates 中有 score >= 0.6 的候选 THEN 系统 SHALL 执行 primary 并推荐其他候选
5. WHEN Skill 执行完成 THEN Orchestrator SHALL 返回 suggested_next_skills（基于 candidates）
6. WHEN 前端收到 suggested_next_skills THEN 界面 SHALL 显示推荐按钮（如"要不要出几道题练习？"）

**实现要点：**
- 修改 `IntentResult` 模型：添加 `candidates: list[IntentCandidate]` 字段
- 更新 Intent Router prompt：返回 top3 intents + scores
- Orchestrator 根据候选意图生成 suggested_next_skills

### Requirement 16: 上下文聚合与统一管理

**User Story:** 作为系统开发者，我希望有一个统一的 ContextCollector 模块聚合所有上下文信息（用户画像、会话历史、上传文件等），从而让 Intent Router 和 Skill Orchestrator 能访问完整的上下文。

#### Acceptance Criteria

1. WHEN Agent API 收到请求 THEN ContextCollector SHALL 聚合以下信息：
   - UserLearningProfile（长期记忆）
   - SessionContext（短期记忆）
   - recent_turns（最近 N 条对话）
   - uploads_summary（上传文件摘要，未来扩展）
2. WHEN ContextCollector 完成聚合 THEN 输出 SHALL 为 AnalysisContext 对象
3. WHEN IntentRouter 解析意图 THEN 它 SHALL 接收 AnalysisContext 作为输入
4. WHEN Skill Orchestrator 执行 THEN 它 SHALL 接收 AnalysisContext 作为输入
5. WHEN 某些上下文信息缺失（如新用户无历史）THEN ContextCollector SHALL 返回空值而不报错

**实现要点：**
- 新建 `backend/app/core/context_collector.py`
- 定义 `AnalysisContext` dataclass
- 在 `agent.py` 中调用顺序：ContextCollector → IntentRouter → Orchestrator

### Requirement 17: Planner 大脑层与任务跳跃

**User Story:** 作为学生，我希望在学习过程中能自然地跳转任务（如"做题 → 讲解 → 笔记 → 再做题"），而系统能理解我的意图并记住上下文，从而提供连贯的学习体验。

#### Acceptance Criteria

1. WHEN 系统需要决策下一步 Skill THEN Planner SHALL 生成 ExecutionPlan
2. WHEN ExecutionPlan 生成 THEN 它 SHALL 包含：
   - current_skill: 当前要执行的 Skill
   - pipeline_skills: 可选的连续执行 Skill 列表（如先 Explain 再 Quiz）
   - suggested_next_skills: 推荐的后续 Skill（供前端显示）
3. WHEN Skill 执行完成 THEN Memory Manager SHALL 接收 SkillEvent 更新状态
4. WHEN SkillEvent 被记录 THEN 它 SHALL 包含：{skill_id, intent, topic, artifact_type, artifact_id}
5. WHEN 用户提出关联请求（如"第2题我不会，讲一下"）THEN Planner SHALL 从 Memory 中获取上一轮的 artifact（quiz_set），并构建 ExplainSkill 参数
6. WHEN Skills 之间需要信息传递 THEN 只能通过 Memory + Planner，不允许 Skill 之间直接调用

**实现要点：**
- 新建 `backend/app/core/planner.py`，定义 `Planner` 类
- 定义 `ExecutionPlan` 和 `SkillEvent` Pydantic 模型
- 在 MemoryManager 中添加 `record_skill_event()` 方法
- 示例 Demo：连续对话"给我3道题" → "第2题讲一下" → "整理成笔记"

### Requirement 18: 并行执行与 Manus 学习包模式

**User Story:** 作为学生，当我上传一段课程笔记或讲座转写时，我希望系统能一次性生成多种学习材料（笔记、练习题、闪卡），而不是我反复请求多次，从而节省时间和提高效率。

#### Acceptance Criteria

1. WHEN 用户输入长文本或上传文件 THEN 系统 SHALL 首先调用 ContentAnalysisSkill 解析内容
2. WHEN ContentAnalysisSkill 返回结果 THEN 输出 SHALL 包含：
   - subject: 学科
   - topic: 主题
   - knowledge_points: 知识点列表
   - chapter_structure: 章节结构（可选）
   - key_examples: 重要示例
3. WHEN ContentAnalysis 完成 THEN Orchestrator SHALL 根据 Plan 并行执行多个 Skill
4. WHEN 并行执行多个 Skill THEN Orchestrator SHALL 使用 asyncio.gather() 并发调用
5. WHEN 所有 Skill 完成 THEN 结果 SHALL 汇总为一个 LearningBundle artifact
6. WHEN 前端收到 LearningBundle THEN 界面 SHALL 显示增强的 LearningBundleCard，内嵌多个子卡片
7. WHEN LearningBundleCard 显示 THEN 它 SHALL 包含：
   - 学习路线提示（如"先看笔记，再做题，再复习卡片"）
   - 展开/折叠的子卡片（QuizCard, ExplainCard, FlashcardCard）

**实现要点：**
- 新增 `ContentAnalysisSkill`：配置文件 + prompt + handler
- 在 SkillOrchestrator 中添加 `execute_skills_parallel()` 方法
- 修改 LearningBundleSkill 支持吃多个子产物汇总
- 前端新增 `LearningBundleCard` 组件，支持嵌套渲染

**Demo 场景：**
- 输入："这是我今天的微积分课笔记：[长文本]，帮我生成学习材料"
- 流程：ContentAnalysisSkill → [NotesSkill, QuizSkill, FlashcardSkill] 并行 → LearningBundleSkill 汇总
- 输出：完整学习包卡片，包含笔记、5道练习题、8张闪卡

---

## Out of Scope（MVP 不包含）

以下功能在 demo 阶段不实现，但架构支持后续扩展：

- ❌ 多技能 Pipeline（BundleSkill）
- ~~❌ 用户认证系统~~ ✅ **已纳入 Requirement 14**
- ~~❌ 持久化存储（Redis/MongoDB）~~ ✅ **已纳入 Requirement 14（使用 SQLite）**
- ❌ 实时 WebSocket 更新
- ❌ 语音输入/输出
- ❌ 多语言支持
- ❌ Homework Skill、FlashcardSkill 等其他技能
- ❌ 完整的用户画像分析（简化版 mastery_map）
- ❌ 成本监控和预算控制
- ❌ 密码重置/找回功能
- ❌ OAuth 第三方登录（Google/GitHub）
- ❌ 用户头像上传

## Success Metrics

### V1 Demo 成功标准 (已完成)

1. ✅ 用户能在一个界面完成"练习题 → 讲解 → 再练习"的完整学习流程
2. ✅ Intent Router 对明确意图的识别准确率 > 85%
3. ✅ 端到端响应时间 < 5 秒
4. ✅ 系统能记住用户在会话中的主题切换
5. ✅ 代码结构清晰，新增一个 Skill 只需 < 50 行代码
6. ✅ 演示视频能展示核心价值：从工具箱到智能助手的体验提升
7. ✅ 用户能注册/登录，退出后重新登录时自动加载历史偏好和聊天记录
8. ✅ 系统能根据用户历史行为（如连续3次使用闪卡）持久化偏好，影响后续意图识别
9. ✅ 多用户场景：不同用户的数据完全隔离，互不影响

### V2 进阶成功标准 (待实现)

10. 🆕 **模糊意图处理**：用户输入"帮我学习极限"时，系统能返回意图分布（explain 0.7, quiz 0.6, flashcard 0.4），执行主意图并推荐其他选项
11. 🆕 **任务跳跃能力**：用户能连续对话"给我3道题" → "第2题我不会" → "整理成笔记"，系统通过 Memory 记住上下文并正确执行
12. 🆕 **并行执行效率**：用户上传长文本后，系统能同时生成笔记、练习题、闪卡，整体响应时间 < 10秒（比顺序执行节省 40-60% 时间）
13. 🆕 **Planner 决策准确性**：Planner 能根据用户偏好和意图分布生成合理的 ExecutionPlan，包含当前 Skill 和建议的后续 Skills
14. 🆕 **推荐系统有效性**：前端显示的"推荐下一步"按钮点击率 > 30%，证明推荐的相关性
15. 🆕 **学习包完整性**：Manus 模式生成的学习包包含至少3种类型的学习材料（笔记、练习题、闪卡），且内容连贯
16. 🆕 **Token 成本优化**：并行执行模式相比顺序调用多个 Skill，token 消耗减少 40-60%

---

## V3: 上下文管理与成本优化 (基于 Manus 启发的架构改进)

### Requirement 12: KV 缓存优化

**User Story:** 作为系统，我希望通过 KV 缓存优化重复上下文的处理，从而降低延迟和token成本（针对输入输出比100:1的Agent场景，成本可降低近10倍）。

#### Acceptance Criteria

1. WHEN 用户发起多轮对话 THEN 系统 SHALL 识别并缓存重复的上下文前缀（如system prompt、历史对话）
2. WHEN 使用缓存命中 THEN 系统 SHALL 跳过Prefill阶段，直接使用缓存的KV状态
3. WHEN 输入token与输出token比例 >= 100:1 THEN 系统 SHALL 自动启用缓存优化
4. WHEN 缓存启用后 THEN 平均响应延迟 SHALL 降低 30-50%
5. WHEN 缓存启用后 THEN 输入token成本 SHALL 降低 80-90%（对于高输入比场景）

### Requirement 13: 文件系统作为外部记忆

**User Story:** 作为Agent，我希望将文件系统作为外部长期记忆，而不是依赖模型上下文存储所有历史，从而实现无限容量、持久化和结构化的记忆管理。

#### Acceptance Criteria

1. WHEN Agent 需要记录信息 THEN 系统 SHALL 提供 `write_memory` 工具将内容写入文件系统
2. WHEN Agent 需要回忆信息 THEN 系统 SHALL 提供 `read_memory` 工具从文件系统检索内容
3. WHEN 存储学习材料 THEN 系统 SHALL 使用结构化格式（JSON/Markdown）便于检索和Agent理解
4. WHEN 文件系统存储使用 THEN 上下文窗口 SHALL 只保留当前任务相关的摘要，历史详情存于文件
5. WHEN Agent 主动管理记忆 THEN 系统 SHALL 学会何时写入、何时读取、如何组织信息
6. WHEN 记忆容量 THEN 文件系统存储 SHALL 无大小限制（相比上下文窗口的固定限制）

### Requirement 14: 可恢复压缩（指针引用）

**User Story:** 作为Agent，我希望用轻量级"指针"（如文件路径、URL、ID）代替庞大的原始信息，从而实现100%信息保真的无损"压缩"。

#### Acceptance Criteria

1. WHEN 生成大型学习材料（如长文档、图片、音频）THEN 系统 SHALL 存储到文件系统并返回唯一标识符
2. WHEN 上下文中引用内容 THEN 系统 SHALL 使用指针（如 `file://notes/ww2_history.md`）而非完整内容
3. WHEN Agent 需要访问内容 THEN 系统 SHALL 通过指针恢复完整信息（100%保真）
4. WHEN 指针引用使用 THEN 上下文token消耗 SHALL 降低 90%+（对于大型内容）
5. WHEN 多次引用同一内容 THEN 系统 SHALL 重用指针，避免重复传输

### Requirement 15: 保留错误尝试（从失败中学习）

**User Story:** 作为Agent，我希望在上下文中完整保留失败记录，从而通过观察错误隐式更新内部信念，避免重复犯错。

#### Acceptance Criteria

1. WHEN 工具调用失败 THEN 系统 SHALL 完整保留失败记录（Action + Error Observation）
2. WHEN 继续对话 THEN 系统 SHALL 将失败记录追加到上下文末端（而非隐藏）
3. WHEN 模型看到失败记录 THEN 它 SHALL 调整后续行为，避免相同错误
4. WHEN 成功纠正错误 THEN 系统 SHALL 同时保留失败和成功记录（形成完整的学习轨迹）
5. WHEN 错误记录数量 THEN 系统 SHALL 保留最近的5-10条失败（避免上下文过载）

### Requirement 16: 预填充引导模式（Prefill Guidance）

**User Story:** 作为系统，我希望通过在 `<...>assistant` 位置预先拼接不同文本，精确引导模型行为（自动/必需/指定三种模式）。

#### Acceptance Criteria

1. WHEN 使用自动模式 THEN 系统 SHALL 在助手位置预填充 `<...>assistant`，让模型自由响应
2. WHEN 使用必需模式 THEN 系统 SHALL 预填充 `<...>assistant<tool_code>`，强制模型调用工具
3. WHEN 使用指定模式 THEN 系统 SHALL 预填充 `<...>assistant<tool_code>specific_tool(...)`，指定具体工具和参数
4. WHEN 预填充生效 THEN 模型输出 SHALL 严格遵循预填充的引导格式
5. WHEN 需要强制行为 THEN 系统 SHALL 优先使用必需/指定模式而非依赖Prompt指令

### Requirement 17: 动态计划管理（Todo追加架构）

**User Story:** 作为Agent，我希望通过"只追加"的todo管理机制，将最重要的导航信息始终置于上下文末端（注意力最强区域），从而高效对抗遗忘。

#### Acceptance Criteria

1. WHEN Agent 制定计划 THEN 系统 SHALL 生成结构化 `todo.md` 并追加到上下文末端
2. WHEN 计划更新 THEN 系统 SHALL 重写整个 `todo.md` 并再次追加到末端（而非修改原处）
3. WHEN 上下文窗口 THEN 最新的计划 SHALL 始终位于注意力最强的"近期范围"
4. WHEN 任务进行中 THEN Agent SHALL 能实时看到当前任务、已完成任务、待办任务
5. WHEN todo追加后 THEN 系统 SHALL 利用注意力特性，让模型专注于最新计划状态

### Requirement 18: 目标漂移防护

**User Story:** 作为Agent，我希望在长任务链（如10+步骤）中保持目标聚焦，避免因上下文稀释导致的"目标漂移"问题。

#### Acceptance Criteria

1. WHEN 任务链长度 > 10步 THEN 系统 SHALL 每5步重写一次高层目标到上下文末端
2. WHEN 目标重写 THEN 系统 SHALL 包含：原始用户请求、当前进度、剩余关键任务
3. WHEN 检测到偏离 THEN 系统 SHALL 通过 Planner 重新评估当前行为是否符合原始目标
4. WHEN 长任务完成率 THEN 使用目标防护的任务完成率 SHALL > 85%（相比无防护的 < 60%）
5. WHEN Agent行为 THEN 系统 SHALL 进化为会计划、会回顾、会纠偏的"项目经理"模式

### V3 成功标准

17. 🚀 **KV缓存效果**：对于多轮对话场景，响应延迟降低 30-50%，输入token成本降低 80%+
18. 🚀 **文件系统集成**：Agent 能主动使用 read/write 工具管理外部记忆，上下文窗口仅保留当前任务摘要
19. 🚀 **指针压缩率**：大型内容（>1000 tokens）通过指针引用后，上下文占用降低 90%+
20. 🚀 **错误学习能力**：相同类型错误的重复率 < 10%（相比无错误记录的 > 40%）
21. 🚀 **预填充准确性**：强制工具调用的成功率 > 95%（必需/指定模式）
22. 🚀 **长任务完成率**：10+ 步骤任务的完成率 > 85%（使用todo追加 + 目标防护）
23. 🚀 **目标一致性**：长任务中偏离原始目标的步骤 < 15%

