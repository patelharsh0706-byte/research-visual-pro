"""
export_abstract.py
──────────────────
Python wrapper around scripts/export-abstract.js.

Screenshots the graphical-abstract section of a deployed paper page
and saves a print-ready PNG to web/public/abstracts/<slug>.png.

Usage (standalone):
    python3 generator/export_abstract.py <slug> [section_id] [base_url]

Usage (from pipeline):
    from generator.export_abstract import export_abstract
    png_path = export_abstract("drug-repurposing-pushpakom-2019")
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
BASE_URL = "https://research-visual-pro.vercel.app"
DEFAULT_SECTION = "summary"


def export_abstract(
    slug: str,
    section_id: str = DEFAULT_SECTION,
    base_url: str = BASE_URL,
) -> str:
    """
    Run the Puppeteer export script and return the path to the saved PNG.
    Raises RuntimeError if the script fails.
    """
    _ensure_deps()

    url = f"{base_url}/{slug}"
    out_dir = Path(__file__).parent.parent / "web" / "public" / "abstracts"

    print(f"[export_abstract] screenshotting {url}#section-{section_id} …")

    result = subprocess.run(
        ["node", "export-abstract.js", url, section_id, slug, str(out_dir)],
        cwd=str(SCRIPTS_DIR),
        capture_output=False,  # let stdout/stderr stream to terminal
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"[export_abstract] Puppeteer script exited with code {result.returncode}"
        )

    png_path = out_dir / f"{slug}.png"
    if not png_path.exists():
        raise RuntimeError(f"[export_abstract] expected output not found: {png_path}")

    return str(png_path)


def _ensure_deps() -> None:
    """Install node_modules in scripts/ if not already present."""
    nm = SCRIPTS_DIR / "node_modules"
    if not nm.exists():
        print("[export_abstract] installing Puppeteer (first run only) …")
        subprocess.run(
            ["pnpm", "install"],
            cwd=str(SCRIPTS_DIR),
            check=True,
        )


# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 export_abstract.py <slug> [section_id] [base_url]")
        sys.exit(1)

    slug     = sys.argv[1]
    section  = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_SECTION
    base_url = sys.argv[3] if len(sys.argv) > 3 else BASE_URL

    path = export_abstract(slug, section, base_url)
    print(f"\nGraphical abstract saved: {path}")
