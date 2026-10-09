#!/bin/bash
# Reviewer CI poller for PR #2074 round 2, head 96497ffc694302b814eecaeea2710bfdbebf6678.
# Polls the check-runs API at the head every 300 s (shared quota, tvofi 2026-10-07),
# backs off on 403; exits when nothing is queued/in_progress or after MAX_LOOPS.
SHA=96497ffc694302b814eecaeea2710bfdbebf6678
E=/Users/timmalmstrom/hpo-seats/review-2074b/evidence
MAX_LOOPS=${1:-20}
i=0
while [ "$i" -lt "$MAX_LOOPS" ]; do
  i=$((i + 1))
  out=$(gh api "repos/tvofi/heatpump_optimizer/commits/$SHA/check-runs?per_page=100" \
        --jq '.check_runs[] | [.name, .status, (.conclusion // "-")] | @tsv' 2>&1)
  if printf '%s\n' "$out" | grep -qi 'HTTP Error 403\|rate limit'; then
    echo "$(date -u +%H:%M:%SZ) loop=$i 403/rate-limited, backing off" >> "$E/ci_poll.log"
    sleep 600
    continue
  fi
  n=$(printf '%s\n' "$out" | grep -c .)
  if printf '%s\n' "$out" | grep -qE 'queued|in_progress'; then
    live=$(printf '%s\n' "$out" | grep -cE 'queued|in_progress')
    echo "$(date -u +%H:%M:%SZ) loop=$i STILL-RUNNING checks=$n live=$live" >> "$E/ci_poll.log"
    printf '%s\n' "$out" | sort > "$E/checkruns_latest.tsv"
    sleep 300
  else
    echo "$(date -u +%H:%M:%SZ) loop=$i SETTLED checks=$n" >> "$E/ci_poll.log"
    printf '%s\n' "$out" | sort > "$E/checkruns_latest.tsv"
    printf '%s\n' "$out" | sort > "$E/checkruns_final.tsv"
    exit 0
  fi
done
echo "$(date -u +%H:%M:%SZ) loop=$i MAX_LOOPS-REACHED (not settled)" >> "$E/ci_poll.log"
