#!/usr/bin/env bash
# Replay tools/pr/ci_predict.py over every commit of the given pull requests and
# set its verdict beside what CI's `closures` and `mutation` jobs concluded at
# that commit (R9-RO-11's pre-study and null control).
#
#   tools/audit/seat/ci_predict_replay.sh <scratch-dir> <pr>...
#
# One row per commit that carries a `closures` or `mutation` check run:
#   pr sha closures:<ci>/<predicted> mutation:<ci>/<predicted>
# where <ci> is the check run's conclusion and <predicted> the number of
# PREDICT lines for that job. A green CI job beside a non-zero prediction is a
# false alarm; a red one beside zero is a miss -- read the job's log for why
# (an inherited main red, or a read the predictor cannot see). The predictor
# run is this checkout's, over a detached worktree of each commit, against that
# commit's own fork point from origin/main, which is what CI compared.
# API and worktree failures are counted and printed, never swallowed.
set -uo pipefail
here=$(cd "$(dirname "$0")/../../.." && pwd)
scratch=${1:?scratch dir}; shift
repo=${REPO:-tvofi/heatpump_optimizer}
mkdir -p "$scratch"
fails=0
for pr in "$@"; do
  for sha in $(gh api "repos/$repo/pulls/$pr/commits" --paginate -q '.[].sha'); do
    runs=$(gh api "repos/$repo/commits/$sha/check-runs?per_page=100" --paginate \
      -q '.check_runs[]|[.name,(.conclusion // "pending")]|@tsv' 2>/dev/null) || { fails=$((fails+1)); continue; }
    cl=$(printf '%s\n' "$runs" | awk -F'\t' '$1=="closures"{print $2}' | sort -u | paste -sd+ -)
    mu=$(printf '%s\n' "$runs" | awk -F'\t' '$1=="mutation"{print $2}' | sort -u | paste -sd+ -)
    [ -n "$cl$mu" ] || continue
    wt="$scratch/wt-$sha"
    [ -d "$wt" ] || git -C "$here" worktree add -q --detach "$wt" "$sha" 2>/dev/null || { fails=$((fails+1)); continue; }
    out=$(cd "$wt" && python3 "$here/tools/pr/ci_predict.py" --base origin/main 2>&1)
    pc=$(printf '%s\n' "$out" | grep -c '^PREDICT closures')
    pm=$(printf '%s\n' "$out" | grep -c '^PREDICT mutation')
    pf=$(printf '%s\n' "$out" | grep -c '^PREDICT fast')
    printf '%s\t%s\tclosures:%s/%s\tmutation:%s/%s\tfast-unclassified:%s\n' \
      "$pr" "${sha:0:10}" "${cl:-none}" "$pc" "${mu:-none}" "$pm" "$pf"
    printf '%s\n' "$out" > "$scratch/predict-${sha:0:10}.txt"
    git -C "$here" worktree remove --force "$wt" 2>/dev/null
  done
done
echo "replay failures (API or worktree): $fails" >&2
