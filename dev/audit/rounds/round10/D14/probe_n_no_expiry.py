"""N-no-expiry probes: each returns a value for a `now` 47 h past the series' last entry.

Property: an entry whose slot has ended is never "current". Each probe FAILS
(exit 1) while the seam publishes a finite value past the series' end.
Command: PYTHONPATH=.:tests/hastub python3 dev/audit/rounds/round10/D14/probe_n_no_expiry.py
"""
import math, sys, types
from datetime import datetime, timedelta, timezone
from custom_components.heatpump_optimizer import coordinator as cm

T0 = datetime(2026, 1, 15, 10, 0, tzinfo=timezone.utc)
NOW = T0 + timedelta(hours=50)
fails = 0
fc = [{"datetime": (T0 + timedelta(hours=k)).isoformat(), "temperature": -3.0 + k} for k in range(4)]
v = cm.forecast_outdoor_now(fc, NOW)
ok = v is None
print(f"PROBE forecast_outdoor_now past_end={v} {'pass' if ok else 'FAIL'}")
fails += not ok
plan = types.SimpleNamespace(timestamps=[T0 + timedelta(minutes=15 * k) for k in range(12)],
                             dhw_temp_trajectory=[50.0 - 0.5 * k for k in range(12)])
v = cm._open_loop_plan_value(plan, "dhw_temp_trajectory", NOW)
ok = v is None
print(f"PROBE _open_loop_plan_value past_end={v} {'pass' if ok else 'FAIL'}")
fails += not ok
# control: inside the series both return the covering entry
c1 = cm.forecast_outdoor_now(fc, T0 + timedelta(minutes=90))
c2 = cm._open_loop_plan_value(plan, "dhw_temp_trajectory", T0 + timedelta(minutes=20))
print(f"CONTROL covered forecast={c1} plan={c2}")
print(f"RESULT probe_failures={fails} count")
sys.exit(1 if fails else 0)
