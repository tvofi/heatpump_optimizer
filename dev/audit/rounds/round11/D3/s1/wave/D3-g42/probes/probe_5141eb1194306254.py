#!/usr/bin/env python3
# Metric: flow_lift_factor at flow_temp == cop_flow_reference_temp.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g42/probes/probe_5141eb1194306254.py
# Expected: flow==ref: baseline carnot_flow/carnot_ref == 1.0 exactly; mutant returns 1.0 => equivalent-candidate. Reads RESULT <metric>_baseline / _mutant per metric, then RESULT metrics_moved=<n>.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g42 (see wave/D3-g42/MACHINE.txt); exact arithmetic, no timing.
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalModel.flow_lift_factor, line 3366.
# Perturbation: production line 3366 `not flow_temp > ref` -> `not flow_temp >= ref` (key 5141eb1194306254), applied to a scratch copy of custom_components (never the gate tree);
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
    for kw in ({},dict(cop_flow_reference_temp=45.0),dict(cop_flow_reference_temp=30.0,cop_reference_temp=-5.0),dict(cop_reference_temp=50.0)):
        p=ThermalParameters(**kw); m=ThermalModel(p); ref=p.cop_flow_reference_temp
        for t in (-20.0,-5.0,0.0,7.0,12.0,40.0):
            out.append((f"f_{sorted(kw.items())}_{t}",repr(m.flow_lift_factor(ref,t))))
    return out
if __name__ == "__main__":
    main("5141eb1194306254", measure, __file__)
