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
        slug: 'ngram-language-model',
        title: 'AI 猜词第一课：数频率为何走不通',
        summary: '从手机输入法"猜下一个词"讲起，铺开语言模型的起点：序列数据为什么顺序即信息、文字如何经四步流水线变成数字，再用一个 4 句话、10 个词的迷你语料亲手数一遍 n 元语法——看它如何在"加大 n 更准"与"格子指数膨胀又填不满"之间两头堵；而齐普夫定律的长尾更宣判了数频率的死刑：经验被锁死在格子里，无法从"他"迁移到"她"。这正是神经网络登场的理由，也是整个 RNN 系列的起点。',
        tags: ['深度学习', '语言模型', 'n 元语法', '齐普夫定律', '序列建模', 'NLP'],
        date: '2026-07-09',
        readingTime: '8 分钟',
        image: '/images/articles/ngram-language-model.png',
      },
      {
        slug: 'rnn',
        title: '当神经网络学会记忆：一文读懂 RNN',
        summary: '承接语言模型"想记住历史又不能让参数爆炸"的两难，拆解 RNN 如何用"更新账本、读出预测"两步规则与一套共享参数，把任意长的历史压进固定大小的隐状态；再讲透困惑度为何读作"模型每步在几个候选词之间纠结"，并跟着一个小批量走完从采样、前向到参数更新的完整训练旅程，直到让模型自己写出句子。',
        tags: ['深度学习', 'RNN', '循环神经网络', '语言模型', '困惑度', '序列建模'],
        date: '2026-07-08',
        readingTime: '7 分钟',
        image: '/images/articles/rnn.png',
      },
      {
        slug: 'rnn-gradient',
        title: 'RNN 的死穴：梯度爆炸与消失',
        summary: '同一个权重矩阵沿时间被连乘几十次，这件事有两本账：前向的雪球有 tanh 踩刹车，反向的连乘没人管。先用前馈网络的两本账讲清"链式法则一层乘两个因子"的读法，再用一个极简 RNN 沿三条路径亲手推出 BPTT 的梯度——隔几步就乘几个 w，大于 1 爆炸、小于 1 消失，结构注定；最后算清两个补丁的账：梯度裁剪治爆炸、截断 BPTT 省算力，但消失无解，除非换结构。',
        tags: ['深度学习', 'RNN', '梯度爆炸', '梯度消失', 'BPTT', '梯度裁剪'],
        date: '2026-07-11',
        readingTime: '8 分钟',
        image: '/images/articles/rnn-gradient.png',
      },
      {
        slug: 'modern-rnn',
        title: '给记忆装阀门：一文读懂现代 RNN',
        summary: '承接"梯度消失无解，除非换结构"的判决，拆解门控的共同底层——把连乘的乘数从定死的 W×tanh′ 换成可学到 1 的门，给记忆和梯度修一条加法直通路；再看 GRU 两个门与 LSTM 三个门加一条记忆传送带的分工取舍，以及深度、双向两个正交增强和双向"只能当编码器"的边界。',
        tags: ['深度学习', 'GRU', 'LSTM', '门控', 'RNN', '双向 RNN'],
        date: '2026-07-11',
        readingTime: '8 分钟',
        image: '/images/articles/modern-rnn.png',
      },
      {
        slug: 'word2vec',
        title: '当词语第一次变成向量：一文读懂 word2vec',
        summary: '从独热编码表达不了相似度的死胡同出发，拆解 Skip-gram/CBOW 两个对偶模型、"两个矩阵 + 查表 + 点积"的极简结构与借口任务思想，再到负采样/层序 softmax 如何绕开 O(|V|) 分母、下采样与三数组打包的工程细节——词语第一次变成向量，一切现代 embedding 都从这里出发。',
        tags: ['深度学习', 'word2vec', '词向量', 'NLP', '负采样', 'Skip-gram'],
        date: '2026-07-08',
        readingTime: '17 分钟',
        image: '/images/articles/word2vec.png',
      },
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
    slug: 'agent',
    name: '智能体',
    description: '智能体设计模式:提示链、路由、上下文工程等——《Agentic Design Patterns》精读专栏',
    icon: '🦾',
    color: '#06b6d4',
    heroImage: '/images/topics/agent-hero.png',
    articles: [
      {
        slug: 'prompt-chaining-basics',
        title: '一个大提示,不如一条链',
        summary: '复杂任务塞进一个大提示总在翻车——指令忽略、上下文漂移、错误传播、窗口不足、幻觉,五种失败同根同源:一次调用对齐了太多目标。本文给出提示链改造三板斧:一步一目标拆步骤、每步指派角色、步骤间用 JSON 结构化交接,并用一条最小两步链讲清 LangChain 与编排框架怎么选。',
        tags: ['智能体', '提示链', 'Prompt Chaining', 'LangChain', '结构化输出'],
        date: '2026-07-18',
        readingTime: '8 分钟',
        image: '/images/articles/prompt-chaining-basics.png',
      },
      {
        slug: 'prompt-chaining-use-cases',
        title: '你的任务该不该拆链?看四个信号',
        summary: '七类典型场景一张地图归成三组;再深挖两个案例:带校验回路的发票抽取链把「靠运气」变成「有抓手」,研究智能体示范并行采集与串行综合各干各的;最后是四条经验法则——多阶段、要验证、要工具、要状态,见到这四个信号就该拆链。',
        tags: ['智能体', '提示链', 'Prompt Chaining', '工作流', 'LangGraph'],
        date: '2026-07-18',
        readingTime: '8 分钟',
        image: '/images/articles/prompt-chaining-use-cases.png',
      },
      {
        slug: 'context-engineering',
        title: '提示词调无可调?该做上下文工程了',
        summary: '同一个模型效果天差地别,差距往往不在提示词,而在模型「看到的世界」。上下文工程把优化对象从一句话扩大到全部信息环境:系统提示、检索文档、工具输出、隐式数据四层拼出完整操作图景,再用评估闭环让上下文质量持续迭代,而不是靠手感。',
        tags: ['智能体', '上下文工程', 'Context Engineering', '提示工程', 'RAG'],
        date: '2026-07-18',
        readingTime: '8 分钟',
        image: '/images/articles/context-engineering.png',
      },
      {
        slug: 'routing-basics',
        title: '链解决怎么走,路由解决走哪条',
        summary: '固定链只有一条路,真实请求却五花八门。路由给智能体装上分诊台:先判意图再分发;LLM、Embedding、规则、ML 分类器四种机制各有账本;路由发生在入口、链中、选工具三个时机;最后一份判断清单说清什么时候该上路由、什么时候让链安静直行。',
        tags: ['智能体', '路由', 'Routing', '意图识别', 'LangGraph'],
        date: '2026-07-18',
        readingTime: '8 分钟',
        image: '/images/articles/routing-basics.png',
      },
      {
        slug: 'routing-in-practice',
        title: '分支画在明处,还是交给模型?',
        summary: '同一个「预订 + 咨询」场景,LangChain 让你亲手写路由提示、接好每条分支,Google ADK 只要挂上子代理、分发自动发生。两种路由工程范式怎么选:显式路由规则可读、分支可单独调试;自动委派声明能力清单、由框架做意图匹配;无论选哪边,「意图不明」的兜底路线都必须亲手接好。',
        tags: ['智能体', '路由', 'Routing', 'LangChain', 'Google ADK'],
        date: '2026-07-18',
        readingTime: '8 分钟',
        image: '/images/articles/routing-in-practice.png',
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
