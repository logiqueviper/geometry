"""Publication graphics generated only from saved observations and graph data.

Figures are 7.16 inches wide, use >=8 pt text and an Okabe--Ito policy palette.
Legacy observations remain exploratory. No missing experiment is interpolated.
"""
import os
os.environ.setdefault("MPLCONFIGDIR","/workspace/platonic-env/matplotlib")
os.environ.setdefault("XDG_CACHE_HOME","/workspace/platonic-env/cache")
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path
import csv
import hashlib
import json
import textwrap
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D
from matplotlib.colors import TwoSlopeNorm
from study.geometry import SOLIDS,geometry
from study.simulator import POLICIES,Simulation,workload,Config
from study.benchmark import WORKLOADS
from study.analyze import interval

ROOT=Path(__file__).resolve().parents[1]
FIG=ROOT/"paper/figures"
VIS=ROOT/"visualizations"
ORDER=tuple(sorted(SOLIDS,key=lambda s:SOLIDS[s][0]))
LABEL={"static":"Static","neighbor_push":"Neighbor push","neighbor_steal":"Neighbor steal",
       "global_steal":"Global steal","central_rebalance":"Master rebalance",
       "central_queue":"Master queue (1)","guided_queue":"Guided queue"}
COLOR=dict(zip(POLICIES,["#66717A","#D55E00","#0072B2","#009E73","#CC79A7","#E69F00","#56B4E9"]))
MARKER=dict(zip(POLICIES,["o","s","^","D","P","v","X"]))
LINE=dict(zip(POLICIES,["-","-","--","-.",":","--","-."]))
SHORT={"tetrahedron":"T4","octahedron":"O6","cube":"C8","icosahedron":"I12","dodecahedron":"D20"}
INK="#182A3A"; GRID="#E3E8ED"; BLUE="#0072B2"; ORANGE="#D55E00"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":8,"axes.labelsize":8,
    "axes.titlesize":10,"xtick.labelsize":8,"ytick.labelsize":8,"legend.fontsize":8,
    "text.color":INK,"axes.labelcolor":INK,"xtick.color":INK,"ytick.color":INK,
    "axes.edgecolor":"#A7B3BE","axes.spines.top":False,"axes.spines.right":False,
    "axes.axisbelow":True,"grid.color":GRID,"grid.linewidth":.6,
    "pdf.fonttype":42,"ps.fonttype":42,"svg.fonttype":"none","figure.facecolor":"white",
    "savefig.facecolor":"white","lines.linewidth":1.3})

def load(path):return list(csv.DictReader(path.open()))
def key(*args):return "|".join(args)
def summary(values):
    avg,lo,hi=interval(values)
    return {"mean":avg,"lo":lo,"hi":hi,"median":float(np.median(values)),
            "q25":float(np.quantile(values,.25)),"q75":float(np.quantile(values,.75))}

