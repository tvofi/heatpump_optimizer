# Shared driver of box D3-g24's two get_current_action probes (not a harness itself). It solves one real
# 6 h plan with the production optimizer, derives result variants from it (empty, one step, the plan as
# is), and per (variant, clock) case records what HeatPumpOptimizer.get_current_action returns in each
# arm (the whole CurrentAction dict) or the exception it raises.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import dataclasses  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402
import _mutlib  # noqa: E402
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import optimizer  # noqa: E402
from custom_components.heatpump_optimizer.optimizer import (  # noqa: E402
    ForecastSeries, HeatPumpOptimizer, OptimizationConfig, SolveInputs)
from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState  # noqa: E402

T0 = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)


def make():
    opt = HeatPumpOptimizer(ThermalModel(ThermalParameters()), OptimizationConfig(
        horizon_hours=6, time_step_minutes=15, target_temp=21.0, min_temp=19.0, max_temp=23.0))
    pr = np.full(24, 2.0)
    pr[:4] = 0.5
    res = opt.optimize(inputs=SolveInputs(
        state=ThermalState(room_temperature=21.0, slab_temperature=25.0, outdoor_temperature=-5.0),
        start_time=T0, forecast=ForecastSeries(prices=pr, outdoor_temps=np.full(24, -5.0))))
    return opt, res


def _cut(res, k):
    """The result with every per-step list cut to its first k entries."""
    n = len(res.timestamps)
    kw = {}
    for f in dataclasses.fields(res):
        v = getattr(res, f.name)
        if isinstance(v, (list, np.ndarray)) and len(v) in (n, n + 1):
            kw[f.name] = v[:k] if isinstance(v, list) else v[:k]
    return dataclasses.replace(res, **kw)


def cases(res):
    ts = res.timestamps
    step = ts[1] - ts[0]
    full, one, empty = res, _cut(res, 1), _cut(res, 0)
    clocks = [("at_start", ts[0]), ("1us_before_start", ts[0] - timedelta(microseconds=1)),
              ("half_step_before", ts[0] - step / 2), ("exactly_one_step_before", ts[0] - step),
              ("beyond_one_step_before", ts[0] - step - timedelta(seconds=1)),
              ("at_step_1", ts[1]), ("mid_step_3", ts[3] + step / 2), ("at_last", ts[-1]),
              ("after_end", ts[-1] + 2 * step)]
    out = [(f"full/{c}", full, t) for c, t in clocks]
    out += [(f"one_step/{c}", one, t) for c, t in clocks]
    out += [(f"empty/{c}", empty, t) for c, t in clocks[:3]]
    return out


def _call(fn, opt, res, now):
    try:
        return ("ok", repr(fn(opt, res, now)))
    except Exception as e:
        return ("raise", type(e).__name__)


def run(old, new, label, opt, res):
    base = HeatPumpOptimizer.get_current_action
    mut = _mutlib.mutated(HeatPumpOptimizer, "get_current_action", old, new, optimizer)
    moved = n = 0
    for name, r, now in cases(res):
        b, m = _call(base, opt, r, now), _call(mut, opt, r, now)
        d = int(b != m)
        moved += d
        n += 1
        if d:
            print(f"CASE {name}: baseline={b[0]} {b[1][:90]} | mutant={m[0]} {m[1][:90]}")
    print(f"RESULT {label}_cases_moved={moved} count")
    print(f"RESULT {label}_cases_tried={n} count")
