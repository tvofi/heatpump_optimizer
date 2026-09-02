#!/usr/bin/env python
"""D2-01 fix harness -- scalar/batched parity in the Euler sub-step regime,
and what the divergence costs the plan at the minimally reachable cell.

Metric: max |T_batch - T_scalar| (deg C) over a 48-step trajectory between
ThermalModel.simulate_trajectory (the model of record) and
ThermalModel.simulate_trajectory_batch (the solver's gradient twin) on the same
schedule, per configuration cell; and the predicted cost (SEK/day, scored by the
scalar path either way) of the plan HeatPumpOptimizer.optimize returns with the
batched jacobian versus with scipy's own scalar FD jacobian, at the single-zone
cell one field off the defaults.

Command:
  PYTHONPATH=tests/hastub python tools/audit/round2/D2/fix/parity_plan_cost.py
  PYTHONPATH=tests/hastub python tools/audit/round2/D2/fix/parity_plan_cost.py --perturb

Expected AFTER the fix (head 7c1b9f1..., Apple M1 8 GB, python 3.13.1,
numpy 2.5.2, scipy 1.18.1, five BLAS thread variables = 1):
  parity_max_diff_golden           = 0.000e+00 degC (exact)
  parity_max_diff_single_nsub1     = 0.000e+00 degC (exact)
  parity_max_diff_single_stiff     = 0.000e+00 degC (exact)
  parity_diff_minimal_cell         = 0.000e+00 degC (exact)
  parity_max_diff_two_zone_stiff   = 0.000e+00 degC (exact)
  plan_cost_delta_minimal          = 0.0000 SEK    (exact)
  plan_schedule_l1_minimal         = 0.0000 kWh    (exact)
  grad_batch_vs_scipy_maxabs_minimal = 0.000e+00   (exact)
Reach, unchanged by the fix (it is a property of the guard, not of the branch):
  reach_preset_configs             = 1320  count (exact)
  reach_preset_nsub_ge2            = 0     count (exact)
  reach_selector_grid_points       = 18513 count (exact)
  reach_selector_grid_nsub_ge2     = 2805  count (exact)
  reach_two_field_grid_nsub_ge2    = 60    count (exact, at the default mass)
BEFORE the fix (baseline 024130c7, the same box), the same lines read
  parity_max_diff_single_stiff  >= 5 degC, up to non-finite;
  parity_diff_minimal_cell      = 3.788e+01 degC;
  plan_cost_delta_minimal       > +60 SEK on a ~31 SEK/day plan.
Every "exact" above is a bitwise equality, so the tolerance is zero: these are
counts and identities, not timings, and none of them needs a quiet box.

Perturbation (--perturb): the minimal cell's `slab_thermal_mass` goes from the
config flow's own selector MINIMUM 0.1 back to the shipped default 5.0, which
takes _stability_substeps from 2 to 1. Direction: every stiff-cell RESULT above
goes to zero on the unfixed tree too, because the defect lives only in the
sub-step regime. On the fixed tree the perturbation changes nothing, because
nothing was non-zero.

Instrumented production symbols:
  thermal_model:ThermalModel.simulate_trajectory_batch (vs simulate_trajectory)
  thermal_model:ThermalModel._stability_substeps
  optimizer:_bounds_supported_by_batch  (forced False for the scalar-jac arm)
  optimizer:_batch_fd_gradient
  presets:derive                        (the questionnaire reach sweep)

Writes nothing anywhere.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import itertools
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
from heatpump_optimizer import presets
from heatpump_optimizer.config_flow import (
    RANGE_HOUSE_THERMAL_MASS,
    RANGE_SLAB_HEAT_TRANSFER,
    RANGE_SLAB_THERMAL_MASS,
)
from heatpump_optimizer.thermal_model import (
    ThermalModel,
    ThermalParameters,
    ThermalState,
)

ap = argparse.ArgumentParser()
ap.add_argument("--perturb", action="store_true")
args = ap.parse_args()

START = golden.START
N = 48
POWERS = np.random.default_rng(11).uniform(0.0, 6.0, size=(4, N))
OT, WI, RA, SO = (np.asarray(a[:N], dtype=float)
                  for a in weather("winter_cold", START))

# The cell the whole finding rests on: ONE field off the shipped defaults, at
# the config flow's own selector minimum. --perturb puts it back to the default.
MINIMAL_CELL = {"slab_thermal_mass": 5.0 if args.perturb else 0.1}


def parity(params, state, powers=POWERS, ext=None, dt=0.25):
    """max |batch - scalar| over every published trajectory, and n_sub."""
    m = ThermalModel(params)
    n_sub = m._stability_substeps(float(WI[0]), float(RA[0]), dt)
    batch = m.simulate_trajectory_batch(
        state, powers, OT, WI, RA, SO, dt, ext, None, None, None)
    worst = 0.0
    finite = True
    for b in range(powers.shape[0]):
        r, s, u, l = m.simulate_trajectory(
            state, powers[b], OT, WI, RA, SO, dt, ext, None, None, None)
        refs = [(batch["room"][b], r), (batch["slab"][b], s),
                (batch["upper"][b], u), (batch["lower"][b], l),
                (batch["buffer"][b], m.last_buffer_trajectory)]
        if batch["wood"] is not None:
            refs.append((batch["wood"][b], m.last_wood_trajectory))
        for arr, ref in refs:
            if not np.all(np.isfinite(arr)):
                finite = False
                worst = float("inf")
                continue
            worst = max(worst, float(np.max(np.abs(arr - ref))))
    return n_sub, worst, finite


def cell_params(overrides, two_zone=False):
    cfg = house(two_zone=two_zone, dhw=False)
    cfg.update(overrides)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = False
    return p


def make_state(wood=None):
    return ThermalState(
        room_temperature=21.0, slab_temperature=22.0,
        outdoor_temperature=float(OT[0]), upper_floor_temperature=21.0,
        lower_floor_temperature=21.0, dhw_temperature=50.0,
        buffer_tank_temperature=40.0, wood_tank_temperature=wood)


# --- 1. the 49 committed golden configurations: the null the fixtures cover ---
worst_golden = 0.0
for name, spec in golden.SCENARIOS.items():
    built = golden.make(**spec)
    ext = (golden.external_heat_for(N)
           if name in golden.EXTERNAL_HEAT_SCENARIOS else None)
    _, d, _ = parity(built["optimizer"].model.params, built["state"], ext=ext)
    worst_golden = max(worst_golden, d)
print(f"RESULT parity_golden_cells={len(golden.SCENARIOS)} count")
print(f"RESULT parity_max_diff_golden={worst_golden:.3e} degC")

# --- 2. single-zone cells, all inside the config flow's own selector ranges ---
SINGLE_CELLS = {
    # label: (slab_thermal_mass, slab_heat_transfer, house_thermal_mass)
    "minimal_slab0.1": (MINIMAL_CELL["slab_thermal_mass"], 0.8, 10.0),
    "slab0.2_k1.5": (0.2, 1.5, 10.0),
    "slab0.5_k5.0": (0.5, 5.0, 10.0),
    "slab0.3_k5.0": (0.3, 5.0, 10.0),
    "slab0.1_k5.0": (0.1, 5.0, 10.0),
    "house0.5_slab5_k5.0": (5.0, 5.0, 0.5),
    # n_sub == 1 controls
    "ctrl_default": (5.0, 0.8, 10.0),
    "ctrl_slab1.0_k5.0": (1.0, 5.0, 10.0),
    "ctrl_slab0.5_k2.0": (0.5, 2.0, 10.0),
}
stiff, ctrl_worst, minimal_diff = {}, 0.0, 0.0
for label, (c_slab, k_slab, c_room) in SINGLE_CELLS.items():
    p = cell_params({"slab_thermal_mass": c_slab, "slab_heat_transfer": k_slab,
                     "house_thermal_mass": c_room})
    n_sub, d, fin = parity(p, make_state())
    print(f"CELL single {label}: n_sub={n_sub} max_diff={d:.3e} finite={fin}")
    if label == "minimal_slab0.1":
        minimal_diff = d
        print(f"RESULT minimal_cell_nsub={n_sub} count")
    if n_sub > 1:
        stiff[label] = d
    else:
        ctrl_worst = max(ctrl_worst, d)
vals = np.array(list(stiff.values()), dtype=float) if stiff else np.zeros(0)
finite_vals = vals[np.isfinite(vals)]
print(f"RESULT parity_max_diff_single_nsub1={ctrl_worst:.3e} degC")
print(f"RESULT parity_single_stiff_cells={len(stiff)} count")
print("RESULT parity_single_stiff_nonfinite_cells="
      f"{int(np.sum(~np.isfinite(vals)))} count")
print("RESULT parity_max_diff_single_stiff="
      f"{float(np.max(finite_vals)) if finite_vals.size else 0.0:.3e} degC")
print("RESULT parity_min_diff_single_stiff="
      f"{float(np.min(finite_vals)) if finite_vals.size else 0.0:.3e} degC")
loo = np.sort(finite_vals)[:-1] if finite_vals.size > 1 else finite_vals
print("RESULT parity_single_stiff_drop_most_favourable="
      f"{float(np.max(loo)) if loo.size else 0.0:.3e} degC")
print(f"RESULT parity_diff_minimal_cell={minimal_diff:.3e} degC")

# --- 3. two-zone stiff cells: the branch that was always right ---
TWO_CELLS = {
    "upper0.25_inter3.0": {"upper_floor_thermal_mass": 0.25,
                           "inter_zone_heat_transfer": 3.0},
    "lower0.25_k5.0": {"lower_floor_thermal_mass": 0.25,
                       "slab_heat_transfer": 5.0},
    # The configuration tests/features.py's repaired "two-zone stability
    # substeps" cell now runs.
    "features_repaired_cell": {"mixing_valve_mode": "manual",
                               "house_thermal_mass": 0.5,
                               "slab_thermal_mass": 0.5,
                               "slab_heat_transfer": 5.0,
                               "upper_floor_thermal_mass": 0.3,
                               "lower_floor_thermal_mass": 0.5},
    # The configuration it USED to run: `room_thermal_mass` is not a config
    # key, so only three overrides landed and n_sub stayed 1.
    "features_shipped_cell": {"mixing_valve_mode": "manual",
                              "room_thermal_mass": 0.3,
                              "slab_thermal_mass": 0.5,
                              "upper_floor_thermal_mass": 0.3,
                              "lower_floor_thermal_mass": 0.5},
}
two_worst = 0.0
for label, over in TWO_CELLS.items():
    n_sub, d, fin = parity(cell_params(over, two_zone=True), make_state())
    print(f"CELL two-zone {label}: n_sub={n_sub} max_diff={d:.3e} finite={fin}")
    if label == "features_shipped_cell":
        print(f"RESULT features_shipped_substep_cell_nsub={n_sub} count")
    if label == "features_repaired_cell":
        print(f"RESULT features_repaired_substep_cell_nsub={n_sub} count")
    two_worst = max(two_worst, d)
print(f"RESULT parity_max_diff_two_zone_stiff={two_worst:.3e} degC")

# --- 4. the plan consequence, with its null controls -------------------------
def solve(overrides, batch_on, price_profile="winter_typical"):
    built = golden.make(two_zone=False, dhw=False, price_profile=price_profile,
                        config_overrides=overrides)
    orig = optmod._bounds_supported_by_batch
    if not batch_on:
        optmod._bounds_supported_by_batch = lambda bounds: False
    try:
        return built["optimizer"].optimize(
            built["state"], built["prices"], built["outdoor"], built["wind"],
            built["rain"], built["solar"], START)
    finally:
        optmod._bounds_supported_by_batch = orig


def consequence(tag, overrides, price_profile="winter_typical"):
    rb = solve(overrides, True, price_profile)
    rs = solve(overrides, False, price_profile)
    xb = np.asarray(rb.power_schedule)
    xs = np.asarray(rs.power_schedule)
    print(f"CELL solve {tag}: batch status={rb.status} "
          f"objective={rb.objective_value:.4f} cost={rb.predicted_cost:.4f} | "
          f"scalar status={rs.status} objective={rs.objective_value:.4f} "
          f"cost={rs.predicted_cost:.4f}")
    print(f"RESULT plan_cost_batch_{tag}={rb.predicted_cost:.4f} SEK")
    print(f"RESULT plan_cost_scalar_{tag}={rs.predicted_cost:.4f} SEK")
    print("RESULT plan_cost_delta_"
          f"{tag}={rb.predicted_cost - rs.predicted_cost:.4f} SEK")
    print("RESULT plan_schedule_l1_"
          f"{tag}={float(np.sum(np.abs(xb - xs)) * 0.25):.4f} kWh")
    print(f"RESULT plan_energy_batch_{tag}={float(np.sum(xb) * 0.25):.4f} kWh")
    print(f"RESULT plan_energy_scalar_{tag}={float(np.sum(xs) * 0.25):.4f} kWh")
    print("RESULT plan_objective_gap_"
          f"{tag}={rb.objective_value - rs.objective_value:.4f} objective")
    return rb, rs


consequence("minimal", MINIMAL_CELL)
# Null control 1: the shipped defaults, n_sub = 1. Nothing may move.
consequence("default_null", {})
# Null control 2: flat prices at the same stiff cell. A cost gap that is only
# forgone arbitrage collapses here; what survives is the model error itself.
consequence("minimal_flat", MINIMAL_CELL, price_profile="flat")

# --- 5. the gradient the solver actually uses, against scipy's own -----------
captured = {}


def _capture(objective, candidates, bounds, args=(), maxiter=300,
             batch_objective=None, fd_eps=1e-4):
    captured.update(objective=objective, batch=batch_objective, bounds=bounds)
    raise RuntimeError("captured")


def grad_check(overrides, label):
    built = golden.make(two_zone=False, dhw=False, config_overrides=overrides)
    orig = optmod._multi_start_minimize
    optmod._multi_start_minimize = _capture
    try:
        built["optimizer"].optimize(
            built["state"], built["prices"], built["outdoor"], built["wind"],
            built["rain"], built["solar"], START)
    except RuntimeError:
        pass
    finally:
        optmod._multi_start_minimize = orig
    obj, bobj, bounds = captured["objective"], captured["batch"], captured["bounds"]
    lb = np.array([b[0] for b in bounds])
    ub = np.array([b[1] for b in bounds])
    rng = np.random.default_rng(5)
    worst = 0.0
    for _ in range(3):
        x0 = np.clip(rng.uniform(0.2, 5.0, size=lb.size), lb, ub)
        f0 = float(obj(x0))
        g_batch = optmod._batch_fd_gradient(bobj, (), x0, f0, 1e-4, bounds)
        g_scipy = approx_derivative(obj, x0, method="2-point", abs_step=1e-4,
                                    f0=f0, bounds=(lb, ub))
        d = np.abs(g_batch - g_scipy)
        worst = max(worst, float(np.nanmax(d)) if np.any(np.isfinite(d))
                    else float("inf"))
    print(f"RESULT grad_batch_vs_scipy_maxabs_{label}={worst:.3e} "
          "objective_per_kW")


grad_check(MINIMAL_CELL, "minimal")
grad_check({}, "default_null")

# --- 6. reach: who can land in the sub-step regime ---------------------------
# 6a. the guided questionnaire, through the production `presets.derive`.
AREAS = [20.0, 118.0, 216.0, 314.0, 412.0, 510.0,
         608.0, 706.0, 804.0, 902.0, 1000.0]
preset_cells = 0
preset_fire = 0
preset_worst_nsub = 1
for structure, era, foundation, area, emitter in itertools.product(
        presets.STRUCTURES, presets.ERAS, presets.FOUNDATIONS, AREAS,
        presets.EMITTERS):
    cfg = house(two_zone=False, dhw=False)
    cfg.update(presets.derive(presets.BuildingPreset(
        structure=structure, era=era, foundation=foundation,
        heated_area_m2=area, lower_emitter=emitter, upper_emitter=emitter,
        two_zone=False)))
    m = ThermalModel(ThermalParameters.from_config(cfg))
    n_sub = m._stability_substeps(float(WI[0]), float(RA[0]), 0.25)
    preset_cells += 1
    preset_worst_nsub = max(preset_worst_nsub, n_sub)
    if n_sub >= 2:
        preset_fire += 1
print(f"RESULT reach_preset_configs={preset_cells} count")
print(f"RESULT reach_preset_nsub_ge2={preset_fire} count")
print(f"RESULT reach_preset_max_nsub={preset_worst_nsub} count")

# 6b. the expert page's own selector lattice, the grid the round-2 panel put on
# the record: the two slab fields at every value their selectors accept (their
# own steps, endpoints included -- 121 x 51) crossed with the house-mass field
# at its two endpoints and the shipped default (0.5 / 10.0 / 80.0), 18513
# points. The production guard is called on every point; the params object is
# the one `from_config` built for the stock house, and only the three swept
# fields move.
def _axis(rng_, step):
    lo, hi = rng_
    vals = [lo]
    v = lo + step
    while v <= hi + 1e-9:
        vals.append(round(v, 6))
        v += step
    if abs(vals[-1] - hi) > 1e-9:
        vals.append(hi)
    return vals


slab_axis = _axis(RANGE_SLAB_THERMAL_MASS, 0.5)
k_axis = _axis(RANGE_SLAB_HEAT_TRANSFER, 0.1)
grid_model = ThermalModel(cell_params({}))
room_axis = [RANGE_HOUSE_THERMAL_MASS[0],
             grid_model.params.room_thermal_mass,
             RANGE_HOUSE_THERMAL_MASS[1]]
grid_points = 0
grid_fire = 0
two_field_points = 0
two_field_fire = 0
default_room = grid_model.params.room_thermal_mass
for c_slab in slab_axis:
    grid_model.params.slab_thermal_mass = c_slab
    for k_slab in k_axis:
        grid_model.params.slab_heat_transfer = k_slab
        for c_room in room_axis:
            grid_model.params.room_thermal_mass = c_room
            n_sub = grid_model._stability_substeps(
                float(WI[0]), float(RA[0]), 0.25)
            grid_points += 1
            if n_sub >= 2:
                grid_fire += 1
            if c_room == default_room:
                two_field_points += 1
                if n_sub >= 2:
                    two_field_fire += 1
print(f"RESULT reach_selector_grid_points={grid_points} count")
print(f"RESULT reach_selector_grid_nsub_ge2={grid_fire} count")
print(f"RESULT reach_selector_grid_fraction={grid_fire / grid_points:.4f} ratio")
print(f"RESULT reach_two_field_grid_points={two_field_points} count")
print(f"RESULT reach_two_field_grid_nsub_ge2={two_field_fire} count")

proc = time.process_time() - _T_PROC0
thr = time.thread_time() - _T_THR0
print(f"RESULT thread_factor={proc / max(thr, 1e-9):.3f} ratio")
print(f"RESULT load1={os.getloadavg()[0]:.2f} load")
print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap} count")
