from __future__ import annotations

"""
viz_schemas.py — single source of truth for every viz module's props contract.

Used by:
  - agent_chart_selector.py  (knows which viz fits which data type)
  - agent_config_writer.py   (knows what props to generate)
  - agent_validator.py       (checks generated props against schema)

Adding a new viz module? Add its entry here first, then write the .ts file.
"""

from typing import Any

# ── Data type taxonomy ────────────────────────────────────────────────────────
# Each viz is tagged with the data types it handles well.
# agent_chart_selector uses these tags to route from extracted data → viz key.

DATA_TYPES = {
    "comparison":    "A vs B (same metric, different groups)",
    "time_series":   "Values over time (year, month, etc.)",
    "distribution":  "Many values of a single variable",
    "network":       "Nodes and directed edges / causal paths",
    "spatial":       "Geographic / map data",
    "table":         "Multi-row, multi-column categorical table",
    "gauge":         "Single ratio or pass/fail count",
    "hierarchy":     "Hub-and-spoke or tree structure",
    "scatter":       "Two continuous variables (XY plot)",
    "sentiment":     "Qualitative sentiment or tone distribution",
}

# ── Viz registry ─────────────────────────────────────────────────────────────

VIZ_SCHEMAS: dict[str, dict[str, Any]] = {

    "bars": {
        "description": "Grouped bar chart. Best for comparing 1-2 numeric series across categories.",
        "mount": "svg",
        "data_types": ["comparison"],
        "required_props": {
            "data": "list[dict] — rows; each row has xKey column + one column per series key",
        },
        "optional_props": {
            "xKey":        "str — column name for x-axis labels (default: 'party')",
            "series":      "list[{key, label, color, opacity?}] — bar series definitions",
            "yDomain":     "[number, number] — y-axis [min, max] (default: [0, 100])",
            "valueSuffix": "str — appended to bar value labels, e.g. '%' or 'M' (default: '')",
            "highlight":   "{xVal: str, key: str} — adds a ★ marker on a specific bar",
        },
        "example_props": {
            "xKey": "drug_type",
            "series": [
                {"key": "cost_usd_m", "label": "Cost (USD M)", "color": "#1A6B8A", "opacity": 1},
                {"key": "years",      "label": "Years to approval", "color": "#E67E22", "opacity": 0.8},
            ],
            "yDomain": [0, 3000],
            "data": [
                {"drug_type": "Repurposed",    "cost_usd_m": 300, "years": 6},
                {"drug_type": "New Drug (NCE)", "cost_usd_m": 2500, "years": 12},
            ],
        },
        "pitfalls": [
            "yDomain must cover all values in data or bars will be clipped",
            "series[].key must match column names in data rows exactly",
            "Max ~8 groups or x-axis labels overlap — consider horizontal bars instead",
        ],
    },

    "timeline": {
        "description": "Multi-line time series chart. Best for showing how N metrics change over years.",
        "mount": "svg",
        "data_types": ["time_series"],
        "required_props": {
            "data":   "list[dict] — rows with 'year' (number) + one column per series key",
            "series": "list[str] — column names to plot as lines",
        },
        "optional_props": {
            "colors":       "Record<str, str> — line color per series key",
            "seriesLabels": "Record<str, str> — display label per series key (default: capitalised key)",
            "yDomain":      "[number, number] — y-axis [min, max] (default: auto from data)",
            "annotation":   "{year: number, label: str} — vertical dashed marker line",
        },
        "example_props": {
            "series": ["repurposed", "new_drug"],
            "colors": {"repurposed": "#27AE60", "new_drug": "#C0392B"},
            "seriesLabels": {"repurposed": "Repurposed Drugs", "new_drug": "New Chemical Entities"},
            "data": [
                {"year": 1987, "repurposed": 1, "new_drug": 8},
                {"year": 1995, "repurposed": 4, "new_drug": 12},
            ],
            "annotation": {"year": 2003, "label": "Orphan Drug Act era"},
        },
        "pitfalls": [
            "'year' column must be a number, not a string",
            "All series keys must exist in every data row (missing → NaN → line breaks)",
        ],
    },

    "precision": {
        "description": "Deviation dot plot. Best for showing how items deviate from a central baseline.",
        "mount": "svg",
        "data_types": ["distribution"],
        "required_props": {
            "data": "list[{p: str, v: number}] — p = label, v = deviation in range [-1, 1]",
        },
        "optional_props": {},
        "example_props": {
            "data": [
                {"p": "Lenalidomide", "v":  1.00},
                {"p": "Rituximab",    "v":  0.76},
                {"p": "Fingolimod",   "v":  0.00},
                {"p": "Raloxifene",   "v": -0.57},
            ]
        },
        "pitfalls": [
            "v must be in [-1, 1] — normalise your raw values before passing",
            "Dots overlap when many items cluster near 0 — consider spreading to avoid occlusion",
        ],
    },

    "matrix": {
        "description": "Heatmap / grid. Best for showing which cells in a categorical table are active.",
        "mount": "svg",
        "data_types": ["table"],
        "required_props": {
            "parties": "list[str] — row labels",
            "media":   "list[str] — column labels",
            "sigData": "Record<row, Record<col, str|null>> — null = empty cell, str = highlighted cell value",
        },
        "optional_props": {},
        "example_props": {
            "parties": ["United States", "European Union"],
            "media":   ["Exclusivity", "Tax Credit", "Fee Waiver"],
            "sigData": {
                "United States":  {"Exclusivity": "7 yrs", "Tax Credit": "50%", "Fee Waiver": "Yes"},
                "European Union": {"Exclusivity": "10 yrs","Tax Credit": None, "Fee Waiver": "Yes"},
            },
        },
        "pitfalls": [
            "Every key in parties must exist as a key in sigData",
            "Every string in media must exist as a nested key inside each sigData[party]",
        ],
    },

    "sem": {
        "description": "Box-and-arrow structural diagram. Best for showing causal / pathway relationships.",
        "mount": "svg",
        "data_types": ["network"],
        "required_props": {
            "nodes": "list[{id,label,x,y,w,h,color}] — rectangular boxes with absolute SVG coords (viewBox 0 0 600 400)",
            "paths": "list[{from,to,sig,coef}] — arrows; from/to are node ids; sig=true → accent-colored arrow",
        },
        "optional_props": {
            "legend": "{sigLabel: str, insigLabel: str}",
        },
        "layout_rules": [
            "Arrows draw from RIGHT EDGE of 'from' node to LEFT EDGE of 'to' node",
            "Only left-to-right arrows look correct (from.x < to.x)",
            "Use 2-3 columns: inputs (x≈30), optional middle (x≈220), outputs (x≈450)",
            "Nodes at x=30 with w=120: right edge at x=150. Nodes at x=450: left edge at x=450",
            "Standard separation: 600 wide viewBox → left column max x+w = 200, right column x ≥ 400",
        ],
        "example_props": {
            "nodes": [
                {"id": "input_a", "label": "Input A", "x": 30,  "y": 80,  "w": 110, "h": 46, "color": "#1A5276"},
                {"id": "output",  "label": "Output",  "x": 450, "y": 170, "w": 110, "h": 46, "color": "#1A6B8A"},
            ],
            "paths": [
                {"from": "input_a", "to": "output", "sig": True, "coef": "β=0.61*"},
            ],
            "legend": {"sigLabel": "Significant (p<0.05)", "insigLabel": "Not significant"},
        },
        "pitfalls": [
            "from/to ids must match node ids exactly",
            "Right-to-left arrows (from.x > to.x) render backwards",
        ],
    },

    "bubbles": {
        "description": "Orbital network. Best for showing variables clustering around two central concepts.",
        "mount": "svg",
        "data_types": ["network"],
        "required_props": {
            "centers": "list[{id,label,dx,dy,r,color}] — central nodes; dx/dy are offsets from SVG center (300,225)",
            "vars":    "list[{label,cat,angle,dist,r,color}] — satellite nodes; angle in degrees from center, dist in px",
        },
        "optional_props": {
            "cornerLabels": "{media: str, socioEcon: str} — corner annotations",
        },
        "layout_rules": [
            "All vars connect to ALL centers — don't use vars to show relationships between centers",
            "angle -180 to -1 = left half; 0 to 180 = right half",
            "Keep dist 160–210 so satellites stay within the 600x450 viewBox",
            "r 20–35 for satellites; r 40–55 for centers",
        ],
        "pitfalls": [
            "vars connect to every center, not just their cat — cat is just a color grouping label",
        ],
    },

    "accuracy": {
        "description": "Animated arc gauge showing a correct/total ratio.",
        "mount": "svg",
        "data_types": ["gauge"],
        "required_props": {
            "total":   "number — total count (denominator)",
            "correct": "number — successful count (numerator)",
        },
        "optional_props": {
            "sublabel":      "str — text below the large number (default: 'out of N provinces correctly predicted')",
            "correctLabel":  "str — label for the correct segment (default: 'N Correct')",
            "incorrectLabel":"str — label for the incorrect segment (default: 'N Incorrect')",
        },
        "pitfalls": [
            "correct must be ≤ total or arc overflows",
        ],
    },

    "upgrade": {
        "description": "Hub-and-spoke diagram. Best for showing N recommendations or components around a central theme.",
        "mount": "div",
        "data_types": ["hierarchy"],
        "required_props": {},
        "optional_props": {
            "centerLabel": "list[str] — lines of text for the center node (default: ['Google','Trends','2.0'])",
            "nodes":       "list[{id,label,r,color,desc}] — outer nodes; label supports '\\n' for line breaks; desc shown on hover",
        },
        "layout_rules": [
            "Nodes are auto-positioned evenly in a circle; no manual x/y needed",
            "3 nodes → orbit radius 145px; 4–8 nodes → orbit radius 158px",
            "label '\\n' creates line breaks below the circle",
        ],
        "pitfalls": [
            "More than 8 nodes will overlap — prefer 4–6 for readability",
        ],
    },

    "scatter": {
        "description": "XY scatter plot with optional trend line.",
        "mount": "svg",
        "data_types": ["scatter"],
        "required_props": {
            "data": "list[{x: number, y: number, label?: str}]",
        },
        "optional_props": {
            "xLabel": "str — x-axis title",
            "yLabel": "str — y-axis title",
            "showTrendline": "bool (default true)",
        },
        "pitfalls": [],
    },

    "sentiment": {
        "description": "Sentiment score distribution chart.",
        "mount": "svg",
        "data_types": ["sentiment"],
        "required_props": {},
        "optional_props": {},
        "pitfalls": ["Largely fallback-driven; props support limited in current version"],
    },

    "equation": {
        "description": "Rendered mathematical formula or equation display.",
        "mount": "svg",
        "data_types": [],
        "required_props": {},
        "optional_props": {},
        "pitfalls": ["Renders a fixed formula; not data-driven"],
    },

    "market": {
        "description": "Animated concentric circles showing audience/market size.",
        "mount": "svg",
        "data_types": [],
        "required_props": {},
        "optional_props": {},
        "pitfalls": [
            "FULLY HARDCODED — shows Indonesia internet user data regardless of props",
            "Do not use for paper-specific data; use bubbles or bars instead",
        ],
    },

    "map": {
        "description": "Single choropleth map (Indonesia province level).",
        "mount": "svg",
        "data_types": ["spatial"],
        "required_props": {},
        "optional_props": {},
        "pitfalls": ["Indonesia-specific geography; not usable for other regions"],
    },

    "dualmap": {
        "description": "Side-by-side choropleth maps for comparing two spatial datasets.",
        "mount": "div",
        "data_types": ["spatial"],
        "required_props": {
            "provinces":   "list[str] — 34 Indonesian province names in order",
            "searchValues":"list[number] — 0/0.5/1 per province for left map",
            "realValues":  "list[number] — 0/0.5/1 per province for right map",
        },
        "pitfalls": ["Indonesia-specific; not generalisable to other geographies"],
    },
}


