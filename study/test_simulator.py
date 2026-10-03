"""Analytic, ownership, geometry, and adversarial protocol validation."""
import numpy as np
import pytest
from .geometry import geometry, SOLIDS, alternative_edges
from .simulator import Simulation, Config, POLICIES, workload

@pytest.mark.parametrize("solid", SOLIDS)
def test_geometry(solid):
    vertices,edges,adj = geometry(solid)
    assert np.allclose(np.linalg.norm(vertices,axis=1),1)
    assert all(i in adj[j] for i,j in edges)

@pytest.mark.parametrize("solid", SOLIDS)
def test_static_analytic(solid):
    n = SOLIDS[solid][0]; costs = workload("lognormal",120,18)
    c = Config()
    init = c.latency_ms+(c.control_bytes+120//n*c.task_bytes)/(c.bandwidth_mib_s*2**20/1000)
    finish = init+max(x.sum() for x in np.split(costs,n))
    result = c.latency_ms+c.result_bytes/(c.bandwidth_mib_s*2**20/1000)
    actual = Simulation(solid,"static",costs,config=c,audit=True).run()
    assert actual["makespan_ms"] == pytest.approx(finish+result)
    assert actual["messages"] == n+len(costs)

@pytest.mark.parametrize("solid", SOLIDS)
@pytest.mark.parametrize("policy", POLICIES)
@pytest.mark.parametrize("shared", [False,True])
def test_exactly_once_all_policies(solid,policy,shared):
    sim = Simulation(solid,policy,workload("clustered",120,82),config=Config(shared_nic=shared,master_service_ms=.003),audit=True)
    result = sim.run()
    assert result["collected"] == 120
    assert result["utilization"] <= 1
    for _,action,task,node in sim.trace:
        assert 0 <= task < 120 and 0 <= node < sim.n

def test_routed_transfer_nonadjacent():
    sim = Simulation("cube","global_steal",workload("clustered",120,1),audit=True)
    result = sim.run()
    assert result["migrated_tasks"] > 0
    assert result["master_messages"] > 128

def test_zero_overhead_identical_work():
    c = Config(latency_ms=0, bandwidth_mib_s=1e15,task_bytes=0,result_bytes=0,control_bytes=0)
    for policy in POLICIES:
        result = Simulation("icosahedron",policy,np.ones(120),config=c,audit=True).run()
        assert result["makespan_ms"] == pytest.approx(10.)

def test_push_and_steal_improve_known_imbalance():
    costs = np.r_[np.full(30,4.),np.ones(90)]
    c = Config(latency_ms=.001,bandwidth_mib_s=1000)
    baseline = Simulation("tetrahedron","static",costs,config=c).run()
    for policy in ("neighbor_push","neighbor_steal","central_rebalance"):
        sim = Simulation("tetrahedron",policy,costs,config=c,audit=True)
        result = sim.run()
        assert result["makespan_ms"] < .75*baseline["makespan_ms"]
        assert result["migrated_tasks"] > 0

def test_running_long_task_cannot_migrate():
    costs = np.ones(120); costs[0] = 1000
    for policy in POLICIES:
        result = Simulation("icosahedron",policy,costs,audit=True).run()
        assert result["makespan_ms"] >= 1000

@pytest.mark.parametrize("policy", POLICIES)
def test_slow_links_and_reservation_races(policy):
    for seed in range(4):
        sim = Simulation("dodecahedron",policy,workload("pareto",120,seed),seed,
                         Config(latency_ms=2,bandwidth_mib_s=.5,split=.75),audit=True)
        result = sim.run()
        assert result["executed"] == result["collected"] == 120

@pytest.mark.parametrize("solid",SOLIDS)
@pytest.mark.parametrize("topology",["star","ring","grid","random_regular","complete"])
def test_topology_controls(solid,topology):
    edges=alternative_edges(topology,solid,9)
    assert len(edges)==len(set(edges))
    if topology=="random_regular":
        assert len(edges)==SOLIDS[solid][1]
        assert all(sum(i in e for e in edges)==SOLIDS[solid][2] for i in range(SOLIDS[solid][0]))
    for policy in ("neighbor_push","neighbor_steal"):
        sim=Simulation(solid,policy,workload("clustered",120,9),audit=True,peer_edges=edges)
        assert sim.run()["collected"]==120
