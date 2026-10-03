# AGENT INSTRUCTION FILE
## Project: Master-Centered Platonic-Solid Cluster Scheduling — Top-Tier IEEE Journal Paper

Read this whole file before doing anything. Re-read Section 1 (Golden Rules) at the start of every work session.

---

## 0. WHAT THIS FILE IS

**Goal (plain words):** turn an existing simulation study into a paper strong enough to be sent to a top journal. **Primary target:** IEEE Transactions on Parallel and Distributed Systems (TPDS). **Fallbacks:** IEEE Transactions on Cloud Computing, IEEE Transactions on Computers, Journal of Parallel and Distributed Computing (JPDC), Future Generation Computer Systems (FGCS). Before writing, open the target journal's "Information for Authors" page and record: page limit, overlength charges, blind/open review policy, supplementary-material policy, AI-use disclosure rule. Save these in `docs/JOURNAL_RULES.md`.

**Honest limit:** nobody can guarantee acceptance. This file maximizes the quality and honesty of the work. A weak result honestly reported is better than a strong-looking result that is not true.

**Who does what**

| Task | Agent | Human (the author) |
|---|---|---|
| Code, simulator, analysis, plots, LaTeX, literature search | YES | reviews |
| Buying and assembling hardware, wiring, running experiments on it | NO — writes the runbook and scripts | YES |
| Choosing authors, affiliations, final claims, submission | NO | YES |
| Inventing numbers, references, or results | **NEVER** | **NEVER** |

If something needs a physical action or a decision, write it into `docs/HUMAN_TODO.md` with exact steps and expected output format. Do not guess and do not simulate "pretend hardware results".

---

## 1. GOLDEN RULES

### MUST
1. **Every number in the paper comes from a saved data file** produced by a script. Generate tables, figures and in-text numbers automatically (e.g. write `results/numbers.json`, then generate LaTeX macros `\newcommand{\MakespanIcosaPush}{216.2}`). No hand-typed results.
2. **Every reference must be verified** to exist: look it up by DOI/Crossref/publisher page/DBLP/Google Scholar, and copy authors, title, venue, year, pages, DOI from the real record. Items in Section 9 are *leads from memory* and may contain mistakes.
3. **Separate tuning data from evaluation data.** Tune parameters on tuning seeds; report results on different, untouched evaluation seeds. Give every competitor the same tuning budget.
4. **Write the hypotheses and analysis plan before the final runs** (`docs/PREREGISTRATION.md`), then freeze the code with a git tag (`v-final-experiments`). Anything done after seeing results is labelled "exploratory".
5. **Report negative and null results** (when a method does not win). Never hide them.
6. **Label every result by its evidence type:** *analytic*, *simulation*, or *hardware measurement*. Never mix them without saying so.
7. **State assumptions and limits** next to the claims they limit.
8. **Keep a changelog** (`docs/CHANGELOG.md`) and run the full test suite after every change.
9. **Disclose AI assistance** in the acknowledgments as IEEE policy requires (check the current wording). Keep a record of what the agent produced.
10. **Ask the human** (via `docs/HUMAN_TODO.md`) whenever a decision affects claims, cost, or authorship.

### MUST NOT
1. Do **not** fabricate data, hardware results, citations, quotations, DOIs, author names, or affiliations.
2. Do **not** claim "first", "novel", "optimal", or "superior" unless proven by a documented literature search or by the data with statistics. Use "to the best of our knowledge" only after the search in WP1.
3. Do **not** present simulated results as if they were measured on hardware.
4. Do **not** tune your proposed method harder than the competitors.
5. Do **not** pick the best seeds, drop bad runs, or change the design after seeing results. If a run is excluded, record why in `results/EXCLUSIONS.md` *before* looking at its effect.
6. Do **not** claim a "geometric advantage" from the 3D shape unless the data isolates it (see RQ2). Geometry gives adjacency; it gives no speed advantage when all links are equal.
7. Do **not** copy text from other papers. Paraphrase fully; cite. Keep similarity low. Never copy figures from other works.
8. Do **not** use marketing words (revolutionary, groundbreaking, state-of-the-art without a cited comparison, "significantly" without a statistical test).
9. Do **not** put "Platonic" or "geometry" in a claim the data does not support.
10. Do **not** leave author names invented. Use placeholders `[AUTHOR NAME]`, `[AFFILIATION]`.

---

## 2. STARTING MATERIAL AND ITS KNOWN WEAKNESSES

Existing package: `platonic-study/` (simulator `study/simulator.py`, 116 tests, 16,050 simulated runs, an IEEEtran manuscript). **Step 1 is an audit:** unzip, run the tests, rebuild the paper, and write `docs/AUDIT.md` listing, for each item below, whether it is true and how you will fix it. Keep the good parts (tests, paired seeds, bootstrap, replay verification, honest limitations).

| # | Weakness (why it is not top-tier yet) | Fix (work package) |
|---|---|---|
| W1 | Novelty is low; only ~5 references; missing the diffusion / dimension-exchange / topology-aware load-balancing literature | WP1 |
| W2 | Main findings are mostly null (push ≈ stealing; Platonic ≈ degree-matched random graph) and no new idea is offered | WP5 (new policy) + WP2 (theory that *explains* the null result) |
| W3 | Fully simulated; no real hardware; no calibration or validation | WP4, WP3 |
| W4 | All workers identical; links constant; zero scheduling CPU cost | WP3 |
| W5 | Only 4–20 workers; topology effects usually appear at larger scale | WP3 (scalable families) |
| W6 | Comparing solids mixes two effects: number of workers N and topology | WP2/WP6 (compare at equal N; use spectral metrics) |
| W7 | "Clustered" workload is artificial; no real task traces or real applications | WP6 |
| W8 | Cell-wise uncorrected confidence intervals; many comparisons | WP6 statistics plan |
| W9 | Competitor set misses classic self-scheduling variants (factoring, trapezoid), diffusion, lifeline, oracle LPT, real runtimes | WP5 |
| W10 | Title and framing over-sell "Platonic"; geometry has no performance role in the model | Section 3 reframing |
| W11 | Parameters were explored without a tuning/evaluation split | Rule 3 |

---

## 3. THE RESEARCH STORY (do not drift from this)

### 3.1 Title candidates (human picks one)
- "Does Topology Matter for Master-Centered Work Sharing? A Model, Simulation, and Prototype Study on Platonic-Solid Clusters"
- "Hub-Assisted Neighbor Work Sharing on Regular Polyhedral Cluster Topologies: Analysis, Simulation, and Hardware Validation"

### 3.2 One-sentence thesis
*On clusters whose workers sit at the vertices of a regular polyhedron with a hub (master) at the centre, how fast load rebalances is governed by a few graph properties (degree, diameter, spectral gap), and a policy that sends control information through the hub but moves data over peer edges performs competitively with or better than classic schedulers — validated on a physical prototype.*

(If the data later contradict part of this, rewrite the thesis to match the data. Never the other way round.)

### 3.3 Research questions
- **RQ1** How much does neighbor-based redistribution improve on static allocation, and when (task-cost variability, N, communication cost)?
- **RQ2** Does the Platonic arrangement itself help, or is performance explained by simple graph properties (degree, diameter, algebraic connectivity λ₂) at equal N and equal link count?
- **RQ3** Does a hub-assisted policy (control through master, data over edges) beat pure push, pure stealing, diffusion, and central queues?
- **RQ4** Do conclusions survive realistic effects: heterogeneous workers, scheduling CPU cost, shared NICs, stragglers, node failure, larger N?
- **RQ5** How close does the simulator come to the physical prototype (prediction error, same ranking of schedulers)?

