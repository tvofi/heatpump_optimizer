"""V2 (independent) harness for D1-s2-04.

Metric (one line): per cycle-path callee, over 3 async_refresh cycles in which
the callee raises every call, the number of log records at WARNING or above
from ANY logger (not keyed on the message text) plus repair issues created,
minus the same count in a no-fault control run; a real-trigger arm makes
_async_watch_learning_drift fail without injection (snapshot ring loaded
with a tz-naive taken_at, D1-s1-01's leaf) and counts the same.
Count key: records reaching a root handler at NOTSET; _create_issue calls;
last_update_success from the production DataUpdateCoordinator refresh.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/u1_guards.py
Expected: extra_visible=0 for all 5 injected sites and for the real-trigger arm; cycles_ok 3/3 (+-0).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")
import asyncio, copy, logging, sys, time
from datetime import timedelta
from unittest import mock
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
sys.path.insert(0, "tools/audit/round9/D1/s2")
_p0, _t0 = time.process_time(), time.thread_time()
from harness import FakeEntry, FakeHass  # noqa
from homeassistant.util import dt as dt_util  # noqa
from heatpump_optimizer import coordinator as cm  # noqa
from lifecycle import CFG, _states  # noqa

HC = cm.HeatPumpOptimizerCoordinator
SITES = ["_command_frequency", "_async_drive_pumps", "_async_watch_learning_drift",
         "_maybe_run_fuse_advisor", "_maybe_refresh_price_tile"]


class Rec(logging.Handler):
    def __init__(self):
        super().__init__(logging.NOTSET); self.n = 0

    def emit(self, r):
        if r.levelno >= logging.WARNING:
            self.n += 1


def cycles(site, cached, real_trigger=False):
    hass = FakeHass(_states())
    c = HC(hass, FakeEntry(data=dict(CFG)))
    calls = {"n": 0}
    issues = []

    async def fake_opt(*a, **k):
        return copy.deepcopy(cached)

    async def boom(self, *a, **k):
        calls["n"] += 1
        raise RuntimeError("u1 fault")
    ps = [mock.patch.object(cm, "_await_optimize", fake_opt),
          mock.patch.object(cm, "_create_issue", lambda *a, **k: issues.append(1))]
    if site and not real_trigger:
        ps.append(mock.patch.object(HC, site, boom))
    for p in ps:
        p.start()
    root = logging.getLogger()
    rec = Rec(); root.addHandler(rec); old = root.level; root.setLevel(logging.NOTSET)
    ok = 0
    try:
        if real_trigger:
            past = (dt_util.now() - timedelta(days=9)).replace(tzinfo=None).isoformat()
            asyncio.run(c._snapshot_store.async_save({"snapshots": [{"taken_at": past, "healthy": True,
                        "alarmed_at_capture": False, "accuracy": {}, "learners": {}}]}))
            asyncio.run(c._async_load_snapshots())
            orig = HC._async_watch_learning_drift

            async def spy(self):
                calls["n"] += 1
                try:
                    return await orig(self)
                except Exception:
                    calls["raised"] = calls.get("raised", 0) + 1
                    raise
            ps.append(mock.patch.object(HC, "_async_watch_learning_drift", spy)); ps[-1].start()
        for _ in range(3):
            asyncio.run(c.async_refresh())
            ok += int(c.last_update_success)
    finally:
        for p in ps:
            p.stop()
        root.removeHandler(rec); root.setLevel(old)
    extra = {}
    if real_trigger:
        extra["snap_taken"] = len(c._snapshot_ring.snapshots) - 1
        extra["raised"] = calls.get("raised", 0)
    return rec.n + len(issues), ok, calls["n"], extra


def main():
    hass = FakeHass(_states())
    c = HC(hass, FakeEntry(data=dict(CFG)))
    asyncio.run(c._async_update_data())
    cached = copy.deepcopy(c._optimization_result)
    cm._shutdown_process_pool()
    base, ok, _, _ = cycles(None, cached)
    print(f"RESULT control_visible={base} records_over_3_cycles cycles_ok={ok}/3")
    silent = 0
    for s in SITES:
        v, ok, n, _ = cycles(s, cached)
        print(f"RESULT inj_{s}_extra_visible={v - base} records (callee_calls={n}, cycles_ok={ok}/3)")
        silent += int(n > 0 and v - base <= 0)
    print(f"RESULT silent_injected_sites={silent} of {len(SITES)}")
    v, ok, n, ex = cycles("_async_watch_learning_drift", cached, real_trigger=True)
    print(f"RESULT real_naive_snapshot_extra_visible={v - base} records (heartbeat_calls={n}, cycles_ok={ok}/3, "
          f"heartbeat_raised={ex.get('raised')}, snapshots_taken={ex.get('snap_taken')})")


main()
p, t = time.process_time() - _p0, time.thread_time() - _t0
print(f"RESULT thread_factor={p / t if t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    print("RESULT swapins=" + [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1])
except Exception:
    print("RESULT swapins=na")
