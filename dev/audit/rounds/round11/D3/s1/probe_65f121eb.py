#!/usr/bin/env python3
# Metric: what optimizer._holiday_flags_for returns for an EMPTY holiday_dates set on a fixed 4-step horizon
#   (baseline None = no holiday array built), and how many production solves reach it with an empty set.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/probe_65f121eb.py
# EXPECTED RESULT holiday_flags_baseline=None
# EXPECTED RESULT holiday_flags_mutant=[False, False, False, False, False]
# EXPECTED RESULT moved=1 count
# EXPECTED RESULT null_delta=0 count  (a non-empty holiday set: the guard is false either way)
# EXPECTED RESULT reach_empty_calls=1 count (one optimize() with default empty holiday_dates)
# EXPECTED RESULT reach_plan_maxabs_diff_kw=0.0 kW (whole-plan power_schedule identical in both arms)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-rem (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:_holiday_flags_for (line 773
#   `    if not holiday_dates:`), called at optimizer.py:4403 with self.config.holiday_dates.
# Perturbation: line 773 -> `    if False:` (GUARD_OFF 65f121eb047174ad), applied in memory (function recompiled from
#   its own source, patched onto the module for the mutant arm only). Direction: None -> array of n+1 False.
#   VERDICT: EQUIVALENT on every observable. The only consumer of holiday_flags is
#   dhw_planner:_dhw_windows_at (dhw_planner.py:75), which reads `holiday = False` for None and
#   bool(flag)=False for an all-False array, so windows_for_day gets holiday=False either way; the
#   returned array differs only in its allocation. The probe prints the returned value moving
#   (None vs all-False) and the full plan not moving.
# Null control: holiday_dates={date} non-empty; mutant and baseline return identical arrays.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap
from datetime import date, datetime, timedelta
from pathlib import Path
from unittest import mock

def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")

ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT))
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import optimizer  # noqa: E402

OLD = "    if not holiday_dates:"
NEW = "    if False:"


def mutant_fn():
    src = textwrap.dedent(inspect.getsource(optimizer._holiday_flags_for))
    old, new = OLD.strip(), NEW.strip()
    assert src.count(old) == 1, "anchor line moved"
    ns = dict(optimizer.__dict__)
    exec(compile(src.replace(old, new, 1), optimizer.__file__, "exec"), ns)
    return ns["_holiday_flags_for"]


t0 = datetime(2026, 1, 5, 22, 0)
steps = [t0 + timedelta(hours=i) for i in range(4)]
empty, full = frozenset(), frozenset({date(2026, 1, 6)})
mut = mutant_fn()
b = optimizer._holiday_flags_for(steps, empty)
m = mut(steps, empty)
nb, nm = optimizer._holiday_flags_for(steps, full), mut(steps, full)
null_delta = int(not np.array_equal(nb, nm))
print(f"RESULT holiday_flags_baseline={b}")
print(f"RESULT holiday_flags_mutant={None if m is None else m.tolist()}")
print(f"RESULT moved={int((b is None) != (m is None))} count")
print(f"RESULT null_delta={null_delta} count")

# Reach + downstream: drive the production optimize() with the default (empty) holiday_dates.
reach = {"empty": 0, "total": 0}
real = optimizer._holiday_flags_for


def spy(sd, hd):
    reach["total"] += 1
    reach["empty"] += int(not hd)
    return real(sd, hd)


try:
    from custom_components.heatpump_optimizer.thermal_model import ThermalParameters, ThermalState, ThermalModel
    from custom_components.heatpump_optimizer.optimizer import (
        HeatPumpOptimizer, OptimizationConfig, SolveInputs, ForecastSeries, SolveLimits)

    def solve():
        opt = HeatPumpOptimizer(ThermalModel(ThermalParameters()), OptimizationConfig(
            horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=19.0, max_temp=23.0))
        pr = np.full(96, 2.0)
        pr[:8] = 0.5
        return opt.optimize(inputs=SolveInputs(
            state=ThermalState(room_temperature=21.0, slab_temperature=25.0, outdoor_temperature=-5.0),
            start_time=datetime(2026, 1, 15, 12, 0), forecast=ForecastSeries(prices=pr, outdoor_temps=np.full(96, -5.0)),
            limits=SolveLimits()))
    with mock.patch.object(optimizer, "_holiday_flags_for", spy):
        r1 = solve()
    with mock.patch.object(optimizer, "_holiday_flags_for", mut):
        r2 = solve()
    pe = float(np.max(np.abs(np.asarray(r1.power_schedule) - np.asarray(r2.power_schedule))))
    print(f"RESULT reach_plan_maxabs_diff_kw={pe}")
except Exception as exc:  # reach drive is best-effort
    print(f"RESULT reach_drive_error={type(exc).__name__}: {str(exc)[:160]}")
print(f"RESULT reach_empty_calls={reach['empty']} count")
print(f"RESULT reach_total_calls={reach['total']} count")
