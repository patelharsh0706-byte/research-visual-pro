type UpgradeArgs = { mountEl: HTMLElement; panelEl?: HTMLElement; props?: any };
export default function renderUpgrade({ mountEl, panelEl, props }: UpgradeArgs) {
  const d3 = (globalThis as any).d3;
  if (!d3) return;

  mountEl.replaceChildren();

  const prevTooltip = panelEl?.querySelector(".d3-tooltip") || document.body.querySelector(".d3-tooltip-upgrade");
  if (prevTooltip) prevTooltip.remove();

  const tooltipTarget = panelEl ? d3.select(panelEl) : d3.select("body");
  const tooltip = tooltipTarget.append("div").attr("class", panelEl ? "d3-tooltip" : "d3-tooltip d3-tooltip-upgrade");

  const svg = d3.select(mountEl).append("svg")
    .attr("viewBox", `0 0 600 450`)
    .style("width", "100%")
    .style("height", "100%")
    .style("overflow", "visible");

  const cx = 300;
  const cy = 210;

  // Props with fallback to original Google Trends demo data
  const centerLines: string[] = props?.centerLabel ?? ["Google", "Trends", "2.0"];

  const defaultOuterNodes = [
    { id: "n1", label: "Sentiment Analysis", r: 35, color: "#2980B9", desc: "Understand if the search volume represents positive support or negative curiosity." },
    { id: "n2", label: "User-Level Weight",  r: 35, color: "#2980B9", desc: "Prevent a few highly active 'Power Users' from dominating the region's search volume." },
    { id: "n3", label: "Hybrid Modeling",    r: 35, color: "#2980B9", desc: "Combine real-time search trends with established polling and survey methods." }
  ];
  const outerDefs: Array<{ id: string; label: string; r: number; color: string; desc: string }> =
    props?.nodes ?? defaultOuterNodes;

  // Position outer nodes evenly in a circle starting from top (-90°)
  const orbitRadius = outerDefs.length <= 3 ? 145 : 158;
  const outerNodes = outerDefs.map((def, i) => {
    const angle = (-Math.PI / 2) + (2 * Math.PI * i) / outerDefs.length;
    return { ...def, x: cx + Math.cos(angle) * orbitRadius, y: cy + Math.sin(angle) * orbitRadius };
  });

  // Links from center to each outer node
  outerNodes.forEach((n, i) => {
    svg.append("line")
      .attr("x1", cx).attr("y1", cy)
      .attr("x2", cx).attr("y2", cy)
      .attr("stroke", "var(--ink-muted)")
      .attr("stroke-width", 2)
      .attr("stroke-dasharray", "4 4")
      .attr("opacity", 0)
      .transition().duration(1000).delay(500 + i * 80)
      .attr("x2", n.x).attr("y2", n.y)
      .attr("opacity", 0.6);
  });

  // Center node
  const centerG = svg.append("g").attr("transform", `translate(${cx},${cy})`);

  centerG.append("circle")
    .attr("r", 68).attr("fill", "none")
    .attr("stroke", "var(--ink-muted)").attr("stroke-width", 1)
    .attr("stroke-dasharray", "2 2").attr("opacity", 0.5);

  centerG.append("circle")
    .attr("r", 60).attr("fill", "var(--paper)")
    .attr("stroke", "var(--ink)").attr("stroke-width", 3);

  const lineH = 18;
  const totalH = (centerLines.length - 1) * lineH;
  centerLines.forEach((line, i) => {
    centerG.append("text")
      .attr("text-anchor", "middle")
      .attr("dy", i * lineH - totalH / 2)
      .attr("fill", "var(--ink)")
      .style("font-size", centerLines.length > 3 ? "11px" : "14px")
      .style("font-weight", "700")
      .text(line);
  });

  // Outer nodes
  outerNodes.forEach((n, i) => {
    const g = svg.append("g")
      .attr("transform", `translate(${cx},${cy})`)
      .style("cursor", "pointer");

    g.transition().duration(1000).delay(i * 200)
      .attr("transform", `translate(${n.x},${n.y})`);

    g.append("circle")
      .attr("r", n.r)
      .attr("fill", "var(--paper)")
      .attr("stroke", n.color)
      .attr("stroke-width", 3);

    // Keep original SVG icons for the 3 fallback node IDs; show index number for custom nodes
    if (n.id === "n1") {
      const ic = g.append("g").attr("transform", "translate(-12,-12)")
        .attr("fill", "none").attr("stroke", "var(--ink)").attr("stroke-width", "2")
        .attr("stroke-linecap", "round").attr("stroke-linejoin", "round");
      ic.append("path").attr("d", "M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z");
      ic.append("path").attr("d", "M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z");
      ic.append("path").attr("d", "M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4");
    } else if (n.id === "n2") {
      const ic = g.append("g").attr("transform", "translate(-12,-12)")
        .attr("fill", "none").attr("stroke", "var(--ink)").attr("stroke-width", "2")
        .attr("stroke-linecap", "round").attr("stroke-linejoin", "round");
      ic.append("path").attr("d", "m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z");
      ic.append("path").attr("d", "m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z");
      ic.append("path").attr("d", "M7 21h10");
      ic.append("path").attr("d", "M12 3v18");
    } else if (n.id === "n3") {
      const ic = g.append("g").attr("transform", "translate(-12,-12)")
        .attr("fill", "none").attr("stroke", "var(--ink)").attr("stroke-width", "2")
        .attr("stroke-linecap", "round").attr("stroke-linejoin", "round");
      ic.append("path").attr("d", "M2 15c6.667-6 13.333 0 20-6");
      ic.append("path").attr("d", "m7 18 2.891 2.891");
      ic.append("path").attr("d", "M9 22c1.798-1.998 2.518-3.995 2.807-5.993");
    } else {
      // Custom node: numbered badge
      g.append("text")
        .attr("text-anchor", "middle").attr("dominant-baseline", "middle")
        .attr("fill", n.color)
        .style("font-size", "20px").style("font-weight", "700")
        .text(String(i + 1));
    }

    // Label below the circle (supports \n for line breaks)
    const labelLines = n.label.split("\n");
    labelLines.forEach((line, li) => {
      g.append("text")
        .attr("text-anchor", "middle")
        .attr("dy", n.r + 16 + li * 14)
        .attr("fill", "var(--ink)")
        .style("font-size", "12px").style("font-weight", "600")
        .text(line);
    });

    g.on("mouseover", function(this: SVGGElement, evt: any) {
      d3.select(this).select("circle")
        .attr("stroke-width", 5).attr("r", n.r + 4).attr("fill", "var(--paper-dark)");
      tooltip.classed("visible", true)
        .html(`<strong>${n.label.replace("\n", " ")}</strong><br><span style="font-size:13px">${n.desc}</span>`)
        .style("left", evt.offsetX + 20 + "px")
        .style("top", evt.offsetY - 30 + "px")
        .style("max-width", "250px");
    }).on("mouseout", function(this: SVGGElement) {
      d3.select(this).select("circle")
        .attr("stroke-width", 3).attr("r", n.r).attr("fill", "var(--paper)");
      tooltip.classed("visible", false);
    });
  });
}
