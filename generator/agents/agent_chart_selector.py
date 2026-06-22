from __future__ import annotations

"""
Agent 3 — Chart Selector
=========================
Input:  beats (from agent_story_planner) + paper_data
Output: chart_plan.json — beats with viz_key and props_skeleton filled in

Responsibilities:
  - For each beat, look at suggested_data_type + data_refs
  - Route to the best viz key from viz_schemas.py
  - Extract the specific data rows/values needed for that viz's props
  - Flag beats where no existing viz fits (for agent_custom_viz)

LLM: Claude Sonnet (data extraction + routing; called once per beat)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import llm
from schemas.viz_schemas import (
    VIZ_SCHEMAS,
    format_schema_for_prompt,
    get_viz_keys_for_data_type,
)

# ── Deterministic routing rules (no LLM needed) ───────────────────────────────
ROUTING_RULES: dict[str, str] = {
    "comparison":   "bars",
    "time_series":  "timeline",
    "distribution": "precision",
    "network":      "sem",
    "spatial":      "map",
    "table":        "matrix",
    "gauge":        "accuracy",
    "hierarchy":    "upgrade",
    "scatter":      "scatter",
    "sentiment":    "sentiment",
}

SYSTEM_PROMPT = """\
You are a creative data visualization expert and science communicator for academic scrollytelling.

For each narrative beat, follow these steps in order:

STEP 1 — THINK IN METAPHORS FIRST.
Before touching the viz registry, ask: "What physical or spatial metaphor captures this finding
for someone who has never read a research paper?"
Examples of good metaphor thinking:
  - Drug attrition over trials → a funnel that leaks at every stage
  - Knowledge flowing back from licensee to licensor → a river reversing course
  - Before/after matching → two worlds side by side that converge
  - Citation network → light radiating outward from a source
Write your metaphor answer in the "metaphor" field.

STEP 2 — PICK THE VIZ.
If the metaphor maps to an existing viz key → use it.
If the metaphor demands something the existing keys can't represent → set viz_key to "custom"
and write a detailed visual_brief describing exactly what Agent 6 should build.
Avoid defaulting to "bars" for the immersive beat — it must be custom or a visually expressive type.
No more than 2 sections across the whole paper may use the same viz_key.

STEP 3 — PICK ANIMATION STYLE.
Choose one animation_style for how this viz enters when the reader scrolls to it:
  - fly_in:  elements animate up from below (good for reveals, bar charts)
  - morph:   elements scale + unblur into view (good for diagrams, networks)
  - cascade: elements appear left-to-right with stagger (good for comparisons)
  - count_up: numbers animate from zero (good for stat-heavy sections)
  - fade:    simple opacity transition (default, works for everything)

STEP 4 — EXTRACT PROPS.
Extract ONLY data explicitly stated in the paper_data — never invent numbers.
Map to the exact props shape required by the viz schema.

Return ONLY valid JSON. No markdown. No explanation outside the JSON.

