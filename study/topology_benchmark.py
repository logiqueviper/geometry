import csv
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from .geometry import SOLIDS, alternative_edges
from .simulator import Simulation, Config, workload

def case(job):
    solid,kind,seed,topology=job
    edges=alternative_edges(topology,solid,seed+90001)
    c=Config(); costs=workload(kind,2400,seed)
    rows=[]
    for policy in ("neighbor_push","neighbor_steal"):
        result=Simulation(solid,policy,costs,seed+70001,c,peer_edges=edges).run()
        rows.append({"suite":"topology","solid":solid,"workers":SOLIDS[solid][0],
                     "workload":kind,"seed":seed,"tasks":2400,"policy":policy,
                     "topology":topology,"peer_links":len(edges),**asdict(c),**result})
    return rows

def main():
    jobs=[(s,w,r,t) for s in SOLIDS for w in ("lognormal","pareto","clustered")
          for r in range(30) for t in ("star","ring","grid","random_regular","complete")]
    start=time.time()
    with open("results/topology.csv","w",newline="") as f,ProcessPoolExecutor(max_workers=4) as pool:
        writer=None
        for i,rows in enumerate(pool.map(case,jobs,chunksize=4),1):
            if writer is None:writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader()
            writer.writerows(rows)
            if i%150==0:
                f.flush();print(f"{i}/{len(jobs)} cases; {time.time()-start:.1f}s",flush=True)
    print(f"{len(jobs)*2} runs completed",flush=True)

if __name__ == "__main__":main()
