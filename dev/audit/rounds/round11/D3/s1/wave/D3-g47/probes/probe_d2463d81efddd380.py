#!/usr/bin/env python3
# Metric: count of inputs (draw_kw in {0.0,-0.0,nan,tiny}, finite setpoint/inlet/wood, plus a non-finite setpoint) where (reduced, coil) differs between baseline and the `draw<=0 -> draw<0` mutant
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g47/probes/probe_d2463d81efddd380.py
# EXPECTED RESULT: inputs_differing=1 (only dhw_setpoint=inf with draw 0: baseline (0.0,0.0), mutant nan); finite inputs 0 -> equivalent-candidate for finite inputs
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g47 (4 vCPU Xeon @ 2.30GHz). Values are exact (no wall/CPU numbers).
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:dhw_coil_draw_reduction (line 2998).
# Perturbation: the gate's one-line mutant `if draw_kw <= 0.0:` -> `if draw_kw < 0.0:` applied in memory (g47_mut.load re-compiles the module source with that one line
#   replaced; nothing on disk changes). Direction: see EXPECTED. Null control: `controls` inputs where the edit cannot matter must show 0 differing.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import g47_mut
INF, NAN = float("inf"), float("nan")
inputs = [dict(draw_kw=d, wood_temp=w, dhw_setpoint=s, inlet_temp=i) for d in (0.0, -0.0, 1e-300, -1e-300) for w in (5.0, 10.0, 45.0, 90.0) for s in (20.0, 48.0, 60.0) for i in (5.0, 10.0, 20.0)]
inputs += [dict(draw_kw=0.0, wood_temp=60.0, dhw_setpoint=INF, inlet_temp=10.0), dict(draw_kw=0.0, wood_temp=NAN, dhw_setpoint=50.0, inlet_temp=10.0)]
controls = [dict(draw_kw=d, wood_temp=60.0, dhw_setpoint=50.0, inlet_temp=10.0) for d in (0.5, 2.0, 7.0)]
g47_mut.probe('d2463d81efddd380', 'dhw_coil_draw_reduction', inputs, controls)
