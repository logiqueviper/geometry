import numpy as np
import pytest
from study.geometry import SOLIDS,geometry
from .graph_metrics import adjacency,metrics,hub_edges,geodesic,exact_bisection,approximate_bisection

KNOWN={"tetrahedron":4.,"octahedron":4.,"cube":2.,"icosahedron":5-np.sqrt(5),"dodecahedron":3-np.sqrt(5)}

@pytest.mark.parametrize("solid",SOLIDS)
def test_known_spectra_and_cone(solid):
    n=SOLIDS[solid][0];edges=geometry(solid)[1]
    worker=metrics(n,edges);hub=metrics(n+1,hub_edges(n,edges))
    assert worker["lambda2"]==pytest.approx(KNOWN[solid])
    assert hub["lambda2"]==pytest.approx(min(n+1,1+worker["lambda2"]))
    assert hub["diameter"]<=2
    assert worker["edge_connectivity"]==SOLIDS[solid][2]

@pytest.mark.parametrize("n",[4,6,8,12,20])
def test_complete_graph_analytic(n):
    edges=[(i,j) for i in range(n) for j in range(i+1,n)]
    m=metrics(n,edges)
    assert m["lambda2"]==pytest.approx(n)
    assert m["bisection_width"]==(n//2)*(n-n//2)
    assert m["diffusion_steps_99pct_l2"]==1
    assert m["edge_connectivity"]==n-1

@pytest.mark.parametrize("n",[4,6,8,12,20])
def test_ring_cut_and_spectrum(n):
    edges=[tuple(sorted((i,(i+1)%n))) for i in range(n)]
    m=metrics(n,edges)
    assert m["lambda2"]==pytest.approx(2-2*np.cos(2*np.pi/n))
    assert m["bisection_width"]==m["edge_connectivity"]==2
    assert m["diameter"]==n//2

def test_disconnected_has_no_finite_mixing_claim():
    m=metrics(8,[])
    assert not m["connected"] and m["lambda2"]==0
    assert m["diameter"] is None and m["diffusion_steps_99pct_l2"] is None

@pytest.mark.parametrize("f",[1,2,3,4])
def test_geodesic_triangulations(f):
    v,e=geodesic(f)
    assert len(v)==10*f*f+2 and len(e)==3*len(v)-6
    assert np.allclose(np.linalg.norm(v,axis=1),1)
    if f==1:
        assert len(v)==12 and np.all(adjacency(len(v),e).sum(axis=1)==5)

@pytest.mark.parametrize("solid",SOLIDS)
def test_heuristic_cut_never_beats_exact_optimum(solid):
    v,e,_=geometry(solid)
    assert approximate_bisection(adjacency(len(v),e))>=exact_bisection(len(v),e)

def test_diffusion_prediction_matches_l2_contraction():
    v,e,_=geometry("dodecahedron");a=adjacency(len(v),e);m=metrics(len(v),e)
    lap=np.diag(a.sum(axis=1))-a;p=np.eye(len(v))-m["alpha_convex"]*lap
    assert np.min(p)>=-1e-12 and np.allclose(p.sum(axis=1),1)
    rng=np.random.default_rng(42);x=rng.random(len(v));mean=x.mean();initial=np.linalg.norm(x-mean)
    for _ in range(m["diffusion_steps_99pct_l2"]):x=p@x
    assert np.linalg.norm(x-mean)<=.0100001*initial
