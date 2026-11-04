#!/bin/bash
cd /Users/timmalmstrom/hpo-seats/r10s6/orch-wt
while pgrep -f "train.sh --queue train/queue22.json" >/dev/null; do sleep 20; done
echo "s25 finished $(date -u +%FT%TZ); launching s26"
exec bash tools/audit/seat/train.sh --queue train/queue23.json --repo tvofi/heatpump_optimizer --state-dir train/s26 --mandate 6329234399 --overlap --skip-bad --bot-prs --pre-flight --approval-carry --free-holders
