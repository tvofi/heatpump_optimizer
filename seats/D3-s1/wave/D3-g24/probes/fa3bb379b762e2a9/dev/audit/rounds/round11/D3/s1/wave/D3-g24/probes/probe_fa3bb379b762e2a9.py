#!/usr/bin/env python3
# Metric: number of input cases (of the shared list in _stash_cases.py) on which
#   HeatPumpOptimizer._stash_price_horizon hands the solve a different outcome under the mutant than on the
#   baseline: returned price array, stashed _price_known / _pv_surplus (values, dtype, NaN-aware), or the
#   exception raised. Count key: the values the production method returns/stashes, never an input attribute.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g24/probes/probe_fa3bb379b762e2a9.py
# Expected: see EXPECTED below (exact counts, tolerance 0).
# EXPECTED RESULT null_cases_moved=0 count
# EXPECTED RESULT null_cases_tried=25 count
# EXPECTED RESULT mutant_cases_moved=0 count
# EXPECTED RESULT mutant_cases_tried=25 count
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g24 (4 vCPU Intel Xeon @ 2.10GHz, Linux,
#   CPython 3.14 venv-ci).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._stash_price_horizon
#   (optimizer.py:4700, CMP_BOUND).
# Perturbation: mutant fa3bb379b762e2a9, optimizer.py:4700
#   'if pv_surplus.size < n_steps:' -> 'if pv_surplus.size <= n_steps:',
#   applied in memory (_mutlib.mutated recompiles the method from its own source); direction: cases_moved
#   0 -> >0 if the mutant changes behaviour on any case.
# Null control: the baseline method against itself on the same cases (null_cases_moved must be 0).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _mutlib  # noqa: E402
import _stash_core  # noqa: E402
from _stash_cases import CASES  # noqa: E402

OLD = '        if pv_surplus.size < n_steps:'
NEW = '        if pv_surplus.size <= n_steps:'
_stash_core.run(OLD, OLD, CASES, "null")
_stash_core.run(OLD, NEW, CASES, "mutant")
_mutlib.footer()
