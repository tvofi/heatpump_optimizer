#!/bin/bash
# Reviewer's mutant batch: option block then clamp block.
S=~/hpo-seats/r10s6/rev-3866-local
cd $S/wt || exit 1
cat > $S/runclamp.sh <<'EOF'
PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude 'exec(open("~/hpo-seats/r10s6/rev-3866-local/clamp_prelude.py").read())' "# (C) Set-points are written on the entity's own step" "def _bst_q(value_c" 2>&1
EOF
PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --emit-prelude $S/clamp_prelude.py "# (C) Set-points are written on the entity's own step" "def _bst_q(value_c" 2>&1 | tail -1
bash $S/runclamp.sh > $S/ev/clamp_head.txt; echo "CLAMP HEAD rc=$? $(grep BLOCK $S/ev/clamp_head.txt)"
for m in "O-M1 min->max" "O-M2 >= strict" "O-M3 dropped voids other" "O-M4 floor off" "O-M5 ceiling off" "O-M6 indoor reads" "O-M7 boost_ceiling cap GUARD_OFF" "O-M8 map top ignores limit" "O-M7+M8" "O-M9 hold ignores limit" "O-M10 feedback ignores limit" "O-M11 sensor bypasses crossed-pair rule" "O-M12 option never read"; do
  f=$(echo "$m" | tr -c 'A-Za-z0-9' '_')
  python3 $S/mut.py "$m" $S/runfl.sh $S/ev/mut_$f.txt
done
for m in "C-M1 max clamp off" "C-M2 min clamp off" "C-M3 max rounds nearest" "C-M4 min rounds nearest" "C-M5 number keys every domain"; do
  f=$(echo "$m" | tr -c 'A-Za-z0-9' '_')
  python3 $S/mut.py "$m" $S/runclamp.sh $S/ev/mut_$f.txt
done
git status --short
echo BATCH-DONE
