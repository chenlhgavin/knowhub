// 知识库数据结构 - 可扩展的主题与文章管理

export interface Article {
  slug: string;
  title: string;
  summary: string;
  tags: string[];
  date: string;
  updated?: string;
  readingTime?: string;
  image?: string;          // 文章封面图（相对于 public 目录的路径）
}

export interface Topic {
  slug: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  heroImage?: string;      // 主题 Hero 背景图（相对于 public 目录的路径）
  articles: Article[];
}

export const topics: Topic[] = [
  {
    slug: 'deep-learning',
    name: '深度学习',
    description: 'NLP 预训练模型、词向量、Transformer 架构、微调范式等深度学习核心技术',
    icon: '🧠',
    color: '#f97316',
    heroImage: '/images/topics/deep-learning-hero.png',
    articles: [
      {
        slug: 'bert-family',
        title: '当词向量学会看上下文：一文读懂 BERT',
        summary: '从静态词向量的一词多义与"三明治"困境出发，拆解 BERT 的双向编码器架构、三嵌入输入表示、MLM/NSP 预训练任务与"换头+轻推"微调范式，并梳理 RoBERTa / DistilBERT / ELECTRA 等家族图谱与它在今天的定位。',
        tags: ['深度学习', 'BERT', 'NLP', '预训练', 'Transformer', '微调'],
        date: '2026-07-07',
        readingTime: '18 分钟',
        image: '/images/articles/bert-family.png',
      },
      {
        slug: 'sentence-transformers',
        title: '把一句话装进一个向量：一文读懂 sentence-transformers',
        summary: '从 BERT 原生句向量的失效与 cross-encoder 的 O(N²) 推理账单出发，拆解 SBERT 的双塔结构、mean pooling 与批内负采样对比学习，再到 retrieve & re-rank 两级架构——讲清今天几乎所有语义检索与 RAG 系统的地基。',
        tags: ['深度学习', 'SBERT', '句向量', '对比学习', 'RAG', '语义检索'],
        date: '2026-07-08',
        readingTime: '14 分钟',
        image: '/images/articles/sentence-transformers.png',
      },
    ],
  },
  {
    slug: 'rust',
    name: 'Rust',
    description: 'Rust 语言核心概念、所有权系统、并发编程、生态工具等',
    icon: '🦀',
    color: '#dea584',
    heroImage: '/images/topics/rust-hero.png',
    articles: [
      {
        slug: 'design-philosophy',
        title: 'Rust 设计哲学：安全、并发与零成本抽象',
        summary: '深入剖析 Rust 语言的六大设计哲学：零成本抽象、所有权系统、无畏并发、显式优于隐式、编译期保证和实用主义，理解 Rust 为何能在安全性和性能之间取得完美平衡。',
        tags: ['Rust', '设计哲学', '所有权', '并发', '类型系统'],
        date: '2026-02-07',
        readingTime: '10 分钟',
        image: '/images/articles/rust-design-philosophy.png',
      },
      {
        slug: 'ownership-system',
        title: 'Rust 所有权系统深度解析：从设计原理到最佳实践',
        summary: '全方位深入剖析 Rust 所有权系统的设计哲学与内部机制，涵盖所有权规则、借用系统、生命周期、智能指针、内部可变性等核心概念，结合 Mermaid 图表与实战场景详解最佳实践。',
        tags: ['Rust', '所有权', '借用', '生命周期', '智能指针', '内存安全'],
        date: '2026-02-07',
        readingTime: '25 分钟',
        image: '/images/articles/rust-ownership-system.png',
      },
      {
        slug: 'smart-pointers',
        title: 'Rust 智能指针：从原理到实战',
        summary: '系统剖析 Rust 标准库中的智能指针体系，涵盖 Box、Rc/Arc、Cell/RefCell、Cow、Pin 等核心类型的内存布局、实现原理与组合模式，结合 Mermaid 图表与决策树指导实战选型。',
        tags: ['Rust', '智能指针', '内存管理', '所有权', '并发', 'RAII'],
        date: '2026-02-10',
        readingTime: '30 分钟',
        image: '/images/articles/rust-smart-pointers.png',
      },
    ],
  },
  {
    slug: 'multimodal-agent',
    name: '多模态Agent',
    description: '多模态AI Agent架构、工具调用、视觉推理、编排框架等',
    icon: '🤖',
    color: '#8b5cf6',
    heroImage: '/images/topics/multimodal-agent-hero.png',
    articles: [],
  },
  {
    slug: 'architecture',
    name: '架构设计',
    description: '优秀开源项目的架构剖析、设计模式、接口哲学与工程实践',
    icon: '🏛️',
    color: '#0ea5e9',
    heroImage: '/images/topics/architecture-hero.png',
    articles: [
      {
        slug: 'claude-agent-sdk-architecture',
        title: 'Claude Agent SDK Python 架构设计解析',
        summary: '从架构视角系统剖析 Anthropic Claude Agent SDK 的四层分层设计、双模式 API、双向控制协议、三方协作数据流与扩展机制，提炼值得借鉴的工程设计原则。',
        tags: ['架构设计', 'SDK', 'Claude', 'Agent', 'Python', 'MCP', '异步编程'],
        date: '2026-02-13',
        readingTime: '20 分钟',
        image: '/images/articles/claude-agent-sdk-architecture.png',
      },
    ],
  },
  {
    slug: 'python',
    name: 'Python',
    description: 'Python 高级特性、异步编程、数据科学、Web开发等',
    icon: '🐍',
    color: '#3572A5',
    heroImage: '/images/topics/python-hero.png',
    articles: [
      {
        slug: 'concurrency-deep-dive',
        title: 'Python 并发深度解析：从 GIL 到 asyncio',
        summary: '从 GIL 的底层机制出发，逐一剖析 threading、multiprocessing、concurrent.futures、asyncio 四大并发模型的原理与适用场景，并展望 Free-threaded Python 对未来生态的影响。',
        tags: ['Python', 'GIL', '并发', '异步', 'asyncio', '多线程', '多进程'],
        date: '2026-02-13',
        readingTime: '25 分钟',
        image: '/images/articles/python-concurrency-deep-dive.png',
      },
    ],
  },
];

