#!/usr/bin/env python3
"""D2.M1 DHW refill coil: energy conservation across the wood and DHW stores.

Metric (one line): per step, coil_residual = (heat the coil took out of the
wood tank) - (heat the coil spared the DHW tank), kWh, from two runs of
ThermalModel.simulate_trajectory_with_dhw identical but for
dhw_wood_coil_enabled. The tap delivers the same water in both runs (the
coil only preheats the refill), so conservation requires residual == 0.

Count key: the wood and DHW temperatures simulate_trajectory_with_dhw
returns, times each store's own capacity (C_w = wood_tank_thermal_mass,
C_dhw = dhw_tank_thermal_mass) -- the delivered values, never the draw
inputs or the coil helper's own return.

Hooks: thermal_model:ThermalModel.simulate_trajectory_with_dhw (and through
it thermal_model:dhw_coil_draw_reduction and ThermalModel.simulate_dhw_step).

Command (from the export root):
  PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python tools/audit/round9/D2/s1/m1_coil.py
  ... --perturb=mixuse   (thermal_model.DHW_MIXED_USE_TEMP -> inlet + 1e-3 K,
                          which makes the tank-temperature draw scale 1 above the
                          inlet; the residual must go to ~0)
Expected at baseline: residual 0 (|r| < 1e-12) for every DHW tank at or above
40 degC (the null control, measured 3.3e-15); below it 28/28 cells > 0, max
0.405991 kWh, 0.054010 at DHW 35 / wood 70; under --perturb=mixuse 0/28.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, box B4 (cloud container, linux).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import copy
import sys
import time

import numpy as np

sys.path.insert(0, "custom_components")
from heatpump_optimizer import mixing_valve  # noqa: E402
from heatpump_optimizer import thermal_model as tm  # noqa: E402

PERTURB = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--perturb=")), "")

_t0p, _t0t = time.process_time(), time.thread_time()

BASE = dict(two_zone_enabled=True, mixing_valve_mode=mixing_valve.MODE_MANUAL,
            buffer_tank_volume=200.0, wood_tank_configured=True, wood_tank_volume=500.0,
            dhw_enabled=True, dhw_tank_volume=200.0, dhw_setpoint=55.0)


def model(coil):
    p = tm.ThermalParameters(**BASE, dhw_wood_coil_enabled=coil)
    assert p.dhw_coil_active == coil
    return tm.ThermalModel(p)


M_ON, M_OFF = model(True), model(False)
if PERTURB == "mixuse":
    tm.DHW_MIXED_USE_TEMP = M_ON.params.dhw_inlet_reference + 1e-3
C_W = M_ON.params.wood_tank_thermal_mass
C_D = M_ON.params.dhw_tank_thermal_mass


def run(m, dhw0, wood0, n, draw):
    s = tm.ThermalState(room_temperature=21.0, slab_temperature=24.0,
                        upper_floor_temperature=21.0, lower_floor_temperature=21.0,
                        buffer_tank_temperature=40.0, dhw_temperature=dhw0,
                        wood_tank_temperature=wood0)
    r = m.simulate_trajectory_with_dhw(
        initial_state=copy.deepcopy(s), space_power_schedule=np.zeros(n),
        dhw_power_schedule=np.zeros(n), outdoor_temps=np.full(n, 0.0),
        start_hour=7.0, dt_hours=0.25, dhw_draw_rates=np.full(n, draw))
    # Heat the inlet floor fabricated on the last step is booked, not physics.
    return r[4], r[6], m._step_dhw_floor_injected * 0.25


def residual(dhw0, wood0, n=1, draw=2.0):
    d_on, w_on, f_on = run(M_ON, dhw0, wood0, n, draw)
    d_off, w_off, f_off = run(M_OFF, dhw0, wood0, n, draw)
    wood_out = C_W * (w_off[-1] - w_on[-1])
    dhw_spared = C_D * (d_on[-1] - d_off[-1]) - (f_on - f_off)
    return wood_out - dhw_spared, wood_out


worst_below = 0.0
worst_at = None
null_worst = 0.0
cells = []
for dhw0 in (12.0, 15.0, 20.0, 25.0, 30.0, 35.0, 39.0, 40.0, 45.0, 50.0, 55.0, 60.0):
    for wood0 in (30.0, 50.0, 70.0, 90.0):
        r, coil = residual(dhw0, wood0)
        if dhw0 >= 40.0:
            null_worst = max(null_worst, abs(r))
        else:
            cells.append(r)
            if r > worst_below:
                worst_below, worst_at = r, (dhw0, wood0, coil)

print(f"RESULT coil_residual_null_max_at_or_above_40C={null_worst:.3e} kWh")
print(f"RESULT coil_residual_cells_below_40C={len(cells)} count")
print(f"RESULT coil_residual_cells_nonzero_below_40C={sum(1 for c in cells if c > 1e-12)} count")
print(f"RESULT coil_residual_max_one_step={worst_below:.6f} kWh")
print(f"# worst at dhw0={worst_at[0]} wood0={worst_at[1]} (coil took {worst_at[2]:.6f} kWh)")
srt = sorted(cells)
print(f"RESULT coil_residual_min_one_step={srt[0]:.6f} kWh")
print(f"RESULT coil_residual_drop_most_favourable={srt[-2]:.6f} kWh")
r35, c35 = residual(35.0, 70.0)
print(f"RESULT coil_residual_dhw35_wood70={r35:.6f} kWh (coil took {c35:.6f} kWh)")

pc, tc = time.process_time() - _t0p, time.thread_time() - _t0t
print(f"RESULT thread_factor={pc / max(tc, 1e-9):.4f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    with open("/proc/vmstat") as fh:
        sw = next(int(ln.split()[1]) for ln in fh if ln.startswith("pswpin"))
except (OSError, StopIteration):
    sw = -1
print(f"RESULT swapins={sw}")
