"""Reviewer's probe, round 6: a mode write while the compressor is settled STOPPED and a start is PENDING.

Run from a tree root with PYTHONPATH=tests/hastub:<root>. The signal settles stopped ten minutes before
the write; a start (50 Hz) is read `lead` seconds before the write. With lead under the 30 s debounce the
start is pending at the write; the control reads it 120 s before and a pass confirms it, so the compressor is
settled running at the write."""
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

def drive(lead, later=()):
    rec = ds._Record(None, Saves()); rec.loaded = True
    hz = [0.0]
    rec.reader = lambda: (hz[0], None, None, True)
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

print("start pending 10 s before the write, keeps running :", drive(10))
print("start pending 10 s before, zero again at 15 s (glitch):", drive(10, [(15, 0.0)]))
print("control: start confirmed 120 s before the write    :", drive(120))