// 获取指定主题
export function getTopic(slug: string): Topic | undefined {
  return topics.find((t) => t.slug === slug);
}

// 获取所有主题摘要
export function getTopicsSummary() {
  return topics.map((t) => ({
    slug: t.slug,
    name: t.name,
    description: t.description,
    icon: t.icon,
    color: t.color,
    heroImage: t.heroImage,
    articleCount: t.articles.length,
  }));
}

// 获取所有文章（跨主题），按日期降序
export function getAllArticles() {
  return topics
    .flatMap((t) =>
      t.articles.map((a) => ({
        ...a,
        topicSlug: t.slug,
        topicName: t.name,
        topicIcon: t.icon,
        topicColor: t.color,
      }))
    )
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
}

// 获取主题 Hero 图片映射
export function getTopicHeroImages(): Record<string, string> {
  const map: Record<string, string> = {};
  topics.forEach((t) => {
    if (t.heroImage) map[t.slug] = t.heroImage;
  });
  return map;
}

// 获取所有标签
export function getAllTags(): string[] {
  const tags = new Set<string>();
  topics.forEach((t) => t.articles.forEach((a) => a.tags.forEach((tag) => tags.add(tag))));
  return Array.from(tags).sort();
}

// 统计信息
export function getStats() {
  const totalArticles = topics.reduce((sum, t) => sum + t.articles.length, 0);
  const totalTags = getAllTags().length;
  return {
    topicCount: topics.length,
    articleCount: totalArticles,
    tagCount: totalTags,
  };
}
