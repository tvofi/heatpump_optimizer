"""VERIFIER-OWN harness for round-4 D2-04 (seat D2-1, refute-first).

Independent of the finder's cop_below_unity.py: (a) it re-derives the COP
value from MY OWN closed-form reading of compute_cop's source and checks
production against it at 2000 RANDOM points in the envelope (the finder's
grid was a regular lattice -- this attacks grid artefacts); (b) it re-grids
at 0.5 degC resolution; (c) it measures the inversion band with a sign
count of the derivative rather than first/last indices; (d) it drives the
production symbols the money path calls (marginal_cop) at the temperatures
the optimizer's own _buffer_charge_ceiling bisection feeds it.

METRIC (one line):
  own_min_cop_random = min over 2000 uniform-random (outdoor, flow) points
  in [-25,15] x [35,buffer_max] of ThermalModel.compute_cop (valved config,
  cop_flow_carnot on) -- a heat-pump COP must stay >= 1; measured it is
  ~0.72. own_formula_maxrel = max relative deviation of production from my
  closed form, proving WHICH factors produce it.

EXACT COMMAND (from a tree root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
    /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
    tools/audit/round4/D2/d2_own_D2-04.py

EXPECTED (baseline 7dd68dd; float identities, tolerance 1e-9):
  own_formula_maxrel      < 1e-12     (production == my closed form)
  own_min_cop_random      ~ 0.72
  own_random_below_unity  > 100 of 2000
  own_fine_cells_below_unity ~ 51*(scale to finer grid) -- >0 at 0.5 degC
  own_dhw_min_cop         ~ 0.84
  own_invert_band_width_c ~ 19        (-40..-21 at flow 70)
  own_negative_steps      > 100       (derivative < 0 cells at 0.05 degC)
  own_marginal_cop_-21_70 ~ 0.72      (the money symbol)
  own_perturbed_min_cop   = 1.0       (clamp 0.5 -> 1.0, one line)

INSTRUMENTED SYMBOLS: thermal_model.py:ThermalModel.compute_cop,
compute_cop_dhw, marginal_cop, ThermalParameters.from_config (the
cop_flow_carnot gate), optimizer.py:_buffer_charge_ceiling's call shape
(read: line 5877 feeds marginal_cop store_temp in [35, buffer_max_temp]).
PERTURBATION (executed in-section 5): max(cop, 0.5) -> max(cop, 1.0)
via a wrapper; own_perturbed_min_cop must rise to 1.0.
NULL CONTROLS: with mixing_valve_mode "none" (no valve -> no Carnot term)
min over the same random points must be 1.05; at the DHW penalty's own
reference temperature (35 degC) the DHW min must be 1.05.

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
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalParameters,
)

CPU = Cpu()
CFG = {"mixing_valve_mode": "manual", "two_zone_enabled": True}
P = ThermalParameters.from_config(CFG)
MODEL = ThermalModel(P)
result("own_cop_flow_carnot", int(P.cop_flow_carnot), "bool")
result("own_cop_nominal", float(P.cop_nominal), "cop")
result("own_cop_reference_c", float(P.cop_reference_temp), "degC")
result("own_flow_reference_c", float(P.cop_flow_reference_temp), "degC")
result("own_buffer_max_c", float(P.buffer_max_temp), "degC")
result("own_derate_none", int(P.defrost_derate is None), "bool")


def my_formula(outdoor: float, flow: float) -> float:
    """My own closed form from reading compute_cop's source."""
    delta = outdoor - P.cop_reference_temp
    factor = max(0.3, 1.0 + 0.025 * delta)
    cop = P.cop_nominal * min(factor, 1.5) * P.cop_scale
    ref = P.cop_flow_reference_temp
    if flow > ref:
        t_out = min(outdoor, P.cop_reference_temp) + 273.15
        cf = (flow + 273.15) / max(flow + 273.15 - t_out, 1.0)
        cr = (ref + 273.15) / max(ref + 273.15 - t_out, 1.0)
        cop *= max(0.25, cf / cr)
    return max(cop, 0.5)


# --- 1. random-point cross-check of my formula vs production ----------------
rng = np.random.default_rng(42)
out_r = rng.uniform(-25.0, 15.0, 2000)
flow_r = rng.uniform(35.0, float(P.buffer_max_temp), 2000)
worst = 0.0
below = 0
min_cop = float("inf")
with CPU:
    for o, f in zip(out_r, flow_r):
        got = MODEL.compute_cop(float(o), flow_temp=float(f))
        worst = max(worst, abs(got - my_formula(float(o), float(f)))
                    / max(got, 1e-9))
        if got < 1.0:
            below += 1
        min_cop = min(min_cop, got)
result("own_formula_maxrel", worst, "rel")
result("own_min_cop_random", min_cop, "cop")
result("own_random_below_unity", below, "count")
result("own_random_points", 2000, "count")

