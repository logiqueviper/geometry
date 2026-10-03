"""Check saved visualization provenance and prospective separation."""
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]

def test_historical_raw_files_remain_byte_identical():
    expected = {
        "raw.csv": "f7091594e6761b08fbb95bef756c339db688a7b66311a8a0a838058adc4757ed",
        "topology.csv": "16e5d0e6568b4e691a174d04672939e5fc81de1befb9c4ff6edb4763fddd158e"}
    for name, digest in expected.items():
        assert hashlib.sha256((ROOT / "results" / name).read_bytes()).hexdigest() == digest

def test_all_primary_chart_observations_match_source_csv():
    data = json.loads((ROOT / "results/visual_data.json").read_text())
    for row in csv.DictReader((ROOT / "results/raw.csv").open()):
        if row["suite"] != "main": continue
        group = data["groups"]["|".join(row[k] for k in ("suite", "solid", "workload", "policy"))]
        index = group["seeds"].index(int(row["seed"]))
        assert group["makespan_ms"]["values"][index] == float(row["makespan_ms"])

def test_paired_effects_use_same_workload_seed_and_ratio_direction():
    data = json.loads((ROOT / "results/visual_data.json").read_text())
    for key, effect in data["effects"].items():
        solid, work, comparator = key.split("|")
        base = data["groups"][f"main|{solid}|{work}|{comparator}"]
        push = data["groups"][f"main|{solid}|{work}|neighbor_push"]
        assert effect["seeds"] == base["seeds"] == push["seeds"]
        np.testing.assert_allclose(effect["values"], np.array(base["makespan_ms"]["values"])/push["makespan_ms"]["values"], rtol=1e-14)

def test_pdf_figure_widths_and_atlas_inventory():
    index = json.loads((ROOT / "visualizations/figure-index.json").read_text())
    assert len(index) == len(PdfReader(ROOT / "visualizations/visual-atlas.pdf").pages) == 13
    for item in index:
        page = PdfReader(ROOT / "paper/figures" / (item["name"] + ".pdf")).pages[0]
        assert abs(float(page.mediabox.width)/72 - 7.16) < 0.001
        assert item["minimum_font_points"] >= 8
        assert not item["text_outside_canvas"]

def test_prospective_seed_ranges_and_equal_initial_counts():
    plan = json.loads((ROOT / "analysis/experiment_plan.json").read_text())
    ranges = [plan["historical_seeds"], *plan["seed_ranges"].values()]
    for i, (lo, hi) in enumerate(ranges):
        assert lo <= hi
        for other_lo, other_hi in ranges[i+1:]:
            assert hi < other_lo or other_hi < lo
    assert plan["primary"]["runs"] == len(plan["primary"]["solids"])*len(plan["primary"]["workloads"])*len(plan["primary"]["policies"])*plan["primary"]["seeds"]
    for family in ("geodesic", "hypercube"):
        assert all(plan["scaling"][family + "_strong_tasks"] % n == 0 for n in plan["scaling"][family + "_worker_counts"])
    assert plan["status"] == "draft_requires_human_approval_after_literature_review"
