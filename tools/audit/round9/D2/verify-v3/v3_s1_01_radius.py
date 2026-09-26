#!/usr/bin/env python3
"""V3 (round 9, D2-s1-01): Euler step radius over the accepted ranges, and what a real solve publishes.

Metric (one line): (a) share of 20000 log-uniform random single-zone configs inside the
config-flow ranges (house mass, house loss, slab mass, slab transfer; NumberSelector
enforces these in real HA, tests/ha_contract.py marks NumberSelector faithful) whose
per-substep explicit-Euler matrix M = I + h*A (A the analytic 2x2 RC matrix, h = 0.25 h /
the production ThermalModel._stability_substeps count) has spectral radius > 1, checked
against the production trajectory (simulate_trajectory, zero input) leaving [0, 25] C;
(b) for the finder's named point (C=0.5, u=0.2, Cs=0.5, k=5.0) driven through a real
HeatPumpOptimizer.optimize (golden make(), winter_single_no_dhw weather/prices): max |room|
of the published room_temp_trajectory and whether predicted_cost is finite.
Command: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D2/verify-v3/v3_s1_01_radius.py [--perturb]
Perturbation (--perturb): thermal_model.EULER_STABILITY_MAX_RATIO 1.5 -> 1.0 in memory;
(a) must go to 0 and (b) max |room| must fall inside the physical envelope (direction: to_zero).
Expected at baseline: see verify-v3 report (random draw seeded 20260926, exact).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: G3-V3 cloud container, 4 cores, linux.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import copy, sys, time
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np
from heatpump_optimizer import thermal_model as tm
from heatpump_optimizer.config_flow import (RANGE_HOUSE_HEAT_LOSS, RANGE_HOUSE_THERMAL_MASS,
    RANGE_SLAB_HEAT_TRANSFER, RANGE_SLAB_THERMAL_MASS)

PERTURB = "--perturb" in sys.argv
if PERTURB:
    tm.EULER_STABILITY_MAX_RATIO = 1.0
t0p, t0t = time.process_time(), time.thread_time()
DT = 0.25
rng = np.random.default_rng(20260926)

def lu(r, n):
    return np.exp(rng.uniform(np.log(r[0]), np.log(r[1]), n))

N = 20000
C = lu(RANGE_HOUSE_THERMAL_MASS, N); U = lu(RANGE_HOUSE_HEAT_LOSS, N)
CS = lu(RANGE_SLAB_THERMAL_MASS, N); K = lu(RANGE_SLAB_HEAT_TRANSFER, N)
unstable = 0; traj_checked = 0; traj_agree = 0; worst = 0.0
for c, u, cs, k in zip(C, U, CS, K):
    p = tm.ThermalParameters.from_config({"house_thermal_mass": float(c), "house_heat_loss_coefficient": float(u),
        "slab_thermal_mass": float(cs), "slab_heat_transfer": float(k), "two_zone_mode": "off"})
    p.internal_gains = 0.0; p.internal_gains_profile = None
    m = tm.ThermalModel(p)
    n_sub = m._stability_substeps(0.0, 0.0, DT)
    h = DT / n_sub
    uu = p.heat_loss_coefficient * p.house_heat_loss_scale
    A = np.array([[-(uu + p.slab_heat_transfer) / p.room_thermal_mass, p.slab_heat_transfer / p.room_thermal_mass],
                  [p.slab_heat_transfer / p.slab_thermal_mass, -p.slab_heat_transfer / p.slab_thermal_mass]])
    rho = float(np.max(np.abs(np.linalg.eigvals(np.eye(2) + h * A))))
    worst = max(worst, rho)
    bad = rho > 1.0 + 1e-9
    unstable += bad
    # production cross-check on every unstable draw and every 50th stable one
    if bad or traj_checked < 400:
        traj_checked += 1
        s0 = tm.ThermalState(room_temperature=21.0, slab_temperature=25.0, upper_floor_temperature=21.0,
                             lower_floor_temperature=21.0, buffer_tank_temperature=21.0)
        r = m.simulate_trajectory(s0, np.zeros(96), np.zeros(96), dt_hours=DT)
        st = np.vstack([r[0], r[1]])
        out = (not np.all(np.isfinite(st))) or st.max() > 25 + 1e-6 or st.min() < -1e-6
        traj_agree += (out == bad)

print(f"RESULT random_configs={N} count")
print(f"RESULT analytic_rho_gt_1={unstable} configs")
print(f"RESULT analytic_rho_gt_1_share={unstable/N:.5f} ratio")
print(f"RESULT analytic_worst_rho={worst:.4f} ratio")
print(f"RESULT traj_crosscheck_agree={traj_agree}/{traj_checked} configs")

# (b) consequence through a real solve
from golden import make
built = make(dhw=False, config_overrides={"house_thermal_mass": 0.5, "house_heat_loss_coefficient": 0.2,
             "slab_thermal_mass": 0.5, "slab_heat_transfer": 5.0})
opt = built["optimizer"]
res = opt.optimize(built["state"], built["prices"], built["outdoor"], built["wind"], built["rain"],
                   built["solar"], __import__("golden").START, None, None)
room = np.asarray(res.room_temp_trajectory, float)
print(f"RESULT solve_n_sub={opt.model._stability_substeps(0.0,0.0,DT)} count")
print(f"RESULT solve_room_finite={int(np.all(np.isfinite(room)))} bool")
print(f"RESULT solve_room_max_abs={np.nanmax(np.abs(room)):.4g} degC")
print(f"RESULT solve_room_range={np.nanmin(room):.4g}..{np.nanmax(room):.4g} degC")
print(f"RESULT solve_predicted_cost={res.predicted_cost!r} currency")
print(f"RESULT solve_power_sum_kwh={float(np.sum(res.power_schedule))*DT:.4g} kWh")
print(f"RESULT perturbed={int(PERTURB)}")
dp, dtt = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={dp/max(dtt,1e-9):.4f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
sw = 0
try:
    for line in open("/proc/vmstat"):
        if line.startswith("pswpin"): sw = int(line.split()[1])
except OSError: pass
print(f"RESULT swapins={sw}")
