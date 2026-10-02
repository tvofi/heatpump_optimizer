#!/bin/bash
# R9-F10.8 RCA reproduction. Run from a full clone (git fetch --unshallow).
# Builds throwaway branches in a scratch worktree; touches nothing remote.
set -u
W=${1:-/tmp/f108-repro}
git worktree add -q "$W" f67f598a^1 && cd "$W" || exit 2
G="git -c user.name=r -c user.email=r@x"
D() { PYTHONPATH=tests/hastub python3 tests/env_drift.py "$@" 2>&1 | head -1; }

# R1: solver branch cut before #1806, merges f67f598a, keeps F6.4's claims.
git checkout -q -b solver && echo "# repro" >> custom_components/heatpump_optimizer/coordinator.py
$G commit -qam solver && $G merge -q --no-edit f67f598a
echo "R1 PR shape (CLAIM_HEAD, ref=merge-base f67f598a):"; CLAIM_HEAD=HEAD D --claims-only f67f598a
# R2: that branch merged into main, kept claims -> main's push check.
git checkout -q -b main-kept f67f598a && $G merge -q --no-ff --no-edit solver
echo "R2 main push shape, claims kept (ref HEAD^1):"; D --claims-only HEAD^1
# R3/R4: drop on the branch, then PR shape and main push shape.
git checkout -q solver && D --drop-inherited f67f598a && $G commit -qam drop
echo "R3 PR shape after drop:"; CLAIM_HEAD=HEAD D --claims-only f67f598a
git checkout -q -b main-dropped f67f598a && $G merge -q --no-ff --no-edit solver
echo "R4 main push shape after drop:"; D --claims-only HEAD^1
echo "R4 claim-file delta vs f67f598a:"; git diff --stat f67f598a HEAD -- tests/golden/
# R5: null control, docs-only branch that merged f67f598a.
git checkout -q -b docs f67f598a^1 && echo x >> docs/HANDOVER.md && $G commit -qam docs && $G merge -q --no-edit f67f598a
echo "R5 docs-only PR shape:"; CLAIM_HEAD=HEAD D --claims-only f67f598a
echo "R5 docs-only autofix:"; D --drop-inherited f67f598a
