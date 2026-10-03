"""Create paired bootstrap summaries, publication plots, and LaTeX tables."""
import os
os.environ.setdefault("MPLCONFIGDIR","/workspace/platonic-env/matplotlib")
os.environ.setdefault("XDG_CACHE_HOME","/workspace/platonic-env/cache")
import csv
from collections import defaultdict
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .geometry import SOLIDS, geometry
from .simulator import POLICIES, Simulation, workload
from .benchmark import WORKLOADS

ROOT=Path(__file__).resolve().parents[1]
FIG=ROOT/"paper/figures"
LABEL={"static":"Static","neighbor_push":"Neighbor push","neighbor_steal":"Neighbor steal",
       "global_steal":"Global steal","central_rebalance":"Master rebalance",
       "central_queue":"Master queue (1)","guided_queue":"Guided queue"}
SHORT={"tetrahedron":"Tetra.","cube":"Cube","octahedron":"Octa.","dodecahedron":"Dodeca.","icosahedron":"Icosa."}
COLORS=["#6b7280","#c43c39","#277da8","#6a4c93","#2a9d8f","#cf8b16","#405b31"]
plt.rcParams.update({"font.size":9,"axes.spines.top":False,"axes.spines.right":False,
                     "pdf.fonttype":42,"ps.fonttype":42,"axes.axisbelow":True})

def load(path):
    rows=list(csv.DictReader(open(path)))
    for r in rows:
        for k in ("makespan_ms","utilization","messages","master_messages","bytes","migrated_tasks","lower_bound_ms"):
            r[k]=float(r[k])
        r["seed"]=int(r["seed"])
    return rows

def interval(values):
    v=np.asarray(values,dtype=float)
    rng=np.random.default_rng(192024)
    boots=v[rng.integers(0,len(v),size=(10000,len(v)))].mean(axis=1)
    lo,hi=np.quantile(boots,[.025,.975])
    return float(v.mean()),float(lo),float(hi)

def savefig(fig,name):
    fig.savefig(FIG/(name+".pdf"),bbox_inches="tight")
    fig.savefig(FIG/(name+".png"),dpi=220,bbox_inches="tight")
    plt.close(fig)

