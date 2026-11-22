#!/usr/bin/env python3
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_0275af9776ae709e.py
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g20 (4 vCPU Intel Xeon @ 2.10GHz).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._build_space_power_caps, line 4802
#   `if space_blocked:` (the mode gate's zero ceiling).
# Metric: count of inputs whose returned (throttling, power_caps, caps_extra_arr) differs between baseline and mutant.
# Perturbation: key 0275af9776ae709e GUARD_OFF `if space_blocked:` -> `if False:`, in memory. Direction: with space heating
#   blocked the ceiling is max_electrical_power instead of 0.0 at every step.
# EXPECTED RESULT inputs_moved>0 (every blocked=True row); null_delta=0.
# Null control: blocked False.
from _arrays import run
from _caps_cases import cases, NULL
run("_build_space_power_caps", "if space_blocked:", "if False:", cases(), NULL)