### 3.4 Hypotheses (write the exact versions into PREREGISTRATION.md)
- **H1** Neighbor redistribution reduces makespan versus static allocation whenever task-cost variability is non-zero; no gain at zero variability.
- **H2** At equal N and equal peer-link count, topologies with larger λ₂ / smaller diameter rebalance faster; the Platonic graph is not better than a degree-matched rewired graph beyond what λ₂/diameter predict.
- **H3** Hub-assisted work sharing has lower or equal makespan versus pure push and pure stealing under high latency or high bandwidth cost, at modest extra master traffic.
- **H4** The advantage of redistribution grows with imbalance and shrinks with communication cost.
- **H5** The calibrated simulator predicts hardware makespan within a stated error (goal: mean absolute percentage error ≤ 5%) and preserves the ranking of schedulers (Kendall τ reported).

### 3.5 Contributions (final wording only after results; each must point to a figure or table)
- **C1** A formal model and a graph-metric analysis of master-centered polyhedral clusters.
- **C2** A hub-assisted work-sharing policy (or a clear negative result if it does not help).
- **C3** A controlled, statistically rigorous comparison against ≥ 10 competitors on simulated and real workloads.
- **C4** A physical prototype and a calibrated simulator validated against it.
- **C5** A complete open artifact (code, data, scripts, hardware runbook).

### 3.6 Claims allowed vs not allowed
- Allowed: "Under [conditions], policy X reduces mean makespan by a% (95% CI [lo, hi]) relative to Y."
- Not allowed: "Platonic solids are the best topology." "Our method outperforms all schedulers."

---

## 4. MASTER WORKFLOW (follow in order; each box is a gate)

```
+--------------------------------------------------------------------+
| STEP 0  AUDIT                                                      |
| Unzip platonic-study, run tests, rebuild paper.                    |
| Write docs/AUDIT.md (Section 2 table: true/false + fix plan).      |
| Create docs/HUMAN_TODO.md, docs/CHANGELOG.md, docs/JOURNAL_RULES.md|
+---------------------------------+----------------------------------+
                                  v
+--------------------------------------------------------------------+
| STEP 1  LITERATURE (WP1)                                           |
| Search the topics in Section 9. Verify every reference.            |
| Build refs.bib (>= 50 verified). Build the related-work table.     |
| Write "how we differ" for the 5 closest papers.                    |
| GATE: if someone already did the same thing, tell the human.       |
+---------------------------------+----------------------------------+
                                  v
+--------------------------------------------------------------------+
| STEP 2  THEORY + GRAPH METRICS (WP2)                               |
| Compute metrics for all graphs (Table T3). Check against known     |
| values in WP2. Write the analytic model and predictions H2.        |
+---------------------------------+----------------------------------+
                                  v
+--------------------------------------------------------------------+
| STEP 3  PREREGISTRATION (Rule 4)                                   |
| Write hypotheses, metrics, tests, seed split, exclusion rules.     |
| Human approves. Commit.                                            |
+---------------------------------+----------------------------------+
                                  v
+--------------------------------------------------------------------+
| STEP 4  SIMULATOR UPGRADE (WP3) + NEW POLICY (WP5)                 |
| Add heterogeneity, CPU overhead, scalable graphs, failures.        |
| Implement all competitors. Tests must stay green (add new tests). |
+---------------------------------+----------------------------------+
                                  v
+--------------------------------------------------------------------+
| STEP 5  HARDWARE (WP4)  -- HUMAN BUILDS, AGENT PREPARES            |
| Agent: BOM options, wiring plan, runbook, harness, data schema.    |
| Human: build, run micro-benchmarks, send raw logs.                 |
| Agent: calibrate simulator from logs. Validate (H5).               |
| GATE: validation error acceptable? If not, fix model, not data.    |
+---------------------------------+----------------------------------+
                                  v
+--------------------------------------------------------------------+
| STEP 6  TUNING (tuning seeds only), then FREEZE (git tag)          |
+---------------------------------+----------------------------------+
                                  v
+--------------------------------------------------------------------+
| STEP 7  FINAL EXPERIMENTS (WP6) on evaluation seeds + hardware     |
| Run everything in the preregistered matrix. No peeking-and-editing.|
+---------------------------------+----------------------------------+
                                  v
+--------------------------------------------------------------------+
| STEP 8  ANALYSIS + FIGURES + TABLES (WP7)                          |
| Auto-generate all. Statistics per Section 6.6.                     |
+---------------------------------+----------------------------------+
                                  v
+--------------------------------------------------------------------+
| STEP 9  WRITE THE PAPER (Section 10 template)                      |
| Rewrite thesis/claims to match what the data show.                 |
+---------------------------------+----------------------------------+
                                  v
+--------------------------------------------------------------------+
| STEP 10  QUALITY GATES + ARTIFACT (Section 13 checklist)           |
| Zero LaTeX warnings, all refs verified, reproduce-from-scratch OK. |
+---------------------------------+----------------------------------+
                                  v
+--------------------------------------------------------------------+
| STEP 11  SUBMISSION PACKAGE (Section 12) -> hand to human          |
+--------------------------------------------------------------------+
```

---

## 5. WORK PACKAGES

### WP1 — Literature review and positioning
**Do**
1. Search (Google Scholar, DBLP, IEEE Xplore, ACM DL, arXiv, Semantic Scholar, Crossref) for each topic in Section 9.1. Record queries and dates in `docs/LIT_SEARCH_LOG.md`.
2. Read abstracts and key sections; for the closest 10 papers read fully.
3. Build `refs.bib` with ≥ 50 verified entries (target 50–70; at least 25% from the last 7 years; mix of journals and top conferences).
4. Build **Table T2** (related-work matrix): rows = papers, columns = topology considered, hub/master, heterogeneous nodes, real hardware, policies compared, statistics rigor, open artifact.
5. For the 5 closest papers, write 3–5 sentences each on "what they did / what we do differently".
6. Explicitly check prior art on **physical polyhedral clusters**, including patent US20210004344A1 (cuboctahedron cluster with a central hub node; verify the claims text). Cite it; state clearly how this work differs (Platonic solids, scheduling-focused, controlled comparison).
**Do not** cite papers you have not opened. Do not cite predatory-journal papers unless they are the only source; mark them as weak.
**Output:** `refs.bib`, `docs/LIT_SEARCH_LOG.md`, `docs/RELATED_WORK_NOTES.md`, T2.

