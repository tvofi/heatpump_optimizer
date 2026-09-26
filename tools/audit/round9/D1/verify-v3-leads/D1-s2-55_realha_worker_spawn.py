"""V3 verify of D1-s2-55: an OSError from Popen, driven through a REAL HeatPumpOptimizerCoordinator
on genuine Home Assistant 2026.2.3 (no tests/hastub). subprocess.Popen is stdlib and identical
under real HA; this checks the production coordinator's sequencing bug (the OSError-raising call
sits outside its own error-translating try) is unaffected by the HA provider.

Metric: of 3 cycles with subprocess.Popen raising OSError(EAGAIN) inside _ensure_worker, count
cycles whose async_run_optimization publishes a plan, plus the count of solve_worker_fallback
issues raised (the #511 in-process-fallback path).

Command (no tests/hastub on the path):
    PYTHONPATH=custom_components:tests /root/venvha/bin/python \
        tools/audit/round9/D1/verify-v3-leads/D1-s2-55_realha_worker_spawn.py
Expected: planned=0 of 3, fallback_notice=0 -- matching the stub's worker_spawn.py; --no-inject
control (real Popen succeeds) -> planned=3 of 3.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Home Assistant 2026.2.3 (venvha).
"""
import sys
sys.path.insert(0, "tools/audit/round9/D1/verify-v3-leads")
import _realha_rig as rig  # noqa: E402
import asyncio  # noqa: E402
import errno  # noqa: E402
import subprocess  # noqa: E402
from heatpump_optimizer import coordinator as coord_mod  # noqa: E402

INJECT = "--no-inject" not in sys.argv
_orig_popen = subprocess.Popen


def failing_popen(*a, **k):
    raise OSError(errno.EAGAIN, "Resource temporarily unavailable")


async def arm():
    stops = rig.freeze_now()
    try:
        coord = await rig.abuild_coordinator()
        notices = {"n": 0}
        orig_note = getattr(coord_mod, "_note_worker_fallback", None)
        if orig_note is not None:
            def spy_note(*a, **k):
                notices["n"] += 1
                return orig_note(*a, **k)
            coord_mod._note_worker_fallback = spy_note

        if INJECT:
            subprocess.Popen = failing_popen
        planned = 0
        try:
            for _ in range(3):
                await coord._update_current_state()
                ret = await coord.async_run_optimization()
                planned += coord._optimization_result is not None
        finally:
            subprocess.Popen = _orig_popen
            if orig_note is not None:
                coord_mod._note_worker_fallback = orig_note
        print(f"RESULT real_planned={planned} cycles_of_3")
        print(f"RESULT real_fallback_notice={notices['n']} issues")
    finally:
        for p in stops:
            p.stop()
        # release the real worker process this test may have spawned when
        # INJECT is off, so it does not linger.
        global _PW
        _PW = getattr(coord_mod, "_PROCESS_WORKER", None)
        if _PW is not None:
            try:
                _PW.terminate()
            except Exception:  # noqa: BLE001
                pass


asyncio.run(arm())
rig.tail()
