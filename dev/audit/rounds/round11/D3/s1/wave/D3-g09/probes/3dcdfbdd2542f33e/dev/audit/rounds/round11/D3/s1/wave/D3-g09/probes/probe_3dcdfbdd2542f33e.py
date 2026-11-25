#!/usr/bin/env python3
# Metric: HeatPumpOptimizerCoordinator._predicted_next_room_temp() (degC) baseline vs mutant, over trajectory
#   lengths 1..12 and 97 (the production plan's n_steps+1) at every optimization_interval 10..120 by 5.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_3dcdfbdd2542f33e.py
# EXPECTED RESULT production_trajectory_len=97 and differing_cells_at_production_len=0; differing cells
#   (mutant raises IndexError) only where len(trajectory) <= steps = round(interval/15) <= 8.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g09 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._predicted_next_room_temp
#   (coordinator.py:10267 `idx = min(steps, len(trajectory) - 1)`).
# Perturbation: mutant 3dcdfbdd2542f33e, `min(steps, len(trajectory) - 1)` -> `(steps)`, in memory.
#   Direction: none at the production length; IndexError on a trajectory no longer than steps.
# Reach: the one OptimizationResult constructor (optimizer.py:3848) emits n_steps+1 points with the forecasts
#   held flat to opt_config.n_steps (coordinator.py:7475), so a trajectory of <= 8 points is not produced.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _probe_lib as L  # noqa: E402
import _pred_common as P  # noqa: E402

OLD = "idx = min(steps, len(trajectory) - 1)"
NEW = "idx = (steps)"
MUT = L.mutant(P.C, "_predicted_next_room_temp", OLD, NEW)
n_prod = L.coord()._opt_config.n_steps + 1
print(f"RESULT production_trajectory_len={n_prod}")
at_prod = short = cells = 0
for interval in range(10, 125, 5):
    for n in list(range(1, 13)) + [n_prod]:
        traj = [20.0 + 0.1 * i for i in range(n)]
        b, m = P.call(P.make(interval), traj), P.call(P.make(interval), traj, MUT)
        cells += 1
        if b != m:
            if n == n_prod:
                at_prod += 1
            else:
                short += 1
            if interval in (30, 120) and n in (1, 2, 8):
                print(f"RESULT differ interval={interval} len={n} baseline={b} mutant={m}")
print(f"RESULT differing_cells_at_production_len={at_prod}")
print(f"RESULT differing_cells_short_trajectory={short}")
print(f"RESULT cells_tried={cells}")
L.trailer()
