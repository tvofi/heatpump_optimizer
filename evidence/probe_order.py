"""Reviewer's probe: a meter rise held one refresh, then the element latch read at the next refresh (no meter event)."""
import sys
from datetime import datetime, timedelta, timezone
from heatpump_optimizer import running_signal as rs, wear
T0 = datetime(2026, 11, 15, 10, 0, tzinfo=timezone.utc)
state = {"kw": 0.0, "element": False}
def reader():
    if state["element"]:
        return None, None, None, False
    return None, state["kw"], 0.3, False
sig = rs.Signal(None)
sig.reader = reader
c = wear.StartCounter(hold=wear.RiseHold()); c.restore(None)
starts = []
rs.subscribe(sig, lambda e: starts.extend(c.hear(*e)), lambda r: starts.extend(c.refresh(r)))
t = lambda s: T0 + timedelta(seconds=s)
rs.note(sig, t(0)); rs.confirm(sig, t(31))            # settled stop
state["kw"] = 2.0; rs.note(sig, t(100)); rs.confirm(sig, t(131))  # partial average confirmed as a rise
rs.refresh(sig, t(160))                               # first refresh reads it running
state["element"] = True; rs.refresh(sig, t(460))      # latch seen at the next refresh, no meter event
rs.confirm(sig, t(491))                               # no-class edge confirmed
print("RESULT starts=%d" % len(starts))
