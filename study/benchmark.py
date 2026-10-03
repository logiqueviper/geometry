"""Paired fixed-work benchmarks; writes all individual runs before analysis."""
import argparse
import csv
from dataclasses import asdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import json
import time
import platform
import numpy as np
import scipy
from .geometry import SOLIDS
from .simulator import Config, POLICIES, Simulation, workload

WORKLOADS = ("constant","exponential","lognormal","pareto","clustered")

def case(job):
    suite,solid,kind,seed,tasks,c = job
    costs = workload(kind,tasks,seed)
    rows=[]
    for policy in POLICIES:
        result = Simulation(solid,policy,costs,seed+70001,c).run()
        rows.append({"suite":suite,"solid":solid,"workers":SOLIDS[solid][0],
                     "workload":kind,"seed":seed,"tasks":tasks,"policy":policy,
                     **asdict(c),"work_cv":float(costs.std()/costs.mean()),**result})
    return rows

def jobs(reps,sensitivity_reps):
    main = [("main",s,w,seed,2400,Config()) for s in SOLIDS for w in WORKLOADS for seed in range(reps)]
    sensitivity = []
    for s in ("icosahedron","dodecahedron"):
        for w in ("lognormal","clustered"):
            configs = []
            for latency in (.001,.1,1.): configs.append((f"latency_{latency}",Config(latency_ms=latency)))
            for bw in (10.,1000.): configs.append((f"bandwidth_{bw}",Config(bandwidth_mib_s=bw)))
            configs += [("shared_nic",Config(shared_nic=True)),
                        ("master_service",Config(master_service_ms=.01)),
                        ("shared_nic_master",Config(shared_nic=True,master_service_ms=.01)),
                        ("split_quarter",Config(split=.25)),("split_threequarters",Config(split=.75)),
                        ("batch_8",Config(batch_cap=8)),("retry_fast",Config(retry_ms=.1)),
                        ("retry_slow",Config(retry_ms=10.))]
            for label,c in configs:
                sensitivity += [(label,s,w,seed,2400,c) for seed in range(sensitivity_reps)]
            for tasks in (120,9600):
                sensitivity += [(f"tasks_{tasks}",s,w,seed,tasks,Config()) for seed in range(sensitivity_reps)]
    return main+sensitivity

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--replicates",type=int,default=30)
    parser.add_argument("--sensitivity-replicates",type=int,default=15)
    parser.add_argument("--processes",type=int,default=4)
    parser.add_argument("--output",default="results/raw.csv")
    args=parser.parse_args()
    all_jobs=jobs(args.replicates,args.sensitivity_replicates)
    path=Path(args.output);path.parent.mkdir(exist_ok=True,parents=True)
    start=time.time(); count=0
    with path.open("w",newline="") as f, ProcessPoolExecutor(max_workers=args.processes) as pool:
        writer=None
        for rows in pool.map(case,all_jobs,chunksize=2):
            if writer is None:
                writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader()
            writer.writerows(rows); count+=1
            if count%50==0 or count==len(all_jobs):
                f.flush(); print(f"{count}/{len(all_jobs)} paired cases; {count*len(POLICIES)} runs; {time.time()-start:.1f}s",flush=True)
    metadata={"replicates":args.replicates,"sensitivity_replicates":args.sensitivity_replicates,
              "runs":len(all_jobs)*len(POLICIES),"elapsed_seconds":time.time()-start,
              "python":platform.python_version(),"numpy":np.__version__,"scipy":scipy.__version__,
              "primary_config":asdict(Config()),"task_count":2400,"unit":"milliseconds",
              "seed_scheme":"workload seed 0..R-1; scheduler seed workload seed + 70001",
              "hardware_scope":"discrete-event simulation, not hardware timing"}
    path.with_suffix(".metadata.json").write_text(json.dumps(metadata,indent=2)+"\n")
    print(json.dumps(metadata,indent=2))

if __name__ == "__main__": main()
