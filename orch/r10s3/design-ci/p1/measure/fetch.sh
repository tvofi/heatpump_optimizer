#!/bin/sh
# Read-only fetch of the same REST endpoints the GitHub MCP actions_list tool wraps.
# Usage: sh fetch.sh  (writes raw/*.json)
set -e
D=$(dirname "$0")/raw; mkdir -p "$D"
A=https://api.github.com/repos/tvofi/heatpump_optimizer/actions
curl -sSf "$A/workflows/tests.yml/runs?event=pull_request&status=completed&per_page=30" > "$D/runs_pull_request.json"
curl -sSf "$A/workflows/tests.yml/runs?event=push&branch=main&status=completed&per_page=5" > "$D/runs_push_main.json"
curl -sSf "$A/workflows/tests.yml/runs?event=schedule&status=completed&per_page=5" > "$D/runs_schedule.json"
for f in runs_pull_request runs_push_main runs_schedule; do
  python3 -I -c "import json,sys;[print(r['id']) for r in json.load(open(sys.argv[1]))['workflow_runs']]" "$D/$f.json"
done | sort -u | while read id; do
  [ -s "$D/jobs_$id.json" ] || curl -sSf "$A/runs/$id/jobs?filter=latest&per_page=100" > "$D/jobs_$id.json"
done
