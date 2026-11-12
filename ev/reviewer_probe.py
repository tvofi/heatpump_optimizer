"""Reviewer's probe (the reviewer's instrument, not the finder's): pure learner only."""
import sys
from datetime import datetime, timedelta, timezone
sys.path[:0] = ["tests/hastub", "tests", "custom_components"]
from heatpump_optimizer import duty_switch as ds

UTC = timezone.utc
t0 = datetime(2026, 1, 1, 12, tzinfo=UTC)

# 1. span after the evidence aged away: does one day's five stops latch on?
d = ds.Direction()
d.book(t0, True, 100.0)
far = t0 + timedelta(days=365)
d.decay(far)
print("RESULT span_probe aged: n=%.6g usable=%s span=%d" % (d.n, d.usable, d.span_days))
for i in range(5):
    d.book(far + timedelta(minutes=10 * i), True, 100.0)
print("RESULT span_probe after 5 stops on ONE day a year later: n=%.4f p=%.2f span_days=%d usable=%s"
      % (d.n, d.p, d.span_days, d.usable))
c = ds.Direction()
for i in range(5):
    c.book(far + timedelta(minutes=10 * i), True, 100.0)
print("RESULT span_probe control, fresh learner, same 5 stops on one day: span_days=%d usable=%s" % (c.span_days, c.usable))

# 2. how often the published attributes change with no new observation
L = ds.DutySwitchLearner()
for name in ds.DIRECTIONS:
    for i in range(20):
        L.directions[name].book(t0 + timedelta(hours=i * 3), i % 2 == 0, 300.0)
start = t0 + timedelta(days=3)
prev, changes = None, 0
for m in range(24 * 60):
    pub = L.published(start + timedelta(minutes=m))
    if pub != prev:
        changes += 1
        prev = pub
print("RESULT attr_churn: %d distinct published dicts over 24 h of one-minute reads, no new episode (n about 20 per direction)" % changes)
E0 = ds.DutySwitchLearner()
print("RESULT attr_churn control, empty learner: published=%r" % E0.published(start))

# 3. the same span probe with a sixth stop (five on one day decay to n just under 5)
def six(first):
    d = ds.Direction()
    if first:
        d.book(t0, True, 100.0); d.decay(far)
    for i in range(6):
        d.book(far + timedelta(minutes=10 * i), True, 100.0)
    return d
a, b = six(True), six(False)
print("RESULT span_probe6 one year-old episode (weight %.3g) then 6 stops on one day: n=%.4f span_days=%d usable=%s" % (1.4e-8, a.n, a.span_days, a.usable))
print("RESULT span_probe6 control, fresh learner, the same 6 stops on one day: n=%.4f span_days=%d usable=%s" % (b.n, b.span_days, b.usable))
# 4. five stops over two days, an hour apart each: n at the fifth
e = ds.Direction()
for i in range(5):
    e.book(t0 + timedelta(hours=10 * i), True, 100.0)
print("RESULT fifth_episode five stops ten hours apart over two days: n=%.4f span_days=%d usable=%s" % (e.n, e.span_days, e.usable))
# 5. the heated gate on a room-unit set-point
ctx = ds.SwitchContext(inlet_c=30.0, water_setpoint_c=None, source_leg_s=14.0)
print("RESULT heated_room_unit inlet 30.0, set-point 21.0 (room units), 14 s leg: heated=%s" % ds._heated("dhw_space", ctx))
ctx = ds.SwitchContext(inlet_c=30.0, water_setpoint_c=32.0, source_leg_s=14.0)
print("RESULT heated_room_unit control, set-point 32.0 (water units): heated=%s" % ds._heated("dhw_space", ctx))
# 6. round 3: a kept-only direction (the reporting install's space->dhw rows) keeps its days
g = ds.Direction()
for i in range(3):
    g.book(t0 + timedelta(hours=i), False, None)
moved = [g.decay(t0 + timedelta(hours=3, minutes=m)) for m in (1, 2)]
print("RESULT kept_only three kept episodes, then two passes: k=%.2f n=%.2f span_days=%d decay_reports=%s" % (g.k, g.n, g.span_days, moved))
