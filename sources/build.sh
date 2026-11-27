#!/bin/sh
set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo_dir"
python_bin=${PORTO_FAIFO_PYTHON:-.venv/bin/python}

"$python_bin" scripts/build.py
"$python_bin" scripts/build_mono.py
