#!/bin/bash
# ci_predict --self-test at three refs, sequentially; log each.
set -u
BASE=/Users/timmalmstrom/hpo-seats/r10s6/review-2853-r5
log=$BASE/ev/ci-predict-selftest.log
: > "$log"
run() {
  local name=$1 dir=$2 sha=$3
  echo "===== $name $sha start $(date -u +%H:%M:%S) =====" >> "$log"
  ( cd "$dir" && PYTHONPATH=tests/hastub /usr/bin/time -p python3 tools/pr/ci_predict.py --self-test ) >> "$log" 2>&1
  echo "===== $name rc=$? end $(date -u +%H:%M:%S) =====" >> "$log"
}
run head  "$BASE/wt-14427f3" 14427f3acc22e8e7e0040deca9d398175bf212e6
run oldhead "$BASE/wt-oldhead" b69828eb4a056850e7fc8914e6cde391f04743df
run main  "$BASE/wt-main"    a0e7664ea6485b9ad8f68d164cd255ec4fd51fb9
echo "ALL-DONE" >> "$log"
