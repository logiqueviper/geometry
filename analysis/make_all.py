"""One-command regeneration of evidence-based exploratory visualization outputs."""
import argparse
from pathlib import Path
from . import graph_metrics,visualize,build_dashboard,statistics,report_numbers

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--refresh-graphs",action="store_true")
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    if args.refresh_graphs or not (root/"results/graph_metrics.json").exists():graph_metrics.main()
    statistics.main();visualize.main();build_dashboard.main();report_numbers.main()

if __name__=="__main__":main()
