#!/usr/bin/env python3
# Metric: over the cases of _window_core.cases() (window 15/60 min x dt 0.25/0.5/1.0/0.75/1-min x six start
#   times on and off the window boundary x tariff masks off/on, plus dt 1e-9/0/-0.25 and start None), two
#   counts: return_moved = cases where HeatPumpOptimizer._window_offset_steps itself returns a different
#   offset (or raises) under the mutant; downstream_moved = cases where anything the production consumers
#   build from that offset differs -- _peak_billing's PeakBilling (offset_steps itself excluded), the
#   _grid_terms capacity penalty (scalar and batch) on a fixed seeded plan, and the published _grid_report
#   dict -- or one raises. Count key: the consumers' returned values.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g24/probes/probe_0f03bb94bcab1682.py
# Expected: see EXPECTED below (exact counts, tolerance 0).
# EXPECTED RESULT null_return_moved=0 count
# EXPECTED RESULT null_downstream_moved=0 count
# EXPECTED RESULT null_cases_tried=127 count
# EXPECTED RESULT mutant_return_moved=57 count
# EXPECTED RESULT mutant_downstream_moved=0 count
# EXPECTED RESULT mutant_cases_tried=127 count
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g24 (4 vCPU Intel Xeon @ 2.10GHz, Linux,
#   CPython 3.14 venv-ci).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._window_offset_steps
#   (optimizer.py:4067, GUARD_OFF), driven through its one caller _peak_billing (optimizer.py:4117).
# Perturbation: mutant 0f03bb94bcab1682, optimizer.py:4067
#   'if phase == 0:' -> 'if False:',
#   applied in memory (_mutlib.mutated; mock.patch.object on the class for the mutant arm only);
#   direction: return_moved / downstream_moved 0 -> >0.
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

OLD = '        if phase == 0:'
NEW = '        if False:'
_window_core.run(OLD, OLD, "null")
_window_core.run(OLD, NEW, "mutant")
_mutlib.footer()
