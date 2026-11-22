#!/usr/bin/env python3
"""Verifier VD3L, independent V2 measurements (own inputs, whole-module mutants).
Run: VROOT=<tree> PYTHONPATH=<tree>/tests/hastub python3 v2_simple.py
Each finding prints RESULT <id>_base / _mut / _null; null = an input where the mutated
comparison cannot decide, so base==mut is required."""
import os, sys
for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(v, "1")
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from mutload import load

def r(k, v): print(f"RESULT {k}={v}")

# D3-s1-02: tariff.py:744 k<=0 -> k<0. Own vector [0.5, 4.0, 4.0, 1.0], tau 0.05.
b, m = load("tariff", 744, "if x.size == 0 or k <= 0:", "if x.size == 0 or k < 0:")
x = np.array([0.5, 4.0, 4.0, 1.0])
r("02_scalar_k0_base", round(b._smooth_topk_sum(x, 0, 0.05), 6))
r("02_scalar_k0_mut", round(m._smooth_topk_sum(x, 0, 0.05), 6))
r("02_batch_k0_mut", np.round(m._smooth_topk_sum_batch(x[None, :], 0, 0.05), 6).tolist())
r("02_null_k2_delta", abs(b._smooth_topk_sum(x, 2, 0.05) - m._smooth_topk_sum(x, 2, 0.05)))
r("02_null_kneg_delta", abs(b._smooth_topk_sum(x, -1, 0.05) - m._smooth_topk_sum(x, -1, 0.05)))

# D3-s1-62: grid_fee.py:173 `if not sep:` -> `if False:`. Own text "Jan-Mar 0.3" (tokens but no '=').
b, m = load("grid_fee", 173, "if not sep:", "if False:")
def nrules(mod, spec):
    try:
        return len(mod.parse_rules(spec))
    except mod.GridFeeError:
        return -1
    except Exception as e:
        return f"other:{type(e).__name__}"
for name, spec in (("bare_tokens", "Jan-Mar 0.3"), ("bare_rate", "0.7")):
    r(f"62_{name}_base", nrules(b, spec)); r(f"62_{name}_mut", nrules(m, spec))
    r(f"62_{name}_problem_base", b.spec_problem(spec)); r(f"62_{name}_problem_mut", m.spec_problem(spec))
r("62_null_delta", int(nrules(b, "Jan-Mar 17:00-20:00 = 0.3") != nrules(m, "Jan-Mar 17:00-20:00 = 0.3")))

# D3-s1-63: grid_fee.py:355 > -> >= ; own tie uses a NEGATIVE rule whose |rate| equals fixed.
b, m = load("grid_fee", 355, "if abs(rule.rate) > worst:", "if abs(rule.rate) >= worst:")
def sched(mod, fixed, rules):
    return mod.GridFeeSchedule(mode=mod.MODE_RULES, fixed=fixed, rules=tuple(mod.parse_rules(rules)))
s_b, s_m = sched(b, 0.4, "Jun = -0.4"), sched(m, 0.4, "Jun = -0.4")
r("63_base", b.max_abs_component(s_b)); r("63_mut", m.max_abs_component(s_m))
r("63_null_delta", int(b.max_abs_component(sched(b, 0.4, "Jun = 0.5")) != m.max_abs_component(sched(m, 0.4, "Jun = 0.5"))))

# D3-s1-64: grid_fee.py:383 < -> <= ; own tie fixed=0.1 with rule "Mon = 0.1".
b, m = load("grid_fee", 383, "if rule.rate < lowest:", "if rule.rate <= lowest:")
r("64_base", b.min_component(sched(b, 0.1, "Mon = 0.1"))); r("64_mut", m.min_component(sched(m, 0.1, "Mon = 0.1")))
r("64_null_delta", int(b.min_component(sched(b, 0.1, "Mon = 0.05")) != m.min_component(sched(m, 0.1, "Mon = 0.05"))))

# D3-s1-65 / 66: flow_lift. Own sequence: 5 residuals of 0 K, then one of +10 K (curve 30 C).
def bias(mod, seq, curve=30.0):
    fb = mod.FlowCurveBias()
    for res in seq:
        fb.observe(curve + res, curve)
    return round(fb.bias_k, 6)
b, m = load("flow_lift", 47, "FLOW_BIAS_ALPHA = 0.1", "FLOW_BIAS_ALPHA = 0.2")
r("65_base", bias(b, [0]*5 + [10])); r("65_mut", bias(m, [0]*5 + [10]))
r("65_null_delta", abs(bias(b, [0, 10, 0, 10]) - bias(m, [0, 10, 0, 10])))
b, m = load("flow_lift", 188, "if self.samples < FLOW_BIAS_MIN_SAMPLES:", "if self.samples <= FLOW_BIAS_MIN_SAMPLES:")
r("66_base", bias(b, [0]*5 + [10])); r("66_mut", bias(m, [0]*5 + [10]))
r("66_null_delta", abs(bias(b, [0]*4 + [10]) - bias(m, [0]*4 + [10])))
r("66_null7_delta", round(abs(bias(b, [0]*5 + [10] + [10]) - bias(m, [0]*5 + [10] + [10])), 6))

# D3-s1-67: thermal_model.py:169 `if not spec:` -> `if False:`; via ThermalParameters.from_config, own config.
b, m = load("thermal_model", 169, "if not spec:", "if False:")
const = load("const")
for name, cfg in (("absent", {}), ("empty", {const.CONF_HOLIDAY_DHW_WINDOWS: ""})):
    try:
        vb = b.ThermalParameters.from_config(dict(cfg)).dhw_holiday_windows
        vm = m.ThermalParameters.from_config(dict(cfg)).dhw_holiday_windows
    except Exception as e:
        vb = vm = f"from_config raised {type(e).__name__}: {e}"
    r(f"67_{name}_base", vb); r(f"67_{name}_mut", vm)
cfg = {const.CONF_HOLIDAY_DHW_WINDOWS: "06:00-07:30"}
r("67_null_delta", int(b._holiday_dhw_windows(cfg) != m._holiday_dhw_windows(cfg)))

# D3-s1-71: price_model.py:252 <= -> < ; own day: 96 quarters each exactly the float that makes mean==1e-6.
b, m = load("price_model", 252, "if float(np.mean(values)) <= 1e-6:", "if float(np.mean(values)) < 1e-6:")
from datetime import datetime, timezone
day = np.zeros(96); day[:4] = 24e-6  # one hour carries everything; mean = 96e-6/96
r("71_mean_exact", int(float(np.mean(day)) == 1e-6))
def acc(mod, vals):
    pm = mod.PriceShapeModel()
    return int(bool(pm.observe_day_quarters(datetime(2026, 3, 4, tzinfo=timezone.utc), list(vals))))
r("71_base", acc(b, day)); r("71_mut", acc(m, day))
r("71_null_delta", abs(acc(b, day * 2) - acc(m, day * 2)) + abs(acc(b, day * 0.5) - acc(m, day * 0.5)))
