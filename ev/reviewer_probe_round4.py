"""Reviewer's probe (round 4), run from the root of the tree it measures:
    PYTHONPATH=tests/hastub:custom_components python3 reviewer_probe_round4.py
Shows the two surviving mutants change what an install records. The reviewer's instrument, not the finder's."""
import asyncio, sys
from datetime import datetime, timedelta, timezone
from heatpump_optimizer import duty_switch as ds, wear

t0 = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)

# 1. kept-only direction: three kept episodes, then the pass one minute later.
d = ds.Direction()
for i in range(3):
    d.book(t0 + timedelta(seconds=i), False, None)
moved = d.decay(t0 + timedelta(minutes=1))
print(f"RESULT kept_only k={d.k:.2f} n={d.n:.2f} span_days={d.span_days} record_changed_on_pass={moved}")
# control: a stopped-only direction, where k equals n and the mutant cannot differ
c = ds.Direction()
for i in range(3):
    c.book(t0 + timedelta(seconds=i), True, 60.0)
print(f"RESULT kept_only_control(stopped_only) span_days={c.span_days} record_changed_on_pass={c.decay(t0 + timedelta(minutes=1))}")

# 2. a stop read inside the window, still in its debounce at the pass on the window's end.
class Store:
    async def async_load(self): return None
    async def async_save(self, data): pass

def run(pending_stop):
    rec = ds._Record(None, Store())
    rec.loaded = True
    rec.tracker.settled = True
    rec.learner.episode = ds.Episode(t0, "dhw_space")
    when = t0 + timedelta(seconds=ds.STOP_WINDOW_S)
    if pending_stop:
        rec.tracker.pending = (False, when - timedelta(seconds=wear.EDGE_DEBOUNCE_S / 2.0))
    ctx = ds.SwitchContext(mode_written_at=t0)
    asyncio.run(ds.note_pass(rec, when, ctx))
    first = (rec.learner.episode is not None, rec.learner.directions["dhw_space"].kept, rec.learner.directions["dhw_space"].stopped)
    # the debounce elapses; the confirmed stop reaches the learner on the next pass
    asyncio.run(ds.note_pass(rec, when + timedelta(seconds=wear.EDGE_DEBOUNCE_S), ctx))
    d = rec.learner.directions["dhw_space"]
    return first, (rec.learner.episode is not None, d.kept, d.stopped, None if rec.learner.episode is None else rec.learner.episode.stop_at is not None)

print(f"constants STOP_WINDOW_S={ds.STOP_WINDOW_S} EDGE_DEBOUNCE_S={wear.EDGE_DEBOUNCE_S}")
a, b = run(True)
print(f"RESULT pending_across_window at_window_end(open,kept,stopped)={a} after_debounce(open,kept,stopped,stop_attributed)={b}")
a, b = run(False)
print(f"RESULT pending_across_window_control(no stop read) at_window_end={a} after={b}")
