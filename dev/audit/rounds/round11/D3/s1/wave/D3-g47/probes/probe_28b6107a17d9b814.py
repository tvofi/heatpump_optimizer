#!/usr/bin/env python3
# Metric: floor for indoor_rh_percent <= 0 and non-finite (lower RH clamp dropped; negative RH gives e<0 and the same -100 return)
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g47/probes/probe_28b6107a17d9b814.py
# EXPECTED RESULT: inputs_differing=0 -> equivalent-candidate
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g47 (4 vCPU Xeon @ 2.30GHz). Values are exact (no wall/CPU numbers).
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:mold_safe_room_floor (line 2852).
# Perturbation: the gate's one-line mutant `rh = min(max(indoor_rh_percent, 0.0), 100.0) / 100.0` -> `rh = min((indoor_rh_percent), 100.0) / 100.0` applied in memory (g47_mut.load re-compiles the module source with that one line
#   replaced; nothing on disk changes). Direction: see EXPECTED. Null control: `controls` inputs where the edit cannot matter must show 0 differing.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import g47_mut
INF, NAN = float("inf"), float("nan")
def _m(rh, rt=21.0): return dict(room_temp_c=rt, indoor_rh_percent=rh, outdoor_temp_c=-5.0, frsi=0.7, surface_rh_limit=0.8)
inputs = [_m(r) for r in (0.0, -0.0, -1.0, -50.0, -1e9, NAN, INF, -INF)] + [_m(-5.0, t) for t in (-30.0, 0.0, 40.0)]
controls = [_m(55.0), _m(100.0)]
g47_mut.probe('28b6107a17d9b814', 'mold_safe_room_floor', inputs, controls)
