"""
paper_data_schema.py — Pydantic models for the structured paper data
that agent_extractor.py produces and all downstream agents consume.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class NumericStat:
    """A single number extracted from the paper text."""
    value: float
    unit: str          # e.g. "M", "%", "years", "genes", ""
    context: str       # sentence it appeared in
    section: str       # which section of the paper


@dataclass
class Table:
    """A parsed table from the paper."""
    caption: str
    headers: list[str]
    rows: list[dict[str, Any]]   # list of {header: value} dicts
    section: str
    page: int


@dataclass
class Figure:
    """A figure caption extracted from the paper."""
    number: str        # e.g. "Figure 1", "Fig. 2a"
    caption: str
    section: str
    page: int


@dataclass
class Section:
    """A section of the paper."""
    heading: str
    text: str          # full section text
    page_start: int


@dataclass
class PaperData:
    """
    Structured output of agent_extractor.py.
    Everything downstream agents need to know about a paper.
    """
    # Bibliographic
    title: str
    authors: str
    journal: str
    year: int
    doi: str

    # Content
    abstract: str
    sections: list[Section] = field(default_factory=list)
    tables: list[Table] = field(default_factory=list)
    figures: list[Figure] = field(default_factory=list)
    stats: list[NumericStat] = field(default_factory=list)

    # Raw full text (fallback for agents that need it)
    full_text: str = ""

    def to_prompt_context(self, max_chars: int = 8000) -> str:
        """
        Return a compact string representation for use in LLM prompts.
        Prioritises abstract, tables, key stats, figure captions.
        """
        parts = [
            f"TITLE: {self.title}",
            f"AUTHORS: {self.authors}",
            f"JOURNAL: {self.journal} ({self.year})",
            f"DOI: {self.doi}",
            "",
            "ABSTRACT:",
            self.abstract,
            "",
        ]

        if self.stats:
            parts.append("KEY STATISTICS:")
            for s in self.stats[:20]:
                parts.append(f'  - {s.value}{s.unit}  [{s.section}]  "{s.context[:120]}"')
            parts.append("")

        if self.tables:
            parts.append("TABLES:")
            for t in self.tables:
                parts.append(f"  [{t.section}] {t.caption}")
                parts.append(f"  Headers: {', '.join(t.headers)}")
                for row in t.rows[:5]:
                    parts.append(f"    {row}")
                parts.append("")

        if self.figures:
            parts.append("FIGURE CAPTIONS:")
            for f in self.figures[:10]:
                parts.append(f"  {f.number}: {f.caption[:200]}")
            parts.append("")

        text = "\n".join(parts)
        if len(text) > max_chars:
            text = text[:max_chars] + "\n[... truncated ...]"
        return text
