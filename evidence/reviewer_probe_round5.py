"""Reviewer's probe, round 5: a mode write while the compressor is read STOPPED (settled False).

Run from a tree root with PYTHONPATH=tests/hastub:<root>. Prints what dhw_space books when the
write lands with the running signal settled stopped and it stays stopped through the window, and the
control with the compressor read running at the write and kept running."""
import asyncio, sys
from datetime import datetime, timedelta, timezone
from custom_components.heatpump_optimizer import duty_switch as ds, pump_mode as pm

T0 = datetime(2026, 1, 10, 0, 0, tzinfo=timezone.utc)

class Saves:
    async def async_load(self): return None
    async def async_save(self, data): pass

def ctx(at):
    return ds.SwitchContext(mode_written_at=at, last_write_at=at, inlet_c=45.0, water_setpoint_c=35.0,
                            source_leg_s=600.0, target_demand=True, plan_stays=True)

def drive(hz_at_write, later=()):
    rec = ds._Record(None, Saves()); rec.loaded = True
    hz = [hz_at_write]
    rec.reader = lambda: (hz[0], None, None, True)
    ds.note_signal(rec, T0 - timedelta(minutes=10))
    asyncio.run(ds.note_pass(rec, T0 - timedelta(minutes=5), ctx(None)))
    settled = rec.tracker.settled
    ds.note_mode_write(rec, T0, pm.MODE_DHW, pm.MODE_HEAT, ctx(T0))
    opened = rec.learner.episode is not None
    for mark in range(15, 601, 15):
        when = T0 + timedelta(seconds=mark)
        for at, value in later:
            if at == mark:
                hz[0] = value; ds.note_signal(rec, when)
        asyncio.run(ds.note_pass(rec, when, ctx(T0)))
    d = rec.learner.directions["dhw_space"]
    return dict(settled_at_write=settled, opened=opened, stopped=d.stopped, kept=d.kept, void=d.void,
                k=round(d.k, 3), n=round(d.n, 3), published=rec.learner.published(T0 + timedelta(seconds=600)))

print("stopped at the write, stays stopped :", drive(0.0))
print("stopped at the write, starts at 60 s:", drive(0.0, [(60, 50.0)]))
print("control: running at the write, kept :", drive(50.0))