# --- 2. my own fine grid (0.5 degC) ------------------------------------------
outs = np.arange(-25.0, 15.01, 0.5)
flows = np.arange(35.0, float(P.buffer_max_temp) + 0.01, 0.5)
g = np.array([[MODEL.compute_cop(float(o), flow_temp=float(f)) for o in outs]
              for f in flows])
result("own_fine_cells", int(g.size), "count")
result("own_fine_cells_below_unity", int(np.sum(g < 1.0)), "count")
result("own_fine_min_cop", float(g.min()), "cop")
ri, ci = np.unravel_index(int(np.argmin(g)), g.shape)
result("own_fine_min_at", f"outdoor={outs[ci]}C,flow={flows[ri]}C")
# leave-one-out: drop the coldest outdoor COLUMN and the hottest flow ROW
result("own_fine_below_unity_drop_coldest_col",
       int(np.sum(g[:, 1:] < 1.0)), "count")
result("own_fine_below_unity_drop_hottest_row",
       int(np.sum(g[:-1, :] < 1.0)), "count")

# --- 3. DHW at my own tank grid -----------------------------------------------
tanks = np.arange(40.0, float(P.dhw_hard_max_temp) + 0.01, 1.0)
gd = np.array([[MODEL.compute_cop_dhw(float(o), float(t)) for o in outs]
               for t in tanks])
result("own_dhw_cells", int(gd.size), "count")
result("own_dhw_min_cop", float(gd.min()), "cop")
result("own_dhw_cells_below_unity", int(np.sum(gd < 1.0)), "count")
result("own_dhw_at_35c_min", float(np.min(
    [MODEL.compute_cop_dhw(float(o), 35.0) for o in outs])), "cop")

# --- 4. the inversion, by derivative sign count -------------------------------
sweep = np.arange(-40.0, 10.001, 0.05)
c70 = np.array([MODEL.compute_cop(float(o), flow_temp=70.0) for o in sweep])
d = np.diff(c70)
neg = d < -1e-15
result("own_negative_steps", int(np.sum(neg)), "count")
result("own_invert_band_lo_c", float(sweep[int(np.argmax(neg))]), "degC")
result("own_invert_band_hi_c",
       float(sweep[len(d) - 1 - int(np.argmax(neg[::-1])) + 1]), "degC")
result("own_invert_band_width_c",
       float(sweep[len(d) - 1 - int(np.argmax(neg[::-1])) + 1]
             - sweep[int(np.argmax(neg))]), "degC")
result("own_invert_cop_at_-30c",
       MODEL.compute_cop(-30.0, flow_temp=70.0), "cop")
result("own_invert_cop_at_-21c",
       MODEL.compute_cop(-21.0, flow_temp=70.0), "cop")

# --- 5. the money symbol, at the temperatures the ceiling bisection feeds -----
result("own_marginal_cop_-21_70",
       MODEL.marginal_cop(-21.0, "buffer", store_temp=70.0), "cop")
result("own_marginal_cop_-25_70",
       MODEL.marginal_cop(-25.0, "buffer", store_temp=70.0), "cop")
result("own_marginal_cop_dhw_-25_60",
       MODEL.marginal_cop(-25.0, "dhw", store_temp=60.0), "cop")

# --- 6. null control: no valve -> no Carnot term -------------------------------
plain = ThermalModel(ThermalParameters.from_config(
    {"mixing_valve_mode": "none"}))
result("own_null_carnot_off", int(plain.params.cop_flow_carnot), "bool")
off = np.array([[plain.compute_cop(float(o), flow_temp=float(f))
                 for o in outs] for f in flows])
result("own_null_min_cop", float(off.min()), "cop")
result("own_null_below_unity", int(np.sum(off < 1.0)), "count")
c_off = np.array([plain.compute_cop(float(o), flow_temp=70.0) for o in sweep])
result("own_null_worst_step", float(np.min(np.diff(c_off))), "cop")

# --- 7. perturbation: final clamp 0.5 -> 1.0 (one production line) -------------
_orig_compute = ThermalModel.compute_cop


def compute_cop_clamped(self, outdoor_temp, humidity=None, flow_temp=None):
    return max(_orig_compute(self, outdoor_temp, humidity, flow_temp), 1.0)


ThermalModel.compute_cop = compute_cop_clamped
try:
    pc = np.array([[MODEL.compute_cop(float(o), flow_temp=float(f))
                    for o in outs] for f in flows])
    result("own_perturbed_min_cop", float(pc.min()), "cop")
    result("own_perturbed_below_unity", int(np.sum(pc < 1.0)), "count")
finally:
    ThermalModel.compute_cop = _orig_compute

footer(CPU, "[d]2_own_D2-04")
