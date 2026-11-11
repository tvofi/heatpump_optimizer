#!/bin/bash
# Reviewer's round-3 driver at the head: mutants of the body's round-2 set plus NULL,
# then features.py at head and at the merge base, then closure select.
W=$1; cd $W/wt || exit 2
while [ ! -e $W/ev/.done ]; do sleep 5; done
export PYTHONPATH=tests/hastub GOLDEN_MODE=drift
F=custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
out=$W/ev/mutants.txt; : > $out
run() { # name, python edit
  name=$1; shift
  python3 - "$F" "$@" <<'PY'
import sys,re
p,old,new=sys.argv[1],sys.argv[2],sys.argv[3]
s=open(p).read()
n=s.count(old)
if n!=1: print("EDIT-MISS",n); sys.exit(3)
open(p,"w").write(s.replace(old,new))
PY
  erc=$?
  if [ $erc -ne 0 ]; then echo "$name: EDIT-NOT-APPLIED" >> $out; git checkout -q -- $F; return; fi
  node tests/card.mjs > $W/ev/mut_$name.log 2>&1; rc=$?
  fails=$(grep -c '^FAIL' $W/ev/mut_$name.log)
  first=$(grep -m3 '^FAIL' $W/ev/mut_$name.log | tr '\n' '|')
  if [ $rc -eq 0 ]; then v=SURVIVED; else v=KILLED; fi
  echo "$name: $v rc=$rc fails=$fails first=$first" >> $out
  git checkout -q -- $F
}
# anchors are discovered by grep of the card file, printed for the record
grep -n '_folds' $F > $W/ev/folds_lines.txt
grep -n 'again.focus()' $F >> $W/ev/folds_lines.txt
grep -n 'set hass' $F >> $W/ev/folds_lines.txt
echo "anchors-written" >> $out
echo DRIVER-READY > $W/ev/.anchors
while [ ! -e $W/ev/.go ]; do sleep 2; done
. $W/ev/.go
git -C $W/wt status --short >> $out
echo "status-after: $(git -C $W/wt status --short | wc -l) dirty" >> $out
# features.py at head and at merge base ceb3070
python3 tests/features.py > $W/ev/features_head.txt 2>&1; echo rc=$? >> $W/ev/features_head.txt
git -C $W/wt checkout -q --detach ceb3070ccb49fe6dfc9d403458e8a3cc03c5595e
python3 tests/features.py > $W/ev/features_base.txt 2>&1; echo rc=$? >> $W/ev/features_base.txt
git -C $W/wt checkout -q --detach 82e14f6d8fb87fc65dd993d1cadbd35883090f07
python3 tests/closure.py select --diff ceb3070ccb49fe6dfc9d403458e8a3cc03c5595e --workdir $W/wt > $W/ev/closure_select.txt 2>&1; echo rc=$? >> $W/ev/closure_select.txt
python3 tools/audit/archscore/score.py --diff ceb3070ccb49fe6dfc9d403458e8a3cc03c5595e > $W/ev/archscore.txt 2>&1; echo rc=$? >> $W/ev/archscore.txt
git diff --quiet ceb3070ccb49fe6dfc9d403458e8a3cc03c5595e...HEAD -- VERSION RELEASE_NOTES.md custom_components/heatpump_optimizer/manifest.json && echo untouched > $W/ev/version_untouched.txt
echo FINISHED > $W/ev/.finished
