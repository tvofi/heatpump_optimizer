#!/bin/bash
# Local fix-review mutants for PR #3838 at 9516fcc5; run from the mutation worktree.
set -u
M=/Users/timmalmstrom/hpo-seats/r10s6/rev-3838-mut
S=/Users/timmalmstrom/hpo-seats/r10s6/rev-3838-scratch
cd "$M" || exit 9
export PYTHONPATH=tests/hastub OPENBLAS_NUM_THREADS=1
P2S='#3616 R11-OUTSIDE-ROOMS-P2: a room short of its target'
P2E='R.section("R10-DRAW-MAP-EVIDENCE part A'
B3S='R.section("#3616 R11-OUTSIDE-ROOMS-3B'
CBS="R.section(\"#224 stage 2 — optimize's comfort envelope"
CBE="R.section(\"#224 stage 2 — optimize's unpublished-horizon"
python3 tools/audit/seat/features_block.py --emit-prelude $S/P2 "$P2S" "$P2E" > $S/emit_p2.txt 2>&1; echo "emit P2 rc=$?"
python3 tools/audit/seat/features_block.py --emit-prelude $S/P3B "$B3S" > $S/emit_3b.txt 2>&1; echo "emit 3B rc=$?"
python3 tools/audit/seat/features_block.py --emit-prelude $S/PCB "$CBS" "$CBE" > $S/emit_cb.txt 2>&1; echo "emit CB rc=$?"
# the body notes the emitter misses asyncio for P2
grep -q "import asyncio as _asyncio" $S/P2 || sed -i '' '1i\
import asyncio as _asyncio
' $S/P2
det() { # $1 = p2|3b
  if [ "$1" = p2 ]; then
    timeout 1500 python3 tools/audit/seat/features_block.py --prelude "exec(open('$S/P2').read())" "$P2S" "$P2E" > $S/o.txt 2>&1
  elif [ "$1" = cb ]; then
    timeout 1500 python3 tools/audit/seat/features_block.py --prelude "exec(open('$S/PCB').read())" "$CBS" "$CBE" > $S/o.txt 2>&1
  else
    timeout 1500 python3 tools/audit/seat/features_block.py --prelude "exec(open('$S/P3B').read())" "$B3S" > $S/o.txt 2>&1
  fi
  echo $?
}
for d in p2 3b cb; do echo "UNMUTATED $d rc=$(det $d) $(grep -E 'BLOCK (PASSED|FAILED)' $S/o.txt | tail -1)"; done
for md in $PAIRS; do
  m=${md%%:*}
  for d in $(echo ${md#*:} | tr , ' '); do
    python3 $S/mutants.py "$m" || { echo "$m APPLY-FAIL"; continue 2; }
    rc=$(det $d); f=$(grep -m1 -E "^ *FAIL|Traceback|BLOCK (PASSED|FAILED)" $S/o.txt | cut -c1-160)
    git checkout -q -- custom_components
    [ "$rc" = 0 ] && echo "$m SURVIVED ($d)" || echo "$m KILLED rc=$rc ($d) $f"
  done
done
git status --short custom_components | head
