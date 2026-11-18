#!/bin/bash
# Re-take env_drift's --capture --all reach on this run (D3-s1-01 re-check);
# the local run's baselines are kept as state/baselines-local.json.
cd /Users/timmalmstrom/hpo-orch/r10s6/r11/audit-r11-D3-s1 || exit 2
export PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
PY=/Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python3
P=dev/audit/rounds/round11/D3/s1
$PY $P/prescreen.py trace-capture --tree-offset 7 > $P/state/retrace-cap-r2.out 2>&1
$PY $P/m5_envdrift_reach.py > $P/state/envdrift-reach-r2.out 2>&1
$PY $P/m5_envdrift_reach.py --as-if-fixed > $P/state/envdrift-reach-r2-fixed.out 2>&1
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) RETRACE-01 $(grep -h 'capture_never\|gate_skippable' $P/state/envdrift-reach-r2.out $P/state/envdrift-reach-r2-fixed.out | tr '\n' ' ') $(grep load1 $P/state/envdrift-reach-r2.out)" >> $P/r2/PROGRESS.log
