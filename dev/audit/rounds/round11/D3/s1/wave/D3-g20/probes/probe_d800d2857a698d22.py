#!/usr/bin/env python3
# Metric: count of _anticipatory_weights inputs whose returned weight vector differs between baseline and mutant,
#   and weight[0] at the tie (constant solar gain exactly 0.5 kW, loss factor 1.0, dt 0.25 h, n 4).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_d800d2857a698d22.py
# EXPECTED RESULT tie_baseline_weight0=1.0, tie_mutant_weight0=0.85 (max(0.6, 1 - 0.5*0.3)); inputs_moved>0; null_delta=0.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g20 (4 vCPU Intel Xeon @ 2.10GHz).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._anticipatory_weights,
#   line 3405 `if future_solar > 0.5:`.
# Perturbation: key d800d2857a698d22 CMP_BOUND `>` -> `>=`, in memory. Direction: weight at mean solar == 0.5
#   falls 1.0 -> 0.85.
# Null control: solar=loss=2.0 (comparison true either way).
from _weights import run
run("if future_solar > 0.5:  # > 0.5 kW solar gain is significant",
    "if future_solar >= 0.5:  # > 0.5 kW solar gain is significant",
    "dt=0.25 n=4 solar=0.5 loss=1.0")
