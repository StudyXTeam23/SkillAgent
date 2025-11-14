Agent Skill 系统架构设计文档说明
StudyX 架构升级：从工具集到 Skill Agent

核心目标：在用户体验提升的前提下，通过高效意图分析与Skill 化架构，实现 token 成本与开发/运营成本的双重下降。


---
1. 为什么要做 Skill Agent？

1.1 用户体验痛点：现在的 StudyX 太“像工具箱”

当前 StudyX 已经有多个成熟工具：
- AI 作业助手
- AI 课堂笔记生成器
- AI 测验
- AI 抽认卡
- AI 导师
- …
  
问题在于：这些工具彼此独立，用户必须“自己决定用哪个”。

典型体验：
- 想先“解一道题”，再“听讲解”，最后“做几道练习”  
- 现在需要在 3 个工具之间来回跳转  
- 每一步都要回到首页重新选择功能
  
用户的学习路径被切成多段，每一步都需要人为判断和操作，体验支离破碎。


---
1.2 意图识别痛点：系统不知道“用户到底想干嘛”

当前系统不理解：
- 同一句话可能包含多个意图：
  - 「帮我解这题，并顺便讲讲这个概念，再给我出几道练习」
- 多轮对话中，用户意图在不断变化：
  - 第 1 轮：要解题
  - 第 2 轮：要讲解
  - 第 3 轮：要测验
    
现在的 StudyX：
- 完全依赖用户自己判断并切换工具  
- 系统不会“记住”上一轮的任务，更不会自动规划学习路径
  

---
1.3 成本痛点：模型 token & 内部开发成本

模型 token 成本：
- MCP 式“大 Agent”需要在同一个 Prompt 里塞：
  - 所有工具的说明
  - 大量对话历史
  - 课程内容
- 每轮调用都在重复发送大量、与当前任务无关的信息  
- token 消耗高，且难以精细控制
  
开发 & 运营成本：
- 新增一个工具 = 新页面 + 新后端接口 + 一套独立 Prompt  
- 工具间逻辑难共享，代码与 Prompt 难维护  
- 高级功能（例如“笔记 + 抽认卡 + 测验”组合学习）需要手写专门逻辑，维护成本高

---
2. StudyX vs Skill Agent：三个真实场景对比

场景 1：解题 + 讲解 + 测验（多轮任务）

现在（工具集模式）：
1. 学生上传题目 → 使用「作业助手」  
2. 想听讲解 → 回首页 → 找「AI 导师」入口  
3. 想做练习题 → 再回首页 → 找「AI 测验」  
  
学习链路被拆成多段，每一步都依赖学生自己进行行为编排。

Skill Agent 模式：
同一个课程对话框里，学生只需自然对话：
1. 「帮我解这题」 → 意图 = homework_help → 调 HomeworkSkill  
2. 「能讲讲这个概念吗？」 → 意图 = tutor_explain → 调 TutorSkill  
3. 「再给我几道类似的练习题」 → 意图 = quiz → 调 QuizSkill  
  
体验改进：多轮任务在一个上下文里自动衔接，学生只管学习，不用来回跳工具。  
成本侧：每个 Skill 用的是精简 Prompt，只包含当前任务的规则，token 显著下降。

---
场景 2：课堂录音 → 笔记 + 抽认卡 + 测验（学习包）

现在：
1. 学生用「课堂笔记生成器」生成一版笔记  
2. 想要抽认卡 → 回工具列表 → 使用「抽认卡」  
3. 想要测验 → 再回列表 → 使用「AI 测验」  
  
每一个步骤都是独立的调用与界面，系统不会自动组合。

Skill Agent：
学生只说一句：

「这是今天的录音，帮我整理成学习资料并给我练习题。」

Course Agent 自动：
- 通过 Intent Router 判断：note_taking + flashcards + quiz  
- 按顺序调用：
  - LectureNotesSkill → 结构化笔记  
  - FlashcardSkill → 关键概念抽认卡  
  - QuizSkill → 针对本节课内容的测验  
- 最终打包成一个「学习包」返回前端
  