Output per beat:
{{
  "beat_id": "same as input",
  "metaphor": "one sentence describing the visual metaphor you chose",
  "viz_key": "one of the registry keys, or 'custom'",
  "mount": "svg or div",
  "animation_style": "fly_in | morph | cascade | count_up | fade",
  "visual_brief": "only if viz_key is 'custom' — detailed description for the D3 artist",
  "props": {{ ... exact props matching the viz schema ... }},
  "data_sourced_from": ["list of exact quotes/stats used"]
}}
"""


def run(beats: list[dict], paper_data: dict, model: str = "claude-sonnet-4-6") -> list[dict]:
    """
    Route each beat to a viz key and extract props.
    Uses deterministic rules first; falls back to LLM for ambiguous cases.
    """
    chart_plan = []

    for beat in beats:
        beat_id = beat.get("beat_id", "unknown")
        data_type = beat.get("suggested_data_type", "")

        # Deterministic fast-path
        candidate_key = ROUTING_RULES.get(data_type)

        if candidate_key and _has_required_data(candidate_key, beat, paper_data):
            print(f"[chart_selector] {beat_id} → {candidate_key} (deterministic)")
            props = _extract_props_llm(beat, paper_data, candidate_key, model)
        else:
            # LLM selects and extracts
            candidates = get_viz_keys_for_data_type(data_type) or list(VIZ_SCHEMAS.keys())
            print(f"[chart_selector] {beat_id} → LLM routing (candidates: {candidates})")
            props_result = _route_and_extract_llm(beat, paper_data, candidates, model)
            candidate_key = props_result.get("viz_key", "upgrade")
            props = props_result

        chart_plan.append({
            "beat_id":        beat_id,
            "headline":       beat.get("headline", ""),
            "finding_text":   beat.get("finding_text", ""),
            "narrative_role": beat.get("narrative_role", ""),
            "layout":         beat.get("layout", "sidecar"),
            "theme_shift":    beat.get("theme_shift", False),
            "viz_key":        candidate_key,
            "mount":          VIZ_SCHEMAS.get(candidate_key, {}).get("mount", "svg"),
            "animation_style":props.get("animation_style", "fade"),
            "metaphor":       props.get("metaphor", ""),
            "visual_brief":   props.get("visual_brief", props.get("custom_description", "")),
            "props":          props.get("props", {}),
            "data_sourced_from": props.get("data_sourced_from", beat.get("data_refs", [])),
        })

    print(f"[chart_selector] planned {len(chart_plan)} sections")
    return chart_plan


def _has_required_data(viz_key: str, beat: dict, paper_data: dict) -> bool:
    """Quick check: does the paper data plausibly have what this viz needs?"""
    schema = VIZ_SCHEMAS.get(viz_key, {})
    required = schema.get("required_props", {})

    # Heuristic: if there are required props, check paper has enough numeric stats or tables
    if "data" in required:
        return len(paper_data.get("stats", [])) > 0 or len(paper_data.get("tables", [])) > 0
    if "nodes" in required:
        return True   # SEM nodes are hand-designed, always possible
    return True


def _extract_props_llm(
    beat: dict,
    paper_data: dict,
    viz_key: str,
    model: str
) -> dict:
    """Ask LLM to extract props for a known viz key."""
    schema_text = format_schema_for_prompt(viz_key)
    context = _compact_paper_context(paper_data, beat)

    prompt = f"""Beat to visualize:
Headline: {beat.get('headline')}
Finding: {beat.get('finding_text')}
Data refs: {beat.get('data_refs', [])}

Assigned viz key: {viz_key}

Viz schema:
{schema_text}

Paper data (use ONLY these numbers):
{context}

Extract the exact props object for this viz. Use only values explicitly stated in the paper data.
Return JSON: {{"viz_key": "{viz_key}", "props": {{...}}, "data_sourced_from": [...]}}"""

    raw = llm.call(prompt, system=SYSTEM_PROMPT, model=model)
    return _parse_json(raw)


def _route_and_extract_llm(
    beat: dict,
    paper_data: dict,
    candidates: list[str],
    model: str
) -> dict:
    """Ask LLM to pick the best viz key AND extract props."""
    schemas_text = "\n\n".join(format_schema_for_prompt(k) for k in candidates[:6])
    context = _compact_paper_context(paper_data, beat)

    prompt = f"""Beat to visualize:
Headline: {beat.get('headline')}
Finding: {beat.get('finding_text')}
Data refs: {beat.get('data_refs', [])}

Available viz schemas:
{schemas_text}

Paper data (use ONLY these numbers):
{context}

Pick the best viz_key and extract its props. Return JSON:
{{"viz_key": "chosen_key", "mount": "svg or div", "props": {{...}}, "data_sourced_from": [...]}}"""

    raw = llm.call(prompt, system=SYSTEM_PROMPT, model=model)
    return _parse_json(raw)


def _compact_paper_context(paper_data: dict, beat: dict) -> str:
    """Compact context focused on what's relevant to this beat."""
    lines = []
    # Key stats
    for s in paper_data.get("stats", [])[:20]:
        lines.append(f"  {s['value']}{s['unit']} — {s['context'][:80]}")
    # Tables
    for t in paper_data.get("tables", [])[:3]:
        lines.append(f"  TABLE: {t['caption']}")
        if t.get("rows"):
            for row in t["rows"][:5]:
                lines.append(f"    {row}")
    return "\n".join(lines) if lines else "(no structured data extracted)"


def _parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = "\n".join(text.split("\n")[1:])
    if text.endswith("```"):
        text = "\n".join(text.split("\n")[:-1])
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"viz_key": "upgrade", "props": {}, "data_sourced_from": []}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 agent_chart_selector.py <paper_data.json> <beats.json>")
        sys.exit(1)
    paper = json.loads(Path(sys.argv[1]).read_text())
    beats = json.loads(Path(sys.argv[2]).read_text())
    plan = run(beats, paper)
    print(json.dumps(plan, indent=2))
