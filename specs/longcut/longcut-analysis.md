# LongCut — 深度源码分析

## 一、项目概述

LongCut（前身 TLDW）是一个 AI 驱动的 YouTube 长视频学习工具。
用户粘贴一个 YouTube 链接，系统自动提取字幕、生成精华片段（Highlight Reels）、AI 摘要、带时间戳的问答，以及笔记工作区，让用户在几分钟内吸收一个小时视频的核心内容。

项目地址：<https://github.com/SamuelZ12/longcut>

---

## 二、技术栈

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| **前端框架** | Next.js 15 (App Router) + React 19 | Turbopack 构建，Server/Client Components 混合 |
| **语言** | TypeScript 5 (strict mode) | 全栈统一语言 |
| **样式** | Tailwind CSS v4 + PostCSS | 静态 CSS 生成，零 CSS-in-JS 运行时开销 |
| **组件库** | shadcn/ui (Radix UI 原语) | 可组合的无头组件 |
| **数据库** | PostgreSQL (Supabase 托管) | PostGREST 查询 + SQL 迁移 |
| **认证** | Supabase Auth | Email OTP + OAuth (Google/GitHub) |
| **AI — 主模型** | xAI Grok 4 (`grok-4-1-fast-non-reasoning`) | 结构化 JSON 输出 |
| **AI — 备选模型** | Google Gemini (级联：`gemini-2.5-flash-lite` → `gemini-3-flash` → `gemini-3-pro`) | 自动降级回退 |
| **字幕获取** | Supadata API | YouTube 字幕提取服务 |
| **支付** | Stripe | 订阅 + 一次性充值 |
| **邮件** | Postmark | 事务性邮件（欢迎、月报、Newsletter） |
| **部署** | Vercel | Serverless Functions + Edge Middleware |

---

## 三、架构设计

### 3.1 整体架构

LongCut 是一个**单体全栈 Next.js 15 应用**，采用 App Router 架构，API Routes 充当后端服务层。

```
┌───────────────────────────────────────────────────────────────┐
│                      Next.js 15 Application                   │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│   ┌──────────────┐    ┌────────────┐    ┌─────────────────┐  │
│   │   UI 层       │    │ Auth 上下文 │    │ 播放命令中心     │  │
│   │  React 19     │◄──►│ Supabase   │    │ PlaybackCommand │  │
│   │  shadcn/ui    │    │ AuthProvider│    │ 集中式状态管理   │  │
│   └──────┬───────┘    └────────────┘    └────────┬────────┘  │
│          │ csrfFetch                              │           │
│   ┌──────▼────────────────────────────────────────▼────────┐ │
│   │               API Route Handlers (Next.js)              │ │
│   │  /api/video-info  /api/transcript  /api/generate-topics │ │
│   │  /api/generate-summary  /api/chat  /api/notes           │ │
│   │  /api/stripe/*    /api/webhooks/stripe  ...             │ │
│   └──────┬──────────────────────────────────────────────────┘ │
│          │ withSecurity() 中间件                              │
│   ┌──────▼──────────────────────────────────────────────────┐ │
│   │               安全与业务逻辑层                             │ │
│   │  CSRF 校验 · 速率限制 · 认证检查 · 订阅管理 · 审计日志      │ │
│   └──────┬──────────────────────────────────────────────────┘ │
│          │                                                     │
│   ┌──────▼───────┐  ┌──────────┐  ┌────────────────────────┐ │
│   │  AI 处理层    │  │ 持久化层  │  │     外部服务层          │ │
│   │  ├ Prompts   │  │ Supabase │  │  Stripe · Supadata     │ │
│   │  ├ Grok      │  │ PostgreSQL│  │  YouTube · Postmark    │ │
│   │  ├ Gemini    │  │          │  │  Google Translate      │ │
│   │  └ QuoteMatcher│ │          │  │                        │ │
│   └──────────────┘  └──────────┘  └────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```

### 3.2 核心架构模式

**1. AI Provider 抽象层 — 注册表模式**

```
lib/ai-providers/
├── index.ts           # 统一入口：generateStructuredContent()
├── registry.ts        # Provider 注册表，工厂模式
├── grok-adapter.ts    # xAI Grok 适配器
└── gemini-adapter.ts  # Google Gemini 适配器（含级联回退）
```

