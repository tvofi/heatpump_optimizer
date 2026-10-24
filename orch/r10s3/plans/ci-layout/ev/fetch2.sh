#!/bin/sh
# Read-only GETs, paginated. Usage: sh fetch2.sh <ev dir>
# The merged PRs' final heads (merged_heads.txt): runs, jobs, check runs.
# And for each fix PR, its pull_request-event Tests runs (one per head pushed) and its commits.
set -eu
EV=$1; R=repos/tvofi/heatpump_optimizer
while read pr s br; do
  gh api --paginate "$R/actions/runs?head_sha=$s&per_page=100" --jq '.workflow_runs[]' | jq -s '{workflow_runs:.}' > "$EV/raw/runs_$s.json"
  for id in $(jq -r '.workflow_runs[].id' "$EV/raw/runs_$s.json"); do
    [ -s "$EV/raw/jobs_$id.json" ] || gh api "$R/actions/runs/$id/jobs?filter=all&per_page=100" > "$EV/raw/jobs_$id.json"
  done
  gh api --paginate "$R/commits/$s/check-runs?per_page=100&filter=all" --jq '.check_runs[]' | jq -s '{check_runs:.}' > "$EV/raw/checks_$s.json"
  b=${br#tvofi/}
  gh api --paginate "$R/actions/workflows/tests.yml/runs?branch=$b&per_page=100" --jq '.workflow_runs[]|{id,event,head_sha,created_at,updated_at,conclusion,run_attempt}' | jq -s . > "$EV/raw/branchruns_$pr.json"
done < "$EV/merged_heads.txt"
