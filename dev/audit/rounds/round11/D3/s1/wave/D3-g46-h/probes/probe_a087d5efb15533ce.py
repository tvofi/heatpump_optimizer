#!/usr/bin/env python3
# Metric: heat (kW) q_rad_from_buf + q_floor_from_buf that _valve_two_zone_delivery credits the emitters from a
#   single-tank store whose available energy is exactly 0.0 while the emitters ask for heat (drawn > 0).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g46-h/probes/probe_a087d5efb15533ce.py
# EXPECTED RESULT delivered_kw_baseline=0.0 ; delivered_kw_mutant>0 (tie: available == 0.0 exactly -> baseline zeroes the draw, mutant leaves it)
# EXPECTED RESULT null_delta=0.0 (available strictly > 0 or strictly < 0: `<=` and `<` agree)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g46-h (4 vCPU Xeon @ 2.30GHz); numbers provisional.
# Instrumented symbol: thermal_model.py:_valve_two_zone_delivery line 2598 `        elif available <= 0.0:`
# Perturbation: key a087d5efb15533ce, `<=` -> `<` in memory (function recompiled). Direction: 0 -> positive delivery.
# Null control: available strictly negative / strictly positive inputs.
from _pc import tm, mutant
base = tm._valve_two_zone_delivery
mut = mutant("_valve_two_zone_delivery", "elif available <= 0.0:", "elif available < 0.0:")
p = tm.ThermalParameters()
st = tm.ThermalState(buffer_tank_temperature=40.0, upper_floor_temperature=21.0, slab_temperature=22.0)
dt = 0.25
floor_t = min(21.0, 22.0)
stored = tm._buffer_capacity(p) * max(0.0, 40.0 - floor_t) / max(dt, 1e-6)
def run(f, qloss, tp=0.0):
    r = f(p, st, tp, 0.0, qloss, None, 5.0, 0.2, dt, False)
    return r[0] + r[1]
# exact tie: tp - qloss + stored == 0.0 with tp = 0 and qloss = stored
tie_b, tie_m = run(base, stored), run(mut, stored)
print("tie available == 0.0:", (0.0 - stored + stored) == 0.0)
print("RESULT delivered_kw_baseline=%r" % tie_b)
print("RESULT delivered_kw_mutant=%r" % tie_m)
# null: strictly negative and strictly positive availability
for tag, q in (("neg", stored * 1.5), ("pos", stored * 0.5)):
    print("RESULT null_delta_%s=%r" % (tag, run(base, q) - run(mut, q)))
