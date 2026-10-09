#!/bin/bash
# Reviewer CI poller for PR #2074 head d7c830c2fa99ee2428f86aa469a7da540f21eeb9.
# Polls the check-runs API at the head every 300 s (shared quota, tvofi 2026-10-07)
# and appends a one-line-per-check snapshot; exits when nothing is queued/in_progress
# or after MAX_LOOPS.
SHA=d7c830c2fa99ee2428f86aa469a7da540f21eeb9
E=/Users/timmalmstrom/hpo-seats/review-2074/evidence
MAX_LOOPS=${1:-16}
i=0
while [ "$i" -lt "$MAX_LOOPS" ]; do
  i=$((i + 1))
  out=$(gh api "repos/tvofi/heatpump_optimizer/commits/$SHA/check-runs?per_page=100" \
        --jq '.check_runs[] | [.name, .status, (.conclusion // "-")] | @tsv' 2>&1)
  if printf '%s\n' "$out" | grep -qE 'queued|in_progress'; then
    live=$(printf '%s\n' "$out" | grep -cE 'queued|in_progress')
    echo "$(date -u +%H:%M:%SZ) loop=$i STILL-RUNNING live=$live" >> "$E/ci_poll.log"
    printf '%s\n' "$out" | sort > "$E/checkruns_latest.tsv"
    sleep 300
  else
    echo "$(date -u +%H:%M:%SZ) loop=$i SETTLED" >> "$E/ci_poll.log"
    printf '%s\n' "$out" | sort > "$E/checkruns_latest.tsv"
    printf '%s\n' "$out" | sort > "$E/checkruns_final.tsv"
    exit 0
  fi
done
echo "$(date -u +%H:%M:%SZ) loop=$i MAXLOOPS-REACHED (not settled)" >> "$E/ci_poll.log"
