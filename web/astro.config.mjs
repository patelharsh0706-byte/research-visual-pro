import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import remarkGfm from 'remark-gfm';
import remarkSmartypants from 'remark-smartypants';
import rehypeExternalLinks from 'rehype-external-links';

export default defineConfig({
  output: 'static',
  site: process.env.VERCEL_PROJECT_PRODUCTION_URL
    ? `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}`
    : 'http://localhost:4321',
  integrations: [mdx()],
  markdown: {
    remarkPlugins: [remarkGfm, remarkSmartypants],
    rehypePlugins: [
      [rehypeExternalLinks, { target: '_blank' }],
    ],
  },
});
