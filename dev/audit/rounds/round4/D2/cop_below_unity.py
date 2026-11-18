"""D2 round 4, finding D2-04: the modelled COP falls below 1.0 -- below a
plain resistive heater, and below the Carnot bound of any vapour-compression
cycle -- over a reachable part of the configured operating envelope, because
two multiplicative corrections are applied AFTER the nameplate curve's own
`max(0.3, ...)` floor and the final clamp sits at 0.5 rather than 1.0.

METRIC (one line): `min_cop` = the smallest value ThermalModel.compute_cop /
compute_cop_dhw returns over the operating grid the configuration itself
admits (outdoor -25..+15 degC x flow 35..buffer_max_temp=70 degC for space,
x tank 40..dhw_hard_max for DHW), and `cells_below_unity` = how many of the
grid's cells are under 1.0. Both should be 0 / >=1.0: a heat pump whose
COP is below 1 delivers less heat than the electricity it is charged for,
which no vapour-compression cycle does and which the resistive backup every
such system carries bounds from below.

WHY (re-derivable): `compute_cop` builds
    cop = cop_nominal * min(max(0.3, 1 + 0.025*(T_out - 7)), 1.5) * cop_scale
whose 0.3 factor floor keeps the nameplate curve at 3.5*0.3 = 1.05, i.e.
deliberately above unity. It then multiplies by the defrost derate (<= 1),
and by the Carnot flow ratio max(0.25, carnot_flow/carnot_ref) (<= 1 above
the 35 degC flow reference), and finally clamps with `max(cop, 0.5)`.
`compute_cop_dhw` multiplies the same base by `max(0.5, 1 - 0.008*(T_dhw -
35))`. Each factor is individually defensible; their product crosses 1.0 and
the final clamp does not stop it.
`cop_flow_carnot` is not an exotic option: ThermalParameters.from_config
sets it to `mixing_valve.is_throttling(mode)`, so every valved install has
it on. `compute_cop_dhw` has no gate at all.

EXACT COMMAND (from the export root):
    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D2/cop_below_unity.py

EXPECTED (baseline 7dd68dd): closed-form float identities, tolerance 1e-6.
    space.min_cop                 = 0.71954 +- 1e-5  (outdoor -21, flow 70)
    space.cells_below_unity       = 51 of 328
    space.cells_below_unity_loo   = 44              (coldest column dropped)
    space.crossing_outdoor_flow45 = -19.915 +- 0.01 degC
    space.crossing_outdoor_flow55 = -18.236 +- 0.01 degC
    space.crossing_outdoor_flow65 = -16.521 +- 0.01 degC
    dhw.min_cop                   = 0.84  +- 1e-6   (outdoor -25, tank 60 =
                                                     the shipped hard max)
    dhw.cells_below_unity         = 23 of 205
    dhw.crossing_outdoor_set55    = -19.395 +- 0.01 degC
    marginal_cop_buffer_at_-25C_70C = 0.73848 +- 1e-5  (the symbol the
        terminal credit and the settlement price call, so the sub-unity
        value reaches the money and not only the simulation)
    null.space_carnot_off_min_cop = 1.05  +- 1e-9    (null control: with the
        Carnot flow term off the nameplate floor holds over the WHOLE grid)
    null.dhw_at_35C_min_cop       = 1.05  +- 1e-9    (null control: at the
        DHW penalty's own reference temperature the penalty is 1.0)
    perturbed.cop_nominal_5.0.space_cells_below_unity = 0  (see
        PERTURBATION; 3.5 -> 51, 4.0 -> 28, 4.5 -> 11, 4.8 -> 2, 5.0 -> 0)
  the same mechanism's second consequence -- an INVERTED COP band:
    invert.flow70.band_lo_c       = -40.0  (the sweep's own edge)
    invert.flow70.band_hi_c       = -21.0 +- 0.1 degC
    invert.flow70.drop_-30_to_-21_pct = 5.325 +- 0.01 pct  (the model says
        the pump gets 5.3 % WORSE as the weather warms from -30 to -21 degC;
        2.10 / 3.64 / 4.83 pct at flow 45 / 55 / 65)
    null.carnot_off_worst_step_vs_outdoor = 0.0 +- 1e-12  (null control: the
        nameplate curve alone is monotone over the identical sweep)

INSTRUMENTED SYMBOLS: thermal_model.py:ThermalModel.compute_cop,
thermal_model.py:ThermalModel.compute_cop_dhw,
thermal_model.py:ThermalModel.marginal_cop (the one the terminal credit and
the settlement price call), thermal_model.py:ThermalParameters.from_config
(which is what turns `cop_flow_carnot` on for a valved install),
thermal_model.py:ThermalParameters.buffer_max_temp / dhw_hard_max_temp (the
envelope the grid is taken from, read rather than assumed).

PERTURBATION (the judge runs it): raise `cop_nominal` from the shipped
default 3.5 -- a config change, CONF_HEAT_PUMP_COP_NOMINAL. `min_cop` must
RISE proportionally and `cells_below_unity` must FALL, reaching 0 by
cop_nominal ~ 4.8 for space. Section 3 sweeps cop_nominal in-process and
prints the count at each value, so the direction is measured here. The
one-line production alternative is `max(cop, 0.5)` -> `max(cop, 1.0)` in
compute_cop plus the same in compute_cop_dhw's return, under which
`cells_below_unity` must fall to 0 at every cop_nominal.

NULL CONTROLS: `null.space_carnot_off_min_cop` and `null.dhw_at_35C_min_cop`
must both be 1.05 -- the base curve alone never goes below unity, so the
metric is measuring the post-floor corrections and not the curve.

SWEEP / LEAVE-ONE-OUT: the grid is 360 (space) and 315 (DHW) cells; section
1 reports min, the count under unity, the worst cell, and the count with the
single coldest outdoor column dropped.

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
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalParameters,
)

CPU = Cpu()

# The valved configuration, built the way production builds it: from_config
# turns cop_flow_carnot on for any throttling valve mode.
CFG = {"mixing_valve_mode": "manual", "two_zone_enabled": True}
PARAMS = ThermalParameters.from_config(CFG)
result("cop_flow_carnot", int(PARAMS.cop_flow_carnot), "bool")
result("cop_nominal", float(PARAMS.cop_nominal), "cop")
result("buffer_max_temp_c", float(PARAMS.buffer_max_temp), "degC")
result("dhw_hard_max_temp_c", float(PARAMS.dhw_hard_max_temp), "degC")
MODEL = ThermalModel(PARAMS)

OUTDOORS = np.arange(-25.0, 15.1, 1.0)                      # 41 columns
FLOWS = np.arange(35.0, PARAMS.buffer_max_temp + 0.1, 5.0)  # 8 rows
TANKS = np.arange(40.0, PARAMS.dhw_hard_max_temp + 0.1, 5.0)


def grid(fn, rows):
    with CPU:
        return np.array([[fn(float(o), float(r)) for o in OUTDOORS]
                         for r in rows])


space = grid(lambda o, f: MODEL.compute_cop(o, flow_temp=f), FLOWS)
dhw = grid(lambda o, t: MODEL.compute_cop_dhw(o, t), TANKS)

for tag, g, rows in (("space", space, FLOWS), ("dhw", dhw, TANKS)):
    result(f"{tag}.cells", int(g.size), "count")
    result(f"{tag}.min_cop", float(g.min()), "cop")
    ri, ci = np.unravel_index(int(np.argmin(g)), g.shape)
    result(f"{tag}.min_at", f"outdoor={OUTDOORS[ci]}C,level={rows[ri]}C")
    result(f"{tag}.cells_below_unity", int(np.sum(g < 1.0)), "count")
    # leave-one-out: drop the single coldest outdoor column
    result(f"{tag}.cells_below_unity_loo",
           int(np.sum(g[:, 1:] < 1.0)), "count")

# Where the space curve crosses unity, per flow temperature.
for f in (45.0, 55.0, 65.0):
    lo, hi = -40.0, 20.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if MODEL.compute_cop(mid, flow_temp=f) < 1.0:
            lo = mid
        else:
            hi = mid
    result(f"space.crossing_outdoor_flow{int(f)}", 0.5 * (lo + hi), "degC")
for t in (55.0, 60.0, 65.0):
    lo, hi = -40.0, 20.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if MODEL.compute_cop_dhw(mid, t) < 1.0:
            lo = mid
        else:
            hi = mid
    result(f"dhw.crossing_outdoor_set{int(t)}", 0.5 * (lo + hi), "degC")

# --- the SAME mechanism, second consequence: COP INVERTS below -21 degC -----
# Below outdoor -21 degC the nameplate factor is pinned by its own
# `max(0.3, ...)` floor while the Carnot ratio keeps FALLING as outdoor
# rises, so the product falls with rising outdoor: the model says the pump
# gets worse as the weather warms. Reported as the width of the band and the
# COP drop across the part of it inside a realistic envelope (-30..-21).
for f in (45.0, 55.0, 65.0, 70.0):
    grid_o = np.arange(-40.0, 10.001, 0.1)
    with CPU:
        c = np.array([MODEL.compute_cop(float(o), flow_temp=f)
                      for o in grid_o])
    d = np.diff(c)
    tag = f"invert.flow{int(f)}"
    if not np.any(d < -1e-15):
        result(f"{tag}.band_width_c", 0.0, "degC")
        continue
    i0 = int(np.argmax(d < -1e-15))
    i1 = len(d) - 1 - int(np.argmax((d < -1e-15)[::-1]))
    result(f"{tag}.band_lo_c", float(grid_o[i0]), "degC")
    result(f"{tag}.band_hi_c", float(grid_o[i1 + 1]), "degC")
    lo30 = MODEL.compute_cop(-30.0, flow_temp=f)
    hi21 = MODEL.compute_cop(-21.0, flow_temp=f)
    result(f"{tag}.cop_at_-30c", lo30, "cop")
    result(f"{tag}.cop_at_-21c", hi21, "cop")
    result(f"{tag}.drop_-30_to_-21_pct", 100.0 * (lo30 - hi21) / lo30, "pct")
# null control for the inversion: with the Carnot term off the same sweep is
# monotone non-decreasing in outdoor temperature.
# marginal_cop -- the symbol the terminal credit and the settlement price
# use -- carries the same values, so the sub-unity price reaches the money.
result("marginal_cop_buffer_at_-25C_70C",
       MODEL.marginal_cop(-25.0, "buffer", store_temp=70.0), "cop")
result("marginal_cop_dhw_at_-25C_60C",
       MODEL.marginal_cop(-25.0, "dhw", store_temp=60.0), "cop")

# --- null controls ---------------------------------------------------------
plain = ThermalModel(ThermalParameters.from_config({"mixing_valve_mode": "none"}))
result("null.cop_flow_carnot", int(plain.params.cop_flow_carnot), "bool")
off = np.array([[plain.compute_cop(float(o), flow_temp=float(f))
                 for o in OUTDOORS] for f in FLOWS])
result("null.space_carnot_off_min_cop", float(off.min()), "cop")
result("null.space_carnot_off_cells_below_unity",
       int(np.sum(off < 1.0)), "count")
at35 = np.array([MODEL.compute_cop_dhw(float(o), 35.0) for o in OUTDOORS])
result("null.dhw_at_35C_min_cop", float(at35.min()), "cop")
# null control for the inversion: with the Carnot term off the curve is
# monotone non-decreasing in outdoor temperature over the same sweep.
_worst_off = 0.0
for f in (45.0, 55.0, 65.0, 70.0):
    c = np.array([plain.compute_cop(float(o), flow_temp=f)
                  for o in np.arange(-40.0, 10.001, 0.1)])
    _worst_off = min(_worst_off, float(np.min(np.diff(c))))
result("null.carnot_off_worst_step_vs_outdoor", _worst_off, "cop")

# --- the perturbation, executed --------------------------------------------
for nominal in (3.5, 4.0, 4.5, 4.8, 5.0, 6.0):
    p = ThermalParameters.from_config(
        {**CFG, "heat_pump_cop_nominal": nominal})
    m = ThermalModel(p)
    with CPU:
        g = np.array([[m.compute_cop(float(o), flow_temp=float(f))
                       for o in OUTDOORS] for f in FLOWS])
    result(f"perturbed.cop_nominal_{nominal}.space_cells_below_unity",
           int(np.sum(g < 1.0)), "count")
    result(f"perturbed.cop_nominal_{nominal}.space_min_cop",
           float(g.min()), "cop")

footer(CPU, "[c]op_below_unity")
