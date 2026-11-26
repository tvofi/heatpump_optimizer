#!/usr/bin/env python3
# Metric: dhw_coast_hours over the tie to==from and neighbours.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g42/probes/probe_523356020b4bb37b.py
# Expected: equal outputs (to==from: hot==cold -> log 1 = 0 -> clip 0.0; or hot<=0 -> 0.0) => equivalent-candidate. Reads RESULT <metric>_baseline / _mutant per metric, then RESULT metrics_moved=<n>.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g42 (see wave/D3-g42/MACHINE.txt); exact arithmetic, no timing.
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalModel.dhw_coast_hours, line 3640.
# Perturbation: production line 3640 `to_temp >= from_temp` -> `to_temp > from_temp` (key 523356020b4bb37b), applied to a scratch copy of custom_components (never the gate tree);
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
    for f in (10.0,20.0,30.0,55.0):
        for amb in (10.0,20.0,25.0):
            for e in (0.0,1e-9):
                out.append((f"h_{f}_{amb}_{e}",repr(m.dhw_coast_hours(f,f-e,amb))))
    return out
if __name__ == "__main__":
    main("523356020b4bb37b", measure, __file__)