体验改进：一次输入 → 完整学习链路结果；中间步骤全部对用户隐藏。  
成本侧：多个 Skill 共享课程检索结果与状态，不需要每个工具都重新查与重构上下文。

---
场景 3：课程级记忆与个性化学习

现在：
- 每个工具都是“无状态”的  
- StudyX 不知道：
  - 这个学生在哪些知识点上长期薄弱
  - 更偏好哪种学习形式（文字讲解 vs 抽认卡 vs 测验）
- 很难做个性化推荐与学习路径规划
  
Skill Agent：
- 为每门课维护 StudentCourseState：
  - mastery_map（知识点掌握度）
  - 错题记录
  - 常用工具 / 学习偏好
  - 最近学习主题
    
当学生说：
「下周要考试，帮我重点复习一下。」  

Course Agent 会：
- 从 mastery_map 找到薄弱知识点  
- 默认选择该学生偏好的输出形式（例如 抽认卡 + 测验）  
- 自动规划复习内容，优先覆盖弱项
  
体验改进：表现为“这个 AI 很懂我正在学什么 & 哪里不会”。  
业务侧：更强的留存与付费理由（真正的个性化学习助手）。

---
3. 目标架构：如何在体验、意图与成本之间取得平衡？

3.1 核心设计：Course Agent + Skill Registry

Course Agent（每门课一个）负责三件事：
1. 高效意图分析（Intent Router）
  - 使用轻量模型 & 精简 Prompt  
  - 每轮判断当前输入属于：
    - homework_help / note_taking / quiz / flashcards / tutor / podcast / bundle / …
  - 输出结构化意图结果（intent + topic + target_artifact）
    
2. 记忆管理（Memory Manager）
  - 维护 StudentCourseState：
    - 知识点掌握度  
    - 偏好输出形式  
    - 错题记录与最近学习任务  
  - 为各 Skill 提供“学生画像”摘要，用极少 token 提升个性化质量
    
3. 技能编排（Skill Orchestrator）
  - 读取 Skill Registry（技能注册表）  
  - 基于意图、学生状态、成本策略选择合适的 Skill（或组合多个）  
  - 控制调用顺序及上下文复用

---
3.2 Skill Registry：成本与维护的核心抓手

每个 Skill 抽象为一条配置：
- 能力描述：做什么  
- 输入 / 输出结构  
- 需要的课程上下文（课件、作业、录音）  
- 使用的模型（便宜 or 贵）  
- 成本画像（cost_profile）  
- 延迟画像（latency_profile）  
- 是否可组合使用（composable）
  
好处：
- 对前端：不必新增一堆工具页，也可以增量接入新能力  
- 对后端：新增 Skill ≈ 新增一个配置 + Prompt 模板，降低开发成本  
- 对成本控制：可以显式地为每类 Skill 选用不同的模型与上下文长度，从架构上控制 token 消耗

3.3 StudyX Skill Agent 整体架构（问题导向 / 通用学习场景）图
skill_agent_demo/prd_document/architecture_img/image.png

精简核心架构图（通用解题 / 学习问题）
skill_agent_demo/prd_document/architecture_img/image-2.png

3.3.1 架构动线说明
我们先把“整套东西是怎么跑起来的”讲清楚，用一个很具体的场景来走一遍线：
用户在 StudyX 里说：
「我想练一练微积分里极限这块，给我几道题。」
下面这段就是可以贴在两张 PlantUML 图后面的 架构动线说明。

---
1️⃣ 用户 → StudyX Chat UI
1. 用户在 统一对话入口（StudyX Chat UI） 输入：
“我想练一练微积分里极限这块，给我几道题。”
2. 前端只做一件事：
  把这句话 + 用户 ID + 会话 ID 一起发给后端的 StudyX Agent。
对应图里的组件：
- User → StudyX Chat UI → StudyX Agent / Intent Router

---
2️⃣ Intent Router（意图分类器）：这句话到底想干嘛？
3. Intent Router 接收到请求后，会看三类信息：
  1. 当前这句话
  2. 最近几轮对话（SessionContext 的简要摘要）
  3. 用户学习画像的一个简短概述（UserLearningProfile 摘要）
