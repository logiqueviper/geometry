# Prospective research plan — DRAFT, not approved or executed

This document is not a retroactive preregistration. Historical workload seeds
0–29 and their results have already been inspected. All historical analysis and
graphics are labeled **exploratory simulation**. No final-experiment tag has been
created. The machine-readable plan is `analysis/experiment_plan.json`.

The supplied project workflow requires literature review, then human approval of
this plan, then implementation, physical calibration, fair tuning, freeze, and
held-out evaluation. This draft makes the decision reviewable; it does not
assert those prerequisites have been completed.

## Research questions and bounded hypotheses

- **H1:** In the homogeneous, fixed-link primary regime, neighbor redistribution
  reduces job time when avoidable chunk-cost imbalance exceeds redistribution
  cost. Equal-cost, exact equal-count chunks supply no useful redistribution
  opportunity. We do not assume every nonzero variability level gives a benefit.
- **H2:** At fixed N and peer-link budget, graph connectivity explains part of
  observed rebalancing behavior. The continuous diffusion model is a heuristic
  for atomic tasks, not a theorem. Platonic connectivity need not retain an
  effect after graph metrics and workload factors are controlled.
- **H3:** Hub-assisted control with peer-only data transfer can compete with
  push and neighbor stealing under some communication regimes. Direction and
  size of any advantage are hypotheses, not guaranteed outcomes.
- **H4:** Avoidable imbalance and communication cost interact; higher variability
  can supply more balancing opportunity, while transfer and control cost can
  erase it. Long indivisible tasks can cap any improvement.
- **H5:** A separately calibrated simulator predicts held-out prototype job times
  and policy rankings. MAPE <=5% is a target. Failure of that target must be
  reported; hardware data cannot be altered to reach it.

## Information, topology, and policy fairness

Primary nodes remain homogeneous and links stable, preserving the requested
original model. Heterogeneity, CPU overhead, stragglers, and failures are
separately labeled extension regimes. Only the LPT oracle sees true task costs.
All other policies use the same measured/advertised information budget and
physical links. The hub policy advertises queue counts and idle epochs; the
master nominates edge-adjacent pairs. Inputs travel directly along peer edges,
not on added links. Stale hints must pass the same receiver acceptance/epoch
checks before transfer. A state-machine specification and tests are prerequisites.

Use the correct primary definitions of SS, GSS, FAC2, TSS, diffusion, steal-one,
and steal-half after their sources are verified. Parameters, queue operations,
message sizes, processor service costs, and termination rules must be documented
before frozen runs. The current guided denominator-2N variant is historical;
it cannot silently become the classic GSS comparator under the same name.

Every tunable policy receives the same maximum candidate count and tuning-seed
budget. Parameters are selected across a prespecified set of solids/workloads,
not separately optimized against each final cell. Nonparametric references and
the oracle are identified rather than given fictional tuning searches.

## Seed split and inventory

- Historical data: 0–29, never final evaluation.
- Tuning instances: 1000–1029. Evaluation instances: 2000–2029.
- Key evaluation comparisons: 3000–3099, a separate 100-seed set.
- Topology evaluation graphs: 4000–4019, independent of workload seed. Cross
  twenty graphs with thirty workload seeds; do not conflate graph and instance
  randomness as in the historical design.
- Topology tuning graphs: 5000–5019. Graph-model fit uses evaluation graphs
  4000–4014 and predicts 4015–4019; held-out metrics must not enter fitting.

The draft specifies 11,700 primary, 1,600 key-comparison, 21,600 rewiring, 3,240
scaling, and 23,040 communication runs before additional controls, ablations,
extensions, or hardware. Final inventory must be expanded and checked after
available equipment and implementation resources are known. These counts are
prospective planned sizes, not completed measurements.

Strong scaling uses a fixed job within each family. Geodesic counts 12/42/92/162
share 52,164 tasks; hypercubes 8/16/32/64/128 share 16,384. This preserves exact
equal-count chunks. Cross-family raw-time comparisons would compare different
jobs and are disallowed. Weak scaling uses 300 tasks per worker. Same-N controls
always share the exact same job and physical master resource model.

## Outcomes and statistical family

Primary outcome: master dispatch to last unique identified result, including
all communication and service queues. Report mean, median, IQR, and bootstrap
intervals. Speedup is a mean paired ratio, never a ratio of reported means.

The primary comparison family contains push versus static and hub-assisted
versus push and neighbor stealing in every primary workload/solid cell. With
six workloads and five solids, this is **90 comparisons**. Report Holm-adjusted
two-sided paired signed-rank tests, paired effect sizes, and a stated family-wise
error interpretation. Cell-wise intervals remain labeled as such; use simultaneous
intervals for family-wide claims. The oracle is not a fair competitive policy.

No-difference claims require equivalence testing with the prospectively declared
relative margin +/-1%, using paired log-ratios and justified assumptions. Report
both difference and equivalence tests; an inconclusive difference test alone
does not prove equivalence. If data violate t-based TOST assumptions, report
bootstrap equivalence bounds rather than silently changing the margin.

Graph comparisons use crossed graph/instance resampling or a justified mixed
model. A naive 600-observation IID bootstrap is disallowed. Define rebalancing
time and censoring before implementation: observer-only remaining-cost metrics
must never become scheduler information. Report nonattainment/censoring rather
than excluding graphs that never reach the balance threshold. The exact endpoint
and censored model remain a methods item requiring review before freeze.

## Calibration, faults, exclusions, and stopping

Calibration and validation hardware configurations are disjoint. Record raw
microbenchmarks, environment fingerprints, warmups, randomized order, temperatures,
and all failure logs. Validate complete task outputs before considering timing.

Failure recovery permits re-executed task **attempts** with attempt IDs and leases.
The required end invariant is one accepted final result per original ID. Physical
exactly-once execution cannot generally be guaranteed after an uncertain crash;
the failure-free exactly-once execution invariant remains separate.

Do not exclude slow or unfavorable runs. Exclude only independently diagnosed
corrupt manifests, invalid routing, instrumentation failure, or predefined
prototype warmups. Record each reason before inspecting its performance effect.
Use a prespecified simulation event-budget ceiling to diagnose nontermination;
retain failure outcomes rather than translating them into winning makespans.

After implementation, source verification, approved hardware protocol and tuning,
commit the exact code/data manifests and create `v-final-experiments`. Any method
change after inspecting evaluation results requires a new labeled experiment,
not replacement of the frozen evidence. No submission, authorship selection,
purchase, or acceptance claim is authorized by this draft.
