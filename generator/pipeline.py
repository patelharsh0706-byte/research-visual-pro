from __future__ import annotations

"""
pipeline.py — Orchestrator
===========================
Usage:
    python3 pipeline.py <pdf_path> [--slug <slug>] [--web-src <path>] [--out <dir>]

Runs all 6 agents in sequence:
  1. Extractor   — PDF → paper_data.json
  2. StoryPlanner— paper_data → beats
  3. ChartSelector— beats → chart_plan (viz_key + props per section)
  4. ConfigWriter— chart_plan → config.ts + page.mdx
  5. Validator   — validate + fact-check (loops back to ConfigWriter on FAIL, max 2 tries)
  6. CustomViz   — (optional) writes custom D3 modules for beats flagged viz_key=custom

Environment:
    ANTHROPIC_API_KEY   required for agents 2–6
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Add generator root to path
sys.path.insert(0, str(Path(__file__).parent))

from agents import (
    agent_chart_selector,
    agent_config_writer,
    agent_custom_viz,
    agent_extractor,
    agent_reviewer,
    agent_story_planner,
    agent_validator,
)

DEFAULT_WEB_SRC = str(Path(__file__).parent.parent / "web" / "src")


def slugify(title: str) -> str:
    """Convert a paper title to a URL-safe slug."""
    s = title.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s.strip())
    s = re.sub(r"-+", "-", s)
    return s[:60]


def run(
    pdf_path: str,
    slug: str | None = None,
    web_src_dir: str = DEFAULT_WEB_SRC,
    out_dir: str | None = None,
    max_validator_retries: int = 2,
) -> dict:
    """
    Full pipeline. Returns a result dict with paths to generated files.
    """
    print(f"\n{'='*60}")
    print(f"[pipeline] source: {pdf_path}")
    print(f"{'='*60}\n")

    # ── Resolve output directory ───────────────────────────────────────────────
    work_dir = Path(out_dir) if out_dir else Path(pdf_path).parent / ".scrolly-work"
    work_dir.mkdir(parents=True, exist_ok=True)

    # ── Agent 1: Extract ──────────────────────────────────────────────────────
    print("[pipeline] step 1/6 — extracting PDF...")
    paper_data = agent_extractor.run(pdf_path, str(work_dir))

    # Determine slug from paper title if not given
    if not slug:
        slug = slugify(paper_data.get("title", Path(pdf_path).stem))
    print(f"[pipeline] slug: {slug}")

    (work_dir / "paper_data.json").write_text(json.dumps(paper_data, indent=2))

    # ── Agent 2: Story Planner ────────────────────────────────────────────────
    print("\n[pipeline] step 2/6 — planning narrative beats...")
    beats = agent_story_planner.run(paper_data)
    (work_dir / "beats.json").write_text(json.dumps(beats, indent=2))
    print(f"[pipeline] {len(beats)} beats: {[b.get('beat_id') for b in beats]}")

    # ── Agent 3: Chart Selector ───────────────────────────────────────────────
    print("\n[pipeline] step 3/6 — selecting charts and extracting props...")
    chart_plan = agent_chart_selector.run(beats, paper_data)
    (work_dir / "chart_plan.json").write_text(json.dumps(chart_plan, indent=2))

    # Handle custom viz flags before config writing
    custom_sections = [b for b in chart_plan if b.get("viz_key") == "custom"]
    if custom_sections:
        print(f"\n[pipeline] step 3b — generating {len(custom_sections)} custom viz module(s)...")
        for beat in custom_sections:
            viz_name = f"{slug}-{beat['beat_id']}"
            agent_custom_viz.run(beat, paper_data, viz_name, web_src_dir)
            # Update the chart_plan entry with the generated key
            beat["viz_key"] = re.sub(r"[^a-z0-9]", "_", viz_name.lower())
            beat["mount"] = "svg"

    # ── Agent 4: Config Writer ────────────────────────────────────────────────
    config_ts = ""
    page_mdx  = ""
    validator_result = None

    for attempt in range(1, max_validator_retries + 2):
        print(f"\n[pipeline] step 4/6 — writing config + MDX (attempt {attempt})...")
        config_ts, page_mdx = agent_config_writer.run(chart_plan, paper_data, slug)
        (work_dir / f"config_attempt{attempt}.ts").write_text(config_ts)
        (work_dir / f"page_attempt{attempt}.mdx").write_text(page_mdx)

        # ── Agent 5: Validator ────────────────────────────────────────────────
        print(f"\n[pipeline] step 5/6 — validating (attempt {attempt})...")
        validator_result = agent_validator.run(config_ts, page_mdx, paper_data, chart_plan)
        print(f"[pipeline] {validator_result.summary()}")

        if validator_result.passed:
            break

        if attempt <= max_validator_retries:
            # Feed errors back into config writer
            error_summary = "\n".join(
                f"- [{e.error_type}] {e.location}: {e.message}"
                for e in validator_result.errors
            )
            print(f"[pipeline] retrying config writer with {len(validator_result.errors)} errors...")
            # Patch the chart_plan with corrections before retry
            _apply_schema_corrections(chart_plan, validator_result.errors)
        else:
            print(f"[pipeline] validator still failing after {max_validator_retries} retries — emitting with warnings")

    # ── Agent 7: Final Reviewer ───────────────────────────────────────────────
    print(f"\n[pipeline] step 6/7 — benchmark review (completeness vs gold standard)...")
    config_ts = agent_reviewer.run(config_ts, paper_data, slug)
    (work_dir / "config_reviewed.ts").write_text(config_ts)

    # ── Emit final files ──────────────────────────────────────────────────────
    print(f"\n[pipeline] step 7/7 — writing files to {web_src_dir}...")
    agent_config_writer.write_files(config_ts, page_mdx, slug, web_src_dir)

    # Print warnings
    if validator_result and validator_result.warnings:
        print("\n[pipeline] WARNINGS:")
        for w in validator_result.warnings:
            print(f"  ⚠  {w}")

    result = {
        "slug":       slug,
        "config_ts":  str(Path(web_src_dir) / "scrolly" / "data" / f"{slug}.ts"),
        "page_mdx":   str(Path(web_src_dir) / "pages" / f"{slug}.mdx"),
        "work_dir":   str(work_dir),
        "passed":     validator_result.passed if validator_result else False,
        "errors":     len(validator_result.errors) if validator_result else 0,
    }

    print(f"\n{'='*60}")
    print(f"[pipeline] DONE — page: http://localhost:4321/{slug}/")
    print(f"[pipeline] run `pnpm build` in web/ to compile")
    print(f"{'='*60}\n")

    return result


def _apply_schema_corrections(chart_plan: list[dict], errors: list) -> None:
    """Apply simple auto-corrections based on validator errors before retry."""
    from schemas.viz_schemas import VIZ_SCHEMAS
    for err in errors:
        if err.error_type == "schema" and "mount" in err.message:
            # Fix wrong mount type
            for beat in chart_plan:
                if beat["beat_id"] in err.location:
                    correct_mount = VIZ_SCHEMAS.get(beat["viz_key"], {}).get("mount", "svg")
                    beat["mount"] = correct_mount
                    print(f"[pipeline] auto-fixed mount for {beat['beat_id']} → {correct_mount}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="research-visual-pro pipeline")
    parser.add_argument("pdf",      help="Path to the PDF file")
    parser.add_argument("--slug",   help="URL slug (auto-generated from title if not given)")
    parser.add_argument("--web-src",default=DEFAULT_WEB_SRC, help="Path to web/src/")
    parser.add_argument("--out",    help="Working directory for intermediate files")
    args = parser.parse_args()

    run(
        pdf_path=args.pdf,
        slug=args.slug,
        web_src_dir=args.web_src,
        out_dir=args.out,
    )
