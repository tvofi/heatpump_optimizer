# Reviewer's adaptation of probe.py's HUMIDITY arm for a tree where humidity reads through InputReader.
import sys
from datetime import datetime, timedelta, timezone
sys.path.insert(0, "custom_components")
from heatpump_optimizer import const, inputs
key = const.CONF_INDOOR_HUMIDITY_ENTITY
now = datetime(2026, 1, 1, 3, tzinfo=timezone.utc)
def run(held, polled):
    class S:
        state = "55"; attributes = {"unit_of_measurement": "%"}
        last_updated = last_changed = now - timedelta(minutes=held + (3 if polled else 0))
        last_reported = now - timedelta(minutes=held)
    class States:
        def get(self, eid): return S()
    class H: states = States()
    r = inputs.InputReader(H(), {key: "sensor.h"}, now=lambda: now).read(key)
    return r.problem, r.value
for held, polled in [(241, False), (359, False), (361, False), (121, True), (119, True)]:
    print(f"RESULT humidity held={held} polled={polled} -> {run(held, polled)}")
