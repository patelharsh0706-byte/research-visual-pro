# Roadmap

## MVP (weekend) - prove the loop end-to-end

- [ ] Fork alharkan's scrolly repo, get it running locally.
- [ ] Hardcode ONE quantitative arXiv paper (with clean tables).
- [ ] Hand-write the target `data/<slug>.ts` config for it (the gold output).
- [ ] Write the LLM prompt that emits that same config from the paper text → compare to gold.
- [ ] Render and scroll through it. Done = the loop works for one paper.

Goal: de-risk Step 2 (LLM → valid config). Everything else is plumbing.

## v1 - the product

- [ ] PDF/arXiv ingest (GROBID + table extraction).
- [ ] Prompt generalized across paper types (with the 5-8 beat structure).
- [ ] Config schema validator (reject hallucinated viz keys / bad props before render).
- [ ] Per-paper theming via frontmatter `theme` block.
- [ ] Simple upload UI → generated page.

## Later - the coverage gap

- [ ] New D3 viz types for concept maps / method diagrams (net-new work).
- [ ] **Gemini / Nano Banana Pro fallback lane** (deferred, gated):
  - Only fires when no real data maps to a chart.
  - Feed the paper's own figure as reference; redraw/clean up, never invent.
  - Label output "illustrative" so it is never mistaken for extracted data.
  - Faithfulness check before it ships.

## Open questions

- Outreach to alharkan? README invites reuse and he has clearly thought about this exact problem - possible collaborator.
- Better social signal: re-run /last30days with X + YouTube enabled for sharper pain-point quotes.
- Licensing of the forked scrolly system for a commercial product.
