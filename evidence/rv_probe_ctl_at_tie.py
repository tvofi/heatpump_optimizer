"""Does equiv_probe.py's OWN control differ on any tied case? (reviewer's instrument)"""
import runpy, sys, io, contextlib
import numpy as np
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    g = runpy.run_path("tools/audit/round9/F10/f10_6/equiv_probe.py")
away, optimizer, compiled, mutant_text = g["away"], g["optimizer"], g["compiled"], g["mutant_text"]
src, _, _ = mutant_text(away, "if last < first:", "CMP_BOUND")
_, ctext, _ = mutant_text(away, "if last < first:", "GUARD_OFF")
h, c = compiled(away, src, "_holiday_span"), compiled(away, ctext, "_holiday_span")
at_tie = sum(1 for a in g["away_grid"]() if g["away_tie"](a) and h(*a) != c(*a))
off_tie = sum(1 for a in g["away_grid"]() if not g["away_tie"](a) and h(*a) != c(*a))
print(f"RESULT rv probe-control away differs_at_tie={at_tie} differs_off_tie={off_tie}")
OLD = "idx = i if i <= last else last"
src, _, _ = mutant_text(optimizer, OLD, "CMP_BOUND")
_, ctext, _ = mutant_text(optimizer, OLD, None, new="idx = last")
kw = dict(cls="HeatPumpOptimizer")
h, c = compiled(optimizer, src, "_dhw_planner_draws", **kw), compiled(optimizer, ctext, "_dhw_planner_draws", **kw)
# per-ITERATION: the control can only differ at an iteration with i < last, never at i == last
at = off = 0
for me, d, wt in g["opt_grid"]():
    a, b = h(me, d, wt), c(me, d, wt); last = len(wt) - 1
    for i in range(len(d)):
        if a[i] != b[i]:
            at += i == last; off += i != last
print(f"RESULT rv probe-control optimizer differing_iterations_at_tie={at} off_tie={off}")
