#!/bin/bash
cd $HOME/audit-r11-D3-s1
export PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
P=dev/audit/rounds/round11/D3/s1
PY=<home>/.local/state/hpo/venv-ci/bin/python3
echo 8e82d7a0b3617003 > $P/state/c2_keys_now.txt
$PY $P/prescreen.py complete --src c2 --keys $P/state/c2_keys_now.txt --workers 1 --tree-offset 3
$PY $P/prescreen.py complete --src c3c6 --keys $P/state/c36_keys.txt --workers 1 --tree-offset 3
