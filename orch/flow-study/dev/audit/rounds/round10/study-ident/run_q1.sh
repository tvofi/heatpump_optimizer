#!/bin/bash
# Q1 grid: every arm of ident_rolling.py over 6 plants x 3 scenarios + the
# delivery arms. Usage (repository root): dev/audit/rounds/round10/study-ident/run_q1.sh OUTDIR
# Writes OUTDIR/<job>.out and .json, and OUTDIR/rc.log with one rc per job.
set -u
H=dev/audit/rounds/round10/study-ident/ident_rolling.py
O=${1:?outdir}
mkdir -p "$O"
: > "$O/rc.log"
jobs_l=()
for p in P0 P1 P2 P3 P4 P5; do jobs_l+=("--plant $p --scenario autumn"); done
for p in P1 P2 P3 P4 P5; do jobs_l+=("--plant $p --scenario flat"); jobs_l+=("--plant $p --scenario indep"); done
for g in 0.6 0.4; do jobs_l+=("--plant P0 --scenario autumn --delivery $g"); jobs_l+=("--plant P1 --scenario autumn --delivery $g"); done
for j in "${jobs_l[@]}"; do
  n=$(echo "$j" | tr -d ' -')
  ( PYTHONPATH=tests/hastub python3 $H $j --json "$O/$n.json" > "$O/$n.out" 2>&1; echo "rc=$? $j" >> "$O/rc.log" ) &
  while [ "$(jobs -r | wc -l)" -ge 6 ]; do sleep 2; done
done
wait
echo DONE >> "$O/rc.log"
