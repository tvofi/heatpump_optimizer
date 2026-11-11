"""Verifier V2 for D1-s2-02. Metric: of now offsets {+1,+2,+4,+24,+100}h past the
END of a 4-row hourly list (last row covers [T0+3h,T0+4h)), how many return the
last row's value from coordinator._current_spot_price (unbound call). Control:
offsets inside the list.
Command: PYTHONPATH=tests/hastub:custom_components python3 dev/audit/rounds/round10/D1/v_s2_price_own.py"""
from datetime import timedelta
from types import SimpleNamespace
from unittest import mock
from homeassistant.util import dt as dt_util
from heatpump_optimizer import coordinator as cm
T0 = dt_util.now().replace(minute=0, second=0, microsecond=0)
obj = SimpleNamespace(_prices=[{"starts_at": (T0 + timedelta(hours=i)).isoformat(), "value": v} for i, v in enumerate((1.0, 1.1, 1.2, 1.3))])
f = cm.HeatPumpOptimizerCoordinator._current_spot_price
def at(h):
    with mock.patch.object(cm.dt_util, "now", return_value=T0 + timedelta(hours=h)):
        return f(obj)
past = [at(h) for h in (5, 6, 8, 28, 104)]; inside = [at(h) for h in (0.5, 2.5)]
print("past", past, "inside", inside)
print(f"RESULT past_end_returns_last={sum(p == 1.3 for p in past)} of 5")
