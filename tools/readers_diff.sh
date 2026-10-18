#!/bin/sh
# Independent reader survey (review seat). Run from a checkout of origin/main.
# Prints, per name, every tracked file outside .github/workflows naming it as a
# quoted literal or a workflow path, and whether either design's corpus names the file.
CORPUS="$1"; T1=$(mktemp); T2=$(mktemp)
names='fast (3.14)|browser|briefs|typing|mutation|closures|closure-scope|hassfest|validate-hacs|policy-docs|wave-script|pr-contract|env-matrix|Analyze (actions)|Analyze (javascript-typescript)|Analyze (python)|budget-raise-gate|arch-score|nightly-status|delivery-status|recheck-gate|composed-proof|mutation-pin-plan|record-autofix|cancel-superseded|ci-ratchet|lane-proofs|coverage-ratchet|graders-head-copy|mutation-nightly|mutation-ledger|slow|nightly-ha|closures-autofix|claims-autofix|mutation-autofix|mutation-pins|rerun-stale-contract|rerun-stale-verdict'
echo "$names" | tr '|' '\n' | while read -r n; do
  git grep -lP "[\"'\`]\Q$n\E[\"'\` ]" -- . ':!.github/workflows' ':!tests/mutation_ledger' ':!*.lock' ; done | sort -u > "$T1"
for w in tests.yml governance.yml codeql.yml hassfest.yml validate.yml pr-contract.yml arch-score.yml budget-raise-gate.yml pr-contract-rerun.yml budget-raise-gate-rerun.yml '"Tests"' '"PR contract"' '"Budget raise gate"' '"CodeQL"' '"Governance"'; do
  git grep -lF "$w" -- . ':!.github/workflows' ':!tests/mutation_ledger'; done | sort -u > "$T2"
sort -u "$T1" "$T2" | while read -r f; do
  b=$(basename "$f")
  if grep -qF "$f" "$CORPUS" || grep -qF "$b" "$CORPUS"; then echo "named   $f"; else echo "MISSED  $f"; fi
done
rm -f "$T1" "$T2"
