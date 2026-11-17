"""Reviewer's probe: the lifted floor against the solver's own bound build, at a
day/night setback, weekend values and a holiday, across the autumn DST change."""
import sys
from datetime import datetime, date
from zoneinfo import ZoneInfo
import numpy as np
from heatpump_optimizer import rooms
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig, _step_clock
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters
tz = ZoneInfo("Europe/Stockholm")
cfg = OptimizationConfig(target_temp=21.0, min_temp=19.0, max_temp=23.0)
for k, v in dict(comfort_temp_day=21.0, comfort_temp_night=19.5, comfort_temp_day_weekend=20.5,
                 holiday_dates=frozenset({date(2026, 10, 26)})).items():
    object.__setattr__(cfg, k, v) if hasattr(cfg, k) else print("no field", k)
opt = HeatPumpOptimizer(ThermalModel(ThermalParameters()), cfg)
worst = 0.0
for start, base in [(datetime(2026, 10, 24, 20, 0, tzinfo=tz), None),
                    (datetime(2026, 10, 25, 1, 45, tzinfo=tz), np.linspace(0.0, 0.6, 192)),
                    (datetime(2026, 3, 29, 1, 30, tzinfo=tz), None)]:
    n = 192
    held = rooms.HeldLift(1.0, "climate.a", None, 3.0)
    m = rooms.lifted(held, base, cfg, start, n)
    when, hours = _step_clock(start, n, cfg.dt_hours)
    targets, mins, maxs, _ = opt._build_comfort_bounds(hours, n, m, None, when)
    t0, f0, _, _ = opt._build_comfort_bounds(hours, n, base, None, when)
    over = np.max(mins - targets)
    hol = [i for i, w in enumerate(when) if w.date() == date(2026, 10, 26)]
    print(f"start={start.isoformat()} lifted_steps={int(np.sum(mins > f0 + 1e-12))} "
          f"max(lifted floor - target)={over:+.4f} holiday_steps_lifted={int(np.sum((mins - f0)[hol] > 1e-12)) if hol else 0}")
    worst = max(worst, over)
print("RESULT lifted floor over the solver's own target, worst:", f"{worst:+.4f}")
sys.exit(0 if worst <= 1e-9 else 1)
