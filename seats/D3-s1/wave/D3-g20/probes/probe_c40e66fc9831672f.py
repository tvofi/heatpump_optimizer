#!/usr/bin/env python3
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_c40e66fc9831672f.py
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g20 (4 vCPU Intel Xeon @ 2.10GHz).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._buffer_charge_ceiling (out_mean, humidity None).
# Metric: count of inputs (buffer_max_temp x outdoor mean x tank UA grid, plus constructed exact ties net(T)==0.0)
#   whose returned charge ceiling (C) differs between the baseline and the mutant; the moved values themselves.
# Null control: default parameters at out_mean 15 C (net(hi) > 0, returns buffer_max_temp on both arms).
# Perturbation: key c40e66fc9831672f CLAMP_DROP line 6069 `lo = max(20.0, float(p.cop_flow_reference_temp))` -> `lo = (20.0)`,
#   in memory. Direction: in cold weather where net(35) <= 0 the baseline returns 35 C; the mutant bisects down from 35 into
#   [20, 35] and returns a LOWER ceiling.
# EXPECTED RESULT inputs_moved>0; focus hi=70.0 out=-20.0: baseline=35.0, mutant<35.0; null_delta=0.
from _ceiling import run
run("lo = max(20.0, float(p.cop_flow_reference_temp))", "lo = (20.0)", focus="hi=70.0 out=-20.0 ua=None")
