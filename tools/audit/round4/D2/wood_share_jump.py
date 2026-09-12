"""D2 round 4, finding D2-03: the 4-way valve law `thermal_model.wood_share`
is discontinuous at `hp_temp == flow_set`, where its own docstring says it is
continuous, and the jump reaches ~1.0 of the emitter draw.

METRIC (one line): `share_jump` = wood_share(w, flow-1e-6, flow, floor)
                                 - wood_share(w, flow+1e-6, flow, floor)
-- the change in the fraction of the emitter draw taken from the wood tank
caused by moving the HEAT-PUMP tank by 2e-6 degC across the weather-curve
temperature, with the wood tank held fixed. The docstring's contract is
"Three regions, continuous in w * Q_draw across every boundary", i.e.
share_jump == 0 to float tolerance (1e-12).

Two further metrics put the jump in energy, through production symbols:
`wood_energy_jump_kwh`  -- the difference in the wood tank's one-step
    enthalpy change through ThermalModel.simulate_step on the two-tank
    topology, for the same 2e-6 degC move of the HP tank.
`traj_wood_jump_kwh`    -- the same difference when the HP tank is moved
    across flow_set NOT by hand but by a 1e-6 kW change in the SOLVER'S
    OWN DECISION VARIABLE (step-0 electrical power) through
    ThermalModel.simulate_trajectory. This is what makes the objective
    discontinuous in the variable L-BFGS-B differentiates.

WHY (re-derivable): with hp_temp just above flow_set the law is in region 2
and f_w = (hp_temp - flow_set)/(hp_temp - wood_temp) -> 0. With hp_temp just
below it the law is in region 3 and returns
max(wood-hp, wood-flow+margin)/margin, which at hp == flow tends to
1 - (flow_set - wood_temp)/margin -- 0.875 at wood_temp = flow_set - 0.25
with margin = WOOD_TANK_MIN_MARGIN = 2.0 degC, not 0. Region 3 was written
for "both at or below the curve, switch to the hotter source" and does not
vanish at the region-2 boundary.

DIRECTION: the jump is DOWNWARD in wood use as the HP tank warms -- exactly
backwards against the documented priority law ("wood-while-usable ... not
hotter-tank-first"): the wood tank is abandoned because the heat pump's own
tank got hotter.

EXACT COMMAND (from the export root):
    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D2/wood_share_jump.py

EXPECTED (baseline 7dd68dd): pure float identities, tolerance 1e-9 absolute
on shares and 1e-9 kWh on energies.
    share_jump_worst          = 0.9995 +- 1e-9   (wood_temp = flow_set-0.001)
    share_jump_at_0.25C       = 0.875  +- 1e-9
    share_jump_null_at_2C     = 0.0    +- 1e-6   (null control: a full margin
                                                  below the curve region 3
                                                  already returns 0)
    share_jump_null_above     = 0.0    exactly   (null control: wood at or
                                                  above the curve is region 1
                                                  on both sides)
    share_jump_vec_at_0.25C   = 0.875  +- 1e-9   (the batched twin agrees)
    wood_energy_jump_kwh      = -0.64167 +- 1e-4 (15-min step, 500 L wood tank)
    traj_power_gap_kw         = 2.78e-17 kW      (one float ulp of step-0
                                                  electrical power)
    traj_wood_jump_kwh        = -1.1101 +- 1e-3  (the wood tank's step-1
                                                  enthalpy change moves by
                                                  1.11 kWh across one ulp of
                                                  the solver's own variable)
    perturbed_share_jump_worst = 0.000998 +- 1e-5 (see PERTURBATION;\n                                                  the residue is the\n                                                  2e-6 degC probe itself)\n    perturbed_wood_energy_jump_kwh = 7.3e-07 +- 1e-6

INSTRUMENTED SYMBOLS: thermal_model.py:wood_share (the law),
thermal_model.py:_wood_share_vec (its batched twin, checked to carry the
same jump), thermal_model.py:ThermalModel._simulate_step_two_zone via
ThermalModel.simulate_step (the energy), ThermalModel.simulate_trajectory
(the decision variable), ThermalParameters.topology_layout /
two_tank_modelled (the gate: TOPOLOGY_TWO_TANK_4WAY).

PERTURBATION (the judge runs it): one line in `wood_share`'s region 3 --
multiply its returned value by `min(1.0, max(0.0, (flow_set - hp_temp) /
max(margin, 1e-6)))`, which is 1 away from the boundary and 0 at it. Under
it `share_jump_worst` must FALL to 0 and `wood_energy_jump_kwh` to 0.
Section 4 executes that perturbation in-process and prints it.

NULL CONTROLS: `share_jump_null_at_2C` (wood a full margin below the curve)
and `share_jump_null_above` (wood at or above the curve) must both be
exactly 0 -- the jump has to vanish where the two regions genuinely meet, or
the metric is measuring the sweep and not the discontinuity.

SWEEP: section 1 sweeps wood_temp across the whole (flow_set - margin,
flow_set] band and reports where the jump is worst.

ROOT RULE: os.getcwd(); resolves nothing from __file__.
BASELINE SHA: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697 (export, no .git).
MACHINE: 8-core Apple M1, 8 GB, macOS 25.6.0, python 3.11.5, numpy 2.4.6.
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
DELTA = 1e-6      # degC the HP tank is moved across the curve
OUT = -5.0        # outdoor temperature
DT = 0.25
MARGIN = tm.WOOD_TANK_MIN_MARGIN

PARAMS = ThermalParameters(
    two_zone_enabled=True, mixing_valve_mode="manual",
    wood_tank_configured=True,
)
MODEL = ThermalModel(PARAMS)
result("topology_layout", PARAMS.topology_layout)
result("two_tank_modelled", int(PARAMS.two_tank_modelled), "bool")

# The curve temperature this configuration puts on the emitters, taken from
# the production symbol the step itself calls, not re-derived.
_u_up = MODEL.effective_heat_loss_coefficient(PARAMS.upper_floor_heat_loss)
_u_lo = MODEL.effective_heat_loss_coefficient(
    PARAMS.lower_floor_heat_loss_learned)
_design = PARAMS.max_electrical_power * max(PARAMS.cop_nominal, 1.0)
_ddt = max(PARAMS.emitter_design_delta_t, 1.0)
FLOW_SET = mixing_valve.flow_setpoint(
    target_temp=(PARAMS.mixing_valve_target or PARAMS.comfort_ceiling),
    outdoor_temp=OUT,
    heat_loss_coefficient=_u_up + _u_lo,
    emitter_ua=_design / _ddt,
)
result("flow_set_c", float(FLOW_SET), "degC")
result("wood_tank_min_margin_c", float(MARGIN), "degC")

FLOOR = 21.0      # the coldest zone the tanks feed, as the step computes it


def share_jump(wood_temp: float) -> float:
    with CPU:
        below = tm.wood_share(wood_temp, FLOW_SET - DELTA, FLOW_SET, FLOOR)
        above = tm.wood_share(wood_temp, FLOW_SET + DELTA, FLOW_SET, FLOOR)
    return below - above


# --- 1. sweep the band and find the worst point ----------------------------
offsets = [0.001, 0.05, 0.1, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75,
           1.999, 2.0, 2.5]
jumps = []
for off in offsets:
    j = share_jump(FLOW_SET - off)
    jumps.append(j)
    result(f"share_jump_at_{off}C_below_curve", j, "fraction")
worst_i = int(np.argmax(np.abs(jumps)))
result("share_jump_worst", float(jumps[worst_i]), "fraction")
result("share_jump_worst_at_offset_c", offsets[worst_i], "degC")
result("share_jump_null_at_2C", share_jump(FLOW_SET - MARGIN), "fraction")
result("share_jump_null_above", share_jump(FLOW_SET + 5.0), "fraction")
result("cells", len(offsets), "count")
result("cells_nonzero", int(np.sum(np.abs(np.array(jumps)) > 1e-12)), "count")
_j = np.abs(np.array(jumps))
result("loo_mean_worst_dropped",
       float(np.delete(_j, int(np.argmax(_j))).mean()), "fraction")

# the batched twin carries the same jump
_v_below = tm._wood_share_vec(
    np.array([FLOW_SET - 0.25]), np.array([FLOW_SET - DELTA]), FLOW_SET,
    np.array([FLOOR]))
_v_above = tm._wood_share_vec(
    np.array([FLOW_SET - 0.25]), np.array([FLOW_SET + DELTA]), FLOW_SET,
    np.array([FLOOR]))
result("share_jump_vec_at_0.25C", float(_v_below[0] - _v_above[0]), "fraction")


# --- 2. the jump in energy, through the production step --------------------
def one_step_wood_energy(hp_temp: float, wood_temp: float) -> float:
    st = ThermalState(
        room_temperature=21.0, slab_temperature=23.0, outdoor_temperature=OUT,
        upper_floor_temperature=21.0, lower_floor_temperature=21.0,
        buffer_tank_temperature=hp_temp, wood_tank_temperature=wood_temp,
    )
    with CPU:
        nxt = MODEL.simulate_step(st, 0.0, OUT, dt_hours=DT)
    return PARAMS.wood_tank_thermal_mass * (
        nxt.wood_tank_temperature - wood_temp)


W = FLOW_SET - 1.0
_e_below = one_step_wood_energy(FLOW_SET - DELTA, W)
_e_above = one_step_wood_energy(FLOW_SET + DELTA, W)
result("wood_dE_below_kwh", _e_below, "kWh")
result("wood_dE_above_kwh", _e_above, "kWh")
result("wood_energy_jump_kwh", _e_below - _e_above, "kWh")
result("wood_energy_jump_frac_of_discharge",
       abs(_e_below - _e_above) / max(abs(_e_below), 1e-12), "fraction")

# --- 3. driven by the solver's own decision variable ------------------------
# Two steps. Step 0's electrical power sets the HP tank temperature that
# step 1's valve law reads, so a change in the SOLVER'S variable moves
# hp_temp across flow_set. The wood tank's start temperature is bisected
# first so that after step 0 it sits 0.25 degC below the curve -- inside the
# band where the law jumps -- and then step-0 power is bisected onto the
# crossing. Both bisections drive ThermalModel.simulate_trajectory only.
BUF0 = FLOW_SET - 3.0
WOOD1_TARGET = FLOW_SET - 0.25


def traj(p0: float, wood0: float) -> tuple[float, float, float]:
    st = ThermalState(
        room_temperature=21.0, slab_temperature=23.0, outdoor_temperature=OUT,
        upper_floor_temperature=21.0, lower_floor_temperature=21.0,
        buffer_tank_temperature=BUF0, wood_tank_temperature=wood0,
    )
    with CPU:
        _r, _s, _u, _l, buf, _ref, wood = MODEL.simulate_trajectory(
            st, np.array([p0, 0.0]), np.full(2, OUT), dt_hours=DT)
    return (float(buf[1]), float(wood[1]),
            PARAMS.wood_tank_thermal_mass * float(wood[2] - wood[1]))


lo, hi = FLOW_SET - 1.0, FLOW_SET + 8.0
for _ in range(80):
    mid = 0.5 * (lo + hi)
    if traj(0.18, mid)[1] > WOOD1_TARGET:
        hi = mid
    else:
        lo = mid
WOOD0 = 0.5 * (lo + hi)
result("traj_wood_start_c", WOOD0, "degC")
result("traj_wood_at_step1_c", traj(0.18, WOOD0)[1], "degC")

plo, phi = 0.0, PARAMS.max_electrical_power
for _ in range(200):
    pm = 0.5 * (plo + phi)
    if traj(pm, WOOD0)[0] > FLOW_SET:
        phi = pm
    else:
        plo = pm
_b_buf, _b_w1, _b_e = traj(plo, WOOD0)
_a_buf, _a_w1, _a_e = traj(phi, WOOD0)
result("traj_crossing_power_kw", 0.5 * (plo + phi), "kW")
result("traj_power_gap_kw", phi - plo, "kW")
result("traj_buf_below_c", _b_buf, "degC")
result("traj_buf_above_c", _a_buf, "degC")
result("traj_wood_dE_below_kwh", _b_e, "kWh")
result("traj_wood_dE_above_kwh", _a_e, "kWh")
result("traj_wood_jump_kwh", _b_e - _a_e, "kWh")

# --- 4. the perturbation, executed ------------------------------------------
_orig_share = tm.wood_share


def wood_share_continuous(wood_temp, hp_temp, flow_set, floor_temp,
                          margin=tm.WOOD_TANK_MIN_MARGIN):
    value = _orig_share(wood_temp, hp_temp, flow_set, floor_temp, margin)
    if wood_temp >= flow_set or hp_temp > flow_set:
        return value
    # region 3 only: fade it out as the HP tank reaches the curve.
    return value * min(1.0, max(0.0, (flow_set - hp_temp) / max(margin, 1e-6)))


tm.wood_share = wood_share_continuous
try:
    pj = [wood_share_continuous(FLOW_SET - o, FLOW_SET - DELTA, FLOW_SET,
                                FLOOR)
          - wood_share_continuous(FLOW_SET - o, FLOW_SET + DELTA, FLOW_SET,
                                  FLOOR)
          for o in offsets]
    result("perturbed_share_jump_worst", float(np.max(np.abs(pj))), "fraction")
    result("perturbed_wood_energy_jump_kwh",
           one_step_wood_energy(FLOW_SET - DELTA, W)
           - one_step_wood_energy(FLOW_SET + DELTA, W), "kWh")
finally:
    tm.wood_share = _orig_share

footer(CPU, "[w]ood_share_jump")
