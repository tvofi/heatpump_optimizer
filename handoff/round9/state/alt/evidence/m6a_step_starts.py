"""M6a probe: do the two _utc_step_starts definitions agree wherever production can call them?
Run: PYTHONPATH=tests/hastub:custom_components python3 m6a_step_starts.py"""
from datetime import datetime
from zoneinfo import ZoneInfo
from heatpump_optimizer.coordinator import _utc_step_starts as coord_steps
from heatpump_optimizer.optimizer import _utc_step_starts as opt_steps, OptimizationConfig
import inspect, heatpump_optimizer.optimizer as o
print("dt_hours property:", inspect.getsource(OptimizationConfig.dt_hours.fget).strip().splitlines()[-1].strip())
tz = ZoneInfo("Europe/Stockholm")
days = {"spring": datetime(2026, 3, 29, tzinfo=tz), "autumn": datetime(2026, 10, 25, tzinfo=tz), "plain": datetime(2026, 8, 26, tzinfo=tz)}
bad = 0; total = 0
for name, d in days.items():
    for minutes in (5, 10, 15, 20, 30, 60):
        n = int(48 * 60 / minutes)
        a = opt_steps(d, n, minutes / 60.0)
        b = coord_steps(d, n, 0, int(round((minutes / 60.0) * 60)))  # the _horizon_step_starts bridge
        total += 1
        if a != b:
            bad += 1; print("DISAGREE", name, minutes)
print(f"whole-minute steps (reachable: dt_hours = time_step_minutes/60): {total - bad}/{total} agree")
# control: a step the bridge cannot represent (unreachable in production) does disagree
d = days["autumn"]; a = opt_steps(d, 10, 0.3 + 1/600); b = coord_steps(d, 10, 0, int(round((0.3 + 1/600) * 60)))
print("control, non-whole-minute dt=0.30167h:", "disagree" if a != b else "agree")
# offset parameter: coordinator-only
print("coordinator offset callers need step_offset; optimizer version has none:", "step_offset" in inspect.signature(coord_steps).parameters, "step_offset" in inspect.signature(opt_steps).parameters)
