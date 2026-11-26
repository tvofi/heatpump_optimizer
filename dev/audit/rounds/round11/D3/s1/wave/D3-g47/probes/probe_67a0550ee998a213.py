#!/usr/bin/env python3
# Metric: floor at indoor_rh_percent == 0 (e == 0): baseline the sentinel -100.0; mutant (guard off) runs dew_point_for_pressure on the clamped 1e-9 hPa
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g47/probes/probe_67a0550ee998a213.py
# EXPECTED RESULT: inputs_differing>=1: baseline -100.0; mutant about -169 degC at outdoor -5, frsi 0.7
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g47 (4 vCPU Xeon @ 2.30GHz). Values are exact (no wall/CPU numbers).
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:mold_safe_room_floor (line 2854).
# Perturbation: the gate's one-line mutant `if e <= 1e-9:` -> `if False:` applied in memory (g47_mut.load re-compiles the module source with that one line
#   replaced; nothing on disk changes). Direction: see EXPECTED. Null control: `controls` inputs where the edit cannot matter must show 0 differing.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import g47_mut
INF, NAN = float("inf"), float("nan")
inputs = [dict(room_temp_c=21.0, indoor_rh_percent=0.0, outdoor_temp_c=-5.0, frsi=0.7, surface_rh_limit=0.8), dict(room_temp_c=21.0, indoor_rh_percent=-3.0, outdoor_temp_c=-5.0, frsi=0.7, surface_rh_limit=0.8), dict(room_temp_c=21.0, indoor_rh_percent=0.0, outdoor_temp_c=-20.0, frsi=0.7, surface_rh_limit=0.8), dict(room_temp_c=21.0, indoor_rh_percent=0.0, outdoor_temp_c=10.0, frsi=0.7, surface_rh_limit=0.8), dict(room_temp_c=21.0, indoor_rh_percent=1e-12, outdoor_temp_c=-5.0, frsi=0.7, surface_rh_limit=0.8)]
controls = [dict(room_temp_c=21.0, indoor_rh_percent=55.0, outdoor_temp_c=-5.0, frsi=0.7, surface_rh_limit=0.8), dict(room_temp_c=21.0, indoor_rh_percent=20.0, outdoor_temp_c=-5.0, frsi=0.7, surface_rh_limit=0.8), dict(room_temp_c=21.0, indoor_rh_percent=95.0, outdoor_temp_c=-5.0, frsi=0.7, surface_rh_limit=0.8)]
g47_mut.probe('67a0550ee998a213', 'mold_safe_room_floor', inputs, controls)
