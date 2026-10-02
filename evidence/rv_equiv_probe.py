"""Reviewer's own check of equiv_probe.py: (1) count ties INSIDE the compiled
production function (an append in the compare), not by recomputation;
(2) a TIE-ONLY control -- an edit that changes the result only when the two
sides are equal -- must differ on the same grid, or the grid cannot see a tie."""
import runpy, sys, io, contextlib
from datetime import timedelta
sys.argv = ["equiv_probe.py"]
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    g = runpy.run_path("tools/audit/round9/F10/f10_6/equiv_probe.py")
print("probe:", " | ".join(l for l in buf.getvalue().splitlines() if l.startswith("RESULT")))
import numpy as np
away, optimizer, compiled, mutant_text, run = g["away"], g["optimizer"], g["compiled"], g["mutant_text"], g["run"]

def count_ties(mod, text, name, grid, cls=None):
    T = []
    f = compiled(mod, text, name, **({"cls": cls} if cls else {}))
    f.__globals__["_T"] = T
    for a in grid(): f(*a)
    return sum(T), len(T)

# away: head with tie counter; tie-only control
src, _, _ = mutant_text(away, "if last < first:", "CMP_BOUND")
_, tie_txt, _ = mutant_text(away, "if last < first:", None, new="if (_T.append(last == first) or True) and last < first:")
_, ctl_txt, _ = mutant_text(away, "if last < first:", None, new="if last < first or last == first and (first := first - timedelta(days=1)):")
print("RESULT rv away ties_in_function=%d of evaluations=%d" % count_ties(away, tie_txt, "_holiday_span", g["away_grid"]))
h = compiled(away, src, "_holiday_span"); c = compiled(away, ctl_txt, "_holiday_span")
print("rv away tie-only control:", end=" "); run("away tie-only", h, h, c, g["away_grid"], lambda a: 0)

OLD = "idx = i if i <= last else last"
src, _, _ = mutant_text(optimizer, OLD, "CMP_BOUND")
_, tie_txt, _ = mutant_text(optimizer, OLD, None, new="idx = i if (_T.append(i == last) or True) and i <= last else last")
_, ctl_txt, _ = mutant_text(optimizer, OLD, None, new="idx = i if i < last else (last - 1 if i == last and last > 0 else last)")
t, n = count_ties(optimizer, tie_txt, "_dhw_planner_draws", g["opt_grid"], cls="HeatPumpOptimizer")
print("RESULT rv optimizer tie_iterations=%d of iterations=%d" % (t, n))
h = compiled(optimizer, src, "_dhw_planner_draws", cls="HeatPumpOptimizer")
c = compiled(optimizer, ctl_txt, "_dhw_planner_draws", cls="HeatPumpOptimizer")
print("rv optimizer tie-only control:", end=" "); run("optimizer tie-only", h, h, c, g["opt_grid"], lambda a: 0)
