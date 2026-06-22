from __future__ import annotations

"""
Agent 2 — Story Planner
========================
Input:  paper_data dict (from agent_extractor)
Output: narrative_outline.json — list of 5-7 beats, each with:
          {beat_id, headline, finding_text, data_refs, suggested_data_type}

Responsibilities:
  - Decide the narrative arc: what does a non-expert reader need to understand?
  - Identify which finding/stat belongs in each beat
  - Tag each beat with a data type so agent_chart_selector can route it
  - Does NOT pick chart types or write props

LLM: Claude Opus (best reasoning; called once per paper)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import llm
from schemas.viz_schemas import DATA_TYPES

SYSTEM_PROMPT = """\
You are a science communicator who turns academic research into compelling visual stories.

Given structured data extracted from a research paper, your job is to design a 5-7 beat
scrollytelling narrative — the kind that makes a non-expert lean forward and keep reading.

Rules:
1. Each beat must be GROUNDED in a specific finding, statistic, or table from the paper.
   Never invent numbers. Quote the exact values from the paper data provided.
2. The narrative arc must follow: Hook → Problem → Method → Key Finding(s) → Implication.
3. Each beat gets ONE data type tag from this list:
   {data_types}
4. narrative_role must be one of: intro | problem | method | finding | implication
5. layout: exactly ONE beat in the paper must be flagged "immersive" — the single most
   dramatic, emotionally resonant finding. All others are "sidecar". Choose carefully.
6. theme_shift: only the immersive beat may set this to true. It signals a color palette
   change to mark the emotional peak of the narrative.
7. Return ONLY valid JSON — no markdown, no explanation outside the JSON.

Output format:
{{
  "beats": [
    {{
      "beat_id": "intro",
      "headline": "Short punchy verb-first headline (≤8 words, present tense)",
      "finding_text": "2-3 sentence narrative paragraph written for a non-expert. Lead with human implication before the statistic. No jargon.",
      "data_refs": ["exact quote or stat from paper, e.g. '7,000+ rare diseases'"],
      "suggested_data_type": "one of the data type keys above",
      "narrative_role": "one of: intro | problem | method | finding | implication",
      "layout": "sidecar or immersive (exactly one beat per paper must be immersive)",
      "theme_shift": false,
      "why": "one sentence: why this beat matters for the story"
    }}
  ]
}}
""".format(data_types="\n".join(f"  - {k}: {v}" for k, v in DATA_TYPES.items()))


def run(paper_data: dict, model: str = "claude-opus-4-8") -> list[dict]:
    """
    Call Claude to design the narrative outline.
    Returns list of beat dicts.
    """
    paper_context = _format_paper_context(paper_data)

    user_message = f"""Here is the extracted data from the research paper:

{paper_context}

Design a 5-7 beat scrollytelling narrative for this paper.
Each beat must reference specific numbers, findings, or data from the paper above.
Return only the JSON object."""

    print(f"[story_planner] calling {model}...")
    raw = llm.call(user_message, system=SYSTEM_PROMPT, model=model)

    # Strip accidental markdown fences
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:])
    if raw.endswith("```"):
        raw = "\n".join(raw.split("\n")[:-1])

    try:
        result = json.loads(raw)
        beats = result.get("beats", result if isinstance(result, list) else [])
        print(f"[story_planner] {len(beats)} beats planned")
        return beats
    except json.JSONDecodeError as e:
        print(f"[story_planner] JSON parse error: {e}")
        print(f"[story_planner] raw response:\n{raw[:500]}")
        return []


def _format_paper_context(paper_data: dict) -> str:
    parts = [
        f"TITLE: {paper_data.get('title', 'Unknown')}",
        f"AUTHORS: {paper_data.get('authors', '')}",
        f"JOURNAL: {paper_data.get('journal', '')} ({paper_data.get('year', '')})",
        "",
        "ABSTRACT:",
        paper_data.get("abstract", "")[:1500],
        "",
    ]

    if paper_data.get("stats"):
        parts.append("KEY STATISTICS (use these for data_refs):")
        for s in paper_data["stats"][:25]:
            parts.append(f"  {s['value']}{s['unit']}  -- \"{s['context'][:100]}\"")
        parts.append("")

    if paper_data.get("tables"):
        parts.append("TABLES:")
        for t in paper_data["tables"][:5]:
            parts.append(f"  {t['caption']}")
            if t.get("headers"):
                parts.append(f"  Columns: {', '.join(t['headers'])}")
            for row in t.get("rows", [])[:3]:
                parts.append(f"    {row}")
        parts.append("")

    if paper_data.get("figures"):
        parts.append("FIGURE CAPTIONS:")
        for f in paper_data["figures"][:8]:
            parts.append(f"  {f['number']}: {f['caption'][:150]}")
        parts.append("")

    return "\n".join(parts)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 agent_story_planner.py <paper_data.json>")
        sys.exit(1)
    data = json.loads(Path(sys.argv[1]).read_text())
    beats = run(data)
    print(json.dumps(beats, indent=2))
