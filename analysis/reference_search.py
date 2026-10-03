"""Resolve literature leads against live Crossref records; never invent metadata.

Matching verifies bibliographic existence only. Full-paper/claim reading is a
separate, explicit status and is never inferred from a successful DOI lookup.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlencode,quote
from urllib.request import Request,urlopen
from zoneinfo import ZoneInfo
import argparse
import json
import re
import hashlib
import time

ROOT=Path(__file__).resolve().parents[1]
LEADS=[
 "Adaptive load sharing in homogeneous distributed systems",
 "Scheduling multithreaded computations by work stealing",
 "Dynamic load balancing for distributed memory multiprocessors",
 "Load balancing and Poisson equation in a graph",
 "Dynamic load balancing by random matchings",
 "An improved diffusion algorithm for dynamic load balancing",
 "Load Balancing in Parallel Computers: Theory and Practice",
 "Strategies for dynamic load balancing on highly parallel computers",
 "How network topology affects dynamic load balancing",
 "A simple load balancing scheme for task allocation in parallel machines",
 "Guided self-scheduling: A practical scheduling scheme for parallel supercomputers",
 "Factoring: a method for scheduling parallel loops",
 "Trapezoid self-scheduling: a practical scheduling scheme for parallel compilers",
 "Scalable work stealing",
 "Lifeline-based global load balancing",
 "Non-blocking steal-half work queues",
 "The power of two choices in randomized load balancing",
 "UTS: An Unbalanced Tree Search Benchmark",
 "A comparison of eleven static heuristics for mapping a class of independent tasks onto heterogeneous distributed computing systems",
 "Bounds on multiprocessing timing anomalies",
 "Algebraic connectivity of graphs",
 "Spectral Graph Theory",
 "Principles and Practices of Interconnection Networks",
 "Introduction to Parallel Algorithms and Architectures",
 "Regular Polytopes",
 "Scientific benchmarking of parallel computing systems: twelve ways to tell the masses when reporting performance results",
 "Rigorous benchmarking in reasonable time",
 "Statistical comparisons of classifiers over multiple data sets",
 "A simple sequentially rejective multiple test procedure",
 "Versatile, scalable, and accurate simulation of distributed applications and platforms",
 "The ns-3 network simulator",
 "MapReduce: simplified data processing on large clusters",
 "Improving MapReduce performance in heterogeneous environments",
 "Heterogeneity and dynamicity of clouds at scale: Google trace analysis",
 "Ray: a distributed framework for emerging AI applications",
 "The implementation of the Cilk-5 multithreaded language",
 "Performance of a Simple 32 Core Raspberry Pi Cluster",
 "WRENCH: A Framework for Simulating Workflow Management Systems",
 "Sparrow: Distributed, Low Latency Scheduling",
 "Large-scale cluster management at Google with Borg",
 "Firmament: Fast, Centralized Cluster Scheduling at Scale",
 "Learning Scheduling Algorithms for Data Processing Clusters",
 "Borg: the Next Generation",
 "Array programming with NumPy",
 "SciPy 1.0: fundamental algorithms for scientific computing in Python",
 "Matplotlib: A 2D Graphics Environment",
]
RECENT_QUERIES=["dynamic loop scheduling load balancing","topology aware work stealing",
 "work stealing latency distributed memory","diffusion load balancing parallel computing",
 "scientific benchmarking parallel performance reproducibility","SimGrid simulation validation calibration"]

def normalized(text):return re.sub(r"[^a-z0-9]+"," ",text.lower()).strip()
def request(url):
    req=Request(url,headers={"User-Agent":"PlatonicSchedulingStudy/1.0 (bibliographic-verification; public academic records)","Accept":"application/json"})
    with urlopen(req,timeout=40) as response:return json.loads(response.read())

def lookup(title):
    url="https://api.crossref.org/works?"+urlencode({"query.title":title,"rows":3})
    try:
        response=request(url);items=response["message"]["items"]
        ranked=[]
        for item in items:
            actual=" ".join(item.get("title",[]))
            ratio=SequenceMatcher(None,normalized(title),normalized(actual)).ratio()
            ranked.append((ratio,item))
        ranked.sort(key=lambda p:p[0],reverse=True)
        ratio,item=ranked[0]
        return {"query":title,"url":url,"similarity":ratio,"status":"candidate_match" if ratio>=.83 else "needs_review",
                "record":item,"alternatives":[p[1] for p in ranked[1:]]}
    except Exception as error:return {"query":title,"url":url,"status":"request_failed","error":str(error)}

def main():
    parser=argparse.ArgumentParser();parser.add_argument("--refresh",action="store_true");args=parser.parse_args()
    path=ROOT/"docs/source-records";path.mkdir(parents=True,exist_ok=True)
    output=path/"crossref-candidates.json"
    if output.exists() and not args.refresh:
        results=json.loads(output.read_text())["candidates"]
    else:
        previous={r['query']:r for r in json.loads(output.read_text())['candidates']} if output.exists() else {}
        results=[]
        # Crossref's observed public-array headers specify one request/second
        # and one concurrent request. Respect both; retain successful records.
        for index,title in enumerate(LEADS):
            cached=previous.get(title)
            if cached and cached['status']!='request_failed':results.append(cached);continue
            time.sleep(1.1)
            result=lookup(title);results.append(result)
            print(f"Resolved lead {index+1}/{len(LEADS)}: {result['status']}",flush=True)
        output.write_text(json.dumps({"retrieved_at":datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),"candidates":results},indent=2)+"\n")
    recent=[]
    for query in RECENT_QUERIES:
        time.sleep(1.1)
        url="https://api.crossref.org/works?"+urlencode({"query":query,"filter":"from-pub-date:2019-01-01,type:journal-article","rows":8})
        try:recent.append({"query":query,"url":url,"records":request(url)["message"]["items"]})
        except Exception as e:recent.append({"query":query,"url":url,"error":str(e)})
    (path/"crossref-recent-candidates.json").write_text(json.dumps(recent,indent=2)+"\n")
    for item in results:
        record=item.get("record",{})
        print(item["status"],round(item.get("similarity",0),3)," | ",item["query"]," | ",record.get("title")," | ",record.get("DOI"))
    print("Recent candidate records saved for manual relevance review; none automatically cited.")

if __name__=="__main__":main()
