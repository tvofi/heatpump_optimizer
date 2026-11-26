#!/usr/bin/env python3
# Metric: dhw_coast_hours with to_temp >= from_temp (guard off), default UA and UA == 0.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g42/probes/probe_eb094b1749a24474.py
# Expected: default UA: equal (clip -> 0.0); with ua_kw_per_c==0 baseline 0.0 vs mutant 168.0 => moved. Reads RESULT <metric>_baseline / _mutant per metric, then RESULT metrics_moved=<n>.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g42 (see wave/D3-g42/MACHINE.txt); exact arithmetic, no timing.
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalModel.dhw_coast_hours, line 3640.
# Perturbation: production line 3640 `to_temp >= from_temp` -> `False` (key eb094b1749a24474), applied to a scratch copy of custom_components (never the gate tree);
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
    import dataclasses
    p=ThermalParameters(); m=ThermalModel(p); out=[]
    for f,t in ((50,55),(50,50),(55,60)):
        out.append((f"default_ua_{f}_{t}",repr(m.dhw_coast_hours(f,t))))
    ua0=_zero_ua(p)
    m0=ThermalModel(ua0)
    for f,t in ((50,55),(50,50)):
        out.append((f"ua0_{f}_{t}",repr(m0.dhw_coast_hours(f,t))))
    from custom_components.heatpump_optimizer import thermal_model as _tm
    out.append(("DHW_COOLING_RATE_MIN",_tm.DHW_COOLING_RATE_MIN))
    for cr in (0.0,-5.0,1e-12):
        pp=ThermalParameters(dhw_cooling_rate=cr)
        out.append((f"config_ua_cooling_rate_{cr}",repr(pp.dhw_tank_heat_loss_coefficient)))
    return out
if __name__ == "__main__":
    main("eb094b1749a24474", measure, __file__)
