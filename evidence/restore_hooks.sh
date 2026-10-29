#!/bin/bash
# usage: restore_hooks.sh <sha> <pinned>  -- CI's policy-docs base restore, then policy_lint --hooks
set -uo pipefail
sha=$1; PINNED=$2; d=$(mktemp -d)
git -C /home/user/heatpump_optimizer worktree add -q --detach $d/t $sha
cd $d/t
eval "$(bash /tmp/tmp.UfOUctH6ef/wt/.claude/hooks/session-start.sh --env-lines)"
git diff --name-only -z "$(git hash-object -t tree /dev/null)" "$PINNED" -- \
  '.claude/workflows/*.mjs' '.claude/workflows/*.py' '.claude/workflows/vendor' 'tools/audit/*.sh' \
  'tools/audit/record-predicate' 'tools/audit/round6/D11/fix/codeowners_gap.py' 'tools/policy/*.mjs' \
  'tools/policy/*.py' 'tools/pr/*.py' 'tools/policy/vendor' 'tools/pr/*.sh' 'tools/seat/*.sh' \
  'tools/coverage/*.sh' 'dev/audit/*.sh' 'tools/policy/record-predicate' \
  'dev/audit/rounds/round6/D11/fix/codeowners_gap.py' 'tests/layout.py' > $d/pinned.list
git checkout "$PINNED" --pathspec-from-file=$d/pinned.list --pathspec-file-nul
echo "restored: $(git diff --cached --name-only | tr '\n' ' ')"
node tools/policy/policy_lint.mjs --hooks 2>&1 | grep -E 'FAIL|HOOKS|passed|SELF-TEST' 
cd /; git -C /home/user/heatpump_optimizer worktree remove --force $d/t
