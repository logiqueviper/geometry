"""Graph properties, exact small-graph cuts, and analytic diffusion proxies.

These are analytic graph computations, not hardware or new scheduler results.
Disconnected graphs have undefined path lengths and no mixing prediction.
"""
from itertools import combinations
from functools import lru_cache
from pathlib import Path
import csv
import json
import math
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path, maximum_flow
from scipy.spatial import ConvexHull
from study.geometry import SOLIDS, geometry, alternative_edges

ROOT=Path(__file__).resolve().parents[1]

def adjacency(n,edges):
    a=np.zeros((n,n),dtype=np.int64)
    for i,j in edges:
        if not (0<=i<n and 0<=j<n) or i==j:raise ValueError("Invalid edge")
        a[i,j]=a[j,i]=1
    return a

@lru_cache(maxsize=12)
def balanced_masks(n):
    # For even n, fixing vertex zero removes complementary duplicates.
    k=n//2
    if n%2==0:
        masks=np.fromiter((1+sum(1<<i for i in group) for group in combinations(range(1,n),k-1)),dtype=np.uint64)
    else:
        masks=np.fromiter((sum(1<<i for i in group) for group in combinations(range(n),k)),dtype=np.uint64)
    return masks

def exact_bisection(n,edges):
    if n<2:return 0
    if n>21:raise ValueError("Exact bisection limited to 21 vertices")
    masks=balanced_masks(n);cut=np.zeros(len(masks),dtype=np.int16)
    for i,j in edges:cut+=(((masks>>i)^(masks>>j))&1).astype(np.int16)
    return int(cut.min())

