"""Check experiment completeness and replay selected saved numerical results."""
import csv
import json
import hashlib
from pathlib import Path
import numpy as np
from .simulator import Simulation, Config, POLICIES, workload
from .geometry import SOLIDS, alternative_edges
from .benchmark import WORKLOADS

def read(path):
    return list(csv.DictReader(path.open()))

def config(row):
    defaults=Config()
    values={}
    for name,value in defaults.__dict__.items():
        if isinstance(value,bool):values[name]=row[name]=="True"
        elif isinstance(value,int):values[name]=int(row[name])
        else:values[name]=float(row[name])
    return Config(**values)

def main():
    root=Path(__file__).resolve().parents[1]
    rows=read(root/"results/raw.csv"); top=read(root/"results/topology.csv")
    assert len(rows)==11550 and len(top)==4500
    expected={(s,w,p,seed) for s in SOLIDS for w in WORKLOADS for p in POLICIES for seed in range(30)}
    actual={(r["solid"],r["workload"],r["policy"],int(r["seed"])) for r in rows if r["suite"]=="main"}
    assert actual==expected and len(actual)==5250
    keys=[(r["suite"],r["solid"],r["workload"],r["policy"],r["seed"]) for r in rows]
    assert len(keys)==len(set(keys))
    expected_top={(s,w,p,seed,t) for s in SOLIDS for w in ("lognormal","pareto","clustered")
                  for p in ("neighbor_push","neighbor_steal") for seed in range(30)
                  for t in ("star","ring","grid","random_regular","complete")}
    actual_top={(r["solid"],r["workload"],r["policy"],int(r["seed"]),r["topology"]) for r in top}
    assert actual_top==expected_top
    for r in rows+top:
        assert int(r["executed"])==int(r["collected"])==int(r["tasks"])
        assert np.isfinite(float(r["makespan_ms"])) and float(r["makespan_ms"])>=float(r["lower_bound_ms"])-1e-8
        assert 0<float(r["utilization"])<=1
    # All policy/solid primary combinations plus representative bottlenecks
    # and every topology control. These replays compare full numerical outputs.
    sample=[r for r in rows if int(r["seed"])==3 and r["workload"]=="clustered" and
            r["suite"] in ("main","shared_nic_master","latency_1.0","batch_8","tasks_120")]
    sample += [r for r in top if int(r["seed"])==3 and r["workload"]=="clustered"]
    for r in sample:
        seed=int(r["seed"]);costs=workload(r["workload"],int(r["tasks"]),seed)
        edges=None if r["suite"]!="topology" else alternative_edges(r["topology"],r["solid"],seed+90001)
        result=Simulation(r["solid"],r["policy"],costs,seed+70001,config(r),peer_edges=edges).run()
        for k,value in result.items():
            assert np.isclose(value,float(r[k]),rtol=1e-12,atol=1e-10),(r["suite"],r["solid"],r["policy"],k)
    report={"raw_runs_checked":len(rows)+len(top),"selected_full_output_replays":len(sample),
            "all_tasks_executed_and_collected":True,"all_required_primary_and_topology_cells_present":True}
    (root/"results/verification.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))

if __name__=="__main__":main()
