# Tech Stack

## Frontend / Render (reused from alharkan7/alharkan7.github.io)

| Layer | Tech | Notes |
|---|---|---|
| Framework | Astro 5.16.6 | Static output for local dev; server output for Vercel deploy |
| Content | MDX (via @astrojs/mdx) | Each paper = one `.mdx` file in `src/pages/` |
| Charts | D3.js v7 | **CDN global only** — loaded via `<script is:inline src="https://d3js.org/d3.v7.min.js">`. NOT an npm dep. Accessed as `globalThis.d3` inside all viz modules. |
| Theming | CSS custom properties | `--ink`, `--ink-muted`, `--paper`, `--paper-dark`, `--accent-blue`, `--political-red`. Per-paper override via frontmatter `theme:` block. Light/dark toggle via `body.light-theme` class + localStorage. |
| Fonts | Google Fonts CDN | Lora (serif, narrative text) + Inter (sans-serif, viz labels, nav) |
| Scroll engine | Custom Intersection Observer | `scrolly-runtime.ts` — no polling. Fires `switchViz(vizId)` when `.scroll-section` enters viewport. Viz panels fade in lazily; D3 module initializes once on first view. |

## Viz Registry (`web/src/scrolly/viz/`)

14 prebuilt D3 modules. Each exports `default function renderX({ mountEl, panelEl, props? })`.

| Key | Mount type | What it shows |
|---|---|---|
| `scatter` | svg | XY scatter with trend line, island color legend |
| `timeline` | svg | Horizontal timeline with events |
| `bars` | svg | Vertical bar chart |
| `bubbles` | svg | Bubble chart (size = magnitude) |
| `matrix` | svg | Grid/heatmap matrix |
| `map` | svg | Choropleth (province-level, Indonesia) |
| `sem` | svg | Structural equation model diagram |
| `equation` | svg | Rendered math/formula display |
| `sentiment` | svg | Sentiment score distribution |
| `accuracy` | svg | Accuracy bar (correct/incorrect breakdown) |
| `precision` | svg | Deviation waterfall chart |
| `dualmap` | div | Side-by-side choropleth maps |
| `market` | svg | Market/attention landscape |
| `upgrade` | div | Feature upgrade roadmap visualization |

**Fallback data:** every module has realistic fallback data baked in. If `props` is omitted or empty, the chart renders with the demo dataset. Real data goes in `props`.

## Generator (to build)

| Component | Tech | Notes |
|---|---|---|
| PDF ingest | PyMuPDF (`fitz`) + arXiv Python SDK | Extract text, tables, captions |
| GROBID (optional) | Java REST service | Better multi-column structure parsing |
| LLM | Claude via `anthropic` Python SDK | claude-sonnet-4-6 or opus for config generation |
| Validation | Pure Python JSON Schema check | Reads viz registry filenames; no TS compiler needed |
| Orchestration | `pipeline.py` | CLI: `python3 pipeline.py <pdf_or_arxiv_id>` |

## CSP note

When deploying, `astro.config.mjs` must allow `d3js.org` in `script-src`. Already handled in local dev config. For Vercel deployment, re-add the `security.directives` block from the original repo's `astro.config.mjs`.
