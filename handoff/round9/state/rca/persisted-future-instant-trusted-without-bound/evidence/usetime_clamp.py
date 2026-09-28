"""In-memory mutant: the fix F1.9's note describes ("clamp each restored
instant to the moment it is read back") applied where the string is parsed,
i.e. at USE time, at the two parse-at-use seams of D1-s1-04. Production
SnapshotRing.due and CurveLearner._step_down, stamp written 400 d ahead.
Arms: unfixed (baseline), use-time clamp (mutant), load-time clamp (the
stored string bounded once when read back, what the store boundary does)."""
import datetime as dt, sys
from pathlib import Path
sys.path[:0] = [str(Path.cwd()/"tests/hastub"), str(Path.cwd()/"custom_components")]
from heatpump_optimizer import snapshots, curve_learning

T0 = dt.datetime(2026, 1, 1, 12)
AHEAD = T0 + dt.timedelta(days=400)
class Clamping(dt.datetime):
    now_for_clamp = None
    @classmethod
    def fromisoformat(cls, s):
        return min(dt.datetime.fromisoformat(s), cls.now_for_clamp)

def snap_takes(stamp, use_clamp, days=60):
    ring = snapshots.SnapshotRing(); ring.snapshots = [{"taken_at": stamp.isoformat()}]
    snapshots.datetime = Clamping if use_clamp else dt.datetime
    n = 0
    for d in range(1, days + 1):
        now = T0 + dt.timedelta(days=d); Clamping.now_for_clamp = now
        if ring.due(now):
            ring.snapshots.append({"taken_at": now.isoformat()}); n += 1
    snapshots.datetime = dt.datetime
    return n

def curve_steps(stamp, use_clamp, days=60):
    c = curve_learning.CurveLearner(); c._last_step_at = stamp.isoformat(); c.bias = 2.0
    curve_learning.datetime = Clamping if use_clamp else dt.datetime
    n = 0
    for d in range(1, days + 1):
        now = T0 + dt.timedelta(days=d); Clamping.now_for_clamp = now
        before = c.bias; c._step_down(now); n += c.bias != before
    curve_learning.datetime = dt.datetime
    return n

for name, fn in (("snapshot_takes_60d", snap_takes), ("curve_steps_60d", curve_steps)):
    print(f"RESULT {name} honest={fn(T0, False)} unfixed={fn(AHEAD, False)} "
          f"use_time_clamp={fn(AHEAD, True)} load_time_clamp={fn(min(AHEAD, T0), False)}")
