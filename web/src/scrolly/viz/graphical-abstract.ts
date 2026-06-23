type GraphicalAbstractArgs = { mountEl: SVGSVGElement | HTMLElement; panelEl?: HTMLElement; props?: any };

export default function renderGraphicalAbstract({ mountEl, props }: GraphicalAbstractArgs) {
  const d3 = (globalThis as any).d3;
  if (!d3) return;

  mountEl.replaceChildren();

  const W = 700, H = 420;
  const svg = d3.select(mountEl).attr("viewBox", `0 0 ${W} ${H}`);

  const p = {
    leftTitle:    props?.leftTitle    ?? "New Drug Development",
    rightTitle:   props?.rightTitle   ?? "Drug Repurposing",
    funnelLabel:  props?.funnelLabel  ?? ["Second Life", "for Drugs"],
    oldCostLabel: props?.oldCostLabel ?? "$2B",
    newCostNum:   props?.newCostNum   ?? 300,
    newCostFrom:  props?.newCostFrom  ?? 2000,
    oldYears:     props?.oldYears     ?? 12,
    newYears:     props?.newYears     ?? 5,
    stat1:        props?.stat1        ?? "7,000+ rare diseases · 95% untreated",
    stat2:        props?.stat2        ?? "12+ approved repurposed drugs to date",
    stat1Tip:     props?.stat1Tip     ?? "95% of 7,000+ rare diseases have no approved treatment",
    stat2Tip:     props?.stat2Tip     ?? "Includes sildenafil, thalidomide derivatives, and aspirin repurposings",
    citation:     props?.citation     ?? "Pushpakom et al. · Nature Reviews Drug Discovery · 2019",
  };

  // ── Defs ──────────────────────────────────────────────────────────────────
  const defs = svg.append("defs");

  defs.append("linearGradient")
    .attr("id", "ga-arrow-grad").attr("x1", "0%").attr("x2", "100%")
    .call((g: any) => {
      g.append("stop").attr("offset", "0%").attr("stop-color", "#1A6B8A");
      g.append("stop").attr("offset", "100%").attr("stop-color", "#E67E22");
    });

  defs.append("marker")
    .attr("id", "ga-arrowhead").attr("markerWidth", 8).attr("markerHeight", 8)
    .attr("refX", 6).attr("refY", 4).attr("orient", "auto")
    .append("path").attr("d", "M0,0 L0,8 L8,4 Z").attr("fill", "#E67E22");

  // ── Backgrounds ───────────────────────────────────────────────────────────
  svg.append("rect").attr("width", 268).attr("height", H).attr("fill", "#EEF2F7");
  svg.append("rect").attr("x", 268).attr("width", W - 268).attr("height", H).attr("fill", "#FAFBFC");
  svg.append("line")
    .attr("x1", 268).attr("y1", 0).attr("x2", 268).attr("y2", H)
    .attr("stroke", "#CBD5E0").attr("stroke-width", 1);

  // ── Panel titles ──────────────────────────────────────────────────────────
  svg.append("text").attr("x", 134).attr("y", 26)
    .attr("text-anchor", "middle").attr("font-family", "Inter, sans-serif")
    .attr("font-size", 12).attr("font-weight", 700).attr("fill", "#1A3A5C")
    .text(p.leftTitle);

  svg.append("text").attr("x", 134).attr("y", 43)
    .attr("text-anchor", "middle").attr("font-family", "Inter, sans-serif")
    .attr("font-size", 9).attr("fill", "#5A7A9A")
    .text(`New Drug: $2B · 12 years`);

  svg.append("text").attr("x", 490).attr("y", 26)
    .attr("text-anchor", "middle").attr("font-family", "Inter, sans-serif")
    .attr("font-size", 12).attr("font-weight", 700).attr("fill", "#1A3A5C")
    .text(p.rightTitle);

  svg.append("text").attr("x", 490).attr("y", 43)
    .attr("text-anchor", "middle").attr("font-family", "Inter, sans-serif")
    .attr("font-size", 9).attr("font-weight", 600).attr("fill", "#E67E22")
    .text("Repurposed Drug: $300M · 5 years");

  // ── Molecule icon (top-left) ──────────────────────────────────────────────
  const molG = svg.append("g").attr("transform", "translate(28, 62)");
  const mnodes: [number, number][] = [[0, 0], [18, 0], [9, 15]];
  mnodes.forEach(([x, y]) =>
    molG.append("circle").attr("cx", x).attr("cy", y).attr("r", 5.5)
      .attr("fill", "none").attr("stroke", "#5A7A9A").attr("stroke-width", 1.5)
  );
  [[0, 1], [0, 2], [1, 2]].forEach(([a, b]) =>
    molG.append("line")
      .attr("x1", mnodes[a][0]).attr("y1", mnodes[a][1])
      .attr("x2", mnodes[b][0]).attr("y2", mnodes[b][1])
      .attr("stroke", "#5A7A9A").attr("stroke-width", 1.5)
  );

  // ── Winding road ──────────────────────────────────────────────────────────
  const roadD = [
    "M 48,70",
    "L 208,70",
    "Q 236,70 236,98",
    "L 236,128",
    "Q 236,156 208,156",
    "L 48,156",
    "Q 20,156 20,184",
    "L 20,214",
    "Q 20,242 48,242",
    "L 208,242",
    "Q 236,242 236,270",
    "L 236,300",
    "Q 236,324 212,330",
    "L 158,336",
  ].join(" ");

  // Road body
  const roadBg = svg.append("path")
    .attr("d", roadD).attr("fill", "none")
    .attr("stroke", "#1A3A5C").attr("stroke-width", 20)
    .attr("stroke-linecap", "round").attr("stroke-linejoin", "round");

  // Road center dashes
  const roadDash = svg.append("path")
    .attr("d", roadD).attr("fill", "none")
    .attr("stroke", "white").attr("stroke-width", 1.5)
    .attr("stroke-dasharray", "9 7").attr("opacity", 0);

  // Animate road drawing via stroke-dashoffset
  const pathNode = roadBg.node() as SVGPathElement | null;
  const pathLen = pathNode?.getTotalLength?.() ?? 950;

  roadBg
    .attr("stroke-dasharray", pathLen)
    .attr("stroke-dashoffset", pathLen)
    .transition().duration(1400).ease(d3.easeLinear)
    .attr("stroke-dashoffset", 0);

  roadDash.transition().delay(1400).duration(0).attr("opacity", 1);

  // ── Left patient icon ─────────────────────────────────────────────────────
  const lp = svg.append("g").attr("transform", "translate(148, 348)").attr("opacity", 0);
  drawPerson(lp, "#4A6080", 8);
  lp.transition().delay(1400).duration(400).attr("opacity", 1);

  // ── Funnel ────────────────────────────────────────────────────────────────
  const fG = svg.append("g").attr("opacity", 0);

  fG.append("path")
    .attr("d", "M 246,150 L 334,150 L 310,278 L 270,278 Z")
    .attr("fill", "#1A5276");
  // highlight stripe
  fG.append("path")
    .attr("d", "M 246,150 L 268,150 L 280,278 L 270,278 Z")
    .attr("fill", "#2E86C1").attr("opacity", 0.38);
  // tube
  fG.append("path")
    .attr("d", "M 270,278 L 310,278 L 305,316 L 275,316 Z")
    .attr("fill", "#154360");

  const fLabels = Array.isArray(p.funnelLabel) ? p.funnelLabel : [p.funnelLabel];
  fLabels.forEach((line: string, i: number) =>
    fG.append("text")
      .attr("x", 290).attr("y", 205 + i * 16)
      .attr("text-anchor", "middle").attr("font-family", "Inter, sans-serif")
      .attr("font-size", 10.5).attr("font-weight", 700).attr("fill", "white")
      .text(line)
  );

  fG.transition().delay(1000).duration(500).attr("opacity", 1);

  // ── Right side: pill → arrow → patient ───────────────────────────────────
  const pX = 358, aY = 124, arrowEnd = 586;

  // Pill bottle
  const pillG = svg.append("g")
    .attr("transform", `translate(${pX}, ${aY - 22})`).attr("opacity", 0);
  pillG.append("rect").attr("x", -8).attr("y", -7).attr("width", 11).attr("height", 9).attr("rx", 2).attr("fill", "#154360");
  pillG.append("rect").attr("x", -11).attr("y", 2).attr("width", 22).attr("height", 28).attr("rx", 4).attr("fill", "#1A5276");
  pillG.append("text").attr("x", 0).attr("y", 20).attr("text-anchor", "middle")
    .attr("font-family", "Inter, sans-serif").attr("font-size", 9)
    .attr("fill", "white").attr("font-weight", 700).text("Rx");
  pillG.transition().delay(1500).duration(400).attr("opacity", 1);

  // Arrow — grows via width animation on a rect with gradient fill
  const arrowX1 = pX + 14;
  svg.append("rect")
    .attr("x", arrowX1).attr("y", aY - 5)
    .attr("width", 0).attr("height", 10).attr("rx", 5)
    .attr("fill", "url(#ga-arrow-grad)")
    .transition().delay(1800).duration(700).ease(d3.easeLinear)
    .attr("width", arrowEnd - arrowX1);

  // Arrowhead triangle
  svg.append("polygon")
    .attr("points", `${arrowEnd},${aY - 11} ${arrowEnd + 17},${aY} ${arrowEnd},${aY + 11}`)
    .attr("fill", "#E67E22").attr("opacity", 0)
    .transition().delay(2500).duration(300).attr("opacity", 1);

  // Right patient
  const rp = svg.append("g")
    .attr("transform", `translate(${arrowEnd + 28}, ${aY - 18})`).attr("opacity", 0);
  drawPerson(rp, "#E67E22", 10);
  rp.transition().delay(2500).duration(400).attr("opacity", 1);

  // "Cost reduction" label
  svg.append("text").attr("x", 490).attr("y", 164)
    .attr("text-anchor", "middle").attr("font-family", "Inter, sans-serif")
    .attr("font-size", 10.5).attr("font-weight", 600).attr("fill", "#4A6080")
    .attr("opacity", 0).text("Cost reduction")
    .transition().delay(2600).duration(400).attr("opacity", 1);

  // ── Tooltip ───────────────────────────────────────────────────────────────
  const tip = d3.select(document.body)
    .append("div").attr("class", "d3-tooltip")
    .style("position", "absolute").style("opacity", 0)
    .style("pointer-events", "none");

  function withTip(sel: any, html: string) {
    return sel
      .on("mouseover", (ev: MouseEvent) =>
        tip.style("opacity", 1).html(html)
          .style("left", (ev.pageX + 12) + "px")
          .style("top", (ev.pageY - 28) + "px"))
      .on("mouseleave", () => tip.style("opacity", 0));
  }

  // ── Animated stats ────────────────────────────────────────────────────────
  // $2B → $300M
  svg.append("text").attr("x", 408).attr("y", 205)
    .attr("font-family", "Inter, sans-serif").attr("font-size", 24)
    .attr("font-weight", 800).attr("fill", "#1A3A5C")
    .text(p.oldCostLabel);

  svg.append("text").attr("x", 452).attr("y", 205)
    .attr("font-family", "Inter, sans-serif").attr("font-size", 24)
    .attr("font-weight", 800).attr("fill", "#E67E22").text("→");

  const costTgt = svg.append("text").attr("x", 474).attr("y", 205)
    .attr("font-family", "Inter, sans-serif").attr("font-size", 24)
    .attr("font-weight", 800).attr("fill", "#E67E22").attr("opacity", 0)
    .style("cursor", "default");

  withTip(costTgt, "~10% of the $2–3B cost of developing a new chemical entity");
  countUp(costTgt.node(), p.newCostFrom, p.newCostNum,
    (n: number) => `$${Math.round(n)}M`, 2700, d3);

  // 12 → 5 years
  svg.append("text").attr("x", 408).attr("y", 242)
    .attr("font-family", "Inter, sans-serif").attr("font-size", 19)
    .attr("font-weight", 700).attr("fill", "#1A3A5C")
    .text(`${p.oldYears} years`);

  svg.append("text").attr("x", 494).attr("y", 242)
    .attr("font-family", "Inter, sans-serif").attr("font-size", 19)
    .attr("font-weight", 700).attr("fill", "#E67E22").text("→");

  const timeTgt = svg.append("text").attr("x", 514).attr("y", 242)
    .attr("font-family", "Inter, sans-serif").attr("font-size", 19)
    .attr("font-weight", 700).attr("fill", "#E67E22").attr("opacity", 0)
    .style("cursor", "default");

  withTip(timeTgt, "~60% faster than the 12–15 year path for a new drug");
  countUp(timeTgt.node(), p.oldYears, p.newYears,
    (n: number) => `${Math.round(n)} yrs`, 3200, d3);

  // Supporting stats
  [
    { text: p.stat1, tipText: p.stat1Tip, y: 278 },
    { text: p.stat2, tipText: p.stat2Tip, y: 300 },
  ].forEach(({ text, tipText, y }, i) => {
    const el = svg.append("text").attr("x", 490).attr("y", y)
      .attr("text-anchor", "middle").attr("font-family", "Inter, sans-serif")
      .attr("font-size", 10).attr("fill", "#4A6080").attr("opacity", 0)
      .style("cursor", "default").text(text);
    withTip(el, tipText);
    el.transition().delay(3500 + i * 250).duration(400).attr("opacity", 1);
  });

  // ── Citation strip ────────────────────────────────────────────────────────
  svg.append("line")
    .attr("x1", 275).attr("y1", 403).attr("x2", 694).attr("y2", 403)
    .attr("stroke", "#CBD5E0").attr("stroke-width", 0.5);
  svg.append("text").attr("x", 490).attr("y", 416)
    .attr("text-anchor", "middle").attr("font-family", "Inter, sans-serif")
    .attr("font-size", 8.5).attr("fill", "#9BA8B5").text(p.citation);

  // ── Helper: stick-figure person ───────────────────────────────────────────
  function drawPerson(g: any, color: string, r: number) {
    const sw = r * 0.28;
    g.append("circle").attr("r", r).attr("fill", color);
    g.append("line").attr("y1", r).attr("y2", r + r * 2.2)
      .attr("stroke", color).attr("stroke-width", sw);
    g.append("line").attr("x1", -r * 1.1).attr("y1", r + r * 1.1)
      .attr("x2", r * 1.1).attr("y2", r + r * 1.1)
      .attr("stroke", color).attr("stroke-width", sw);
    g.append("line").attr("y1", r + r * 2.2).attr("x2", -r * 0.7).attr("y2", r + r * 3.8)
      .attr("stroke", color).attr("stroke-width", sw);
    g.append("line").attr("y1", r + r * 2.2).attr("x2", r * 0.7).attr("y2", r + r * 3.8)
      .attr("stroke", color).attr("stroke-width", sw);
  }

  // ── Helper: count-up tween ────────────────────────────────────────────────
  function countUp(
    node: SVGTextElement | null,
    from: number,
    to: number,
    fmt: (n: number) => string,
    delay: number,
    _d3: any
  ) {
    if (!node) return;
    _d3.select(node)
      .transition().delay(delay).duration(300).attr("opacity", 1)
      .transition().duration(950).ease(_d3.easeQuadOut)
      .tween("text", () => {
        const interp = _d3.interpolateNumber(from, to);
        return (t: number) => { node.textContent = fmt(interp(t)); };
      });
  }
}
