#!/bin/bash
# CI watcher v2: alerts only on NEW states (per-PR signature file), exits 1 with a report.
R=tvofi/heatpump_optimizer; S=${CI_WATCH_STATE:-/private/tmp/audit-7/ci-watch-state}; mkdir -p $S
while true; do
  OUT=""
  for n in $(gh pr list --repo $R --state open --json number --jq '.[].number'); do
    sig_file="$S/$n"
    H=$(gh pr view $n --repo $R --json headRefOid,mergeable --jq '.headRefOid + " " + .mergeable' 2>/dev/null)
    sha=$(echo $H | cut -d' ' -f1); mb=$(echo $H | cut -d' ' -f2)
    issue=""
    [ "$mb" = "CONFLICTING" ] || [ "$mb" = "DIRTY" ] && issue=" | $mb — needs local main absorb"
    reds=$(gh api "repos/$R/commits/$sha/check-runs?per_page=100" --jq '[.check_runs | group_by(.name)[] | sort_by(.started_at) | last | select(.conclusion=="failure")] | .[].name' 2>/dev/null | tr '\n' ' ')
    [ -n "$reds" ] && issue="$issue | RED: $reds"
    total=$(gh api "repos/$R/commits/$sha/check-runs?per_page=100" --jq '.check_runs | length' 2>/dev/null)
    [ "$total" = "0" ] && [ "$mb" = "MERGEABLE" ] && issue="$issue | STALLED zero-runs"
    sig="${sha:0:8}${issue}"
    if [ -n "$issue" ] && [ "$(cat $sig_file 2>/dev/null)" != "$sig" ]; then
      OUT="$OUT\nPR#$n at ${sha:0:8}:$issue"
      echo "$sig" > $sig_file
    fi
    [ -z "$issue" ] && rm -f $sig_file
  done
  if [ -n "$OUT" ]; then echo -e "CI-WATCH ALERT ($(date -u +%H:%MZ)): NEW state(s):$OUT"; exit 1; fi
  sleep 300
done
