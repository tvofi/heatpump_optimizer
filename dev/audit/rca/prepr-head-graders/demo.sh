#!/usr/bin/env bash
# R10-RCA-PREPR-HEAD-GRADERS: drive the countermeasure, tools/pr/ci_predict.py's
# `graders` arm, on one historical head against the base CI graded it with.
#
#   demo.sh <head-sha> <base-sha> <out-dir> [comment]
#
# A shared throwaway clone is checked out at <head>, its origin/main set to
# <base>, and this branch's ci_predict.py and agreement_py.py are copied over
# the old head's copies UNCOMMITTED: the predictor is the code under test, and
# the arm grades only committed state (the merge of HEAD into the base), so
# the copies change what predicts, never what is predicted. With a fourth
# argument a commit appending a `//` comment to tools/policy/policy_lint.mjs
# is made first, so the arm is keyed and a green result is the arm run and
# passing, not a skip. Prints the predictor's PREDICT and CI PREDICT lines,
# then `rc=<rc> seconds=<s>`. The seat's own checkout is never touched.
set -u
head=$1 base=$2 out=$3 comment=${4:-}
root=$(git rev-parse --show-toplevel)
. "$root/tests/throwaway_git.sh"
mkdir -p "$out"
wt=$(mktemp -d "$out/wt.XXXXXX")
trap 'rm -rf "$wt"' EXIT
throwaway_git_clone -q --shared --no-checkout "$root" "$wt/t" || { echo "rc=x no-clone"; exit 2; }
cd "$wt/t" || exit 2
throwaway_git_env
git checkout -q --detach "$head" && git update-ref refs/remotes/origin/main "$base" || { echo "rc=x no-checkout"; exit 2; }
if [ -n "$comment" ]; then
  echo '// a comment the null control adds so the graders arm is keyed' >> tools/policy/policy_lint.mjs
  git commit -qam "null control: a comment in policy_lint.mjs" || exit 2
fi
cp "$root/tools/pr/ci_predict.py" tools/pr/ci_predict.py
cp "$root/tools/policy/agreement_py.py" tools/policy/agreement_py.py
t0=$(date +%s)
PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base "$base" --only graders > "$out/predict.out" 2>&1; rc=$?
grep -E '^(PREDICT|CI PREDICT)' "$out/predict.out" | cut -c1-400
echo "rc=$rc seconds=$(( $(date +%s) - t0 ))"
