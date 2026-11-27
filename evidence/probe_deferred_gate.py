"""Reviewer's probe (not the finder's): is a deferred run's gate re-run alone while its sources are busy?
python3 probe_deferred_gate.py <dir holding sweep.py, prelude.py, sweep_selftest.py>"""
import sys
sys.path.insert(0, sys.argv[1])
import sweep  # noqa: E402
from sweep_selftest import World, run, v_run  # noqa: E402


def deferring(rid, created="1", attempt=1, started="5"):
    r = run(rid, created, attempt=attempt, started=started)
    r["units"] = [{"name": "prelude", "status": "completed", "conclusion": "failure", "completed_at": "1",
                   "steps": [{"name": sweep.DEFER_STEP, "conclusion": "failure"}]}]
    return r


busy = run(5, "1", status="in_progress", gstatus="in_progress", started="4")
w = World([deferring(1), busy, v_run()], 9)
rc, out = w.sweep()
print("POSTS", w.posts)
print(out)
