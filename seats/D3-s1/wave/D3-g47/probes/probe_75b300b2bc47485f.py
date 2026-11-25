#!/usr/bin/env python3
# Metric: floor for surface_rh_limit < 0.05 and == 0 (`max(limit, 0.05)` clamp dropped)
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g47/probes/probe_75b300b2bc47485f.py
# EXPECTED RESULT: inputs_differing>=1 (limit 0.01/0.04: baseline uses 0.05, mutant a lower dew point->higher floor; limit 0.0 raises ZeroDivisionError)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g47 (4 vCPU Xeon @ 2.30GHz). Values are exact (no wall/CPU numbers).
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:mold_safe_room_floor (line 2856).
# Perturbation: the gate's one-line mutant `t_surface_min = dew_point_for_pressure(e / max(surface_rh_limit, 0.05))` -> `t_surface_min = dew_point_for_pressure(e / (surface_rh_limit))` applied in memory (g47_mut.load re-compiles the module source with that one line
#   replaced; nothing on disk changes). Direction: see EXPECTED. Null control: `controls` inputs where the edit cannot matter must show 0 differing.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import g47_mut
INF, NAN = float("inf"), float("nan")
inputs = [dict(room_temp_c=21.0, indoor_rh_percent=55.0, outdoor_temp_c=-5.0, frsi=0.7, surface_rh_limit=0.04), dict(room_temp_c=21.0, indoor_rh_percent=55.0, outdoor_temp_c=-5.0, frsi=0.7, surface_rh_limit=0.01), dict(room_temp_c=21.0, indoor_rh_percent=55.0, outdoor_temp_c=-5.0, frsi=0.7, surface_rh_limit=0.0), dict(room_temp_c=21.0, indoor_rh_percent=55.0, outdoor_temp_c=-5.0, frsi=0.7, surface_rh_limit=-0.1)]
controls = [dict(room_temp_c=21.0, indoor_rh_percent=55.0, outdoor_temp_c=-5.0, frsi=0.7, surface_rh_limit=0.05), dict(room_temp_c=21.0, indoor_rh_percent=55.0, outdoor_temp_c=-5.0, frsi=0.7, surface_rh_limit=0.8), dict(room_temp_c=21.0, indoor_rh_percent=55.0, outdoor_temp_c=-5.0, frsi=0.7, surface_rh_limit=1.0)]
g47_mut.probe('75b300b2bc47485f', 'mold_safe_room_floor', inputs, controls)
