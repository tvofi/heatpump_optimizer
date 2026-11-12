"""Reviewer's probe, round 5: which pass's context void-checks a confirmed stop.

A stop is read on the pass 60 s after the write and confirmed (30 s debounce) by the pass at 90 s, whose
context is clean; a defrost reads on from the pass at 105 s. Control: no defrost, restart read at 300 s.
Run from a tree root with PYTHONPATH=tests/hastub:<root>."""
import asyncio
from datetime import datetime, timedelta, timezone
from custom_components.heatpump_optimizer import duty_switch as ds, pump_mode as pm

T0 = datetime(2026, 1, 10, 0, 0, tzinfo=timezone.utc)

class Saves:
    async def async_load(self): return None
    async def async_save(self, data): pass

def ctx(at, **over):
    return ds.SwitchContext(**{"mode_written_at": at, "last_write_at": at, "inlet_c": 45.0,
                               "water_setpoint_c": 35.0, "source_leg_s": 600.0, "target_demand": True,
                               "plan_stays": True, **over})

def drive(readings, defrost_from=None):
    rec = ds._Record(None, Saves()); rec.loaded = True
    hz = [50.0]
    rec.reader = lambda: (hz[0], None, None, True)
    ds.note_signal(rec, T0 - timedelta(minutes=10))
    asyncio.run(ds.note_pass(rec, T0 - timedelta(minutes=5), ctx(None)))
    ds.note_mode_write(rec, T0, pm.MODE_DHW, pm.MODE_HEAT, ctx(T0))
    for mark in range(15, 601, 15):
        when = T0 + timedelta(seconds=mark)
        for at, value in readings:
            if at == mark:
                hz[0] = value; ds.note_signal(rec, when)
        asyncio.run(ds.note_pass(rec, when, ctx(T0, defrosting=defrost_from is not None and mark >= defrost_from)))
    d = rec.learner.directions["dhw_space"]
    return dict(stopped=d.stopped, kept=d.kept, void=d.void, censored=d.censored, off_s=d.off_s, k=d.k, n=d.n)

print("stop at 60 s, defrost from the pass at 105 s:", drive([(60, 0.0)], defrost_from=105))
print("control: stop at 60 s, restart at 300 s     :", drive([(60, 0.0), (300, 50.0)]))
