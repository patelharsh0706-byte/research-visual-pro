export const config = {
  slug: "kelchtermans-2022-licensing-learning",
  metadata: {
    brand: "License to Learn",
    title: "Do Licensors Learn from Out-Licensing? Empirical Evidence from the Pharmaceutical Industry",
    description: "Analysing 1,861 pharmaceutical licensing deals, this study reveals that technology sellers gain significant knowledge spillbacks — not just revenue — from out-licensing.",
    homeNavUrl: "/data",
  },
  hero: {
    titleHtml: 'The <span class="hero-accent">Hidden Learning</span> Inside a Licensing Deal',
    subtitleHtml: "Sellers gain knowledge, not just revenue",
    authorsHtml: "Kelchtermans et al. · KU Leuven & IMT Lucca",
    teaserHtml: "When pharma firms license their technology out, they don't just earn royalties — they learn. Across <strong>1,861 deals</strong>, licensors cited licensee patents <strong>146% more</strong> after signing, with 73% of those citations flowing in directions that had never existed before.",
    ctaHref: "#section-intro",
    stats: [
      {
        target: 1861,
        unit: " deals",
        label: "Pharma licensing deals analysed",
      },
      {
        target: 254,
        unit: " firms",
        label: "Pharma & biotech firms tracked",
      },
      {
        target: 146,
        unit: "%",
        label: "Increase in patent citations from licensing",
      },
      {
        target: 73,
        unit: "%",
        label: "Novel citations — never cited before licensing",
      },
    ],
  },
  theme: {
    accent: "#5B8DB8",
    secondary: "#E67E22",
  },
  sections: [
    {
      id: "intro",
      navLabel: "Overview",
      mobileLabel: "Overview",
      headline: "The Hidden Payoff Inside a Licensing Deal",
      viz: {
        key: "sem",
        mount: "svg",
        title: "Two Pathways From One Deal",
        captionHtml: "<p>This structural equation model maps how out-licensing affects a licensor's R&D output through two distinct pathways. The conventional view (grey) holds that licensing revenue funds more research — but the study finds that pathway is statistically insignificant. Look instead at the purple arrow: reverse knowledge spillback, where the licensor learns from its licensee, is the real driver of innovation gains.</p>",
        props: {
          nodes: [
            {
              id: "outlicensing",
              label: "Technology\nOut-Licensing",
              x: 20,
              y: 170,
              w: 155,
              h: 60,
              color: "#5B8DB8",
            },
            {
              id: "spillback",
              label: "Reverse Knowledge\nSpillback",
              x: 218,
              y: 55,
              w: 164,
              h: 60,
              color: "#7B68EE",
            },
            {
              id: "revenue",
              label: "Licensing\nRevenue",
              x: 218,
              y: 285,
              w: 164,
              h: 60,
              color: "#888888",
            },
            {
              id: "innovation",
              label: "Licensor R&D\nOutput",
              x: 425,
              y: 170,
              w: 155,
              h: 60,
              color: "#E67E22",
            },
          ],
          paths: [
            { from: "outlicensing", to: "spillback", sig: true },
            { from: "spillback", to: "innovation", sig: true },
            { from: "outlicensing", to: "revenue", sig: false },
            { from: "revenue", to: "innovation", sig: false },
          ],
          legend: {
            sigLabel: "Hidden learning pathway (study finding)",
            insigLabel: "Conventional textbook pathway",
          },
        },
      },
    },
    {
      id: "problem",
      navLabel: "Context",
      mobileLabel: "Context",
      headline: "Licensing Exploded — But Who Benefits?",
      viz: {
        key: "bars",
        mount: "svg",
        title: "Licensors Cite Far More Patents",
        captionHtml: "<p>This chart compares average cross-firm patent citations between licensing pairs (firms that signed a deal together) and control pairs (similar firms that never licensed). Licensing pairs cite each other at roughly twice the rate of controls — and the gap is even more pronounced for biotech firms (5.36 vs 1.66). The key question the study asks: does licensing <em>cause</em> this knowledge flow, or do innovative firms simply license more?</p>",
        props: {
          data: [
            { group: "All Firms", licensing: 3.49, control: 1.66 },
            { group: "Pharma Only", licensing: 3.40, control: 1.66 },
            { group: "Biotech Only", licensing: 5.36, control: 1.66 },
          ],
          xKey: "group",
          series: [
            { key: "licensing", label: "Licensing Pairs (avg citations)", color: "#5B8DB8" },
            { key: "control", label: "Control Pairs (avg citations)", color: "#aaaaaa" },
          ],
          yDomain: [0, 6],
          valueSuffix: "",
        },
      },
    },
    {
      id: "method",
      navLabel: "Data",
      mobileLabel: "Data",
      headline: "1,861 Deals, Two Decades of Data",
      viz: {
        key: "accuracy",
        mount: "svg",
        title: "Matched Pairs After Rigorous Filtering",
        captionHtml: "<p>Starting from 4,113 licensing dyads sourced from the RoyaltyStat database (1990–2016), the authors applied Coarsened Exact Matching (CEM) to find non-licensing firm pairs with nearly identical R&D histories, patent stocks, and firm size. Only 1,608 pairs survived — roughly 39% of the original pool. This retained sample is what makes the causal inference credible: the matched controls are near-twins of the licensors before the deal was signed.</p>",
        props: {
          total: 4113,
          correct: 1608,
          correctLabel: "1,608 Matched Licensing Pairs",
          incorrectLabel: "2,505 Excluded (unmatched)",
          sublabel: "licensing dyads retained after coarsened exact matching (CEM)",
        },
      },
    },
    {
      id: "players",
      navLabel: "Players",
      mobileLabel: "Players",
      headline: "The Giants Behind the Deals",
      viz: {
        key: "bars",
        mount: "svg",
        title: "Top Licensors and Licensees by Deals",
        captionHtml: "<p>A handful of firms dominate both sides of the market. Roche is uniquely positioned as both a heavy licensor (80 deals) and licensee (127 deals), while Crucell and Elan appear almost exclusively as sellers. On the buyer side, Pfizer and Novartis lead with 139 and 133 deals respectively — but almost no licensor activity. This asymmetry matters: the study's learning effect is measured specifically for the licensor side.</p>",
        props: {
          data: [
            { party: "Roche", licensors: 80, licensees: 127 },
            { party: "Crucell", licensors: 68, licensees: 0 },
            { party: "Elan", licensors: 58, licensees: 0 },
            { party: "Pfizer", licensors: 0, licensees: 139 },
            { party: "Novartis", licensors: 0, licensees: 133 },
          ],
          xKey: "party",
          series: [
            { key: "licensors", label: "Licensor Deals", color: "#4e79a7" },
            { key: "licensees", label: "Licensee Deals", color: "#f28e2b" },
          ],
          yDomain: [0, 150],
          valueSuffix: "",
        },
      },
    },
    {
      id: "finding",
      navLabel: "Finding",
      mobileLabel: "Finding",
      headline: "Sellers Learn More Than Twice as Much",
      viz: {
        key: "precision",
        mount: "svg",
        title: "Licensors Outpace Controls in Citations",
        captionHtml: "<p>This panel shows relative citation rates compared to the baseline cross-firm average of 2.58 citations. Licensing pairs cite each other significantly more than non-licensing controls — and biotech licensors show the largest effect at +0.92 above baseline. The control group sits at −1.0, confirming the gap is not explained by pre-existing innovativeness. The study attributes this surplus to reverse knowledge spillback: licensors absorbing know-how from the firms they sold technology to.</p>",
        props: {
          data: [
            { label: "Biotech Licensors", v: 0.92 },
            { label: "All Licensing Pairs", v: 0.5 },
            { label: "Pharma Licensors", v: 0.43 },
            { label: "Non-Licensing (control)", v: -1.0 },
          ],
          centerLine: "Avg cross-firm citation rate: 2.58",
          valueLabel: "Relative citation rate (licensing vs. baseline)",
        },
      },
    },
    {
      id: "rigor",
      navLabel: "Rigor",
      mobileLabel: "Rigor",
      headline: "Comparing Apples to Apples",
      viz: {
        key: "matrix",
        mount: "svg",
        title: "Before vs. After Matching Balance",
        captionHtml: "<p>This balance table shows what CEM matching actually achieved. Before matching, licensing dyads were drawn from a pool of 865,401 potential control pairs — and the patent-stock gap between licensor and control was a massive 883 patents on average, making fair comparison impossible. After matching, the gap collapsed to just 6.39 patents across 1,608 paired dyads. This near-elimination of pre-treatment imbalance is what allows the authors to attribute post-licensing citation gains to the deal itself.</p>",
        props: {
          parties: ["Pre-CEM", "Post-CEM"],
          media: [
            "Licensing Dyads (N)",
            "Non-Licensing Dyads (N)",
            "Patent-Stock Gap",
          ],
          sigData: {
            "Pre-CEM": {
              "Licensing Dyads (N)": "4,113",
              "Non-Licensing Dyads (N)": "865,401",
              "Patent-Stock Gap": "883.60",
            },
            "Post-CEM": {
              "Licensing Dyads (N)": "1,608",
              "Non-Licensing Dyads (N)": "1,608",
              "Patent-Stock Gap": "6.39",
            },
          },
        },
      },
    },
    {
      id: "implication",
      navLabel: "Takeaway",
      mobileLabel: "Takeaway",
      headline: "Selling Tech Can Make You Smarter",
      viz: {
        key: "accuracy",
        mount: "svg",
        title: "Most New Citations Are Truly Novel",
        captionHtml: "<p>Of all the patent citations that licensors directed at their licensees after the deal, 73% had never existed between those two firms before — entirely new knowledge channels opened by the licensing relationship. Only 27% were citations that already existed pre-deal. This novelty ratio is the sharpest evidence that licensing is not merely reinforcing existing ties but actively creating new learning pathways that would not have formed otherwise.</p>",
        props: {
          total: 100,
          correct: 73,
          correctLabel: "73% Novel Citations",
          incorrectLabel: "27% Prior Citations",
          sublabel: "of licensor citations to licensee are first-time — knowledge that never flowed this way before licensing",
        },
      },
    },
  ],
  footerHtml: `
    <div class="footer-inner">
      <div class="footer-thesis">
        <div class="footer-label">Full Research Paper</div>
        <p><em>Technovation 112 (2022) 102405</em></p>
      </div>
      <div class="footer-meta">
        <p><strong>Authors:</strong> Available online 16 October 2021</p>
        <p><strong>Journal:</strong> ScienceDirect, 2022</p>
        <p><strong>DOI:</strong> 10.1016/j.technovation.2021.102405</p>
      </div>
      <div class="footer-actions">
        <a href="https://doi.org/10.1016/j.technovation.2021.102405" target="_blank" class="footer-btn">Read the Paper</a>
      </div>
    </div>
  `,
};

