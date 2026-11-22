#!/usr/bin/env python3
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_9e71bd23e996ec6a.py
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g20 (4 vCPU Intel Xeon @ 2.10GHz).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._build_space_power_caps, line 4828
#   `if extra.size < n_steps:` (the extra-caps padding).
# Metric: count of inputs whose returned (throttling, power_caps, caps_extra_arr) differs between baseline and mutant.
# Perturbation: key 9e71bd23e996ec6a CMP_BOUND `<` -> `<=`, in memory. Only extra.size == n_steps differs, where the
#   mutant concatenates an empty pad. Direction: none expected.
# EXPECTED RESULT inputs_moved_beyond_exception_type=0 count (a 0-d input raises on both arms, IndexError vs ValueError); null_delta=0.
# Null control: extra None (the branch is not entered).
from _arrays import run
from _caps_cases import cases, NULL
run("_build_space_power_caps", "if extra.size < n_steps:", "if extra.size <= n_steps:", cases(), NULL)
