import { defineCollection, z } from 'astro:content';

// 文章内容集合 - 按主题分目录存放
// 例如: src/content/rust/design-philosophy.md

const rust = defineCollection({
  type: 'content',
  schema: z.object({}).passthrough().optional(),
});

const multimodalAgent = defineCollection({
  type: 'content',
  schema: z.object({}).passthrough().optional(),
});

const python = defineCollection({
  type: 'content',
  schema: z.object({}).passthrough().optional(),
});

const architecture = defineCollection({
  type: 'content',
  schema: z.object({}).passthrough().optional(),
});

const presentations = defineCollection({
  type: 'content',
  schema: z.object({}).passthrough().optional(),
});

export const collections = {
  rust,
  'multimodal-agent': multimodalAgent,
  python,
  architecture,
  presentations,
};