所有 AI 调用通过 `generateStructuredContent(params)` 统一入口，对上层屏蔽 Provider 差异。
Zod Schema 在运行时转换为各 Provider 的原生 JSON Schema 格式。

**2. 安全中间件装饰器 — `withSecurity()`**

每个 API Route Handler 都被 `withSecurity()` 包装，支持安全预设：
- `PUBLIC` — 仅速率限制
- `AUTHENTICATED` — CSRF + 认证 + 速率限制
- `AUTHENTICATED_READ_ONLY` — 认证 + 速率限制（无 CSRF）
- `STRICT` — 全部安全检查 + 严格的 body size 限制

**3. 播放命令模式 — 集中式控制通道**

视频播放器的所有交互通过 `PlaybackCommand` 单一通道分发：

| 命令 | 说明 |
|------|------|
| `SEEK` | 跳转到绝对时间点 |
| `PLAY_TOPIC` | 播放某个精华片段 |
| `PLAY_SEGMENT` | 播放指定片段区间 |
| `PLAY_ALL` | 按顺序自动播放全部精华 |
| `PLAY_CITATIONS` | 播放 AI 对话中引用的片段 |
| `PLAY` / `PAUSE` | 基础播放控制 |

**4. 异步生命周期管理 — AbortManager**

`lib/promise-utils.ts` 提供：
- `AbortManager` — 协调多个并发请求的取消
- `backgroundOperation()` — 非阻塞后台任务（保存、建议生成）
- `safePromise()` — Go 风格错误处理 `[data, error]` 元组

**5. 引用匹配引擎 — 多策略级联**

`lib/quote-matcher.ts` 实现三级匹配策略：
1. **精确匹配** — Boyer-Moore 子串搜索
2. **规范化匹配** — 忽略大小写和标点
3. **模糊匹配** — 3-gram Jaccard 相似度（阈值 0.8）

将 AI 返回的引用文本精确映射到字幕的 segment index + character offset，实现像素级高亮。

---

## 四、数据流

### 4.1 主流程：从 URL 到完整分析

```
用户粘贴 YouTube URL
        │
        ▼
路由跳转 /analyze/[videoId]
        │
        ▼
┌───────────────────────────────────┐
│         并行获取（Phase 1）         │
│  ├─ /api/video-info  → 标题、作者、时长、缩略图  │
│  └─ /api/check-video-cache → 是否有缓存分析      │
└───────┬───────────────────────────┘
        │
        ▼
  命中缓存？──── 是 ────→ 直接加载，跳到展示
        │ 否
        ▼
/api/transcript → Supadata API 获取字幕
        │
        ▼  格式检测 → 时间单位归一化 → 短句合并
        │
        ▼
┌───────────────────────────────────┐
│     并行 AI 生成（Phase 2）        │
│  Promise.allSettled() 全部并行     │
│                                   │
│  1. /api/generate-topics          │
│     Smart 模式：全文一次性分析      │
│     Fast 模式：5 分钟窗口分块处理   │
│     → Topic[] + 候选池             │
│                                   │
│  2. /api/generate-summary         │
│     → 4-6 条 Key Takeaways        │
│                                   │
│  3. /api/suggested-questions      │
│     → 5-7 条讨论问题（后台非阻塞）  │
│                                   │
│  4. /api/top-quotes               │
│     → 精选引用（后台非阻塞）        │
└───────┬───────────────────────────┘
        │  数据逐步到达，UI 渐进渲染
        ▼
后台自动保存到 video_analyses 表
并记录 video_generations 用于计费
```

### 4.2 AI 对话流

```
用户输入问题
    │
    ▼
速率限制检查（认证用户/匿名用户不同限额）
    │
    ▼
POST /api/chat
├─ 上下文构建：[话题列表] + [对话历史（最近 5 轮）] + [完整带时间戳字幕]
├─ AI Provider 生成回答
├─ 解析响应中的时间戳引用 [MM:SS]
└─ 引用匹配 → segment index + character offset
    │
    ▼
客户端高亮对应字幕片段，支持点击跳转播放
```

### 4.3 主题探索流（Theme-based）

