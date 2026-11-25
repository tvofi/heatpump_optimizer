#!/usr/bin/env python3
# Metric: number of (result variant x clock) cases of _action_core.cases() -- a real 6 h / 15-min plan, its
#   first step alone, and the plan emptied; clocks at the first start, 1 us / half a step / exactly one step /
#   one step + 1 s before it, on step 1, mid step 3, on the last start and past the end -- on which
#   HeatPumpOptimizer.get_current_action returns a different CurrentAction (whole dict, repr-compared) or
#   raises differently under the mutant. Count key: the returned action.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g24/probes/probe_0270b5efaac478d2.py
# Expected: see EXPECTED below (exact counts, tolerance 0).
# EXPECTED RESULT null_cases_moved=0 count
# EXPECTED RESULT null_cases_tried=21 count
# EXPECTED RESULT mutant_cases_moved=3 count
# EXPECTED RESULT mutant_cases_tried=21 count
# EXPECTED RESULT reach_optimize_empty_results=0 count
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g24 (4 vCPU Intel Xeon @ 2.10GHz, Linux,
#   CPython 3.14 venv-ci).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer.get_current_action
#   (optimizer.py:6550, GUARD_OFF).
# Perturbation: mutant 0270b5efaac478d2, optimizer.py:6550
#   'if not result.timestamps:' -> 'if False:',
#   applied in memory (_mutlib.mutated recompiles the method from its own source); direction: cases_moved
#   0 -> >0.
# Null control: the baseline method against itself on the same cases (null_cases_moved must be 0).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import warnings
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
warnings.simplefilter("ignore", RuntimeWarning)
import _mutlib  # noqa: E402
import _action_core  # noqa: E402

OLD = '        if not result.timestamps:'
NEW = '        if False:'
_opt, _res = _action_core.make()
_action_core.run(OLD, OLD, "null", _opt, _res)
_action_core.run(OLD, NEW, "mutant", _opt, _res)

# Reach: the one production caller (coordinator.py:6464) hands get_current_action the result optimize() just
# returned; reach_optimize_empty_results counts the degenerate solves (horizon 0, empty prices, horizon below
# one step) that RETURN a result with no timestamps instead of raising first.
from datetime import datetime, timezone  # noqa: E402
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer.optimizer import (  # noqa: E402
    ForecastSeries, HeatPumpOptimizer, OptimizationConfig, SolveInputs)
from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState  # noqa: E402
_empty = 0
for _name, _cfg, _pr in [("horizon0", dict(horizon_hours=0), np.full(24, 1.0)),
                         ("prices_empty", dict(horizon_hours=6), np.array([])),
                         ("horizon_lt_step", dict(horizon_hours=0.1), np.full(24, 1.0))]:
    _o = HeatPumpOptimizer(ThermalModel(ThermalParameters()), OptimizationConfig(**_cfg))
    try:
        _r = _o.optimize(inputs=SolveInputs(
            state=ThermalState(room_temperature=21.0, slab_temperature=25.0, outdoor_temperature=-5.0),
            start_time=datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc),
            forecast=ForecastSeries(prices=_pr, outdoor_temps=np.full(max(len(_pr), 1), -5.0))))
        _empty += int(not _r.timestamps)
        print(f"INFO reach {_name}: returned {len(_r.timestamps)} timestamps")
    except Exception as _e:
        print(f"INFO reach {_name}: optimize raises {type(_e).__name__} before any action is read")
print(f"RESULT reach_optimize_empty_results={_empty} count")
_mutlib.footer()
