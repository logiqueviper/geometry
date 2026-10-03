# Master-centered Platonic-solid scheduling study

This repository contains a completed **discrete-event simulation study** and an
IEEE two-column journal-format manuscript. It does not report physical-cluster
measurements. Node compute power, link bandwidth, and link latency are constant.

Read [paper/paper.pdf](paper/paper.pdf) for the study, or
[results/summary.csv](results/summary.csv) for all scheduler means and confidence
intervals. The final ZIP contains source, raw runs, analysis, figures, and PDF.

## Measured scope and findings

- All five Platonic solids: tetrahedron (4 workers), cube (8), octahedron (6),
  dodecahedron (20), and icosahedron (12), each with an additional master.
- Seven policies: static equal allocation, neighbor push, neighbor stealing,
  global stealing, master-mediated rebalancing, single-task master queue,
  and guided master queue (batch `ceil(remaining / (2 * workers))`).
- 2,400 independent tasks in the primary experiment, 1 ms mean cost, 4 KiB
  input, 64-byte identified result, 32-byte header/control message; 100 MiB/s
  and 10 microseconds per directed link. Results stream to the master.
- Constant, exponential, lognormal (population CV 2), capped Pareto, and sorted
  lognormal clustered workloads. Equal initial **counts** do not imply equal cost.
- 5,250 primary runs, 6,300 sensitivity runs, and 4,500 topology runs = 16,050.
  Thirty paired seeds per primary/topology cell; fifteen per sensitivity cell.
- Paired speedup over static: 1.074–1.228 for independent lognormal costs and
  2.763–5.630 for the clustered stress workload. Equal-cost tasks have no gain.
  Neighbor push has the lowest mean in only 1 of 20 variable-cost primary cells.
  Other schedulers frequently match or improve on it.
- Rewired controls preserve degree and peer-link count. Results do not establish
  general superiority of Platonic connectivity. Ring, grid, star, and complete
  graph controls have different peer-link budgets and are reported accordingly.

Raw milliseconds are simulated time. A faster machine changes study execution
time, not these simulated results. Bootstrap intervals are exploratory, uncorrected
cell-wise 95% intervals; a lowest mean is not automatically a significant win.

## Run and reproduce

Work in the existing isolated checkout. Do not create a worktree for setup.
The current cloud image supplies Python 3.12 and `pdflatex`; the bundled class
avoids a CTAN download during compilation. Dependencies are pinned in
`requirements-study.txt`. Installation only writes a virtual environment and
caches outside the checkout; tests can create normal local cache files.

```bash
cd /workspace/geometry
bash setup-study.sh
source /workspace/platonic-env/venv/bin/activate
export MPLCONFIGDIR=/workspace/platonic-env/matplotlib
export XDG_CACHE_HOME=/workspace/platonic-env/cache
python -m study.benchmark --replicates 30 --sensitivity-replicates 15 --processes 4
python -m study.topology_benchmark
python -m study.verify_results
python -m study.analyze
python -m study.build_paper
```

Benchmark commands regenerate the documented result CSVs. If changing task
counts, policies, or repetition counts, adapt `verify_results.py`'s expected design
and update the manuscript rather than presenting a different experiment under
the current paper's claims. No services, credentials, GPU, or live server are needed.
Network is needed only when installing missing Python packages.

Quick readiness check without rerunning all measurements:

```bash
cd /workspace/geometry
/workspace/platonic-env/venv/bin/python -m pytest study/test_simulator.py -q
/workspace/platonic-env/venv/bin/python -m study.verify_results
/workspace/platonic-env/venv/bin/python -m study.build_paper
```

The recorded tests pass 116 checks, including geometry, analytic static timing,
zero-overhead balancing, every scheduler and solid, task conservation after each
event in audit runs, routing, running-task immobility, reservation races, and
topology controls. Every benchmark verifies completion and result collection
of every unique ID. The replay verifier also compares saved numerical outputs
with fresh simulations of selected cases.

## Files

| Path | Contents |
|---|---|
| `study/geometry.py` | Coordinates, minimum-distance edges, graph checks, controls |
| `study/simulator.py` | Event model, FIFO links, task ownership, seven schedulers |
| `study/test_simulator.py` | 116 validation tests |
| `study/benchmark.py` | Paired primary and sensitivity experiments |
| `study/topology_benchmark.py` | Same-size alternative graph experiments |
| `study/analyze.py` | Seed-paired bootstrap analysis and publication plots |
| `study/verify_results.py` | Experiment completeness and deterministic replay |
| `results/raw.csv` | 11,550 individual scheduler and sensitivity runs |
| `results/topology.csv` | 4,500 individual topology runs |
| `results/summary.csv` | Makespan intervals, speedups, utilization, traffic |
| `results/paired_effects.csv` | Push/static and push/local-steal paired intervals |
| `results/topology_summary.csv` | Topology means and paired controls |
| `results/verification.json` | Executed completeness/replay evidence |
| `paper/paper.tex` | Editable IEEE journal manuscript |
| `paper/paper.pdf` | Compiled two-column paper |
| `paper/figures/` | Eight standalone PDF and PNG figures |
| `paper/CLASS_PROVENANCE.md` | Bundled class source and checksum |

The paper includes six of the eight figures; the all-policy makespan chart and
an illustrative task timeline are also supplied as standalone figures. Author
names and affiliations are intentionally left for the study owner to supply.
No tracked files existed in this initially unborn repository; the study files
are new, and no existing application code or lockfiles were altered.

## Modeling boundaries

Tasks execute once, without preemption. Only queued tasks migrate; peers must
share an actual edge. Push uses idle epochs plus offer/accept/reject reservations.
Control packets consume link capacity. Returned results go directly to the
master, preserving original IDs even after multiple migrations. Schedulers do
not know actual task durations. Nonadjacent global requests and data use the
same physical two-hop master route. Primary links are independent full-duplex
serializers; shared-NIC and master-service constraints are separate sensitivities.

The clustered workload deliberately concentrates expensive tasks and is not a
measured application trace. Costs are normalized to exactly 2,400 ms total work
in every primary instance. The topology control uses degree-preserving random
rewiring, not a uniform random-regular graph sampler. Geometry affects adjacency;
it supplies no physical-distance advantage when all links have equal latency.
The paper states omitted CPU-control costs, failures, memory, and other limits.
