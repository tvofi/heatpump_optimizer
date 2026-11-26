#!/usr/bin/env python3
# Metric: number of grid inputs (of 34992) on which _valve_two_zone_delivery's 5-tuple (q_rad, q_floor, wood_draw, q_wood_loss, C_w)
#   differs between baseline and mutant; plus the same count restricted to ordinary dt_hours (>= 0.25) and to dt_hours < 1e-6.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g45/probes/probe_39041ccf21eedba6.py
# EXPECTED RESULT baseline-vs-baseline moved=0 (null); inputs_moved>0 (see FIRST combo)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g45 (4 vCPU Xeon @ 2.10GHz), provisional.
# Instrumented symbol: thermal_model.py:2583 _valve_two_zone_delivery `if drawn > delivered > 0.0:`
#   (called from _simulate_step_two_zone, thermal_model.py:3963).
# Perturbation: key 39041ccf21eedba6, `if drawn > delivered > 0.0:` -> `if False:` (a partly starved two-tank step no longer scales the emitter draw down), in an in-memory module copy. Direction: output changes.
# Null control: the same grid run baseline vs baseline (identical module text) moves 0 inputs.
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
import valvecommon as v
base_n, base_moved, _, _ = v.run(2583, 'if drawn > delivered > 0.0:', 'if drawn > delivered > 0.0:')
print(f"RESULT null_moved={base_moved} count")
n, moved, first, worst = v.report(2583, 'if drawn > delivered > 0.0:', 'if False:')
for label, dts in (("ordinary_dt_ge_0.25", (0.25, 1.0)), ("tiny_dt_lt_1e-6", (0.0, 1e-7))):
    g = dict(T_up=(18.0, 21.0, 24.0), T_sl=(15.0, 21.0, 27.0), T_buf=(25.0, 40.0, 60.0), T_w=(30.0, 55.0, 80.0),
             tp=(0.0, 1.0, 6.0), ext=(0.0, 2.0, 10.0), loss=(0.0, 0.1, 3.0), tgt=(None, 35.0), dt=dts, two=(True, False))
    gn, gm, _, _ = v.run(2583, 'if drawn > delivered > 0.0:', 'if False:', g)
    print(f"RESULT moved_{label}={gm} of {gn} count")
