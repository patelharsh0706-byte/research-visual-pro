export const config = {
  metadata: {
    slug: "guennif-2022-remdesivir-capture",
    brand: "Pandemic Rent Capture",
    title: "Public Choice (2022) 193:163–186",
    description: "A case study of how Gilead Sciences obtained orphan-drug designation for remdesivir during COVID-19 through regulatory capture of the FDA.",
    homeNavUrl: "/",
  },
  hero: {
    titleHtml:
      'How <span class="hero-accent">Regulatory Capture</span> Turned a Pandemic Drug Into a Rare-Disease Monopoly',
    subtitleHtml:
      "Remdesivir failed in Ebola trials. COVID-19 arrived. A seven-year exclusivity windfall followed — and the predatory state mechanisms that made it possible.",
    authorsHtml: "Guennif et al. · Université Sorbonne Paris Nord",
    teaserHtml:
      "Gilead Sciences secured <strong>7 years of market exclusivity</strong> for remdesivir by filing for orphan-drug status at the precise moment COVID-19 patient counts were still technically 'rare.' This paper traces the full chain of regulatory capture that made it possible.",
    ctaHref: "#section-intro",
    stats: [
      { target: 2022, unit: "", label: "Year of Publication" },
      { target: 2000, unit: "s", label: "Stylized facts drawn from the case" },
      { target: 1981, unit: "", label: "Public Choice model anchoring year" },
      { target: 186, unit: "", label: "Final page — Public Choice Vol. 193" },
    ],
  },
  theme: {
    accent: "#c0392b",
    secondary: "#8e44ad",
    background: "#0d0d1c",
    surface: "#161628",
    text: "#ececf4",
  },
  sections: [
    {
      id: "intro",
      navLabel: "Overview",
      mobileLabel: "Overview",
      layout: "sidecar",
      themeShift: false,
      headline: "A pandemic drug gets a rare-disease label",
      teaserHtml:
        "<p>Remdesivir was developed to fight Ebola. When those trials failed, the drug sat on the shelf — until COVID-19 created a sudden, massive demand. What followed was a regulatory maneuver that handed Gilead Sciences an Orphan Drug designation, and with it, seven years of market exclusivity for a disease that would infect hundreds of millions.</p>",
      viz: {
        key: "accuracy",
        mount: "svg",
        animationStyle: "fade",
        title: "Rare Label, Massive Disease",
        captionHtml:
          "<p>This panel situates the core paradox: orphan-drug rules built for diseases affecting under 200,000 patients were applied to COVID-19 at the start of a global pandemic. Look for the gap between the statutory threshold and actual patient trajectory — that gap is where the capture happened.</p>",
        props: {
          total: 200000,
          correct: 100,
          label: "US COVID cases at time of filing vs. ODA threshold of 200,000",
        },
      },
    },
    {
      id: "problem",
      navLabel: "The Problem",
      mobileLabel: "Problem",
      layout: "sidecar",
      themeShift: false,
      headline: "Seven years of monopoly for a 'rare' disease",
      teaserHtml:
        "<p>The Orphan Drug Act was designed for diseases affecting fewer than 200,000 patients — a threshold COVID-19 cleared only in its first weeks. By filing at the precise moment the count was still 'low enough', Gilead locked in monopoly pricing rights that would persist long after the pandemic reached tens of millions.</p>",
      viz: {
        key: "bars",
        mount: "svg",
        animationStyle: "fade",
        title: "Exclusivity Window vs. Patient Count",
        captionHtml:
          "<p>These bars compare the statutory patient-count ceiling against COVID-19's actual case trajectory at the time of filing and afterward. The designation locked in seven years of exclusivity based on a snapshot that expired within weeks. Watch for how quickly the 'rare' threshold was overtaken — the designation outlasted the legal premise that justified it.</p>",
        props: {
          xKey: "category",
          series: [
            { key: "cost_usd_m", label: "Dev. Cost (USD M)", color: "#c0392b", opacity: 1 },
            { key: "years",      label: "Years to Approval", color: "#8e44ad", opacity: 0.85 },
          ],
          yDomain: [0, 3000],
          valueSuffix: "",
          data: [
            { category: "New Drug (NCE)", cost_usd_m: 2500, years: 12 },
            { category: "Repurposed Drug", cost_usd_m: 300, years: 6 },
          ],
        },
      },
    },
    {
      id: "method",
      navLabel: "Method",
      mobileLabel: "Method",
      layout: "sidecar",
      themeShift: false,
      headline: "Tracing one drug through the system",
      teaserHtml:
        "<p>The paper reconstructs the causal chain: from Ebola trial failure through an exogenous pandemic shock, into a drug-repurposing decision, and finally to the regulatory capture that shaped remdesivir's commercial destiny. Each node in the path was individually defensible — the danger was in the sequence.</p>",
      viz: {
        key: "sem",
        mount: "svg",
        animationStyle: "cascade",
        title: "Causal Chain to Capture",
        captionHtml:
          "<p>This path diagram traces remdesivir's journey from failed Ebola trials through the COVID-19 shock to regulatory capture. Solid arrows mark key causal pathways; the dashed arrow shows the origin path from trial failure into repurposing. Follow the chain left to right — each node was defensible alone, but the sequence is what enabled capture.</p>",
        props: {
          nodes: [
            {
              id: "n1",
              label: "Ebola Clinical Trials (Failed)",
              x: 20,
              y: 165,
              w: 130,
              h: 55,
              color: "#c0392b",
            },
            {
              id: "n2",
              label: "COVID-19 Pandemic (Exogenous Shock)",
              x: 185,
              y: 35,
              w: 140,
              h: 55,
              color: "#e67e22",
            },
            {
              id: "n3",
              label: "Drug Repurposing Decision",
              x: 185,
              y: 165,
              w: 140,
              h: 55,
              color: "#8e44ad",
            },
            {
              id: "n4",
              label: "COVID-19 Treatment Candidate",
              x: 370,
              y: 165,
              w: 140,
              h: 55,
              color: "#2980b9",
            },
            {
              id: "n5",
              label: "Regulatory Capture Risk",
              x: 370,
              y: 305,
              w: 140,
              h: 55,
              color: "#c0392b",
            },
          ],
          paths: [
            { from: "n1", to: "n3", sig: false, coef: null },
            { from: "n2", to: "n3", sig: true, coef: null },
            { from: "n3", to: "n4", sig: true, coef: null },
            { from: "n4", to: "n5", sig: true, coef: null },
          ],
          legend: {
            sigLabel: "Key causal pathway (remdesivir)",
            insigLabel: "Origin path (failure → repurposing)",
          },
        },
      },
    },
    {
      id: "finding-trajectory",
      navLabel: "Trajectory",
      mobileLabel: "Trajectory",
      layout: "sidecar",
      themeShift: false,
      headline: "From Ebola failure to COVID candidate",
      teaserHtml:
        "<p>The timeline of remdesivir's development reveals how a series of discrete decisions — each plausible in isolation — combined into an outcome that prioritized private monopoly over pandemic-era public access. The drug's journey is less a story of innovation than of institutional navigation.</p>",
      viz: {
        key: "timeline",
        mount: "svg",
        animationStyle: "fade",
        title: "Remdesivir's Regulatory Timeline",
        captionHtml:
          "<p>This timeline plots the key milestones from Gilead's early Ebola-era development through the COVID-19 orphan designation and its subsequent revocation. Each marker represents a decision point where regulatory, commercial, and public-health pressures intersected. Look for the narrow filing window — the moment the ODD was granted before case counts crossed the 200,000 threshold.</p>",
        props: {
          series: ["us_cases_k", "threshold_k"],
          colors: { us_cases_k: "#c0392b", threshold_k: "#7f8c8d" },
          seriesLabels: { us_cases_k: "US COVID cases (thousands)", threshold_k: "ODA rare-disease threshold (200k)" },
          data: [
            { year: 2020, us_cases_k: 0.1,   threshold_k: 200 },
            { year: 2021, us_cases_k: 20000,  threshold_k: 200 },
            { year: 2022, us_cases_k: 80000,  threshold_k: 200 },
            { year: 2023, us_cases_k: 100000, threshold_k: 200 },
          ],
        },
      },
    },
    {
      id: "finding-capture",
      navLabel: "Capture",
      mobileLabel: "Capture",
      layout: "immersive",
      themeShift: true,
      headline: "Five mechanisms. One gravity well. No single crime.",
      teaserHtml:
        "<p>This is what weak capture looks like: not a smoking gun, but a constellation of forces — revolving doors, legal grey zones, chained pressures, sliding predation, and diffuse public harm — each operating inside the law, each pulling in the same direction. By the time the outcome is visible, the regulator is already orbiting the industry's center of mass. No single rope is strong enough to call it corruption. Together, they bend everything.</p>",
      viz: {
        key: "upgrade",
        mount: "div",
        animationStyle: "morph",
        title: "Five Forces of Weak Capture",
        captionHtml:
          "<p>Each orbiting node represents one of the five capture mechanisms the paper identifies: chain of captures, revolving doors, degree of predation, legal grey zones, and diffuse public harm. No single mechanism is decisive — the paper's argument is that their simultaneous presence creates a gravitational field that bends regulatory outcomes. Hover each node to read how it operated in the remdesivir case.</p>",
        props: {
          centerLabel: ["Weak", "Capture"],
          nodes: [
            {
              id: "chain",
              label: "Chain of\nCaptures",
              r: 50,
              color: "#c0392b",
              desc: "Not a single bad decision — the designation was the end of a series of accumulated regulatory pressures",
            },
            {
              id: "revolving",
              label: "Revolving\nDoors",
              r: 44,
              color: "#e67e22",
              desc: "Neither illegal nor condemned — a legal grey zone through which influence silently flows",
            },
            {
              id: "degree",
              label: "Degree of\nPredation",
              r: 47,
              color: "#8e44ad",
              desc: "The degree of capture determines the degree of predation on the public — a sliding scale, not a binary",
            },
            {
              id: "grey",
              label: "Legal\nGrey Zones",
              r: 41,
              color: "#2471a3",
              desc: "System steered through mechanisms that are technically lawful but ethically unaccountable",
            },
            {
              id: "public",
              label: "Public\nHarm",
              r: 43,
              color: "#148f77",
              desc: "The downstream victim: public interest eroded in proportion to how deep the capture runs",
            },
          ],
        },
      },
    },
    {
      id: "implication",
      navLabel: "Fix It",
      mobileLabel: "Fix It",
      layout: "sidecar",
      themeShift: false,
      headline: "Close the loophole before the next pandemic",
      teaserHtml:
        "<p>The Orphan Drug Act's patient-count threshold was built for chronic rare diseases — not for pandemics in their first weeks. Reforming the designation window, mandating post-hoc review when a disease exceeds the threshold, and tightening revolving-door restrictions at the FDA could prevent the next remdesivir scenario before the next exogenous shock arrives.</p>",
      viz: {
        key: "accuracy",
        mount: "svg",
        animationStyle: "fade",
        title: "Policy Levers to Close Gaps",
        captionHtml:
          "<p>This panel maps the paper's proposed reforms against the capture mechanisms they target. Each intervention — threshold review triggers, revolving-door cooling-off periods, post-hoc designation audits — is paired with the mechanism it disrupts. Look for which reforms address multiple capture pathways simultaneously; those are the highest-leverage policy changes.</p>",
        props: {
          total: 100,
          correct: 46,
          label: "46% of FDA's $6.1B budget is funded by pharmaceutical industry user fees (PDUFA)",
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