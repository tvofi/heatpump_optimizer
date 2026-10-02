from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from heatpump_optimizer.power_guard import GuardState
from heatpump_optimizer.manual_plan import ManualOverride
from heatpump_optimizer import accuracy
tz = ZoneInfo("Europe/Stockholm")
a = datetime(2026,3,29,1,59,58,tzinfo=tz); b = datetime(2026,3,29,3,0,3,tzinfo=tz)
g = GuardState(); g._last_event = a
print("RESULT spring throttled(true 5s) =", g.throttled(b))
# retry stamp: now 01:58 CET + 5 true min = 03:03 CEST
now = datetime(2026,3,29,1,58,tzinfo=tz)
r = accuracy.utc_shift(now, timedelta(minutes=5)) if hasattr(accuracy,'utc_shift') else now+timedelta(minutes=5)
print("RESULT spring retry stamp =", r.isoformat(), "| raw + =", (now+timedelta(minutes=5)).isoformat())