### WP2 — Graph metrics and analytic model
**Compute for every graph** (worker graph alone, and worker graph + master hub): vertices, edges, degree (min/max/mean), diameter, mean shortest-path length, bisection width (exact for small graphs, heuristic with stated method for large), edge connectivity, **algebraic connectivity λ₂** (second-smallest Laplacian eigenvalue; "how well-connected the graph is for spreading load"), spectral gap of the diffusion matrix, condition number, expansion.
**Sanity checks (agent must reproduce; these are known results):** λ₂ of the worker graph — tetrahedron 4; octahedron 4; cube 2; icosahedron 5−√5 ≈ 2.764; dodecahedron 3−√5 ≈ 0.764. If your code disagrees, find the bug before continuing.
**Graph families to include (all with the same master-hub construction):**
- Platonic: tetrahedron (N=4), octahedron (6), cube (8), icosahedron (12), dodecahedron (20).
- Platonic-derived, to reach larger N: geodesic subdivisions of the icosahedron (N = 10f²+2 → 42, 92, 162 for frequency 2, 3, 4). Clearly label as "Platonic-derived".
- Controls: degree-matched random rewiring (many random graphs per solid, not one), random regular graphs, ring, 2D grid/torus, hypercube (N = 8, 16, 32…), star (no peer edges), complete graph.
**Analytic model (required):**
1. Define the load-sharing process as a diffusion on the peer graph. Derive/cite the convergence rate in terms of λ₂ and the diffusion parameter (Cybenko 1989; Boillat 1990; Hu & Blake 1999). Predict a *balancing time* for each graph.
2. Give a simple makespan model: T ≈ initial transfer + max(work/N, longest task) + rebalancing penalty + result return. State assumptions.
3. State predictions as testable form: "balancing time ∝ log(imbalance)/λ₂".
4. Include proofs only if complete and correct. Otherwise label as "model" or "heuristic", and put derivations in the appendix.
**Must separate the effects of N and topology:** compare topologies at equal N; compare sizes within a family using the model.
**Output:** `analysis/graph_metrics.py`, Table T3, `docs/MODEL.md`.

### WP3 — Simulator upgrade
Keep the verified core. Add, each with unit tests and an on/off switch:
1. **Heterogeneous worker speeds** (e.g., speeds from measured distributions; slow/fast mixes; time-varying slowdown).
2. **Scheduling CPU cost** per message and per decision at workers and master (calibrated in WP4).
3. **Measured latency/bandwidth distributions** instead of constants (sample from measured traces).
4. **Shared-NIC and switch models** matching the prototype wiring (WP4 Option B).
5. **Master capacity model** (service rate, queueing) for larger N.
6. **Failures and stragglers:** worker slowdown by factor k; worker crash at time t; master re-queues timed-out tasks; result de-duplication by task ID. Report the effect on makespan and correctness (every ID exactly once in the final result set).
7. **Scalable graphs** (WP2 families) up to N ≈ 162 (and up to ~1000 for a scaling-only appendix, if run time allows).
8. **Dynamic task spawning** (stretch; for tree-search style workloads).
9. **Determinism and speed:** fixed RNG streams per component so adding a feature does not change old results; profile and parallelize across cases only.
10. **Cross-check:** reproduce a small scenario in an independent tool (ns-3 or SimGrid) and compare. Document differences.
**Keep** the invariants: every task executes once; every result reaches the master; T ≥ compute lower bound; ownership audit after each event in test mode.
**Output:** upgraded `study/`, new tests (target ≥ 200 total), `docs/SIMULATOR_SPEC.md` (full description of the model so a reviewer can re-implement it).

### WP4 — Physical prototype (human builds; agent prepares)
**Why:** a top journal will ask for real measurements. A simulator alone is the single biggest weakness.
**What "Platonic cluster in space" means for evidence (be precise in the paper):** the 3D frame gives a *wiring pattern* (which node connects to which) and a *packaging* (cable length, airflow, modularity). It does not change speed unless link properties differ. Say this plainly. Optionally measure cable length, temperature, and power per layout.
**Agent produces** `hardware/` with:
1. **Bill of materials with at least 2 options** (costs verified by web search on the day; mark date):
   - *Option A — real peer links:* every worker needs (peer degree + 1 master link) network ports: tetrahedron 4, cube 4, dodecahedron 4, octahedron 5, icosahedron 6. The master needs one port per worker (4 to 20), so use a switch or a multi-port card on the master. Use multi-port boards or USB/PCIe Ethernet adapters. Warning: USB adapters share a bus and add noise — measure it.
   - *Option B — VLAN-emulated topology:* one managed gigabit switch; each logical edge is a separate VLAN between two nodes; each node uses VLAN sub-interfaces on one physical port. Cheap and rewireable (controls = change config). Limitation to state in the paper: each node's single physical port is **shared** between all its edges (the shared-NIC model in the simulator), so results are for that contention regime.
   - Recommended minimum: tetrahedron, octahedron and cube prototypes with the same boards; extend to icosahedron (12) and dodecahedron (20) if budget allows (Option B).
2. **Wiring plans** (edge lists, port maps, VLAN IDs) generated from the same `geometry.py` that the simulator uses (single source of truth).
3. **Frame design notes** (3D-printed/laser-cut/aluminium-extrusion polyhedron; vertex mounts; cable lengths); optional.
4. **OS/software setup script** (identical images; fixed CPU governor; disable power saving; pin cores; chrony or PTP time sync; record kernel/software versions).
5. **Micro-benchmark suite** (so the simulator can be calibrated with real numbers):
   - link latency distribution per edge (≥ 10,000 pings or application-level round trips); bandwidth per edge (iperf3) **and all edges simultaneously**; message size sweep (32 B … 1 MiB);
   - per-message CPU cost (send/receive, serialization);
   - task compute time distribution on each node (identify slow nodes; thermal throttling);
   - effect of simultaneous traffic on several links of the same node.
6. **Macro-benchmark harness:** the same scheduler code logic as the simulator (same state machine, same message types) implemented in Python (asyncio/ZeroMQ) or C++/MPI. The agent writes it, tests it on one laptop with emulated nodes, then the human runs it on hardware.
7. **Runbook** (`hardware/RUNBOOK.md`) with exact commands, expected outputs, randomized run order, warm-up runs (discarded), rest periods between runs, temperature/power logging, and a data format (`hardware/DATA_SCHEMA.md`, one CSV row per run + one JSON event log per run).
8. **Fault-injection scripts** (CPU throttling with `stress-ng`/`cpulimit`, `tc netem` for latency/loss/bandwidth, kill -9 a worker).
9. **Energy measurement** plan (inline USB/DC power meter; joules per task).
**Run counts on hardware:** ≥ 20 repetitions per configuration (more if variance is high), randomized order; report all runs.
**Do not** simulate hardware results to fill gaps. If hardware is unavailable for some configuration, say "simulation only" in the paper.
**Calibration → validation:** calibrate on a calibration subset of configurations; validate on held-out configurations. Report MAPE, max error, Bland–Altman or parity plot, and Kendall τ for scheduler rankings (**H5**).

### WP5 — Schedulers (competitors and the proposed policy)
**Interface:** all schedulers use the same simulator hooks and cannot see true task costs (except the oracle). Document each as pseudocode + parameters + complexity + message cost.

**Proposed policy candidates (evaluate honestly; keep what the data support):**
- **P-A Hub-assisted work sharing ("control through the hub, data over edges"):** workers send small, rate-limited load summaries to the master (they already talk to it); the master tells idle workers which neighbor is most loaded (or tells busy workers which neighbor is idle); donated tasks move over peer edges, not through the master. Design the update rate and staleness handling explicitly.
- **P-B Topology-aware donation fraction:** donation fraction f as a function of degree and λ₂ (e.g., f ≈ 1/(deg+1) for diffusion-like behavior).
- **P-C Speed-aware donation (heterogeneous nodes):** donate in proportion to estimated speeds (measured online from completed tasks).
- Combine only if each part is shown useful by an ablation.

