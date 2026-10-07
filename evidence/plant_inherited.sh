#!/usr/bin/env bash
# Reviewer's plant: a red main carries (a selectable script no lane records)
# must not refuse an unrelated branch. Throwaway clone; prints the predictor's output.
set -u
SRC=/Users/timmalmstrom/hpo-seats/review-2030/wt
D=$(mktemp -d); trap 'rm -rf "$D"' EXIT
git clone -q --shared "$SRC" "$D/r" && cd "$D/r" || exit 9
G="git -c user.name=r -c user.email=r@x -c commit.gpgsign=false"
$G checkout -q --detach
# "main" with an unrecorded selectable script on it
echo "# planted on main" > tests/zz_main_unrecorded_check.py
$G add -A && $G commit -qm "main carries NO RECORDING"
git update-ref refs/remotes/origin/main HEAD
# an unrelated branch: a comment in a selectable script
$G checkout -q -b unrelated
echo "# a comment" >> tests/wood_advisor.py && $G commit -qam unrelated
echo "--- branch touching only tests/wood_advisor.py; main carries the red"
PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main; echo "rc=$?"
echo "--- control: same branch, main without the plant"
git update-ref refs/remotes/origin/main HEAD~2
$G checkout -q --detach HEAD~2 && $G checkout -q -b ctl && echo "# a comment" >> tests/wood_advisor.py && $G commit -qam ctl
PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main; echo "rc=$?"
