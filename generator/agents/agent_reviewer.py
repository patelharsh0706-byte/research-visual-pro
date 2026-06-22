from __future__ import annotations

"""
Agent 7 — Final Reviewer
=========================
Input:  config_ts string + paper_data dict + slug
Output: patched config_ts string that passes all benchmark checks

Benchmark: drug-repurposing-pushpakom-2019.ts (the gold-standard page)

Checklist (derived from benchmark):
  metadata:  title, description, brand, homeNavUrl
  hero:      label, titleHtml, subtitleHtml, authorsHtml, teaserHtml, ctaHref, stats (4 entries)
  sections[]: navLabel, mobileLabel, viz.title, viz.captionHtml  (per section)
  footerHtml: footer-inner > footer-thesis + footer-meta + footer-actions (.footer-btn)

LLM: Claude Sonnet (fill-in; one call per missing field group)
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import llm

# ── Benchmark structure (derived from drug-repurposing gold standard) ─────────

BENCHMARK_HERO_FIELDS = ["label", "titleHtml", "subtitleHtml", "authorsHtml", "teaserHtml", "ctaHref"]
BENCHMARK_METADATA_FIELDS = ["title", "description", "brand", "homeNavUrl"]
BENCHMARK_SECTION_VIZ_FIELDS = ["title", "captionHtml"]
BENCHMARK_SECTION_FIELDS = ["navLabel", "mobileLabel"]

# Visual rendering limits (derived from fixed D3 legend spacing in bars.ts + sem.ts)
BARS_LABEL_MAX_CHARS = 25   # bars.ts legend: i * 220px — each slot fits ~25 chars at 10px Inter
SEM_LEGEND_MAX_CHARS = 40   # sem.ts: first item starts at x=30; second starts at x=335 (305px gap)

FOOTER_TEMPLATE = """\
`
    <div class="footer-inner">
      <div class="footer-thesis">
        <div class="footer-label">Full Research Paper</div>
        <p><em>{paper_title}</em></p>
      </div>
      <div class="footer-meta">
        <p><strong>Authors:</strong> {authors}</p>
        <p><strong>Journal:</strong> {journal}, {year}</p>
        <p><strong>DOI:</strong> {doi}</p>
      </div>
      <div class="footer-actions">
        <a href="https://doi.org/{doi}" target="_blank" class="footer-btn">Read the Paper</a>
      </div>
    </div>
  `"""

SYSTEM_REVIEWER = """\
You are a TypeScript config editor for academic scrollytelling pages.

Your job is to PATCH a TypeScript config object by filling in ONLY the fields listed
as missing. Do not change any existing fields or props. Do not change section IDs or
viz keys. Return the COMPLETE patched TypeScript config — no explanation, no fences.

Rules:
- hero.label: short journal + year pill, e.g. "Nature Reviews Drug Discovery · 2019"
- hero.subtitleHtml: the paper's subtitle or a short punchy descriptor (≤8 words)
- hero.authorsHtml: "LastName et al. · Institution" — infer from paper_data.authors
- hero.teaserHtml: 1-2 sentence hook with <strong> on the most striking stat
- hero.ctaHref: "#section-" + first section id
- metadata.title: same as paper title
- metadata.description: 1-sentence description for SEO
- metadata.homeNavUrl: always "/"
- sections[].mobileLabel: 1-2 word short form of navLabel
- sections[].viz.title: punchy 4-6 word title for the visualization panel
- sections[].viz.captionHtml: 2-3 sentences explaining what the chart shows and what to look for
- footerHtml: use the exact HTML structure with classes footer-inner, footer-thesis,
  footer-label, footer-meta, footer-actions, footer-btn
