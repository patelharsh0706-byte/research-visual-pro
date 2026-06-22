import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import remarkGfm from 'remark-gfm';
import remarkSmartypants from 'remark-smartypants';
import rehypeExternalLinks from 'rehype-external-links';

export default defineConfig({
  output: 'static',
  site: 'http://localhost:4321',
  vite: {
    server: {
      allowedHosts: ['localhost'],
    },
  },
  integrations: [mdx()],
  markdown: {
    remarkPlugins: [remarkGfm, remarkSmartypants],
    rehypePlugins: [
      [rehypeExternalLinks, { target: '_blank' }],
    ],
  },
});
