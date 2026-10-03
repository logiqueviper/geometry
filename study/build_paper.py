"""Compile twice in the paper's working directory and preserve TeX failures."""
import subprocess
from pathlib import Path

def main():
    root=Path(__file__).resolve().parents[1]
    with (root/"results/latex-build.log").open("w") as log:
        for _ in range(2):
            subprocess.run(["pdflatex","-interaction=nonstopmode","-halt-on-error","paper.tex"],
                           cwd=root/"paper",stdout=log,stderr=subprocess.STDOUT,check=True)
    path=root/"paper/paper.pdf"
    assert path.exists() and path.stat().st_size>10000
    print(f"Compiled {path} ({path.stat().st_size} bytes)")

if __name__=="__main__":main()