def get_schema(viz_key: str) -> dict[str, Any] | None:
    return VIZ_SCHEMAS.get(viz_key)


def get_viz_keys_for_data_type(data_type: str) -> list[str]:
    """Return all viz keys that handle a given data type."""
    return [k for k, v in VIZ_SCHEMAS.items() if data_type in v.get("data_types", [])]


def format_schema_for_prompt(viz_key: str) -> str:
    """Return a compact schema description for inclusion in LLM prompts."""
    schema = VIZ_SCHEMAS.get(viz_key)
    if not schema:
        return f"Unknown viz key: {viz_key}"
    lines = [
        f"## viz key: `{viz_key}`",
        f"**Description:** {schema['description']}",
        f"**mount:** \"{schema['mount']}\"",
        f"**Data types:** {', '.join(schema.get('data_types', ['none']))}",
    ]
    if schema.get("required_props"):
        lines.append("**Required props:**")
        for k, v in schema["required_props"].items():
            lines.append(f"  - `{k}`: {v}")
    if schema.get("optional_props"):
        lines.append("**Optional props:**")
        for k, v in schema["optional_props"].items():
            lines.append(f"  - `{k}`: {v}")
    if schema.get("pitfalls"):
        lines.append("**Pitfalls:**")
        for p in schema["pitfalls"]:
            lines.append(f"  - {p}")
    return "\n".join(lines)
