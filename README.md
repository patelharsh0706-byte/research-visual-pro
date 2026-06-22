# research-visual-pro

Turn a dense research paper into an interactive, scroll-driven visual story so it is *understood*, not just *summarized*.

## The problem

Reading research papers is slow, dense, and boring. You lose the concepts in walls of prose. Existing AI tools (SciSpace, Elicit, Consensus, SciSummary) attack this by producing **more text** - summaries, chat-with-PDF, extracted tables. Almost nobody turns the paper into a **structured visual narrative**.

## The insight

The gap is *visual output*, not *summary output*. A paper has a natural arc - question → method → key result → implication. If you render that arc as **scrollytelling** (narrative on the left, a synchronized chart on the right that updates as you scroll), the concepts land.

The rendering engine for this already exists and is explicitly reusable: alharkan's `scrolly/` system (Astro + D3 + TypeScript) from `github.com/alharkan7/alharkan7.github.io`. A human writes the narrative (MDX) and the data (TS config) by hand today. **Our product is an LLM that generates both from a PDF.** That is the whole thesis in one sentence.

## Why now / competitive read (from /last30days, 2026-06-21)

- Text-summary tools are crowded; structured-visual-output is the open lane.
- Google's **PaperBanana** (Feb 2026) and **Napkin** prove demand for paper→visual, but they generate single diagrams, not full guided narratives.
- **ScrollyVis (IEEE TVCG)** academically validated scientific scrollytelling and named the exact bottleneck: *"not all scientists possess web-development skills."* The scrolly template solves the dev half; the LLM solves the authoring half.
- Positioning warning: academics are visibly AI-fatigued (r/Professors). Sell **comprehension**, never "AI-generated science."

See [research/competitive-landscape.md](research/competitive-landscape.md) for sources.

## Scope decisions (locked)

- **v1 = scrollytelling only.** Faithful D3 charts driven by real numbers extracted from the paper. No generative imagery in the core loop.
- **Gemini / Nano Banana Pro is deferred**, and only ever as a narrow, labeled, fallback "concept illustration" lane for qualitative/theory papers the 14 fixed viz types cannot render. Gated behind a faithfulness check (redraw the paper's own figure, never invent). Adding it now multiplies the hardest unsolved problem (LLM-picks-right-visual) by a second one (don't-hallucinate-the-science).

## Status

Planning. See [ROADMAP.md](ROADMAP.md) for the build order and [ARCHITECTURE.md](ARCHITECTURE.md) for the pipeline.
