"""Embed saved observations into a self-contained, offline HTML explorer."""
import json
from pathlib import Path
from study.geometry import SOLIDS,geometry
from study.simulator import POLICIES
from study.benchmark import WORKLOADS
from .visualize import LABEL

def main():
    root=Path(__file__).resolve().parents[1]
    data=json.loads((root/"results/visual_data.json").read_text())
    primary={k:v for k,v in data["groups"].items() if k.startswith("main|")}
    payload={"metadata":data["metadata"],"groups":primary,"effects":data["effects"],
             "policies":list(POLICIES),"workloads":list(WORKLOADS),"labels":LABEL,"solids":{}}
    for s,(n,e,d,_) in SOLIDS.items():
        vertices,edges,_=geometry(s)
        payload["solids"][s]={"name":s.title(),"workers":n,"degree":d,"vertices":vertices.tolist(),"edges":edges}
    template=(root/"analysis/dashboard.html").read_text()
    assert template.count("__STUDY_DATA__")==1
    serialized=json.dumps(payload,separators=(",",":"),allow_nan=False).replace("<","\\u003c")
    output=root/"visualizations/dashboard.html"
    output.write_text(template.replace("__STUDY_DATA__",serialized))
    assert '<script src=' not in output.read_text() and '__STUDY_DATA__' not in output.read_text()
    print(f"Built {output}: {output.stat().st_size} bytes; no runtime network dependency.")

if __name__=="__main__":main()
