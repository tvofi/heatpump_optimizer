#!/bin/bash
# D3-s1 resume run (local, round 11): controls, then the U1 pre-screen of every
# remaining unpinned cell site, with the C3C6 M22 re-drive beside it on its own
# tree. Resumable: prescreen.py writes one result file per mutant and skips keys
# already under results/<sub>/. Holds one heavy slot (gate_lock.py) for its life.
set -u
cd /Users/timmalmstrom/hpo-orch/r10s6/r11/audit-r11-D3-s1 || exit 2
export PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
P=dev/audit/rounds/round11/D3/s1
S=$P/state
PY=/Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python3
W=${D3S1_WORKERS:-4}
LOG=$P/r2/PROGRESS.log
stamp() { date -u +%Y-%m-%dT%H:%M:%SZ; }
load1() { sysctl -n vm.loadavg | awk '{print $2}'; }
python3 tests/gate_lock.py slot-take --label d3-s1 --owner-pid $$ >> $LOG 2>&1
trap 'python3 tests/gate_lock.py slot-release --label d3-s1 >> $LOG 2>&1' EXIT
echo "$(stamp) CHAIN-U1 start workers=$W load1=$(load1)" >> $LOG

if [ ! -f $S/r2-controls.done ]; then
  [ -f $S/null-local.json ] || cp $S/null.json $S/null-local.json
  $PY $P/prescreen.py run --anchors $P/posctl_anchors.txt --sub posctl-r2 --workers 1 --tree-offset 1 > $S/posctl-r2.out 2>&1 &
  $PY $P/prescreen.py null > $S/null-r2.out 2>&1
  wait
  echo "$(stamp) CONTROLS $(grep null_verdict $S/null-r2.out) posctl-r2: $(grep -c 'POSCTL-R2 KILLED' $S/posctl-r2.out) of 2 KILLED load1=$(load1)" >> $LOG
  touch $S/r2-controls.done
fi

if [ ! -f $S/r2-m22.done ]; then
  mkdir -p $S/superseded
  for f in $S/results/c3c6/*.json; do
    if grep -q '"verdict": "TIMEOUT"' "$f"; then mv "$f" $S/superseded/; fi
  done
  ( $PY $P/prescreen.py run --mutants $P/c3c6_mutants.json --sub c3c6 --workers 1 --tree-offset $W > $S/m22-r2.out 2>&1
    echo "$(stamp) M22 $(grep -E 'C3C6 (KILLED|SURVIVED|TIMEOUT)' $S/m22-r2.out | tail -1) load1=$(load1)" >> $LOG
    touch $S/r2-m22.done ) &
fi

$PY $P/prescreen.py run --workers $W --sub pre > $S/u1.out 2>&1
rc=$?
wait
echo "$(stamp) CHAIN-U1 end rc=$rc driven=$(ls $S/results/pre | wc -l | tr -d ' ') load1=$(load1)" >> $LOG
