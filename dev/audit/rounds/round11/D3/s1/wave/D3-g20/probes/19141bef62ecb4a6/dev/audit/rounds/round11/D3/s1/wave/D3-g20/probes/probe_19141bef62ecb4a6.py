#!/usr/bin/env python3
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_19141bef62ecb4a6.py
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g20 (4 vCPU Intel Xeon @ 2.10GHz).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._build_comfort_bounds, line 4766
#   `if f.size < n_steps:` (the mold-floor padding).
# Metric: count of inputs whose returned (targets, min bounds, max bounds, (comfort floors, mold floors)) differs
#   (np.array_equal, nan-equal, shapes; an exception counts as its type name) between baseline and mutant.
# Perturbation: key 19141bef62ecb4a6 CMP_BOUND `<` -> `<=`, in memory. Only f.size == n_steps differs, where the mutant
#   concatenates an empty pad. Direction: none expected.
# EXPECTED RESULT inputs_moved_beyond_exception_type=0 count (a 0-d input raises on both arms, IndexError vs ValueError); null_delta=0.
# Null control: floors None (the branch is not entered).
from _arrays import run
from _bounds_cases import cases, NULL
run("_build_comfort_bounds", "if f.size < n_steps:", "if f.size <= n_steps:", cases(), NULL)
