"""Verifier V2 for D1-s2-03. Metric: WARNING records from coordinator._weather_series
over 4 direct calls with _weather_forecast=[] vs 4 with one row (unbound call).
Command: PYTHONPATH=tests/hastub:custom_components python3 dev/audit/rounds/round10/D1/v_s2_weather_own.py"""
import logging
from types import SimpleNamespace
from homeassistant.util import dt as dt_util
from heatpump_optimizer import coordinator as cm
class H(logging.Handler):
    n = 0
    def emit(self, r):
        if r.levelno == logging.WARNING and "No weather forecast" in r.getMessage(): H.n += 1
cm._LOGGER.addHandler(H())
f = cm.HeatPumpOptimizerCoordinator._weather_series
o = SimpleNamespace(_weather_forecast=[], _current_state=SimpleNamespace(outdoor_temperature=3.0), _solar_radiation=0.0)
for _ in range(4): f(o, 8, dt_util.now().replace(hour=0, minute=0, second=0, microsecond=0), 0)
print(f"RESULT empty_warnings={H.n} of 4"); H.n = 0
o._weather_forecast = [{"datetime": dt_util.now().isoformat(), "temperature": 2.0}]
for _ in range(4):
    try: f(o, 8, dt_util.now().replace(hour=0, minute=0, second=0, microsecond=0), 0)
    except Exception as e: print("ctrl err", type(e).__name__); break
print(f"RESULT control_warnings={H.n}")
