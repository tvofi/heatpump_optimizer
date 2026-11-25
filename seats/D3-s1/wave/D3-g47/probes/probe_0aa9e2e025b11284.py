#!/usr/bin/env python3
# Metric: count of inputs where (reduced, coil) differs when the t_in <= setpoint cap is dropped (t_in is local; the next use is max(0, setpoint - t_in))
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g47/probes/probe_0aa9e2e025b11284.py
# EXPECTED RESULT: inputs_differing=0 -> equivalent-candidate
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g47 (4 vCPU Xeon @ 2.30GHz). Values are exact (no wall/CPU numbers).
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:dhw_coil_draw_reduction (line 3003).
# Perturbation: the gate's one-line mutant `t_in = min(t_in, dhw_setpoint)` -> `t_in = (t_in)` applied in memory (g47_mut.load re-compiles the module source with that one line
#   replaced; nothing on disk changes). Direction: see EXPECTED. Null control: `controls` inputs where the edit cannot matter must show 0 differing.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import g47_mut
INF, NAN = float("inf"), float("nan")
inputs = [dict(draw_kw=d, wood_temp=w, dhw_setpoint=s, inlet_temp=i) for d in (0.5, 3.0) for w in (5.0, 30.0, 60.0, 95.0, INF, NAN) for s in (8.0, 10.0, 12.0, 30.0, 55.0) for i in (5.0, 10.0, 12.0)]
controls = [dict(draw_kw=2.0, wood_temp=10.0, dhw_setpoint=55.0, inlet_temp=10.0)]
g47_mut.probe('0aa9e2e025b11284', 'dhw_coil_draw_reduction', inputs, controls)
