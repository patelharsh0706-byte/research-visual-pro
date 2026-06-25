export const config = {
  slug: "guennif-2022-remdesivir-capture",
  metadata: {
    brand: "Orphan Drug Capture",
    title: "Capture Along the Regulatory Process: The Remdesivir Episode",
    description: "A public-choice analysis of how Gilead secured orphan drug designation for remdesivir during COVID-19, unlocking monopoly pricing through systemic regulatory capture.",
    homeNavUrl: "/",
  },
  hero: {
    titleHtml: `How a pandemic drug <span class="hero-accent">captured</span> the orphan system`,
    subtitle: "Remdesivir's journey from Ebola to COVID-19 exposed a quiet chain of regulatory capture — and left governments paying monopoly prices during a global emergency.",
    subtitleHtml: "One drug. One loophole. A pandemic's worth of monopoly rent.",
    authorsHtml: "Guennif et al. · Springer Nature / Science+Business Media",
    teaserHtml: "When COVID-19 infected hundreds of millions, Gilead obtained orphan drug status for remdesivir — a designation legally reserved for diseases affecting <strong>fewer than 200,000 Americans</strong> — triggering tax credits, expedited review, and seven years of market exclusivity at public expense.",
    ctaHref: "#section-intro",
    stats: [
      { target: 2022, unit: "", label: "Year published" },
      { target: 2000, unit: "s", label: "Stylized facts drawn from data" },
      { target: 1981, unit: "", label: "Orphan Drug Act enacted" },
      { target: 186, unit: "", label: "Pages in journal volume" },
    ],
  },
  theme: {
    accent: "#c0392b",
    secondary: "#1a5276",
    background: "#0d1b2a",
    surface: "#132338",
    text: "#e8edf2",
    textMuted: "#8fa3b8",
  },
  sections: [
    {
      id: "intro",
      navLabel: "Orphan Claim",
      mobileLabel: "Orphan",
      layout: "sidecar",
      themeShift: false,
      headline: "A drug for a pandemic claimed orphan status",
      teaserHtml: "<p>Remdesivir was developed to fight Ebola. When COVID-19 struck hundreds of millions, Gilead secured an orphan drug designation — a status legally reserved for diseases affecting fewer than 200,000 Americans. The contradiction was stark, and it came with a price tag.</p>",
      viz: {
        key: "accuracy",
        mount: "svg",
        animationStyle: "fade",
        title: "COVID Scale vs. Orphan Threshold",
        captionHtml: "<p>This chart contrasts the scale of COVID-19's U.S. patient population against the 200,000-person legal ceiling that defines an orphan disease. The gap is not a rounding error — it spans tens of millions of patients. Look for just how far remdesivir's real market exceeded the designation's statutory limit at the moment the FDA approved it.</p>",
        props: {
          total: 20000000,
          correct: 200000,
          label: "ODA threshold (200k) vs U.S. COVID cases at FDA approval (Oct 2020 ~20M)",
        },
      },
    },
    {
      id: "problem",
      navLabel: "Bent Law",
      mobileLabel: "Bent Law",
      layout: "sidecar",
      themeShift: false,
      headline: "A rare-disease law was bent toward a global epidemic",
      teaserHtml: "<p>The Orphan Drug Act of 1983 was designed to incentivize treatments for conditions too rare to attract commercial investment. Remdesivir's orphan designation — granted in March 2020 as COVID-19 was declared a pandemic — stretched that intent beyond recognition, unlocking tax credits, expedited review, and seven years of market exclusivity.</p>",
      viz: {
        key: "bars",
        mount: "svg",
        animationStyle: "fade",
        title: "ODA Benefits Gilead Unlocked",
        captionHtml: "<p>Each bar represents a distinct market incentive triggered by orphan designation: 50% R&D tax credits, priority FDA review, and seven years of exclusive market rights. These benefits compound — notice how the combined effect creates a structural moat that competitors cannot overcome even when a public health emergency expands the market to pandemic scale.</p>",
        props: {
          xKey: "benefit",
          series: [
            { key: "value_m", label: "Estimated value (USD M)", color: "#c0392b", opacity: 1 },
          ],
          yDomain: [0, 2200],
          data: [
            { benefit: "Expected global revenue (2020)", value_m: 2000 },
            { benefit: "NIH public funding (2014–19)", value_m: 76 },
            { benefit: "Gilead R&D spend (clinical trials)", value_m: 1000 },
            { benefit: "Production cost per course", value_m: 0.001 },
          ],
        },
      },
    },
    {
      id: "method",
      navLabel: "Framework",
      mobileLabel: "Framework",
      layout: "sidecar",
      themeShift: false,
      headline: "Researchers built a framework to detect capture",
      teaserHtml: "<p>Guennif and colleagues drew on public choice theory to construct a structural model of regulatory capture — mapping how industry influence flows through regulatory processes to generate orphan designations, and ultimately, predatory pricing power during public health crises.</p>",
      viz: {
        key: "sem",
        mount: "svg",
        animationStyle: "fade",
        title: "Capture Detection Framework Map",
        captionHtml: "<p>This diagram lays out the analytical framework's key variables — industry lobbying intensity, regulator characteristics, designation outcomes, and pricing behavior. The authors use it to test whether each link in the chain is statistically significant or merely coincidental. Pay attention to which pathways survive scrutiny: that is where the capture is real.</p>",
        props: {
          nodes: [
            { id: "lobby",    label: "Industry\nLobbying",    x: 15,  y: 90,  w: 110, h: 50, color: "#d35400" },
            { id: "capture",  label: "Type of\nCapture",      x: 175, y: 90,  w: 110, h: 50, color: "#c0392b" },
            { id: "desig",    label: "Designation\nOutcome",  x: 335, y: 90,  w: 120, h: 50, color: "#922b21" },
            { id: "deg",      label: "Degree of\nPredation",  x: 335, y: 230, w: 120, h: 50, color: "#1a5276" },
            { id: "price",    label: "Pricing\nBehavior",     x: 505, y: 160, w: 110, h: 50, color: "#6c3483" },
          ],
          paths: [
            { from: "lobby",   to: "capture", sig: true,  coef: null },
            { from: "capture", to: "desig",   sig: true,  coef: null },
            { from: "capture", to: "deg",     sig: false, coef: null },
            { from: "desig",   to: "price",   sig: true,  coef: null },
            { from: "deg",     to: "price",   sig: true,  coef: null },
          ],
          legend: {
            sigLabel: "Tested causal link",
            insigLabel: "Indirect / unclear pathway",
          },
        },
      },
    },
    {
      id: "finding-trajectory",
      navLabel: "Drug History",
      mobileLabel: "History",
      layout: "sidecar",
      themeShift: false,
      headline: "One molecule chased Ebola, SARS, then COVID",
      teaserHtml: "<p>Remdesivir's development history traces a calculated path: originally synthesized for hepatitis C, repurposed for Ebola, tested against MERS-CoV, and then rapidly repositioned as COVID-19's first authorized antiviral — each pivot accompanied by fresh orphan filings and regulatory accommodations.</p>",
      viz: {
        key: "timeline",
        mount: "svg",
        animationStyle: "fade",
        title: "Remdesivir's Disease Pivot History",
        captionHtml: "<p>The timeline marks each disease target remdesivir was repositioned toward — hepatitis C, Ebola, MERS-CoV, and COVID-19 — alongside the corresponding orphan filings and FDA interactions. Notice how the regulatory strategy closely shadows the commercial opportunity: each new indication brought a fresh wave of statutory benefits before clinical evidence was mature.</p>",
        props: {
          series: ["cumulative_patents", "oda_designations"],
          colors: { cumulative_patents: "#c0392b", oda_designations: "#1a5276" },
          seriesLabels: { cumulative_patents: "Cumulative patent filings", oda_designations: "Orphan Drug designations" },
          data: [
            { year: 2008, cumulative_patents: 1, oda_designations: 0 },
            { year: 2011, cumulative_patents: 3, oda_designations: 0 },
            { year: 2015, cumulative_patents: 5, oda_designations: 1 },
            { year: 2018, cumulative_patents: 7, oda_designations: 1 },
            { year: 2020, cumulative_patents: 8, oda_designations: 2 },
          ],
        },
      },
    },
    {
      id: "finding-capture",
      navLabel: "The Capture",
      mobileLabel: "Capture",
      layout: "immersive",
      themeShift: true,
      headline: "A relay race run in the dark — industry passed its baton through every gate",
      teaserHtml: "<p>The capture was not a single corrupt act. It was systemic and incremental: industry influence shaped the regulatory process, which granted orphan designation, which enabled market predation — all amplified by the degree of capture baked into the system. No fingerprints. No single smoking gun. Just a chain of quiet advantages, each defensible in isolation, devastating in aggregate.</p>",
      viz: {
        key: "sem",
        mount: "svg",
        animationStyle: "cascade",
        title: "Capture Chain: Influence to Predation",
        captionHtml: "<p>This structural equation model traces the full capture pathway: industry influence → regulatory process → orphan designation → market predation, with the degree of capture amplifying the final outcome. Each arrow represents a statistically tested link. The cascade animation reveals how influence accumulates step by step — watch for how the degree-of-capture node supercharges the endpoint even when each individual link appears modest.</p>",
        props: {
          nodes: [
            { id: "industry", label: "Industry Influence", x: 15, y: 175, w: 115, h: 50, color: "#d35400" },
            { id: "reg", label: "Regulatory Process", x: 175, y: 175, w: 120, h: 50, color: "#c0392b" },
            { id: "orphan", label: "Orphan Designation", x: 345, y: 175, w: 130, h: 50, color: "#922b21" },
            { id: "predation", label: "Market Predation", x: 460, y: 305, w: 125, h: 50, color: "#6c3483" },
            { id: "cap_deg", label: "Degree of Capture", x: 205, y: 50, w: 135, h: 50, color: "#1a5276" },
          ],
          paths: [
            { from: "industry", to: "reg", sig: true },
            { from: "reg", to: "orphan", sig: true },
            { from: "orphan", to: "predation", sig: true },
            { from: "cap_deg", to: "predation", sig: true },
          ],
          legend: {
            sigLabel: "Capture pathway (weak but systemic)",
            insigLabel: "No significant link",
          },
        },
      },
    },
    {
      id: "implication",
      navLabel: "Fix the Gap",
      mobileLabel: "Reform",
      layout: "sidecar",
      themeShift: false,
      headline: "Close the loophole before the next pandemic",
      teaserHtml: "<p>The authors argue that the Orphan Drug Act needs an explicit epidemic carve-out: once a disease exceeds defined population thresholds — or is declared a public health emergency — orphan protections should be suspended. Without reform, the next pandemic pathogen will face the same capture playbook, and governments will again pay monopoly rents for treatments developed largely on public funds.</p>",
      viz: {
        key: "accuracy",
        mount: "svg",
        animationStyle: "fade",
        title: "Policy Gap: No Epidemic Carve-Out",
        captionHtml: "<p>This chart maps what the Orphan Drug Act currently covers against what it leaves open during declared public health emergencies. The unshaded region is the policy gap — no automatic suspension triggers, no population-threshold override, no price controls. Look for how small a statutory amendment would be needed to close a vulnerability that cost governments billions during COVID-19.</p>",
        props: {
          total: 12,
          correct: 0,
          label: "ODA reform proposals adopted since 1983: 0 of 12+ submitted to Congress",
        },
      },
    },
  ],
  footerHtml: `
    <div class="footer-inner">
      <div class="footer-thesis">
        <div class="footer-label">Full Research Paper</div>
        <p><em>Public Choice (2022) 193:163–186</em></p>
      </div>
      <div class="footer-meta">
        <p><strong>Authors:</strong> https://doi.org/10.1007/s11127-022-01005-0</p>
        <p><strong>Journal:</strong> Science+Business Media, LLC, part of Springer Nature 2022, 2022</p>
        <p><strong>DOI:</strong> 10.1007/s11127-022-01005-0</p>
      </div>
      <div class="footer-actions">
        <a href="https://doi.org/10.1007/s11127-022-01005-0" target="_blank" class="footer-btn">Read the Paper</a>
      </div>
    </div>
  `,
};