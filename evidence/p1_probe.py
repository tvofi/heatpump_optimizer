"""Probe: step-0 hot-water charge shipped when the compressor runs, no charge is under way,
and the tank sits at/above its start temperature. Run from a tree root."""
import sys
from dataclasses import replace
sys.path[:0] = ["tests/hastub", "custom_components", "tests", "dev/audit/harnesses"]
import numpy as np
import r11_honest_dhw_runs as h
import golden
from heatpump_optimizer import optimizer as om
kept = om.HeatPumpOptimizer.optimize
cfg = {}
def solve(opt, *, inputs):
    st = inputs.state
    st = replace(st, dhw_charge_under_way=False, dhw_start_hysteresis_k=cfg["k"],
                 dhw_temperature=cfg["t"])
    inputs = replace(inputs, state=st, compressor_running=True)
    return kept(opt, inputs=inputs)
om.HeatPumpOptimizer.optimize = solve
for name in h.FIXTURES:
    for k in (1.0, 3.0, 5.0):
        for t in (40.0, 44.0, 46.0, 48.0, 50.0, 52.0):
            cfg.update(k=k, t=t)
            got = golden.capture(name, golden.SCENARIOS[name])
            d = np.asarray(got["dhw_power_schedule"], float)
            print(f"{name} k={k} t0={t}: step0 {d[0]:.3f} step1 {d[1]:.3f} sum {d.sum():.3f}")
