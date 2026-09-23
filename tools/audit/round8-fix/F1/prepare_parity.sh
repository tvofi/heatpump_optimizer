#!/usr/bin/env bash
# R8 F1(a)(b) -- does a finder tree that tools/audit/prepare_baseline.sh
# prepares still run the gate the way the baseline does?
#
# (a) prepare_baseline.sh's own finders_can_start refusal refused its output:
#     the strip removed round4/D11/governance_cost.py and round4/D6/claims.json,
#     which tests/entities.py opens unguarded.
# (b) past (a), tests/entities.py failed checks in a stripped tree that pass in
#     an unstripped one.
#
# METRICS, all from one run of the script under test at the checkout's HEAD:
#   prepare_rc               prepare_baseline.sh's exit status (2 = refused)
#   closure_paths_missing    tools/audit/round*/ paths tests/closures.json names
#                            that are absent, summed over the export and every
#                            worktree (the PHANTOM check in tests/closure.py
#                            refuses any such path)
#   entities_extra_fails     --entities only: failing tests/entities.py check
#                            names in the stripped tree that are not failing in
#                            its unstripped control, for the export (control: a
#                            plain `git archive` of the same commit) and the D0
#                            worktree (control: the clone itself, same .git
#                            and origin)
#
# COMMAND (from the checkout under test; SCRATCH must not exist):
#   tools/audit/round8-fix/F1/prepare_parity.sh SCRATCH [--entities]
# EXPECTED at a fixed head (tolerance: exact):
#   RESULT prepare_rc=0
#   RESULT closure_paths_missing=0
#   RESULT entities_extra_fails_export=0
#   RESULT entities_extra_fails_worktree=0
# Exit status 1 when any of them is not.
#
# PERTURBATION: at the merge base (the strip that removed every earlier round)
# -> prepare_rc=2, and the harness stops there. Direction: up.
# NULL CONTROL: the controls above; a check that fails in both trees (an
# origin that is a local path, for instance) is not counted.
set -uo pipefail
SCRATCH="${1:?scratch dir (must not exist)}"; ENT="${2:-}"
PY="${PYTHON:-$(command -v python3)}"   # prepare_baseline.sh wants an executable path
SRC="$(git rev-parse --show-toplevel)"; HEAD="$(git -C "$SRC" rev-parse HEAD)"
[ -e "$SCRATCH" ] && { echo "refusing: $SCRATCH exists"; exit 2; }
mkdir -p "$SCRATCH"
git clone -q --shared --no-checkout "$SRC" "$SCRATCH/repo"
git -C "$SCRATCH/repo" checkout -q "$HEAD"
out="$( cd "$SCRATCH/repo" && PYTHON="$PY" bash tools/audit/prepare_baseline.sh 8 "$HEAD" 2>&1 )"
rc=$?
printf '%s\n' "$out" | grep -E '^(RESULT|refusing)' | sed 's/^/  prepare: /'
echo "RESULT prepare_rc=$rc"
[ "$rc" -eq 0 ] || exit 1

trees=("$SCRATCH/audit-r8-baseline"); for d in "$SCRATCH"/audit-r8-D*; do trees+=("$d"); done
missing=0
for t in "${trees[@]}"; do
  n=$("$PY" - "$t" <<'PY'
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
names = {f for fs in json.loads((root / "tests/closures.json").read_text())["closures"].values()
         for f in fs if f.startswith("tools/audit/round")}
print(sum(not (root / f).is_file() for f in names))
PY
)
  missing=$((missing + n))
done
echo "RESULT closure_paths_missing=$missing"
status=0; [ "$missing" -eq 0 ] || status=1
[ "$ENT" = "--entities" ] || exit "$status"

mkdir -p "$SCRATCH/control-export"
git -C "$SCRATCH/repo" archive "$HEAD" | tar -x -C "$SCRATCH/control-export"
run() { ( cd "$1" && PYTHONPATH=tests/hastub "$PY" tests/entities.py >"$2" 2>&1 ); }
run "$SCRATCH/audit-r8-baseline" "$SCRATCH/ent-export.log" &
run "$SCRATCH/control-export" "$SCRATCH/ent-control-export.log" &
run "$SCRATCH/audit-r8-D0" "$SCRATCH/ent-worktree.log" &
run "$SCRATCH/repo" "$SCRATCH/ent-control-worktree.log" &
wait
fails() {
  # A check line is two spaces, FAIL, the name; a traceback that ended the run
  # is a failure too, and is named by its last line.
  grep -E '^  FAIL ' "$1" | sed -E 's/  \[.*$//' | sort -u
  tail -1 "$1" | grep -E 'Error|Traceback' | sed 's/^/CRASH /'
}
for pair in "export control-export" "worktree control-worktree"; do
  set -- $pair
  extra=$(comm -23 <(fails "$SCRATCH/ent-$1.log") <(fails "$SCRATCH/ent-$2.log"))
  n=$(printf '%s' "$extra" | grep -c . || true)
  echo "RESULT entities_extra_fails_$1=$n"
  [ -n "$extra" ] && printf '%s\n' "$extra" | sed 's/^/  /'
  echo "  totals: $(tail -1 "$SCRATCH/ent-$1.log") | control: $(tail -1 "$SCRATCH/ent-$2.log")"
  [ "$n" -eq 0 ] || status=1
done
exit "$status"
