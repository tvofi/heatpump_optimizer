#!/usr/bin/env python3
# Metric: _wood_share_vec share for a region-2 element (wood < flow_set < hp) whose floor_temp == flow_set (span 0)
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g46-h/probes/probe_968644425a4f97f8.py   (PROBE_ROOT=<clean baseline copy> while a gate runs)
# Expected: baseline 0.0 (finite); mutant nan (0*0/0)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g46-h (4 vCPU Xeon @ 2.30GHz); numbers provisional.
# Instrumented symbol: thermal_model.py:_wood_share_vec line 2946
# Perturbation: key 968644425a4f97f8, span `np.maximum(flow_set - floor_temp, 1e-6)` -> `(flow_set - floor_temp)`, in memory (function recompiled from its own source).
# Null control: floor_temp 5 K below flow_set (span positive: both agree)
import warnings, numpy as np
from _pc import tm, mutant
b = tm._wood_share_vec
m = mutant("_wood_share_vec", "span = np.maximum(flow_set - floor_temp, 1e-6)", "span = (flow_set - floor_temp)")
warnings.simplefilter("ignore")
flow = 35.0
w = np.array([30.0]); h = np.array([40.0])
for tag, fl in (("tie_floor_eq_flow", flow), ("floor_above", flow + 2.0), ("null_floor_below", flow - 5.0)):
    f = np.array([fl]); x, y = float(b(w, h, flow, f)[0]), float(m(w, h, flow, f)[0])
    print("RESULT %s baseline=%r mutant=%r" % (tag, x, y))
