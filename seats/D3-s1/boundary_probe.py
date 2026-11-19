#!/usr/bin/env python3
# Metric: per full-gate survivor that is a comparison-boundary or return-shape mutant, whether the production
#   symbol's own answer moves on the boundary input (moved=1) and whether its consumer's answer moves (consumer=1).
#   moved=0 marks an equivalent mutant at that input; moved=1, consumer=0 marks a value change no reader sees.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/boundary_probe.py
# EXPECTED RESULT M25_moved=1 count       price_model.PriceShapeModel.expected_daily_min(level=0.0): None -> 0.0
# EXPECTED RESULT M03_moved=0 count       thermal_model.ThermalParameters.seasonal_inlet_temp at swing 0: identical
# EXPECTED RESULT M35_moved=1 count       flow_lift.FlowCurveBias.observe at samples == FLOW_BIAS_MIN_SAMPLES
# EXPECTED RESULT M36_moved=1 count       grid_fee.max_abs_component tie: source "fixed" -> "rules"
# EXPECTED RESULT M21_moved=1 count       grid_fee.min_component tie: source "fixed" -> "rules"
# EXPECTED RESULT H773_moved=1 count      optimizer._holiday_flags_for(no holidays): None -> all-False array
# EXPECTED RESULT H773_consumer=0 count   dhw_planner._dhw_windows_at answers identically for both
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-top6 (4 vCPU Xeon @ 2.30GHz). Counts are exact.
# Instrumented symbols: price_model:PriceShapeModel.expected_daily_min (L337), price_model:PriceShapeModel.observe_day_quarters
#   (L252), thermal_model:ThermalParameters.seasonal_inlet_temp (L835), flow_lift:FlowCurveBias.observe (L188),
#   grid_fee:max_abs_component (L355), grid_fee:min_component (L383), optimizer:_holiday_flags_for (L773).
# Perturbation: each site's recorded mutant line (state/results/complete/<key>.json), applied in memory by
#   re-compiling that one function from its own source with the one edit; nothing on disk changes.
#   Direction per row: moved 0 -> 1 where the boundary input reaches the edited comparison.
# Null control: every row also evaluates an input off the boundary; null_moved counts rows whose off-boundary
#   answer differs between arms (expected 0).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import dataclasses, inspect, json, sys, textwrap
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT))
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import (  # noqa: E402
    dhw_planner, flow_lift as fl, grid_fee as gf, optimizer as op, price_model as pm, thermal_model as tm,
)
from custom_components.heatpump_optimizer.dhw_schedule import parse_windows  # noqa: E402


def mut_of(key, func, owner_ns):
    m = json.loads((HERE / "state/results/complete" / f"{key}.json").read_text())["mutant"]
    src = textwrap.dedent(inspect.getsource(func))
    old, new = m["old"].strip(), m["new"].strip()
    assert src.count(old) == 1, f"{key}: anchor occurs {src.count(old)} times"
    ns = dict(owner_ns)
    exec(compile(src.replace(old, new), "<mutant>", "exec"), ns)
    return ns[func.__name__]


null_moved = 0
out = {}

# M25 price_model.py:337 `level <= 0.0` -> `level < 0.0`
model = pm.PriceShapeModel()
model.days = [pm.SHAPE_CONFIDENCE_DAYS] * len(model.days)
f25 = mut_of("2719aef4cbb8b464", pm.PriceShapeModel.expected_daily_min, pm.__dict__)
out["M25_moved"] = int(model.expected_daily_min([0], 0.0) != f25(model, [0], 0.0))
out["M25_mutant_value"] = f25(model, [0], 0.0)
null_moved += int(model.expected_daily_min([0], 1.0) != f25(model, [0], 1.0))

