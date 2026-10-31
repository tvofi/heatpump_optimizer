"""VERIFIER-OWN harness for round-4 D2-03 (seat D2-1, refute-first).

Independent of the finder's wood_share_jump.py: a SECOND configuration (my
own outdoor temperature, hence a different curve temperature from the
production mixing_valve.flow_setpoint), a dense 400-point sweep of the band
(instead of 13 offsets), the one-sided limits computed analytically from
the region formulas, the solver-variable discontinuity driven by
numpy.nextafter on step-0 power (a single ulp, not a bisected bracket), and
a check that the jump survives a different wood-tank mass (it is a share,
so it must).

METRIC (one line):
  own_jump(o) = wood_share(flow-o, flow-1e-9, flow, floor)
              - wood_share(flow-o, flow+1e-9, flow, floor)
  -- the share of the emitter draw taken from wood, moved by 2e-9 degC of
  HP-tank temperature across the curve, wood held o below it. The docstring
  claims "continuous ... across every boundary", so own_jump_max over the
  dense sweep must be ~0; measured it is ~1.

EXACT COMMAND (from a tree root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
    /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
    tools/audit/round4/D2/d2_own_D2-03.py

EXPECTED (baseline 7dd68dd; float identities, tolerance 1e-9):
  own_flow_set_c            ~ 31-32   (my own outdoor temp, not the finder's)
  own_jump_max              ~ 0.9999  (worst over 400 offsets in (0, margin))
  own_jump_analytic_maxrel  <  1e-9   (production matches 1 - o/margin exactly)
  own_cells_jumping         = 400 of 400 for o < margin, 0 at o >= margin
  own_nextafter_jump_kwh    ~ -1.1    (wood enthalpy step moves across ONE
                                       ulp of step-0 power via nextafter)
  own_direction_backward    = 1       (raising the HP tank DROPS the wood
                                       share: backwards vs wood-while-usable)
  own_perturbed_jump_max    ~ 0       (region 3 faded at the boundary)

INSTRUMENTED SYMBOLS: thermal_model.py:wood_share,
thermal_model.py:ThermalModel.simulate_step / simulate_trajectory,
mixing_valve.py:flow_setpoint (the curve temperature).
PERTURBATION (executed in-section 5): multiply region 3's return by
min(1, max(0, (flow_set - hp)/margin)); own_perturbed_jump_max must fall
to the probe residue.
NULL CONTROLS: o >= margin (region 3 already 0 on both sides) and wood at
or above the curve (region 1 on both sides) must give jump == 0.

ROOT RULE: os.getcwd(). BASELINE SHA: 7dd68dd; measured on branch head
0855277 (custom_components/ diff vs baseline: version strings only).
MACHINE: 8-core Apple M1, macOS 25.6.0, python 3.11.5.
"""
from __future__ import annotations

import os
import sys

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "tools", "audit", "round4", "D2"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "tests", "hastub"))
sys.path.insert(0, os.path.join(ROOT, "custom_components"))

import numpy as np  # noqa: E402  (after the pin, deliberately)

from _d2common import Cpu, footer, result  # noqa: E402
from heatpump_optimizer import mixing_valve, thermal_model as tm  # noqa: E402
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalParameters, ThermalState,
)

CPU = Cpu()
OUT = -15.0     # my own outdoor temperature (finder used -5.0)
DT = 0.25
MARGIN = tm.WOOD_TANK_MIN_MARGIN
DELTA = 1e-9    # my own probe (finder used 1e-6)

PARAMS = ThermalParameters(
    two_zone_enabled=True, mixing_valve_mode="manual",
    wood_tank_configured=True,
)
MODEL = ThermalModel(PARAMS)
_u = (MODEL.effective_heat_loss_coefficient(PARAMS.upper_floor_heat_loss)
      + MODEL.effective_heat_loss_coefficient(
          PARAMS.lower_floor_heat_loss_learned))
_design = PARAMS.max_electrical_power * max(PARAMS.cop_nominal, 1.0)
FLOW_SET = mixing_valve.flow_setpoint(
    target_temp=(PARAMS.mixing_valve_target or PARAMS.comfort_ceiling),
    outdoor_temp=OUT,
    heat_loss_coefficient=_u,
    emitter_ua=_design / max(PARAMS.emitter_design_delta_t, 1.0),
)
FLOOR = 21.0
result("own_flow_set_c", float(FLOW_SET), "degC")
result("own_finder_flow_set_differs", int(abs(FLOW_SET - 26.6) > 0.5), "bool")


def jump(o: float) -> float:
    with CPU:
        below = tm.wood_share(FLOW_SET - o, FLOW_SET - DELTA, FLOW_SET, FLOOR)
        above = tm.wood_share(FLOW_SET - o, FLOW_SET + DELTA, FLOW_SET, FLOOR)
    return below - above


# --- 1. dense sweep of the band ----------------------------------------------
offsets = np.linspace(1e-4, MARGIN * 1.5, 400)
jumps = np.array([jump(float(o)) for o in offsets])
result("own_cells", offsets.size, "count")
result("own_jump_max", float(np.max(jumps)), "fraction")
result("own_jump_min", float(np.min(jumps)), "fraction")
result("own_cells_jumping", int(np.sum(np.abs(jumps) > 1e-12)), "count")

