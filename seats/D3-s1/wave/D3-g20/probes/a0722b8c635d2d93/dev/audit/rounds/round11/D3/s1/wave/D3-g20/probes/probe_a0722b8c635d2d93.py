#!/usr/bin/env python3
# Metric: count of _anticipatory_weights inputs whose returned weight vector differs (np.array_equal, nan-equal;
#   an exception counts as its type name) between the baseline and the mutant, over a grid of dt x n_steps x
#   solar x loss including dt > 8 h (lookahead int(8/dt) == 0, the only case where `end <= i` and `end < i` differ).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_a0722b8c635d2d93.py
# EXPECTED RESULT inputs_moved=0 count (equivalent at the output: the mutant's empty slice gives np.mean([])=nan,
#   nan > 0.5 and nan > 1.1 are False, the weight stays 1.0); null_delta=0.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g20 (4 vCPU Intel Xeon @ 2.10GHz).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._anticipatory_weights,
#   line 3402 `if end <= i:`.
# Perturbation: key a0722b8c635d2d93 CMP_BOUND `if end <= i:` -> `if end < i:`, applied in memory (method
#   re-compiled from its own source, patched onto the class for the mutant arm). Direction: none expected.
# Null control: dt=0.25 h, n=96, solar=loss=2.0 (lookahead 32, end > i always).
from _weights import run
run("if end <= i:", "if end < i:", "dt=9.0 n=4 solar=2.0 loss=2.0")
