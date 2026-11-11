#!/usr/bin/env bash
# R10-FLY-CIPREDICT-RESTORING (#2952): one planted edit per restoring job, graded
# by the working tree's ci_predict.py `graders` arm with --base <head>, so only
# the plant is in the diff. The plant is a comment appended to the job's own
# restored program (a head copy differing from the base copy), then committed.
#
#   plant_jobs.sh <head> <program> <out-file> [<body-file>]
#
# The job set the arm walks is the enumeration rule's (`restoring_jobs`), not a
# list here. Writes the predictor's output, then `rc=<rc>`, to <out-file>.
set -u
head=$1 prog=$2 out=$3 body=${4:-}
root=$(git rev-parse --show-toplevel)
. "$root/tests/throwaway_git.sh"
wt=$(mktemp -d); trap 'rm -rf "$wt"' EXIT
throwaway_git_clone -q --shared --no-checkout "$root" "$wt/t" >/dev/null || exit 2
cd "$wt/t" || exit 2
throwaway_git_env
git checkout -q --detach "$head" && git update-ref refs/remotes/origin/main "$head" || exit 2
case $prog in *.mjs|*.js) printf '\n// plant\n' >> "$prog" ;; *) printf '\n# plant\n' >> "$prog" ;; esac
git commit -qam "plant $prog" || exit 2
cp "$root/tools/pr/ci_predict.py" tools/pr/ci_predict.py
extra=(); [ -n "$body" ] && extra=(--body "$body")
PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base "$head" --only graders "${extra[@]}" > "$out" 2>&1; echo "rc=$?" >> "$out"
