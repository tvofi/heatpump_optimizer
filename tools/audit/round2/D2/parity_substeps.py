#!/usr/bin/env python
"""D2 harness -- scalar/batched simulation parity in the Euler sub-step regime.

Metric: max |T_batch - T_scalar| (deg C) over a 48-step trajectory between
ThermalModel.simulate_trajectory (scalar) and ThermalModel.simulate_trajectory_batch
(the solver's gradient twin) on the same schedule, per configuration cell; and
the plan the solver returns with vs without the batched jacobian at the worst cell.
Command:
  PYTHONPATH=tests/hastub python tools/audit/round2/D2/parity_substeps.py
  PYTHONPATH=tests/hastub python tools/audit/round2/D2/parity_substeps.py --perturb
Expected (baseline c398fc84, Apple M1, python 3.13, numpy 2.5, scipy 1.18):
  parity_max_diff_golden = 0 exactly (all 49 golden configs, bitwise);
  parity_max_diff_single_nsub1 = 0 exactly; parity_max_diff_two_zone_stiff = 0 exactly;
  parity_max_diff_single_stiff >> 1 deg C (single-zone cells with n_sub >= 2, inside
  the config-flow ranges RANGE_SLAB_THERMAL_MASS=(0.1,60), RANGE_SLAB_HEAT_TRANSFER=(0.02,5)).
Perturbation (--perturb): slab_heat_transfer 5.0 -> 0.8 on the worst cell (n_sub 2 -> 1):
  parity_max_diff_single_stiff -> 0 exactly (to_zero).
Instrumented: thermal_model:ThermalModel.simulate_trajectory_batch vs simulate_trajectory,
  thermal_model:ThermalModel._stability_substeps, optimizer:_bounds_supported_by_batch,
  optimizer:_batch_fd_gradient.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import resource
import sys
import time
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np
_T_PROC0 = time.process_time()
_T_THR0 = time.thread_time()

from scipy.optimize._numdiff import approx_derivative

import golden
from profiles import house, weather
from heatpump_optimizer import optimizer as optmod
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState

ap = argparse.ArgumentParser()
ap.add_argument("--perturb", action="store_true")
args = ap.parse_args()

START = golden.START
N = 48
rng = np.random.default_rng(11)
POWERS = rng.uniform(0.0, 6.0, size=(4, N))
ot, wi, ra, so = (np.asarray(a[:N], dtype=float) for a in weather("winter_cold", START))


def parity(params, state, powers=POWERS, ext=None, dt=0.25):
    m = ThermalModel(params)
    n_sub = m._stability_substeps(float(wi[0]), float(ra[0]), dt)
    batch = m.simulate_trajectory_batch(state, powers, ot, wi, ra, so, dt, ext, None, None, None)
    worst = 0.0
    finite = True
    for b in range(powers.shape[0]):
        r, s, u, l = m.simulate_trajectory(state, powers[b], ot, wi, ra, so, dt, ext, None, None, None)
        refs = [(batch["room"][b], r), (batch["slab"][b], s), (batch["upper"][b], u),
                (batch["lower"][b], l), (batch["buffer"][b], m.last_buffer_trajectory)]
        if batch["wood"] is not None:
            refs.append((batch["wood"][b], m.last_wood_trajectory))
        for arr, ref in refs:
            if not np.all(np.isfinite(arr)):
                finite = False
                worst = float("inf")
                continue
            d = float(np.max(np.abs(arr - ref)))
            worst = max(worst, d)
    return n_sub, worst, finite


def make_state(two_zone, wood=None):
    return ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=float(ot[0]),
                        upper_floor_temperature=21.0, lower_floor_temperature=21.0,
                        dhw_temperature=50.0, buffer_tank_temperature=40.0, wood_tank_temperature=wood)


# ---- 1. all 49 golden scenario configurations (the sweep the fixtures cover) ----
worst_golden = 0.0
for name, spec in golden.SCENARIOS.items():
    built = golden.make(**spec)
    p = built["optimizer"].model.params
    st = built["state"]
    ext = golden.external_heat_for(N) if name in golden.EXTERNAL_HEAT_SCENARIOS else None
    n_sub, d, fin = parity(p, st, ext=ext)
    worst_golden = max(worst_golden, d)
print(f"RESULT parity_golden_cells={len(golden.SCENARIOS)} count")
print(f"RESULT parity_max_diff_golden={worst_golden:.3e} degC")

# ---- 2. single-zone cells inside the config-flow ranges ----
single_cells = {
    # (slab_thermal_mass, slab_heat_transfer, house_thermal_mass)
    "slab0.1_k0.8_default_transfer": (0.1, 0.8, 10.0),
    "slab0.5_k5.0": (0.5, 5.0, 10.0),
    "slab0.3_k5.0": (0.3, 5.0, 10.0),
    "slab0.1_k5.0": (0.1, 5.0, 10.0),
    "house0.5_slab5_k5.0": (5.0, 5.0, 0.5),
    "slab0.2_k1.5": (0.2, 1.5, 10.0),
    # controls: n_sub == 1
    "slab1.0_k5.0_ctrl": (1.0, 5.0, 10.0),
    "slab0.5_k2.0_ctrl": (0.5, 2.0, 10.0),
    "default_ctrl": (5.0, 0.8, 10.0),
}
stiff_vals = {}
ctrl_worst = 0.0
for label, (c_slab, k_slab, c_room) in single_cells.items():
    if args.perturb and label == "slab0.5_k5.0":
        k_slab = 0.8
    cfg = house(two_zone=False, dhw=False)
    cfg.update({"slab_thermal_mass": c_slab, "slab_heat_transfer": k_slab, "house_thermal_mass": c_room})
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = False
    n_sub, d, fin = parity(p, make_state(False))
    print(f"CELL single {label}: n_sub={n_sub} max_diff={d:.3e} finite={fin}")
    if n_sub > 1:
        stiff_vals[label] = d
    else:
        ctrl_worst = max(ctrl_worst, d)
print(f"RESULT parity_max_diff_single_nsub1={ctrl_worst:.3e} degC")
vals = np.array([v for v in stiff_vals.values()], dtype=float)
finite_vals = vals[np.isfinite(vals)]
print(f"RESULT parity_single_stiff_cells={len(stiff_vals)} count")
print(f"RESULT parity_single_stiff_nonfinite_cells={int(np.sum(~np.isfinite(vals)))} count")
if finite_vals.size:
    print(f"RESULT parity_max_diff_single_stiff={float(np.max(finite_vals)):.3e} degC")
    print(f"RESULT parity_min_diff_single_stiff={float(np.min(finite_vals)):.3e} degC")
    loo = np.sort(finite_vals)[:-1] if finite_vals.size > 1 else finite_vals
    print(f"RESULT parity_single_stiff_drop_most_favourable_max={float(np.max(loo)) if loo.size else 0.0:.3e} degC")
else:
    print("RESULT parity_max_diff_single_stiff=inf degC")
if "slab0.5_k5.0" in stiff_vals or args.perturb:
    key = "slab0.5_k5.0"
    print(f"RESULT parity_diff_slab0.5_k5.0={stiff_vals.get(key, 0.0):.3e} degC")

# ---- 3. two-zone stiff cells: the two-zone twin honours dt/n_sub ----
two_cells = {
    "upper0.25_inter3.0": {"upper_floor_thermal_mass": 0.25, "inter_zone_heat_transfer": 3.0},
    "lower0.25_k5.0": {"lower_floor_thermal_mass": 0.25, "slab_heat_transfer": 5.0},
    "slab0.1_k5.0_valve": {"slab_thermal_mass": 0.1, "slab_heat_transfer": 5.0, "mixing_valve_mode": "manual",
                           "buffer_tank_volume": 750.0},
}
two_worst = 0.0
for label, over in two_cells.items():
    cfg = house(two_zone=True, dhw=False)
    cfg.update(over)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = False
    n_sub, d, fin = parity(p, make_state(True))
    print(f"CELL two-zone {label}: n_sub={n_sub} max_diff={d:.3e} finite={fin}")
    two_worst = max(two_worst, d)
print(f"RESULT parity_max_diff_two_zone_stiff={two_worst:.3e} degC")

# ---- 4. solver consequence at the worst reachable single-zone cell ----
cell_over = {"slab_thermal_mass": 0.5, "slab_heat_transfer": 0.8 if args.perturb else 5.0}


def solve(batch_on):
    built = golden.make(two_zone=False, dhw=False, config_overrides=cell_over)
    orig = optmod._bounds_supported_by_batch
    if not batch_on:
        optmod._bounds_supported_by_batch = lambda bounds: False
    try:
        res = built["optimizer"].optimize(built["state"], built["prices"], built["outdoor"],
                                          built["wind"], built["rain"], built["solar"], START)
    finally:
        optmod._bounds_supported_by_batch = orig
    return res


r_batch = solve(True)
r_scalar = solve(False)
xb = np.asarray(r_batch.power_schedule)
xs = np.asarray(r_scalar.power_schedule)
print(f"CELL solve batch-jac: status={r_batch.status} objective={r_batch.objective_value:.4f} cost={r_batch.predicted_cost:.4f}")
print(f"CELL solve scalar-jac: status={r_scalar.status} objective={r_scalar.objective_value:.4f} cost={r_scalar.predicted_cost:.4f}")
print(f"RESULT solve_objective_gap_batch_minus_scalar={r_batch.objective_value - r_scalar.objective_value:.4f} objective")
print(f"RESULT solve_schedule_l1_distance={float(np.sum(np.abs(xb - xs)) * 0.25):.4f} kWh")
print(f"RESULT solve_cost_batch={r_batch.predicted_cost:.4f} SEK")
print(f"RESULT solve_cost_scalar={r_scalar.predicted_cost:.4f} SEK")
print(f"RESULT solve_room_min_batch={float(np.min(r_batch.room_temp_trajectory)):.3f} degC")
print(f"RESULT solve_room_min_scalar={float(np.min(r_scalar.room_temp_trajectory)):.3f} degC")

# ---- 5. the gradient the solver uses vs scipy's own and vs a central difference ----
captured = {}


def capture_multi_start(objective, candidates, bounds, args=(), maxiter=300, batch_objective=None, fd_eps=1e-4):
    captured["objective"] = objective
    captured["batch"] = batch_objective
    captured["bounds"] = bounds
    captured["x0"] = np.asarray(candidates[0], dtype=float)
    captured["args"] = args
    raise RuntimeError("captured")


def grad_check(config_overrides, label):
    built = golden.make(two_zone=False, dhw=False, config_overrides=config_overrides)
    orig = optmod._multi_start_minimize
    optmod._multi_start_minimize = capture_multi_start
    try:
        built["optimizer"].optimize(built["state"], built["prices"], built["outdoor"],
                                    built["wind"], built["rain"], built["solar"], START)
    finally:
        optmod._multi_start_minimize = orig
    obj = captured["objective"]
    bobj = captured["batch"]
    bounds = captured["bounds"]
    lb = np.array([b[0] for b in bounds]); ub = np.array([b[1] for b in bounds])
    worst_batch_vs_scipy = 0.0
    worst_rel = 0.0
    worst_idx = -1
    rng2 = np.random.default_rng(5)
    for k in range(3):
        x0 = np.clip(rng2.uniform(0.2, 5.0, size=lb.size), lb, ub)
        f0 = float(obj(x0))
        g_batch = optmod._batch_fd_gradient(bobj, (), x0, f0, 1e-4, bounds)
        g_scipy = approx_derivative(obj, x0, method="2-point", abs_step=1e-4, f0=f0, bounds=(lb, ub))
        g_central = approx_derivative(obj, x0, method="3-point", abs_step=1e-3, bounds=(lb, ub))
        worst_batch_vs_scipy = max(worst_batch_vs_scipy, float(np.max(np.abs(g_batch - g_scipy))))
        rel = np.abs(g_scipy - g_central) / np.maximum(np.abs(g_central), 1e-3)
        i = int(np.argmax(rel))
        if rel[i] > worst_rel:
            worst_rel = float(rel[i]); worst_idx = i
    print(f"RESULT grad_batch_vs_scipy_maxabs_{label}={worst_batch_vs_scipy:.3e} objective_per_kW")
    print(f"RESULT grad_forward_vs_central_maxrel_{label}={worst_rel:.3e} ratio")
    print(f"RESULT grad_forward_vs_central_worst_step_{label}={worst_idx} index")


grad_check({}, "default")
grad_check(cell_over, "stiff")

proc = time.process_time() - _T_PROC0
thr = time.thread_time() - _T_THR0
print(f"RESULT thread_factor={proc / max(thr, 1e-9):.3f} ratio")
print(f"RESULT load1={os.getloadavg()[0]:.2f} load")
print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap} count")
