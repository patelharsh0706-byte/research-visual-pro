type BarsArgs = {
  mountEl: SVGSVGElement;
  props?: any;
};

export default function renderBars({ mountEl, props }: BarsArgs) {
  const d3 = (globalThis as any).d3;
  if (!d3) return;

  mountEl.replaceChildren();

  const rootStyles = getComputedStyle(document.documentElement);
  const inkMuted   = rootStyles.getPropertyValue("--ink-muted").trim()   || "#7E8AB8";
  const accentBlue = rootStyles.getPropertyValue("--accent-blue").trim() || "#4DE1FF";
  const politicalRed = rootStyles.getPropertyValue("--political-red").trim() || "#FF4D9D";

  const W = 600;
  const H = 400;
  const M = { top: 20, right: 30, bottom: 80, left: 60 };
  const iW = W - M.left - M.right;
  const iH = H - M.top - M.bottom;

  // ── Fallback: Indonesia election demo ──────────────────────────────────────
  const fallbackData = [
    { party: "PDIP",    media: 27.1, combined: 83.9 },
    { party: "Gerindra",media: 32.2, combined: 72.2 },
    { party: "PKS",     media: 36.2, combined: 59.9 },
    { party: "Nasdem",  media: 38.2, combined: 50.8 },
    { party: "PKB",     media: 28.3, combined: 72.7 },
    { party: "Demokrat",media: 21.4, combined: 34.7 },
  ];
  const fallbackSeries = [
    { key: "media",    label: "Media Only",      color: accentBlue,   opacity: 0.65 },
    { key: "combined", label: "Combined Model",  color: politicalRed, opacity: 1    },
  ];

  // ── Props API ──────────────────────────────────────────────────────────────
  // props.data:          Array<Record<string,any>>  — rows keyed by xKey + series keys
  // props.xKey:          string                      — x-axis label column (default "party")
  // props.series:        Array<{key,label,color,opacity?}> — bar series definitions
  // props.yDomain:       [number, number]            — y-axis extent (default [0, 100])
  // props.valueSuffix:   string                      — appended to bar value labels (e.g. "%")
  // props.yFormat:       string                      — d3 format for y-axis ticks (default "~s")
  // props.highlight:     {xVal, key}                 — adds a ★ marker on a specific bar
  const data    = (props?.data    || fallbackData)   as Array<Record<string, any>>;
  const series  = (props?.series  || fallbackSeries) as Array<{ key: string; label: string; color: string; opacity?: number }>;
  const xKey    = (props?.xKey    || "party")        as string;
  const yDomain = (props?.yDomain || [0, 100])       as [number, number];
  const valueSuffix = (props?.valueSuffix ?? "")     as string;

  const svg = d3
    .select(mountEl)
    .attr("viewBox", `0 0 ${W} ${H}`)
    .append("g")
    .attr("transform", `translate(${M.left},${M.top})`);

  const x0 = d3.scaleBand()
    .domain(data.map((d: any) => String(d[xKey])))
    .range([0, iW])
    .padding(0.28);

  const x1 = d3.scaleBand()
    .domain(series.map((s) => s.key))
    .range([0, x0.bandwidth()])
    .padding(0.1);

  const y = d3.scaleLinear().domain(yDomain).range([iH, 0]);

  // Grid + axes
  svg.append("g").attr("class", "grid")
    .call(d3.axisLeft(y).ticks(5).tickSize(-iW).tickFormat(""));

  svg.append("g").attr("class", "axis")
    .attr("transform", `translate(0,${iH})`)
    .call(d3.axisBottom(x0));

  svg.append("g").attr("class", "axis")
    .call(d3.axisLeft(y).ticks(5).tickFormat((d: number) => d + valueSuffix));

  // Bars
  data.forEach((d: any, di: number) => {
    series.forEach((s, si) => {
      const value = Number(d[s.key]) || 0;
      const barH  = iH - y(value);

      svg.append("rect")
        .attr("x", x0(String(d[xKey]))! + x1(s.key)!)
        .attr("y", iH)
        .attr("width", x1.bandwidth())
        .attr("height", 0)
        .attr("fill", s.color)
        .attr("rx", 3)
        .attr("opacity", s.opacity ?? 1)
        .transition()
        .delay(di * 100 + si * 50)
        .duration(700)
        .ease(d3.easeCubicOut)
        .attr("y", y(value))
        .attr("height", barH);

      svg.append("text")
        .attr("x", x0(String(d[xKey]))! + x1(s.key)! + x1.bandwidth() / 2)
        .attr("y", y(value) - 4)
        .attr("text-anchor", "middle")
        .style("font-family", "Inter,sans-serif")
        .style("font-size", "9px")
        .style("font-weight", "700")
        .attr("fill", s.color)
        .text(value + valueSuffix)
        .attr("opacity", 0)
        .transition()
        .delay(di * 100 + si * 50 + 600)
        .duration(300)
        .attr("opacity", 1);
    });
  });

  // Optional highlight star
  const highlight = props?.highlight as { xVal: string; key: string } | undefined;
  if (highlight && x0(highlight.xVal) != null && x1(highlight.key) != null) {
    const hRow = data.find((d: any) => String(d[xKey]) === highlight.xVal);
    if (hRow) {
      const hVal = Number(hRow[highlight.key]) || 0;
      const hColor = series.find((s) => s.key === highlight.key)?.color || "#C0392B";
      svg.append("text")
        .attr("x", x0(highlight.xVal)! + x1(highlight.key)! + x1.bandwidth() / 2)
        .attr("y", y(hVal) - 18)
        .attr("text-anchor", "middle")
        .attr("fill", hColor)
        .style("font-family", "Inter,sans-serif")
        .style("font-size", "11px")
        .style("font-weight", "700")
        .text("★")
        .attr("opacity", 0)
        .transition().delay(1000).attr("opacity", 1);
    }
  }

  // Legend
  const legG = svg.append("g").attr("transform", `translate(0,${iH + 50})`);
  series.forEach((s, i) => {
    legG.append("rect")
      .attr("x", i * 220).attr("y", 0)
      .attr("width", 14).attr("height", 10)
      .attr("fill", s.color).attr("opacity", s.opacity ?? 1).attr("rx", 2);
    legG.append("text")
      .attr("x", i * 220 + 20).attr("y", 9)
      .style("font-size", "10px").style("font-family", "Inter,sans-serif")
      .attr("fill", inkMuted)
      .text(s.label);
  });
}
