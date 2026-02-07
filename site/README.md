# 知识库 (KnowHub)

基于 Astro 5.x 构建的现代化知识库网站，汇集 Rust、多模态 Agent、Python 等技术领域的学习笔记、文章与演示文稿。

线上地址：https://lehuagavin.github.io/knowhub

## 技术栈

- **框架**: Astro 5.x + MDX
- **UI 库**: React 19
- **样式**: Tailwind CSS 4.x + CSS 自定义属性
- **图表**: Mermaid.js
- **图标**: Lucide React
- **部署**: GitHub Pages

## 功能特性

- **主题系统**：支持 Apple 风格（含深色模式）和 MotherDuck 风格两套主题
- **知识主题**：按主题分类组织文章（Rust、多模态 Agent、Python）
- **演示文稿**：幻灯片轮播查看，支持全屏、自动播放、键盘快捷键
- **Mermaid 图表**：文章内嵌 Mermaid 语法自动渲染流程图、架构图
- **响应式设计**：完美适配桌面端和移动端

## 网站页面

| 路径 | 说明 |
|------|------|
| `/` | 首页 — Hero 区、统计数据、主题网格、最新文章 |
| `/topics/[slug]` | 主题页 — 该主题下的所有文章列表 |
| `/topics/[slug]/[article]` | 文章页 — Markdown 渲染、上下篇导航、Mermaid 图表 |
| `/presentations` | 演示文稿列表 — 封面卡片网格 |
| `/presentations/[slug]` | 演示文稿详情 — 幻灯片轮播、缩略图、全屏播放 |
| `/about` | 关于页面 |

## 内容管理

文章和演示文稿通过数据文件 + Markdown/MDX 内容文件管理：

```
src/
├── data/
│   ├── topics.ts              # 主题与文章元数据
│   └── presentations.ts       # 演示文稿元数据
├── content/
│   ├── rust/                  # Rust 主题文章 (Markdown)
│   │   ├── design-philosophy.md
│   │   └── ownership-system.md
│   └── presentations/         # 演示文稿 (MDX)
│       └── rust-essentials.mdx
```

### 添加新文章

1. 在 `src/data/topics.ts` 对应主题的 `articles` 数组中添加文章元数据
2. 在 `src/content/[topic-slug]/` 下创建同名 `.md` 文件

### 添加新演示文稿

1. 在 `src/data/presentations.ts` 的 `presentations` 数组中添加元数据
2. 将幻灯片图片放入 `public/images/presentations/[slug]/`
3. 在 `src/content/presentations/` 下创建同名 `.mdx` 文件，引入 `PresentationCarousel` 组件

## 项目结构

```
├── public/
│   └── images/
│       └── presentations/     # 演示文稿幻灯片图片
├── src/
│   ├── components/
│   │   ├── layout/           # 布局组件 (Navigation, Footer)
│   │   ├── sections/         # 区域组件 (HeroSection, StatsSection, ...)
│   │   ├── cards/            # 卡片组件 (ArticleCard, TopicCard, ...)
│   │   ├── content/          # 内容组件 (Breadcrumb, FeatureGrid, ...)
│   │   └── interactive/      # 交互组件 (PresentationCarousel, TabsView, ...)
│   ├── layouts/              # 页面布局 (BaseLayout)
│   ├── pages/                # 页面路由
│   ├── data/                 # 数据定义
│   ├── content/              # Markdown/MDX 内容
│   ├── styles/               # 全局样式 (global.css)
│   └── utils/                # 工具函数
├── astro.config.mjs
└── package.json
```

## 开发指南

### 启动开发服务器

```bash
npm run dev
```

服务器将在 http://localhost:4321/knowhub 启动

### 构建生产版本

```bash
npm run build
```

### 预览构建结果

```bash
npm run preview
```

## 设计系统

### Apple 主题（默认）

- **主色调**: #0071e3
- 简约留白，细腻动画过渡
- 支持浅色/深色模式自动切换

### MotherDuck 主题

- **主色调**: #6FC2FF
- 硬边偏移阴影，等宽字体标题
- 品牌色系：Yellow、Teal、Coral、Lime

## 许可证

MIT
