#!/usr/bin/env python3
# Metric: dew_point_for_pressure(vapor_pressure) result / exception at 0.0 and negative pressure
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g46-h/probes/probe_ca6ae797caf18708.py   (PROBE_ROOT=<clean baseline copy> while a gate runs)
# Expected: baseline finite (about -139 C or lower); mutant raises ValueError. Production caller guards e <= 1e-9 before the call, so the clamp is unreachable through it
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g46-h (4 vCPU Xeon @ 2.30GHz); numbers provisional.
# Instrumented symbol: thermal_model.py:dew_point_for_pressure line 2827; caller thermal_model.py:2856 (mold floor), guard at 2854
# Perturbation: key ca6ae797caf18708, `max(vapor_pressure_hpa, 1e-9)` -> `vapor_pressure_hpa`, in memory (function recompiled from its own source).
# Null control: vapor pressure 10 hPa: both agree
from _pc import tm, mutant
b = tm.dew_point_for_pressure
m = mutant("dew_point_for_pressure", "ln = math.log(max(vapor_pressure_hpa, 1e-9) / 6.112)", "ln = math.log((vapor_pressure_hpa) / 6.112)")
def call(f, v):
    try: return f(v)
    except Exception as e: return type(e).__name__
for tag, v in (("zero", 0.0), ("negative", -1.0), ("tiny_1e-12", 1e-12), ("null_10hPa", 10.0)):
    print("RESULT %s baseline=%r mutant=%r" % (tag, call(b, v), call(m, v)))
# through the production caller: rh 0 -> early return; smallest positive rh -> arg > 1e-9
for rh in (0.0, 1e-9, 1e-6):
    for fm in (b, m):
        tm.dew_point_for_pressure = fm
        try: r = tm.mold_safe_room_floor(20.0, rh, 0.0, 0.7)
        except Exception as e: r = type(e).__name__
        print("RESULT via_caller rh=%g %s=%r" % (rh, "baseline" if fm is b else "mutant", r))
tm.dew_point_for_pressure = b