4. 它输出一个结构化结果（不做内容生产，只做分类），类似：
{
  "intent": "quiz",
  "topic": "微积分-极限",
  "target_artifact": "quiz_set",
  "confidence": 0.86
}
5. 如果置信度足够高，就把这个 JSON 交给下一步的 Skill Orchestrator；
如果很低，可以让 Agent 反问一句：“你是想要练习题，还是想要讲解？”
对应组件：
- Intent Router
- 读：SessionContext、UserLearningProfile（通过 Memory Manager 间接获取）
- 写：给 Skill Orchestrator 一个清晰的“意图结果 JSON”

---
3️⃣ Memory Manager：了解这个人 & 这次对话
6. Memory Manager 此时会做两件事：
  1. 读取用户长期画像（UserLearningProfile）：
    1. 比如：这个用户在“极限”这部分一直做错比较多
  2. 读取当前会话的短期状态（SessionContext）：
    1. 比如：上一轮刚让系统讲过一次“极限的定义”
7. Memory Manager 会把这些信息做一个 很短的摘要 给 Skill Orchestrator，比如：
“用户在‘极限’掌握度偏弱，且刚刚看过一次极限定义的讲解，更适合给基础练习题。”
对应组件：
- Memory Manager
- 读写：UserLearningProfile、SessionContext

---
4️⃣ Skill Orchestrator（功能编排模块设计文档）：选对 Skill，用好 Skill
8. Skill Orchestrator 拿到：
  1. Intent Router 的结果：intent = quiz，topic = 微积分-极限
  2. Memory 的摘要：用户在微积分-极限上偏弱
  3. 用户原始输入
9. 它去 Skill Registry （功能注册数据设计说明文档） 查一查：
  1. 有没有 intent_tags 包含 quiz 的 Skill？
  2. 找到：QuizSkill，并知道它的：
    1. 输入需要：topic / 可选 difficulty / num_questions
    2. 输出是：结构化题目列表
    3. 使用的模型：例如 gemini-2.5-flash-lite
    4. 是否需要题库 / 资料（例如从 Problem / Content Store 获取历史题目）
10. Orchestrator 决定调用 QuizSkill，并根据 Memory 生成一个调用参数，例如：
{
  "topic": "微积分-极限",
  "difficulty": "easy",
  "num_questions": 5,
  "user_id": "u_123"
}
11. 如果未来要更复杂一点（比如“先给 2 道例题解答，再出 3 道练习”），Orchestrator 也可以按 pipeline 调多个 Skill，这里我们先用单 Skill 调用说明。
对应组件：
- Skill Orchestrator
- 读：Skill Registry、Problem / Content Store、Memory Manager 摘要
- 调：QuizSkill

---
5️⃣ QuizSkill：真正“造题”的地方
12. QuizSkill 是一个 Skill 实现模块，它知道如何基于 topic + 用户信息去生成题目。它内部会：
- 根据 topic = 微积分-极限
- 可能从 Problem / Content Store 拉一些参考题目（题库 / 用户错题 / 之前用过的题）
- 拼一个相对精简的 prompt，调用 LLM Service：
  - 模型由 Skill Registry 中的 models.primary 决定
13. LLM 在这里完成真正的“出题工作”，输出一个结构化结果，例如：
{
  "questions": [
    { "id": "q1", "stem": "...", "options": [...], "answer": "B", "explanation": "..." },
    ...
  ]
}
14. QuizSkill 对结果做一下简单校验（有无题、字段是否完整），再把结果返回给 Skill Orchestrator。
对应组件：
- QuizSkill（属于 Skills 集合）
- 读：Problem / Content Store
- 调：LLM Service

---
6️⃣ Orchestrator 聚合结果 → Memory 更新
15. Skill Orchestrator 接到 QuizSkill 的返回结果后：
- 包装成统一的“学习结果结构”，比如 quiz_set
- 告诉 Memory Manager：
  - 用户刚领了一套“微积分-极限”的基础练习
  - 可以记录：这次做题属于“极限强化练习”
