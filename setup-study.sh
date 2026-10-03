#!/usr/bin/env bash
set -euo pipefail
cd /workspace/geometry
export PIP_CACHE_DIR=/workspace/platonic-env/pip-cache
export MPLCONFIGDIR=/workspace/platonic-env/matplotlib
export XDG_CACHE_HOME=/workspace/platonic-env/cache
mkdir -p "$PIP_CACHE_DIR" "$MPLCONFIGDIR" "$XDG_CACHE_HOME"
python -m venv --system-site-packages /workspace/platonic-env/venv
/workspace/platonic-env/venv/bin/python -m pip install -r requirements-study.txt
command -v pdflatex
test -f paper/IEEEtran.cls
printf '%s\n' 'aea20243d29b1b5940b1a071180d8a1d44fdba4d852305237f562d1dfe00ceac  paper/IEEEtran.cls' | sha256sum --check
/workspace/platonic-env/venv/bin/python -m pytest study analysis -q --junitxml=results/tests.xml
