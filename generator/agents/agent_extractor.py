from __future__ import annotations

"""
Agent 1 — Extractor
====================
Input:  PDF file path
Output: PaperData object (paper_data_schema.py)

Responsibilities:
  - Parse PDF structure (sections, headings, body text)
  - Extract all tables into structured rows
  - Pull numeric statistics from the text (numbers with units and context)
  - Extract figure captions
  - Write output to <slug>/paper_data.json

Does NOT call an LLM — purely rule-based PDF parsing.
"""

import json
import re
import sys
from pathlib import Path

# pip install pymupdf
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None  # type: ignore

# pip install pdfplumber
try:
    import pdfplumber
except ImportError:
    pdfplumber = None  # type: ignore

sys.path.insert(0, str(Path(__file__).parent.parent))
from schemas.paper_data_schema import Figure, NumericStat, PaperData, Section, Table


# ── Number extraction regex ───────────────────────────────────────────────────
# Matches: 2.7-fold, $300M, 95%, 9.4 million, 7,000+, 12-14
_STAT_RE = re.compile(
    r"""
    (?:
        [\$£€]?\s*          # optional currency
        \d[\d,\.]*          # number (with commas/decimals)
        (?:\.\d+)?
        \s*
        (?:                 # optional unit
            billion|million|thousand|M|B|K|
            \%|percent|
            fold|
            years?|months?|days?|
            genes?|compounds?|patients?|diseases?|drugs?|
            [A-Za-z]{1,6}   # other short units
        )?
    )
    """,
    re.VERBOSE | re.IGNORECASE,
)

_SECTION_HEADING_RE = re.compile(
    r"^(?:\d+\.?\s+)?(?:Introduction|Background|Methods?|Results?|Discussion|"
    r"Conclusions?|Abstract|References?|Supplementary|Acknowledgements?|"
    r"[A-Z][A-Za-z ]{3,50})$",
    re.MULTILINE,
)

_FIGURE_RE = re.compile(
    r"(?:Figure|Fig\.?)\s*(\d+[a-z]?)[.:,]?\s+(.+?)(?=\n\n|Figure|Fig\.|Table|\Z)",
    re.DOTALL | re.IGNORECASE,
)

_TABLE_CAPTION_RE = re.compile(
    r"Table\s+(\d+)[.:,]?\s+(.+?)(?=\n\n|Table|\Z)",
    re.DOTALL | re.IGNORECASE,
)


