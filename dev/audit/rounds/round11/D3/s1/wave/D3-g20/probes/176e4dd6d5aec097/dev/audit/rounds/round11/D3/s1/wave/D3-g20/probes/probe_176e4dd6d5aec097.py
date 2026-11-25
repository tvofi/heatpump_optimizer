#!/usr/bin/env python3
# Metric: count of _anticipatory_weights inputs whose returned weight vector differs between baseline and mutant,
#   and weight[0] at the tie (constant loss factor exactly 1.1, solar 0, dt 0.25 h, n 4).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_176e4dd6d5aec097.py
# EXPECTED RESULT tie_baseline_weight0=1.0, tie_mutant_weight0=1.1 (min(1.5, 1.1)); inputs_moved>0; null_delta=0.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g20 (4 vCPU Intel Xeon @ 2.10GHz).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._anticipatory_weights,
#   line 3408 `if future_loss > 1.1:`.
# Perturbation: key 176e4dd6d5aec097 CMP_BOUND `>` -> `>=`, in memory. Direction: weight at mean loss == 1.1
#   rises 1.0 -> 1.1.
# Null control: solar=loss=2.0.
from _weights import run
run("if future_loss > 1.1:", "if future_loss >= 1.1:", "dt=0.25 n=4 solar=0.0 loss=1.1")
