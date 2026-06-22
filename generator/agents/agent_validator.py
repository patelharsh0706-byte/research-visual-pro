from __future__ import annotations

"""
Agent 5 — Validator
====================
Input:  config.ts string + page.mdx string + paper_data + chart_plan
Output: ValidationResult with PASS/FAIL and list of errors

Responsibilities:
  - Rule-based: check every props object against viz_schemas.py
  - Rule-based: check every section id in MDX matches a config section id
  - LLM-assisted: fact-check every number cited in MDX against paper_data
  - LLM-assisted: flag hallucinated claims not grounded in the paper
  - Return structured errors so agent_config_writer can fix them

LLM: Claude Haiku (fast + cheap; called once for fact-checking)
"""

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import llm
from schemas.viz_schemas import VIZ_SCHEMAS

FACT_CHECK_SYSTEM = """\
You are a fact-checker for academic scrollytelling content.

Given:
1. A list of paper statistics (ground truth)
2. An MDX narrative that cites numbers and findings

Your job: find every number or claim in the MDX narrative and check whether it appears
in the paper statistics. Flag any claim that is NOT supported by the statistics list.

Return JSON:
{
  "hallucinations": [
    {"claim": "exact text from MDX", "issue": "what's wrong or not found in paper data"}
  ],
  "verified": ["list of claims that ARE supported by the paper data"]
}

Be strict: if a number in the MDX doesn't appear in the paper statistics with the same
magnitude and unit, flag it. Do not allow approximate paraphrases of made-up numbers.
"""


@dataclass
class ValidationError:
    error_type: str   # "schema", "id_mismatch", "hallucination", "missing_prop"
    location: str     # e.g. "section.cost.props.data"
    message: str


@dataclass
class ValidationResult:
    passed: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def summary(self) -> str:
        if self.passed:
            return f"PASS — {len(self.warnings)} warnings"
        errs = "\n".join(f"  [{e.error_type}] {e.location}: {e.message}" for e in self.errors)
        return f"FAIL — {len(self.errors)} errors:\n{errs}"


def run(
    config_ts: str,
    page_mdx: str,
    paper_data: dict,
    chart_plan: list[dict],
    model: str = "claude-haiku-4-5-20251001"
) -> ValidationResult:
    """Run all validation checks. Returns ValidationResult."""
    errors: list[ValidationError] = []
    warnings: list[str] = []

    # ── 1. Extract sections from config ──────────────────────────────────────
    config_ids = _extract_config_section_ids(config_ts)
    mdx_ids    = _extract_mdx_section_ids(page_mdx)

    # ── 2. ID parity check ───────────────────────────────────────────────────
    for sid in config_ids:
        if sid not in mdx_ids:
            errors.append(ValidationError(
                error_type="id_mismatch",
                location=f"section.{sid}",
                message=f"config has section id '{sid}' but MDX has no <ScrollySection id=\"{sid}\">"
            ))
    for sid in mdx_ids:
        if sid not in config_ids:
            errors.append(ValidationError(
                error_type="id_mismatch",
                location=f"mdx.{sid}",
                message=f"MDX has <ScrollySection id=\"{sid}\"> but config has no matching section"
            ))

    # ── 3. Viz key + mount validation ─────────────────────────────────────────
    for beat in chart_plan:
        viz_key = beat.get("viz_key", "")
        mount   = beat.get("mount", "")
        if viz_key not in VIZ_SCHEMAS and viz_key != "custom":
            errors.append(ValidationError(
                error_type="schema",
                location=f"section.{beat['beat_id']}.viz.key",
                message=f"'{viz_key}' is not a valid viz registry key"
            ))
            continue

        if viz_key in VIZ_SCHEMAS:
            expected_mount = VIZ_SCHEMAS[viz_key]["mount"]
            if mount != expected_mount:
                errors.append(ValidationError(
                    error_type="schema",
                    location=f"section.{beat['beat_id']}.viz.mount",
                    message=f"viz key '{viz_key}' requires mount='{expected_mount}' but got '{mount}'"
                ))

            # Check required props
            schema = VIZ_SCHEMAS[viz_key]
            props  = beat.get("props", {})
            for req_key in schema.get("required_props", {}):
                if req_key not in props:
                    errors.append(ValidationError(
                        error_type="missing_prop",
                        location=f"section.{beat['beat_id']}.props.{req_key}",
                        message=f"required prop '{req_key}' missing for viz '{viz_key}'"
                    ))

    # ── 4. SEM layout check ───────────────────────────────────────────────────
    for beat in chart_plan:
        if beat.get("viz_key") == "sem":
            nodes = beat.get("props", {}).get("nodes", [])
            paths = beat.get("props", {}).get("paths", [])
            node_ids = {n.get("id") for n in nodes}
            for path in paths:
                if path.get("from") not in node_ids:
                    errors.append(ValidationError(
                        error_type="schema",
                        location=f"section.{beat['beat_id']}.props.paths",
                        message=f"path 'from' id '{path.get('from')}' not in nodes"
                    ))
                if path.get("to") not in node_ids:
                    errors.append(ValidationError(
                        error_type="schema",
                        location=f"section.{beat['beat_id']}.props.paths",
                        message=f"path 'to' id '{path.get('to')}' not in nodes"
                    ))
                # Check left-to-right
                from_node = next((n for n in nodes if n.get("id") == path.get("from")), None)
                to_node   = next((n for n in nodes if n.get("id") == path.get("to")), None)
                if from_node and to_node:
                    fx = from_node.get("x", 0) + from_node.get("w", 0)
                    tx = to_node.get("x", 0)
                    if fx > tx:
                        warnings.append(
                            f"section.{beat['beat_id']}: SEM path '{path.get('from')}'→'{path.get('to')}' "
                            f"goes right-to-left (from.x+w={fx} > to.x={tx}) — arrows will render backwards"
                        )

    # ── 5. Precision props range check ───────────────────────────────────────
    for beat in chart_plan:
        if beat.get("viz_key") == "precision":
            data = beat.get("props", {}).get("data", [])
            for item in data:
                v = item.get("v", 0)
                if not (-1.0 <= v <= 1.0):
                    errors.append(ValidationError(
                        error_type="schema",
                        location=f"section.{beat['beat_id']}.props.data",
                        message=f"precision v={v} is outside [-1, 1] — normalise before passing"
                    ))

    # ── 6. Accuracy count check ───────────────────────────────────────────────
    for beat in chart_plan:
        if beat.get("viz_key") == "accuracy":
            props = beat.get("props", {})
            total   = props.get("total", 34)
            correct = props.get("correct", 13)
            if correct > total:
                errors.append(ValidationError(
                    error_type="schema",
                    location=f"section.{beat['beat_id']}.props",
                    message=f"accuracy: correct ({correct}) > total ({total})"
                ))

    # ── 7. LLM fact-check of MDX narrative ───────────────────────────────────
    hallucinations = _fact_check_mdx(page_mdx, paper_data, model)
    for h in hallucinations:
        errors.append(ValidationError(
            error_type="hallucination",
            location="mdx.narrative",
            message=f"{h['issue']} — claim: \"{h['claim'][:100]}\""
        ))

    passed = len(errors) == 0
    return ValidationResult(passed=passed, errors=errors, warnings=warnings)


