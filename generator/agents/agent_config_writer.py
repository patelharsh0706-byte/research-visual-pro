from __future__ import annotations

"""
Agent 4 — Config Writer
========================
Input:  chart_plan (from agent_chart_selector) + paper_data
Output: config.ts string + page.mdx string

Responsibilities:
  - Write the TypeScript config object (hero, sections, theme, footer)
  - Write the MDX narrative (ScrollySection blocks)
  - Every stat cited in MDX must come from paper_data — no invention
  - Section IDs in MDX must exactly match config sections[].id

LLM: Claude Sonnet (writing; called once per paper)
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import llm
from schemas.viz_schemas import VIZ_SCHEMAS

SYSTEM_CONFIG = """\
You are an expert TypeScript developer writing scrollytelling config files.

Rules:
1. The output must be valid TypeScript that exports `export const config = { ... }`.
2. Every section id in sections[] must EXACTLY match a ScrollySection id in the MDX.
3. viz.key must be one of the valid registry keys provided.
4. viz.mount must match the schema for that key ("svg" or "div").
5. props must match the viz schema exactly — wrong prop shapes cause silent fallback to demo data.
6. hero.stats target values must be real numbers from the paper.
7. Return ONLY the TypeScript code block — no explanation, no markdown fences.
"""

SYSTEM_MDX = """\
You are a science communicator writing scrollytelling narratives for academic papers.

Rules:
1. Write one <ScrollySection id="BEAT_ID"> block per beat.
2. The id must EXACTLY match the beat_id from the chart_plan.
3. Every number or statistic cited must come from the paper_data provided — no invention.
4. Each section: 2-4 short paragraphs. Lead with the most surprising finding.
5. End each section with a <div class="data-source-tag">Source: ...</div>.
6. Use **bold** for key numbers and findings.
7. Import line at top: import ScrollySection from '../components/scrolly/ScrollySection.astro';
8. Frontmatter must include layout and configId.
9. Return ONLY the MDX content — no explanation, no code fences.
"""


def run(
    chart_plan: list[dict],
    paper_data: dict,
    slug: str,
    model: str = "claude-sonnet-4-6"
) -> tuple[str, str]:
    """
    Generate config.ts and page.mdx strings.
    Returns (config_ts, page_mdx).
    """
    config_ts = _write_config(chart_plan, paper_data, slug, model)
    page_mdx  = _write_mdx(chart_plan, paper_data, slug, model)

    return config_ts, page_mdx


def _write_config(
    chart_plan: list[dict],
    paper_data: dict,
    slug: str,
    model: str
) -> str:
    plan_summary = json.dumps([{
        "beat_id":        b["beat_id"],
        "headline":       b["headline"],
        "narrative_role": b.get("narrative_role", ""),
        "layout":         b.get("layout", "sidecar"),
        "theme_shift":    b.get("theme_shift", False),
        "viz_key":        b["viz_key"],
        "mount":          b["mount"],
        "animation_style":b.get("animation_style", "fade"),
        "metaphor":       b.get("metaphor", ""),
        "props":          b["props"],
    } for b in chart_plan], indent=2)

    paper_meta = {
        "title":   paper_data.get("title", ""),
        "authors": paper_data.get("authors", ""),
        "journal": paper_data.get("journal", ""),
        "year":    paper_data.get("year", ""),
        "doi":     paper_data.get("doi", ""),
    }

    # Pick 4 hero stats from the top numeric facts
    hero_stats = _pick_hero_stats(paper_data)

    prompt = f"""Write a TypeScript config file for this scrollytelling page.

Slug: {slug}
Paper: {json.dumps(paper_meta)}
Hero stats to use: {json.dumps(hero_stats)}

Chart plan (sections in order):
{plan_summary}

Valid viz registry keys and their mount types:
{json.dumps({k: v['mount'] for k, v in VIZ_SCHEMAS.items()}, indent=2)}

Requirements:
- Export `export const config = {{ ... }}`
- metadata.brand: a short punchy 3-word name for this paper's story
- hero.titleHtml: use <span class="hero-accent"> on 1-2 key words
- theme: pick accent + secondary colors appropriate for this paper's domain
- footerHtml: include paper title, authors, journal, DOI, and a link to the paper
- sections[].viz.key must match the chart plan exactly
- sections[].viz.props must match the chart plan exactly
- sections[].viz.animationStyle: copy from chart plan animation_style field
- sections[].navLabel: 1-2 word nav pill label
- sections[].layout: copy from chart plan ("sidecar" or "immersive")
- sections[].themeShift: copy from chart plan (boolean — true only on the immersive beat)
- For the immersive beat: write a more dramatic headline and teaserHtml that matches the emotional peak

