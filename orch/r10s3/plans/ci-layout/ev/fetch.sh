#!/bin/sh
# Read-only GETs, paginated. Usage: sh fetch.sh <ev dir>
# For main's last 10 first-parent commits and the open PRs' heads, save every
# workflow run at that head_sha and each run's jobs (filter=all), and every check run.
set -eu
EV=$1; R=repos/tvofi/heatpump_optimizer
mkdir -p "$EV/raw"
shas=$( (head -10 "$EV/main_last12.txt" | cut -d' ' -f1; jq -r '.[].headRefOid' "$EV/open_prs.json") )
for s in $shas; do
  gh api --paginate "$R/actions/runs?head_sha=$s&per_page=100" --jq '.workflow_runs[]' | jq -s '{workflow_runs:.}' > "$EV/raw/runs_$s.json"
  for id in $(jq -r '.workflow_runs[].id' "$EV/raw/runs_$s.json"); do
    [ -s "$EV/raw/jobs_$id.json" ] || gh api "$R/actions/runs/$id/jobs?filter=all&per_page=100" > "$EV/raw/jobs_$id.json"
  done
  gh api --paginate "$R/commits/$s/check-runs?per_page=100&filter=all" --jq '.check_runs[]' | jq -s '{check_runs:.}' > "$EV/raw/checks_$s.json"
done
