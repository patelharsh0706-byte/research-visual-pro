# Generator agents package
# Each agent has one job and one input/output contract.
#
# Pipeline order:
#   1. agent_extractor     — PDF → paper_data.json
#   2. agent_story_planner — paper_data → narrative beats
#   3. agent_chart_selector— beats + paper_data → chart_plan with viz_key + props
#   4. agent_config_writer — chart_plan + paper_data → config.ts + page.mdx
#   5. agent_validator     — config + mdx + paper_data → PASS/FAIL with errors
#   6. agent_custom_viz    — (optional) custom beat → new D3 viz module
#   7. agent_reviewer      — benchmark audit vs gold standard → patched config.ts