**Competitors — MUST include:**
1. Static equal partition (reference).
2. Static LPT with clairvoyant (true) costs — **oracle reference**, labelled unrealistic.
3. Central dynamic self-scheduling, chunk = 1 (SS).
4. Guided self-scheduling (GSS; Polychronopoulos & Kuck).
5. Factoring (FAC2; Hummel et al.) — and weighted factoring when speeds differ.
6. Trapezoid self-scheduling (TSS; Tzen & Ni).
7. Randomized global work stealing (steal-one and steal-half variants).
8. Neighbor work stealing (existing).
9. Neighbor push / work sharing (existing "proposed" baseline).
10. Diffusion load balancing (first-order scheme with optimal parameter from λ₂ and λₙ; Cybenko; Hu & Blake).
11. Master rebalance (existing).
12. At least **one real runtime** executed on the prototype: Dask distributed, Ray, or MPI dynamic master–worker. Justify the choice; configure fairly.
**SHOULD include:** dimension-exchange (where the graph allows), power-of-two-choices probing (Mitzenmacher), lifeline-based global load balancing (Saraswat et al.), fixed-chunk self-scheduling with tuned chunk size, Min-min/Sufferage for heterogeneous independent tasks (Braun et al.).
**Fairness rules:** same hardware model, same link resources, same message-size accounting, same tuning budget (e.g., 30 tuning seeds × a small grid per competitor), same task instances (paired seeds), same stopping rule (last result received at master).

### WP6 — Benchmarks and experiment matrix
See Section 6 for details. Summary of experiment groups:
- **E1 Primary comparison** (all policies × all Platonic solids × all workloads), evaluation seeds.
- **E2 Topology controls** (equal N: Platonic vs ≥ 20 random degree-matched rewirings vs ring/grid/torus/hypercube/random-regular/star/complete).
- **E3 Scaling** (strong scaling: fixed total work; weak scaling: work ∝ N) with geodesic and hypercube/torus families up to N ≈ 162.
- **E4 Communication sensitivity** (latency × bandwidth grid; shared NIC; master service cost).
- **E5 Heterogeneity** (speed mixes; time-varying slowdown; stragglers).
- **E6 Faults** (crash one/several workers; recovery time; correctness check).
- **E7 Ablations** (remove each component of the proposed policy).
- **E8 Hardware macro-benchmarks** (prototype: topologies built; subset of policies and workloads; same configs also run in the calibrated simulator for H5).
- **E9 Energy and thermal** (prototype).

### WP7 — Analysis, figures, tables
Section 7 (figures), Section 8 (tables), Section 6.6 (statistics). Everything auto-generated by `analysis/make_all.py`; running it from a clean checkout must recreate every figure/table/number.

### WP8 — Artifact and reproducibility
1. Git repository, tagged releases, `README`, one-command reproduction (`make all` or equivalent), pinned dependencies, Dockerfile.
2. Archive on Zenodo (DOI) after submission readiness; check the journal's supplementary-material and data policies (and IEEE DataPort/Code Ocean options).
3. Include raw data (simulation and hardware), scripts, hardware runbook, wiring files, environment fingerprints.
4. Run the "fresh clone" test: new machine/container → reproduce main figures. Log the result.

### WP9 — Writing
Follow Section 10 exactly. Write after the results are frozen. Make the paper match the data.

### WP10 — Submission package
Section 12.

---

## 6. BENCHMARKS, WORKLOADS, METRICS, STATISTICS

### 6.1 Workloads (tasks are independent unless stated)
Normalize total work per instance so policies are comparable; keep task IDs, sizes, and costs identical across policies within a seed (paired design).

**Synthetic (controlled variability)**
| ID | Name | Definition | Purpose |
|---|---|---|---|
| S1 | Constant | all costs equal | no-gain control |
| S2 | Exponential | unit-mean exponential | mild variability |
| S3 | Lognormal (CV = 2) | independent draws | neutral heterogeneity |
| S4 | Capped Pareto | heavy tail, capped | long-task effect |
| S5 | Clustered | lognormal sorted by cost before chunking | worst-case imbalance for static; label as stress test |
| S6 | Bimodal | 90% short / 10% long | realistic mixes |
| S7 | Variability sweep | lognormal with CV ∈ {0, 0.25, 0.5, 1, 2, 4} | dose–response for H1/H4 |

**Real tasks on the prototype (and measured cost distributions fed to the simulator)**
| ID | Application | Why |
|---|---|---|
| R1 | Mandelbrot / ray-tracing tiles | naturally irregular cost, easy to verify |
| R2 | Monte Carlo (e.g., option pricing or π with variable sample counts) | embarrassingly parallel |
| R3 | Matrix-tile multiplication or image-filter tiles | regular compute, data movement |
| R4 | Small ML inference batches (variable input size) | modern workload, optional |
| R5 | Unbalanced Tree Search (UTS) | standard irregular benchmark; needs dynamic spawn (stretch) |

**Trace-driven (simulation):** task-duration distributions from public traces (Google cluster-data traces; Parallel Workloads Archive / Grid Workloads Archive). Document filtering, sampling and scaling. Cite the trace papers. If the license or format blocks use, say so and skip.

### 6.2 Parameters and grids
- Task data size: 1 KiB, 4 KiB (baseline), 64 KiB, 1 MiB. Result size 64 B baseline (also 4 KiB). Control message 32 B.
- Link latency: 10 µs (baseline), 100 µs, 1 ms, 10 ms. Bandwidth: 10 MiB/s, 100 MiB/s (baseline), 1 GiB/s. Use *measured* values from WP4 for the "calibrated" configuration.
- Tasks per worker (granularity): 10, 50, 300 (baseline-like), 1000.
- N: all Platonic sizes plus scaling families up to ~162.
- Seeds: ≥ 30 evaluation seeds per simulated cell (≥ 100 for key cells); separate tuning seeds (≥ 30); hardware: ≥ 20 repetitions per configuration.
- Always say which results use which seeds.

### 6.3 Metrics (plain word first, technical term in brackets)
**Primary**
- **Total job time** (*makespan*, T): time until the master receives the last result. Report mean, median, 95% CI, and paired ratio versus a reference.
- **Speedup over static** (*S = T_static / T_policy*, paired mean ratio, not ratio of means).
- **Efficiency** (*parallel efficiency* = total work / (N × T)).
- **Gap to ideal** (*T / T_LB*, where T_LB = max(total work/N, longest task)); and gap to the clairvoyant oracle.

