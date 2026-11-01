#!/bin/bash
cd /Users/timmalmstrom/hpo-seats/r10s6/orch-wt
export PATH=/Users/timmalmstrom/hpo-seats/r10s6/orch-wt/tools/audit/seat/shims:$PATH
git fetch origin 2>&1 | tail -2
if [ -z "$(git status --porcelain --untracked-files=no)" ]; then git checkout --detach origin/main 2>&1 | tail -1; else echo "REFRESH SKIPPED"; fi
echo "HEAD $(git rev-parse HEAD) origin/main $(git rev-parse origin/main)"
python3 tools/audit/seat/queue_pre_flight.py train/queue24.json --repo tvofi/heatpump_optimizer 2>&1 | cut -c1-220
exec bash tools/audit/seat/train.sh --queue train/queue24.json --repo tvofi/heatpump_optimizer --state-dir train/s27 --mandate 6329234399 --overlap --skip-bad --bot-prs --pre-flight --approval-carry --free-holders