```
Smart 模式生成 → 候选池（10-15 个候选话题）
    │
    ▼
从候选池提取 Theme 关键词（去重 + 停用词过滤）
    │
    ▼
用户选择 Theme（如 "Decision Making"）
    │
    ▼
POST /api/generate-topics + theme + excludeTopicKeys
    │
    ▼
AI 从候选池中筛选匹配主题的话题
    │
    ▼
结果缓存到客户端 themeTopicsMap，再次选择时直接展示
```

---

## 五、数据库设计

### 核心表结构

```
profiles                         video_analyses
├─ id (PK, → auth.users)        ├─ id (PK, uuid)
├─ email                         ├─ youtube_id (UNIQUE)
├─ stripe_customer_id            ├─ title, author, duration
├─ subscription_tier             ├─ transcript (jsonb)
├─ subscription_status           ├─ topics (jsonb)
├─ topup_credits                 ├─ summary (jsonb)
├─ newsletter_subscribed         ├─ suggested_questions (jsonb)
└─ created_at/updated_at         └─ model_used
                                          │
         ┌────────────────────────────────┤
         ▼                                ▼
   user_videos                     user_notes
   ├─ user_id (FK → profiles)     ├─ user_id (FK → auth.users)
   ├─ video_id (FK → analyses)    ├─ video_id (FK → analyses)
   ├─ accessed_at                  ├─ source ('chat'|'takeaways'|'transcript'|'custom')
   ├─ is_favorite                  ├─ note_text
   └─ UNIQUE(user_id, video_id)   └─ metadata (jsonb)

video_generations                  rate_limits
├─ user_id / identifier            ├─ key (用途标识)
├─ youtube_id                      ├─ identifier (用户 ID 或 IP 哈希)
├─ counted_toward_limit            └─ timestamp
├─ subscription_tier
└─ created_at

stripe_events (幂等)              topup_purchases (充值记录)
├─ event_id (PK)                  ├─ user_id
└─ created_at                     ├─ stripe_payment_intent_id
                                  ├─ credits_purchased
audit_logs (审计)                  └─ amount_paid
├─ user_id, action
├─ resource_type, resource_id
├─ details (jsonb)
└─ ip_address, user_agent
```

**关键数据库函数：**
- `increment_topup_credits(user_id, amount)` — 原子增加充值余额
- `consume_topup_credit(user_id)` — 消费单个充值额度（原子操作，返回 boolean）
- `get_usage_breakdown(user_id, start, end)` — 查询计费周期内的用量明细

**Row Level Security (RLS)：**
所有用户数据表启用 RLS，用户只能访问自己的数据。Service Role 用于后端管理操作绕过 RLS。

---

## 六、API 全景

### 视频处理

| 路由 | 方法 | 功能 | 认证 |
|------|------|------|------|
| `/api/video-info` | POST | 获取视频元数据 | 公开 |
| `/api/transcript` | POST | 获取字幕 | 公开 |
| `/api/check-video-cache` | POST | 检查缓存分析 | 公开 |
| `/api/video-analysis` | POST | 完整分析生成 | 公开（限速） |
| `/api/update-video-analysis` | PUT | 更新已有分析 | 公开 |
| `/api/link-video` | POST | 关联匿名视频到用户 | 需认证 |

### AI 生成

| 路由 | 方法 | 功能 | 认证 |
|------|------|------|------|
| `/api/generate-topics` | POST | 生成精华片段 | 公开（限速） |
| `/api/generate-summary` | POST | 生成摘要/要点 | 公开（限速） |
| `/api/chat` | POST | AI 对话（带引用） | 公开（限速） |
| `/api/suggested-questions` | POST | 生成讨论问题 | 公开 |
| `/api/top-quotes` | POST | 提取精选引用 | 公开 |
| `/api/translate` | POST | 翻译文本 | 公开 |

### 用户数据

| 路由 | 方法 | 功能 | 认证 |
|------|------|------|------|
| `/api/notes` | GET/POST/DELETE | 笔记 CRUD | 需认证 |
| `/api/notes/all` | GET | 全部笔记 | 需认证 |
| `/api/notes/enhance` | POST | AI 笔记增强 | 需认证 |
| `/api/toggle-favorite` | POST | 收藏/取消收藏 | 需认证 |
| `/api/check-limit` | POST | 预检用量限制 | 公开 |

### 支付

