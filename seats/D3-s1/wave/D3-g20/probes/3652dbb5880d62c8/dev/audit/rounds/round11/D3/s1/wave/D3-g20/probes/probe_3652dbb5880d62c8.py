#!/usr/bin/env python3
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_3652dbb5880d62c8.py
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g20 (4 vCPU Intel Xeon @ 2.10GHz).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._co_optimize, line 3969
#   `pinned = (dhw_power > 1e-6) & (space_power >= headroom - 1e-3)`, driven with a recording planner stand-in (_coopt.py).
# Metric: per one-step input, (returned status, steps handed to the DHW re-plan as pinned at p_max); count of inputs
#   whose pair differs between baseline and mutant. "replanned" = the re-plan was adopted, "ok" = returned unchanged.
# Perturbation: key 3652dbb5880d62c8 CMP_BOUND `space_power >= headroom - 1e-3` -> `>`, in memory. Only a step whose space
#   power equals headroom - 1e-3 exactly differs. Direction: at that tie the step is no longer pinned; with no other pinned
#   step the re-plan is skipped (status ok, pinned 0 instead of replanned, 1).
# EXPECTED RESULT inputs_moved = the `tie head-1e-3` rows with dhw > 1e-6; null_delta=0.
# Null control: dhw=1.0, space=1.0 (unpinned on both arms).
from _coopt import run
run("pinned = (dhw_power > 1e-6) & (space_power >= headroom - 1e-3)",
    "pinned = (dhw_power > 1e-6) & (space_power > headroom - 1e-3)", "dhw=1.0 space=tie")
