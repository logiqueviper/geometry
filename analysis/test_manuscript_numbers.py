"""Prevent missing or hand-edited observational macro values."""
import json
from pathlib import Path
import re

def test_every_manuscript_observation_macro_exists():
    root=Path(__file__).resolve().parents[1]
    values=json.loads((root/"results/numbers.json").read_text())["values"]
    used=re.findall(r"\\datum\{([^}]+)\}",(root/"paper/paper.tex").read_text())
    assert len(used)>50
    assert all(key in values for key in used)