- bars series labels: max 25 chars — the D3 legend allocates 220px per slot at 10px Inter font
- sem sigLabel / insigLabel: max 40 chars — legend slots are 305px apart starting at x=30
- hero.stats: must have ≥3 entries, each with target (number), unit (string), label (string)
"""


def run(
    config_ts: str,
    paper_data: dict,
    slug: str,
    model: str = "claude-sonnet-4-6",
) -> str:
    """
    Audit config_ts against the benchmark checklist and fill in any missing fields.
    Returns the patched config_ts string.
    """
    gaps = _audit(config_ts)

    if not gaps["any"]:
        print("[reviewer] config passes all benchmark checks — nothing to patch", file=__import__('sys').stderr)
        return config_ts

    print(f"[reviewer] gaps found: {gaps['summary']}", file=__import__('sys').stderr)

    patched = _patch(config_ts, paper_data, slug, gaps, model)
    print("[reviewer] patched config written", file=__import__('sys').stderr)
    return patched


def _audit(config_ts: str) -> dict:
    """Check the config TS string for missing benchmark fields."""
    gaps: dict = {
        "metadata": [],
        "hero": [],
        "sections": [],   # list of {section_id, missing_viz_fields, missing_section_fields}
        "footer": False,
        "any": False,
        "summary": "",
    }

    # metadata checks
    for field in BENCHMARK_METADATA_FIELDS:
        if not re.search(rf'\b{re.escape(field)}\s*:', config_ts):
            gaps["metadata"].append(field)

    # hero checks
    for field in BENCHMARK_HERO_FIELDS:
        # look for field inside the hero: { ... } block
        hero_block = _extract_block(config_ts, "hero")
        if hero_block and not re.search(rf'\b{re.escape(field)}\s*:', hero_block):
            gaps["hero"].append(field)

    # section checks
    section_ids = re.findall(r'id:\s*["\']([^"\']+)["\']', _extract_block(config_ts, "sections") or "")
    # only section-level ids (heuristic: skip ids inside props)
    section_ids = _filter_section_ids(config_ts, section_ids)

    for sid in section_ids:
        sec_block = _extract_section_block(config_ts, sid)
        if not sec_block:
            continue
        missing_viz = []
        missing_sec = []
        viz_block = _extract_block(sec_block, "viz")
        for field in BENCHMARK_SECTION_VIZ_FIELDS:
            if viz_block and not re.search(rf'\b{re.escape(field)}\s*:', viz_block):
                missing_viz.append(field)
        for field in BENCHMARK_SECTION_FIELDS:
            if not re.search(rf'\b{re.escape(field)}\s*:', sec_block):
                missing_sec.append(field)
        if missing_viz or missing_sec:
            gaps["sections"].append({
                "id": sid,
                "missing_viz": missing_viz,
                "missing_section": missing_sec,
            })

    # footer check
    if "footer-inner" not in config_ts or "footer-btn" not in config_ts:
        gaps["footer"] = True

    # hero stats count check (benchmark: ≥3 stats)
    hero_block = _extract_block(config_ts, "hero")
    gaps["hero_stats_count"] = 0
    if hero_block:
        stats_block = _extract_block(hero_block, "stats")
        if stats_block:
            gaps["hero_stats_count"] = len(re.findall(r'target\s*:', stats_block))
    if gaps["hero_stats_count"] < 3:
        gaps["hero"].append("stats (need ≥3 entries with target/unit/label)")

    # per-section visual quality checks (legend label lengths)
    gaps["visual"] = []
    for sid in section_ids:
        sec_block = _extract_section_block(config_ts, sid)
        if not sec_block:
            continue
        viz_block = _extract_block(sec_block, "viz")
        if not viz_block:
            continue
        viz_key_m = re.search(r'\bkey\s*:\s*["\']([^"\']+)["\']', viz_block)
        if not viz_key_m:
            continue
        viz_key = viz_key_m.group(1)
        props_block = _extract_block(viz_block, "props") or ""

        if viz_key == "bars":
            long_labels = re.findall(
                r'\blabel\s*:\s*["\']([^"\']{' + str(BARS_LABEL_MAX_CHARS + 1) + r',})["\']',
                props_block,
            )
            if long_labels:
                gaps["visual"].append({
                    "section_id": sid, "viz_key": "bars",
                    "issue": f"series label(s) too long (>{BARS_LABEL_MAX_CHARS} chars): {long_labels}",
                    "fix": f"Shorten each bars series label to ≤{BARS_LABEL_MAX_CHARS} chars",
                })

        elif viz_key == "sem":
            legend_block = _extract_block(props_block, "legend") or ""
            for legend_field in ("sigLabel", "insigLabel"):
                m = re.search(rf'\b{legend_field}\s*:\s*["\']([^"\']+)["\']', legend_block)
                if m and len(m.group(1)) > SEM_LEGEND_MAX_CHARS:
                    gaps["visual"].append({
                        "section_id": sid, "viz_key": "sem",
                        "issue": f"{legend_field} too long ({len(m.group(1))} chars, max {SEM_LEGEND_MAX_CHARS}): '{m.group(1)}'",
                        "fix": f"Shorten {legend_field} to ≤{SEM_LEGEND_MAX_CHARS} chars",
                    })

    # summary
    parts = []
    if gaps["metadata"]:
        parts.append(f"metadata missing: {gaps['metadata']}")
    if gaps["hero"]:
        parts.append(f"hero missing: {gaps['hero']}")
    if gaps["sections"]:
        parts.append(f"{len(gaps['sections'])} sections missing fields")
    if gaps["footer"]:
        parts.append("footer needs restructure")
    if gaps["visual"]:
        parts.append(f"{len(gaps['visual'])} visual quality issue(s)")
    gaps["any"] = bool(parts)
    gaps["summary"] = "; ".join(parts) if parts else "none"
    return gaps


def _patch(
    config_ts: str,
    paper_data: dict,
    slug: str,
    gaps: dict,
    model: str,
) -> str:
    """Call LLM once to fill in all gaps and return the complete patched config."""

    gap_instructions = _build_gap_instructions(gaps, paper_data, slug)

    paper_meta = {
        "title": paper_data.get("title", ""),
        "authors": paper_data.get("authors", ""),
        "journal": paper_data.get("journal", ""),
        "year": paper_data.get("year", ""),
        "doi": paper_data.get("doi", ""),
        "abstract": paper_data.get("abstract", "")[:600],
    }

    key_stats = [
        f"  {s['value']}{s['unit']} — {s['context'][:80]}"
        for s in paper_data.get("stats", [])[:15]
    ]

    prompt = f"""You are patching this TypeScript config to add missing fields.

