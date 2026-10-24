#!/bin/bash
H=ea459c0b5f6b4d753394935dfb49e5386480fd40; R=tvofi/heatpump_optimizer
while true; do
 s=$(gh api repos/$R/commits/$H/check-runs --jq '.check_runs[]|select(.name=="codeql / Analyze (python)")|.status+" "+(.conclusion//"")')
 echo "$(date +%H:%M:%S) codeql: $s"
 case "$s" in completed*) break;; esac
 sleep 300
done
sleep 60
gh run rerun 40099071633 --failed -R $R && echo "RERUN pr-contract run 40099071633"
sleep 240
gh api repos/$R/commits/$H/check-runs --jq '.check_runs[]|select(.name=="gate" or .name=="pr-contract / pr-contract")|"AFTER \(.name) \(.status) \(.conclusion)"'
