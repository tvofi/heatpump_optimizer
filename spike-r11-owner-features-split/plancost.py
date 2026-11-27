"""Spike: the plan-mode fork drive's no-fail-fast ceiling from recorded span seconds.

    PYTHONPATH=tests/hastub:tests SPIKE=<swap_run dir> python3 plancost.py LINES.json PARTS.json SCRIPT

Per function-body row: seconds of its reaching spans' needs closure from its first reaching span
on (the server ran everything before it). Module-level row: the header plus the whole closure.
"""
import json
import os
import sys
from collections import Counter

sys.path[:0] = ["tests", os.environ["SPIKE"], os.path.dirname(os.path.abspath(__file__))]
import case_select as cs  # noqa: E402
import forkdrive  # noqa: E402

lines_path, parts_path, script = sys.argv[1:4]
parts = json.load(open(parts_path))
rows, spans = forkdrive.rows_for(lines_path, parts, script)
ent = cs.entry(cs.load(), "tests/features.py")["spans"]
sec = {s.id: ent.get(s.id, {}).get("seconds", 0.0) for s in spans}
idx = {s.id: i for i, s in enumerate(spans)}
needs = {k: set(v.get("needs", [])) for k, v in ent.items()}
head = float(os.environ.get("HEAD_S", "6.9"))
tot, n, sizes = Counter(), Counter(), []
for r in rows:
    if r["first"] is None:
        continue
    plan, todo = set(), list(r["reach"])
    while todo:
        x = todo.pop()
        if x not in plan:
            plan.add(x)
            todo += list(needs.get(x, ()))
    k = "module" if r["module_level"] else "function"
    lo = -1 if k == "module" else r["first"]
    c = sum(sec[x] for x in plan if x in idx and idx[x] >= lo) + (head if k == "module" else 0)
    tot[k] += c
    n[k] += 1
    sizes.append(len(plan))
sizes.sort()
print("rows", dict(n), "ceiling CPU-s", {k: round(v) for k, v in tot.items()}, "total", round(sum(tot.values())),
      "plan spans median", sizes[len(sizes) // 2])
