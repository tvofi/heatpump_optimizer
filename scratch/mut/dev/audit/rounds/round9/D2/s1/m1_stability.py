#!/usr/bin/env python3
"""D2.M1 Euler stability guard vs the coupled stores (round 9, seat D2-s1).

Metric (one line): over configurations produced by presets.derive (every
questionnaire answer) and over the config-flow range corners, count the
configurations where a zero-input 24 h trajectory (P=0, no gains, no sun,
outdoor 0 degC, stores starting at 21/21/21/21 and slab 25) leaves the
physical envelope [T_out, max initial T] by more than 1e-6 K -- the
maximum principle a passive RC network obeys -- and report the worst
per-substep spectral radius of the production step's Jacobian.

Count key: the temperatures simulate_trajectory returns (the value the
production seam delivers), not any parameter.

Hooks: thermal_model:ThermalModel._stability_substeps (the guard),
thermal_model:ThermalModel.simulate_trajectory / _simulate_step_single /
_simulate_step_two_zone (the dynamics), presets:derive (the configs).

Command (from the export root):
  PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python tools/audit/round9/D2/s1/m1_stability.py
  ... --perturb=ratio1   (EULER_STABILITY_MAX_RATIO 1.5 -> 1.0, the Gershgorin
                          bound for a row-diagonally-dominant RC matrix)
Expected at baseline: grid 69/3936 envelope violations, 50 diverged, worst radius
1.3958; examples 2/2 diverged (2.84e35 K); under
--perturb=ratio1 the counts go to 0 and the worst radius falls to <= 1.
Null control: the shipped defaults (single and two-zone) -> 0 violations.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, box B4 (cloud container, linux).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import copy
import itertools
import sys
import time

import numpy as np

sys.path.insert(0, "custom_components")
from heatpump_optimizer import presets  # noqa: E402
from heatpump_optimizer import thermal_model as tm  # noqa: E402
from heatpump_optimizer.config_flow import (  # noqa: E402
    RANGE_HOUSE_HEAT_LOSS, RANGE_HOUSE_THERMAL_MASS, RANGE_SLAB_HEAT_TRANSFER,
    RANGE_SLAB_THERMAL_MASS, RANGE_ZONE_HEAT_LOSS, RANGE_ZONE_THERMAL_MASS,
)

PERTURB = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--perturb=")), "")
if PERTURB == "ratio1":
    tm.EULER_STABILITY_MAX_RATIO = 1.0

_t0p, _t0t = time.process_time(), time.thread_time()

DT = 0.25
N = 96


def model_for(cfg):
    p = tm.ThermalParameters.from_config(cfg)
    p.internal_gains = 0.0
    p.internal_gains_profile = None
    return tm.ThermalModel(p)


def init_state():
    return tm.ThermalState(room_temperature=21.0, slab_temperature=25.0,
                           upper_floor_temperature=21.0, lower_floor_temperature=21.0,
                           buffer_tank_temperature=21.0)


def envelope_excess(m):
    """Largest excursion outside [T_out, max initial] over the 24 h, in K."""
    s0 = init_state()
    r = m.simulate_trajectory(copy.deepcopy(s0), np.zeros(N), np.zeros(N), dt_hours=DT)
    stores = np.vstack([r[0], r[1], r[2], r[3]])
    if not np.all(np.isfinite(stores)):
        return float("inf")
    hi = 25.0
    return float(max(np.max(stores - hi), np.max(0.0 - stores), 0.0))


def spectral_radius(m):
    """Largest |eig| of the per-substep map, by finite differences of the step."""
    p = m.params
    n_sub = m._stability_substeps(0.0, 0.0, DT)
    h = DT / n_sub
    base = init_state()
    if p.two_zone_enabled:
        fields = ("upper_floor_temperature", "lower_floor_temperature", "slab_temperature")

        def step(s):
            return m._simulate_step_two_zone(s, 0.0, 0.0, 0.0, 0.0, 0.0, h, 0.0)
    else:
        fields = ("room_temperature", "slab_temperature")

        def step(s):
            return m._simulate_step_single(s, 0.0, 0.0, 0.0, 0.0, 0.0, h, 0.0)
    f0 = step(copy.deepcopy(base))
    J = np.zeros((len(fields), len(fields)))
    for j, fj in enumerate(fields):
        s = copy.deepcopy(base)
        setattr(s, fj, getattr(s, fj) + 1.0)
        if not p.two_zone_enabled and fj == "room_temperature":
            s.upper_floor_temperature = s.lower_floor_temperature = s.room_temperature
        f1 = step(s)
        for i, fi in enumerate(fields):
            J[i, j] = getattr(f1, fi) - getattr(f0, fi)
    return float(np.max(np.abs(np.linalg.eigvals(J)))), n_sub


def examples():
    """Two named single-zone points inside every config-flow range."""
    for c in (0.5, 1.0):
        yield (f"ex1z:C={c}/u=0.2/Cs={c}/k=5.0",
               {"house_thermal_mass": c, "house_heat_loss_coefficient": 0.2,
                "slab_thermal_mass": c, "slab_heat_transfer": 5.0, "two_zone_mode": "off"})


def preset_configs():
    areas = (20.0, 40.0, 80.0, 140.0, 250.0, 400.0, 1000.0)
    for st, era, fnd, up, lo, tz, area in itertools.product(
        presets.STRUCTURES, tuple(presets._ERA_LOSS_W_PER_M2K),
        tuple(presets._FOUNDATION_ADJUST), presets.EMITTERS, presets.EMITTERS,
        (False, True), areas,
    ):
        bp = presets.BuildingPreset(structure=st, era=era, foundation=fnd,
                                    heated_area_m2=area, upper_emitter=up,
                                    lower_emitter=lo, upper_area_ratio=0.5, two_zone=tz)
        cfg = dict(presets.derive(bp))
        cfg["two_zone_mode"] = "on" if tz else "off"
        yield f"preset:{st}/{era}/{fnd}/{up}/{lo}/{'2z' if tz else '1z'}/{area:g}", cfg


def _grid(rng, k):
    """k geometric points spanning a config-flow range, ends included."""
    lo, hi = rng
    return tuple(float(x) for x in np.geomspace(lo, hi, k))


def grid_configs():
    """A geometric grid over the config-flow ranges (every point a value the
    options page accepts)."""
    for cm, u, cs, k in itertools.product(_grid(RANGE_HOUSE_THERMAL_MASS, 6),
                                          _grid(RANGE_HOUSE_HEAT_LOSS, 4),
                                          _grid(RANGE_SLAB_THERMAL_MASS, 6),
                                          _grid(RANGE_SLAB_HEAT_TRANSFER, 6)):
        yield (f"grid1z:C={cm:.3g}/u={u:.3g}/Cs={cs:.3g}/k={k:.3g}",
               {"house_thermal_mass": cm, "house_heat_loss_coefficient": u,
                "slab_thermal_mass": cs, "slab_heat_transfer": k, "two_zone_mode": "off"})
    for cu, cl, uu, ul, cs, k, iz in itertools.product(
        _grid(RANGE_ZONE_THERMAL_MASS, 4), _grid(RANGE_ZONE_THERMAL_MASS, 4),
        _grid(RANGE_ZONE_HEAT_LOSS, 2), _grid(RANGE_ZONE_HEAT_LOSS, 2),
        _grid(RANGE_SLAB_THERMAL_MASS, 4), _grid(RANGE_SLAB_HEAT_TRANSFER, 4),
        _grid((0.01, 3.0), 3),
    ):
        yield (f"grid2z:Cu={cu:.3g}/Cl={cl:.3g}/uu={uu:.3g}/ul={ul:.3g}/Cs={cs:.3g}/k={k:.3g}/iz={iz:.3g}",
               {"upper_floor_thermal_mass": cu, "lower_floor_thermal_mass": cl,
                "upper_floor_heat_loss": uu, "lower_floor_heat_loss": ul,
                "slab_thermal_mass": cs, "slab_heat_transfer": k,
                "inter_zone_transfer": iz, "two_zone_mode": "on"})


def sweep(label, gen):
    n = bad = unstable = 0
    worst_rho, worst_name, worst_exc = 0.0, "", 0.0
    div = 0
    for name, cfg in gen:
        m = model_for(cfg)
        n += 1
        exc = envelope_excess(m)
        rho, n_sub = spectral_radius(m)
        if exc > 1e-6:
            bad += 1
        if rho > 1.0 + 1e-12:
            unstable += 1
        if not exc < 100.0:
            div += 1
        if rho > worst_rho:
            worst_rho, worst_name = rho, f"{name} (n_sub={n_sub})"
        worst_exc = max(worst_exc, exc)
    print(f"RESULT {label}_configs={n} count")
    print(f"RESULT {label}_envelope_violations={bad} configs")
    print(f"RESULT {label}_rho_gt_1={unstable} configs")
    print(f"RESULT {label}_diverged_100K={div} configs")
    print(f"RESULT {label}_worst_rho={worst_rho:.4f} ratio")
    print(f"RESULT {label}_worst_excess={worst_exc:.4g} K")
    print(f"# {label} worst radius at {worst_name}")


# Null control: shipped defaults.
sweep("default", [("default1z", {"two_zone_mode": "off"}),
                  ("default2z", {"two_zone_mode": "on"})])
sweep("presets", preset_configs())
sweep("examples", examples())
sweep("grid", grid_configs())
sweep("grid1z", (c for c in grid_configs() if c[0].startswith("grid1z")))
sweep("grid2z", (c for c in grid_configs() if c[0].startswith("grid2z")))

pc, tc = time.process_time() - _t0p, time.thread_time() - _t0t
print(f"RESULT thread_factor={pc / max(tc, 1e-9):.4f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    with open("/proc/vmstat") as fh:
        sw = next(int(ln.split()[1]) for ln in fh if ln.startswith("pswpin"))
except (OSError, StopIteration):
    sw = -1
print(f"RESULT swapins={sw}")
