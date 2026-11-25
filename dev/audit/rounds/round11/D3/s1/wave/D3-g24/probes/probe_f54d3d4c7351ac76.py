#!/usr/bin/env python3
# Metric: over the cases of _window_core.cases() (window 15/60 min x dt 0.25/0.5/1.0/0.75/1-min x six start
#   times on and off the window boundary x tariff masks off/on, plus dt 1e-9/0/-0.25 and start None), two
#   counts: return_moved = cases where HeatPumpOptimizer._window_offset_steps itself returns a different
#   offset (or raises) under the mutant; downstream_moved = cases where anything the production consumers
#   build from that offset differs -- _peak_billing's PeakBilling (offset_steps itself excluded), the
#   _grid_terms capacity penalty (scalar and batch) on a fixed seeded plan, and the published _grid_report
#   dict -- or one raises. Count key: the consumers' returned values.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g24/probes/probe_f54d3d4c7351ac76.py
# Expected: see EXPECTED below (exact counts, tolerance 0).
# EXPECTED RESULT null_return_moved=0 count
# EXPECTED RESULT null_downstream_moved=0 count
# EXPECTED RESULT null_cases_tried=127 count
# EXPECTED RESULT mutant_return_moved=3 count
# EXPECTED RESULT mutant_downstream_moved=1 count
# EXPECTED RESULT mutant_cases_tried=127 count
# EXPECTED RESULT reach_optimize_dt0_raises_before=1 count
# EXPECTED RESULT reach_offset_calls_at_dt0=0 count
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g24 (4 vCPU Intel Xeon @ 2.10GHz, Linux,
#   CPython 3.14 venv-ci).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._window_offset_steps
#   (optimizer.py:4069, CLAMP_DROP), driven through its one caller _peak_billing (optimizer.py:4117).
# Perturbation: mutant f54d3d4c7351ac76, optimizer.py:4069
#   'return max(0, int(round((window - phase) / max(dt * 60.0, 1e-6))))' -> 'return max(0, int(round((window - phase) / (dt * 60.0))))',
#   applied in memory (_mutlib.mutated; mock.patch.object on the class for the mutant arm only);
#   direction: return_moved / downstream_moved 0 -> >0.
# Reach: the only moving case is dt == 0; reach_optimize_dt0_raises_before = 1 when the production
#   HeatPumpOptimizer.optimize with time_step_minutes=0 already raises on the BASELINE before any offset is used.
# Null control: the baseline method against itself on the same cases (both null counts must be 0).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import warnings
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
warnings.simplefilter("ignore", RuntimeWarning)
import _mutlib  # noqa: E402
import _window_core  # noqa: E402

OLD = '        return max(0, int(round((window - phase) / max(dt * 60.0, 1e-6))))'
NEW = '        return max(0, int(round((window - phase) / (dt * 60.0))))'
_window_core.run(OLD, OLD, "null")
_window_core.run(OLD, NEW, "mutant")

from datetime import datetime  # noqa: E402
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer.optimizer import (  # noqa: E402
    ForecastSeries, HeatPumpOptimizer, OptimizationConfig, SolveInputs)
from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState  # noqa: E402
_o = HeatPumpOptimizer(ThermalModel(ThermalParameters()), OptimizationConfig(
    horizon_hours=6, time_step_minutes=0, peak_threshold_kw=1.0, peak_price_per_kw=50.0))
_calls = {"n": 0}
_real = HeatPumpOptimizer._window_offset_steps


def _spy(self, *a, **k):
    _calls["n"] += 1
    return _real(self, *a, **k)


try:
    from unittest import mock
    with mock.patch.object(HeatPumpOptimizer, "_window_offset_steps", _spy):
        _o.optimize(inputs=SolveInputs(
            state=ThermalState(room_temperature=21.0, slab_temperature=25.0, outdoor_temperature=-5.0),
            start_time=datetime(2026, 1, 15, 12, 15),
            forecast=ForecastSeries(prices=np.full(24, 1.0), outdoor_temps=np.full(24, -5.0))))
    _r = 0
except Exception as _e:
    _r = 1
    print(f"INFO baseline optimize(time_step_minutes=0) raises {type(_e).__name__}: {str(_e)[:60]}")
print(f"RESULT reach_optimize_dt0_raises_before={_r} count")
print(f"RESULT reach_offset_calls_at_dt0={_calls['n']} count")
_mutlib.footer()
