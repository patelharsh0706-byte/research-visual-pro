from __future__ import annotations

"""
Agent 6 — Custom Viz Generator
================================
Input:  beat dict (from chart_plan where viz_key == "custom") + paper_data
Output: a new TypeScript D3 viz module written to web/src/scrolly/viz/<slug>.ts

Triggered only when agent_chart_selector flags viz_key == "custom",
meaning no existing viz type can faithfully represent the paper's data.

Pattern (from PaperBanana's Critic loop):
  1. Plan  — describe the chart in prose (what axes, what marks, what interaction)
  2. Code   — write the D3 TypeScript function
  3. Review — critique the code against the plan and the viz module contract
  4. Patch  — apply fixes from the critique (max 2 rounds)
  5. Emit   — write the final file

LLM: Claude Opus (code generation; up to 3 calls per custom viz)
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import llm

VIZ_CONTRACT = """\
Every viz module must follow this exact contract:

```typescript
type {Name}Args = { mountEl: SVGSVGElement | HTMLElement; panelEl?: HTMLElement; props?: any };

export default function render{Name}({ mountEl, panelEl, props }: {Name}Args) {
  const d3 = (globalThis as any).d3;
  if (!d3) return;

  mountEl.replaceChildren();  // always clear first

  // ... your D3 code ...
  // Use CSS vars for colours: var(--ink), var(--ink-muted), var(--paper),
  //                           var(--accent-blue), var(--political-red)
  // viewBox: "0 0 600 400" for svg mount, 600x450 for div mount
  // All data comes from props — always provide sensible fallback data
}
```

Key constraints:
- D3 is a global loaded via CDN: (globalThis as any).d3. Never import it.
- For SVG mount: const svg = d3.select(mountEl).attr("viewBox", "0 0 600 400")
- For DIV mount: svg = d3.select(mountEl).append("svg").attr("viewBox", "0 0 600 450")
- All colors via CSS custom properties (no raw hex except in fallback data)
- Props fallback: every prop must have a sensible default so the demo renders without real data
- Font family: "Inter, sans-serif" for labels, "var(--font-serif)" for narrative text

MANDATORY — entrance animation:
  Every element that is a data mark (circle, rect, path, line) must use a D3 transition
  on first render. Example: .attr("opacity", 0).transition().duration(600).delay((_, i) => i * 80).attr("opacity", 1)
  Elements may also animate position/size: start at 0 height/radius and grow to final value.

MANDATORY — hover tooltip:
  Add a tooltip div: const tip = d3.select(mountEl.closest ? mountEl.closest("body") ?? document.body : document.body).append("div").attr("class","d3-tooltip").style("position","absolute").style("opacity",0)
  On mouseover: tip.style("opacity",1).html(tooltipContent).style("left",(event.pageX+12)+"px").style("top",(event.pageY-28)+"px")
  On mouseleave: tip.style("opacity",0)
"""

PLAN_SYSTEM = """\
You are a data artist and science communicator, not a chart maker.
Your job is to design a visual metaphor — not a standard bar or line chart.

A visual metaphor makes the data feel physical and intuitive. Good examples:
  - Drug trials as a funnel that shrinks at each stage
  - Knowledge flowing between firms as animated rivers / directional streams
  - A citation network as light radiating outward from a central node
  - Before/after comparison as two landscapes that morph into each other

Rules:
1. Start from the metaphor in visual_brief (if provided) — honor its intent
2. Describe the chart in precise technical prose: layout, marks, scales, interaction, animation
3. REQUIRE a D3 entrance animation: elements must animate in on first render (transitions, delays)
4. REQUIRE hover interactivity: tooltips showing exact values on hover
5. Keep it under 300 words. Be specific about D3 functions (d3.arc, d3.sankey, d3.forceSimulation, etc.)
"""

CODE_SYSTEM = f"""\
You are a D3.js expert writing TypeScript viz modules for an Astro scrollytelling system.

{VIZ_CONTRACT}

Write ONLY the TypeScript code. No explanation. No markdown fences.
The function name must be renderCustom (or render + the provided name).
"""

CRITIQUE_SYSTEM = """\
You are a senior D3.js code reviewer checking a viz module against its spec.

Check:
1. Does it follow the contract (replaceChildren, globalThis.d3, viewBox, CSS vars)?
2. Does it match the plan (right axes, marks, interaction)?
3. Are all props read with sensible fallbacks?
4. Will it compile as TypeScript (no unknown types, no missing variables)?

