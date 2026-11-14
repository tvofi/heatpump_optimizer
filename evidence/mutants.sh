#!/bin/bash
# Reviewer's mutant driver: each mutant rewrites legionella.py's gate (lines 104-106 at the head),
# runs tests/guard_pins.py and the wide census, and restores.
cd $HOME/wt; F=custom_components/heatpump_optimizer/legionella.py; E=$HOME/rev3581/ev
ORIG=$(sed -n 104,106p $F)
declare -A M
M[verdict_suggested]='        if write is not None and write.written_c < target - margin and target <= write.above_c <= params.dhw_hard_max_temp:'
M[verdict_suggested_range]='        if write is not None and write.written_c < write.above_c <= params.dhw_hard_max_temp and write.written_c < target - margin:'
M[range_le]='        if write is not None and write.written_c < target - margin and write.written_c <= write.above_c <= replace(params, dhw_legionella_temp=write.above_c).dhw_hard_max_temp:'
M[range_dropped]='        if write is not None and write.written_c < target - margin and write.above_c <= replace(params, dhw_legionella_temp=write.above_c).dhw_hard_max_temp:'
M[above_minus_margin]='        if write is not None and write.written_c < target - margin and write.written_c < write.above_c - margin <= replace(params, dhw_legionella_temp=write.above_c).dhw_hard_max_temp - margin:'
M[hard_lt]='        if write is not None and write.written_c < target - margin and write.written_c < write.above_c < replace(params, dhw_legionella_temp=write.above_c).dhw_hard_max_temp:'
M[hard_dropped]='        if write is not None and write.written_c < target - margin and write.written_c < write.above_c:'
M[hard_literal70]='        if write is not None and write.written_c < target - margin and write.written_c < write.above_c <= 70.0:'
M[old_plus_hard]='        if write is not None and write.written_c < target - margin and target <= write.above_c <= replace(params, dhw_legionella_temp=write.above_c).dhw_hard_max_temp:'
M[hard_at_target]='        if write is not None and write.written_c < target - margin and write.written_c < write.above_c <= replace(params, dhw_legionella_temp=target).dhw_hard_max_temp:'
cp $F /tmp/leg.orig
for k in "${!M[@]}"; do
  python3 - "$F" "$k" "${M[$k]}" <<'PY'
import sys
p, k, new = sys.argv[1:]
L = open(p).read().split("\n")
assert L[103].startswith("        if write is not None"), L[103]
L[103:106] = [new]
open(p, "w").write("\n".join(L))
PY
  PYTHONPATH=tests/hastub python3 tests/guard_pins.py > $E/mut_$k.guard_pins.txt 2>&1; rc=$?
  PYTHONPATH=tests/hastub:tests python3 $E/census.py > /tmp/census_$k.txt 2>&1
  diff $E/census_head.txt /tmp/census_$k.txt > $E/mut_$k.census_diff.txt; nd=$(grep -c '^<' $E/mut_$k.census_diff.txt)
  echo "MUTANT $k guard_pins rc=$rc $(grep -c 'FAIL' $E/mut_$k.guard_pins.txt) FAIL-lines; census rows differing=$nd"
  cp /tmp/leg.orig $F
done
git -C $HOME/wt status --short
