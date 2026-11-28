# Seat-built probe (not the finder's): the _offset_change CMP_BOUND mutant hangs.
import sys, signal
from datetime import date, timedelta, datetime, time
from zoneinfo import ZoneInfo
sys.path.insert(0, "custom_components")
import heatpump_optimizer.dhw_schedule as ds
z = ZoneInfo("Europe/Stockholm"); on = date(2026, 10, 25)
print("head:", ds._offset_change(z, on))
src = open(ds.__file__).read().replace("while hi - lo > timedelta(seconds=1):", "while hi - lo >= timedelta(seconds=1):")
ns = {"__name__": "heatpump_optimizer.dhw_schedule_mut", "__package__": "heatpump_optimizer"}; exec(compile(src, "mut", "exec"), ns)
signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(TimeoutError()))
signal.alarm(5)
try:
    print("mutant:", ns["_offset_change"](z, on))
except TimeoutError:
    print("mutant: TIMEOUT after 5 s (loop does not terminate)")
