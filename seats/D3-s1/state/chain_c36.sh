#!/bin/bash
cd $HOME/audit-r11-D3-s1
export PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
P=dev/audit/rounds/round11/D3/s1
while kill -0 $(cat $P/state/null.pid) 2>/dev/null; do sleep 20; done
<home>/.local/state/hpo/venv-ci/bin/python3 $P/prescreen.py run --workers 1 --tree-offset 4 --mutants $P/c3c6_mutants.json --sub c3c6
