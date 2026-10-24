#!/bin/sh
# Read-only GETs, round 2. Needs measure/raw from fetch.sh, plus phase 1's
# raw/runs_pull_request.json copied to raw/tests_runs_pull_request.json.
# Usage: sh measure/fetch2.sh
set -e
D=$(dirname "$0")/raw
R=https://api.github.com/repos/tvofi/heatpump_optimizer
# 1. jobs of every PR run listed for the six non-Tests workflows and the gate
for w in governance codeql hassfest validate pr-contract arch-score budget-raise-gate; do
  python3 -I -c "import json,sys;[print(r['id']) for r in json.load(open(sys.argv[1]))['workflow_runs']]" "$D/runs_${w}_pr.json"
done | sort -u | while read id; do
  [ -s "$D/jobs_$id.json" ] || curl -sSf "$R/actions/runs/$id/jobs?filter=latest&per_page=100" > "$D/jobs_$id.json"
done
# 2. the 20 PR heads phase 1 measured: every check run, and every run, at each
python3 -I -c "import json,sys;[print(r['head_sha']) for r in json.load(open(sys.argv[1]))['workflow_runs'][:22]]" "$D/tests_runs_pull_request.json" | sort -u | while read sha; do
  [ -s "$D/checks_$sha.json" ] || curl -sSf "$R/commits/$sha/check-runs?per_page=100&filter=all" > "$D/checks_$sha.json"
  [ -s "$D/runsat_$sha.json" ] || curl -sSf "$R/actions/runs?head_sha=$sha&per_page=100" > "$D/runsat_$sha.json"
done
# 3. token-permission baseline: the 'Set up job' header of each job of one recent
#    completed pull_request run per workflow (first 60 log lines only)
mkdir -p "$D/logs"
for w in tests governance codeql hassfest validate pr-contract arch-score budget-raise-gate; do
  f="$D/runs_${w}_pr.json"; [ "$w" = tests ] && f="$D/tests_runs_pull_request.json"
  id=$(python3 -I -c "import json,sys;rs=json.load(open(sys.argv[1]))['workflow_runs'];ok=[r for r in rs if r['conclusion']=='success'] or [r for r in rs if r['conclusion']];print(ok[0]['id'])" "$f")
  [ -s "$D/jobs_$id.json" ] || curl -sSf "$R/actions/runs/$id/jobs?filter=latest&per_page=100" > "$D/jobs_$id.json"
  echo "$w $id" >> "$D/logs/baseline_runs.txt.tmp"
  python3 -I -c "import json,sys;[print(j['id'],j['conclusion']) for j in json.load(open(sys.argv[1]))['jobs']]" "$D/jobs_$id.json" | while read jid c; do
    [ "$c" = skipped ] && continue
    [ -s "$D/logs/head_$jid.txt" ] || { curl -sSL "$R/actions/jobs/$jid/logs" 2>/dev/null | head -60 > "$D/logs/head_$jid.txt" || true; }
  done
done
sort -u "$D/logs/baseline_runs.txt.tmp" > "$D/logs/baseline_runs.txt"; rm -f "$D/logs/baseline_runs.txt.tmp"
