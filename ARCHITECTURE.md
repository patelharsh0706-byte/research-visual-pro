# Architecture

The pipeline maps 1:1 onto the four layers of alharkan's scrolly system. We generate the two author-written layers (narrative + data); the other two (layout + engine) we reuse unchanged.

```
PDF / arXiv link
      │
      ▼
┌─────────────┐   1. INGEST
│  extract    │   text + section structure + figures/tables + numbers
└─────────────┘   (GROBID or PDF parser)
      │
      ▼
┌─────────────┐   2. STRUCTURE  ← the LLM step, the riskiest piece
│  Claude     │   paper → scrollytelling script:
│             │   - 5-8 narrative beats (intro→question→method→result→implication)
│             │   - each beat = plain-language MDX
│             │   - each beat picks ONE viz.key + emits its props (real paper data)
└─────────────┘
      │
      ▼
┌─────────────┐   3. RENDER  ← reused from alharkan, ~zero new code for v1
│  write 2    │   src/posts/scrolly/<slug>.mdx     (narrative)
│  files      │   src/scrolly/data/<slug>.ts        (config object)
│             │   ScrollyLayout.astro glues them; runtime + D3 modules render
└─────────────┘
      │
      ▼
  Interactive scrollytelling page
```

## The scrolly system (reused, do not rebuild)

Four layers, from `docs/scrolly-system-notes.md`:

| Layer | File | Who writes it |
|---|---|---|
| Narrative | `src/posts/scrolly/<slug>.mdx` | **We generate** (LLM) |
| Data/config | `src/scrolly/data/<slug>.ts` | **We generate** (LLM) |
| Layout | `src/layouts/ScrollyLayout.astro` | Reuse as-is |
| Engine | `src/scrolly/scrolly-runtime.ts` | Reuse as-is |

Mechanism: each `<ScrollySection id="x">` pairs with a `sections[].id === "x"` in the config. The runtime uses the Intersection Observer API (no scroll polling) to fade in the matching `.viz-panel` when a section enters the viewport.

Prebuilt viz registry (~14 D3 modules in `src/scrolly/viz/`): `scatter`, `timeline`, `bars`, `bubbles`, `matrix`, `map`, `sem`, `equation`, `sentiment`, `accuracy`, `precision`, `dualmap`, `market`, `upgrade`.

## The core risk

Step 2, not step 3. The scrolly system is done and faithful by construction. The unsolved problems are:
1. **LLM picks the right viz.key** for each beat and maps paper data into valid `props`.
2. **Figure/table extraction from PDFs** is genuinely hard and quietly eats most build time.
3. **Coverage gap:** qualitative/theory papers have no data that maps to the 14 viz types → empty right column. This is the (deferred) Gemini lane.

## Tech stack (proposed)

- **Frontend/render:** fork alharkan's Astro repo (already MIT-spirit reusable per its README).
- **LLM:** Claude (config-object generation, narrative rewriting).
- **PDF ingest:** GROBID for structure + a table/figure extractor; arXiv API for source.
- **Validation:** schema-check the emitted TS `config` against the viz registry before render (catch hallucinated viz keys / malformed props).
