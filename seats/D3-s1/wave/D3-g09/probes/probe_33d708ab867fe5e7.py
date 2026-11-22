#!/usr/bin/env python3
# Metric: HeatPumpOptimizerCoordinator._predicted_next_room_temp() (degC; the trajectory point it picks) on a
#   ramp trajectory 20.0 + 0.1*i, compared baseline vs mutant over optimization_interval x time_step_minutes.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_33d708ab867fe5e7.py
# EXPECTED RESULT production_time_step_minutes=15.0 and differing_cells_reachable=0 (the step is the dataclass
#   default; no config path writes it); differing cells appear only at time_step_minutes < 1.0 (0.5: a different
#   point; 0.0: the mutant raises ZeroDivisionError).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g09 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._predicted_next_room_temp
#   (coordinator.py:10262 `/ max(ctx._opt_config.time_step_minutes, 1.0)`).
# Perturbation: mutant 33d708ab867fe5e7, `max(time_step_minutes, 1.0)` -> `(time_step_minutes)`, in memory.
#   Direction: none on any reachable input (equivalent-candidate); a sub-minute step moves the index.
# Null control: the time_step 15.0 cells, where the clamp is inactive by construction.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _probe_lib as L  # noqa: E402
import _pred_common as P  # noqa: E402

OLD = "/ max(ctx._opt_config.time_step_minutes, 1.0)"
NEW = "/ (ctx._opt_config.time_step_minutes)"
MUT = L.mutant(P.C, "_predicted_next_room_temp", OLD, NEW)
print(f"RESULT production_time_step_minutes={L.coord()._opt_config.time_step_minutes}")
traj = [20.0 + 0.1 * i for i in range(97)]
reach = other = 0
tried = []
for interval in (10, 15, 30, 60, 120):
    for ts in (15.0, 5.0, 1.0, 0.5, 0.0):
        b, m = P.call(P.make(interval, ts), traj), P.call(P.make(interval, ts), traj, MUT)
        tried.append(f"{interval}/{ts}")
        if b != m:
            if ts >= 1.0:
                reach += 1
            else:
                other += 1
            print(f"RESULT differ interval={interval} time_step={ts} baseline={b} mutant={m}")
print(f"RESULT differing_cells_reachable={reach}")
print(f"RESULT differing_cells_subminute_step={other}")
print(f"RESULT inputs_tried={len(tried)} (interval/time_step: {' '.join(tried)})")
L.trailer()