| 路由 | 方法 | 功能 | 认证 |
|------|------|------|------|
| `/api/stripe/create-checkout-session` | POST | 创建结账会话 | 需认证 |
| `/api/stripe/create-portal-session` | POST | 账单管理门户 | 需认证 |
| `/api/webhooks/stripe` | POST | Stripe Webhook | 签名验证 |
| `/api/subscription/status` | GET | 订阅状态查询 | 需认证 |

---

## 七、安全架构

LongCut 采用**纵深防御**策略，六层安全机制：

| 层级 | 机制 | 实现 |
|------|------|------|
| **1. CSP** | Content Security Policy | Middleware 注入，白名单 YouTube/Supabase/Stripe 域名 |
| **2. CSRF** | 双重提交 Cookie 模式 | 32 字节加密随机 token，HttpOnly + Secure + SameSite=Strict |
| **3. 速率限制** | 数据库驱动 | `rate_limits` 表按用户/IP 追踪，滑动窗口计数 |
| **4. 输入校验** | Zod Schema | 所有 API 入参经 Zod 验证，YouTube ID 格式校验 |
| **5. 内容净化** | DOMPurify | 用户生成内容的 XSS 防护 |
| **6. 审计追踪** | audit_logs 表 | 记录未授权访问、限速超标、CSRF 违规事件 |

---

## 八、核心功能实现细节

### 8.1 精华片段生成 — 双模式

**Smart 模式（深度分析）：**
- 全文字幕一次性送入 AI
- 生成 5 个精华片段 + 10-15 个候选话题池
- 从候选池提取 Theme 关键词供用户二次探索
- 适合追求质量的场景

**Fast 模式（速度优先）：**
- 字幕按 5 分钟窗口分块（45 秒重叠防止切断）
- 每个分块独立生成 2 个候选
- 跨分块去重后精选 Top 5
- 适合 30 分钟以上的长视频

### 8.2 引用匹配引擎

AI 返回的引用文本需要精确映射回原始字幕：

```
AI 输出："The key insight is..." [02:15-03:30]
              │
              ▼
        Boyer-Moore 精确搜索
              │ 未命中
              ▼
        规范化搜索（忽略大小写/标点）
              │ 未命中
              ▼
        3-gram Jaccard 模糊匹配（阈值 0.8）
              │
              ▼
        映射到 segmentIdx + charOffset
              │
              ▼
        UI 精确高亮对应文字
```

### 8.3 AI 对话系统

- 上下文窗口：完整字幕 + 话题列表 + 最近 5 轮对话历史
- AI 必须以 JSON 格式返回 `{ answer, timestamps[] }`
- 时间戳引用自动映射到字幕片段
- 支持多语言（用户可选择目标语言，AI 以该语言回答）

### 8.4 笔记系统

四种来源类型：
- `transcript` — 从字幕中选取文字创建
- `chat` — 从 AI 对话回答中保存
- `takeaways` — 从摘要要点中勾选
- `custom` — 用户自由输入

每条笔记携带 metadata（时间戳、segment index、来源上下文），支持跨视频汇总查看。

### 8.5 订阅与计费

| 层级 | 额度 | 价格 |
|------|------|------|
| Free | 3 视频/月 | 免费 |
| Pro | 100 视频/月 | $9.99/月 或 $99.99/年 |
| Top-up | +20 视频（一次性） | $2.99 |

计费周期：
- Free 用户：从注册日起滚动 30 天
- Pro 用户：Stripe 订阅周期 `period_start` → `period_end`

缓存命中不计入配额（`counted_toward_limit = false`）。

---

## 九、解决的用户痛点

### 痛点 1：长视频信息密度低

一个 60 分钟的视频，真正高价值的内容可能只有 10-15 分钟。
用户被迫线性观看，大量时间浪费在铺垫、重复和过渡内容上。

**LongCut 方案：** AI 精华片段提取，自动识别高信息密度段落，用户只看精华。

### 痛点 2：缺乏结构化导航

YouTube 原生只有简单的时间线进度条，没有基于内容语义的导航。
用户想回看某个观点，只能凭记忆手动拖拽。

**LongCut 方案：** 按话题生成结构化卡片，点击即跳转，支持 Theme 维度筛选。

### 痛点 3：看完就忘

视频是单向信息流，缺乏交互。
用户被动接收，没有深度加工，知识留存率低。

