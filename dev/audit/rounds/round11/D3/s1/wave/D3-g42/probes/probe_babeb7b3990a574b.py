#!/usr/bin/env python3
# Metric: flow_lift_factor where outdoor cap (cop_reference_temp) exceeds the flow temperature (lift < 1 K).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g42/probes/probe_babeb7b3990a574b.py
# Expected: default params: equal (lift>=1); cop_reference_temp above flow: baseline floored lift, mutant divides by <=0 => moved if such params are reachable. Reads RESULT <metric>_baseline / _mutant per metric, then RESULT metrics_moved=<n>.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g42 (see wave/D3-g42/MACHINE.txt); exact arithmetic, no timing.
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalModel.flow_lift_factor, line 3387.
# Perturbation: production line 3387 `max(flow+273.15-t_out,1.0)` -> `unfloored` (key babeb7b3990a574b), applied to a scratch copy of custom_components (never the gate tree);
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
    for name,kw in (("default",{}),("ref45",dict(cop_reference_temp=45.0)),("ref40_flowref30",dict(cop_reference_temp=40.0,cop_flow_reference_temp=30.0))):
        p=ThermalParameters(**kw); m=ThermalModel(p)
        for fl in (31.0,35.0,36.0,40.0,60.0):
            for t in (-10.0,7.0,35.0,45.0):
                try: v=repr(m.flow_lift_factor(fl,t))
                except Exception as e: v=type(e).__name__
                out.append((f"{name}_{fl}_{t}",v))
    return out
if __name__ == "__main__":
    main("babeb7b3990a574b", measure, __file__)
