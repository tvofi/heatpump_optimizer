#!/usr/bin/env python3
# Metric: floor at e == 1e-9 hPa exactly (`e <= 1e-9` -> `e < 1e-9`): baseline -100.0 vs the dew-point branch
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g47/probes/probe_1111a3e5d9c44e3f.py
# EXPECTED RESULT: inputs_differing>=1 only if an RH makes rh*svp == 1e-9 bit-exactly (searched by ulp walk); else equivalent-candidate
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g47 (4 vCPU Xeon @ 2.30GHz). Values are exact (no wall/CPU numbers).
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:mold_safe_room_floor (line 2854).
# Perturbation: the gate's one-line mutant `if e <= 1e-9:` -> `if e < 1e-9:` applied in memory (g47_mut.load re-compiles the module source with that one line
#   replaced; nothing on disk changes). Direction: see EXPECTED. Null control: `controls` inputs where the edit cannot matter must show 0 differing.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import g47_mut
INF, NAN = float("inf"), float("nan")
import math
from custom_components.heatpump_optimizer import thermal_model as _t
inputs = []
for rt in (-10.0, 0.0, 5.0, 10.0, 21.0, 30.0):
    svp = _t.saturation_vapor_pressure(rt)
    pct = 1e-9 / svp * 100.0
    for _ in range(0, 1):
        cands = {pct}
        x = pct
        for _i in range(64):
            x = math.nextafter(x, 0.0); cands.add(x)
        x = pct
        for _i in range(64):
            x = math.nextafter(x, 1.0); cands.add(x)
        for c in sorted(cands):
            e = min(max(c, 0.0), 100.0) / 100.0 * svp
            if e == 1e-9:
                inputs.append(dict(room_temp_c=rt, indoor_rh_percent=c, outdoor_temp_c=-5.0, frsi=0.7, surface_rh_limit=0.8))
                break
print(f"SEARCH exact-tie inputs found: {len(inputs)} of 6 room temperatures")
inputs += [dict(room_temp_c=21.0, indoor_rh_percent=r, outdoor_temp_c=-5.0, frsi=0.7, surface_rh_limit=0.8) for r in (1e-9, 1e-8, 1e-7, 1e-6)]
controls = [dict(room_temp_c=21.0, indoor_rh_percent=r, outdoor_temp_c=-5.0, frsi=0.7, surface_rh_limit=0.8) for r in (0.0, 30.0, 70.0)]
g47_mut.probe('1111a3e5d9c44e3f', 'mold_safe_room_floor', inputs, controls)
