"""VERIFIER 3 own harness, D2-04 (independent grid and aggregate).

METRIC (one line): v3_cells_below_unity = count of (outdoor, tank-temp) cells
in MY OWN grid -- outdoor -30..-10 degC at 1 degC, tank 40..70 degC at 5 degC
(the charging envelope a valved install actually sweeps) -- where
marginal_cop(outdoor, "buffer", tank) < 1.0; same for "dhw" at setpoints
45..60; plus v3_inversion_slope = cop(-15) - cop(-25) at tank 55 (negative
means COP falls as weather warms).

EXACT COMMAND (from a tree root):
    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D2/verify03_d2_04.py

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
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalParameters,
)

CPU = Cpu()

# valved install: from_config derives cop_flow_carnot from the mode, exactly
# as every real install gets it (the bare-constructor default is False).
from heatpump_optimizer import const as _const  # noqa: E402

P = ThermalParameters.from_config(
    {_const.CONF_MIXING_VALVE_MODE: "manual"}
)
M = ThermalModel(P)
result("v3_cop_flow_carnot", int(P.cop_flow_carnot), "bool")
result("v3_cop_nominal", P.cop_nominal, "cop")
result("v3_buffer_max_temp", P.buffer_max_temp, "degC")

outdoors = np.arange(-30.0, -9.0, 1.0)      # 21 cells
tanks = np.arange(40.0, 70.0, 5.0)          # 7 cells
below = []
for t in tanks:
    for o in outdoors:
        with CPU:
            c = M.marginal_cop(float(o), "buffer", float(t))
        if c < 1.0:
            below.append((float(o), float(t), c))
result("v3_space_cells", len(outdoors) * len(tanks), "count")
result("v3_space_cells_below_unity", len(below), "count")
if below:
    result("v3_space_warmest_below_unity_outdoor_c", max(b[0] for b in below),
           "degC")
    result("v3_space_coolest_tank_below_unity_c", min(b[1] for b in below),
           "degC")
    result("v3_space_min_cop", min(b[2] for b in below), "cop")

# re-aggregate: drop the tank=70 column entirely (attack on the 51-of-328)
below_no70 = [b for b in below if b[1] < 70.0]
result("v3_space_cells_below_unity_no_70C_col", len(below_no70), "count")
# and the mild-winter subset: only outdoor >= -25
below_mild = [b for b in below if b[0] >= -25.0]
result("v3_space_cells_below_unity_outdoor_ge_-25", len(below_mild), "count")

# DHW at the factory setpoint and neighbours
for setpoint in (45.0, 50.0, 55.0, 60.0):
    n = 0
    worst = 99.0
    warmest = None
    for o in outdoors:
        with CPU:
            c = M.marginal_cop(float(o), "dhw", setpoint)
        if c < 1.0:
            n += 1
            worst = min(worst, c)
            warmest = float(o)
    result(f"v3_dhw_set{int(setpoint)}_cells_below_unity", n, "count")
    result(f"v3_dhw_set{int(setpoint)}_min_cop", worst if n else 1.0, "cop")
    result(f"v3_dhw_set{int(setpoint)}_warmest_below_unity_c",
           warmest if warmest is not None else 99.0, "degC")

# inversion, my own slice: COP at tank 55 for outdoor -30,-25,-20,-15
for o in (-30.0, -25.0, -20.0, -15.0):
    with CPU:
        result(f"v3_cop_tank55_out{int(o)}", M.marginal_cop(o, "buffer", 55.0),
               "cop")
with CPU:
    slope = (M.marginal_cop(-15.0, "buffer", 55.0)
             - M.marginal_cop(-25.0, "buffer", 55.0))
result("v3_cop_slope_-25_to_-15", slope, "cop/K")

# null control: unvalved install must sit at the floor 1.05 everywhere
P0 = ThermalParameters.from_config(
    {_const.CONF_MIXING_VALVE_MODE: "none"}
)
M0 = ThermalModel(P0)
result("v3_null_carnot_off", int(P0.cop_flow_carnot), "bool")
mn = min(M0.marginal_cop(float(o), "buffer", float(t))
         for t in tanks for o in outdoors)
result("v3_null_space_min_cop", mn, "cop")

footer(CPU, "[v]erify03_d2_04")
