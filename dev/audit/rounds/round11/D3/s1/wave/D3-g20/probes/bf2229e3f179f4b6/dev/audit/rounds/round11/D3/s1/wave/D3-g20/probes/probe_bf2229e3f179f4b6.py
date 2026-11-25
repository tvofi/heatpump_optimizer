#!/usr/bin/env python3
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_bf2229e3f179f4b6.py
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g20 (4 vCPU Intel Xeon @ 2.10GHz).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._buffer_charge_ceiling (out_mean, humidity None).
# Metric: count of inputs (buffer_max_temp x outdoor mean x tank UA grid, plus constructed exact ties net(T)==0.0)
#   whose returned charge ceiling (C) differs between the baseline and the mutant; the moved values themselves.
# Null control: default parameters at out_mean 15 C (net(hi) > 0, returns buffer_max_temp on both arms).
# Perturbation: key bf2229e3f179f4b6 CMP_BOUND line 6097 `if net(mid) > 0.0:` -> `>= 0.0`, in memory. Only net(mid) == 0.0
#   at a bisection midpoint differs: the baseline sets hi = mid and returns lo just below it, the mutant sets lo = mid and
#   returns mid exactly. Direction: ceiling up by about (hi - lo) / 2**32 at the constructed tie at the first midpoint.
# EXPECTED RESULT moved only on the `tie net(mid)==0` rows, |delta| ~ 1e-8 C; null_delta=0.
from _ceiling import run
run("if net(mid) > 0.0:", "if net(mid) >= 0.0:", focus="tie net(mid)")
