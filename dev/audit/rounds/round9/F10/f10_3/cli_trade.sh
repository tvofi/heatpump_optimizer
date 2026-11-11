#!/bin/sh
# F10.3 end-to-end: tests/mutation_table.py's own CLI on a committed trade diff
# (adds an unpinned guard, deletes another unpinned guard in the same file, so
# the count is flat), then on a comment-only diff (the null control).
# Run from a detached worktree at the head; $PY is the interpreter.
# On origin/main, whose CLI predates the per-site rule, pass EXTRA='--max 0'.
set -e
F=custom_components/heatpump_optimizer/wood_fuel.py
BASE=$(git rev-parse HEAD)
$PY - "$F" <<'PY'
import sys; sys.path.insert(0, "tests")
import mutation_table as mt
f = sys.argv[1]
u = [s for s in mt.unpinned_sites(mt.load_budgets(), mt.inventory())
     if s["file"] == f and s["kind"] == "GUARD_OFF"]
victim = u[0]
lines = open(f).read().splitlines(keepends=True)
lines[victim["line"] - 1] = lines[victim["line"] - 1].replace(victim["old"].strip(), "while False:")
i = next(k for k, l in enumerate(lines) if l.startswith("def "))
j = i
while not lines[j].rstrip().endswith(":"):
    j += 1
lines.insert(j + 1, "    if f1646_trade is None:\n        return None\n")
open(f, "w").write("".join(lines))
print("traded away:", victim["line"], victim["old"].strip())
PY
git -c user.name=demo -c user.email=demo@x commit -qam "demo: trade"
echo "== trade =="; PYTHONPATH=tests/hastub $PY tests/mutation_table.py --scope changed --base "$BASE" $EXTRA 2>&1 | grep -E 'ADDED UNPINNED|MUTATION TABLE|unpinned site' | head -8; echo "rc=$?"
git reset -q --hard "$BASE"
sed -i '1i # null control: a comment' "$F"
git -c user.name=demo -c user.email=demo@x commit -qam "demo: null"
echo "== null =="; PYTHONPATH=tests/hastub $PY tests/mutation_table.py --scope changed --base "$BASE" --max 0 2>&1 | grep -E 'ADDED UNPINNED|MUTATION TABLE|unpinned site' | head -8
git reset -q --hard "$BASE"