def prepare_data():
    raw=load(ROOT/"results/raw.csv");top=load(ROOT/"results/topology.csv")
    grouped=defaultdict(list);cases=defaultdict(dict)
    for row in raw:
        grouped[key(row["suite"],row["solid"],row["workload"],row["policy"])].append(row)
        cases[row["suite"],row["solid"],row["workload"],int(row["seed"])][row["policy"]]=row
    data={"metadata":{"evidence":"simulation","phase":"legacy exploratory; not preregistered",
        "primary_runs":sum(r["suite"]=="main" for r in raw),"sensitivity_runs":sum(r["suite"]!="main" for r in raw),
        "topology_runs":len(top),"total_runs":len(raw)+len(top),"ci":"10000 percentile bootstrap resamples; exploratory cell-wise 95%; uncorrected",
        "bootstrap_seed":192024,"source_sha256":{n:hashlib.sha256((ROOT/"results"/n).read_bytes()).hexdigest() for n in ("raw.csv","topology.csv")},
        "primary_config":asdict(Config()),"policy_colors":COLOR},"groups":{},"effects":{},"topologies":{},"traces":{},"graphs":[]}
    selected=("main","latency_0.001","latency_0.1","latency_1.0","shared_nic","master_service","shared_nic_master")
    for group,rs in grouped.items():
        suite,s,w,p=group.split("|")
        if suite not in selected:continue
        for version,subset in ((suite,rs),("main15",[r for r in rs if int(r["seed"])<15])) if suite=="main" else ((suite,rs),):
            subset=sorted(subset,key=lambda r:int(r["seed"]))
            entry={"seeds":[int(r["seed"]) for r in subset],"n":len(subset)}
            for metric in ("makespan_ms","master_messages","migrated_tasks","bytes","messages","utilization"):
                values=[float(r[metric]) for r in subset]
                entry[metric]={"values":values,**summary(values)}
            ratios=[float(r["makespan_ms"])/float(cases[suite,s,w,int(r["seed"])]["static"]["makespan_ms"]) for r in subset]
            entry["time_over_static"]={"values":ratios,**summary(ratios)}
            data["groups"][key(version,s,w,p)]=entry
    for s in SOLIDS:
        for w in WORKLOADS:
            for comparator in ("static","neighbor_steal"):
                values=[float(cases["main",s,w,seed][comparator]["makespan_ms"])/float(cases["main",s,w,seed]["neighbor_push"]["makespan_ms"]) for seed in range(30)]
                data["effects"][key(s,w,comparator)]={"values":values,"seeds":list(range(30)),**summary(values)}
    for s in SOLIDS:
        for w in ("lognormal","pareto","clustered"):
            for t in ("star","ring","grid","random_regular","complete"):
                rs=sorted([r for r in top if r["solid"]==s and r["workload"]==w and r["policy"]=="neighbor_push" and r["topology"]==t],key=lambda r:int(r["seed"]))
                ratios=[float(cases["main",s,w,int(r["seed"])]["neighbor_push"]["makespan_ms"])/float(r["makespan_ms"]) for r in rs]
                data["topologies"][key(s,w,t)]={"values":ratios,"seeds":[int(r["seed"]) for r in rs],
                    "peer_links":int(rs[0]["peer_links"]),"n":len(rs),**summary(ratios)}
    for p in ("static","neighbor_push"):
        sim=Simulation("icosahedron",p,workload("clustered",240,2),70003,audit=True)
        result=sim.run()
        data["traces"][p]={"config":asdict(Config()),"solid":"icosahedron","tasks":240,"seed":2,
            "evidence":"simulation illustration; outside the 16050 benchmark runs","result":result,
            "events":[[float(at),event,int(task),int(node)] for at,event,task,node in sim.trace]}
    graph_path=ROOT/"results/graph_metrics.json"
    if graph_path.exists():data["graphs"]=json.loads(graph_path.read_text())
    path=ROOT/"results/visual_data.json"
    path.write_text(json.dumps(data,separators=(",",":"),allow_nan=False)+"\n")
    return json.loads(path.read_text())  # draw from the saved artifact, not hidden state

