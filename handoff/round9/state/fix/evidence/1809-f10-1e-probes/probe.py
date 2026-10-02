import asyncio, sys
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from zoneinfo import ZoneInfo
sys.path.insert(0, "tests")
from harness import FakeEntry, FakeHass, FakeState
import numpy as np
from homeassistant.util import dt as dt_util
from heatpump_optimizer import const
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
from heatpump_optimizer import pump_arbiter, power_guard, open_meteo
S = ZoneInfo("Europe/Stockholm")
# autumn fold, true 60 min apart, wall 0 apart
LAST = datetime(2026,10,25,2,55,tzinfo=S)            # fold 0, 00:55Z
NOW  = datetime(2026,10,25,2,55,tzinfo=S,fold=1)     # 01:55Z
assert (NOW.astimezone(timezone.utc)-LAST.astimezone(timezone.utc)).total_seconds()==3600
print("wall diff", (NOW-LAST).total_seconds())
g = power_guard.GuardState(); g._last_event = LAST
print("throttled (want False):", g.throttled(NOW))
om = object.__new__(open_meteo.OpenMeteoSolar); om._last_attempt = LAST
print("should_refresh (want True):", om._should_refresh(NOW, False))
# retry stamp
held = pump_arbiter.ArbiterState() if hasattr(pump_arbiter,"ArbiterState") else None
pump_arbiter.setpoint_check = SimpleNamespace(create_issue=lambda *a,**k:None)
coord = SimpleNamespace(hass=None, _config={})
try:
    pump_arbiter._not_held(coord, held, "mode", "x", LAST)
    print("retry label", held.retry["mode"].isoformat(), "true minutes", (held.retry["mode"].astimezone(timezone.utc)-LAST.astimezone(timezone.utc)).total_seconds()/60)
except Exception as e:
    print("not_held err", repr(e))
