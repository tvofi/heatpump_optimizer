#!/usr/bin/env python3
# Metric: compute_solar_gain at 0 W/m2 and sub-zero, across parameter extremes.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g42/probes/probe_7684dd370eaae807.py
# Expected: gain(0)=0.0 in both arms for finite params (0*finite = 0.0) => equivalent-candidate; only inf area gives nan. Reads RESULT <metric>_baseline / _mutant per metric, then RESULT metrics_moved=<n>.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g42 (see wave/D3-g42/MACHINE.txt); exact arithmetic, no timing.
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalModel.compute_solar_gain, line 3517.
# Perturbation: production line 3517 `solar_radiation <= 0` -> `solar_radiation < 0` (key 7684dd370eaae807), applied to a scratch copy of custom_components (never the gate tree);
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
    import math
    for name,kw in (("default",{}),("big",dict(window_area=1e6)),("zero_area",dict(window_area=0.0)),("neg_scale",dict(solar_aperture_scale=-1.0)),("inf_area",dict(window_area=math.inf))):
        m=ThermalModel(ThermalParameters(**kw))
        for r in (0.0,-0.0,1e-300):
            out.append((f"gain_{name}_{r!r}",repr(m.compute_solar_gain(r))))
    return out
if __name__ == "__main__":
    main("7684dd370eaae807", measure, __file__)
