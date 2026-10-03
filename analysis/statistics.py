"""Explicitly retrospective paired tests; no retrospective preregistration.

Family: all 5 solids x 5 historical workloads x 2 push comparators = 50 tests.
Holm adjustment is valid under arbitrary dependence. The +/-1% equivalence
margin comes from the uploaded plan, after seeing historical data, and is
therefore exploratory. New final claims require the prospective experiment.
"""
from pathlib import Path
import csv
import json
import numpy as np
from scipy.stats import wilcoxon,t
from study.geometry import SOLIDS
from study.benchmark import WORKLOADS
from study.analyze import interval

ROOT=Path(__file__).resolve().parents[1]

def holm(pvalues):
    p=np.asarray(pvalues,dtype=float)
    if p.ndim!=1 or np.any(~np.isfinite(p)) or np.any((p<0)|(p>1)):raise ValueError("Invalid probabilities")
    order=np.argsort(p,kind="stable");adjusted=np.empty(len(p));previous=0.
    for rank,index in enumerate(order):
        previous=max(previous,(len(p)-rank)*p[index]);adjusted[index]=min(1.,previous)
    return adjusted

def tests(proposed,reference,margin=.01):
    p=np.asarray(proposed,dtype=float);r=np.asarray(reference,dtype=float)
    if p.shape!=r.shape or len(p)<2 or np.any(p<=0) or np.any(r<=0):raise ValueError("Invalid paired timings")
    differences=p-r
    if np.allclose(differences,0,rtol=0,atol=1e-10):p_w=1.
    else:p_w=float(wilcoxon(differences,alternative="two-sided",method="auto").pvalue)
    sd=float(differences.std(ddof=1));dz=float(differences.mean()/sd) if sd>1e-12 else (0. if abs(differences.mean())<1e-10 else None)
    logs=np.log(p/r);mean=float(logs.mean());se=float(logs.std(ddof=1)/np.sqrt(len(logs)))
    lower=np.log(1-margin);upper=np.log(1+margin)
    if se<1e-14:p_tost=0. if lower<mean<upper else 1.
    else:p_tost=float(max(t.sf((mean-lower)/se,len(logs)-1),t.cdf((mean-upper)/se,len(logs)-1)))
    speed,lo,hi=interval(r/p)
    return {"mean_paired_speedup":speed,"ratio_ci_low":lo,"ratio_ci_high":hi,
            "wilcoxon_p":p_w,"paired_cohen_dz":dz,"tost_p":p_tost,"tost_margin_relative":margin,
            "tost_assumption":"paired log-ratios with t-based mean bounds; retrospective margin"}

def main():
    raw=list(csv.DictReader((ROOT/"results/raw.csv").open()))
    lookup={(r["solid"],r["workload"],r["policy"],int(r["seed"])):float(r["makespan_ms"]) for r in raw if r["suite"]=="main"}
    output=[]
    for solid in SOLIDS:
        for w in WORKLOADS:
            proposed=[lookup[solid,w,"neighbor_push",s] for s in range(30)]
            for comparator in ("static","neighbor_steal"):
                reference=[lookup[solid,w,comparator,s] for s in range(30)]
                output.append({"solid":solid,"workload":w,"proposed":"neighbor_push","comparator":comparator,
                    "evidence":"simulation","phase":"retrospective exploratory","seeds":30,**tests(proposed,reference)})
    adjusted=holm([r["wilcoxon_p"] for r in output]);tost_adjusted=holm([r["tost_p"] for r in output])
    for row,p,pt in zip(output,adjusted,tost_adjusted):
        row.update({"wilcoxon_p_holm":float(p),"tost_p_holm":float(pt),"holm_family_tests":len(output),
                    "difference_holm_below_0_05":bool(p<.05),"equivalence_holm_below_0_05":bool(pt<.05)})
    (ROOT/"results/exploratory_statistics.json").write_text(json.dumps(output,indent=2,allow_nan=False)+"\n")
    with (ROOT/"results/exploratory_statistics.csv").open("w",newline="") as file:
        writer=csv.DictWriter(file,fieldnames=list(output[0]));writer.writeheader();writer.writerows(output)
    print(f"Saved {len(output)} retrospective paired comparisons with Holm adjustment; none labeled preregistered.")

if __name__=="__main__":main()
