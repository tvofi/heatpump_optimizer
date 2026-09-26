#!/usr/bin/env bash
# D14 sweep, class "fit integrator differs from the simulated plant".
# Finding: D7-s2-01 (verified, medium -- sysid:identify_slab rolls the candidate through
# _simulate_slab_path -> _valve_drive -> ThermalModel.simulate_step(dt_hours=<sample interval>):
# one explicit-Euler step per 30-min recorded sample, coarser than the optimizer's own 0.25h
# step and far coarser than a continuous rollout. On a noise-free, parameter-exact house this
# biases the fit 17-25% low or refuses it, adopting on 0 of 3 presets at the fit's own
# resolution. Heavy per-preset rollout grid NOT re-run here (moderate-cost numeric harness,
# small N class); reusing the finder's own REPORT.md table and harness
# tools/audit/round9/D7/s2/sysid_plant.py.
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../../.." && pwd)"
grep -n "_simulate_slab_path(\|_valve_drive(\|dt_hours=\|def identify_slab\|def identify\b" custom_components/heatpump_optimizer/sysid.py
