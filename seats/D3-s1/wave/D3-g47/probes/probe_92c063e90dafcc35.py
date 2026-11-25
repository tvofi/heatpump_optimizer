#!/usr/bin/env python3
# Metric: wood_share at hp_temp == flow_set exactly (`>` -> `>=`) for wood_temp below flow_set; region 3 at the tie vs region 2's 0.0
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g47/probes/probe_92c063e90dafcc35.py
# EXPECTED RESULT: inputs_differing=0 if region 3 is continuous (0.0) at hp_temp == flow_set -> equivalent-candidate; else >=1
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g47 (4 vCPU Xeon @ 2.30GHz). Values are exact (no wall/CPU numbers).
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:wood_share (line 2903).
# Perturbation: the gate's one-line mutant `if hp_temp > flow_set:` -> `if hp_temp >= flow_set:` applied in memory (g47_mut.load re-compiles the module source with that one line
#   replaced; nothing on disk changes). Direction: see EXPECTED. Null control: `controls` inputs where the edit cannot matter must show 0 differing.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import g47_mut
INF, NAN = float("inf"), float("nan")
def _w(wt, hp, fs, fl): return dict(wood_temp=wt, hp_temp=hp, flow_set=fs, floor_temp=fl, margin=3.0)
inputs = [_w(w, 45.0, 45.0, fl) for w in (20.0, 30.0, 40.0, 43.0, 44.5, 44.999) for fl in (0.0, 15.0, 20.0, 35.0)] + [_w(40.0, 60.0, 60.0, 20.0)]
controls = [_w(40.0, 50.0, 45.0, 20.0), _w(40.0, 40.0, 45.0, 20.0)]
g47_mut.probe('92c063e90dafcc35', 'wood_share', inputs, controls)
