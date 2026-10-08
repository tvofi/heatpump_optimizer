#!/bin/bash
# Reviewer's own mutants for PR #2049 at 04b8b4bd; each applied in the detached
# review worktree, tests/entities.py run, tree restored with git checkout.
set -u
WT=/Users/timmalmstrom/hpo-seats/review-2049/wt
OUT=/Users/timmalmstrom/hpo-seats/review-2049/ev/mutants
PY=/Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python3
cd "$WT" || exit 2
mut() { # id file python-replace-expr-old new
  id=$1 f=$2 old=$3 new=$4
  OLD="$old" NEW="$new" $PY - "$f" <<'PY'
import os, sys
p = sys.argv[1]; s = open(p).read(); o, n = os.environ["OLD"], os.environ["NEW"]
assert s.count(o) == 1, (p, s.count(o)); open(p, "w").write(s.replace(o, n))
PY
  [ $? = 0 ] || { echo "RESULT $id apply-failed"; return; }
  PYTHONPATH=tests/hastub $PY tests/entities.py > "$OUT/$id.txt" 2>&1; rc=$?
  git checkout -q -- tests/
  fails=$(grep -cE '^  FAIL ' "$OUT/$id.txt")
  summ=$(grep -E 'ENTITY CHECKS' "$OUT/$id.txt" | tail -1)
  echo "RESULT $id rc=$rc $summ"
  grep -E '^\s*FAIL ' "$OUT/$id.txt" | grep -iE 'shard|pin summary|INERT|failed recording|UNRELATED|EXCLUSIVE|reddens' | head -4
}
mut M1_pin_shard_overlap tests/mutation_table.py 'order[s["anchor"]] % n == k - 1]' 'order[s["anchor"]] % n <= k - 1]'
mut M2_merge_mixed_heads tests/mutation_table.py '(heads.pop() if len(heads) == 1 else "")' '(sorted(heads)[0] if heads else "")'
mut M3_merge_status_first tests/mutation_table.py 'status = min(statuses, key=lambda s: rank.get(s, 1))' 'status = statuses[-1]'
mut M4_shard_count_floor tests/mutation_table.py 'min(MAX_SHARDS, -(-sites // SITES_PER_SHARD))' 'min(MAX_SHARDS, sites // SITES_PER_SHARD)'
mut M5_summary_remedy_on_left tests/mutation_table.py '    if lived:' '    if left:'
mut M6_stale_inert_off tests/closure.py '            inert = True' '            inert = False'
mut M7_driven_fold_off tests/closure.py 'failed |= {f"tests/{DRIVEN_BY_OTHERS[Path(s).name]}" for s in set(failed)' 'failed |= {f"tests/{DRIVEN_BY_OTHERS[Path(s).name]}" for s in set() '
mut M8_tail_check_off tests/mutation_table.py '            if (verdict[i] is None and not timed[i] and deadline is not None
                    and clock() + cost.get(script, 0.0) > deadline):' '            if (False and verdict[i] is None and not timed[i] and deadline is not None
                    and clock() + cost.get(script, 0.0) > deadline):'
echo DONE