**Load balance**
- **How uneven the work was** (*load imbalance* = max busy time / mean busy time − 1; and the coefficient of variation of busy times).
- **Fairness** (*Jain's index* of busy times).
- **Idle time** (total and per worker; time to first idle; *idle-before-finish*).
- **Time to rebalance** (*balancing time*: time from first imbalance until max/min queue ratio < threshold).

**Cost of balancing**
- Number of messages (control/data/result), bytes moved, **migrations per task**, master messages per second and master CPU utilization, per-link utilization (max/mean), queueing delay at links.
- **Scheduling overhead** (fraction of time spent on non-task work).
- **Tail** (*p95/p99 of result return delay*).

**Robustness and resources**
- Slowdown under a straggler or crash; recovery time; correctness (all IDs once).
- Energy per task (J) and power (W); peak temperature (hardware).
- Variance across seeds (IQR) — a policy with the same mean but huge variance must be reported as such.

**Model quality (H5)**
- MAPE, RMSE, max error between simulator and hardware; Kendall τ and Spearman ρ of scheduler rankings; parity plot.

### 6.4 Experiment matrix (preregister the sizes)
E1 Primary: 5 solids × 5–7 workloads × ≥ 11 policies × 30 seeds.
E2 Topology: for each N in {6, 8, 12, 20} × workloads {S3, S4, S5, R*} × ≥ 20 rewired graphs × 2–3 policies × 30 seeds.
E3 Scaling: families × N × 3 policies × 30 seeds.
E4–E7 as in WP6. E8–E9 hardware.
Write exact counts in the paper (like "n = X runs").

### 6.5 Fairness and validity checklist for the comparison
- Same tuning budget; same information (no policy sees true costs except oracle).
- No policy gets a free direct link that others cannot use.
- Initial allocation differences (queue-based vs equal chunks) stated clearly, and a variant of each with the other allocation tested.
- The reporting unit for each claim is one preregistered primary comparison; all else is exploratory.
- Threats to validity discussed: synthetic vs real workloads; small-N; one hardware family; shared NIC; unmodeled OS effects.

### 6.6 Statistics plan
1. Use **paired** comparisons (same seed → same instance).
2. For each primary comparison report: mean paired ratio, bootstrap 95% CI (≥ 10,000 resamples, percentile or BCa), and an effect size (e.g., Cliff's delta or Cohen's d_z).
3. For multi-policy comparisons across many cells use **Friedman test + Nemenyi post-hoc and a critical-difference diagram** (Demšar 2006), or pairwise Wilcoxon signed-rank with **Holm correction**.
4. Control the false-discovery rate across the preregistered family; report adjusted p-values and CIs.
5. Check assumptions (normality of differences, outliers); use non-parametric when violated.
6. Report variance and distributions (violin/box plots), not only means.
7. Hardware: follow rigorous benchmarking practice (Hoefler & Belli 2015; Kalibera & Jones 2013): report all runs, discard warm-up, state the confidence level, avoid reporting only the best run.
8. For "no difference" claims use equivalence testing (TOST) with a stated margin (e.g., ±1%) instead of "not significant".
9. Do not call a difference "significant" unless the test says so; do not overinterpret a lowest mean.
10. Model fit (H2): regress balancing time on λ₂/diameter/degree with N held fixed; report R², CIs, and a held-out check.

---

## 7. FIGURES (required list; vector PDF, auto-generated)

Rules for every figure: readable at print size (fonts ≥ 8 pt), colorblind-safe palette plus different line styles/markers, axis labels with units, error bars defined in the caption, self-contained caption (what, how many seeds/runs, what to notice), width 3.5 in (one column) or 7.16 in (two columns), consistent policy colors across all figures, referenced in the text, no chart junk, no 3D bar charts.

| Fig | Content | Section |
|---|---|---|
| F1 | Concept: master at centre, workers at vertices (photo of prototype + diagram) | I / VI |
| F2 | The five Platonic worker graphs + master spokes, with N, degree labels | IV |
| F3 | Protocol message sequence diagram (push, accept/reject, hub hints, result) | V |
| F4 | Worker state machine (idle / busy / reserved / receiving) | V |
| F5 | Prototype architecture and wiring (Option A/B), software stack | VI |
| F6 | Simulator vs hardware parity plot (and error histogram) | VIII-A |
| F7 | Main result: makespan (or speedup over static) with 95% CI, all policies, per workload (small multiples) | VIII-B |
| F8 | Critical-difference diagram of policy ranks | VIII-B |
| F9 | Variability dose–response: speedup vs task-cost CV, per policy | VIII-B |
| F10 | Execution timeline (Gantt) per worker: static vs best policy, one run | VIII-B |
| F11 | Topology effect: speedup/balancing time vs λ₂ (and diameter) at equal N, with fitted model | VIII-C |
| F12 | Platonic vs degree-matched random rewirings (distribution of ratios, ≥ 20 graphs) | VIII-C |
| F13 | Scaling: strong and weak scaling curves, ideal line, per family | VIII-D |
| F14 | Overheads: messages, bytes, migrations, master load (stacked bars) | VIII-E |
| F15 | Communication sensitivity heatmap (latency × bandwidth) showing which policy wins | VIII-E |
| F16 | Heterogeneity / straggler effect | VIII-F |
| F17 | Fault injection: makespan and recovery time | VIII-F |
| F18 | Ablation of the proposed policy | VIII-G |
| F19 | Energy per task and temperature (hardware) | VIII-H |

(If space is tight, move F10, F15, F17–F19 to a supplement; keep F1–F3, F6–F9, F11–F14.)

---

## 8. TABLES (required list; auto-generated with `booktabs`)

Rules: no vertical lines; units in headers; best value in bold *only* when supported by the preregistered test; footnote explains abbreviations; ≤ 3 significant digits unless needed.

| Table | Content |
|---|---|
| T1 | Notation (symbols, meaning, units) |
| T2 | Related-work comparison matrix (WP1) |
| T3 | Graph properties: N, edges, degree, diameter, mean path, bisection, λ₂, spectral gap — Platonic, derived, and control graphs |
| T4 | Hardware and software specification of the prototype (boards, NICs, switch, OS, kernel, language, versions) |
| T5 | Measured link/CPU/task parameters used for calibration (mean, std, p99) |
| T6 | Workload definitions (synthetic parameters and real applications) |
| T7 | Scheduler definitions: information used, messages, parameters, tuned values, complexity |
| T8 | Main results with 95% CI (per workload; separate columns for simulation and hardware) |
| T9 | Statistical test results (Friedman/Nemenyi or Holm-adjusted Wilcoxon; effect sizes) |
| T10 | Validation error (MAPE, RMSE, τ) by configuration |
| T11 | Overhead summary (messages, bytes, migrations, master utilization) |
| T12 | Experiment inventory: number of runs per experiment group, seeds, split |

---

## 9. REFERENCES

### 9.1 Topics to search (for WP1)
1. Load sharing vs load balancing; sender- vs receiver-initiated policies.
2. Work stealing (theory and practice); steal-half; hierarchical and topology-aware stealing; lifeline-based balancing.
3. Diffusion and dimension-exchange load balancing on graphs; spectral analysis (λ₂).
4. Topology effects on dynamic load balancing (hypercube, mesh, torus, ring, tree, Fibonacci cube).
5. Loop/task self-scheduling (SS, CSS, GSS, FAC, TSS, AWF).
6. Independent-task mapping on heterogeneous systems (Min-min, Max-min, Sufferage).
7. Interconnection networks and graph properties (diameter, bisection, expansion); regular and symmetric graphs; polyhedral/geodesic networks.
8. Physical cluster designs of unusual shape (polyhedral clusters, patents), single-board-computer clusters (Raspberry Pi etc.), edge/fog clusters, offline/"air-gapped" clusters.
9. Simulation of distributed systems (SimGrid, ns-3, CloudSim) and simulator validation.
10. Rigorous performance benchmarking and statistics (Hoefler & Belli; Kalibera & Jones; Demšar).
11. Fault tolerance and stragglers (MapReduce re-execution, speculative execution, LATE).
12. Energy-aware scheduling on small clusters (optional).
13. Public workload traces.

### 9.2 Leads from memory — **every item must be verified and its metadata corrected; drop any that cannot be verified**
- D. L. Eager, E. D. Lazowska, J. Zahorjan, "Adaptive load sharing in homogeneous distributed systems," IEEE Trans. Software Eng., 1986.
- R. D. Blumofe, C. E. Leiserson, "Scheduling multithreaded computations by work stealing," J. ACM, 1999.
- G. Cybenko, "Dynamic load balancing for distributed memory multiprocessors," J. Parallel Distrib. Comput., vol. 7, 1989.
- J. E. Boillat, "Load balancing and Poisson equation in a graph," Concurrency: Practice and Experience, 1990.
- S. Ghosh, S. Muthukrishnan, "Dynamic load balancing by random matchings," J. Comput. Syst. Sci., 1996.
- Y. F. Hu, R. J. Blake, "An improved diffusion algorithm for dynamic load balancing," Parallel Computing, vol. 25, 1999.
- C. Z. Xu, F. C. M. Lau, *Load Balancing in Parallel Computers: Theory and Practice*, Kluwer, 1997.
- M. Willebeek-LeMair, A. P. Reeves, "Strategies for dynamic load balancing on highly parallel computers," IEEE TPDS, 1993.
- P. K. K. Loh, W. J. Hsu, C. Wentong, N. Sriskanthan, "How network topology affects dynamic load balancing," IEEE Parallel & Distributed Technology, vol. 4, no. 3, 1996.
- L. Rudolph, M. Slivkin-Allalouf, E. Upfal, "A simple load balancing scheme for task allocation in parallel machines," SPAA, 1991.
- C. D. Polychronopoulos, D. J. Kuck, "Guided self-scheduling," IEEE Trans. Computers, 1987.
- S. F. Hummel, E. Schonberg, L. E. Flynn, "Factoring: a method for scheduling parallel loops," Commun. ACM, 1992.
- T. H. Tzen, L. M. Ni, "Trapezoid self-scheduling," IEEE TPDS, 1993.
- J. Dinan et al., "Scalable work stealing," SC, 2009.
- V. A. Saraswat et al., "Lifeline-based global load balancing," PPoPP, 2011.
- D. Hendler, N. Shavit, "Non-blocking steal-half work queues," PODC, 2002.
- M. Mitzenmacher, "The power of two choices in randomized load balancing," IEEE TPDS, 2001.
- S. Olivier et al., "UTS: an unbalanced tree search benchmark," LCPC, 2006.
- T. D. Braun et al., "A comparison of eleven static heuristics for mapping a class of independent tasks onto heterogeneous distributed computing systems," J. Parallel Distrib. Comput., 2001.
- R. L. Graham, "Bounds on multiprocessing timing anomalies," SIAM J. Appl. Math., 1969.
- M. Fiedler, "Algebraic connectivity of graphs," Czechoslovak Math. J., 1973.
- F. R. K. Chung, *Spectral Graph Theory*, AMS, 1997.
- W. J. Dally, B. Towles, *Principles and Practices of Interconnection Networks*, Morgan Kaufmann, 2004.
- F. T. Leighton, *Introduction to Parallel Algorithms and Architectures*, Morgan Kaufmann, 1992.
- H. S. M. Coxeter, *Regular Polytopes*, Dover (any edition).
- T. Hoefler, R. Belli, "Scientific benchmarking of parallel computing systems," SC, 2015.
- T. Kalibera, R. Jones, "Rigorous benchmarking in reasonable time," ISMM, 2013.
- J. Demšar, "Statistical comparisons of classifiers over multiple data sets," J. Mach. Learn. Res., 2006.
- S. Holm, "A simple sequentially rejective multiple test procedure," Scand. J. Statist., 1979.
- H. Casanova et al., "Versatile, scalable, and accurate simulation of distributed applications and platforms" (SimGrid), J. Parallel Distrib. Comput., 2014.
- G. F. Riley, T. R. Henderson, "The ns-3 network simulator," in *Modeling and Tools for Network Simulation*, Springer, 2010.
- J. Dean, S. Ghemawat, "MapReduce: simplified data processing on large clusters," OSDI, 2004.
- M. Zaharia et al., "Improving MapReduce performance in heterogeneous environments" (LATE), OSDI, 2008.
- C. Reiss et al., "Heterogeneity and dynamicity of clouds at scale: Google trace analysis," SoCC, 2012.
- P. Moritz et al., "Ray: a distributed framework for emerging AI applications," OSDI, 2018.
- M. Frigo, C. E. Leiserson, K. H. Randall, "The implementation of the Cilk-5 multithreaded language," PLDI, 1998.
- Patent US20210004344A1, "Modular Polyhedral Computer Architectures and Network Optimization Algorithms" (verify inventor, date, claims).
- Raspberry-Pi cluster performance papers (e.g., the arXiv paper "Performance of a Simple 32 Core Raspberry Pi Cluster", arXiv:1708.05264 — verify authors) and similar single-board-cluster studies.

### 9.3 Reference-quality rules
- IEEE style via `IEEEtran.bst`; include DOI where available; consistent abbreviations.
- Cite primary sources for methods you implement; cite surveys only for background.
- Check the existence and the *claim you attribute to it* (read the paper).
- No reference list padding. Every entry cited in the text; every citation in the list.
- Include recent (last ~5–7 years) relevant works; avoid self-citation bloat.
- Run a final script: every `\cite` resolves; no "?" in the PDF; no duplicate keys.

---

## 10. THE PAPER: COMPLETE IEEE JOURNAL TEMPLATE (what to write in each section and how)

**Format:** `\documentclass[journal]{IEEEtran}`, two columns, 10 pt. Target length: the journal's limit (typically about 12–14 pages for regular papers — verify in JOURNAL_RULES.md). Put extra material in an appendix or a supplement. Title page: placeholders for authors/affiliations.

### 10.0 Writing style rules (apply everywhere)
1. Plain, exact sentences. One idea per sentence. Prefer active voice ("We measure…").
2. Define every symbol at first use and again in T1. Never reuse a symbol for two things.
3. Every claim is backed by a citation, a figure/table, or a derivation — and the text says which.
4. Numbers: value, unit, and uncertainty (e.g., "216.2 ms, 95% CI [214.9, 217.5]"). Say how many runs.
5. Calibrated language: "suggests" for exploratory results, "shows" only with a test, "is consistent with" for null results.
6. Avoid: "novel" (unless proven), "state-of-the-art" (unless compared), "obviously", "very", "significantly" (unless tested), "we believe".
7. Each figure/table is introduced in the text *before* it appears and interpreted ("Fig. 7 shows… the key observation is…").
8. Paragraph pattern: claim → evidence → implication.
9. Keep terminology fixed: choose one word each for *makespan*, *worker*, *master/hub*, *peer link*, *spoke*, *task*, *policy*.
10. Technical term + short plain explanation at first use where a reader outside the subfield may stumble.
11. No text copied from other sources; no figure copied without permission.
12. After drafting, run a language check (grammar and consistency), then read the paper aloud once.

### 10.1 Title
Specific, informative, ≤ 20 words, no abbreviations or hype. Includes the system ("master-centered polyhedral clusters"), the topic ("work sharing / scheduling"), and the evidence type ("analysis, simulation, and prototype validation").

### 10.2 Abstract (150–250 words, a single paragraph, no citations, no undefined symbols)
Structure (1–2 sentences each):
1. **Context/problem:** why load balancing on small hub-and-spoke clusters matters.
2. **Gap:** what is unknown (does topology matter? how do policies compare under measured costs?).
3. **Approach:** model + policy + simulator + prototype, N workers, competitors, workloads, runs.
4. **Main results with numbers:** e.g., speedups and CIs, topology finding, validation error.
5. **Implication/limits:** when it helps, when it does not.
6. **Artifact:** code and data availability (one clause).

### 10.3 Index Terms (4–8)
Distributed scheduling, load balancing, work sharing, work stealing, network topology, spectral graph theory, discrete-event simulation, cluster computing, single-board computers.

### 10.4 I. Introduction (≈ 1–1.25 pages)
Paragraph plan:
1. **Context:** clusters of modest nodes (edge, lab, classroom, offline, embedded) and why task-cost imbalance wastes capacity; give one concrete example.
2. **Existing approaches and their limits:** central queues, work stealing, diffusion; they are studied mostly on abstract or hypercube-like topologies and without a hub.
3. **Gap and question:** state RQ1–RQ5 briefly. State what is unknown.
4. **Approach:** one paragraph on the system (master at centre, workers at vertices), the policy, the evaluation (simulation + prototype).
5. **Contributions:** 4–5 bullets, each verifiable (with section/figure pointers). No overclaiming.
6. **Roadmap:** one sentence per section group.
Include Fig. F1 near the first page. Do not put results tables in the introduction; one headline number is fine.

### 10.5 II. Background and Related Work (≈ 1–1.5 pages)
Organize by themes (subsections A–E), not by author list:
A. Dynamic load balancing and load sharing; B. Work stealing; C. Diffusion and topology-aware balancing (incl. spectral results); D. Self-scheduling and independent-task mapping; E. Physical and small-cluster architectures (polyhedral clusters, single-board computers, patent prior art).
End with a **positioning paragraph + T2**: "Unlike [x], which…, we…". Be fair to prior work; state what was already known (this paper does not claim to invent work sharing or stealing).

### 10.6 III. Problem Statement and System Model (≈ 1 page)
- **A. Platform:** graph G=(V,E), hub m, spokes, link parameters (latency L, bandwidth B), node speeds s_i, routing rule for non-adjacent nodes.
- **B. Workload:** M independent tasks, cost c_i (unknown to schedulers), data size, result size; normalization.
- **C. Execution/communication model:** nonpreemptive, FIFO links (the serialization equation), message costs, CPU overheads, failures (if modeled).
- **D. Objective and metrics:** minimize makespan T; define T_LB, efficiency, imbalance.
- **E. Assumptions list** (numbered; each is revisited in the Limitations section).
T1 (notation) goes here.

### 10.7 IV. Polyhedral Cluster Topologies (≈ 1 page)
- Construction of the five solids and derived graphs (coordinates → minimum-distance edges; geodesic subdivision rule); wiring rule for the hub.
- **T3** (graph metrics) and **F2**.
- What the metrics predict (from WP2): predicted ordering of balancing times; state predictions *before* the results section, linked to H2.
- One honest paragraph: geometry gives adjacency and packaging; it gives no speed advantage when links are equal.

### 10.8 V. Scheduling Policies (≈ 1.5 pages)
- **A. Proposed policy:** purpose; state variables; messages (F3, F4); handshake and race handling; staleness of hub hints; pseudocode (Algorithm 1: worker side; Algorithm 2: hub side).
- **B. Correctness:** exactly-once execution/collection argument; termination; deadlock/livelock freedom (argue carefully; test evidence is separate).
- **C. Complexity:** messages per migration, state per node, master load as a function of N.
- **D. Baselines:** brief description of each competitor (details in T7). Cite sources. State changes you made to adapt them to this platform.

### 10.9 VI. Implementation and Prototype (≈ 1–1.25 pages)
- **A. Simulator:** event model, determinism, invariants, tests (count), cross-check with ns-3/SimGrid.
- **B. Prototype:** hardware (T4, F5), wiring option(s), software stack, time/clock handling, how the same policy code runs in both.
- **C. Calibration:** what was measured (T5), how parameters were fitted, the calibration/validation split.

### 10.10 VII. Experimental Methodology (≈ 1.25 pages)
- A. Research questions and hypotheses (reference PREREGISTRATION.md; say which tests were preregistered).
- B. Workloads (T6), C. Competitors and tuning protocol (T7), D. Metrics (list from 6.3), E. Experimental protocol (seeds, repetitions, randomization, warm-up, exclusions), F. Statistical analysis (6.6), G. Run inventory (T12).
- Include a "Threats to validity" preview sentence pointing to Section IX.

### 10.11 VIII. Results (≈ 3–4 pages) — organize by research question, not by figure
Each subsection: **question → result with numbers → interpretation → caveat.**
- **A. Simulator validation (RQ5, H5):** F6, T10.
- **B. Main comparison (RQ1, RQ3):** F7, F8, F9, T8, T9. State exactly which differences are statistically supported.
- **C. Does topology matter? (RQ2, H2):** F11, F12. Report model fit and the Platonic-versus-rewired comparison, including null results with equivalence tests.
- **D. Scaling:** F13.
- **E. Communication, overhead, master load:** F14, F15, T11.
- **F. Heterogeneity, stragglers, faults (RQ4):** F16, F17.
- **G. Ablation of the proposed policy:** F18.
- **H. Energy/thermal (hardware):** F19 (optional).
Write findings as numbered "Observation 1…n" sentences at the end of each subsection. Keep tuning-set results out of this section.

### 10.12 IX. Discussion (≈ 0.75 page)
- Summary answers to RQ1–RQ5 (one sentence each).
- **Practical guidance:** a short decision table — "if latency is high and tasks are heavy → …".
- **Why the results look like this:** causes, tied to the model (λ₂, diameter, master load).
- **Threats to validity:** internal (implementation bugs, tuning), external (workloads, hardware family, scale), construct (metrics), statistical (multiple comparisons). Mitigations.
- **Limitations** (explicit list: no DAG tasks, failure model scope, one NIC regime, small N on hardware, …).

### 10.13 X. Conclusion and Future Work (≈ 0.4 page)
Restate the problem, the approach, and the 3 most important findings with numbers; one honest limitation; 3 concrete future directions (dynamic spawning/DAGs, larger prototype or geometry-aware cabling, learning-based policies). No new results. No overclaiming.

### 10.14 Back matter
- Acknowledgments (funding, equipment, **AI-assistance disclosure** per IEEE policy).
- Data availability statement (repository, DOI, license).
- References (IEEEtran style).
- Appendices: proofs/derivations, extra tables/figures, hardware photos, parameters.
- Author biographies/photos if the journal requires them (placeholders).

---

## 11. LaTeX SKELETON (start from this; reuse `IEEEtran.cls` from the existing package)

```latex
\documentclass[journal]{IEEEtran}
\usepackage{cite}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{algorithm}
\usepackage{algpseudocode}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{siunitx}
\usepackage{xcolor}
\usepackage{textcomp}
\usepackage[hidelinks]{hyperref}
\input{results/numbers.tex}   % auto-generated macros for every number in the text

\begin{document}
\title{[TITLE]}
\author{[AUTHOR NAME]\IEEEauthorrefmark{1}, [AUTHOR NAME]\IEEEauthorrefmark{2}% 
\thanks{[AFFILIATION AND FUNDING -- human supplies]}}
\markboth{IEEE TRANSACTIONS ON PARALLEL AND DISTRIBUTED SYSTEMS, VOL. XX, NO. X, MONTH 2026}{[AUTHOR] \MakeLowercase{\textit{et al.}}: [SHORT TITLE]}
\maketitle

\begin{abstract}
% Context. Gap. Approach. Key numbers (from numbers.tex). Implication. Artifact.
\end{abstract}

\begin{IEEEkeywords}
Distributed scheduling, load balancing, work sharing, network topology, spectral graph theory, cluster computing.
\end{IEEEkeywords}

\section{Introduction}\label{sec:intro}
\section{Background and Related Work}\label{sec:related}
\section{Problem Statement and System Model}\label{sec:model}
\section{Polyhedral Cluster Topologies}\label{sec:topo}
\section{Scheduling Policies}\label{sec:policies}
\section{Implementation and Prototype}\label{sec:impl}
\section{Experimental Methodology}\label{sec:method}
\section{Results}\label{sec:results}
\subsection{Simulator Validation}
\subsection{Main Comparison}
\subsection{Does Topology Matter?}
\subsection{Scaling}
\subsection{Communication Cost and Master Load}
\subsection{Heterogeneity, Stragglers, and Faults}
\subsection{Ablation}
\section{Discussion}\label{sec:discussion}
\section{Conclusion}\label{sec:conclusion}

\section*{Acknowledgments}
% Funding, equipment. AI-assistance disclosure (check current IEEE wording).

\bibliographystyle{IEEEtran}
\bibliography{refs}

\appendices
\section{Derivations}
\section{Additional Results}
\end{document}
```
Rules: compile with `pdflatex` + `bibtex` until stable; **zero** "undefined reference/citation" warnings; no overfull boxes wider than a few points; PDF fonts embedded (run `pdffonts`); figures included as PDF; table/figure numbers match text; run a spell-check.

---

## 12. SUBMISSION PACKAGE (produce, then hand to the human)

1. `paper.pdf` and LaTeX source, figures, `refs.bib`, compiled with the journal's current class/guidelines (check whether a double-blind version is required; if so, remove names, self-identifying links, and acknowledgments).
2. **Cover letter** (≤ 1 page): problem, what is new, why this journal, confirmation of originality and no simultaneous submission, suggested handling editor/area (optional), conflicts.
3. **Highlights** (3–5 bullets, ≤ 85 characters each, if requested).
4. **Suggested reviewers** (5–6 names with verified affiliations and no conflict; the human decides).
5. **Data/code availability statement** with repository DOI.
6. **AI-use disclosure** and a statement that all content was reviewed and verified by the authors.
7. **Similarity check** report (use the human's institution tool, e.g., iThenticate); fix unintended overlaps; no overlap with the existing dissertation text beyond what is declared.
8. **Prior-publication note:** if a conference version exists, state the overlap and the extension (journal papers usually need substantial new content).
9. **Ethics/conflict/funding** statements; author contributions (CRediT).
10. **Response-to-reviewers plan:** keep a list of likely reviewer objections (Section 2 weaknesses; "only synthetic workloads"; "small N"; "unfair tuning") and the exact figure/table/section that answers each.

---

## 13. QUALITY GATES AND CHECKLISTS

### 13.1 Before writing the paper
- [ ] All tests pass (≥ 200), replay verification passes, fresh-clone reproduction works.
- [ ] Preregistration written and committed *before* final runs; git tag exists.
- [ ] Tuning seeds and evaluation seeds are disjoint (check in code).
- [ ] Every competitor has the same tuning budget (log shows it).
- [ ] Simulator validated against hardware; error reported honestly.
- [ ] All hardware raw logs stored with environment fingerprints.
- [ ] Exclusions logged with reasons.
- [ ] Graph metrics reproduce known values (WP2).

### 13.2 Before submission
**Science**
- [ ] Each contribution is supported by a figure/table; each RQ answered (including "no").
- [ ] No claim outruns evidence; no "geometric advantage" claim unless isolated by RQ2 data.
- [ ] Limitations and threats to validity are complete and specific.
- [ ] Statistics follow Section 6.6; adjusted p-values/CIs reported; equivalence tests for null claims.
**Evidence integrity**
- [ ] Every number/figure/table regenerates from `make all`.
- [ ] Simulation vs hardware results are labelled everywhere.
- [ ] No unexplained differences between text, tables, figures.
**Literature**
- [ ] ≥ 50 references verified; related-work table; closest-paper comparison paragraph; patent prior art cited.
- [ ] No unverifiable citation remains.
**Writing and format**
- [ ] Template and page limit satisfied; abstract 150–250 words; keywords set.
- [ ] Notation consistent; T1 matches usage; terminology fixed.
- [ ] Figures vector, readable, colorblind-safe, captions self-contained.
- [ ] No LaTeX warnings; fonts embedded; PDF accessible (alt text if required).
**Ethics and policy**
- [ ] AI-use disclosure; originality; conflicts; data availability; license.
**Artifact**
- [ ] Repository public (or reviewer-accessible), tagged, DOI minted, README with exact commands and expected outputs, hardware runbook.

### 13.3 Red-flag scan (reject your own draft if any is true)
- A result is better than every competitor in every cell (suspicious — check for bias).
- Large effects appear only in the artificial clustered workload.
- A claim depends on one seed, one graph, or one hardware run.
- The proposed policy was tuned more than the baselines.
- Prototype results exist only for the proposed policy.
- The abstract has adjectives but no numbers.

---

## 14. DO / DO NOT SUMMARY (one page to remember)

**DO**
- Start with the audit and the literature; position honestly.
- Explain the null result with theory (graph metrics) instead of hiding it.
- Test the idea on real hardware and calibrate the simulator with measurements.
- Use paired seeds, tuning/evaluation split, preregistration, corrected statistics.
- Compare against strong, correctly implemented, equally tuned competitors including an oracle and a real runtime.
- Auto-generate every number, table, and figure.
- Keep a clean, reproducible artifact and a human-action list.

**DO NOT**
- Invent data, references, hardware results, or authors.
- Say "first/best/novel/optimal/significant" without proof.
- Credit the 3D shape for performance that comes from N, degree, or λ₂.
- Hide bad runs, switch metrics after seeing results, or tune only your own method.
- Let the paper's story drift away from the data.
- Submit with unverified references, LaTeX warnings, or a non-reproducible artifact.

---

## 15. HOW TO REPORT BACK TO THE HUMAN

After each work package, write `docs/STATUS_WPx.md` (≤ 1 page): what was done, files changed, tests run (pass/fail), key numbers, problems, decisions needed (copy to `docs/HUMAN_TODO.md`), and the next step. Use plain words first, with the technical term in brackets. If a gate fails (e.g., validation error too large, prior art found, no benefit from the new policy), stop and tell the human with options:
1. Fix the model/method and re-run the gate.
2. Reframe the paper honestly (for example: an empirical study with a null result and a validated simulator; a more modest venue).
3. Stop and ask for guidance.

**Final deliverables:** `paper/paper.pdf`, `paper/paper.tex`, `refs.bib`, `figures/`, `results/`, `hardware/`, `docs/`, `study/` (code and tests), submission package (Section 12), and a one-page summary of what the paper can and cannot claim.

*End of instruction file.*