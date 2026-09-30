"""RCA-1747: under a DHW block, is the wood-coil trigger (81aa0c3b, #470) the only route into the replan?
Run at a tree that has the defect (e.g. 754d2319) from the repo root:
  PYTHONPATH=tests/hastub:custom_components:tests python3 rca_coil_trigger.py
The finder's scenario (golden wood_coil, dhw_blocked=True, prices + delta) in two arms:
  as-is      production.
  no-coil    _dhw_coil_wood_forecast returns None, so _co_optimize has only its pre-#470 trigger,
             `pinned = (dhw_power > 1e-6) & ...`, which a blocked first plan (all zero) cannot meet.
Prints the builds made, the first plan's peak DHW power as _co_optimize received it, and what shipped."""
import sys
import numpy as np
sys.argv = [sys.argv[0]]
from golden import make, SCENARIOS, START, external_heat_for
import heatpump_optimizer.optimizer as M

H = M.HeatPumpOptimizer
real_build, real_co, real_wood = H._build_dhw_requirements, H._co_optimize, H._dhw_coil_wood_forecast


def run(arm, delta):
    builds, first_peak = [], []

    def spy(self, *a, **k):
        builds.append(k.get("blocked", "<omitted>"))
        return real_build(self, *a, **k)

    def co(self, h, **kw):
        first_peak.append(float(np.max(kw["dhw_power"])))
        return real_co(self, h, **kw)

    H._build_dhw_requirements, H._co_optimize = spy, co
    if arm == "no-coil":
        H._dhw_coil_wood_forecast = lambda self, *a, **k: None
    try:
        b = make(**SCENARIOS["wood_coil"])
        res = b["optimizer"].optimize(b["state"], np.asarray(b["prices"], dtype=float) + delta, b["outdoor"], b["wind"],
                                      b["rain"], b["solar"], START, None, None,
                                      external_heat_kw=external_heat_for(len(b["prices"])), dhw_blocked=True)
    finally:
        H._build_dhw_requirements, H._co_optimize, H._dhw_coil_wood_forecast = real_build, real_co, real_wood
    kwh = float(np.sum(res.dhw_power_schedule)) * 0.25
    print(f"RESULT arm={arm} delta={delta:+.1f} builds={builds} first_plan_peak_dhw_kw={first_peak} "
          f"shipped_dhw_kwh={kwh:.2f} breach={res.predictive_info.get('dhw_floor_breach_c')}")


for arm in ("as-is", "no-coil"):
    for d in (0.0, -2.0, -3.0):
        run(arm, d)
