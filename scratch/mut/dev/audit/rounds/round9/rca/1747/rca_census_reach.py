"""RCA-1747: does EG-B8's companion check ("every DHW build that solve made was told the mode is
blocked") assert that its fixture reaches the replan?  Run at EG-B8's code head from the repo root:
  PYTHONPATH=tests/hastub:custom_components:tests python3 rca_census_reach.py
Replays the check's own fixture (golden wood_coil, dhw_blocked=True, prices - 2.0) under three arms
and evaluates both of EG-B8's check predicates verbatim:
  as-is       production at the head.
  no-replan   _co_optimize returns its inputs (the replan is never built: a route change, or a
              fixture that stops tempting it). The block is honoured trivially.
  off-spy     _co_optimize rebuilds through an unspied builder that drops `blocked` (the #1747
              defect, reached by a route the spy does not watch, as a planner-call extraction would).
Prints the builds the spy saw, and each check's verdict; a companion that passes 'off-spy' while
the defect ships is blind to its own reach."""
import sys
import numpy as np
sys.argv = [sys.argv[0]]
from golden import make, SCENARIOS, START, external_heat_for
import heatpump_optimizer.optimizer as M

H = M.HeatPumpOptimizer
real_build, real_co = H._build_dhw_requirements, H._co_optimize


def run(arm):
    seen = []

    def spy(self, *a, **k):
        seen.append(k.get("blocked", False))
        return real_build(self, *a, **k)

    def co_noreplan(self, h, **kw):
        return kw["space_power"], kw["dhw_power"], kw["status"]

    def co_offspy(self, h, **kw):
        def unspied(*a, **k):
            k.pop("blocked", None)
            return real_build(self, *a, **k)
        self._build_dhw_requirements = unspied  # instance attribute: the replan's lookup bypasses the class spy
        try:
            return real_co(self, h, **kw)
        finally:
            del self._build_dhw_requirements

    H._build_dhw_requirements = spy
    H._co_optimize = {"as-is": real_co, "no-replan": co_noreplan, "off-spy": co_offspy}[arm]
    try:
        b = make(**SCENARIOS["wood_coil"])
        res = b["optimizer"].optimize(b["state"], np.asarray(b["prices"], dtype=float) - 2.0, b["outdoor"], b["wind"],
                                      b["rain"], b["solar"], START, None, None,
                                      external_heat_kw=external_heat_for(len(b["prices"])), dhw_blocked=True)
    finally:
        H._build_dhw_requirements, H._co_optimize = real_build, real_co
    breach = res.predictive_info.get("dhw_floor_breach_c") or 0.0
    first = max(res.dhw_power_schedule) == 0.0 and breach > 5.0
    companion = len(seen) >= 1 and all(seen)
    reach = len(seen) >= 2 and all(seen)
    kwh = float(np.sum(res.dhw_power_schedule)) * 0.25
    print(f"RESULT arm={arm} builds_seen={seen} shipped_dhw_kwh={kwh:.2f} breach={breach:.3f} "
          f"check_first={'pass' if first else 'FAIL'} check_companion={'pass' if companion else 'FAIL'} "
          f"companion_with_reach(>=2)={'pass' if reach else 'FAIL'}")


for arm in ("as-is", "no-replan", "off-spy"):
    run(arm)