def approximate_bisection(a):
    # Deterministic spectral ordering followed by best improving balanced swaps.
    n=len(a);_,vectors=np.linalg.eigh(np.diag(a.sum(axis=1))-a)
    side=np.zeros(n,dtype=bool);side[np.argsort(vectors[:,1],kind="stable")[:n//2]]=True
    def cut(s):return int(a[np.ix_(s,~s)].sum())
    value=cut(side)
    for _ in range(200):
        best=None;best_value=value
        for i in np.flatnonzero(side):
            for j in np.flatnonzero(~side):
                candidate=side.copy();candidate[i]=False;candidate[j]=True
                # Delta: both endpoint cut changes, corrected for their edge.
                delta=(a[i,side].sum()-a[i,~side].sum())+(a[j,~side].sum()-a[j,side].sum())+2*a[i,j]
                new=value+int(delta)
                if new<best_value:best=(i,j);best_value=new
        if best is None:break
        side[best[0]]=False;side[best[1]]=True;value=best_value
    assert value==cut(side)
    return value

def exact_expansion(n,edges):
    if n>20:raise ValueError("Exact expansion limited to 20 vertices")
    best=math.inf
    for k in range(1,n//2+1):
        masks=np.fromiter((sum(1<<i for i in group) for group in combinations(range(n),k)),dtype=np.uint64)
        cut=np.zeros(len(masks),dtype=np.int16)
        for i,j in edges:cut+=(((masks>>i)^(masks>>j))&1).astype(np.int16)
        best=min(best,float(cut.min())/k)
    return best

def metrics(n,edges,compute_expansion=False):
    edges=sorted({tuple(sorted(e)) for e in edges})
    a=adjacency(n,edges);degree=a.sum(axis=1)
    laplacian=np.diag(degree)-a
    spectrum=np.linalg.eigvalsh(laplacian)
    spectrum[np.abs(spectrum)<1e-10]=0
    lam2=float(spectrum[1]);lammax=float(spectrum[-1])
    connected=bool(lam2>1e-10)
    dist=shortest_path(csr_matrix(a),directed=False)
    paths=dist[np.triu_indices(n,1)]
    diameter=int(paths.max()) if connected else None
    mean_path=float(paths.mean()) if connected else None
    edge_connectivity=min(int(maximum_flow(csr_matrix(a),0,j).flow_value) for j in range(1,n)) if connected else 0
    bisect=exact_bisection(n,edges) if n<=21 else approximate_bisection(a)
    alpha=2/(lam2+lammax) if connected else None
    # Keep diffusion matrix entrywise nonnegative for the convex load model.
    alpha_convex=min(alpha,1/degree.max()) if connected else None
    rho=float(max(abs(1-alpha_convex*spectrum[1:]))) if connected else None
    if rho is not None and rho<1e-12:steps=1
    else:steps=math.ceil(math.log(.01)/math.log(rho)) if connected else None
    expansion=exact_expansion(n,edges) if compute_expansion and n<=20 else None
    return {"vertices":n,"edges":len(edges),"degree_min":int(degree.min()),"degree_max":int(degree.max()),
            "degree_mean":float(degree.mean()),"connected":connected,"diameter":diameter,
            "mean_shortest_path":mean_path,"bisection_width":bisect,
            "bisection_method":"exact enumeration" if n<=21 else "spectral balanced swaps (upper bound)",
            "edge_connectivity":edge_connectivity,"lambda2":lam2,"lambda_max":lammax,
            "condition_number_nonzero":lammax/lam2 if connected else None,
            "alpha_spectral":alpha,"alpha_convex":alpha_convex,"diffusion_rho":rho,
            "diffusion_spectral_gap":1-rho if connected else None,
            "diffusion_steps_99pct_l2":steps,"expansion":expansion,
            "expansion_method":"exact small-subset enumeration" if expansion is not None else "not computed"}

def hub_edges(n,edges):return list(edges)+[(i,n) for i in range(n)]

def geodesic(frequency):
    if frequency<1:raise ValueError("Positive integer frequency required")
    base=geometry("icosahedron")[0];faces=ConvexHull(base).simplices
    vertices=[];lookup={};edges=set();f=frequency
    for face in faces:
        a,b,c=base[face];local={}
        for i in range(f+1):
            for j in range(f+1-i):
                p=((f-i-j)*a+i*b+j*c)/f;p/=np.linalg.norm(p)
                key=tuple(np.round(p,11))
                if key not in lookup:lookup[key]=len(vertices);vertices.append(p)
                local[i,j]=lookup[key]
        for (i,j),v in local.items():
            for di,dj in ((1,0),(0,1),(1,-1)):
                other=local.get((i+di,j+dj))
                if other is not None:edges.add(tuple(sorted((v,other))))
    n=10*f*f+2
    assert len(vertices)==n and len(edges)==3*n-6
    degree=adjacency(n,edges).sum(axis=1)
    assert np.count_nonzero(degree==5)==12 and np.all(np.isin(degree,(5,6)))
    return np.array(vertices),sorted(edges)

def main():
    known={"tetrahedron":4.,"octahedron":4.,"cube":2.,"icosahedron":5-np.sqrt(5),"dodecahedron":3-np.sqrt(5)}
    rows=[]
    for solid,(n,_,_,_) in SOLIDS.items():
        edges=geometry(solid)[1]
        for scope in ("worker","worker_and_hub"):
            nn,ee=(n,edges) if scope=="worker" else (n+1,hub_edges(n,edges))
            m=metrics(nn,ee,compute_expansion=scope=="worker")
            if scope=="worker":assert np.isclose(m["lambda2"],known[solid],atol=1e-9)
            rows.append({"solid":solid,"topology":"platonic","scope":scope,"graph_seed":None,"evidence":"analytic",**m})
        for topology in ("star","ring","grid","complete","random_regular"):
            graph_seeds=range(30) if topology=="random_regular" else [0]
            for seed in graph_seeds:
                ee=alternative_edges(topology,solid,90001+seed)
                rows.append({"solid":solid,"topology":topology,"scope":"worker","graph_seed":90001+seed,
                             "evidence":"analytic",**metrics(n,ee)})
    for f in (2,3,4):
        v,ee=geodesic(f)
        rows.append({"solid":f"geodesic_f{f}","topology":"platonic_derived","scope":"worker","graph_seed":None,
                     "evidence":"analytic",**metrics(len(v),ee)})
    (ROOT/"results/graph_metrics.json").write_text(json.dumps(rows,indent=2,allow_nan=False)+"\n")
    with (ROOT/"results/graph_metrics.csv").open("w",newline="") as file:
        writer=csv.DictWriter(file,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print(f"Saved {len(rows)} analytic graph records; all five known lambda2 values reproduced.")

if __name__=="__main__":main()
