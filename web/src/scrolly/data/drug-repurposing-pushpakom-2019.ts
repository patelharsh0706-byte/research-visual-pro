export const config = {
    metadata: {
        title: "Drug Repurposing: Progress, Challenges and Recommendations",
        description: "A comprehensive review of drug repurposing strategies — from serendipitous discovery to systematic computational approaches — by Pushpakom et al., Nature Reviews Drug Discovery, 2019.",
        brand: "Second Life for Drugs",
        homeNavUrl: "/data"
    },
    hero: {
        label: "Nature Reviews Drug Discovery · 2019",
        titleHtml: 'Drug <span class="hero-accent">Repurposing</span>',
        subtitleHtml: "Progress, Challenges and Recommendations",
        authorsHtml: "Pushpakom et al. · University of Liverpool",
        teaserHtml: 'Developing a new drug from scratch costs over <strong>$2 billion</strong> and takes 12+ years. Repurposing an existing molecule costs ten times less and reaches patients faster. This review maps the full landscape — 12+ approved successes, the data behind them, and the six structural changes needed to unlock the field.',
        ctaHref: "#section-landscape",
        stats: [
            { target: 7000, unit: "+", label: "Rare Diseases" },
            { target: 95, unit: "%", label: "Lack Approved Treatment" },
            { target: 300, unit: "M", label: "Avg. Repurposing Cost (USD)" },
            { target: 12, unit: "+", label: "Approved Repurposed Drugs" }
        ]
    },
    sections: [
        {
            id: "landscape",
            navLabel: "Opportunity",
            mobileLabel: "Landscape",
            viz: {
                key: "bubbles",
                title: "The Untreated Disease Landscape",
                captionHtml: "7,000+ rare diseases (left) meet ≥20,000 existing approved drugs (right). The repurposing opportunity lives at the intersection — computational, clinical, and omics approaches bridge the two worlds.",
                mount: "svg",
                props: {
                    centers: [
                        { id: "diseases", label: "7,000+\nRare Diseases",   dx: -105, dy: 0, r: 50, color: "#1A5276" },
                        { id: "drugs",    label: "≥20,000\nApproved Drugs", dx:  105, dy: 0, r: 50, color: "#1A6B8A" }
                    ],
                    vars: [
                        { label: "Oncology",       cat: "d", angle: -115, dist: 188, r: 30, color: "#2C3E50" },
                        { label: "Rare\nDisease",  cat: "d", angle: -148, dist: 195, r: 28, color: "#2C3E50" },
                        { label: "Neurology",      cat: "d", angle: -168, dist: 200, r: 26, color: "#2C3E50" },
                        { label: "Infectious",     cat: "d", angle:  175, dist: 192, r: 24, color: "#34495E" },
                        { label: "Cardiology",     cat: "d", angle:  155, dist: 188, r: 24, color: "#34495E" },
                        { label: "GWAS\nScreening",       cat: "r", angle:  -30, dist: 188, r: 28, color: "#1A6B8A" },
                        { label: "EHR\nMining",           cat: "r", angle:   10, dist: 193, r: 28, color: "#1A6B8A" },
                        { label: "Phenotypic\nAssays",    cat: "r", angle:   48, dist: 188, r: 26, color: "#2980B9" },
                        { label: "Network\nAnalysis",     cat: "r", angle:   80, dist: 192, r: 26, color: "#2980B9" },
                        { label: "Clinical\nObservation", cat: "r", angle:  112, dist: 188, r: 26, color: "#5DADE2" }
                    ],
                    cornerLabels: {
                        media:    "THERAPEUTIC AREAS",
                        socioEcon: "DISCOVERY APPROACHES"
                    }
                }
            }
        },
        {
            id: "cost",
            navLabel: "The Case",
            mobileLabel: "Cost",
            viz: {
                key: "bars",
                title: "The Economic Argument",
                captionHtml: "Cost Index (blue): repurposed drugs require ~10% of a new drug's $3B development budget. Timeline Index (orange): repurposing compresses the path to approval by ~60%. Both bars show values as % of a new chemical entity baseline.",
                mount: "svg",
                props: {
                    data: [
                        { party: "Repurposed Drug", media: 10, combined: 42 },
                        { party: "New Chemical Entity", media: 83, combined: 97 }
                    ],
                    colors: { media: "#1A6B8A", combined: "#E67E22" }
                }
            }
        },
        {
            id: "pathways",
            navLabel: "Pathways",
            mobileLabel: "Methods",
            viz: {
                key: "sem",
                title: "Discovery Pathways to New Indications",
                captionHtml: "Four routes lead to new drug indications. Established pathways (green arrows) are proven — serendipity gave us Sildenafil; clinical observation gave us Lenalidomide. Computational screening (GWAS, 92 genes identified) and multi-omics mining are the emerging, scalable frontier.",
                mount: "svg",
                props: {
                    nodes: [
                        { id: "serendipity",  label: "Serendipitous\nObservation",  x: 30, y: 30,  w: 120, h: 46, color: "#1A5276" },
                        { id: "computation",  label: "Computational\nScreening",    x: 30, y: 115, w: 120, h: 46, color: "#1A5276" },
                        { id: "clinical_obs", label: "Clinical\nObservation",       x: 30, y: 200, w: 120, h: 46, color: "#1A5276" },
                        { id: "omics",        label: "Multi-Omics\n& EHR Mining",   x: 30, y: 285, w: 120, h: 46, color: "#1A5276" },
                        { id: "approval",     label: "New\nIndication",             x: 450, y: 80,  w: 110, h: 46, color: "#1A6B8A" },
                        { id: "pipeline",     label: "Drug\nPipeline",              x: 450, y: 250, w: 110, h: 46, color: "#2980B9" }
                    ],
                    paths: [
                        { from: "serendipity",  to: "approval", sig: true,  coef: "Proven" },
                        { from: "computation",  to: "approval", sig: true,  coef: "GWAS" },
                        { from: "clinical_obs", to: "approval", sig: true,  coef: "Lenalidomide" },
                        { from: "omics",        to: "approval", sig: false, coef: "Emerging" },
                        { from: "computation",  to: "pipeline", sig: true,  coef: "92 genes" },
                        { from: "omics",        to: "pipeline", sig: true,  coef: "9.4M tests" }
                    ],
                    legend: { sigLabel: "Established pathway", insigLabel: "Emerging / under evaluation" }
                }
            }
        },
        {
            id: "commercial",
            navLabel: "Successes",
            mobileLabel: "Revenue",
            viz: {
                key: "precision",
                title: "The Winner-Takes-All Revenue Distribution",
                captionHtml: "Annual peak revenues of repurposed blockbusters, shown as deviation from the group average ($3.1B). Lenalidomide ($8.2B) and Rituximab ($7.0B) sit far above average; the tail drugs cluster below. Hover each dot for the drug name and revenue figure.",
                mount: "svg",
                props: {
                    data: [
                        { p: "Lenalidomide",  v:  1.00 },
                        { p: "Rituximab",     v:  0.76 },
                        { p: "Fingolimod",    v:  0.00 },
                        { p: "Celecoxib",     v: -0.09 },
                        { p: "Sildenafil",    v: -0.21 },
                        { p: "Atomoxetine",   v: -0.45 },
                        { p: "Minoxidil",     v: -0.45 },
                        { p: "Raloxifene",    v: -0.57 }
                    ]
                }
            }
        },
        {
            id: "policy",
            navLabel: "Policy",
            mobileLabel: "Policy",
            viz: {
                key: "matrix",
                title: "Orphan Drug Regulatory Incentives by Region",
                captionHtml: "Highlighted cells indicate active incentives. The US leads with the strongest combined package — 7-year market exclusivity, 50% tax credit, and full FDA fee waivers. EU and Japan offer 10-year exclusivity but differ on tax treatment.",
                mount: "svg",
                props: {
                    parties: ["United States", "European Union", "Japan", "Australia"],
                    media: ["Exclusivity", "Tax Credit", "Fee Waiver", "Priority Review", "Designation"],
                    sigData: {
                        "United States": {
                            "Exclusivity":     "7 yrs",
                            "Tax Credit":      "50%",
                            "Fee Waiver":      "Yes",
                            "Priority Review": "Yes",
                            "Designation":     "Yes"
                        },
                        "European Union": {
                            "Exclusivity":     "10 yrs",
                            "Tax Credit":      null,
                            "Fee Waiver":      "Yes",
                            "Priority Review": "Yes",
                            "Designation":     "Yes"
                        },
                        "Japan": {
                            "Exclusivity":     "10 yrs",
                            "Tax Credit":      "40%",
                            "Fee Waiver":      null,
                            "Priority Review": "Yes",
                            "Designation":     "Yes"
                        },
                        "Australia": {
                            "Exclusivity":     "5 yrs",
                            "Tax Credit":      "40%",
                            "Fee Waiver":      null,
                            "Priority Review": "Yes",
                            "Designation":     "Yes"
                        }
                    }
                }
            }
        },
        {
            id: "challenges",
            navLabel: "Barriers",
            mobileLabel: "Barriers",
            viz: {
                key: "accuracy",
                title: "The Clinical Translation Gap",
                captionHtml: "NIH-NCATS screened 57 compounds from pharmaceutical collections for repurposing potential. Only 9 were funded for further clinical development — a 16% advance rate that illustrates the steep translational hurdle even for the most systematically screened candidates.",
                mount: "svg",
                props: {
                    total: 57,
                    correct: 9,
                    sublabel: "of 57 NIH-NCATS screened compounds funded for development",
                    correctLabel: "9 Advanced",
                    incorrectLabel: "48 Not Advanced"
                }
            }
        },
        {
            id: "recommendations",
            navLabel: "The Way Forward",
            mobileLabel: "Roadmap",
            viz: {
                key: "upgrade",
                title: "Six Structural Recommendations",
                captionHtml: "Hover each node for detail. The six recommendations span data sharing, assay standardisation, pipeline integration, pre-competitive collaboration, smarter clinical trial design, and patient registries — a systems-level agenda, not a single fix.",
                mount: "div",
                props: {
                    centerLabel: ["Drug", "Repurposing", "2.0"],
                    nodes: [
                        {
                            id: "open-data",
                            label: "Open Data\nRepositories",
                            r: 36, color: "#1A6B8A",
                            desc: "Share negative trial results and preclinical screens publicly. NIH-NCATS and MRC-AstraZeneca consortia (£7M, $12.7M) are early models."
                        },
                        {
                            id: "assays",
                            label: "Standardised\nAssays",
                            r: 36, color: "#1A6B8A",
                            desc: "Harmonise phenotypic screening protocols so drug-response data is comparable across labs and institutions."
                        },
                        {
                            id: "pipelines",
                            label: "Integrated\nPipelines",
                            r: 36, color: "#2980B9",
                            desc: "Connect transcriptomic, proteomic, and clinical databases into a single queryable stack to remove data silos."
                        },
                        {
                            id: "consortia",
                            label: "Pre-competitive\nConsortia",
                            r: 36, color: "#2980B9",
                            desc: "Pool IP between pharma companies for rare diseases too small for solo investment — de-risk the economics."
                        },
                        {
                            id: "trials",
                            label: "Adaptive\nTrial Design",
                            r: 36, color: "#27AE60",
                            desc: "Use biomarker stratification and adaptive Phase II/III designs to cut attrition and reach significance faster."
                        },
                        {
                            id: "registries",
                            label: "Patient\nRegistries",
                            r: 36, color: "#27AE60",
                            desc: "Real-world EHR data from patients on existing drugs is an under-exploited signal for off-label efficacy."
                        }
                    ]
                }
            }
        }
    ],
    theme: {
        accent: "#1A6B8A",
        secondary: "#27AE60"
    },
    footerHtml: `
    <div class="footer-inner">
      <div class="footer-thesis">
        <div class="footer-label">Full Research Paper</div>
        <p><em>Drug repurposing: progress, challenges and recommendations</em></p>
      </div>
      <div class="footer-meta">
        <p><strong>Authors:</strong> Pushpakom S, Iorio F, Eyers PA et al.</p>
        <p><strong>Journal:</strong> Nature Reviews Drug Discovery, 2019</p>
        <p><strong>DOI:</strong> 10.1038/nrd.2018.168</p>
      </div>
      <div class="footer-actions">
        <a href="https://doi.org/10.1038/nrd.2018.168" target="_blank" class="footer-btn">Read the Paper</a>
      </div>
    </div>
  `
};
