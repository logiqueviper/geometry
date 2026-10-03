# Visual study explorer

- `dashboard.html`: interactive, fully offline explorer. Open the extracted file
  in a browser. Change topology, task-cost workload, or metric; hover over every
  retained seed. Confidence intervals and an accessible numerical table use the
  saved observations and bootstrap summaries.
- `visual-atlas.pdf`: standalone publication-width figures with captions.
- `figure-index.json`: figure inventory, evidence scope, sizes, and provenance.
- `../paper/figures/`: vector PDF/SVG and 300-dpi PNG versions of every figure.
- `../results/visual_data.json`: saved inputs for every plotted value, CI,
  illustrative execution trace, and analytic graph calculation.

Regenerate with `python -m analysis.make_all` from the repository root. Add
`--refresh-graphs` to recompute all graph metrics. The script never reruns or
overwrites historical benchmark CSVs. Historical results are exploratory and
are separate from the prospective research plan and any future hardware data.

Missing experiments are intentionally not drawn: no hardware parity plot,
energy chart, failure experiment, hub-policy result, scaling curve, full
latency-by-bandwidth grid, or preregistered critical-difference diagram exists.
