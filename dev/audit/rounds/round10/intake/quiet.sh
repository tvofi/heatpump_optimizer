#!/bin/bash
# D3 quiet window (audit-find.js, phase 'Quiet window'): the full gate, once per
# D3 mutant that survived a finder seat's pre-screen, plus a NULL arm (a marker
# commit, no edit) so a script that is red on this machine with no mutant is
# never counted as a kill.
#
# Usage: bash dev/audit/rounds/round10/intake/quiet.sh <repo> <out_dir> [ID ...]
#   repo     a checkout holding the baseline commit (worktrees are added from it)
#   out_dir  absolute directory for worktrees, logs and quiet.tsv
#   ID       subset of the arms below (default: all, NULL first)
# Each arm: a worktree on a local branch quiet-r10-<id> at the baseline, the
# one-line edit applied and committed so HEAD moves off the baseline, then
#   GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=<baseline> GATE_JOBS=1 ./tests/run.sh
# under the gate lease (label quiet-r10, renewed between arms), the five BLAS
# thread variables at 1. The worktree and branch are removed after the arm.
# Output: <out_dir>/<id>.log per arm and <out_dir>/quiet.tsv with
#   id  file:line  rc  failed_scripts  load1_start  load1_end  seconds
# A mutant is KILLED when its failed set holds a script the NULL arm passed.
set -u
REPO=${1:?repo}; OUT=${2:?out_dir}; shift 2
BASE=$(git -C "$REPO" rev-parse 17f1c55fad1b)
export PATH="$HOME/.local/state/hpo/bin:$PATH"
for v in OMP_NUM_THREADS OPENBLAS_NUM_THREADS MKL_NUM_THREADS NUMEXPR_NUM_THREADS VECLIB_MAXIMUM_THREADS; do export $v=1; done
mkdir -p "$OUT"
# id|file|line|old|new|  (the closing | keeps a trailing space in new; from the D3 seats' reports at the baseline)
ARMS='NULL|||||
M08|custom_components/heatpump_optimizer/coordinator.py|6522| and | or |
M01|custom_components/heatpump_optimizer/optimizer.py|5541| and | or |
M03|custom_components/heatpump_optimizer/optimizer.py|5557| and | or |
M35|custom_components/heatpump_optimizer/ledger.py|306|if dropped:|if not (dropped):|
M26|custom_components/heatpump_optimizer/snapshots.py|239|if dropped:|if not (dropped):|'
WANT="$*"
load1() { sysctl -n vm.loadavg 2>/dev/null | awk '{print $2}'; }
LOCK="python3 $REPO/tests/gate_lock.py"
$LOCK take --label quiet-r10 --lease-seconds 14400 --owner-pid $$ || { echo "lease refused"; exit 3; }
trap '$LOCK release --label quiet-r10 >/dev/null 2>&1' EXIT
[ -f "$OUT/quiet.tsv" ] || printf 'id\tsite\trc\tfailed\tload1_start\tload1_end\tseconds\n' > "$OUT/quiet.tsv"
echo "$ARMS" | while IFS='|' read -r id file line old new _rest; do
  [ -n "$WANT" ] && ! echo " $WANT " | grep -q " $id " && continue
  $LOCK renew --label quiet-r10 --lease-seconds 14400 --owner-pid $$ >/dev/null
  wt="$OUT/wt-$id"; br="quiet-r10-$id"
  git -C "$REPO" worktree remove --force "$wt" 2>/dev/null; git -C "$REPO" branch -D "$br" 2>/dev/null
  git -C "$REPO" worktree add -q -b "$br" "$wt" "$BASE" || { echo "worktree add failed for $id"; continue; }
  if [ "$id" = NULL ]; then
    git -C "$wt" -c user.name=quiet -c user.email=quiet@invalid commit -q --allow-empty -m "quiet-r10 NULL marker"
  else
    python3 - "$wt/$file" "$line" "$old" "$new" <<'PY' || { echo "edit failed for $id"; continue; }
import sys
p, ln, old, new = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
src = open(p).read().split("\n")
assert src[ln - 1].count(old) == 1, (p, ln, src[ln - 1])
src[ln - 1] = src[ln - 1].replace(old, new)
open(p, "w").write("\n".join(src))
PY
    git -C "$wt" -c user.name=quiet -c user.email=quiet@invalid commit -q -am "quiet-r10 $id $file:$line"
  fi
  l0=$(load1); t0=$(date +%s)
  (cd "$wt" && GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF="$BASE" GATE_JOBS=1 HPO_GATE_LOCK_LABEL=quiet-r10 ./tests/run.sh) > "$OUT/$id.log" 2>&1
  rc=$?
  t1=$(date +%s); l1=$(load1)
  failed=$(grep -E '^>>> FAILED: ' "$OUT/$id.log" | sed 's/^>>> FAILED: //' | sort -u | tr '\n' ';')
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$id" "${file:+$file:$line}" "$rc" "$failed" "$l0" "$l1" "$((t1 - t0))" >> "$OUT/quiet.tsv"
  git -C "$REPO" worktree remove --force "$wt"; git -C "$REPO" branch -D "$br" >/dev/null
done
