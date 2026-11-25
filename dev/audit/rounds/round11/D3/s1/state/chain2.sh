#!/bin/bash
cd $HOME/audit-r11-D3-s1
export PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
P=dev/audit/rounds/round11/D3/s1
PY=<home>/.local/state/hpo/venv-ci/bin/python3
mode=$1
if [ "$mode" = c3c6 ]; then
  while pgrep -f "sub c3c6" >/dev/null; do sleep 30; done
  $PY $P/prescreen.py complete --src c3c6 --workers 1 --tree-offset 4
else
  while pgrep -f "sub c2" >/dev/null; do sleep 30; done
  ls $P/state/results/c2/ > /dev/null; $PY $P/prescreen.py complete --src c2 --keys $P/state/c2_keys.txt --workers 1 --tree-offset 3
fi
