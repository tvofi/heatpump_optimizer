#!/usr/bin/env python3
# Metric: dhw_coil_draw_reduction(draw_kw, wood, setpoint, inlet) tuple for draw_kw <= 0
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g46-h/probes/probe_449caa49315447b2.py   (PROBE_ROOT=<clean baseline copy> while a gate runs)
# Expected: baseline (draw_kw, 0.0); mutant differs for a negative draw only (0 and -0.0 give equal values)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g46-h (4 vCPU Xeon @ 2.30GHz); numbers provisional.
# Instrumented symbol: thermal_model.py:dhw_coil_draw_reduction line 2998; callers dhw_planner.py:926, thermal_model.py:5009
# Perturbation: key 449caa49315447b2, `if draw_kw <= 0.0:` -> `if False:`, in memory (function recompiled from its own source).
# Null control: positive draw: guard false either way
import math
from _pc import tm, mutant
b = tm.dhw_coil_draw_reduction
m = mutant("dhw_coil_draw_reduction", "if draw_kw <= 0.0:", "if False:")
for tag, d in (("zero", 0.0), ("negzero", -0.0), ("negative", -1.5), ("nan", float("nan")), ("null_positive", 2.0)):
    for wood in (60.0, 10.0):
        print("RESULT %s wood=%g baseline=%r mutant=%r" % (tag, wood, b(d, wood, 55.0, 10.0), m(d, wood, 55.0, 10.0)))
