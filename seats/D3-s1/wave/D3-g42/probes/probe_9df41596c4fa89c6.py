#!/usr/bin/env python3
# Metric: effective_heat_loss_coefficient at precipitation exactly 0.1 mm/h.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g42/probes/probe_9df41596c4fa89c6.py
# Expected: precip=0.1: baseline = dry value, mutant = rain-scaled (multiplier 1.15) => moved. Reads RESULT <metric>_baseline / _mutant per metric, then RESULT metrics_moved=<n>.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g42 (see wave/D3-g42/MACHINE.txt); exact arithmetic, no timing.
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalModel.effective_heat_loss_coefficient, line 3479.
# Perturbation: production line 3479 `precipitation > 0.1` -> `precipitation >= 0.1` (key 9df41596c4fa89c6), applied to a scratch copy of custom_components (never the gate tree);
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
    p=ThermalParameters(); m=ThermalModel(p)
    return [(f"u_{r}",repr(m.effective_heat_loss_coefficient(0.1,0.0,r))) for r in (0.0,0.099,0.1,0.1000001,1.0)]+[("rain_mult",p.rain_heat_loss_multiplier)]
if __name__ == "__main__":
    main("9df41596c4fa89c6", measure, __file__)