class Renderer:
    def __init__(self,data):
        self.data=data;self.inventory=[]
        FIG.mkdir(parents=True,exist_ok=True);VIS.mkdir(exist_ok=True)
        self.atlas=PdfPages(VIS/"visual-atlas.pdf",metadata={"Title":"Platonic cluster study: exploratory visual atlas","Author":"Study artifact"})

    def entry(self,s,w,p,suite="main",metric="makespan_ms"):
        return self.data["groups"][key(suite,s,w,p)][metric]

    def decorate(self,fig,title,caption,evidence="EXPLORATORY SIMULATION",legend=False):
        fig.text(.045,.976,evidence,ha="left",va="top",fontsize=8,fontweight="bold",color=ORANGE)
        # Wrap by rendered width rather than character count, keeping headings
        # inside a fixed journal-width canvas without reducing font size.
        from matplotlib.font_manager import FontProperties
        renderer=fig.canvas.get_renderer()
        font=FontProperties(size=12,weight="bold")
        lines=[];line=""
        for word in title.split():
            trial=(line+" "+word).strip()
            if line and renderer.get_text_width_height_descent(trial,font,False)[0] > fig.bbox.width*.90:
                lines.append(line);line=word
            else:line=trial
        lines.append(line)
        fig.text(.045,.935,"\n".join(lines),ha="left",va="top",fontsize=12,fontweight="bold",color=INK,linespacing=1.1)
        text="\n".join(textwrap.wrap(caption,width=105))
        fig.text(.045,.025,text,ha="left",va="bottom",fontsize=8,color="#526474",linespacing=1.3)
        if legend:
            handles=[Line2D([],[],color=COLOR[p],marker=MARKER[p],ls=LINE[p],label=LABEL[p],ms=4) for p in POLICIES]
            fig.legend(handles=handles,loc="lower center",bbox_to_anchor=(.5,.11),ncol=4,frameon=False,columnspacing=1.0,handlelength=1.5)
        fig.subplots_adjust(left=.10,right=.97,top=.83,bottom=.24 if legend else .19,wspace=.28,hspace=.43)

    def finish(self,fig,name,title,caption):
        for artist in fig.findobj(matplotlib.text.Text):
            if artist.get_text():
                assert artist.get_fontsize()>=8,(name,artist.get_text(),artist.get_fontsize())
                # IEEEtran's text width is slightly narrower than 7.16 inches.
                # This allowance keeps included figure text above eight points.
                artist.set_fontsize(max(8.2,artist.get_fontsize()))
        fig.canvas.draw()
        renderer=fig.canvas.get_renderer()
        # Matplotlib creates labels outside view limits but does not draw them.
        # Do not misreport those unused ticks as clipping in the exported PDF.
        unused_tick_labels=set()
        for ax in fig.axes:
            for axis in (ax.xaxis,ax.yaxis):
                lo,hi=sorted(axis.get_view_interval())
                for tick in axis.get_major_ticks()+axis.get_minor_ticks():
                    if not lo-1e-12 <= tick.get_loc() <= hi+1e-12:
                        unused_tick_labels.update((tick.label1,tick.label2))
        outside=[]
        for artist in fig.findobj(matplotlib.text.Text):
            if not artist.get_visible() or not artist.get_text() or artist in unused_tick_labels:continue
            box=artist.get_window_extent(renderer)
            if box.x0 < -1 or box.y0 < -1 or box.x1 > fig.bbox.width+1 or box.y1 > fig.bbox.height+1:
                outside.append({"text":artist.get_text(),"bounds":[float(v) for v in box.bounds]})
        if outside:print("Text layout diagnostics:",name,outside,flush=True)
        metadata={"Title":title,"Subject":caption,"Author":"Reproducible study visualization","Keywords":"exploratory simulation; no hardware evidence"}
        fig.savefig(FIG/(name+".pdf"),metadata=metadata)
        fig.savefig(FIG/(name+".png"),dpi=300)
        fig.savefig(FIG/(name+".svg"))
        self.atlas.savefig(fig)
        self.inventory.append({"name":name,"title":title,"caption":caption,"width_inches":float(fig.get_figwidth()),
            "height_inches":float(fig.get_figheight()),"minimum_font_points":8.2,"text_outside_canvas":outside,"formats":["pdf","png","svg"],
            "source":"results/visual_data.json","phase":"exploratory legacy data"})
        plt.close(fig)

    def geometries(self):
        title="Five solids. One master. Only edge-adjacent peers."
        caption="Concept diagram: a red central master connects to every blue worker; dark peer links follow solid edges. N is the worker count and d is peer degree. Geometry specifies adjacency; all modeled links have equal bandwidth and latency."
        fig=plt.figure(figsize=(7.16,2.9))
        for i,s in enumerate(ORDER):
            ax=fig.add_subplot(1,5,i+1,projection="3d");v,e,_=geometry(s)
            for a,b in e:ax.plot(*v[[a,b]].T,color=BLUE,lw=1.15,alpha=.8)
            for p in v:ax.plot(*np.array([[0,0,0],p]).T,color="#9AA9B8",lw=.6,alpha=.45)
            ax.scatter(*v.T,s=16,c=BLUE,edgecolors="white",linewidths=.4,depthshade=False)
            ax.scatter(0,0,0,s=36,c=ORANGE,edgecolors="white",linewidths=.7,depthshade=False)
            ax.set_title(s.title()+f"\nN={len(v)} · d={SOLIDS[s][2]}",fontsize=8,pad=1)
            ax.set_axis_off();ax.set_box_aspect((1,1,1));ax.view_init(elev=18,azim=35)
        self.decorate(fig,title,caption,evidence="SYSTEM DIAGRAM")
        fig.subplots_adjust(left=.02,right=.98,wspace=0,top=.78,bottom=.20)
        self.finish(fig,"solids",title,caption)

    def makespans(self):
        title="Redistribution helps imbalance; dynamic policies often overlap."
        caption="Last-result makespan, 2400 tasks, five solids and seven policies; 30 paired seeds per cell. Markers are means; horizontal bars are uncorrected 95% percentile-bootstrap intervals. Each worker count has its own physical network."
        fig,axes=plt.subplots(2,3,figsize=(7.16,6.4))
        for ax,w in zip(axes.flat,WORKLOADS):
            for j,p in enumerate(POLICIES):
                entries=[self.entry(s,w,p) for s in ORDER]
                y=np.arange(5)+(j-3)*.095
                mean=np.array([v["mean"] for v in entries]);lo=np.array([v["lo"] for v in entries]);hi=np.array([v["hi"] for v in entries])
                ax.errorbar(mean,y,xerr=[mean-lo,hi-mean],fmt=MARKER[p],ms=3.3,color=COLOR[p],lw=.9,capsize=1.2,label=LABEL[p])
            ax.set_yticks(range(5),[SHORT[s] for s in ORDER]);ax.invert_yaxis()
            ax.set_title(w.title(),loc="left");ax.set_xlabel("Makespan (ms)");ax.grid(axis="x")
            ax.tick_params(axis="y",length=0);ax.set_xlim(left=0)
            ax.locator_params(axis="x",nbins=3)
        axes.flat[-1].axis("off")
        handles=[Line2D([],[],marker=MARKER[p],color=COLOR[p],ls="",ms=5,label=LABEL[p]) for p in POLICIES]
        axes.flat[-1].legend(handles=handles,loc="center",frameon=False)
        self.decorate(fig,title,caption);fig.subplots_adjust(bottom=.14,top=.85,wspace=.47,hspace=.42)
        self.finish(fig,"makespans",title,caption)

    def effects_heatmap(self):
        title="Large gains over static do not establish a push advantage."
        caption="Mean paired makespan ratios from 30 seeds per cell; values above one favor neighbor push. Left: static/push. Right: neighbor-steal/push. Exact 95% intervals appear in paired_effects.csv and the companion interval plot. No equivalence claim is made."
        fig,axes=plt.subplots(1,2,figsize=(7.16,4.1))
        for ax,comparator in zip(axes,("static","neighbor_steal")):
            a=np.array([[self.data["effects"][key(s,w,comparator)]["mean"] for s in ORDER] for w in WORKLOADS])
            image=ax.imshow(a,cmap="YlOrBr" if comparator=="static" else "BrBG",vmin=1 if comparator=="static" else .97,vmax=5.8 if comparator=="static" else 1.03,aspect="auto")
            for i in range(5):
                for j in range(5):ax.text(j,i,f"{a[i,j]:.3f}",ha="center",va="center",fontsize=8,color="white" if comparator=="static" and a[i,j]>4.1 else INK)
            ax.set_xticks(range(5),[SHORT[s] for s in ORDER]);ax.set_yticks(range(5),[w.title() for w in WORKLOADS])
            ax.set_title("Static / push" if comparator=="static" else "Neighbor steal / push",loc="left")
            ax.tick_params(length=0);fig.colorbar(image,ax=ax,fraction=.045,pad=.03,shrink=.85)
        self.decorate(fig,title,caption);fig.subplots_adjust(left=.14,right=.90,wspace=.60,top=.82,bottom=.24)
        self.finish(fig,"paired_effects",title,caption)

    def effect_intervals(self):
        title="Show the effect and its uncertainty, including null results."
        caption="Mean paired ratios and uncorrected 95% bootstrap intervals, 30 seeds per solid. Dashed lines denote equal makespan. Lognormal is an independent-cost workload; clustered is a sorted-cost stress test. Interval overlap with one does not demonstrate equivalence."
        fig,axes=plt.subplots(2,2,figsize=(7.16,5.8))
        for row,comp in enumerate(("static","neighbor_steal")):
            for col,w in enumerate(("lognormal","clustered")):
                ax=axes[row,col];entries=[self.data["effects"][key(s,w,comp)] for s in ORDER]
                mean=np.array([e["mean"] for e in entries]);lo=np.array([e["lo"] for e in entries]);hi=np.array([e["hi"] for e in entries])
                ax.axvline(1,color="#7B8792",ls="--",lw=1)
                ax.errorbar(mean,np.arange(5),xerr=[mean-lo,hi-mean],fmt="s",ms=5,color=ORANGE,lw=1.6,capsize=3)
                ax.set_yticks(range(5),[s.title() for s in ORDER]);ax.invert_yaxis();ax.grid(axis="x")
                ax.set_title(("Static / push" if comp=="static" else "Neighbor steal / push")+" · "+w.title(),loc="left")
                ax.set_xlabel("Paired makespan ratio")
                if comp=="neighbor_steal":ax.set_xlim(.95,1.05)
                elif w=="lognormal":ax.set_xlim(.98,1.30)
                else:ax.set_xlim(.9,6.1)
        self.decorate(fig,title,caption);fig.subplots_adjust(left=.18,right=.98,wspace=.68,bottom=.18,top=.83,hspace=.63)
        self.finish(fig,"effect_intervals",title,caption)

    def latency(self):
        title="Fixed latency changes the scheduler tradeoff."
        caption="Clustered workload, 2400 tasks, 100 MiB/s; identical 15-seed subsets at every point. Lines show means; shaded bands show uncorrected 95% bootstrap intervals. Markers and line styles distinguish six dynamic policies. This is a latency sweep, not a full latency-by-bandwidth grid."
        fig,axes=plt.subplots(1,2,figsize=(7.16,4.0))
        suites=("latency_0.001","main15","latency_0.1","latency_1.0");x=np.array([.001,.01,.1,1.])
        for ax,s in zip(axes,("icosahedron","dodecahedron")):
            for p in POLICIES[1:]:
                entries=[self.entry(s,"clustered",p,suite) for suite in suites]
                mean=[e["mean"] for e in entries]
                ax.fill_between(x,[e["lo"] for e in entries],[e["hi"] for e in entries],color=COLOR[p],alpha=.10,lw=0)
                ax.plot(x,mean,color=COLOR[p],marker=MARKER[p],ls=LINE[p],ms=4,label=LABEL[p])
            ax.set_xscale("log");ax.set_title(s.title()+f" · {SOLIDS[s][0]} workers",loc="left")
            ax.set_xlabel("One-way link latency (ms)");ax.set_ylabel("Mean makespan (ms)");ax.grid(alpha=.7)
        self.decorate(fig,title,caption,legend=True);fig.subplots_adjust(left=.10,wspace=.33,bottom=.35,top=.79)
        self.finish(fig,"latency",title,caption)

    def bottlenecks(self):
        title="Independent links and a shared NIC are different regimes."
        caption="Clustered workload; the same 15 seeds in all four conditions. Points are means; bars are uncorrected 95% bootstrap intervals. Shared NICs serialize endpoint traffic. Master service adds 10 microseconds per incoming physical-hop message; 'Both' includes both constraints."
        fig,axes=plt.subplots(1,2,figsize=(7.16,4.2))
        suites=("main15","shared_nic","master_service","shared_nic_master")
        for ax,s in zip(axes,("icosahedron","dodecahedron")):
            for j,p in enumerate(POLICIES[1:]):
                es=[self.entry(s,"clustered",p,suite) for suite in suites]
                mean=np.array([e["mean"] for e in es]);lo=np.array([e["lo"] for e in es]);hi=np.array([e["hi"] for e in es])
                ax.errorbar(mean,np.arange(4)+(j-2.5)*.10,xerr=[mean-lo,hi-mean],fmt=MARKER[p],color=COLOR[p],ms=4,lw=1,capsize=1.5)
            ax.set_yticks(range(4),["Independent","Shared NIC","Master service","Both"]);ax.invert_yaxis()
            ax.set_title(s.title(),loc="left");ax.set_xlabel("Makespan (ms)");ax.grid(axis="x");ax.tick_params(axis="y",length=0)
        self.decorate(fig,title,caption,legend=True);fig.subplots_adjust(left=.16,right=.98,wspace=.65,bottom=.34,top=.80)
        self.finish(fig,"bottlenecks",title,caption)

    def traffic(self):
        title="Local redistribution avoids extra master hops, not migration cost."
        caption="Clustered workload; 30 paired seeds. Means and uncorrected 95% bootstrap intervals. Master hops count initial transfers and all identified results. Migrations count transmissions, so the same ID can contribute repeatedly. Traffic includes control packets dispatched before the last-result stop."
        fig,axes=plt.subplots(1,2,figsize=(7.16,4.3))
        for ax,metric in zip(axes,("master_messages","migrated_tasks")):
            for j,p in enumerate(POLICIES):
                es=[self.entry(s,"clustered",p,metric=metric) for s in ORDER]
                mean=np.array([e["mean"] for e in es]);lo=np.array([e["lo"] for e in es]);hi=np.array([e["hi"] for e in es])
                ax.errorbar(mean,np.arange(5)+(j-3)*.085,xerr=[mean-lo,hi-mean],fmt=MARKER[p],color=COLOR[p],ms=3.5,lw=1,capsize=1.4)
            ax.set_yticks(range(5),[SHORT[s] for s in ORDER]);ax.invert_yaxis();ax.grid(axis="x");ax.set_xlim(left=0)
            ax.set_title("Master traffic" if metric=="master_messages" else "Redistributed tasks",loc="left")
            ax.set_xlabel("Physical message hops" if metric=="master_messages" else "Task transmissions")
            ax.locator_params(axis="x",nbins=4)
        self.decorate(fig,title,caption,legend=True);fig.subplots_adjust(left=.10,right=.97,wspace=.35,bottom=.33,top=.80)
        self.finish(fig,"traffic",title,caption)

    def topologies(self):
        title="Compare peer topologies at the same worker count."
        caption="Neighbor push: mean paired Platonic/control makespan ratio, 30 joint graph/workload draws per cell. Below one favors Platonic connectivity. Only rewired controls preserve degree and peer-link count; the other rows have different link budgets. Color is clipped at +/-0.5 log2 units; labels give exact ratios."
        fig,axes=plt.subplots(1,3,figsize=(7.16,4.2))
        topologies=("star","ring","grid","random_regular","complete")
        image=None
        for ax,w in zip(axes,("lognormal","pareto","clustered")):
            a=np.array([[self.data["topologies"][key(s,w,t)]["mean"] for s in ORDER] for t in topologies])
            image=ax.imshow(np.log2(a),cmap="PuOr",norm=TwoSlopeNorm(vmin=-.5,vcenter=0,vmax=.5),aspect="auto")
            for i in range(5):
                for j in range(5):ax.text(j,i,f"{a[i,j]:.3f}",ha="center",va="center",fontsize=8,color="white" if abs(np.log2(a[i,j]))>.34 else INK)
            ax.set_xticks(range(5),[SHORT[s] for s in ORDER]);ax.set_yticks(range(5),["Star","Ring","Grid","Rewired","Complete"] if ax==axes[0] else [])
            ax.set_title(w.title(),loc="left");ax.tick_params(length=0)
        self.decorate(fig,title,caption);fig.subplots_adjust(left=.12,right=.92,wspace=.16,bottom=.32,top=.80)
        cax=fig.add_axes([.31,.22,.42,.025]);bar=fig.colorbar(image,cax=cax,orientation="horizontal",ticks=[-.5,0,.5]);bar.set_label("log2(Platonic / control)",fontsize=8)
        self.finish(fig,"topologies",title,caption)

    def distributions(self):
        title="Keep every seed visible, not just the average."
        caption="Clustered workload; six dynamic schedulers, 30 paired seeds each. Every dot is one instance's time/static-time ratio. Violin shapes show the observed distribution; bold segments mark the interquartile range and white dots the median. Static is the reference, not a plotted competitor."
        fig,axes=plt.subplots(1,2,figsize=(7.16,4.5))
        for ax,s in zip(axes,("icosahedron","dodecahedron")):
            for i,p in enumerate(POLICIES[1:]):
                e=self.entry(s,"clustered",p,metric="time_over_static");values=np.array(e["values"])
                if np.ptp(values)>1e-10:
                    v=ax.violinplot([values],positions=[i],vert=False,widths=.65,showextrema=False)
                    for body in v["bodies"]:body.set_facecolor(COLOR[p]);body.set_edgecolor("none");body.set_alpha(.18)
                jitter=(np.random.default_rng(8000+i).random(len(values))-.5)*.4
                ax.scatter(values,i+jitter,s=10,c=COLOR[p],alpha=.6,edgecolors="none",zorder=2)
                ax.plot([e["q25"],e["q75"]],[i,i],color=COLOR[p],lw=3,zorder=3)
                ax.scatter([e["median"]],[i],c="white",edgecolors=COLOR[p],s=25,zorder=4)
            ax.set_yticks(range(6),[LABEL[p] for p in POLICIES[1:]] if ax==axes[0] else []);ax.invert_yaxis()
            ax.set_title(s.title(),loc="left");ax.grid(axis="x");ax.set_xlabel("Time / static time · lower is better")
        self.decorate(fig,title,caption);fig.subplots_adjust(left=.24,right=.97,wspace=.20,top=.80,bottom=.22)
        self.finish(fig,"seed_distributions",title,caption)

    def rewirings(self):
        title="Degree-matched rewiring gives a more demanding control."
        caption="Neighbor push, 30 joint graph/workload draws per cell. Dots are paired percentage improvements, 100*(1-T_Platonic/T_rewired); positive values favor Platonic. Diamonds and bars show means and uncorrected 95% bootstrap intervals. Tetrahedral and octahedral rewiring is topologically equivalent up to labels."
        fig,axes=plt.subplots(1,3,figsize=(7.16,4.5))
        for ax,w in zip(axes,("lognormal","pareto","clustered")):
            for i,s in enumerate(ORDER):
                e=self.data["topologies"][key(s,w,"random_regular")];values=100*(1-np.array(e["values"]))
                jitter=(np.random.default_rng(11000+i).random(len(values))-.5)*.38
                ax.scatter(i+jitter,values,s=9,c=BLUE,alpha=.32,edgecolors="none")
                mean=100*(1-e["mean"]);lo=100*(1-e["hi"]);hi=100*(1-e["lo"])
                ax.errorbar(i,mean,yerr=[[mean-lo],[hi-mean]],fmt="D",color=ORANGE,ms=4,lw=1.4,capsize=3)
            ax.axhline(0,color="#7B8792",ls="--",lw=1);ax.grid(axis="y")
            ax.set_xticks(range(5),[SHORT[s] for s in ORDER]);ax.set_title(w.title(),loc="left")
            if ax==axes[0]:ax.set_ylabel("Platonic improvement over rewired (%)")
        self.decorate(fig,title,caption);fig.subplots_adjust(left=.12,right=.97,wspace=.36,top=.81,bottom=.23)
        self.finish(fig,"rewiring_distribution",title,caption)

    def timeline(self):
        title="Task IDs make redistribution visible and auditable."
        caption="Illustrative icosahedral run: 240 clustered tasks, workload seed 2; this is not part of the primary benchmark. Colors identify original equal-count chunks, not policies. Each segment is one nonpreemptive task; the dashed line marks the last result collected at the master. Both runs retain every ID exactly once."
        fig,axes=plt.subplots(2,1,figsize=(7.16,5.8),sharex=True)
        colors=plt.cm.tab20(np.linspace(0,.95,12))
        for ax,p in zip(axes,("static","neighbor_push")):
            trace=self.data["traces"][p];starts={}
            for at,event,task,node in trace["events"]:
                if event=="start":starts[task]=at
                else:ax.broken_barh([(starts[task],at-starts[task])],(node-.34,.68),facecolors=colors[task//20],edgecolors="white",linewidth=.1)
            finish=trace["result"]["makespan_ms"]
            ax.axvline(finish,color=INK,ls="--",lw=1)
            ax.set_yticks([0,3,6,9,11]);ax.set_ylabel("Worker ID");ax.set_ylim(-.7,11.7)
            ax.set_title(LABEL[p]+f" · last result {finish:.2f} ms",loc="left");ax.grid(axis="x")
        axes[-1].set_xlabel("Simulation time (ms)")
        self.decorate(fig,title,caption);fig.subplots_adjust(left=.10,right=.97,hspace=.48,bottom=.19,top=.83)
        self.finish(fig,"timeline",title,caption)

    def graph_spectrum(self):
        title="Graph structure supplies a testable model, not a speed guarantee."
        caption="Analytic graph calculations, not scheduler measurements. Left: algebraic connectivity lambda2 of the peer graph and graph plus master. Right: synchronous convex-diffusion steps sufficient for a 99% reduction of L2 deviation at the selected spectral parameter. Atomic idle-triggered scheduling is a different process."
        fig,axes=plt.subplots(1,2,figsize=(7.16,4.1));records=self.data["graphs"]
        lookup={(r["solid"],r["scope"]):r for r in records if r["topology"]=="platonic"}
        for i,s in enumerate(ORDER):
            for offset,scope,color in ((-.13,"worker",BLUE),(.13,"worker_and_hub",ORANGE)):
                value=lookup[s,scope]["lambda2"]
                axes[0].plot([0,value],[i+offset,i+offset],color=color,lw=1.3)
                axes[0].scatter(value,i+offset,c=color,s=22,zorder=3)
            steps=lookup[s,"worker"]["diffusion_steps_99pct_l2"]
            axes[1].barh(i,steps,height=.46,color=BLUE,alpha=.8)
            axes[1].text(steps+.3,i,str(steps),va="center",fontsize=8)
        for ax in axes:ax.set_yticks(range(5),[s.title() for s in ORDER]);ax.invert_yaxis();ax.grid(axis="x")
        axes[0].set_xlabel("Algebraic connectivity λ₂");axes[1].set_xlabel("Synchronous diffusion steps")
        axes[0].set_title("Connectivity of peers vs hub graph",loc="left");axes[1].set_title("Continuous-load proxy",loc="left")
        axes[1].set_xlim(0,1.22*max(lookup[s,"worker"]["diffusion_steps_99pct_l2"] for s in ORDER))
        axes[0].legend(handles=[Line2D([],[],marker="o",color=BLUE,label="Peers"),Line2D([],[],marker="o",color=ORANGE,label="Peers + hub")],loc="lower right",frameon=False)
        self.decorate(fig,title,caption,evidence="ANALYTIC GRAPH MODEL");fig.subplots_adjust(left=.16,right=.97,wspace=.74,bottom=.24,top=.81)
        self.finish(fig,"graph_spectrum",title,caption)

    def protocol(self):
        title="Explicit messages resolve competing offers to an idle worker."
        caption="Schematic of the implemented neighbor-push protocol, not a timed trace. Donors reserve queued IDs before offering; the receiver accepts one offer and rejects a competing offer. Accepted inputs travel over a peer edge; identified results return directly to the master. No hub-assisted hint policy is implemented here."
        fig,ax=plt.subplots(figsize=(7.16,4.7));x=[.08,.35,.65,.92]
        actors=["Busy donor A","Idle neighbor","Busy donor B","Master"]
        for position,label in zip(x,actors):
            ax.text(position,.94,label,ha="center",va="center",fontsize=8,fontweight="bold")
            ax.plot([position,position],[.12,.88],color="#A7B3BE",lw=.9,ls="--")
        messages=[(1,0,.84,"IDLE epoch",BLUE),(1,2,.79,"IDLE epoch",BLUE),
            (0,1,.71,"OFFER · reserve IDs",ORANGE),(2,1,.63,"OFFER · reserve IDs",ORANGE),
            (1,0,.55,"ACCEPT token A",BLUE),(1,2,.47,"REJECT token B",BLUE),
            (0,1,.36,"DATA · same task IDs",ORANGE),(1,3,.19,"RESULT(task ID)",INK)]
        for source,target,y,label,color in messages:
            ax.annotate("",xy=(x[target],y),xytext=(x[source],y),arrowprops={"arrowstyle":"-|>","color":color,"lw":1.35,"mutation_scale":10})
            ax.text((x[source]+x[target])/2,y+.025,label,ha="center",va="bottom",fontsize=8,color=color,
                bbox={"facecolor":"white","edgecolor":"none","pad":1})
        ax.text(x[2],.405,"Restore\nreserved IDs",ha="center",va="center",fontsize=8,color="#526474")
        ax.text(x[1],.27,"Execute; send BUSY to peers",ha="center",va="center",fontsize=8,color="#526474")
        ax.set_xlim(0,1);ax.set_ylim(.08,1);ax.axis("off")
        self.decorate(fig,title,caption,evidence="IMPLEMENTED PROTOCOL · SCHEMATIC");fig.subplots_adjust(left=.03,right=.98,top=.81,bottom=.22)
        self.finish(fig,"protocol_sequence",title,caption)

    def close(self):
        self.atlas.close()
        (VIS/"figure-index.json").write_text(json.dumps(self.inventory,indent=2)+"\n")
        print(f"Created {len(self.inventory)} PDF/PNG/SVG figure sets and an offline visual atlas.")

def main():
    data=prepare_data();renderer=Renderer(data)
    try:
        for method in (renderer.geometries,renderer.makespans,renderer.effects_heatmap,renderer.effect_intervals,
                       renderer.latency,renderer.bottlenecks,renderer.traffic,renderer.topologies,
                       renderer.distributions,renderer.rewirings,renderer.timeline,renderer.graph_spectrum,renderer.protocol):
            method()
    finally:renderer.close()

if __name__=="__main__":main()
