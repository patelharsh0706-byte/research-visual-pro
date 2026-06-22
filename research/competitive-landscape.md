# Competitive Landscape

Research from `/last30days` run on 2026-06-21. Web supplements used (Reddit API 403'd during run).

## The gap

Text-summary tools are crowded. Visual-output tools generate single diagrams. Nobody auto-generates a **full guided scroll-driven narrative** from a paper.

## Existing tools

| Tool | Output type | Gap |
|---|---|---|
| SciSpace / Elicit / Consensus / SciSummary | Text summaries, chat-with-PDF | More text — doesn't help visual comprehension |
| Google PaperBanana (Feb 2026) | Single diagrams from paper figures | One diagram, no narrative arc |
| Napkin | Single concept diagrams | Whiteboard-style, no data charts |
| ScrollyVis (IEEE TVCG) | Full scrollytelling — but manual | Requires web dev skills; no automation |
| Explainer YouTube channels | Video, human-narrated | Not interactive, not on-demand |

## The open lane

**Automated full narrative** = scroll-driven story (5–8 beats: question → method → key result → implication), each beat synchronized to a real D3 chart from the paper's actual data.

ScrollyVis (IEEE TVCG academic paper) literally named the bottleneck: *"not all scientists possess web-development skills."* The scrolly template solves the dev half; the LLM solves the authoring half.

## Positioning warning

r/Professors thread (483 upvotes, 2026): "Why is AI being shoved down our throats?" Academics are AI-fatigued. **Sell comprehension, never "AI-generated science."** The framing is: "here's a visual guide to this paper" — not "AI summarized this paper."

## Why now

- Google PaperBanana (Feb 2026) proved the demand. But single diagrams ≠ narrative comprehension.
- The scrolly render engine already exists and is explicitly reusable (alharkan's repo README).
- LLMs in 2026 are good enough to reliably pick chart types and extract table numbers into structured config objects.
