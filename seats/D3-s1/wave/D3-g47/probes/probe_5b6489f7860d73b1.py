#!/usr/bin/env python3
# Metric: floor for indoor_rh_percent above 100 (upper RH clamp dropped)
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g47/probes/probe_5b6489f7860d73b1.py
# EXPECTED RESULT: inputs_differing>=1 (RH 100.5/120: baseline caps at 100 %, mutant a higher floor)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g47 (4 vCPU Xeon @ 2.30GHz). Values are exact (no wall/CPU numbers).
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:mold_safe_room_floor (line 2852).
# Perturbation: the gate's one-line mutant `rh = min(max(indoor_rh_percent, 0.0), 100.0) / 100.0` -> `rh = (max(indoor_rh_percent, 0.0)) / 100.0` applied in memory (g47_mut.load re-compiles the module source with that one line
#   replaced; nothing on disk changes). Direction: see EXPECTED. Null control: `controls` inputs where the edit cannot matter must show 0 differing.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import g47_mut
INF, NAN = float("inf"), float("nan")
inputs = [dict(room_temp_c=21.0, indoor_rh_percent=100.5, outdoor_temp_c=-5.0, frsi=0.7, surface_rh_limit=0.8), dict(room_temp_c=21.0, indoor_rh_percent=101.0, outdoor_temp_c=-5.0, frsi=0.7, surface_rh_limit=0.8), dict(room_temp_c=21.0, indoor_rh_percent=120.0, outdoor_temp_c=-5.0, frsi=0.7, surface_rh_limit=0.8), dict(room_temp_c=21.0, indoor_rh_percent=INF, outdoor_temp_c=-5.0, frsi=0.7, surface_rh_limit=0.8)]
controls = [dict(room_temp_c=21.0, indoor_rh_percent=55.0, outdoor_temp_c=-5.0, frsi=0.7, surface_rh_limit=0.8), dict(room_temp_c=21.0, indoor_rh_percent=100.0, outdoor_temp_c=-5.0, frsi=0.7, surface_rh_limit=0.8), dict(room_temp_c=21.0, indoor_rh_percent=0.0, outdoor_temp_c=-5.0, frsi=0.7, surface_rh_limit=0.8)]
g47_mut.probe('5b6489f7860d73b1', 'mold_safe_room_floor', inputs, controls)