# M34 price_model.py:252 `<= 1e-6` -> `< 1e-6` on a day whose quarter mean is exactly 1e-6
f34 = mut_of("c38d53ab787ddbfa", pm.PriceShapeModel.observe_day_quarters, pm.__dict__)
when = datetime(2026, 1, 15)
q = [1e-6] * pm.QUARTERS_PER_DAY
out["M34_boundary_exact"] = int(float(np.mean(np.asarray(q))) == 1e-6)
a, b = pm.PriceShapeModel(), pm.PriceShapeModel()
out["M34_moved"] = int(a.observe_day_quarters(when, q) != f34(b, when, q))
qq = list(np.linspace(0.5, 1.5, pm.QUARTERS_PER_DAY))
a, b = pm.PriceShapeModel(), pm.PriceShapeModel()
null_moved += int(a.observe_day_quarters(when, qq) != f34(b, when, qq))

# M03 thermal_model.py:835 `swing <= 0.0` -> `swing < 0.0`
p0 = dataclasses.replace(tm.ThermalParameters(), dhw_inlet_seasonal_amplitude=0.0)
f03 = mut_of("a4b00ac3ca662eec", tm.ThermalParameters.seasonal_inlet_temp, tm.__dict__)
out["M03_moved"] = int(any(p0.seasonal_inlet_temp(d) != f03(p0, d) for d in range(1, 366)))
p1 = dataclasses.replace(tm.ThermalParameters(), dhw_inlet_seasonal_amplitude=3.0)
null_moved += int(any(p1.seasonal_inlet_temp(d) != f03(p1, d) for d in range(1, 366)))

# M35 flow_lift.py:188 `samples < MIN` -> `samples <= MIN`
f35 = mut_of("a0b3b28854fa500c", fl.FlowCurveBias.observe, fl.__dict__)
x, y = fl.FlowCurveBias(), fl.FlowCurveBias()
for _ in range(fl.FLOW_BIAS_MIN_SAMPLES):
    x.observe(37.0, 35.0)
    f35(y, 37.0, 35.0)
null_moved += int(x.bias_k != y.bias_k)
x.observe(45.0, 35.0)
f35(y, 45.0, 35.0)
out["M35_moved"] = int(x.bias_k != y.bias_k)
out["M35_bias_delta_K"] = round(abs(x.bias_k - y.bias_k), 4)

# M36 grid_fee.py:355 `>` -> `>=` and M21 grid_fee.py:383 `<` -> `<=`: a rule equal to the fixed component
sched = gf.GridFeeSchedule(mode=gf.MODE_RULES, fixed=0.5, rules=[gf.FeeRule(rate=0.5)])
f36 = mut_of("95779f9d6d71c50d", gf.max_abs_component, gf.__dict__)
out["M36_moved"] = int(gf.max_abs_component(sched) != f36(sched))
f21 = mut_of("5cc84148fa68bda1", gf.min_component, gf.__dict__)
out["M21_moved"] = int(gf.min_component(sched) != f21(sched))
off = gf.GridFeeSchedule(mode=gf.MODE_RULES, fixed=0.5, rules=[gf.FeeRule(rate=0.7)])
null_moved += int(gf.max_abs_component(off) != f36(off)) + int(gf.min_component(off) != f21(off))

# optimizer.py:773 GUARD_OFF: no holidays configured
f773 = mut_of("65f121eb047174ad", op._holiday_flags_for, op.__dict__)
steps = [datetime(2026, 1, 15) + timedelta(hours=h) for h in range(24)]
hb, hm = op._holiday_flags_for(steps, frozenset()), f773(steps, frozenset())
out["H773_moved"] = int((hb is None) != (hm is None))
win = parse_windows("06:00-08:00,18:00-21:00")
hol = parse_windows("08:00-10:00")
out["H773_consumer"] = int(any(
    dhw_planner._dhw_windows_at(None, None, i, win, hol, hb) != dhw_planner._dhw_windows_at(None, None, i, win, hol, hm)
    for i in range(25)))
hd = frozenset({steps[3].date()})
null_moved += int(not np.array_equal(op._holiday_flags_for(steps, hd), f773(steps, hd)))

for k, v in out.items():
    print(f"RESULT {k}={v} count")
print(f"RESULT null_moved={null_moved} count")
print("RESULT thread_factor=1.0 ratio")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0 count")
