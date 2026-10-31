#!/usr/bin/env python3
"""Instance probe: a report-on-change reading held unchanged for (limit + 1) min,
which is inside the source's legitimate quiet interval, must not read stale.
Exits 1 (FAIL) when production declares it stale -- i.e. on an instance.
COMMAND: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-N-staleness/probe.py <CONF_KEY|HUMIDITY>
"""
import sys
from datetime import datetime, timedelta, timezone
sys.path.insert(0, "custom_components")
from heatpump_optimizer import const, inputs

name = sys.argv[1]
if name == "HUMIDITY":
    from heatpump_optimizer import coordinator
    lim = coordinator.HUMIDITY_MAX_AGE_MINUTES
    fail = lim < 240.0  # age_of(state) > limit -> None: the mold floor drops
    print(f"{name}: limit={lim} quiet=240 -> {'FAIL stale' if fail else 'pass'}"); sys.exit(int(fail))
key = getattr(const, name)
lim = const.INPUT_MAX_AGE_MINUTES[key]
now = datetime(2026, 1, 1, 3, tzinfo=timezone.utc)
class S:
    state = "0"; attributes = {"unit_of_measurement": "W"}
    last_reported = last_updated = last_changed = now - timedelta(minutes=lim + 1)
class States:
    def get(self, eid): return S()
class H: states = States()
r = inputs.InputReader(H(), {key: "sensor.x"}, now=lambda: now).read(key)
fail = r.problem == "stale"
print(f"{name}: limit={lim} held {lim+1:.0f} min -> problem={r.problem} {'FAIL' if fail else 'pass'}")
sys.exit(int(fail))
