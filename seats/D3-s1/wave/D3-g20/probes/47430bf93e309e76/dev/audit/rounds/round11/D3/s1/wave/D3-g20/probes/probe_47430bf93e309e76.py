#!/usr/bin/env python3
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_47430bf93e309e76.py
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g20 (4 vCPU Intel Xeon @ 2.10GHz).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._build_comfort_bounds, line 4766
#   `if f.size < n_steps:` (the mold-floor padding).
# Metric: count of inputs whose returned bounds tuple differs (an exception counts as its type name) between baseline
#   and mutant; the first moved rows.
# Perturbation: key 47430bf93e309e76 GUARD_OFF `if f.size < n_steps:` -> `if False:`, in memory. Direction: a mold-floor
#   series shorter than the horizon is no longer padded with -inf: np.maximum against the n-step floor raises (size > 1)
#   or broadcasts the single floor over every step (size 1).
# EXPECTED RESULT inputs_moved>0 (floors.size 2..n-1: ValueError; size 1: the floor applied to all n steps); null_delta=0.
# Null control: floors None.
from _arrays import run
from _bounds_cases import cases, NULL
run("_build_comfort_bounds", "if f.size < n_steps:", "if False:", cases(), NULL)
