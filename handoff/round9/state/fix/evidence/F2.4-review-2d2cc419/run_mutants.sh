#!/bin/bash
# usage: run_mutants.sh <tree> <script> <ids...>
S=/tmp/claude-0/-home-claude/6de11d25-1693-5070-8c25-2c3ab2180e07/scratchpad
T=$1; SCR=$2; shift 2
export PATH=$S/vci/bin:$PATH OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_CORETYPE=Haswell PYTHONPATH=tests/hastub
cd $T
for m in "$@"; do
  git checkout -q -- custom_components
  if [ "$m" != "M0" ]; then python3 $S/mutants.py $T $m apply; fi
  git diff --stat -- custom_components | tail -1
  start=$(date +%s)
  python3 $SCR > $S/mut_${m}_$(basename $SCR .py).log 2>&1; rc=$?
  echo "MUTANT $m script=$SCR rc=$rc secs=$(( $(date +%s)-start )) :: $(grep -E 'CHECKS (PASSED|FAILED)|CHECK\(S\) FAILED|FAILED' $S/mut_${m}_$(basename $SCR .py).log | tail -1)"
  grep -E "^\s*(FAIL|✗|not ok)" $S/mut_${m}_$(basename $SCR .py).log | head -8
  git checkout -q -- custom_components
done
