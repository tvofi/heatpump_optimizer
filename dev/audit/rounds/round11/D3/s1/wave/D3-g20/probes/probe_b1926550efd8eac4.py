#!/usr/bin/env python3
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_b1926550efd8eac4.py
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g20 (4 vCPU Intel Xeon @ 2.10GHz).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._co_optimize, line 3969
#   `pinned = (dhw_power > 1e-6) & (space_power >= headroom - 1e-3)`, driven with a recording planner stand-in (_coopt.py).
# Metric: per one-step input, (returned status, steps handed to the DHW re-plan as pinned at p_max); count of inputs
#   whose pair differs between baseline and mutant. "replanned" = the re-plan was adopted, "ok" = returned unchanged.
# Perturbation: key b1926550efd8eac4 CMP_BOUND `dhw_power > 1e-6` -> `>= 1e-6`, in memory. Only a step whose hot-water power
#   is exactly 1e-6 kW differs. Direction: at that tie a step against its ceiling becomes pinned and the re-plan runs
#   (status replanned, pinned 1 instead of ok, 0).
# EXPECTED RESULT inputs_moved = the dhw=1e-06 rows with space >= headroom - 1e-3; null_delta=0.
# Null control: dhw=1.0, space=1.0.
from _coopt import run
run("pinned = (dhw_power > 1e-6) & (space_power >= headroom - 1e-3)",
    "pinned = (dhw_power >= 1e-6) & (space_power >= headroom - 1e-3)", "dhw=1e-06 space=head (")
