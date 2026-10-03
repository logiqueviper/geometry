# Analytic graph model — scope and derivation

Evidence type: **analytic**. This is a continuous-load model, not a theorem about
the current indivisible-task, idle-triggered push scheduler.

For an undirected connected worker graph, let A be the adjacency matrix,
D its diagonal degree matrix, and L = D - A its Laplacian. The synchronous
iteration is x(k+1) = P x(k), where P = I - alpha L. Since L is symmetric,
L 1 = 0, and its eigenvalues are nonnegative, the mean load is preserved.
Decomposing the mean-free load into the nonconstant Laplacian eigenvectors gives

`||x(k) - mean(x) 1||_2 <= rho^k ||x(0) - mean(x) 1||_2`,

where `rho = max_{i >= 2} |1 - alpha lambda_i|`.

The minimax spectral parameter for this stationary linear iteration is
`alpha = 2 / (lambda_2 + lambda_max)`. To retain entrywise nonnegative mixing
weights, the saved convex-load proxy uses
`alpha_convex = min(alpha, 1 / maximum_degree)`.
The recorded 99% reduction step count is `ceil(log(0.01) / log(rho))`, with the
zero-rho case handled as one step. Disconnected worker graphs have no finite
mixing prediction. This model involves known continuous load, synchronized
updates, no task indivisibility, and no communication delay. It cannot supply
measured scheduler balancing times or justify a makespan guarantee.

Adding a universal master creates a graph cone. Its Laplacian spectrum is
`0, N+1, 1+lambda_2, ..., 1+lambda_N`. The graph-metric tests verify this relation
against independently computed eigenvalues. A larger hub-graph connectivity
does not imply peer-data transfers can use absent worker edges. A hub-assisted
control policy will need to obey that routing distinction explicitly.

`analysis/graph_metrics.py` computes worker and hub metrics. Bisection is exact
by enumeration through 21 vertices; larger graphs use spectral ordering and
improving balanced swaps, reported as an upper bound. Edge connectivity uses
minimum max-flow from a fixed vertex to every other vertex. Edge expansion is
enumerated over subsets only for the small Platonic worker graphs; missing
values are marked uncomputed, never substituted by a heuristic without notice.

All five supplied lambda2 values are reproduced. Geodesic subdivisions are
constructed from icosahedral face barycentric grids projected to the unit sphere;
subdivision incidence defines their edges. A global minimum-distance rule is
not used on these nonuniform projected meshes. Frequencies 2, 3, and 4 yield
42, 92, and 162 vertices with twelve degree-five vertices and all others degree
six. Those graphs have not yet been benchmarked by the upgraded scheduler.

External diffusion literature cited in the instructions must be verified before
this becomes a literature-backed journal section. The derivation above stands
as a documented limited mathematical model. A lambda2-only prediction is
insufficient: lambda_max, the selected parameter, update frequency, indivisible
tasks, stale control information, and transfer cost also affect actual behavior.
