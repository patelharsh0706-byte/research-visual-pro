# schema/

Config validator. Runs BEFORE writing any generated file to `web/src/`.

## Why this exists

The generator emits TypeScript as text (Python can't statically type-check TS). The validator is the type-safety layer: it reads the emitted config, parses it as JSON (after stripping the `export const config =` wrapper), and checks:

1. **viz.key is valid** — must be one of the filenames in `web/src/scrolly/viz/` (e.g. `scatter`, `bars`, `timeline`…)
2. **sections[].id uniqueness** — no duplicate IDs
3. **required fields present** — `metadata.title`, `hero.titleHtml`, at least one section
4. **props shape** — basic type check against known prop schemas from the gold sample

## Files (to build)

- `config_schema.json` — JSON Schema for the config object (derived from gold sample shape)
- `validate.py` — reads emitted config text → raises `ValidationError` with a clear message if invalid
- `viz_registry.py` — reads `web/src/scrolly/viz/*.ts` filenames → returns the set of valid keys

## Usage

```python
from generator.schema.validate import validate_config
validate_config(config_text)  # raises if invalid, returns parsed dict if ok
```
