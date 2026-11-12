"""Reviewer's probe, round 7: a mode write while the tracker is UNSETTLED (settled is None) and an edge is PENDING.

Run from a tree root with PYTHONPATH=tests/hastub:<root>. Two ways into the state:
 fresh  - a record just loaded (a restart): the first reading, 50 Hz, is `lead` seconds before the write.
 unavail- the signal settled running, read unavailable (settled None once confirmed), then 50 Hz `lead` s before.
Control: the same first reading 120 s before the write, confirmed by a pass: settled running at the write."""
import asyncio
from datetime import datetime, timedelta, timezone
from custom_components.heatpump_optimizer import duty_switch as ds, pump_mode as pm

T0 = datetime(2026, 1, 10, 0, 0, tzinfo=timezone.utc)

class Saves:
    async def async_load(self): return None
    async def async_save(self, data): pass

def ctx(at):
    return ds.SwitchContext(mode_written_at=at, last_write_at=at, inlet_c=45.0, water_setpoint_c=35.0,
                            source_leg_s=600.0, target_demand=True, plan_stays=True)

def drive(lead, later=(), unavail=False):
    rec = ds._Record(None, Saves()); rec.loaded = True
    hz = [50.0]; ok = [True]
    rec.reader = lambda: (hz[0], None, None, ok[0])
    if unavail:
        ds.note_signal(rec, T0 - timedelta(minutes=20))
        asyncio.run(ds.note_pass(rec, T0 - timedelta(minutes=15), ctx(None)))
        hz[0] = None
        ds.note_signal(rec, T0 - timedelta(minutes=10))
        asyncio.run(ds.note_pass(rec, T0 - timedelta(minutes=5), ctx(None)))
        hz[0] = 50.0
    ds.note_signal(rec, T0 - timedelta(seconds=lead))
    if lead > 60:
        asyncio.run(ds.note_pass(rec, T0 - timedelta(seconds=lead - 45), ctx(None)))
    state = (rec.tracker.settled, rec.tracker.pending is not None)
    ds.note_mode_write(rec, T0, pm.MODE_DHW, pm.MODE_HEAT, ctx(T0))
    opened = rec.learner.episode is not None
    for mark in range(15, 601, 15):
        when = T0 + timedelta(seconds=mark)
        for at, value in later:
            if at == mark:
                hz[0] = value; ds.note_signal(rec, when)
        asyncio.run(ds.note_pass(rec, when, ctx(T0)))
    d = rec.learner.directions["dhw_space"]
    return dict(settled_pending_at_write=state, opened=opened, stopped=d.stopped, kept=d.kept, void=d.void,
                off_s=d.off_s, n=round(d.n, 3), published=rec.learner.published(T0 + timedelta(seconds=600)))

print("fresh record, first reading 50 Hz 10 s before the write :", drive(10))
print("fresh record, 50 Hz 10 s before, zero at 15 s (glitch)   :", drive(10, [(15, 0.0)]))
print("after unavailable, 50 Hz 10 s before the write           :", drive(10, unavail=True))
print("control: first reading 120 s before, confirmed           :", drive(120))
