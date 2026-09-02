#!/usr/bin/env bash
# D3 quiet-window confirmation: one mutant through the full gate, as CI runs it.
#
#   d3_gate.sh <mutant-id>
#
# In the D3 worktree: branch quiet-<id> from the baseline, apply the mutant
# patch, commit it (env_drift refuses HEAD == baseline), run
#   PYTHON=<interp> GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=<baseline> GATE_JOBS=1 ./tests/run.sh
# into tools/audit/round2/quiet/D3-<id>.gate.log, then detach back to the
# baseline and delete the branch. Prints one verdict line:
#   D3_VERDICT <id> survived|killed <failing scripts> rc=<gate rc>
set -u
ID="$1"
BASE=c398fc84eec25fc44b60d74aae05b9a2da205884
WT=/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/audit-r2-D3
PY=/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/tvofi-claude/.venv/bin/python
QDIR="$(cd "$(dirname "$0")" && pwd)"
LOG="$QDIR/D3-$ID.gate.log"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
cd "$WT" || exit 2

# Preconditions: at the baseline, only tools/audit/ untracked, no branch left over.
if [ "$(git rev-parse HEAD)" != "$BASE" ]; then echo "D3_ABORT $ID not at baseline: $(git rev-parse HEAD)"; exit 2; fi
if [ -n "$(git status --short | grep -v '^?? tools/audit/')" ]; then echo "D3_ABORT $ID dirty tree"; git status --short; exit 2; fi
if git show-ref --verify --quiet "refs/heads/quiet-$ID"; then echo "D3_ABORT $ID branch quiet-$ID exists"; exit 2; fi

echo "D3_START $ID $(date '+%H:%M:%S') load=$(sysctl -n vm.loadavg)"
git checkout -q -b "quiet-$ID" "$BASE" || { echo "D3_ABORT $ID checkout failed"; exit 2; }
if ! git apply "tools/audit/round2/D3/mutants/$ID.patch"; then
  echo "D3_ABORT $ID git apply failed"; git checkout -q -- . ; git checkout -q --detach "$BASE"; git branch -D "quiet-$ID"; exit 2
fi
git -c user.name=quiet-window -c user.email=quiet@audit.local commit -q -am "quiet-window mutant $ID" || { echo "D3_ABORT $ID commit failed"; exit 2; }
echo "D3_HEAD $ID $(git rev-parse --short HEAD) $(git diff --stat "$BASE" HEAD | tail -1)"

{
  echo "QUIET_MUTANT=$ID"
  echo "QUIET_HEAD=$(git rev-parse HEAD)"
  echo "QUIET_CMD=PYTHON=$PY GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=$BASE GATE_JOBS=1 ./tests/run.sh"
  echo "QUIET_START=$(date '+%Y-%m-%d %H:%M:%S')"
  echo "QUIET_LOAD_BEFORE=$(sysctl -n vm.loadavg)"
  echo "QUIET_CPU_BEFORE=$(top -l 2 -s 1 -n 0 2>/dev/null | grep 'CPU usage' | tail -1)"
} > "$LOG"
t0=$(date +%s)
PYTHON="$PY" GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF="$BASE" GATE_JOBS=1 ./tests/run.sh >> "$LOG" 2>&1
rc=$?
t1=$(date +%s)
{
  echo "QUIET_LOAD_AFTER=$(sysctl -n vm.loadavg)"
  echo "QUIET_CPU_AFTER=$(top -l 2 -s 1 -n 0 2>/dev/null | grep 'CPU usage' | tail -1)"
  echo "QUIET_EXIT=$rc"
  echo "QUIET_WALL_S=$((t1-t0))"
} >> "$LOG"

# Back to the baseline, branch gone, tree showing only tools/audit/.
git checkout -q -- . 2>/dev/null
git checkout -q --detach "$BASE" || echo "D3_WARN $ID detach failed"
git branch -D "quiet-$ID" >/dev/null 2>&1 || echo "D3_WARN $ID branch delete failed"
# The gate's own by-products (plan payloads etc.) never land in the tree; say so if they did.
LEFT=$(git status --short | grep -v '^?? tools/audit/')
[ -n "$LEFT" ] && echo "D3_WARN $ID leftovers: $LEFT"

if grep -q '^ALL TEST SCRIPTS PASSED' "$LOG"; then
  echo "D3_VERDICT $ID survived - rc=$rc wall=$((t1-t0))s"
else
  fails=$(grep -E '^>>> FAILED:' "$LOG" | sed -E 's/^>>> FAILED: //' | tr '\n' ';')
  other=$(grep -E 'TEST SCRIPT\(S\) FAILED|LANE DID NOT FINISH|TEST NEVER RAN|UNWIRED TEST' "$LOG" | tr '\n' ';')
  echo "D3_VERDICT $ID killed [$fails] $other rc=$rc wall=$((t1-t0))s"
fi