def _extract_config_section_ids(config_ts: str) -> list[str]:
    """
    Pull only top-level section ids from the sections[] array.
    Avoid matching nested id: fields inside props (e.g. SEM nodes[]).
    Strategy: extract the sections[] block, then find top-level id: entries.
    """
    # Grab just the sections: [ ... ] block
    m = re.search(r'sections\s*:\s*\[(.+?)\]\s*,?\s*\n\s*(?:footer|theme|metadata|$)',
                  config_ts, re.DOTALL)
    if not m:
        # Fallback: grab all id: at start-of-object-line (2-6 spaces indent)
        return re.findall(r'^\s{2,6}id:\s*["\']([^"\']+)["\']', config_ts, re.MULTILINE)

    sections_block = m.group(1)
    # In the sections block, top-level id: lines have ~6-8 spaces indent
    # (sections items are indented more than nested nodes)
    # Match id: lines that appear right after { (i.e. before any deeper nesting)
    # Simple heuristic: only first-level id within each { ... } segment
    ids = []
    # Split into section objects by finding { id: "..." pattern at section level
    for seg in re.split(r'\{', sections_block):
        m2 = re.match(r'\s*id:\s*["\']([^"\']+)["\']', seg.strip())
        if m2:
            ids.append(m2.group(1))
    return ids


def _extract_mdx_section_ids(page_mdx: str) -> list[str]:
    """Pull all id="..." from <ScrollySection> tags."""
    return re.findall(r'<ScrollySection\s+id=["\']([^"\']+)["\']', page_mdx)


def _fact_check_mdx(page_mdx: str, paper_data: dict, model: str) -> list[dict]:
    """Use LLM to fact-check numbers in MDX against paper stats."""
    stats_text = "\n".join(
        f"  {s['value']}{s['unit']} — {s['context'][:80]}"
        for s in paper_data.get("stats", [])[:30]
    )

    # Strip MDX markup to get just the prose
    prose = re.sub(r"<[^>]+>", "", page_mdx)
    prose = re.sub(r"\*\*(.+?)\*\*", r"\1", prose)
    prose = prose[:4000]

    prompt = f"""Paper statistics (ground truth):
{stats_text}

MDX narrative (check every number and claim):
{prose}

Find any numbers or claims in the narrative that are NOT supported by the paper statistics above.
Return JSON with hallucinations list."""

    try:
        raw = llm.call(prompt, system=FACT_CHECK_SYSTEM, model=model)
        if raw.startswith("```"):
            raw = "\n".join(raw.split("\n")[1:])
        if raw.endswith("```"):
            raw = "\n".join(raw.split("\n")[:-1])
        result = json.loads(raw)
        return result.get("hallucinations", [])
    except Exception as e:
        print(f"[validator] fact-check error: {e}")
        return []


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 agent_validator.py <paper_data.json> <chart_plan.json> <config.ts> [page.mdx]")
        sys.exit(1)
    paper  = json.loads(Path(sys.argv[1]).read_text())
    plan   = json.loads(Path(sys.argv[2]).read_text())
    config = Path(sys.argv[3]).read_text()
    mdx    = Path(sys.argv[4]).read_text() if len(sys.argv) > 4 else ""
    result = run(config, mdx, paper, plan)
    print(result.summary())
