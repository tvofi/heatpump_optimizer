"""Reviewer's probe (not the finder's): wood_fuel._as_dt with an aware slot against naive plan stamps."""
import sys; sys.path[:0] = ["tests/hastub", "custom_components"]
from datetime import datetime, timezone
from heatpump_optimizer import wood_fuel as w
naive = [datetime(2026, 1, 15, 20, 0)]
aware = [datetime(2026, 1, 15, 20, 0, tzinfo=timezone.utc)]
slot = "2026-01-15T21:00:00+01:00"   # instant 20:00 UTC
print("RESULT as_dt aware-ref (control):", w._as_dt(slot, aware).astimezone(timezone.utc).isoformat())
print("RESULT as_dt naive-ref:", w._as_dt(slot, naive).isoformat(), "(naive plan stamps are UTC by drift.utc_instant)")
