#!/usr/bin/env python3
# Metric: max |share_mutant - share_baseline| of _wood_share_vec over elements with hp_temp == flow_set (wood < flow_set)
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g46-h/probes/probe_efd15cba428cdcf2.py   (PROBE_ROOT=<clean baseline copy> while a gate runs)
# Expected: diff = 0.0 on every tried input (candidate equivalent: region 2 and region 3 both give 0 at the tie)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g46-h (4 vCPU Xeon @ 2.30GHz); numbers provisional.
# Instrumented symbol: thermal_model.py:_wood_share_vec line 2939
# Perturbation: key efd15cba428cdcf2, r2 `hp_temp > flow_set` -> `>=`, in memory (function recompiled from its own source).
# Null control: elements with hp_temp != flow_set (both operators agree)
import numpy as np
from _pc import tm, mutant
b = tm._wood_share_vec
m = mutant("_wood_share_vec", "r2 = (~r1) & (hp_temp > flow_set)", "r2 = (~r1) & (hp_temp >= flow_set)")
worst = 0.0; tried = 0
for flow in (30.0, 35.5, 45.0):
    for floor in (15.0, 22.0, 29.0):
        for wood in np.linspace(5.0, flow - 1e-9, 40):
            for marg in (1e-6, 1.0, tm.WOOD_TANK_MIN_MARGIN, 10.0):
                w = np.array([wood]); h = np.array([flow]); f = np.array([floor])
                d = abs(float(b(w, h, flow, f, marg)[0]) - float(m(w, h, flow, f, marg)[0])); tried += 1
                worst = max(worst, d if d == d else 1e9)
print("RESULT max_abs_diff_at_tie=%r" % worst); print("RESULT inputs_tried=%d" % tried)
w = np.array([40.0]); h = np.array([45.0]); f = np.array([20.0])
print("RESULT null_delta=%r" % abs(float(b(w, h, 35.0, f)[0]) - float(m(w, h, 35.0, f)[0])))