Write ONLY the TypeScript code. No explanation."""

    ts = llm.call(prompt, system=SYSTEM_CONFIG, model=model)
    # Strip accidental fences
    ts = re.sub(r"^```(?:typescript|ts)?\n", "", ts)
    ts = re.sub(r"\n```$", "", ts)
    return ts


def _write_mdx(
    chart_plan: list[dict],
    paper_data: dict,
    slug: str,
    model: str
) -> str:
    beat_summaries = "\n".join(
        f"BEAT {i+1}: id={b['beat_id']}\n  headline={b['headline']}\n  finding={b['finding_text']}\n  data_refs={b['data_sourced_from']}"
        for i, b in enumerate(chart_plan)
    )

    compact_stats = "\n".join(
        f"  {s['value']}{s['unit']} — {s['context'][:120]}"
        for s in paper_data.get("stats", [])[:25]
    )

    prompt = f"""Write the MDX narrative for this scrollytelling page.

Slug: {slug}
Paper title: {paper_data.get('title', '')}
Authors: {paper_data.get('authors', '')}
Journal: {paper_data.get('journal', '')} ({paper_data.get('year', '')})

Narrative beats (in order):
{beat_summaries}

Paper statistics to draw on (only use these — do not invent numbers):
{compact_stats}

Requirements:
- Frontmatter: layout ../layouts/ScrollyLayout.astro, configId {slug}
- Import ScrollySection at the top
- One <ScrollySection id="BEAT_ID"> per beat
- Section label div: <div class="section-label">Section 0N</div>
- ## Heading matching the beat's headline
- 2-4 short paragraphs per section, citing specific numbers from paper statistics
- <div class="data-source-tag">Source: ...</div> at end of each section

Write ONLY the MDX content. No explanation."""

    mdx = llm.call(prompt, system=SYSTEM_MDX, model=model)
    mdx = re.sub(r"^```(?:mdx)?\n", "", mdx)
    mdx = re.sub(r"\n```$", "", mdx)
    return mdx


def _pick_hero_stats(paper_data: dict) -> list[dict]:
    """Pick 4 hero stats: prefer round numbers with units."""
    candidates = []
    for s in paper_data.get("stats", []):
        if s["unit"] and s["value"] > 1:
            candidates.append(s)
    # Sort by magnitude descending, take top 4
    candidates.sort(key=lambda s: s["value"], reverse=True)
    seen: set[str] = set()
    result = []
    for s in candidates:
        unit = s["unit"]
        if unit not in seen and len(result) < 4:
            seen.add(unit)
            result.append({
                "target": int(s["value"]) if s["value"] == int(s["value"]) else s["value"],
                "unit": unit,
                "label": s["context"][:40],
            })
    # Pad if needed
    while len(result) < 4:
        result.append({"target": 0, "unit": "", "label": "See paper"})
    return result


def write_files(config_ts: str, page_mdx: str, slug: str, web_src_dir: str) -> None:
    """Write both files to the Astro web/src/ directory."""
    base = Path(web_src_dir)
    config_path = base / "scrolly" / "data" / f"{slug}.ts"
    mdx_path    = base / "pages" / f"{slug}.mdx"

    config_path.parent.mkdir(parents=True, exist_ok=True)
    mdx_path.parent.mkdir(parents=True, exist_ok=True)

    config_path.write_text(config_ts)
    mdx_path.write_text(page_mdx)
    print(f"[config_writer] wrote {config_path}")
    print(f"[config_writer] wrote {mdx_path}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 agent_config_writer.py <paper_data.json> <chart_plan.json> <slug>")
        sys.exit(1)
    paper = json.loads(Path(sys.argv[1]).read_text())
    plan  = json.loads(Path(sys.argv[2]).read_text())
    slug  = sys.argv[3]
    ts, mdx = run(plan, paper, slug)
    print("=== CONFIG.TS ===")
    print(ts[:1000])
    print("=== PAGE.MDX ===")
    print(mdx[:1000])
