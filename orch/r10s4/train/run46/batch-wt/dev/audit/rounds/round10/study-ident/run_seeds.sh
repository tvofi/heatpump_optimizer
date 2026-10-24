#!/bin/bash
# Seed sweep of ident_rolling.py: is the solar learner's departure from truth a
# bias (same sign across seeds) or noise (zero-mean across seeds)?
# Usage (repository root): dev/audit/rounds/round10/study-ident/run_seeds.sh OUTDIR PLANT [extra args]
set -u
H=dev/audit/rounds/round10/study-ident/ident_rolling.py
O=${1:?outdir}; P=${2:?plant}; shift 2
mkdir -p "$O"
: > "$O/rc_$P.log"
for s in 1 2 3 4 5 6 7 8; do
  ( PYTHONPATH=tests/hastub python3 $H --plant "$P" --seed $s "$@" > "$O/seed_${P}_$s.out" 2>&1; echo "rc=$? seed=$s" >> "$O/rc_$P.log" ) &
  while [ "$(jobs -r | wc -l)" -ge 8 ]; do sleep 2; done
done
wait
echo DONE >> "$O/rc_$P.log"
