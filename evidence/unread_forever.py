import sys, tempfile
from pathlib import Path
sys.path.insert(0, sys.argv[1] + "/tools/audit/seat")
import merge_train as mt
class Stop(Exception): pass
for label, run in (("listing unreadable forever", lambda argv, cwd=None, stdin=None: (1, "HTTP 401 Bad credentials")),):
    sl = []
    def sleep(s):
        sl.append(s)
        if len(sl) >= 2000: raise Stop()
    lines = []
    with tempfile.TemporaryDirectory() as d:
        t = mt.Train("o/r", Path(d), None, "", (), 1, run=run, sleep=sleep, log=lines.append, polls=3)
        try:
            t.review_settle(1, "f" * 40); print(label, "RETURNED after", len(sl), "sleeps,", int(sum(sl)), "s")
        except Stop:
            print(label, "STILL WAITING after", len(sl), "sleeps =", int(sum(sl)), "s simulated; cap", t.wait_cap_s(), "s; last:", lines[-1][:140])
