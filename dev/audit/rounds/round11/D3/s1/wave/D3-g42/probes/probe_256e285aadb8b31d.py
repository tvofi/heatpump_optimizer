#!/usr/bin/env python3
# Metric: flow_lift_factor with carnot_ref <= 1e-9 (cop_flow_reference_temp <= -273.15 C) and a finite sweep.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g42/probes/probe_256e285aadb8b31d.py
# Expected: carnot_ref=(ref+273.15)/max(..,1)>=... > 0 for any physical ref; only ref <= -273.15 reaches the guard => equivalent-candidate for reachable params. Reads RESULT <metric>_baseline / _mutant per metric, then RESULT metrics_moved=<n>.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g42 (see wave/D3-g42/MACHINE.txt); exact arithmetic, no timing.
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalModel.flow_lift_factor, line 3389.
# Perturbation: production line 3389 `carnot_ref <= 1e-9` -> `False` (key 256e285aadb8b31d), applied to a scratch copy of custom_components (never the gate tree);
#   the baseline arm runs the untouched tree. Direction: see Expected.
# Null control: the metrics_moved count over inputs the line cannot distinguish (listed in the metric names); a gate at the comment-only marker (fullgate.py null) leaves the suite green.
import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import main, hits
def _with_ua(p, ua):
    """Params whose dhw_tank_heat_loss_coefficient reads exactly `ua`: the property is memoised on
    (dhw_cooling_rate, dhw_tank_volume), so the cache is primed with the forced value (forced, not config-reachable)."""
    import dataclasses
    q = dataclasses.replace(p)
    q._dhw_ua_cache = ((q.dhw_cooling_rate, q.dhw_tank_volume), ua)
    return q
def _zero_ua(p): return _with_ua(p, 0.0)
def measure(mod):
    from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters
    out=[]
    for ref in (-273.15,-300.0,-100.0,-1.0,0.0,20.0,35.0,60.0):
        p=ThermalParameters(cop_flow_reference_temp=ref); m=ThermalModel(p)
        for fl in (ref+1.0,ref+10.0,80.0):
            try: v=repr(m.flow_lift_factor(fl,0.0))
            except Exception as e: v=type(e).__name__
            out.append((f"ref{ref}_{fl}",v))
    return out
if __name__ == "__main__":
    main("256e285aadb8b31d", measure, __file__)
