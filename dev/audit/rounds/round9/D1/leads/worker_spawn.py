"""D1-s2-55: a solve worker that cannot START (Popen OSError) gets neither the in-process
fallback nor the solve_worker_fallback notice.

Metric: over 3 cycles with subprocess.Popen raising OSError(EAGAIN) in coordinator._ensure_worker,
count cycles that publish a fresh plan (async_run_optimization returns None) and whether the
'solve_worker_fallback' repair issue exists afterwards. Count key: the coordinator's return
value and hass.issues (the stub issue registry the production _note_worker_fallback writes).
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/leads/worker_spawn.py [--wrap] [--no-inject]
Expected: planned=0 of 3, fallback_notice=0 (exact). --wrap (perturbation: the spawn OSError is
re-raised as ProcessWorkerUnavailable, the class _await_optimize catches) -> planned=3, notice=1.
--no-inject (null control: a working spawn) -> planned=3, notice=0.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, machine B10 cloud container.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _rig  # noqa: E402
import asyncio, errno
from heatpump_optimizer import coordinator as cm

WRAP = "--wrap" in sys.argv
INJECT = "--no-inject" not in sys.argv
_popen = cm.subprocess.Popen
_ensure = cm._ensure_worker


def failing_popen(*a, **k):
    raise OSError(errno.EAGAIN, "Resource temporarily unavailable")


def wrapped_ensure():
    try:
        return _ensure()
    except OSError as err:
        raise cm.ProcessWorkerUnavailable(f"cannot start worker: {err}") from err


def run():
    _rig.freeze()
    hass, entry, coord = _rig.make_coord()
    cm._PROCESS_WORKER = None
    if INJECT:
        cm.subprocess.Popen = failing_popen
    if WRAP:
        cm._ensure_worker = wrapped_ensure
    planned = 0
    try:
        async def go():
            nonlocal planned
            await coord._update_current_state()
            for _ in range(3):
                ret = await coord.async_run_optimization()
                planned += ret is None
        asyncio.run(go())
    finally:
        cm.subprocess.Popen = _popen
        cm._ensure_worker = _ensure
        cm._shutdown_process_pool()
    notice = sum(1 for i in getattr(hass, "issues", []) if i[1] == "solve_worker_fallback")
    print(f"RESULT planned={planned} cycles_of_3")
    print(f"RESULT fallback_notice={notice} issues")
    print(f"RESULT solve_failures_counter={coord._solve_failures} count")


run()
_rig.tail()
