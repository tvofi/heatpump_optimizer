#!/usr/bin/env python3
# Metric: dhw_coast_hours with a tiny UA (coast > 168 h).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g42/probes/probe_011b9e2e975b5e98.py
# Expected: ua=1e-6: baseline 168.0, mutant >168 => moved. Reads RESULT <metric>_baseline / _mutant per metric, then RESULT metrics_moved=<n>.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g42 (see wave/D3-g42/MACHINE.txt); exact arithmetic, no timing.
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalModel.dhw_coast_hours, line 3654.
# Perturbation: production line 3654 `np.clip((c_dhw/ua)*np.log(hot/cold),0.0,168.0)` -> `unclipped` (key 011b9e2e975b5e98), applied to a scratch copy of custom_components (never the gate tree);
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
    p=ThermalParameters(); out=[("default_h",repr(ThermalModel(p).dhw_coast_hours(60.0,40.0)))]
    for ua in (1e-3,1e-4,1e-6):
        out.append((f"ua_{ua}",repr(ThermalModel(_with_ua(p,ua)).dhw_coast_hours(60.0,40.0))))
    from custom_components.heatpump_optimizer import thermal_model as _tm
    out.append(("DHW_COOLING_RATE_MIN",_tm.DHW_COOLING_RATE_MIN))
    for cr in (0.0,-5.0,1e-12):
        pp=ThermalParameters(dhw_cooling_rate=cr)
        out.append((f"config_ua_cooling_rate_{cr}",repr(pp.dhw_tank_heat_loss_coefficient)))
    for cr in (0.0,0.05,0.2):
        pp=ThermalParameters(dhw_cooling_rate=cr)
        out.append((f"config_coast_hours_cooling_rate_{cr}",repr(ThermalModel(pp).dhw_coast_hours(60.0,40.0))))
    return out
if __name__ == "__main__":
    main("011b9e2e975b5e98", measure, __file__)
