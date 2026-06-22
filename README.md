# Research Visual Pro

> Drop in a dense academic PDF. Get back an interactive, scroll-driven visual story — real charts, real numbers, guided narrative.

**Live demo →** *(coming soon — Vercel deploy in progress)*

---

## About

Research papers are hard to read. Existing AI tools respond with *more text* — summaries, chat-with-PDF, extracted tables. **Research Visual Pro** takes a different lane: it turns a paper into a **scrollytelling page** — narrative on the left, a synchronized D3 chart on the right that updates as you scroll.

A 7-agent LLM pipeline reads the PDF, plans a narrative arc (question → method → result → implication), selects the right visualization for each beat, extracts real numbers from the paper, and writes the two files the render engine needs. The render engine itself is pure Astro + D3 — no hallucinated diagrams, no invented data.

**The thesis in one sentence:** a human writes the narrative and data config by hand today; this pipeline generates both from a PDF.

---

## Demo

| Homepage | Paper page |
|---|---|
| Auto-discovered paper cards with mini hero thumbnails | Scroll-driven narrative with synchronized D3 charts |

---

## How it works

```
PDF / arXiv URL
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│  7-Agent Python Pipeline (generator/)                       │
│                                                             │
│  1 Extractor   → text, tables, figures, stats               │
│  2 StoryPlanner → 5-8 narrative beats with roles + layout   │
│  3 ChartSelector → best viz type + visual metaphor per beat │
│  4 ConfigWriter → valid TypeScript config object            │
│  5 Validator   → schema-check against the viz registry      │
│  6 CustomViz   → D3 TypeScript module for novel charts      │
│  7 Reviewer    → benchmark audit + fill missing fields      │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
  web/src/scrolly/data/<slug>.ts   ← config
  web/src/pages/<slug>.mdx         ← narrative
     │
     ▼
  Astro + D3 render engine → scrollytelling page
```

---

## Tech stack

| Layer | Tech |
|---|---|
| Frontend | [Astro 5](https://astro.build) (static output) + MDX |
| Charts | [D3.js v7](https://d3js.org) (CDN global, 14 viz modules) |
| Styling | CSS custom properties, Lora + Inter (Google Fonts) |
| Generator | Python 3.11+, [Anthropic SDK](https://github.com/anthropics/anthropic-sdk-python) |
| LLM | Claude Sonnet (planning/config) · Claude Opus (custom viz code) |
| Deploy | Vercel (static) |

---

## Viz library (14 types)

`bars` · `sem` · `scatter` · `matrix` · `timeline` · `bubbles` · `map` · `market` · `equation` · `accuracy` · `precision` · `dualmap` · `sentiment` · `upgrade`

Each module is a pure function: `render({ mountEl, props })` — reads `globalThis.d3`, colors via CSS variables, fallback data baked in.

---

## Published papers

| Paper | Year | Key viz |
|---|---|---|
| Drug Repurposing — Pushpakom et al. | 2019 | SEM, bars, scatter, matrix |
| Licensing & Learning — Kelchtermans & Verboven | 2022 | Bars, scatter, precision |

---

## Run locally

```bash
# Clone
git clone https://github.com/patelharsh0706-byte/research-visual-pro.git
cd research-visual-pro/web

# Install deps
pnpm install

# Dev server
pnpm dev
# → http://localhost:4321
```

**Requirements:** Node 20+, pnpm 9+

---

## Generate a new paper page

```bash
cd generator
pip install anthropic pymupdf

# From a local PDF
python3 pipeline.py --pdf ../samples/papers/your-paper.pdf

# From an arXiv URL
python3 pipeline.py --arxiv https://arxiv.org/abs/XXXX.XXXXX
```

Output is written to `web/src/scrolly/data/<slug>.ts` and `web/src/pages/<slug>.mdx`. The homepage auto-discovers it — no manual updates needed.

**Requirements:** Python 3.11+, Anthropic API key in `ANTHROPIC_API_KEY`

---

## Project structure

```
research-visual-pro/
├── web/                          ← Astro frontend
│   └── src/
│       ├── pages/                ← one .mdx per paper + index.astro
│       ├── scrolly/
│       │   ├── data/             ← generated TS configs
│       │   └── viz/              ← 14 D3 render modules
│       ├── layouts/ScrollyLayout.astro
│       └── components/scrolly/
├── generator/                    ← 7-agent Python pipeline
│   ├── agents/                   ← agent_extractor … agent_reviewer
│   ├── schemas/                  ← viz registry + paper data schema
│   └── pipeline.py               ← orchestrator
├── samples/
│   └── gold/                     ← reference configs for LLM grading
└── docs/                         ← architecture notes
```

---

## Competitive context

Text-summary tools (SciSpace, Elicit, Consensus) are crowded. Visual-output for papers is the open lane. Google's **PaperBanana** and **Napkin** generate single diagrams — not full guided narratives. IEEE TVCG's **ScrollyVis** validated scientific scrollytelling and named the exact bottleneck: *"not all scientists possess web-development skills."* This project closes that gap with an LLM pipeline.

---

## Roadmap

- [x] Render engine (Astro + 14 D3 viz modules)
- [x] 7-agent pipeline
- [x] Homepage with auto-discovered paper cards
- [x] Smooth scroll transitions
- [ ] Vercel deploy
- [ ] arXiv ingest (PDF → structured data)
- [ ] Upload UI (drag-and-drop PDF)
- [ ] Concept-map viz type for qualitative papers

See [ROADMAP.md](ROADMAP.md) for full detail.

---

## License

MIT — render engine adapted from [alharkan7/alharkan7.github.io](https://github.com/alharkan7/alharkan7.github.io) (explicitly reusable per their README).
