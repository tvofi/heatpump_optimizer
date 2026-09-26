#!/usr/bin/env python3
"""V2 (independent) re-measure of D2-s1-01: Euler sub-step guard vs coupled stores.

Metric (one line): over a seeded log-uniform Monte-Carlo sample of the config-flow
ranges (NOT a geometric grid), the share of configurations whose zero-input 24 h
production trajectory (ThermalModel.simulate_step, P=0, no gains, T_out=0, stores
21, slab 25, dt 0.25 h) leaves [0, 25] degC by > 1e-6 K; beside it the analytic
per-substep spectral radius max|eig(I + A*h/n_sub)| of MY OWN RC matrix A (not a
finite difference of the step), with n_sub taken from the production
_stability_substeps. Also the same share on a "plausible" subset (every room/zone
and slab mass >= 2 kWh/K).
Count key: temperatures ThermalModel.simulate_step returns.
Hooks: thermal_model:ThermalModel._stability_substeps, ThermalModel.simulate_step.
Perturbation: --perturb=ratio1 (EULER_STABILITY_MAX_RATIO 1.5 -> 1.0 in memory):
escapes must go to 0.
Command: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D2/verify-v2/v2_stability.py [--perturb=ratio1]
Expected: see verify-v2.md (deterministic, seed 9902; exact counts).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; box G3-V2 (4-core linux cloud container, py3.14.0rc2).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
sys.path.insert(0, "custom_components")
import numpy as np  # noqa: E402
from heatpump_optimizer import thermal_model as tm  # noqa: E402

if "--perturb=ratio1" in sys.argv:
    tm.EULER_STABILITY_MAX_RATIO = 1.0
t0p, t0t = time.process_time(), time.thread_time()
rng = np.random.default_rng(9902)
DT, N = 0.25, 96


def lu(lo, hi):
    return float(np.exp(rng.uniform(np.log(lo), np.log(hi))))


def run_one(two_zone):
    p = tm.ThermalParameters()
    p.internal_gains = 0.0
    p.internal_gains_profile = None
    p.wind_sensitivity = 0.0
    if two_zone:
        p.two_zone_enabled = True
        p.upper_floor_thermal_mass = lu(0.25, 60.0)
        p.lower_floor_thermal_mass = lu(0.25, 60.0)
        p.upper_floor_heat_loss = lu(0.001, 1.0)
        p.lower_floor_heat_loss = lu(0.001, 1.0)
        p.lower_floor_loss_ratio = 1.0
        p.inter_zone_transfer = lu(0.01, 3.0)
        p.slab_thermal_mass = lu(0.1, 60.0)
        p.slab_heat_transfer = lu(0.02, 5.0)
        masses = (p.upper_floor_thermal_mass, p.lower_floor_thermal_mass, p.slab_thermal_mass)
        uu, ul, iz, k = p.upper_floor_heat_loss, p.lower_floor_heat_loss, p.inter_zone_transfer, p.slab_heat_transfer
        cu, cl, cs = masses
        A = np.array([[-(uu + iz) / cu, iz / cu, 0.0],
                      [iz / cl, -(ul + iz + k) / cl, k / cl],
                      [0.0, k / cs, -k / cs]])
    else:
        p.two_zone_enabled = False
        p.room_thermal_mass = lu(0.5, 80.0)
        p.heat_loss_coefficient = lu(0.01, 1.0)
        p.slab_thermal_mass = lu(0.1, 60.0)
        p.slab_heat_transfer = lu(0.02, 5.0)
        masses = (p.room_thermal_mass, p.slab_thermal_mass)
        cr, cs, u, k = p.room_thermal_mass, p.slab_thermal_mass, p.heat_loss_coefficient, p.slab_heat_transfer
        A = np.array([[-(u + k) / cr, k / cr], [k / cs, -k / cs]])
    m = tm.ThermalModel(p)
    n_sub = m._stability_substeps(0.0, 0.0, DT)
    h = DT / n_sub
    rho = float(np.max(np.abs(np.linalg.eigvals(np.eye(len(A)) + A * h))))
    s = tm.ThermalState(room_temperature=21.0, slab_temperature=25.0,
                        upper_floor_temperature=21.0, lower_floor_temperature=21.0,
                        buffer_tank_temperature=21.0, outdoor_temperature=0.0)
    exc = 0.0
    with np.errstate(all="ignore"):
        for _ in range(N):
            s = m.simulate_step(s, 0.0, 0.0, 0.0, 0.0, 0.0, DT)
            vals = [s.slab_temperature] + ([s.upper_floor_temperature, s.lower_floor_temperature]
                                           if two_zone else [s.room_temperature])
            for v in vals:
                if not np.isfinite(v):
                    exc = float("inf")
                else:
                    exc = max(exc, v - 25.0, 0.0 - v)
            if exc == float("inf"):
                break
    return exc > 1e-6, rho, min(masses) >= 2.0, exc, min(masses)


for label, tz, n in (("1z", False, 1500), ("2z", True, 1500)):
    esc = rho_gt1 = agree = plaus = plaus_esc = div100 = 0
    worst = 0.0
    esc_mass = 0.0
    for _ in range(n):
        e, rho, pl, exc, mmin = run_one(tz)
        if e:
            esc_mass = max(esc_mass, mmin)
        esc += e
        rho_gt1 += rho > 1.0 + 1e-9
        agree += e == (rho > 1.0 + 1e-9)
        div100 += not exc < 100.0
        plaus += pl
        plaus_esc += e and pl
        worst = max(worst, rho)
    print(f"RESULT mc{label}_samples={n} count")
    print(f"RESULT mc{label}_escapes={esc} count")
    print(f"RESULT mc{label}_diverged_100K={div100} count")
    print(f"RESULT mc{label}_analytic_rho_gt1={rho_gt1} count")
    print(f"RESULT mc{label}_escape_vs_rho_agreement={agree} of {n}")
    print(f"RESULT mc{label}_worst_analytic_rho={worst:.4f}")
    print(f"RESULT mc{label}_plausible_samples={plaus} count")
    print(f"RESULT mc{label}_plausible_escapes={plaus_esc} count")
    print(f"RESULT mc{label}_largest_min_mass_among_escapes={esc_mass:.3f} kWh/K", flush=True)

pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / max(tc, 1e-9):.4f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = next(int(ln.split()[1]) for ln in open("/proc/vmstat") if ln.startswith("pswpin"))
except Exception:
    sw = -1
print(f"RESULT swapins={sw}")
