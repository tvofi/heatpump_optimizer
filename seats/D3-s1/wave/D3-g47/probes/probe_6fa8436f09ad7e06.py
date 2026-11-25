#!/usr/bin/env python3
# Metric: wood_share when floor_temp >= flow_set in region 2 (`max(flow_set-floor,1e-6)` clamp dropped): baseline 0.0, mutant ZeroDivisionError at floor == flow_set
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g47/probes/probe_6fa8436f09ad7e06.py
# EXPECTED RESULT: inputs_differing>=1: baseline 0.0; mutant RAISES ZeroDivisionError at floor_temp == flow_set (floor_temp > flow_set: -0.0 vs 0.0 sign only)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g47 (4 vCPU Xeon @ 2.30GHz). Values are exact (no wall/CPU numbers).
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:wood_share (line 2906).
# Perturbation: the gate's one-line mutant `span = max(flow_set - floor_temp, 1e-6)` -> `span = (flow_set - floor_temp)` applied in memory (g47_mut.load re-compiles the module source with that one line
#   replaced; nothing on disk changes). Direction: see EXPECTED. Null control: `controls` inputs where the edit cannot matter must show 0 differing.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import g47_mut
INF, NAN = float("inf"), float("nan")
def _w(wt, hp, fs, fl): return dict(wood_temp=wt, hp_temp=hp, flow_set=fs, floor_temp=fl, margin=3.0)
inputs = [_w(40.0, 60.0, 45.0, fl) for fl in (45.0, 45.0 + 1e-9, 46.0, 60.0)]
controls = [_w(40.0, 60.0, 45.0, 20.0), _w(44.0, 55.0, 45.0, 30.0)]
g47_mut.probe('6fa8436f09ad7e06', 'wood_share', inputs, controls)
