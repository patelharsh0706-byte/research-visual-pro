# ingest/

PDF/arXiv extraction. Inputs: a PDF file path or arXiv ID. Outputs: structured dict with:
- `title`, `authors`, `abstract`
- `sections`: list of `{heading, text}`
- `tables`: list of `{caption, rows: [[str]]}` extracted from the PDF
- `figures`: list of `{caption, page}` (we extract captions; image gen is deferred)
- `numbers`: flat list of key numeric findings for the LLM to work with

## Tools

- **PyMuPDF** (`fitz`) — PDF text extraction, bounding-box table heuristics
- **arXiv API** (`arxiv` Python package) — fetch PDF from arXiv ID, get structured metadata
- **GROBID** (optional, Java service) — better structure parsing for multi-column papers; run via REST API

## Entry point (to build)

`extract.py <pdf_path_or_arxiv_id>` → prints JSON to stdout