def write_csv(path,rows):
    with open(path,"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    FIG.mkdir(parents=True,exist_ok=True)
    rows=load(ROOT/"results/raw.csv")
    groups=defaultdict(list)
    paired=defaultdict(dict)
    for r in rows:
        groups[r["suite"],r["solid"],r["workload"],r["policy"]].append(r)
        paired[r["suite"],r["solid"],r["workload"],r["seed"]][r["policy"]]=r
    summaries=[]
    for (suite,s,w,p),rs in groups.items():
        values=[r["makespan_ms"] for r in rs]
        avg,lo,hi=interval(values)
        speeds=[paired[suite,s,w,r["seed"]]["static"]["makespan_ms"]/r["makespan_ms"] for r in rs]
        speed,slo,shi=interval(speeds)
        summaries.append({"suite":suite,"solid":s,"workload":w,"policy":p,"replicates":len(rs),
                          "mean_ms":avg,"ci_low_ms":lo,"ci_high_ms":hi,
                          "mean_paired_speedup":speed,"speedup_ci_low":slo,"speedup_ci_high":shi,
                          **{"mean_"+k:float(np.mean([r[k] for r in rs])) for k in ("utilization","messages","master_messages","bytes","migrated_tasks")}})
    write_csv(ROOT/"results/summary.csv",summaries)
    lookup={(r["suite"],r["solid"],r["workload"],r["policy"]):r for r in summaries}

    # All five actual solid geometries and central spokes.
    fig=plt.figure(figsize=(11,2.4))
    for index,s in enumerate(SOLIDS):
        ax=fig.add_subplot(1,5,index+1,projection="3d")
        vertices,edges,_=geometry(s)
        for a,b in edges:
            v=vertices[[a,b]]; ax.plot(*v.T,color="#277da8",lw=1.1)
        for v in vertices: ax.plot(*np.array([[0,0,0],v]).T,color="0.75",lw=.5,alpha=.6)
        ax.scatter(*vertices.T,c="#277da8",s=14);ax.scatter(0,0,0,c="#c43c39",s=28)
        ax.set_title(f"{s.title()}\n{len(vertices)} workers, {len(edges)} peer links",fontsize=8)
        ax.set_axis_off();ax.set_box_aspect((1,1,1))
    fig.subplots_adjust(wspace=0)
    savefig(fig,"solids")

    # Primary raw milliseconds; topology sizes cannot be compared as equal-N.
    fig,axs=plt.subplots(2,3,figsize=(10.5,6.2)); x=np.arange(5); width=.11
    for ax,w in zip(axs.flat,WORKLOADS):
        for index,p in enumerate(POLICIES):
            vals=[lookup["main",s,w,p] for s in SOLIDS]
            means=np.array([r["mean_ms"] for r in vals])
            err=np.array([[r["mean_ms"]-r["ci_low_ms"] for r in vals],[r["ci_high_ms"]-r["mean_ms"] for r in vals]])
            ax.bar(x+(index-3)*width,means,width,yerr=err,color=COLORS[index],label=LABEL[p],capsize=1)
        ax.set_title(w.title());ax.set_xticks(x,[SHORT[s] for s in SOLIDS]);ax.set_ylabel("Makespan (ms)")
        ax.grid(axis="y",alpha=.2)
    axs.flat[-1].axis("off")
    handles,labels=axs.flat[0].get_legend_handles_labels()
    axs.flat[-1].legend(handles,labels,loc="center",frameon=False)
    fig.tight_layout();savefig(fig,"makespans")

    # Proposed/static and proposed/neighbor-steal paired effects, with intervals.
    effects=[]
    fig,axs=plt.subplots(1,2,figsize=(10,4.2))
    for ax,comp in zip(axs,("static","neighbor_steal")):
        a=np.empty((5,5)); texts={}
        for i,w in enumerate(WORKLOADS):
            for j,s in enumerate(SOLIDS):
                values=[v[comp]["makespan_ms"]/v["neighbor_push"]["makespan_ms"] for (suite,so,wo,_),v in paired.items() if suite=="main" and so==s and wo==w]
                mean,lo,hi=interval(values);a[i,j]=mean
                effects.append({"solid":s,"workload":w,"comparator":comp,"ratio":mean,"ci_low":lo,"ci_high":hi})
                texts[i,j]=f"{mean:.3f}"
        ax.imshow(a,cmap="YlOrRd" if comp=="static" else "RdBu",vmin=1 if comp=="static" else .97,vmax=5.8 if comp=="static" else 1.03)
        for (i,j),txt in texts.items():ax.text(j,i,txt,ha="center",va="center",fontsize=11,color="black")
        ax.set_xticks(range(5),[SHORT[s] for s in SOLIDS]);ax.set_yticks(range(5),[w.title() for w in WORKLOADS])
        ax.set_title(f"{LABEL[comp]} / neighbor push\nMean paired ratio (CI in companion CSV)",fontsize=10)
    fig.tight_layout();savefig(fig,"paired_effects")
    write_csv(ROOT/"results/paired_effects.csv",effects)

    # Illustrative exact execution trace, separate from benchmark measurements.
    fig,axs=plt.subplots(2,1,figsize=(8,4.5),sharex=True)
    for ax,p in zip(axs,("static","neighbor_push")):
        sim=Simulation("icosahedron",p,workload("clustered",240,2),70003,audit=True)
        result=sim.run(); starts={}
        for at,action,task,node in sim.trace:
            if action=="start":starts[task]=at
            else:ax.broken_barh([(starts[task],at-starts[task])],(node-.35,.7),facecolors=plt.cm.tab20((task//20)/12),edgecolor="white",linewidth=.15)
        ax.axvline(result["makespan_ms"],color="black",ls="--",lw=1)
        ax.set_yticks([0,3,6,9,11]);ax.set_ylabel("Worker ID")
        ax.set_title(f"{LABEL[p]}: last result at {result['makespan_ms']:.2f} ms",fontsize=10)
    axs[-1].set_xlabel("Simulation time (ms); colors identify original equal-count chunks")
    fig.tight_layout();savefig(fig,"timeline")

    # Sensitivity compares exactly the same 15 seeds for the baseline.
    fig,axs=plt.subplots(1,2,figsize=(10,3.3))
    for ax,s in zip(axs,("icosahedron","dodecahedron")):
        for p in POLICIES[1:]:
            vals=[]
            for suite in ("latency_0.001","main","latency_0.1","latency_1.0"):
                rs=groups[suite,s,"clustered",p]
                vals.append(np.mean([r["makespan_ms"] for r in rs if r["seed"]<15]))
            ax.plot([.001,.01,.1,1],vals,"o-",label=LABEL[p],color=COLORS[POLICIES.index(p)],ms=4)
        ax.set_xscale("log");ax.set_title(s.title()+", clustered");ax.set_xlabel("Fixed one-way link latency (ms)")
        ax.set_ylabel("Mean makespan (ms)");ax.grid(alpha=.2)
    handles,labels=axs[0].get_legend_handles_labels();fig.legend(handles,labels,loc="upper center",ncol=3,bbox_to_anchor=(.5,1.13),frameon=False)
    fig.tight_layout();savefig(fig,"latency")

    fig,axs=plt.subplots(1,2,figsize=(10,3.3))
    for ax,s in zip(axs,("icosahedron","dodecahedron")):
        labels=["Independent links","Shared NIC","Master service","Both"]
        for index,p in enumerate(POLICIES[1:]):
            suites=["main","shared_nic","master_service","shared_nic_master"]
            vals=[np.mean([r["makespan_ms"] for r in groups[su,s,"clustered",p] if r["seed"]<15]) for su in suites]
            ax.bar(np.arange(4)+(index-2.5)*.13,vals,.13,label=LABEL[p],color=COLORS[index+1])
        ax.set_xticks(range(4),labels,fontsize=8);ax.set_title(s.title()+", clustered")
        ax.set_ylabel("Mean makespan (ms)");ax.grid(axis="y",alpha=.2)
    handles,labels=axs[0].get_legend_handles_labels();fig.legend(handles,labels,loc="upper center",ncol=3,bbox_to_anchor=(.5,1.13),frameon=False)
    fig.tight_layout();savefig(fig,"bottlenecks")

    # Master physical-hop traffic includes result collection in every policy.
    fig,axs=plt.subplots(1,2,figsize=(10,3.3))
    for ax,metric in zip(axs,("mean_master_messages","mean_migrated_tasks")):
        for index,p in enumerate(POLICIES):
            vals=[lookup["main",s,"clustered",p][metric] for s in SOLIDS]
            ax.bar(x+(index-3)*width,vals,width,color=COLORS[index],label=LABEL[p])
        ax.set_xticks(x,[SHORT[s] for s in SOLIDS]);ax.grid(axis="y",alpha=.2)
        ax.set_ylabel("Master link message hops" if "master" in metric else "Migrated task transmissions")
    handles,labels=axs[0].get_legend_handles_labels();fig.legend(handles,labels,loc="upper center",ncol=4,bbox_to_anchor=(.5,1.14),frameon=False)
    fig.tight_layout();savefig(fig,"traffic")

    topology_rows=load(ROOT/"results/topology.csv")
    tg=defaultdict(list)
    tp={}
    for r in topology_rows:
        tg[r["solid"],r["workload"],r["policy"],r["topology"]].append(r)
        tp[r["solid"],r["workload"],r["policy"],r["topology"],r["seed"]]=r
    topology_summary=[]
    for (s,w,p,t),rs in tg.items():
        ratios=[paired["main",s,w,r["seed"]][p]["makespan_ms"]/r["makespan_ms"] for r in rs]
        ratio,lo,hi=interval(ratios)
        avg,alo,ahi=interval([r["makespan_ms"] for r in rs])
        topology_summary.append({"solid":s,"workload":w,"policy":p,"topology":t,"mean_ms":avg,
                                "ci_low_ms":alo,"ci_high_ms":ahi,"platonic_over_control":ratio,"ratio_ci_low":lo,"ratio_ci_high":hi,
                                "peer_links":rs[0]["peer_links"]})
    write_csv(ROOT/"results/topology_summary.csv",topology_summary)
    ts={(r["solid"],r["workload"],r["policy"],r["topology"]):r for r in topology_summary}
    topologies=("star","ring","grid","random_regular","platonic","complete")
    fig,axs=plt.subplots(1,3,figsize=(10.5,3.5))
    for ax,w in zip(axs,("lognormal","pareto","clustered")):
        for index,t in enumerate(topologies):
            vals=[lookup["main",s,w,"neighbor_push"]["mean_ms"] if t=="platonic" else ts[s,w,"neighbor_push",t]["mean_ms"] for s in SOLIDS]
            ax.bar(x+(index-2.5)*.13,vals,.13,label=t.replace("_"," ").title(),color=(COLORS[1] if t=="platonic" else ["#999999","#72a3c0","#73b79f","#d6ae64","#c43c39","#9476b2"][index]))
        ax.set_title(w.title()+", neighbor push");ax.set_xticks(x,[SHORT[s] for s in SOLIDS],fontsize=8)
        ax.set_ylabel("Mean makespan (ms)");ax.grid(axis="y",alpha=.2)
    handles,labels=axs[0].get_legend_handles_labels();fig.legend(handles,labels,loc="upper center",ncol=6,bbox_to_anchor=(.5,1.08),frameon=False)
    fig.tight_layout();savefig(fig,"topologies")

    table=[r"\begin{tabular}{llrrrrrrr}",r"\toprule",r"Workload & Solid & Static & Push & N. steal & G. steal & Rebalance & Queue (1) & Guided \\",r"\midrule"]
    for w in WORKLOADS:
        for s in SOLIDS:
            vals=[lookup["main",s,w,p]["mean_ms"] for p in POLICIES]
            best=min(vals)
            cells=[f"{v:.2f}" for v in vals]
            table.append(w.title()+" & "+SHORT[s]+" & "+" & ".join(cells)+r" \\")
        table.append(r"\midrule")
    table += [r"\bottomrule",r"\end{tabular}"]
    (ROOT/"paper/results_table.tex").write_text("\n".join(table)+"\n")
    effect_table=[r"\begin{tabular}{lrr}",r"\toprule",r"Solid & IID lognormal & Clustered \\",r"\midrule"]
    for s in SOLIDS:
        cells=[]
        for w in ("lognormal","clustered"):
            e=next(r for r in effects if r["solid"]==s and r["workload"]==w and r["comparator"]=="static")
            cells.append(f"{e['ratio']:.3f} [{e['ci_low']:.3f}, {e['ci_high']:.3f}]")
        effect_table.append(SHORT[s]+" & "+" & ".join(cells)+r" \\")
    effect_table += [r"\bottomrule",r"\end{tabular}"]
    (ROOT/"paper/effects_table.tex").write_text("\n".join(effect_table)+"\n")
    wins=sum(lookup["main",s,w,"neighbor_push"]["mean_ms"]==min(lookup["main",s,w,p]["mean_ms"] for p in POLICIES) for s in SOLIDS for w in WORKLOADS if w!="constant")
    report={"primary_cells":25,"variable_cost_cells":20,"push_lowest_mean_variable_cells":wins,
            "total_runs":len(rows)+len(topology_rows),"tests_expected":116,
            "proposed_effects":effects,"topology_effects":topology_summary}
    (ROOT/"results/findings.json").write_text(json.dumps(report,indent=2)+"\n")
    print(f"Analyzed {len(rows)+len(topology_rows)} runs; created 8 figure pairs and tables.")
    print(f"Neighbor push has the lowest mean in {wins}/20 variable-cost cells (descriptive, not significance tests).")

if __name__=="__main__":main()
