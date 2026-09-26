"""V2 (independent) for D1-s2-55: make the solve worker genuinely fail to start (no injected
exception) and count plans and fallback notices.

Metric: per spawn cell, over 3 cycles of async_run_optimization, cycles returning None (a plan
published) and solve_worker_fallback issues raised. Cells (real Popen failures, produced by pointing
coordinator.sys.executable -- the interpreter _ensure_worker launches -- at):
  missing: a path that does not exist (Popen raises FileNotFoundError, an OSError);
  noexec: a temp file without the execute bit (Popen raises PermissionError, an OSError);
  exits: /bin/false, which starts and exits at once (the #511 transport failure, the control:
         _run_in_process converts it to ProcessWorkerUnavailable).
Count key: the coordinator's return value and hass.issues entries the production
_note_worker_fallback writes.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/leads_worker_spawn_real.py
Expected: missing planned=0 of 3 notice=0; noexec planned=0 of 3 notice=0; exits planned=3 of 3
notice=1 (exact). Perturbation --wrap: _ensure_worker re-raises OSError as ProcessWorkerUnavailable
(in memory) -> missing and noexec match exits.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import leads_rig as rig  # noqa: E402  (thread pin inside)
import asyncio
import tempfile
from heatpump_optimizer import coordinator as cm

WRAP = "--wrap" in sys.argv
TMP = tempfile.mkdtemp()
NOEXEC = os.path.join(TMP, "python-noexec")
with open(NOEXEC, "w") as fh:
    fh.write("#!/bin/sh\nexit 0\n")
os.chmod(NOEXEC, 0o644)
CELLS = {"missing": os.path.join(TMP, "no-such-python"), "noexec": NOEXEC, "exits": "/bin/false"}
_real_exe = cm.sys.executable
_ensure = cm._ensure_worker


def wrapped():
    try:
        return _ensure()
    except OSError as err:
        raise cm.ProcessWorkerUnavailable(f"cannot start worker: {err}") from err


def cell(exe):
    rig.freeze()
    hass, entry, coord = rig.coordinator()
    cm._shutdown_process_pool()
    cm._WORKER_FALLBACK_CAUSE = None  # the notice is raised once per distinct cause; reset per cell
    cm.sys.executable = exe
    if WRAP:
        cm._ensure_worker = wrapped
    planned = 0
    try:
        async def go():
            nonlocal planned
            await coord._update_current_state()
            for _ in range(3):
                planned += (await coord.async_run_optimization()) is None
        asyncio.run(go())
    finally:
        cm.sys.executable = _real_exe
        cm._ensure_worker = _ensure
        cm._shutdown_process_pool()
    notice = sum(1 for i in getattr(hass, "issues", []) if i[1] == "solve_worker_fallback")
    return planned, notice


for name, exe in CELLS.items():
    p, n = cell(exe)
    print(f"RESULT {name}: planned={p} of_3 fallback_notice={n}")
print(f"RESULT wrapped={int(WRAP)}")
rig.tail()
