#!/usr/bin/env python3
# Metric: heat (kW, q_rad + q_floor) that thermal_model._valve_two_zone_delivery lets the single-tank buffer
#   discharge into the emitters on one 0.25 h step when the pump makes 0 kW and the tank holds almost no heat.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/probe_22b5ec87.py
# EXPECTED RESULT delivered_baseline=0.278400 kW  (capped at the energy the tank can give: tank-bound)
# EXPECTED RESULT delivered_mutant=2.800000 kW  (cap vanishes: 1e-6 h divisor makes `available` huge, no scaling)
# EXPECTED RESULT delta=2.521600 kW
# EXPECTED RESULT null_delta=0.0 kW  (tank hot and large: drawn <= available in both arms, edit inert)
# EXPECTED RESULT reach_valve_calls=64 count  (calls of _valve_two_zone_delivery with two_tank False, driven
#   through the public ThermalModel.simulate_step on a two-zone throttled-valve parameter set)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-rem (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:_valve_two_zone_delivery, line 2593
#   (the single-tank `else:` branch's `available = thermal_power - q_buf_loss + c_buf*max(0, T_buf-floor)/max(dt_hours,1e-6)`),
#   called from thermal_model.py:3963 inside _simulate_step_two_zone.
# Perturbation: key 22b5ec8775d5bd50, line 2593 `) / max(dt_hours, 1e-6)` -> `) / min(dt_hours, 1e-6)`, applied in
#   memory to the third such line of the function (the one after `available = `). Direction: delivered up.
# Null control: a 300 L tank at 60 C, where available >> drawn and no scaling happens in either arm.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import dataclasses, inspect, sys, textwrap
from pathlib import Path
from unittest import mock

def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")

ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT))
from custom_components.heatpump_optimizer import mixing_valve, thermal_model as tm  # noqa: E402

fn = tm._valve_two_zone_delivery
src = textwrap.dedent(inspect.getsource(fn))
anchor = "        available = thermal_power - q_buf_loss + c_buf * max(\n            0.0, T_buf - floor_temp\n        ) / max(dt_hours, 1e-6)"
assert src.count(anchor) == 1, "anchor moved"
src = src.replace(anchor, anchor.replace("/ max(dt_hours, 1e-6)", "/ min(dt_hours, 1e-6)"), 1)
ns = dict(tm.__dict__)
exec(compile(src, tm.__file__, "exec"), ns)
mut = ns["_valve_two_zone_delivery"]


def drive(fn_, volume, t_buf):
    p = dataclasses.replace(tm.ThermalParameters(), mixing_valve_mode=mixing_valve.MODE_MANUAL,
                            mixing_valve_target=35.0, buffer_tank_volume=volume)
    st = tm.ThermalState(buffer_tank_temperature=t_buf, upper_floor_temperature=21.0, slab_temperature=22.0)
    qr, qf, *_ = fn_(p, st, 0.0, 0.0, 0.0, 35.0, -10.0, 0.2, 0.25, False)
    return qr + qf


base = drive(fn, 20.0, 24.0)
m = drive(mut, 20.0, 24.0)
null_delta = abs(drive(fn, 300.0, 60.0) - drive(mut, 300.0, 60.0))

calls = []
real = tm._valve_two_zone_delivery


def spy(*a, **k):
    calls.append(a[-1])
    return real(*a, **k)


p = dataclasses.replace(tm.ThermalParameters(), two_zone_enabled=True, mixing_valve_mode=mixing_valve.MODE_MANUAL, mixing_valve_target=35.0)
model = tm.ThermalModel(p)
with mock.patch.object(tm, "_valve_two_zone_delivery", spy):
    s = tm.ThermalState(buffer_tank_temperature=30.0)
    for _ in range(8):
        s = model.simulate_step(s, 0.0, -5.0, dt_hours=0.25)
print(f"RESULT delivered_baseline={base:.6f} kW")
print(f"RESULT delivered_mutant={m:.6f} kW")
print(f"RESULT delta={m - base:.6f} kW")
print(f"RESULT null_delta={null_delta} kW")
print(f"RESULT reach_valve_calls={len(calls)} count")
print(f"RESULT reach_valve_calls_single_tank={sum(1 for c in calls if not c)} count")
