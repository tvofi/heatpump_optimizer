#!/bin/bash
# round 2: slot worktree runs a list of mutants serially, restoring between
slot=$1; shift; R=/Users/timmalmstrom/hpo-seats/1848-review; H=9a0960559ed9e87c679e50f30bce43a599c63459
w=$R/mut/slot$slot
[ -d $w ] || git -C $R/wt worktree add -q --detach $w $H
for id in "$@"; do
  git -C $w checkout -q --detach $H && git -C $w checkout -q -- . 
  [ -z "$(git -C $w status --porcelain)" ] || { echo "$id DIRTY-SLOT" > $R/mut/r2-$id.log; continue; }
  $R/venv/bin/python $R/mut/mutants.py $id $w > $R/mut/r2-$id.log 2>&1 || { echo "$id APPLY-FAILED" >> $R/mut/r2-$id.log; echo rc=apply > $R/mut/r2-$id.out; continue; }
  git -C $w diff --stat >> $R/mut/r2-$id.log
  ( cd $w && PYTHONPATH=tests/hastub $R/venv/bin/python tests/entities.py > $R/mut/r2-$id.out 2>&1; echo "rc=$?" >> $R/mut/r2-$id.out )
  git -C $w checkout -q -- .
done