def extract_pdf(pdf_path: str) -> PaperData:
    """Extract structured data from a PDF file."""
    if fitz is None:
        raise ImportError("pymupdf not installed: pip install pymupdf")

    path = Path(pdf_path)
    doc = fitz.open(str(path))

    full_text = ""
    for page in doc:
        full_text += page.get_text("text") + "\n"

    # ── Basic metadata from first page ───────────────────────────────────────
    first_page_text = doc[0].get_text("text") if len(doc) > 0 else ""
    lines = [l.strip() for l in first_page_text.split("\n") if l.strip()]
    journal = ""
    year    = 0
    doi     = ""

    # Find the actual title: skip short header lines (journal vol/issue, ISSN, URLs)
    # Title = first line that is >20 chars, has no bare digits-only tokens, not all-caps journal header
    title = path.stem
    authors = ""
    _header_noise = re.compile(r"^\d+$|ScienceDirect|Elsevier|ISSN|doi:|http|Available|Contents")
    for i, ln in enumerate(lines):
        if len(ln) > 20 and not _header_noise.search(ln) and not re.match(r"^[\d\s./©]+$", ln):
            title = ln
            authors = lines[i + 1] if i + 1 < len(lines) else ""
            break

    # Try to find year and DOI in first 2 pages
    head = "\n".join(doc[i].get_text("text") for i in range(min(2, len(doc))))
    year_match = re.search(r"\b(19|20)\d{2}\b", head)
    if year_match:
        year = int(year_match.group())
    doi_match = re.search(r"10\.\d{4,}/\S+", head)
    if doi_match:
        doi = doi_match.group().rstrip(".")
    journal_match = re.search(r"(?:Nature|Science|Cell|PNAS|NEJM|Lancet|JAMA|BMJ|PLoS)[^\n]{0,80}", head)
    if journal_match:
        journal = journal_match.group().strip()

    # ── Abstract ─────────────────────────────────────────────────────────────
    abstract = ""
    abs_match = re.search(
        r"(?:Abstract|ABSTRACT)\s*\n(.+?)(?=\n(?:Introduction|INTRODUCTION|\d+\.))",
        full_text, re.DOTALL
    )
    if abs_match:
        abstract = abs_match.group(1).strip()[:2000]

    # ── Sections ─────────────────────────────────────────────────────────────
    sections: list[Section] = []
    chunks = re.split(r"\n(?=(?:\d+\.?\s+)?[A-Z][A-Za-z ]{3,60}\n)", full_text)
    for chunk in chunks[:30]:
        head_line = chunk.split("\n")[0].strip()
        body = "\n".join(chunk.split("\n")[1:]).strip()
        if 5 < len(head_line) < 80 and body:
            sections.append(Section(heading=head_line, text=body[:3000], page_start=0))

    # ── Numeric stats ─────────────────────────────────────────────────────────
    stats: list[NumericStat] = []
    sentences = re.split(r"(?<=[.!?])\s+", full_text)
    for sent in sentences:
        for m in _STAT_RE.finditer(sent):
            raw = m.group().strip()
            # Filter noise: must have a digit
            if not re.search(r"\d", raw):
                continue
            # Extract numeric value and unit
            num_match = re.search(r"[\d,\.]+", raw)
            if not num_match:
                continue
            try:
                value = float(num_match.group().replace(",", ""))
            except ValueError:
                continue
            unit = raw[num_match.end():].strip()
            stats.append(NumericStat(
                value=value, unit=unit,
                context=sent.strip()[:200],
                section=_nearest_section(sent, sections)
            ))

    # Deduplicate and limit; filter journal-header noise
    _noise_context = re.compile(r"ISSN|doi:|©|Available online|ScienceDirect|Elsevier|Contents")
    seen: set[str] = set()
    unique_stats: list[NumericStat] = []
    for s in stats:
        if _noise_context.search(s.context):
            continue
        key = f"{s.value}{s.unit}"
        if key not in seen:
            seen.add(key)
            unique_stats.append(s)
    stats = unique_stats[:50]

    # ── Figure captions ────────────────────────────────────────────────────────
    figures: list[Figure] = []
    for m in _FIGURE_RE.finditer(full_text):
        caption = " ".join(m.group(2).split())[:400]
        figures.append(Figure(number=f"Figure {m.group(1)}", caption=caption, section="", page=0))

    # ── Tables (caption-level, structural parsing via pdfplumber) ─────────────
    tables: list[Table] = []
    for m in _TABLE_CAPTION_RE.finditer(full_text):
        caption = " ".join(m.group(2).split())[:300]
        tables.append(Table(
            caption=caption, headers=[], rows=[], section="", page=0
        ))

    if pdfplumber is not None:
        with pdfplumber.open(str(path)) as pdf:
            for page_num, page in enumerate(pdf.pages):
                for tbl in (page.extract_tables() or []):
                    if not tbl or len(tbl) < 2:
                        continue
                    headers = [str(c or "").strip() for c in tbl[0]]
                    rows = [
                        {headers[i]: str(cell or "").strip() for i, cell in enumerate(row)}
                        for row in tbl[1:]
                    ]
                    if len(tables) < len([m for m in _TABLE_CAPTION_RE.finditer(full_text)]):
                        idx = page_num % max(len(tables), 1)
                        if idx < len(tables):
                            tables[idx].headers = headers
                            tables[idx].rows = rows
                            tables[idx].page = page_num + 1

    doc.close()

    return PaperData(
        title=title, authors=authors, journal=journal, year=year, doi=doi,
        abstract=abstract, sections=sections, tables=tables,
        figures=figures, stats=stats, full_text=full_text[:20000]
    )


def _nearest_section(sentence: str, sections: list[Section]) -> str:
    """Return the heading of the first section whose text contains this sentence."""
    for s in sections:
        if sentence[:50] in s.text:
            return s.heading
    return "unknown"


def run(pdf_path: str, out_dir: str | None = None) -> dict:
    """
    Main entry point. Returns paper_data as a dict and optionally writes it to JSON.
    """
    paper = extract_pdf(pdf_path)

    out: dict = {
        "title":    paper.title,
        "authors":  paper.authors,
        "journal":  paper.journal,
        "year":     paper.year,
        "doi":      paper.doi,
        "abstract": paper.abstract,
        "sections": [{"heading": s.heading, "text": s.text[:500]} for s in paper.sections],
        "tables":   [{"caption": t.caption, "headers": t.headers, "rows": t.rows[:10]} for t in paper.tables],
        "figures":  [{"number": f.number, "caption": f.caption} for f in paper.figures],
        "stats":    [{"value": s.value, "unit": s.unit, "context": s.context} for s in paper.stats],
    }

    if out_dir:
        out_path = Path(out_dir) / "paper_data.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(out, indent=2))
        print(f"[extractor] wrote {out_path}")

    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 agent_extractor.py <pdf_path> [out_dir]")
        sys.exit(1)
    result = run(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print(f"[extractor] extracted {len(result['stats'])} stats, "
          f"{len(result['tables'])} tables, {len(result['figures'])} figures")
