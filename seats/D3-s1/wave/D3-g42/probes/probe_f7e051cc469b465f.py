#!/usr/bin/env python3
# Metric: compute_solar_gain at negative irradiance (-10 W/m2).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g42/probes/probe_f7e051cc469b465f.py
# Expected: gain(-10): baseline 0.0, mutant negative => moved: candidate unless no caller can pass negative irradiance. Reads RESULT <metric>_baseline / _mutant per metric, then RESULT metrics_moved=<n>.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g42 (see wave/D3-g42/MACHINE.txt); exact arithmetic, no timing.
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalModel.compute_solar_gain, line 3517.
# Perturbation: production line 3517 `solar_radiation <= 0` -> `False` (key f7e051cc469b465f), applied to a scratch copy of custom_components (never the gate tree);
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
    m=ThermalModel(ThermalParameters())
    return [("gain_m10",repr(m.compute_solar_gain(-10.0))),("gain_0",repr(m.compute_solar_gain(0.0))),("gain_500",repr(m.compute_solar_gain(500.0)))]
if __name__ == "__main__":
    main("f7e051cc469b465f", measure, __file__)
