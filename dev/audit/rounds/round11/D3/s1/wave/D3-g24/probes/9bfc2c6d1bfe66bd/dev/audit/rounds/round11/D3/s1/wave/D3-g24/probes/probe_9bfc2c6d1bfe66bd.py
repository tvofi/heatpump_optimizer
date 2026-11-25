#!/usr/bin/env python3
# Metric: number of input cases (the `refused` vectors and caps of _tighten_core.cases(): zero, None, the
#   1e-9 tie, one ulp either side of it, NaN, negative, the new_cap == cap - 1e-9 tie, cap equal/above/below)
#   on which HeatPumpOptimizer._tighten_buffer_caps returns a different (changed, power_caps, logged count)
#   or raises differently under the mutant. Count key: the method's own return value, the caps array it
#   mutates in place and the count its debug line logs -- never an input attribute.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g24/probes/probe_9bfc2c6d1bfe66bd.py
# Expected: see EXPECTED below (exact counts, tolerance 0).
# EXPECTED RESULT null_cases_moved=0 count
# EXPECTED RESULT null_cases_tried=12 count
# EXPECTED RESULT mutant_cases_moved=1 count
# EXPECTED RESULT mutant_cases_tried=12 count
# EXPECTED RESULT reach_refused_is_none=0 count  (type ndarray)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g24 (4 vCPU Intel Xeon @ 2.10GHz, Linux,
#   CPython 3.14 venv-ci).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._tighten_buffer_caps
#   (optimizer.py:5120, GUARD_OFF); the model's simulate_trajectory is stubbed per case to answer the chosen
#   `refused` vector (mock.patch.object on the instance), the rest is production code.
# Perturbation: mutant 9bfc2c6d1bfe66bd, optimizer.py:5120
#   'if refused is None:' -> 'if False:',
#   applied in memory (_mutlib.mutated recompiles the method from its own source); direction: cases_moved
#   0 -> >0 if the mutant changes behaviour on any case.
# Null control: the baseline method against itself on the same cases (null_cases_moved must be 0).
# Reach: reach_refused_is_none -- whether the real ThermalModel.simulate_trajectory ever answers None in
#   the refused slot (it allocates np.zeros(n_steps) unconditionally, thermal_model.py:4370).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _mutlib  # noqa: E402
import _tighten_core  # noqa: E402

OLD = '        if refused is None:'
NEW = '        if False:'
_tighten_core.run(OLD, OLD, "null")
_tighten_core.run(OLD, NEW, "mutant")
_tighten_core.reach_refused_type()
_mutlib.footer()