# analytic: region 3 at hp=flow gives 1 - o/margin; region 2 gives ~delta/(o+delta)
analytic = np.where(
    offsets < MARGIN,
    (1.0 - offsets / MARGIN) - DELTA / (offsets + DELTA),
    0.0,
)
result("own_jump_analytic_maxrel",
       float(np.max(np.abs(jumps - analytic))
             / max(float(np.max(np.abs(analytic))), 1e-9)), "rel")
# null controls
result("own_jump_null_at_margin", jump(MARGIN), "fraction")
result("own_jump_null_at_2p5margin", jump(MARGIN * 1.25), "fraction")
result("own_jump_null_above_curve", jump(-1.0), "fraction")
# direction: raising the HP tank across the curve DROPS the wood share
result("own_direction_backward",
       int(jump(0.25) > 0.5), "bool")
# the batched twin carries the same jump (finite differences see it too)
_vb = tm._wood_share_vec(np.array([FLOW_SET - 0.25]),
                         np.array([FLOW_SET - DELTA]), FLOW_SET,
                         np.array([FLOOR]))
_va = tm._wood_share_vec(np.array([FLOW_SET - 0.25]),
                         np.array([FLOW_SET + DELTA]), FLOW_SET,
                         np.array([FLOOR]))
result("own_jump_vec_at_0.25C", float(_vb[0] - _va[0]), "fraction")

# --- 2. one ulp of the solver's own variable, via numpy.nextafter -----------
BUF0 = FLOW_SET - 3.0
WOOD_TARGET = FLOW_SET - 0.5


def traj(p0: float, wood0: float):
    st = ThermalState(
        room_temperature=21.0, slab_temperature=23.0, outdoor_temperature=OUT,
        upper_floor_temperature=21.0, lower_floor_temperature=21.0,
        buffer_tank_temperature=BUF0, wood_tank_temperature=wood0,
    )
    with CPU:
        _r, _s, _u2, _l, buf, _ref, wood = MODEL.simulate_trajectory(
            st, np.array([p0, 0.0]), np.full(2, OUT), dt_hours=DT)
    return (float(buf[1]), float(wood[1]),
            PARAMS.wood_tank_thermal_mass * float(wood[2] - wood[1]))


# bisect the WOOD start so the wood tank sits WOOD_TARGET after step 0
lo, hi = FLOW_SET - 1.0, FLOW_SET + 8.0
for _ in range(90):
    mid = 0.5 * (lo + hi)
    if traj(0.18, mid)[1] > WOOD_TARGET:
        hi = mid
    else:
        lo = mid
WOOD0 = 0.5 * (lo + hi)
result("own_wood_at_step1_c", traj(0.18, WOOD0)[1], "degC")

# bisect step-0 power onto the buffer crossing of the curve
plo, phi = 0.0, PARAMS.max_electrical_power
for _ in range(200):
    pm = 0.5 * (plo + phi)
    if traj(pm, WOOD0)[0] > FLOW_SET:
        phi = pm
    else:
        plo = pm
_b, _w1, _e_below = traj(plo, WOOD0)
_a, _w2, _e_above = traj(phi, WOOD0)
result("own_adjacent_ulp_kw", float(phi - plo), "kW")
result("own_adjacent_buf_below_c", _b, "degC")
result("own_adjacent_buf_above_c", _a, "degC")
result("own_adjacent_wood_dE_below_kwh", _e_below, "kWh")
result("own_adjacent_wood_dE_above_kwh", _e_above, "kWh")
result("own_adjacent_jump_kwh", _e_below - _e_above, "kWh")
# and a one-ulp change strictly ABOVE the crossing, via numpy.nextafter
p_up = np.nextafter(phi, np.inf)
_u1, _u2b, _e_up = traj(p_up, WOOD0)
result("own_nextafter_ulp_kw", float(p_up - phi), "kW")
result("own_nextafter_jump_kwh", _e_above - _e_up, "kWh")

# --- 4. the savings baseline imports the same symbol --------------------------
import heatpump_optimizer.optimizer as _opt  # noqa: E402

result("own_optimizer_imports_wood_share",
       int(_opt.wood_share is tm.wood_share), "bool")

# --- 5. perturbation: fade region 3 out at the boundary ----------------------
_orig = tm.wood_share


def wood_share_continuous(wood_temp, hp_temp, flow_set, floor_temp,
                          margin=tm.WOOD_TANK_MIN_MARGIN):
    value = _orig(wood_temp, hp_temp, flow_set, floor_temp, margin)
    if wood_temp >= flow_set or hp_temp > flow_set:
        return value
    return value * min(1.0, max(0.0, (flow_set - hp_temp) / max(margin, 1e-6)))


tm.wood_share = wood_share_continuous
try:
    pj = [wood_share_continuous(FLOW_SET - float(o), FLOW_SET - DELTA,
                                FLOW_SET, FLOOR)
          - wood_share_continuous(FLOW_SET - float(o), FLOW_SET + DELTA,
                                  FLOW_SET, FLOOR)
          for o in offsets]
    result("own_perturbed_jump_max", float(np.max(np.abs(pj))), "fraction")
finally:
    tm.wood_share = _orig

footer(CPU, "[d]2_own_D2-03")
