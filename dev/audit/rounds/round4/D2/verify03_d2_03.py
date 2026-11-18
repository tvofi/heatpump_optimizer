"""VERIFIER 3 own harness, D2-03 (independent metric and probe).

METRIC (one line): v3_jump(d) = wood_share(w, flow-eps, flow, floor)
                              - wood_share(w, flow+eps, flow, floor)
with MY OWN probe eps=1e-9 degC, compared against the closed form
1 - d/margin (region 3's limit minus region 2's limit 0); and
v3_fd_spike_ratio = |finite-difference d(wood enthalpy)/dp| at the crossing
with the production FD step (1e-4 kW) divided by the same FD slope sampled
0.1 kW away from the crossing — the objective's own gradient, not a
diagnostic.

EXACT COMMAND (from a tree root):
    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D2/verify03_d2_03.py

ROOT RULE: os.getcwd(). BASELINE SHA of the finding: 7dd68dd.
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

import numpy as np  # noqa: E402

from _d2common import Cpu, footer, result  # noqa: E402
from heatpump_optimizer import mixing_valve, thermal_model as tm  # noqa: E402
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalParameters, ThermalState,
)

CPU = Cpu()
EPS = 1e-9
OUT = -5.0
DT = 0.25
MARGIN = float(tm.WOOD_TANK_MIN_MARGIN)

PARAMS = ThermalParameters(
    two_zone_enabled=True, mixing_valve_mode="manual",
    wood_tank_configured=True,
)
MODEL = ThermalModel(PARAMS)
_u_up = MODEL.effective_heat_loss_coefficient(PARAMS.upper_floor_heat_loss)
_u_lo = MODEL.effective_heat_loss_coefficient(PARAMS.lower_floor_heat_loss_learned)
_design = PARAMS.max_electrical_power * max(PARAMS.cop_nominal, 1.0)
FLOW_SET = mixing_valve.flow_setpoint(
    target_temp=(PARAMS.mixing_valve_target or PARAMS.comfort_ceiling),
    outdoor_temp=OUT,
    heat_loss_coefficient=_u_up + _u_lo,
    emitter_ua=_design / max(PARAMS.emitter_design_delta_t, 1.0),
)
FLOOR = 21.0

# --- 1. my own probe vs the closed form -------------------------------------
worst_dev = 0.0
for d in (0.01, 0.1, 0.5, 1.0, 1.5, 1.9):
    with CPU:
        below = tm.wood_share(FLOW_SET - d, FLOW_SET - EPS, FLOW_SET, FLOOR)
        above = tm.wood_share(FLOW_SET - d, FLOW_SET + EPS, FLOW_SET, FLOOR)
    measured = below - above
    closed = 1.0 - d / MARGIN
    worst_dev = max(worst_dev, abs(measured - closed))
    result(f"v3_jump_d{d}", measured, "fraction")
    result(f"v3_closed_d{d}", closed, "fraction")
result("v3_jump_vs_closed_worst_dev", worst_dev, "fraction")

# nulls, my own probe
result("v3_jump_null_at_margin",
       tm.wood_share(FLOW_SET - MARGIN, FLOW_SET - EPS, FLOW_SET, FLOOR)
       - tm.wood_share(FLOW_SET - MARGIN, FLOW_SET + EPS, FLOW_SET, FLOOR),
       "fraction")
result("v3_jump_null_above_curve",
       tm.wood_share(FLOW_SET + 1.0, FLOW_SET - EPS, FLOW_SET, FLOOR)
       - tm.wood_share(FLOW_SET + 1.0, FLOW_SET + EPS, FLOW_SET, FLOOR),
       "fraction")

# --- 2. the objective's own FD gradient at the cliff -------------------------
BUF0 = FLOW_SET - 3.0


def traj_wood_de(p0: float, wood0: float) -> float:
    st = ThermalState(
        room_temperature=21.0, slab_temperature=23.0, outdoor_temperature=OUT,
        upper_floor_temperature=21.0, lower_floor_temperature=21.0,
        buffer_tank_temperature=BUF0, wood_tank_temperature=wood0,
    )
    with CPU:
        _r, _s, _u, _l, buf, _ref, wood = MODEL.simulate_trajectory(
            st, np.array([p0, 0.0]), np.full(2, OUT), dt_hours=DT)
    return PARAMS.wood_tank_thermal_mass * float(wood[2] - wood[1])


# bisect wood0 so step-1 wood sits 1.0 below the curve
lo, hi = FLOW_SET - 1.0, FLOW_SET + 8.0
for _ in range(80):
    mid = 0.5 * (lo + hi)
    st = ThermalState(
        room_temperature=21.0, slab_temperature=23.0, outdoor_temperature=OUT,
        upper_floor_temperature=21.0, lower_floor_temperature=21.0,
        buffer_tank_temperature=BUF0, wood_tank_temperature=mid,
    )
    _r, _s, _u, _l, _b, _f, w1 = MODEL.simulate_trajectory(
        st, np.array([0.18, 0.0]), np.full(2, OUT), dt_hours=DT)
    if float(w1[1]) > FLOW_SET - 1.0:
        hi = mid
    else:
        lo = mid
WOOD0 = 0.5 * (lo + hi)

# bisect the crossing power
plo, phi = 0.0, PARAMS.max_electrical_power
for _ in range(200):
    pm = 0.5 * (plo + phi)
    st = ThermalState(
        room_temperature=21.0, slab_temperature=23.0, outdoor_temperature=OUT,
        upper_floor_temperature=21.0, lower_floor_temperature=21.0,
        buffer_tank_temperature=BUF0, wood_tank_temperature=WOOD0,
    )
    _r, _s, _u, _l, buf, _f, _w = MODEL.simulate_trajectory(
        st, np.array([pm, 0.0]), np.full(2, OUT), dt_hours=DT)
    if float(buf[1]) > FLOW_SET:
        phi = pm
    else:
        plo = pm
PCROSS = 0.5 * (plo + phi)

H = 1e-4  # the production FD abs_step (L-BFGS-B 2-point, per tariff.py:489)
fd_at_cliff = (traj_wood_de(PCROSS + H, WOOD0)
               - traj_wood_de(PCROSS - H, WOOD0)) / (2.0 * H)
fd_away = (traj_wood_de(PCROSS + 0.1 + H, WOOD0)
           - traj_wood_de(PCROSS + 0.1 - H, WOOD0)) / (2.0 * H)
fd_below = (traj_wood_de(PCROSS - 0.1 + H, WOOD0)
            - traj_wood_de(PCROSS - 0.1 - H, WOOD0)) / (2.0 * H)
result("v3_pcross_kw", PCROSS, "kW")
result("v3_fd_slope_at_cliff_kwh_per_kwh", fd_at_cliff, "kWh/kWh")
result("v3_fd_slope_0p1_above", fd_away, "kWh/kWh")
result("v3_fd_slope_0p1_below", fd_below, "kWh/kWh")
result("v3_fd_spike_ratio_vs_above", abs(fd_at_cliff / fd_away)
       if fd_away != 0 else float("inf"), "ratio")
result("v3_fd_jump_kwh", traj_wood_de(PCROSS - H, WOOD0)
       - traj_wood_de(PCROSS + H, WOOD0), "kWh")

footer(CPU, "[v]erify03_d2_03")
