# prompts/

The LLM step: paper text + extracted data → scrollytelling config object.

## Files (to build)

- `system.txt` — system prompt establishing the scrollytelling author persona and output contract
- `paper_to_config.txt` — user-turn prompt template. Variables: `{title}`, `{abstract}`, `{sections_json}`, `{tables_json}`, `{viz_registry}` (list of valid viz keys + their props schema)
- `few_shot_example.ts` — the gold config (`samples/gold/google-trends-prediction.ts`) formatted as a few-shot example in the prompt

## Output contract

The LLM must emit a single TypeScript `export const config = { ... }` block matching the schema in `generator/schema/config_schema.json`. The validator (`generator/schema/validate.py`) runs before anything is written to disk.

## Viz key selection logic

Prompt instructs the LLM to:
1. Pick ONE viz key per section from the registry list
2. Fill `props` with REAL numbers from the paper's tables/figures — never invented
3. Use fallback viz keys (`bars`, `timeline`) when uncertain, NOT hallucinated ones