16. Memory Manager 更新：
- SessionContext：这轮对话的主题和产物
- UserLearningProfile：记录一次“极限的练习行为”（方便之后做更全面的掌握度分析）
对应组件：
- Skill Orchestrator
- Memory Manager 更新 UserLearningProfile、SessionContext

---
7️⃣ 返回前端：渲染为真正可做的题
17. 最终，StudyX Agent 将结果返回给前端 StudyX Chat UI，格式大概类似：
{
  "type": "quiz_set",
  "title": "微积分·极限基础练习",
  "questions": [ ... ],
  "meta": { "topic": "微积分-极限", "difficulty": "easy" }
}
18. 前端根据 type = quiz_set，渲染为“可答题卡片界面”：
- 每道题一个卡片
- 支持用户作答
- 可以再触发后续交互，比如“查看解析”、“换一套”、“提升难度”
对应组件：
- StudyX Agent → StudyX Chat UI
- 前端渲染题目列表 / 答题交互

---
8️⃣ 用户继续对话：新动线再次启动
19. 用户做完题后可以继续说：
“我这几道题错得挺多的，能给我讲讲这些题背后的核心概念吗？”
20. 新的一句话又进入同样的架构动线：
- Intent Router 这次可能识别为 intent = tutor_explain
- Skill Orchestrator 改为调用 TutorSkill 或 ExplainSkill
- 但会利用刚才这一轮练习结果（错题）作为输入

3.4 总结：真实开发落地需要的是这些“模块级”的内容： 
1. Intent Router API Intent Router（意图分类模块设计文档）
2. Memory Manager 数据结构 Memory Manager（记忆管理模块设计文档）
3. Skill Registry schema Skill Registry Schema（功能注册数据模块设计文档）
4. Skill Orchestrator pipeline 逻辑 Skill Orchestrator（功能编排模块设计文档）
5. 每个 Skill 的实现签名 Skills 的统一实现接口说明文档

---
4. 预期结果：体验、意图、成本三线优化

4.1 用户体验显著提升
- 一个课程，一个对话入口，覆盖解题 / 笔记 / 测验 / 抽认卡 / 导师讲解 / Podcast…  
- 学习过程连续：不再需要在工具间跳来跳去  
- 系统“看起来知道用户在学什么、哪里不会、接下来该干嘛”
  
4.2 意图识别变成“低成本、高准确率”的基础设施
- 轻量 Intent Router 每轮只处理当下对话 + 精简状态摘要  
- 不再用一个超级大 Prompt 让模型“瞎猜用哪个工具”  
- 意图结果是结构化 JSON，后续逻辑更稳定、更易监控
  
4.3 降本增效：token 成本 & 开发运维成本同步下降
token 成本：
- 工具说明从“大杂烩”变成“按需加载的 Skill Prompt”  
- 课程内容通过检索提供，而不是整段硬塞  
- 多个 Skill 在一次学习流程中可以复用相同的检索结果和状态摘要  
- 对意图识别可使用便宜模型，整体调用结构更细腻可控
  
开发 & 运营成本：
- 新能力 = 新 Skill + Registry注册信息，不需要重新设计一个完整工具  
- Code & Prompt 以 Skill 为单位封装，易于测试与调优  
- 基础设施（记忆、检索、意图路由）对所有 Skill 复用，减少重复造轮子  

---
5. 总结
- 为什么需要 Skill Agent？
因为现在的 StudyX 像一个“工具商店”，而不是一个“懂课程、懂学生的 AI 学习伙伴”。
- Skill Agent 解决了什么？
通过 Course Agent + Intent Router + Skill Registry + Memory，让系统能在一个入口里自动理解用户意图、自动选择与组合技能，并基于课程记忆提供个性化结果。
- 收益在哪里？  
  - 学生：体验更顺滑，真正感觉“被教 & 被带着走”  
  - 产品：形成学习路径、课程记忆与个性化服务的差异化壁垒  
  - 技术 & 运营：token 成本下降，功能扩展更快，维护复杂度降低
    
这不是在增加一个“新功能”，而是在为 StudyX 升级一套 更聪明、更省钱、更好用的底层架构。