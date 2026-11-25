#!/usr/bin/env python3
# Metric: outcome of dhw_coil_draw_reduction when dhw_setpoint == inlet_temp (span clamp 1e-6 dropped): baseline (0.0, draw) vs mutant exception
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g47/probes/probe_41063896cdb5ea71.py
# EXPECTED RESULT: inputs_differing>=1: baseline (0.0, draw_kw); mutant RAISES ZeroDivisionError at setpoint == inlet_temp
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g47 (4 vCPU Xeon @ 2.30GHz). Values are exact (no wall/CPU numbers).
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:dhw_coil_draw_reduction (line 3004).
# Perturbation: the gate's one-line mutant `span = max(dhw_setpoint - inlet_temp, 1e-6)` -> `span = (dhw_setpoint - inlet_temp)` applied in memory (g47_mut.load re-compiles the module source with that one line
#   replaced; nothing on disk changes). Direction: see EXPECTED. Null control: `controls` inputs where the edit cannot matter must show 0 differing.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import g47_mut
INF, NAN = float("inf"), float("nan")
inputs = [dict(draw_kw=2.0, wood_temp=w, dhw_setpoint=s, inlet_temp=10.0) for w in (10.0, 40.0, 60.0) for s in (10.0, 10.0 + 1e-9, 10.0 - 1e-3, 9.0, 12.0)]
controls = [dict(draw_kw=2.0, wood_temp=40.0, dhw_setpoint=s, inlet_temp=10.0) for s in (30.0, 48.0, 60.0)]
g47_mut.probe('41063896cdb5ea71', 'dhw_coil_draw_reduction', inputs, controls)
