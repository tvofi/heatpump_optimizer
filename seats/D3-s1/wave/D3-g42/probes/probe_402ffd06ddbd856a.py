#!/usr/bin/env python3
# Metric: dhw_coast_hours(20, 10, ambient 20): from_temp == ambient.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g42/probes/probe_402ffd06ddbd856a.py
# Expected: baseline 0.0 (tank at ambient never coasts) vs mutant 168.0 (cold<0 branch) => moved. Reads RESULT <metric>_baseline / _mutant per metric, then RESULT metrics_moved=<n>.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g42 (see wave/D3-g42/MACHINE.txt); exact arithmetic, no timing.
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalModel.dhw_coast_hours, line 3649.
# Perturbation: production line 3649 `hot <= 0.0` -> `hot < 0.0` (key 402ffd06ddbd856a), applied to a scratch copy of custom_components (never the gate tree);
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
    m=ThermalModel(ThermalParameters()); out=[]
    for f,t,a in ((20.0,10.0,20.0),(20.0,19.0,20.0),(30.0,10.0,30.0),(21.0,10.0,20.0)):
        out.append((f"h_{f}_{t}_{a}",repr(m.dhw_coast_hours(f,t,a))))
    return out
if __name__ == "__main__":
    main("402ffd06ddbd856a", measure, __file__)
