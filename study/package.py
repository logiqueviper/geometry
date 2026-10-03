"""Bundle reproducibility artifacts with per-file SHA-256 checksums."""
import hashlib
import json
from pathlib import Path
import zipfile

def main():
    root=Path(__file__).resolve().parents[1]
    paths=[root/"README.md",root/"setup-study.sh",root/"requirements-study.txt"]
    for directory in ("study","results","paper"):
        for path in (root/directory).rglob("*"):
            if not path.is_file() or "__pycache__" in path.parts:continue
            if path.suffix in (".pyc",".aux",".out"):continue
            if path.name in ("paper.log","setup.log","manifest.json"):continue
            paths.append(path)
    paths=sorted(paths)
    manifest={"files":[{"path":str(p.relative_to(root)),"bytes":p.stat().st_size,
                        "sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],
              "experiment_runs":16050,"validation_tests":116,"replayed_cases":141,
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
