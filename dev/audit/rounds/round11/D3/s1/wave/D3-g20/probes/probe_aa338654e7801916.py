#!/usr/bin/env python3
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_aa338654e7801916.py
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g20 (4 vCPU Intel Xeon @ 2.10GHz).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._buffer_charge_ceiling (out_mean, humidity None).
# Metric: count of inputs (buffer_max_temp x outdoor mean x tank UA grid, plus constructed exact ties net(T)==0.0)
#   whose returned charge ceiling (C) differs between the baseline and the mutant; the moved values themselves.
# Null control: default parameters at out_mean 15 C (net(hi) > 0, returns buffer_max_temp on both arms).
# Perturbation: key aa338654e7801916 GUARD_OFF line 6070 `if hi <= lo:` -> `if False:`, in memory. Direction: with
#   buffer_max_temp below the 35 C flow reference and net(hi) <= 0 the mutant returns lo = 35 C, ABOVE the tank's own rating.
# EXPECTED RESULT inputs_moved>0; focus hi=30.0 out=-30.0: baseline=30.0, mutant=35.0; null_delta=0.
from _ceiling import run
run("if hi <= lo:", "if False:", focus="hi=30.0 out=-30.0 ua=None")
