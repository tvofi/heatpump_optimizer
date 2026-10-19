#!/bin/bash
cd /tmp/seat/rev2445
for m in ${MUTS:-L_CMP_BOUND L_CONST10 L_FLOOR_RETURN_DEL L_RELAXED_RETURN_DEL}; do
  git -C mut checkout -q -- . 
  if ! python3 tools/mutants.py mut $m 2> ev/mut_$m.err; then echo "$m APPLY-FAILED"; continue; fi
  tools/mini.sh /tmp/seat/rev2445/mut > ev/mut_$m.txt 2>&1; rc=$?
  echo "$m exit=$rc red=$(grep -c '^  FAIL' ev/mut_$m.txt) $(grep -E '^  FAIL' ev/mut_$m.txt | cut -c8-70 | tr '\n' '|')"
done
git -C mut checkout -q -- . ; echo "restored: $(git -C mut status --short | wc -l) dirty"
