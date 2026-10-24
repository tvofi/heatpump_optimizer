#!/bin/bash
set -uo pipefail
RID=37189127388
cd /Users/timmalmstrom/heatpump_optimizer
for i in $(seq 1 80); do
  line=$(gh api repos/tvofi/heatpump_optimizer/actions/runs/$RID --jq '"\(.status) \(.conclusion // "-")"')
  echo "$(date -u +%T) $line"
  case "$line" in
    "completed success") break ;;
    completed*) echo "TESTS NOT GREEN: $line"; exit 1 ;;
  esac
  sleep 60
done
~/.local/state/hpo/venv-ci/bin/python3 tools/release/stamp.py --bump patch --title "EG-A2 one-formula class closure; mutation wall-clock budget; instruments into the tree; card and site polish; coverage tracer diet; nightly ledger CPU bounds" --push --push-key ~/.zcode/stamp-deploy.key 2>&1 | tail -8