Paper metadata:
{json.dumps(paper_meta, indent=2)}

Key stats from paper:
{chr(10).join(key_stats)}

Current config (patch this — do not change existing content):
{config_ts}

GAPS TO FILL — add ONLY these fields, exactly where they belong in the structure:
{gap_instructions}

Return the complete patched TypeScript config. No markdown fences. No explanation."""

    raw = llm.call(prompt, system=SYSTEM_REVIEWER, model=model)

    # Strip accidental fences
    raw = re.sub(r"^```(?:typescript|ts)?\n?", "", raw.strip())
    raw = re.sub(r"\n?```$", "", raw)
    return raw.strip()


def _build_gap_instructions(gaps: dict, paper_data: dict, slug: str) -> str:
    lines = []

    if gaps["metadata"]:
        lines.append(f"ADD to metadata: {gaps['metadata']}")

    if gaps["hero"]:
        lines.append(f"ADD to hero: {gaps['hero']}")
        lines.append("  - hero.ctaHref should be '#section-' + first section id")
        lines.append("  - hero.teaserHtml: 1-2 sentences with <strong> on best stat")

    for sec in gaps["sections"]:
        sid = sec["id"]
        if sec["missing_section"]:
            lines.append(f"Section '{sid}': ADD {sec['missing_section']}")
        if sec["missing_viz"]:
            lines.append(f"Section '{sid}' viz: ADD {sec['missing_viz']}")
            lines.append(f"  - viz.title: 4-6 words, punchy label for the chart")
            lines.append(f"  - viz.captionHtml: 2-3 sentences explaining chart + what to look for")

    if gaps["footer"]:
        doi = paper_data.get("doi", "")
        authors = paper_data.get("authors", "")
        journal = paper_data.get("journal", "")
        year = paper_data.get("year", "")
        title = paper_data.get("title", "")
        footer = FOOTER_TEMPLATE.format(
            paper_title=title,
            authors=authors[:80],
            journal=journal,
            year=year,
            doi=doi,
        )
        lines.append(f"REPLACE footerHtml with this exact structure:\nfooterHtml: {footer}")

    for v in gaps.get("visual", []):
        lines.append(f"Section '{v['section_id']}' ({v['viz_key']}): {v['fix']}")
        lines.append(f"  Issue: {v['issue']}")

    return "\n".join(lines)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_block(text: str, key: str) -> str | None:
    """Extract the content of key: { ... } from a TS string."""
    pattern = rf'\b{re.escape(key)}\s*:\s*[\[{{]'
    m = re.search(pattern, text)
    if not m:
        return None
    start = m.end() - 1
    open_ch = text[start]
    close_ch = ']' if open_ch == '[' else '}'
    depth = 0
    for i in range(start, len(text)):
        if text[i] == open_ch:
            depth += 1
        elif text[i] == close_ch:
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return None


def _extract_section_block(config_ts: str, section_id: str) -> str | None:
    """Extract the { ... } block for a specific section by its id."""
    pattern = rf'id:\s*["\'{re.escape(section_id)}["\']'
    m = re.search(rf'id:\s*["\']({re.escape(section_id)})["\']', config_ts)
    if not m:
        return None
    # Walk back to find the opening { of this section object
    start = config_ts.rfind('{', 0, m.start())
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(config_ts)):
        if config_ts[i] == '{':
            depth += 1
        elif config_ts[i] == '}':
            depth -= 1
            if depth == 0:
                return config_ts[start:i + 1]
    return None


def _filter_section_ids(config_ts: str, all_ids: list[str]) -> list[str]:
    """
    Keep only section-level ids — ids that appear as direct children of sections[].
    Heuristic: the sections[] block starts with 'sections: [' and each section
    starts with a '{' followed (within ~200 chars) by 'id:'.
    Exclude ids that appear inside nested structures like nodes[].
    """
    sections_block = _extract_block(config_ts, "sections")
    if not sections_block:
        return []

    # Find ids that appear at section depth (depth=1 inside sections[])
    section_ids = []
    depth = 0
    i = 0
    while i < len(sections_block):
        ch = sections_block[i]
        if ch in '[{':
            depth += 1
        elif ch in ']}':
            depth -= 1
        # At depth=2 we're inside a section object; id: at depth=2 is section-level
        if depth == 2:
            id_match = re.match(r'\s*id:\s*["\']([^"\']+)["\']', sections_block[i:i+50])
            if id_match:
                section_ids.append(id_match.group(1))
                i += len(id_match.group(0))
                continue
        i += 1
    return section_ids


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 agent_reviewer.py <config.ts> <paper_data.json>")
        sys.exit(1)
    config = Path(sys.argv[1]).read_text()
    paper = json.loads(Path(sys.argv[2]).read_text())
    slug = Path(sys.argv[1]).stem
    patched = run(config, paper, slug)
    print(patched)
