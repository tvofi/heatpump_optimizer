#!/bin/sh
# Read-only GETs (unauthenticated; the repository is public). Usage: sh measure/fetch.sh
set -e
D=$(dirname "$0")/raw; mkdir -p "$D"
R=https://api.github.com/repos/tvofi/heatpump_optimizer
g() { curl -sSf "$R/$1" > "$D/$2"; }
g rulesets rulesets.json
g rulesets/23698884 ruleset_23698884.json
g rules/branches/main rules_branch_main.json
curl -sSf "$R" > "$D/repo.json"
g "actions/workflows?per_page=100" workflows.json
curl -sS "$R/actions/permissions" > "$D/actions_permissions.json" || true
for w in governance codeql hassfest validate pr-contract arch-score budget-raise-gate; do
  g "actions/workflows/$w.yml/runs?event=pull_request&status=completed&per_page=10" "runs_${w}_pr.json"
done
g "actions/workflows/budget-raise-gate.yml/runs?event=pull_request_review&per_page=10" runs_brg_review.json
g "actions/workflows/budget-raise-gate-rerun.yml/runs?per_page=10" runs_brg_rerun.json
g "actions/workflows/pr-contract-rerun.yml/runs?per_page=30" runs_prc_rerun.json
g "actions/runs?event=merge_group&per_page=10" runs_merge_group.json
g "actions/runs?status=action_required&per_page=30" runs_action_required.json
