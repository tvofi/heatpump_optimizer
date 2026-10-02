#!/bin/bash
# run one mutant in its own detached worktree at the head
id=$1; R=/Users/timmalmstrom/hpo-seats/1848-review; H=4f594b42635be021152dec6e3934af1a674cec52
w=$R/mut/wt-$id
git -C $R/wt worktree add -q --detach $w $H 2>/dev/null || true
$R/venv/bin/python $R/mut/mutants.py $id $w > $R/mut/$id.log 2>&1 || { echo "$id APPLY-FAILED" >> $R/mut/$id.log; exit; }
git -C $w diff --stat >> $R/mut/$id.log
( cd $w && PYTHONPATH=tests/hastub $R/venv/bin/python tests/entities.py > $R/mut/$id.out 2>&1; echo "rc=$?" >> $R/mut/$id.out )
{ grep -E '^\s*FAIL' $R/mut/$id.out | cut -c1-200; tail -2 $R/mut/$id.out; } >> $R/mut/$id.log
git -C $w checkout -q -- . 
