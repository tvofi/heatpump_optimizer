"""V2 for D17-s2-02: call HeatPumpOptimizerCoordinator._weather_series unbound on a minimal
object, with a -5 C hourly forecast, and the measured outdoor reading at -25 / -3 / +10 C.
Metric: max-min over readings of the returned series' first 4 steps (the current hour).
Null: the same with an empty forecast.
Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D17/verify/v2_s2_02_weather.py
"""
import sys
from types import SimpleNamespace
from datetime import datetime, timezone, timedelta
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
from heatpump_optimizer import coordinator as co

class NS(SimpleNamespace):
    __hash__ = object.__hash__
    __eq__ = object.__eq__


fn = co.HeatPumpOptimizerCoordinator._weather_series
mid = datetime(2026, 1, 12, 0, 0, tzinfo=timezone.utc)


def series(reading, forecast):
    obj = NS(
        _weather_forecast=forecast, _solar_radiation_forecast=[], _solar_radiation=0.0,
        _current_state=SimpleNamespace(outdoor_temperature=reading),
        _held_logs={}, _log_held={}, hass=None,
    )
    try:
        return fn(obj, 96, mid, 0)[0][:4]
    except AttributeError as e:
        # log_held may want other state; stub generously
        raise


fc = [{"datetime": (mid + timedelta(hours=h)).isoformat(), "temperature": -5.0} for h in range(30)]
for label, forecast in (("forecast", fc), ("null_no_forecast", [])):
    vals = [series(r, forecast) for r in (-25.0, -3.0, 10.0)]
    spread = max(max(v) for v in vals) - min(min(v) for v in vals)
    print(f"RESULT s2_02_{label}_current_hour_spread_K={spread:.3f} first={[v[0] for v in vals]}")