Return JSON:
{
  "issues": ["list of concrete issues to fix"],
  "ok_to_ship": true/false
}
"""


def run(
    beat: dict,
    paper_data: dict,
    viz_name: str,
    web_src_dir: str,
    model: str = "claude-opus-4-8"
) -> str:
    """
    Generate a custom D3 viz module for a beat that no existing viz handles.
    Returns the file path of the written module.
    """
    safe_name = re.sub(r"[^a-z0-9]", "_", viz_name.lower())
    func_name = "render" + "".join(w.capitalize() for w in safe_name.split("_"))

    print(f"[custom_viz] planning {safe_name}...")

    # ── Step 1: Plan ──────────────────────────────────────────────────────────
    plan_prompt = f"""Paper: {paper_data.get('title', '')}

Beat to visualize:
Headline: {beat.get('headline', '')}
Narrative role: {beat.get('narrative_role', '')}
Finding: {beat.get('finding_text', '')}
Data: {beat.get('data_sourced_from', [])}

Visual brief from Chart Selector (honor this intent):
{beat.get('visual_brief') or beat.get('custom_description') or '(none — invent a compelling metaphor)'}

Metaphor identified: {beat.get('metaphor', '(none)')}

Design the custom D3 chart. Describe precisely:
- The visual metaphor (what physical thing does the data look like?)
- Layout: radial, force, sankey, chord, funnel, geographic, or other
- Marks: what SVG elements represent what data dimensions
- Data shape for props (what arrays/objects the render function receives)
- Entrance animation sequence (what animates in first, second, etc.)
- Hover tooltip content (what exact values are shown)"""

    plan = llm.call(plan_prompt, system=PLAN_SYSTEM, model=model)
    print(f"[custom_viz] plan:\n{plan[:200]}...")

    # ── Step 2: Generate code ─────────────────────────────────────────────────
    code_prompt = f"""Chart plan:
{plan}

Function name: {func_name}

Write the complete TypeScript viz module for this chart.
Include realistic fallback data so it renders without props.
Data from the paper (for the default fallback):
{beat.get('data_sourced_from', [])}"""

    code = _strip_fences(llm.call(code_prompt, system=CODE_SYSTEM, model=model))

    # ── Steps 3–4: Critique and patch (max 2 rounds) ──────────────────────────
    for round_num in range(1, 3):
        critique_prompt = f"""Chart plan:
{plan}

Generated code:
```typescript
{code}
```

Review this code against the contract and plan. Return JSON."""

        crit_raw = _strip_fences(llm.call(critique_prompt, system=CRITIQUE_SYSTEM, model=model))

        try:
            import json as _json
            critique = _json.loads(crit_raw)
        except Exception:
            critique = {"issues": [], "ok_to_ship": True}

        if critique.get("ok_to_ship") or not critique.get("issues"):
            print(f"[custom_viz] critique round {round_num}: OK to ship")
            break

        print(f"[custom_viz] critique round {round_num}: {len(critique['issues'])} issues — patching...")

        patch_prompt = f"""Fix these issues in the code:
{chr(10).join(f'- {i}' for i in critique['issues'])}

Current code:
```typescript
{code}
```

Return the complete fixed TypeScript code only."""

        code = _strip_fences(llm.call(patch_prompt, system=CODE_SYSTEM, model=model))

    # ── Step 5: Emit file ─────────────────────────────────────────────────────
    out_path = Path(web_src_dir) / "scrolly" / "viz" / f"{safe_name}.ts"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(code)
    print(f"[custom_viz] wrote {out_path}")

    return str(out_path)


def _strip_fences(text: str) -> str:
    text = re.sub(r"^```(?:typescript|ts)?\n?", "", text)
    text = re.sub(r"\n?```$", "", text)
    return text.strip()


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 agent_custom_viz.py <paper_data.json> <beat.json> <viz_name> [web_src_dir]")
        sys.exit(1)

    import json
    paper    = json.loads(Path(sys.argv[1]).read_text())
    beat     = json.loads(Path(sys.argv[2]).read_text())
    name     = sys.argv[3]
    web_src  = sys.argv[4] if len(sys.argv) > 4 else "web/src"

    path = run(beat, paper, name, web_src)
    print(f"[custom_viz] done: {path}")
