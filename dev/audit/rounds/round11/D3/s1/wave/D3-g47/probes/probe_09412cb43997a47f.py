#!/usr/bin/env python3
# Metric: floor (degC) mold_safe_room_floor returns for frsi below the 0.3 clamp
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g47/probes/probe_09412cb43997a47f.py
# EXPECTED RESULT: inputs_differing>=1 (frsi 0.1/0.0/-0.2: baseline floor uses 0.3, mutant a far larger/ill-defined floor, frsi=0 raises)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g47 (4 vCPU Xeon @ 2.30GHz). Values are exact (no wall/CPU numbers).
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:mold_safe_room_floor (line 2851).
# Perturbation: the gate's one-line mutant `frsi = min(max(frsi, 0.3), 0.98)` -> `frsi = min((frsi), 0.98)` applied in memory (g47_mut.load re-compiles the module source with that one line
#   replaced; nothing on disk changes). Direction: see EXPECTED. Null control: `controls` inputs where the edit cannot matter must show 0 differing.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import g47_mut
INF, NAN = float("inf"), float("nan")
inputs = [dict(room_temp_c=21.0, indoor_rh_percent=55.0, outdoor_temp_c=-5.0, frsi=0.29, surface_rh_limit=0.8), dict(room_temp_c=21.0, indoor_rh_percent=55.0, outdoor_temp_c=-5.0, frsi=0.1, surface_rh_limit=0.8), dict(room_temp_c=21.0, indoor_rh_percent=55.0, outdoor_temp_c=-5.0, frsi=0.0, surface_rh_limit=0.8), dict(room_temp_c=21.0, indoor_rh_percent=55.0, outdoor_temp_c=-5.0, frsi=-0.2, surface_rh_limit=0.8)]
controls = [dict(room_temp_c=21.0, indoor_rh_percent=55.0, outdoor_temp_c=-5.0, frsi=0.3, surface_rh_limit=0.8), dict(room_temp_c=21.0, indoor_rh_percent=55.0, outdoor_temp_c=-5.0, frsi=0.5, surface_rh_limit=0.8), dict(room_temp_c=21.0, indoor_rh_percent=55.0, outdoor_temp_c=-5.0, frsi=0.9, surface_rh_limit=0.8)]
g47_mut.probe('09412cb43997a47f', 'mold_safe_room_floor', inputs, controls)
