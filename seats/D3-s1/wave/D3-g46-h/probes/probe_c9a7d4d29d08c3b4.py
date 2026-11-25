#!/usr/bin/env python3
# Metric: _wood_share_vec share at margin == 0 for a region-3 element with wood_temp == hp_temp < flow_set
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g46-h/probes/probe_c9a7d4d29d08c3b4.py   (PROBE_ROOT=<clean baseline copy> while a gate runs)
# Expected: baseline finite; mutant nan (0/0 in hotter). production never passes margin (default WOOD_TANK_MIN_MARGIN > 1e-6, clamp inert there)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g46-h (4 vCPU Xeon @ 2.30GHz); numbers provisional.
# Instrumented symbol: thermal_model.py:_wood_share_vec line 2952; sole production caller thermal_model.py:4685 passes no margin
# Perturbation: key c9a7d4d29d08c3b4, `m = max(margin, 1e-6)` -> `m = (margin)`, in memory (function recompiled from its own source).
# Null control: default margin: both agree
import warnings, numpy as np
from _pc import tm, mutant
b = tm._wood_share_vec
m = mutant("_wood_share_vec", "m = max(margin, 1e-6)", "m = (margin)")
warnings.simplefilter("ignore")
w = np.array([30.0]); h = np.array([30.0]); f = np.array([20.0])
for tag, mg in (("margin0", 0.0), ("null_default", tm.WOOD_TANK_MIN_MARGIN)):
    print("RESULT %s baseline=%r mutant=%r" % (tag, float(b(w, h, 35.0, f, mg)[0]), float(m(w, h, 35.0, f, mg)[0])))
print("RESULT default_margin_gt_floor=%r" % (tm.WOOD_TANK_MIN_MARGIN > 1e-6))
