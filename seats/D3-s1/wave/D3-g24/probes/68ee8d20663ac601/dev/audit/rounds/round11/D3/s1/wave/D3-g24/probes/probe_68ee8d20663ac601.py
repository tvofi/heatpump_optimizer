#!/usr/bin/env python3
# Metric: number of (result variant x clock) cases of _action_core.cases() -- a real 6 h / 15-min plan, its
#   first step alone, and the plan emptied; clocks at the first start, 1 us / half a step / exactly one step /
#   one step + 1 s before it, on step 1, mid step 3, on the last start and past the end -- on which
#   HeatPumpOptimizer.get_current_action returns a different CurrentAction (whole dict, repr-compared) or
#   raises differently under the mutant. Count key: the returned action.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g24/probes/probe_68ee8d20663ac601.py
# Expected: see EXPECTED below (exact counts, tolerance 0).
# EXPECTED RESULT null_cases_moved=0 count
# EXPECTED RESULT null_cases_tried=21 count
# EXPECTED RESULT mutant_cases_moved=0 count
# EXPECTED RESULT mutant_cases_tried=21 count
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g24 (4 vCPU Intel Xeon @ 2.10GHz, Linux,
#   CPython 3.14 venv-ci).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer.get_current_action
#   (optimizer.py:6559, CMP_BOUND).
# Perturbation: mutant 68ee8d20663ac601, optimizer.py:6559
#   'if now_s < starts[0]:' -> 'if now_s <= starts[0]:',
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

OLD = '        if now_s < starts[0]:'
NEW = '        if now_s <= starts[0]:'
_opt, _res = _action_core.make()
_action_core.run(OLD, OLD, "null", _opt, _res)
_action_core.run(OLD, NEW, "mutant", _opt, _res)
_mutlib.footer()
