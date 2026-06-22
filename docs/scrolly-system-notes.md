# Scrolly System Notes

Reference for how the 4-layer scrollytelling engine works. Source: alharkan7/alharkan7.github.io.

## The 4 Layers

```
Layer 1: Narrative MDX          web/src/pages/<slug>.mdx
Layer 2: Data/config TS         web/src/scrolly/data/<slug>.ts
Layer 3: ScrollyLayout.astro    web/src/layouts/ScrollyLayout.astro  ← glue
Layer 4: scrolly-runtime.ts     web/src/scrolly/scrolly-runtime.ts   ← engine
```

We generate layers 1 and 2. Layers 3 and 4 are reused unchanged.

## How a page renders

1. `ScrollyLayout.astro` runs at build time. It reads `configId` from MDX frontmatter, globs `../scrolly/data/*.ts`, loads the matching config, and merges it with any frontmatter overrides (frontmatter wins).
2. The layout renders the full HTML: 2-column sticky layout (left = `.scroll-col` text, right = `.viz-col` panel stack).
3. For each `sections[]` entry, the layout writes a `.viz-panel` div (hidden) with the viz key and props serialized as `data-props` JSON.
4. `scrolly-entry.ts` runs on load → calls `scrolly-runtime.ts::initScrolly()`.
5. The runtime attaches an IntersectionObserver to every `.scroll-section` element. When a section enters the viewport (≥40% visible), it fires `switchViz(section.dataset.vizId)`.
6. `switchViz` fades out the current panel, fades in the target panel, and lazily initializes the D3 module if it hasn't been initialized yet (dynamic `import()` of `viz/<key>.ts`).

## The section ↔ config pairing

**CRITICAL:** every `<ScrollySection id="X">` in the MDX must match a `sections[].id === "X"` in the config. Mismatch = the section scrolls past with no chart. The generator must keep these in sync.

```
MDX:                               Config:
<ScrollySection id="accuracy">     { id: "accuracy", viz: { key: "accuracy", ... } }
```

## Viz module signature

```typescript
export default function renderX({
  mountEl: SVGSVGElement | HTMLElement,  // the chart SVG or div
  panelEl: HTMLElement,                  // the containing panel (for tooltip div)
  props?: any                            // from config sections[].viz.props
}): void
```

- `mount: "svg"` → `mountEl` is an `<svg>` element; use `d3.select(mountEl)` directly
- `mount: "div"` → `mountEl` is a `<div>`; build DOM inside it
- Always read `const d3 = (globalThis as any).d3;` — do NOT import D3
- Colors: always use CSS vars (`var(--ink-muted)`, `var(--paper)`) — never hardcode
- ViewBox: `"0 0 600 400"` is standard; use it so charts are responsive

## Theming

Per-paper theme via frontmatter:

```yaml
theme:
  accent: "#E67E22"
  secondary: "#2980B9"
```

`ScrollyLayout` maps these to CSS vars:
- `accent` → `--accent-blue`
- `secondary` → `--political-red`
- `paper` → `--paper`
- `paperDark` → `--paper-dark`
- `ink` → `--ink`

Light/dark: `body.light-theme` class toggled via nav button; persisted to `localStorage["scrolly-theme"]`.

## Common pitfalls

1. **MDX id ≠ config id** — silent missing chart
2. **Hallucinated viz key** — runtime does `import(./viz/${key}.ts)` — 404 if key doesn't exist. Schema validator catches this.
3. **D3 not available** — `globalThis.d3` is null if the CDN script hasn't loaded yet. All viz modules guard with `if (!d3) return;`. The CDN script is loaded synchronously in `<head>` so this should never happen in practice.
4. **props shape mismatch** — D3 module reads `props.someKey || fallbackValue`, so wrong props silently fall back to demo data. The validator checks critical prop shapes.
5. **`mount` type wrong** — `map` key needs `mount: "div"` (it builds `<canvas>` inside), not `svg`. Check the viz module source if unsure.

## Adding a new viz type

1. Write `web/src/scrolly/viz/<newkey>.ts` following the render signature above
2. Add `<newkey>` to the viz registry list in `generator/schema/viz_registry.py`
3. Use it in a config with `viz: { key: "<newkey>", mount: "svg"|"div", props: {...} }`
