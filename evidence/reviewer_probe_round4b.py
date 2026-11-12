"""Reviewer's probe (round 4), r4v_tracker_settled_any: a mode write while the running signal is unknown,
then the signal returns reading stopped inside the window.
    PYTHONPATH=tests/hastub:custom_components python3 reviewer_probe_round4b.py"""
import asyncio
from datetime import datetime, timedelta, timezone
from heatpump_optimizer import duty_switch as ds, wear
t0 = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)
class Store:
    async def async_load(self): return None
    async def async_save(self, data): pass
(old, new), direction = next((k, v) for k, v in ds._DIRECTION.items() if v == "dhw_space")
def run(first_reading):
    rec = ds._Record(None, Store()); rec.loaded = True
    reading = [first_reading]
    rec.reader = lambda: reading[0]
    ds.note_signal(rec, t0 - timedelta(minutes=10))
    asyncio.run(ds.note_pass(rec, t0 - timedelta(minutes=5), ds.SwitchContext()))
    settled = rec.tracker.settled
    ctx = ds.SwitchContext(mode_written_at=t0, last_write_at=t0, source_leg_s=3600.0, target_demand=True, plan_stays=True)
    ds.note_mode_write(rec, t0, old, new, ctx)
    opened = rec.learner.episode is not None
    reading[0] = (0.0, None, None, True)            # the signal reads stopped 60 s after the write
    ds.note_signal(rec, t0 + timedelta(seconds=60))
    for s in (61, 120, 181, 240):
        asyncio.run(ds.note_pass(rec, t0 + timedelta(seconds=s), ctx))
    reading[0] = (50.0, None, None, True)           # and running again 300 s after the write
    ds.note_signal(rec, t0 + timedelta(seconds=300))
    for s in (301, 331, 400):
        asyncio.run(ds.note_pass(rec, t0 + timedelta(seconds=s), ctx))
    d = rec.learner.directions[direction]
    return f"settled_at_write={settled} episode_opened={opened} stopped={d.stopped} kept={d.kept} void={d.void}"
print("RESULT unknown_signal_at_write", run((None, None, None, True)))
print("RESULT unknown_signal_control(running at write)", run((50.0, None, None, True)))
