"""Bundle reproducibility artifacts with per-file SHA-256 checksums."""
import hashlib
import json
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

def main():
    root=Path(__file__).resolve().parents[1]
    paths=[root/name for name in ("README.md","setup-study.sh","requirements-study.txt",
                                  "Makefile","Dockerfile","refs.bib")]
    for directory in ("study","analysis","results","paper","docs","hardware","visualizations"):
        for path in (root/directory).rglob("*"):
            if not path.is_file() or any(p in path.parts for p in ("__pycache__","source-records","raw")):continue
            if path.suffix in (".pyc",".aux",".out"):continue
            if path.name in ("paper.log","setup.log","manifest.json","tests.xml"):continue
            paths.append(path)
    paths=sorted(paths)
    suites=list(ET.parse(root/"results/tests.xml").getroot().iter("testsuite"))
    assert all(int(s.attrib.get(k,0))==0 for s in suites for k in ("failures","errors","skipped"))
    tests=sum(int(s.attrib["tests"]) for s in suites)
    manifest={"files":[{"path":str(p.relative_to(root)),"bytes":p.stat().st_size,
                        "sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],
              "experiment_runs":16050,"validation_tests":tests,"replayed_cases":141,
              "research_phase":"exploratory historical simulation; prospective plan draft",
              "hardware_measurements":0,"new_policy_final_experiments":0,
              "timing_scope":"discrete-event simulated milliseconds; not hardware performance"}
    manifest_path=root/"results/manifest.json"
    manifest_path.write_text(json.dumps(manifest,indent=2)+"\n")
    paths.append(manifest_path)
    archive=root/"platonic-study.zip"
    with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for path in paths:z.write(path,"platonic-study/"+str(path.relative_to(root)))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for entry in manifest["files"]:
            data=z.read("platonic-study/"+entry["path"])
            assert hashlib.sha256(data).hexdigest()==entry["sha256"]
    print(f"Verified {archive}: {len(paths)} files, {archive.stat().st_size} bytes")

if __name__=="__main__":main()
