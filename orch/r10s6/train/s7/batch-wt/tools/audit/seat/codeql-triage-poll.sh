#!/bin/bash
# Dismiss the 3 #1769 evidence-alerts once GitHub attaches them, re-run CodeQL, report.
R=tvofi/heatpump_optimizer; PATHS=("dev/audit/rounds/round8/evidence/D11/s2_release_gate.py" "dev/audit/rounds/round9/D11/s1/privileged_pr_code.py" "dev/audit/rounds/round9/D8/leads/l2_d8_leads.py")
for i in $(seq 1 36); do
  sleep 600
  FOUND=$(gh api "repos/$R/code-scanning/alerts?state=open&per_page=100" --jq '[.[] | select([.most_recent_instance.location.path] | inside(["'"${PATHS[0]}"'","'"${PATHS[1]}"'","'"${PATHS[2]}"'"]))] | map("\(.number) \(.most_recent_instance.location.path)") | .[]' 2>/dev/null)
  N=$(echo "$FOUND" | grep -c '^[0-9]' 2>/dev/null)
  echo "poll $i: open evidence alerts = $N"
  if [ "${N:-0}" -ge 3 ]; then
    for num in $(echo "$FOUND" | awk '{print $1}'); do
      gh api -X PATCH "repos/$R/code-scanning/alerts/$num" -f state=dismissed -f dismiss_reason=used_in_tests -f comment="Audit-evidence harness (register tranche 1, PR #1769); frozen byte-identity to 79aa98ec/6f58e33e. Dismissed under tvofi's recorded mandate decision 2026-09-29." > /dev/null && echo "dismissed $num"
    done
    # find the failed CodeQL run at the head and rerun it
    JOB=$(gh api "repos/$R/checks/runs" -X GET 2>/dev/null | head -c 0; echo 109534061903)
    RUNID=$(gh api "repos/$R/actions/jobs/$JOB" --jq .run_id 2>/dev/null)
    [ -n "$RUNID" ] && gh run rerun "$RUNID" --repo $R --failed 2>&1 | tail -1 && echo "reran run $RUNID"
    sleep 120
    H=3ad6e085accc2254dbf816ae1a105eb7caeb925c
    for j in $(seq 1 20); do
      REDS=$(gh api "repos/$R/commits/$H/check-runs?per_page=100" --jq '[.check_runs | group_by(.name)[] | sort_by(.started_at) | last | select(.conclusion=="failure")] | .[].name' 2>/dev/null | tr '\n' ' ')
      [ -z "$REDS" ] && { echo "CODEQL-TRIAGE-DONE: head green"; exit 0; }
      sleep 60
    done
    echo "CODEQL-TRIAGE-PARTIAL: alerts dismissed but checks still red: $REDS"; exit 1
  fi
done
echo "CODEQL-TRIAGE-TIMEOUT: alerts never attached within 6h"; exit 1
