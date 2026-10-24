#!/usr/bin/env python3
"""#1748 move simulation (the DHW planner extraction #1743 plans), run in a
scratch worktree of the branch head: the 19 methods EG-B5-DESIGN.md lists
leave optimizer.py's HeatPumpOptimizer verbatim for a new dhw_planner.py
class DhwPlanner, and `_pin_is_free` leaves for manual_plan.py; the ledger is
re-keyed (completeness 0). Prints the per-site verdict under the prototype's
identity (no diff sides, 8eda51a2) and under this branch's (diff sides).

  cd <worktree> && python3 move_1748.py [--new-guard]
--new-guard also inserts one genuinely new unpinned guard inside a moved
method: it must stay refused.
"""
import ast, subprocess, sys
from pathlib import Path
ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
import mutation_table as mt  # noqa: E402

MOVE = ["_dhw_planning_prices", "_baseline_dhw_economics", "_effective_dhw_windows",
        "_dhw_legionella_due", "_dhw_legionella_ceilings", "_dhw_legionella_plan",
        "_dhw_coil_wood_forecast", "_dhw_planner_draws", "_dhw_window_floors",
        "_build_dhw_requirements", "_dhw_cop_profile", "_plan_dhw_min_cost",
        "_apply_dhw_pins", "_dhw_plan_temps", "_repair_dhw_floor",
        "_clamp_dhw_to_capacity", "_apply_dhw_min_run", "_dhw_raise_fits",
        "_plan_dhw_cheapest_first"]
P = ROOT / mt.PKG
opt = P / "optimizer.py"
src = opt.read_text()
lines = src.splitlines(keepends=True)
tree = ast.parse(src)
cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "HeatPumpOptimizer")
spans = []
for n in cls.body:
    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in MOVE:
        start = min([n.lineno] + [d.lineno for d in n.decorator_list])
        spans.append((start, n.end_lineno, n.name))
found = sorted(s[2] for s in spans)
pin = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_pin_is_free")
moved = "class DhwPlanner:\n"
for a, b, _ in sorted(spans):
    moved += "\n" + "".join(lines[a - 1:b])
if "--new-guard" in sys.argv:
    a, b, name = sorted(spans)[0]
    body = moved.splitlines(keepends=True)
    i = next(k for k, l in enumerate(body) if f"def {name}(" in l)
    while not body[i].rstrip().endswith(":"):
        i += 1
    ind = " " * (len(body[i + 1]) - len(body[i + 1].lstrip()))
    body.insert(i + 1, f"{ind}if f1748_new_guard is None:\n{ind}    return None\n")
    moved = "".join(body)
pin_src = "".join(lines[min([pin.lineno] + [d.lineno for d in pin.decorator_list]) - 1:pin.end_lineno])
drop = set()
for a, b, _ in spans:
    drop.update(range(a, b + 1))
drop.update(range(pin.lineno, pin.end_lineno + 1))
opt.write_text("".join(l for i, l in enumerate(lines, 1) if i not in drop))
(P / "dhw_planner.py").write_text(moved)
mp = P / "manual_plan.py"
mp.write_text(mp.read_text() + "\n\n" + pin_src)

# Re-key the ledger as the move PR would: scope and file change, text does not.
b = mt.load_budgets()
old_f, new_f = mt.PKG + "optimizer.py:HeatPumpOptimizer.", mt.PKG + "dhw_planner.py:DhwPlanner."
for m in mt.LEDGER_MAPS:
    out = {}
    for k, v in b.get(m, {}).items():
        for name in MOVE:
            if k.startswith(old_f + name + " ") or k.startswith(old_f + name + "."):
                k = new_f + k[len(old_f):]
                break
        if k.startswith(mt.PKG + "optimizer.py:_pin_is_free"):
            k = mt.PKG + "manual_plan.py" + k[len(mt.PKG + "optimizer.py"):]
        out[k] = v
    b[m] = out
sites = mt.inventory()
fixed, _ = mt.normalize(b, sites)
mt.write_budgets(fixed)
b = mt.load_budgets()
print(f"moved methods found: {len(found)} of {len(MOVE)}")
print(f"RESULT completeness_problems={len(mt.completeness_problems(b, sites))} count")
unpinned = mt.unpinned_sites(b, sites)
base = mt.base_unpinned_sites("HEAD", sites)
sides = mt.diff_sides("HEAD")
proto = mt.added_unpinned(unpinned, base)
here = mt.added_unpinned(unpinned, base, sides)
print(f"RESULT count_rule_refuses={mt.ratchet_refusal(len(base), unpinned) or 0} count  "
      f"(unpinned {len(unpinned)} vs base {len(base)})")
print(f"RESULT added_prototype_identity={len(proto)} count")
from collections import Counter
print("  by file:", dict(Counter(s['file'].rsplit('/', 1)[-1] for s in proto)))
print(f"RESULT added_with_move_match={len(here)} count")
for s in here:
    print(f"    ADDED {mt.triage_key(s)}: {s['old'].strip()}")
