#!/usr/bin/env bash
# R10-RCA-PREPR-HEAD-GRADERS: one review-round plant, committed on <head> and
# graded by the `graders` arm of <predictor-sha>'s ci_predict.py with --base
# <head>, so only the plant is in the diff.
#
#   plant.sh <head> <mdit|gate> <predictor-sha> <out-file>
#
# mdit: a comment appended to tools/policy/vendor/markdown-it.min.js (review
# round 3's seam). gate: budget_raise_gate.py's JUSTIFICATION_SCORE accepting
# `Arch score`, with prepr/raise/good.md using that spelling (round 2's seam).
# A shared throwaway clone; the seat's own checkout is never touched. Writes
# the predictor's output, then `rc=<rc> seconds=<s>`, to <out-file>.
set -u
head=$1 kind=$2 pred=$3 out=$4
root=$(git rev-parse --show-toplevel)
. "$root/tests/throwaway_git.sh"
wt=$(mktemp -d); trap 'rm -rf "$wt"' EXIT
throwaway_git_clone -q --shared --no-checkout "$root" "$wt/t" >/dev/null || exit 2
cd "$wt/t" || exit 2
throwaway_git_env
git checkout -q --detach "$head" && git update-ref refs/remotes/origin/main "$head" || exit 2
case $kind in
  mdit) printf '\n/* plant: an edit to the vendored parser only */\n' >> tools/policy/vendor/markdown-it.min.js ;;
  gate) sed -i 's/Architecture score: dS \[+-\]/Arch(?:itecture)? score: dS [+-]/' tools/policy/budget_raise_gate.py
        sed -i 's/^Architecture score: dS +0.1000 IMPROVES/Arch score: dS +0.1000 IMPROVES/' tools/policy/fixtures/policy-rot/prepr/raise/good.md ;;
  *) echo "plant.sh: no plant $kind"; exit 2 ;;
esac
git commit -qam "plant $kind" || exit 2
git show "$pred:tools/pr/ci_predict.py" > tools/pr/ci_predict.py
git show "$pred:tools/policy/agreement_py.py" > tools/policy/agreement_py.py
t0=$(date +%s.%N)
PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base "$head" --only graders > "$out" 2>&1; rc=$?
echo "rc=$rc seconds=$(echo "$(date +%s.%N) - $t0" | bc)" >> "$out"
