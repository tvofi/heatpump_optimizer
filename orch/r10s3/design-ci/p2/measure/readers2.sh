#!/bin/sh
# Phase-2 reader survey: who reads a workflow NAME, a workflow FILE, a non-Tests
# check name, the dispatch lists, or a per-file structural pin. Run from a checkout
# of origin/main: sh <probe>/measure/readers2.sh > <probe>/measure/readers2.txt
S="tools tests .github dev/governance .claude/skills .claude/workflows CLAUDE.md AGENTS.md dev/programme/HANDOVER.md"
X=":!tests/mutation_ledger/survivor_triage"
hdr() { printf '\n=== %s\n' "$1"; }
hdr "1. workflow display names (quoted), outside the workflow that owns them"
for n in "Tests" "Governance" "CodeQL" "Hassfest" "Validate" "PR contract" "Architecture score" "Budget raise gate" "PR contract re-run" "Budget raise gate re-run"; do
  printf -- '--- "%s": ' "$n"; git grep -nF "\"$n\"" -- $S "$X" | wc -l
  git grep -nF "\"$n\"" -- $S "$X" | cut -c1-160
done
hdr "2. workflow files named by path or basename (dispatch lists, readers)"
for f in tests.yml governance.yml codeql.yml hassfest.yml validate.yml pr-contract.yml arch-score.yml budget-raise-gate.yml pr-contract-rerun.yml budget-raise-gate-rerun.yml; do
  printf -- '--- %s: files ' "$f"; git grep -lF "$f" -- $S "$X" | wc -l
  git grep -lF "$f" -- $S "$X" | sed 's/^/      /'
done
hdr "3. gh workflow run / dispatch sites"
git grep -nE "gh workflow run|workflow run \"\\\$wf\"|/dispatches|DISPATCH *=|_AF_DISPATCHED" -- $S "$X" | cut -c1-200
hdr "4. non-Tests required check names as quoted literals, outside .github/workflows"
for n in hassfest validate-hacs policy-docs wave-script pr-contract env-matrix "Analyze (actions)" "Analyze (javascript-typescript)" "Analyze (python)" budget-raise-gate arch-score; do
  printf -- "--- '%s': " "$n"; git grep -nP "[\"'\`]\Q$n\E[\"'\`]" -- $S "$X" ':!.github/workflows' | wc -l
  git grep -nP "[\"'\`]\Q$n\E[\"'\`]" -- $S "$X" ':!.github/workflows' | cut -c1-170 | head -25
done
hdr "5. required-context lists and counts"
git grep -nE "required-contexts|REQ17|PR_ONLY *=|RULESET *=|main-protect-checks|23698884|17 required|seventeen" -- $S "$X" | cut -c1-170
hdr "6. structural pins in tests/entities.py keyed on a workflow file"
grep -noE '_GOV_FILES = \[[^]]*\]|\.github/workflows/[a-z-]+\.yml' tests/entities.py | awk -F: '{print $3}' | sort | uniq -c
grep -nE 'concurrency|cancel-in-progress|pull_request: edited|"edited"|merge_group' tests/entities.py | cut -c1-150 | head -60
hdr "7. workflow_call / uses: ./ today"
git grep -nE "workflow_call|uses: \./\.github" -- .github | cut -c1-150
hdr "8. app-held run approval sites (HPO_RUNS) and loop-guard subjects"
git grep -nE "HPO_RUNS_PEM|action_required" -- .github tools tests | cut -c1-150 | head -40
