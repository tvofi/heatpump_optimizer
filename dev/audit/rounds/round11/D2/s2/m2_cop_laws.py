"""D2.M2 cells cop-monotone, carnot-band, derate-unit-interval, per climate.

Metric (one line per identity; tolerance 1e-12 absolute unless stated):
  cop_outdoor_fall   = count of adjacent grid pairs where ThermalModel.compute_cop (valve plant,
                       flow priced; direct plant, curve flow; plain) or compute_cop_dhw FALLS as
                       outdoor rises.
  cop_flow_rise      = count of adjacent pairs where compute_cop (valve) or compute_cop_dhw
                       RISES as the flow / tank temperature rises (KEY: the COP the production
                       method returns).
  lift_over1/max     = ThermalModel.flow_lift_factor outside [0, 1] (a lift cost is a derate).
  dhw55_over_space   = mean over the climate's outdoor steps of compute_cop_dhw(T, 55)/compute_cop(T).
  batch_parity_maxabs= max |_batch_cop - compute_cop| on the valve plant (bitwise contract).
  carnot_frac_min/max= COP / ((Tf+273.15)/(Tf-Tout)) over Tf > Tout+1 K; the tree states no
                       band, so only the physical bound (0, 1] is judged: carnot_frac_over1.
  derate_out_of_unit = count of defrost/partload/flow-lift factors outside [0, 1].
  derate_edge_jumps  = count of |factor(e+1e-9) - factor(e-1e-9)| > 1e-6 at every bucket edge.
  duty_law_mismatch  = count of duty grid points where defrost.derate_from_duty(d) differs
                       from the module's documented law clip(1 - d*DEFROST_LOSS_MULTIPLIER,
                       DERATE_MIN, DERATE_MAX) by > 1e-12.   (KEY: the value the production
                       function returns, never an input attribute.)
  frost_cop_ratio    = compute_cop(T, 90 %RH) with a fully trusted MEASURED duty of 0.2 in
                       every bucket / compute_cop with no derate, over the climate's
                       frost-band steps (documented law: 1 - 0.2*1.5 = 0.70).

Command (from the export root):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D2/s2/m2_cop_laws.py [--perturb]
--perturb=<arm> applies one one-line edit in a private copy of the package (tempfile root):
  defrost: defrost.py `1.0 + duty * DEFROST_LOSS_MULTIPLIER` -> `1.0 - duty * ...`
           expected: duty_law_mismatch 60 -> 0, frost_cop_ratio 1.0 -> 0.70 (winter_mild, shoulder).
  lift:    thermal_model.py flow_lift_factor `carnot_ref / carnot_flow` -> `carnot_flow / carnot_ref`
           expected: every *.cop_flow_rise, *.lift_over1, *.carnot_frac_over1 and
           batch_parity_maxabs -> 0.
Expected at baseline: see the RESULT block recorded in REPORT.md (counts exact).
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B5 (shared, counts only).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C

EDITS = {
    "defrost": [("defrost.py", "1.0 + duty * DEFROST_LOSS_MULTIPLIER", "1.0 - duty * DEFROST_LOSS_MULTIPLIER")],
    "lift": [("thermal_model.py", "return max(0.25, carnot_ref / carnot_flow)", "return max(0.25, carnot_flow / carnot_ref)")],
}
_arm = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--perturb=")), None)
C.setup_paths(EDITS[_arm] if _arm else None)

from dataclasses import replace
from datetime import datetime, timezone
import numpy as np

from heatpump_optimizer import defrost
from heatpump_optimizer.thermal_model import (
    ThermalModel, ThermalParameters, partload_factor,
)
from profiles import weather

START = datetime(2025, 1, 15, 0, 0, tzinfo=timezone.utc)
CLIMATES = ("winter_cold", "winter_mild", "summer_warm", "summer_cool", "shoulder")
TOL = 1e-12

base = ThermalParameters()
valve = replace(base, cop_flow_carnot=True)
direct = replace(base, flow_curve_cop=True, flow_curve_bias=0.0)
flows = np.arange(20.0, 70.0 + 1e-9, 0.5)
tanks = np.arange(35.0, 65.0 + 1e-9, 0.5)


def inferred_learner(seed):
    rng = np.random.default_rng(seed)
    d = defrost.DefrostDerate()
    for t in range(len(d.factors)):
        for h in range(len(d.factors[t])):
            d.factors[t][h] = float(rng.uniform(defrost.DERATE_MIN, defrost.DERATE_MAX))
            d.counts[t][h] = int(rng.integers(0, 25))
    return d


def measured_learner(duty_value=None, seed=0):
    rng = np.random.default_rng(seed)
    d = defrost.DefrostDerate()
    for t in range(len(d.duty)):
        for h in range(len(d.duty[t])):
            d.duty[t][h] = float(duty_value if duty_value is not None else rng.uniform(0.0, 0.3))
            d.duty_counts[t][h] = defrost.DERATE_CONFIDENCE_SAMPLES
    return d


totals = {"cop_outdoor_fall": 0, "cop_flow_rise": 0, "lift_over1": 0, "carnot_frac_over1": 0, "derate_out_of_unit": 0,
          "derate_edge_jumps": 0, "batch_parity_maxabs": 0.0}
for climate in CLIMATES:
    outdoor = np.asarray(weather(climate, START)[0], dtype=float)
    T = np.linspace(outdoor.min() - 2.0, outdoor.max() + 2.0, 241)
    mv, md, mp = ThermalModel(valve), ThermalModel(direct), ThermalModel(base)
    # --- cop-monotone --------------------------------------------------------
    viol = 0
    rise = 0
    for f in flows:
        c = np.array([mv.compute_cop(t, flow_temp=f) for t in T])
        viol += int(np.sum(np.diff(c) < -TOL))
    for curve_model in (md, mp):
        c = np.array([curve_model.compute_cop(t) for t in T])
        viol += int(np.sum(np.diff(c) < -TOL))
    for tk in tanks:
        c = np.array([mp.compute_cop_dhw(t, tk) for t in T])
        viol += int(np.sum(np.diff(c) < -TOL))
    for t in T:
        c = np.array([mv.compute_cop(t, flow_temp=f) for f in flows])
        rise += int(np.sum(np.diff(c) > TOL))
        c = np.array([mp.compute_cop_dhw(t, tk) for tk in tanks])
        rise += int(np.sum(np.diff(c) > TOL))
    parity = max(
        float(np.max(np.abs(mv._batch_cop(float(t), None, flows, True)
                            - np.array([mv.compute_cop(float(t), flow_temp=f) for f in flows]))))
        for t in T)
    # --- carnot-band ---------------------------------------------------------
    fr = []
    for t in T:
        for f in flows:
            if f > t + 1.0:
                fr.append(mv.compute_cop(t, flow_temp=f) / ((f + 273.15) / (f - t)))
        for tk in tanks:
            if tk > t + 1.0:
                fr.append(mp.compute_cop_dhw(t, tk) / ((tk + 273.15) / (tk - t)))
    fr = np.array(fr)
    over1 = int(np.sum(fr > 1.0))
    # --- derate-unit-interval ------------------------------------------------
    H = np.linspace(0.0, 100.0, 41)
    out_unit = 0
    for learner in (inferred_learner(1), inferred_learner(2), measured_learner(seed=3)):
        vals = np.array([[learner.factor(t, h) for h in H] for t in T])
        out_unit += int(np.sum((vals < 0.0) | (vals > 1.0)))
    for d in (0.0, 0.1, 0.3, 0.45):
        pp = replace(base, cop_partload_derate=d)
        v = partload_factor(pp, np.linspace(0.0, pp.max_electrical_power * 1.2, 200))
        out_unit += int(np.sum((v < 0.0) | (v > 1.0)))
    fl = np.array([mv.flow_lift_factor(t, f) for t in T for f in flows])
    lift_over1 = int(np.sum((fl < 0.0) | (fl > 1.0)))
    lift_max = float(fl.max())
    jumps = 0
    for learner in (inferred_learner(1), measured_learner(seed=3)):
        for e in defrost.TEMP_EDGES + (defrost.FROST_BAND_MIN_C, defrost.FROST_BAND_MAX_C):
            for h in H:
                if abs(learner.factor(e + 1e-9, h) - learner.factor(e - 1e-9, h)) > 1e-6:
                    jumps += 1
        for e in defrost.HUMIDITY_EDGES:
            for t in T:
                if abs(learner.factor(t, e + 1e-9) - learner.factor(t, e - 1e-9)) > 1e-6:
                    jumps += 1
    # --- the measured defrost law through compute_cop ------------------------
    frost = outdoor[(outdoor >= defrost.FROST_BAND_MIN_C) & (outdoor < defrost.FROST_BAND_MAX_C)]
    if frost.size:
        derated = ThermalModel(replace(base, defrost_derate=measured_learner(0.2)))
        ratio = float(np.mean([derated.compute_cop(t, 90.0) / mp.compute_cop(t, 90.0) for t in frost]))
    else:
        ratio = "n/a"
    C.result(f"{climate}.cop_outdoor_fall", viol, "count")
    C.result(f"{climate}.cop_flow_rise", rise, "count")
    C.result(f"{climate}.lift_over1", lift_over1, "count")
    C.result(f"{climate}.lift_max", round(lift_max, 6), "factor")
    C.result(f"{climate}.dhw55_over_space_cop", round(float(np.mean([mp.compute_cop_dhw(t, 55.0) / mp.compute_cop(t) for t in outdoor])), 6), "ratio")
    C.result(f"{climate}.batch_parity_maxabs", parity)
    C.result(f"{climate}.carnot_frac_min", round(float(fr.min()), 4))
    C.result(f"{climate}.carnot_frac_max", round(float(fr.max()), 4))
    C.result(f"{climate}.carnot_frac_over1", over1, "count")
    C.result(f"{climate}.derate_out_of_unit", out_unit, "count")
    C.result(f"{climate}.derate_edge_jumps", jumps, "count")
    C.result(f"{climate}.frost_steps", int(frost.size), "count")
    C.result(f"{climate}.frost_cop_ratio", ratio if ratio == "n/a" else round(ratio, 6), "ratio")
    totals["cop_outdoor_fall"] += viol
    totals["cop_flow_rise"] += rise
    totals["lift_over1"] += lift_over1
    totals["carnot_frac_over1"] += over1
    totals["derate_out_of_unit"] += out_unit
    totals["derate_edge_jumps"] += jumps
    totals["batch_parity_maxabs"] = max(totals["batch_parity_maxabs"], parity)

duties = np.linspace(0.0, defrost.DEFROST_DUTY_MAX, 61)
documented = np.clip(1.0 - duties * defrost.DEFROST_LOSS_MULTIPLIER, defrost.DERATE_MIN, defrost.DERATE_MAX)
got = np.array([defrost.derate_from_duty(d) for d in duties])
C.result("duty_law_mismatch", int(np.sum(np.abs(got - documented) > TOL)), "count")
C.result("duty_law_at_0.2", round(float(defrost.derate_from_duty(0.2)), 6), "factor")
C.result("duty_law_documented_at_0.2", round(float(np.clip(1 - 0.2 * defrost.DEFROST_LOSS_MULTIPLIER, defrost.DERATE_MIN, 1.0)), 6), "factor")
for k, v in totals.items():
    C.result(f"total.{k}", v)
C.trailer()