**LongCut 方案：** AI 问答让用户主动提问与视频内容对话；笔记系统促进知识加工和沉淀。

### 痛点 4：无法快速评估一个视频值不值得看

在打开一个小时的视频之前，用户不知道内容质量和相关性。

**LongCut 方案：** Key Takeaways + Top Quotes + 精华片段预览，帮用户在几分钟内判断是否值得深入。

### 痛点 5：语言障碍

优质视频往往是英文的，非英语母语用户理解有门槛。

**LongCut 方案：** 多语言支持 — 字幕翻译 + AI 对话可指定目标语言回答。

---

## 十、潜在需求点与扩展方向

### 10.1 内容层扩展

| 方向 | 说明 | 价值 |
|------|------|------|
| **播客/音频支持** | 扩展到 Spotify、Apple Podcast 等音频平台 | 长音频同样存在信息密度低的痛点，市场需求大 |
| **多视频系列分析** | 将同一频道/话题的多个视频关联分析，生成跨视频知识图谱 | 系统性学习场景，如在线课程系列 |
| **本地视频/文件上传** | 支持上传本地视频或音频文件进行分析 | 企业培训视频、会议录像、内部讲座等场景 |
| **实时直播分析** | 对正在进行的 YouTube Live/会议进行实时精华提取 | 会议/讲座实时参与场景 |
| **PDF/文章对比** | 视频内容与相关论文/文章的交叉引用和对比分析 | 学术研究场景 |

### 10.2 学习体验增强

| 方向 | 说明 | 价值 |
|------|------|------|
| **间隔重复（Spaced Repetition）** | 从笔记/要点自动生成 Anki 风格的记忆卡片 | 长期知识留存是学习的核心挑战 |
| **学习路径推荐** | 基于用户历史分析的视频内容，推荐下一个应该看的视频 | 系统性学习引导 |
| **知识图谱可视化** | 将多个视频的概念关系可视化为节点图 | 帮助用户建立概念间的连接 |
| **协作学习** | 多人对同一视频的笔记和讨论共享 | 学习小组/课堂场景 |
| **AI 生成测验** | 基于视频内容自动生成选择题/问答题 | 主动学习 > 被动观看 |

### 10.3 导出与集成

| 方向 | 说明 | 价值 |
|------|------|------|
| **Notion/Obsidian 导出** | 一键将分析结果和笔记导出到主流知识管理工具 | 融入用户已有的知识管理工作流 |
| **浏览器插件** | Chrome/Firefox 扩展，在 YouTube 页面内嵌 LongCut 功能 | 降低使用门槛，无需跳转 |
| **API 开放** | 提供公共 API 供第三方集成 | 企业/开发者可嵌入到自有产品中 |
| **Markdown/PDF 报告导出** | 将完整分析导出为结构化文档 | 分享和存档需求 |

### 10.4 技术优化

| 方向 | 说明 | 价值 |
|------|------|------|
| **流式响应（Streaming）** | AI 生成过程采用 SSE/WebSocket 流式返回 | 改善首字节到达时间，提升感知速度 |
| **离线模式 / PWA** | 缓存已分析的视频到本地，支持离线回顾 | 通勤/无网络场景 |
| **精华片段视频剪辑** | 自动将精华片段剪成短视频并导出 | 内容创作者二次创作需求 |
| **语音输入问答** | 语音提问，AI 语音回答（TTS） | 边看视频边免手操作交互 |
| **多模态分析** | 不仅分析字幕文本，还分析视频画面（PPT 内容识别、演示动作检测） | 技术讲座中 PPT/代码演示是关键信息载体，纯字幕分析会遗漏 |

### 10.5 商业化方向

| 方向 | 说明 | 价值 |
|------|------|------|
| **企业版（Team/Enterprise）** | 团队共享分析库、管理员后台、SSO | B2B 市场，培训/知识管理场景 |
| **教育机构套件** | 教师布置视频学习任务 + 查看学生笔记/测验完成情况 | EdTech 垂直场景 |
| **内容创作者工具** | 帮助 YouTuber 分析自己视频的内容结构、识别高光时刻用于剪辑 | 创作者经济 |
| **白标 / 嵌入式方案** | 允许其他平台嵌入 LongCut 的分析能力 | 平台级收入，如 LMS 集成 |
