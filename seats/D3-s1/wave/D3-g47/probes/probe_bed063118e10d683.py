#!/usr/bin/env python3
# Metric: returned (target, updated) of learner_newton_step at base_u == 1e-6 exactly (baseline None, mutant a step)
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g47/probes/probe_bed063118e10d683.py
# EXPECTED RESULT: inputs_differing=1: baseline None, mutant tuple at base_u=1e-6 exactly
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g47 (4 vCPU Xeon @ 2.30GHz). Values are exact (no wall/CPU numbers).
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:learner_newton_step (line 3073).
# Perturbation: the gate's one-line mutant `if base_u <= 1e-6 or capacity <= 1e-6:` -> `if base_u < 1e-6 or capacity <= 1e-6:` applied in memory (g47_mut.load re-compiles the module source with that one line
#   replaced; nothing on disk changes). Direction: see EXPECTED. Null control: `controls` inputs where the edit cannot matter must show 0 differing.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import g47_mut
INF, NAN = float("inf"), float("nan")
inputs = [dict(current=1.0, base_u=1e-6, capacity=2.0e4, residual=0.1, delta_t=10.0, dt_hours=0.25, trust_region=0.1, alpha=0.2), dict(current=1.0, base_u=1e-6 - 1e-12, capacity=2.0e4, residual=0.1, delta_t=10.0, dt_hours=0.25, trust_region=0.1, alpha=0.2)]
controls = [dict(current=1.0, base_u=1e-6 + 1e-9, capacity=2.0e4, residual=0.1, delta_t=10.0, dt_hours=0.25, trust_region=0.1, alpha=0.2), dict(current=1.0, base_u=0.5, capacity=2.0e4, residual=0.1, delta_t=10.0, dt_hours=0.25, trust_region=0.1, alpha=0.2), dict(current=1.0, base_u=0.0, capacity=2.0e4, residual=0.1, delta_t=10.0, dt_hours=0.25, trust_region=0.1, alpha=0.2)]
g47_mut.probe('bed063118e10d683', 'learner_newton_step', inputs, controls)
