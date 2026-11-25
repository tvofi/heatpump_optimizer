#!/usr/bin/env python3
# Metric: floor (degC) for frsi above the 0.98 clamp
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g47/probes/probe_4c3cfbe1e4ad2a14.py
# EXPECTED RESULT: inputs_differing>=1 (frsi 0.99/1.0/1.5: baseline floor uses 0.98, mutant the raw frsi)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g47 (4 vCPU Xeon @ 2.30GHz). Values are exact (no wall/CPU numbers).
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:mold_safe_room_floor (line 2851).
# Perturbation: the gate's one-line mutant `frsi = min(max(frsi, 0.3), 0.98)` -> `frsi = (max(frsi, 0.3))` applied in memory (g47_mut.load re-compiles the module source with that one line
#   replaced; nothing on disk changes). Direction: see EXPECTED. Null control: `controls` inputs where the edit cannot matter must show 0 differing.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import g47_mut
INF, NAN = float("inf"), float("nan")
inputs = [dict(room_temp_c=21.0, indoor_rh_percent=55.0, outdoor_temp_c=-5.0, frsi=0.99, surface_rh_limit=0.8), dict(room_temp_c=21.0, indoor_rh_percent=55.0, outdoor_temp_c=-5.0, frsi=1.0, surface_rh_limit=0.8), dict(room_temp_c=21.0, indoor_rh_percent=55.0, outdoor_temp_c=-5.0, frsi=1.5, surface_rh_limit=0.8), dict(room_temp_c=21.0, indoor_rh_percent=55.0, outdoor_temp_c=-15.0, frsi=2.0, surface_rh_limit=0.8)]
controls = [dict(room_temp_c=21.0, indoor_rh_percent=55.0, outdoor_temp_c=-5.0, frsi=0.3, surface_rh_limit=0.8), dict(room_temp_c=21.0, indoor_rh_percent=55.0, outdoor_temp_c=-5.0, frsi=0.7, surface_rh_limit=0.8), dict(room_temp_c=21.0, indoor_rh_percent=55.0, outdoor_temp_c=-5.0, frsi=0.98, surface_rh_limit=0.8)]
g47_mut.probe('4c3cfbe1e4ad2a14', 'mold_safe_room_floor', inputs, controls)
