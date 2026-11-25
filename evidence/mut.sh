#!/bin/bash
# Reviewer mutants for PR #3838 at d7029ade; run from a detached worktree at the head.
set -u
W=/tmp/tmp.y49CjaZqL2; S=$HOME/scr
cd $HOME/wt || exit 9
export PYTHONPATH=tests/hastub OPENBLAS_NUM_THREADS=1
B3S='R.section("#3616 R11-OUTSIDE-ROOMS-3B'
CBS="R.section(\"#224 stage 2 — optimize's comfort envelope"
CBE="R.section(\"#224 stage 2 — optimize's unpublished-horizon"
det() {
  case $1 in
    3b) timeout 1500 python3 tools/audit/seat/features_block.py --prelude "exec(open('$S/P3B').read())" "$B3S" > $S/o.txt 2>&1 ;;
    cb) timeout 1500 python3 tools/audit/seat/features_block.py --prelude "exec(open('$S/PCB').read())" "$CBS" "$CBE" > $S/o.txt 2>&1 ;;
    edge) timeout 1500 python3 tests/edge.py > $S/o.txt 2>&1 ;;
  esac
  echo $?
}
for d in ${DETS:-3b cb}; do echo "UNMUTATED $d rc=$(det $d) $(grep -E 'PASSED|FAILED' $S/o.txt | tail -1)"; done
for m in ${MUTS:-$(python3 $W/ev/mutants.py --list)}; do
  for d in ${DETS:-3b cb}; do
    python3 $W/ev/mutants.py "$m" || { echo "$m APPLY-FAIL"; continue 2; }
    rc=$(det $d); f=$(grep -m1 -E "FAIL|Traceback|Error" $S/o.txt | cut -c1-200)
    git checkout -q -- custom_components
    if [ "$rc" = 0 ]; then echo "$m SURVIVED ($d)"; else echo "$m KILLED rc=$rc ($d) $f"; continue 2; fi
  done
done
echo "git status: $(git status --short custom_components | wc -l) modified"
