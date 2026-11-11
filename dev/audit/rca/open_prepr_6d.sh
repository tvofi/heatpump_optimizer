#!/bin/bash
# Step 6d's predictor, timed at one head (R10-RCA-OPEN-PREPR-SLOW, C4).
#
#   bash dev/audit/rca/open_prepr_6d.sh <head> [<main>]
#
# Runs, in a throwaway worktree of <head>, the command prepr.sh's predict_line
# runs for step 6d (`ci_predict.py --base <base> --record-self-tests`), <base>
# being the merge base of <head> and <main> (default b0762725099f, the main the
# three opens of 2026-11-10 measured against). Prints the head, the base, the
# predictor's rc, its wall seconds, a sha1 of its sorted PREDICT lines (the
# fixer's before/after identity check) and its last line. A SCOPED head is the
# null control for a FULL one: same command, same host, seconds apart.
set -u
head=${1:?head}; main=${2:-b0762725099f}
repo=$(git rev-parse --show-toplevel) || exit 2
w=$(mktemp -d) || exit 2
trap 'git -C "$repo" worktree remove --force "$w/t" >/dev/null 2>&1; rm -rf "$w"' EXIT
git -C "$repo" worktree add -q --detach "$w/t" "$head" || exit 2
cd "$w/t" || exit 2
base=$(git merge-base HEAD "$main") || exit 2
echo "head=$(git rev-parse HEAD) base=$base"
s=$SECONDS
PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base "$base" --record-self-tests > "$w/out" 2>&1
r=$?
echo "rc=$r wall_s=$((SECONDS - s))"
echo "predict_sha1=$(grep '^PREDICT' "$w/out" | sort | sha1sum | cut -d' ' -f1) predict_lines=$(grep -c '^PREDICT' "$w/out")"
tail -1 "$w/out"
