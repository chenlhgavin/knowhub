// 演示文稿数据结构

export interface Presentation {
  slug: string;
  title: string;
  description: string;
  date: string;
  coverImage?: string;
  slideCount: number;
  tags?: string[];
}

export const presentations: Presentation[] = [
  {
    slug: 'rust-essentials',
    title: 'Rust 设计哲学',
    description:
      '深入剖析 Rust 语言的六大设计哲学：零成本抽象、所有权系统、无畏并发、显式优于隐式、实用主义、编译期保证。理解这些核心理念，掌握现代系统级编程的设计精髓。',
    date: '2026-02-07',
    coverImage: '/images/presentations/rust-essentials/01.jpg',
    slideCount: 7,
    tags: ['Rust', '设计哲学', '零成本抽象', '所有权系统', '无畏并发', '编译期保证'],
  },
];

// 获取所有演示文稿
export function getAllPresentations(): Presentation[] {
  return [...presentations].sort(
    (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
  );
}

// 获取指定演示文稿
export function getPresentation(slug: string): Presentation | undefined {
  return presentations.find((p) => p.slug === slug);
}
