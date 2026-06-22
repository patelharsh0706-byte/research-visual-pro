# samples/papers/

Test PDFs for the generator pipeline.

Place PDF files here. The generator pipeline reads from this directory during development.

## Naming convention

`<slug>.pdf` — same slug as the matching gold config in `../gold/<slug>.ts`

## Current samples

- (empty — add a quantitative arXiv paper here as the first end-to-end test)

## Recommended first paper

Pick a short, quantitative paper with clear tables and numeric results. The Google Trends paper (`google-trends-prediction`) is the reference — its gold config is already written. A good second paper is any arXiv paper with a results table you can hand-map to `bars` or `scatter` viz types.
