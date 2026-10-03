# Retrospective statistical extension

All existing seeds have been inspected. This extension is exploratory; it is
not a preregistration or confirmation of an invented new policy. Saved source:
`results/exploratory_statistics.json` and CSV. Recompute with
`python -m analysis.statistics`.

The difference-test family contains all 5 solids × 5 workloads × 2 comparisons
(push versus static and neighbor stealing), for 50 paired cells. Tests use
two-sided Wilcoxon signed ranks and Holm adjustment over all 50 p-values. All
zero differences return p=1. The script reports paired Cohen dz; zero variance
with a nonzero mean difference is undefined, represented as null, not infinity.
Ratio confidence intervals bootstrap paired seed ratios with 10,000 resamples.
Those intervals remain uncorrected cell-wise intervals and cannot support a
family-wide confidence statement.

Equivalence is tested on paired log ratios with a relative ±1% margin, using
t-based two one-sided tests and a separate Holm adjustment over 50 equivalence
p-values. The margin came from the supplied instructions after historical data
were observed. It is therefore retrospective and requires assumptions about
paired log-ratio mean inference. No failed difference test is relabeled as
equivalence. Constant workloads have exact deterministic timing under this
model; their lack of redistribution benefit is also analytic.

Under this declared retrospective family, 20 of 25 static/push difference cells
and zero of 25 neighbor-steal/push difference cells pass adjusted p<0.05. Five
static/push and sixteen neighbor-steal/push cells pass the separately adjusted
equivalence criterion. These are descriptive exploratory outcomes conditional
on synthetic workloads and the chosen model, not proof of universal equality or
geometric superiority. Read the saved per-cell results before attributing a
direction or magnitude; a significant difference alone does not give direction.

The historical rewiring experiment ties one graph to each workload seed. It is
not the planned crossed 20-graph × 30-workload design; these 30 combined samples
cannot separate graph and workload variance. Future graph inference must use
crossed resampling or a justified mixed model and prespecified outcomes.
