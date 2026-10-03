"""Regular solids; edges derived from shortest Euclidean vertex distance."""
from itertools import product
from functools import lru_cache
import numpy as np
from scipy.spatial import ConvexHull

SOLIDS = {"tetrahedron": (4, 6, 3, 4), "cube": (8, 12, 3, 6),
          "octahedron": (6, 12, 4, 8), "dodecahedron": (20, 30, 3, 12),
          "icosahedron": (12, 30, 5, 20)}

@lru_cache(maxsize=None)
def geometry(name):
    phi = (1 + np.sqrt(5)) / 2
    signs = list(product((-1., 1.), repeat=2))
    if name == "tetrahedron":
        vertices = [p for p in product((-1., 1.), repeat=3) if np.prod(p) == 1]
    elif name == "cube":
        vertices = list(product((-1., 1.), repeat=3))
    elif name == "octahedron":
        vertices = list(np.eye(3)) + list(-np.eye(3))
    elif name == "icosahedron":
        vertices = [(0, a, b*phi) for a,b in signs] + [(a, b*phi, 0) for a,b in signs] + [(a*phi, 0, b) for a,b in signs]
    elif name == "dodecahedron":
        vertices = list(product((-1., 1.), repeat=3)) + [(0, a/phi, b*phi) for a,b in signs] + [(a/phi, b*phi, 0) for a,b in signs] + [(a*phi, 0, b/phi) for a,b in signs]
    else:
        raise ValueError(name)
    vertices = np.array(vertices, dtype=float)
    vertices /= np.linalg.norm(vertices[0])
    dist = np.linalg.norm(vertices[:, None] - vertices[None, :], axis=2)
    edge_length = dist[dist > 1e-10].min()
    edges = [(i,j) for i in range(len(vertices)) for j in range(i+1,len(vertices)) if np.isclose(dist[i,j], edge_length)]
    neighbors = {i: [] for i in range(len(vertices))}
    for i,j in edges:
        neighbors[i].append(j); neighbors[j].append(i)
    # ConvexHull triangulates pentagons/squares; count unique supporting planes.
    faces = len(np.unique(np.round(ConvexHull(vertices).equations, 8), axis=0))
    v,e,d,f = SOLIDS[name]
    assert (len(vertices), len(edges), faces) == (v,e,f)
    assert all(len(ns) == d for ns in neighbors.values())
    assert v-e+f == 2
    seen, todo = set(), [0]
    while todo:
        i = todo.pop()
        if i not in seen:
            seen.add(i); todo.extend(neighbors[i])
    assert len(seen) == v
    return vertices, edges, neighbors

def alternative_edges(name, solid, seed):
    """Physical peer-topology controls with the same master spokes."""
    n,_,degree,_ = SOLIDS[solid]
    if name == "star": return []
    if name == "complete": return [(i,j) for i in range(n) for j in range(i+1,n)]
    if name == "ring": return sorted({tuple(sorted((i,(i+1)%n))) for i in range(n)})
    if name == "grid":
        rows = {4:2,6:2,8:2,12:3,20:4}[n]; cols=n//rows
        edges=[]
        for r in range(rows):
            for c in range(cols):
                i=r*cols+c
                if c+1<cols: edges.append((i,i+1))
                if r+1<rows: edges.append((i,i+cols))
        return edges
    if name != "random_regular": raise ValueError(name)
    # Degree-preserving double-edge swaps; this is a rewired control, not a
    # claimed uniform sample from the space of all regular graphs.
    rng=np.random.default_rng(seed)
    original=set(geometry(solid)[1])
    for attempt in range(50):
        edges=set(original)
        for _ in range(100*len(edges)):
            pairs=sorted(edges)
            picks=rng.choice(len(pairs),2,replace=False)
            a,b=pairs[picks[0]];c,d=pairs[picks[1]]
            if rng.random()<.5:c,d=d,c
            if len({a,b,c,d})<4: continue
            new1=tuple(sorted((a,c)));new2=tuple(sorted((b,d)))
            if new1 in edges or new2 in edges:continue
            edges.remove(tuple(sorted((a,b))));edges.remove(tuple(sorted((c,d))))
            edges.update((new1,new2))
        adj={i:set() for i in range(n)}
        for a,b in edges:adj[a].add(b);adj[b].add(a)
        seen=set();todo=[0]
        while todo:
            i=todo.pop()
            if i not in seen:seen.add(i);todo.extend(adj[i])
        if len(seen)==n:
            assert len(edges)==len(original) and all(len(x)==degree for x in adj.values())
            return sorted(edges)
    raise RuntimeError("Failed to produce connected degree-preserving control")
