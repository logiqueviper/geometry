# Audit of the starting study

Evidence: **simulation**, not a prototype measurement. Baseline commit:
`9ea4fb844c89648717e8cc190a9e5b2887e649a6`.

The original ZIP passes its CRC checks. Its simulator, geometry, and test files
match the checkout. The full original suite passes **116 tests**; the result
verifier checks **16,050 records** and reproduces **141 cases**. The eight-page
legacy IEEE journal PDF rebuilds. It has no unresolved references or overfull
boxes, but does have underfull vertical-box notices. Those notices and the older
class remain formatting work for the journal revision. Data hashes are recorded
in `results/audit.json`. Existing measurements have already been inspected and
cannot retrospectively become preregistered or held-out evaluation data.

| Item | Finding | Required correction |
|---|---|---|
| W1 Literature/positioning | Confirmed: five starting references; no comprehensive prior-art search. 56 DOI metadata records now verified, including 26 since 2019; full-text review remains pending. | Verify primary records and read attributed claims; expand relevant literature before novelty framing. |
| W2 Mostly null competitive findings | Confirmed: push has the lowest mean in only one variable-cost primary cell. | Retain negative findings; evaluate hub-assisted policy on fresh seeds, with equal tuning budgets. |
| W3 No hardware validation | Confirmed: no physical measurements exist in the artifact. | Human prototype, separate calibration and held-out validation. Never fill this with simulation. |
| W4 Idealized resources | Confirmed: homogeneous compute, fixed links, zero worker scheduling CPU cost. NIC/master sensitivities already exist. | Add optional measured CPU/heterogeneity/failure models after preregistration approval; preserve original default behavior. |
| W5 Small scale | Confirmed: 4–20 workers. | Standalone geodesic graph construction now exists for 42, 92, and 162 vertices; scheduler scaling remains unrun. |
| W6 Worker-count confounding | Confirmed for comparisons across solids. Existing topology controls hold N fixed. | Analyze worker graph and hub graph separately; report degree, diameter, cuts, and spectra. No causal shape claim from strong scaling. |
| W7 Artificial clustered work | Confirmed and previously disclosed. | Keep as a stress test; add real workloads and license-cleared traces to prospective experiments. |
| W8 Multiple comparisons | Confirmed: starting intervals are uncorrected and exploratory. | Add transparently retrospective Holm-adjusted paired analyses; preregister the final family. Non-significance alone is not equivalence. |
| W9 Competitors | Confirmed: seven policies, no oracle/factoring/TSS/diffusion/hub policy/real runtime. | Implement and verify those policies after method approval and source verification; compare fairly. |
| W10 Geometry framing | Partial: title emphasizes solids, but text already denies universal geometric superiority. | New journal framing must match tested graph properties; cannot advertise prototype validation before measurements. |
| W11 Tuning leakage | Confirmed: exploratory parameter variants have no tuning/evaluation split. | Preserve as historical exploratory data; new tuning and evaluation seeds must be disjoint from each other and from all historical seeds. |

The visual refresh uses all existing runs and exposes distributions and intervals.
It does not cure the missing hardware, missing methods, or prospective evidence.
The full journal upgrade remains at its literature and prospective-design gates.

Independent new checks reproduce all five specified worker-graph algebraic
connectivity values. The cone/hub spectra are also checked. The graph-analysis, statistics, and artifact-provenance suites bring the full test
count to **160**. Exact small-graph cuts and large-graph heuristic cuts are
distinguished in the saved graph records.

A manuscript rounding error in the icosahedral Pareto Platonic/rewired mean ratio
was corrected from 1.004 to 1.003 using the original full-precision summary.
Observed decimal values are now generated from saved data before typesetting.
