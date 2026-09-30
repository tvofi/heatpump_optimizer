"""Probe: does _co_optimize's replan honour a DHW mode block?  (issue: R9-EG-DHW-BLOCK-REPLAN)
Run from the repo root: PYTHONPATH=tests/hastub:custom_components:tests python3 b8_replan_blocked.py
Scenario: tests/golden.py 'wood_coil' (with its external-heat forecast), dhw_blocked=True, prices shifted by DELTA.
Arm 'as-is': production code.  Arm 'control': the replan's _build_dhw_requirements call is given blocked=True
(the value _optimize_with_dhw's own build receives), everything else identical."""
import sys, copy, numpy as np
sys.argv = [sys.argv[0]]
import golden as G
from heatpump_optimizer.optimizer import HeatPumpOptimizer
orig = HeatPumpOptimizer._build_dhw_requirements
calls = []
def spy(self, *a, **k):
    calls.append(k.get("blocked", "<omitted>"))
    if FORCE and "blocked" not in k:
        k["blocked"] = True
    return orig(self, *a, **k)
HeatPumpOptimizer._build_dhw_requirements = spy
def run(delta):
    b = G.make(**G.SCENARIOS["wood_coil"]); opt = b["optimizer"]; n = len(b["prices"])
    calls.clear()
    res = opt.optimize(b["state"], np.asarray(b["prices"]) + delta, b["outdoor"], b["wind"], b["rain"], b["solar"], G.START,
                       None, None, external_heat_kw=G.external_heat_for(n), dhw_blocked=True)
    dhw = np.asarray(res.dhw_power_schedule, dtype=float)
    kwh = float(dhw.sum() * opt.config.dt_hours)
    reasons = sorted({r for r in (getattr(res, "dhw_reasons", None) or []) if r}) if hasattr(res, "dhw_reasons") else None
    return kwh, int((dhw > 1e-9).sum()), res.predictive_info.get("dhw_floor_breach_c"), list(calls), int((np.asarray(b["prices"]) + delta < 0).sum()), n
for arm, FORCE in (("as-is", False), ("control", True)):
    for d in (0.0, -1.0, -2.0, -3.0):
        kwh, steps, breach, c, neg, n = run(d)
        print(f"{arm:8s} delta={d:+.1f} negative_steps={neg}/{n} shipped_dhw_kwh={kwh:.2f} dhw_steps={steps} dhw_floor_breach_c={breach} build_calls_blocked_arg={c}")
