#!/bin/bash
cd /Users/timmalmstrom/hpo-orch/r10s6/r11/audit-r11-D3-s1
export PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
P=dev/audit/rounds/round11/D3/s1
/Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python3 $P/prescreen.py run --mutants $P/c2_mutants.json --sub c2 --workers 3 --tree-offset 0
