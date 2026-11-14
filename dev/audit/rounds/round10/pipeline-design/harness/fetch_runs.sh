#!/bin/bash
# Read-only: lists ci.yml workflow runs per UTC day into data/runs/<day>-<page>.json.
# One GET per page of 100; stops when the core bucket falls under FLOOR or after MAXCALLS.
set -u
export PATH="$HOME/.local/state/hpo/bin:$HOME/.local/state/hpo/venv-ci/bin:$PATH"
OUT=${PD_DATA:-$(cd "$(dirname "$0")/../data" && pwd)}/runs
REPO=tvofi/heatpump_optimizer
FLOOR=${FLOOR:-2400}; MAXCALLS=${MAXCALLS:-110}; calls=0
JQ='{total_count, runs: [.workflow_runs[] | {id, event, head_sha, head_branch, status, conclusion, run_attempt, created_at, run_started_at, updated_at, display_title, prs: [.pull_requests[]?.number], actor: .actor.login, trig: .triggering_actor.login}]}'
for day in "$@"; do
  for half in "T00:00:00Z..${day}T11:59:59Z" "T12:00:00Z..${day}T23:59:59Z"; do
    page=1
    while :; do
      f="$OUT/${day}-${half:1:2}-$page.json"
      if [ ! -s "$f" ]; then
        rem=$(gh api rate_limit --jq .resources.core.remaining) || { echo "rate read failed"; exit 2; }
        [ "$rem" -lt "$FLOOR" ] && { echo "STOP floor rem=$rem"; exit 3; }
        [ "$calls" -ge "$MAXCALLS" ] && { echo "STOP maxcalls"; exit 4; }
        gh api "repos/$REPO/actions/workflows/ci.yml/runs?per_page=100&page=$page&created=${day}${half}" --jq "$JQ" > "$f.tmp" && mv "$f.tmp" "$f" || { echo "FAIL $f"; exit 5; }
        calls=$((calls+1)); sleep 2
      fi
      n=$(jq '.runs|length' "$f"); tot=$(jq .total_count "$f")
      echo "$day $half page $page n=$n total=$tot calls=$calls"
      [ "$n" -lt 100 ] && break
      page=$((page+1)); [ "$page" -gt 10 ] && { echo "TRUNCATED $day $half"; break; }
    done
  done
done
echo DONE calls=$calls
