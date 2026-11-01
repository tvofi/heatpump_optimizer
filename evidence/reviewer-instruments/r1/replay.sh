#!/bin/bash
# Reviewer's own replay: run the driver CLI (as git invokes it) at a given worktree over the seven P196 merges.
# usage: replay.sh <worktree> <outdir>
WT=$1; OUT=$2; mkdir -p $OUT
cd /home/user/heatpump_optimizer
CLAIM=tests/golden/claimed_drift.txt
while read label o t; do
  b=$(git merge-base "$o" "$t")
  d=$OUT/$label; mkdir -p $d
  git show $b:$CLAIM > $d/O; git show $o:$CLAIM > $d/A; git show $t:$CLAIM > $d/B
  cp $d/A $d/merged
  (cd $WT && python3 tests/env_drift.py --merge-claim-file $d/O $d/merged $d/B 7 $CLAIM) > $d/stdout 2> $d/stderr
  rc=$?
  marker=$(grep -o 'MERGE-CLAIM: [a-z]*' $d/stderr $d/stdout | head -1 | sed 's/.*MERGE-CLAIM/MERGE-CLAIM/')
  echo "RESULT $label rc=$rc ${marker:-no-marker} base=$(git rev-parse --short $b)"
done <<'CASES'
#2841 11e8075d f6784210c
#2745a 8d0572dc 28800999
#2745b cc679118 2563e2922
#2834 c38903518 2563e2922
3a07c2eaa 3a07c2eaa^1 3a07c2eaa^2
e438816e3 e438816e3^1 e438816e3^2
5bf232eac 5bf232eac^1 5bf232eac^2
CASES
