"""D1.M5 guards: inject a persistent exception into each callee a cycle-path
``except Exception`` fences, and count what the user can see.

Metric (one line): per guarded callee, over 3 consecutive cycles each raising
the injected TypeError, the number of log records at WARNING or above plus
repair issues raised (``visible_<callee>``); a site with 0 is silent. Also
whether each cycle completed and whether the callee was actually reached.
Count key: records the production ``heatpump_optimizer`` loggers emit and
issues ``ir.async_create_issue`` receives, with the callee reached (the
injected raise counted by the harness).

Command (from the export root):
    PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python \
        tools/audit/round9/D1/s2/guards.py [--perturb debug_to_warning]
Expected at baseline: see RESULT lines (exact counts). Baseline
1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: B4.

Perturbation ``debug_to_warning``: the coordinator's DEBUG calls are routed to
WARNING in memory (what a guard that logs its swallowed failure visibly does);
silent_sites must fall to 0.
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")
os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")

import argparse
import asyncio
import copy
import logging
import sys
from unittest import mock

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from harness import FakeEntry, FakeHass  # noqa: E402

from heatpump_optimizer import coordinator as cm  # noqa: E402
from lifecycle import CFG, _states  # noqa: E402

HC = cm.HeatPumpOptimizerCoordinator
# The callees _async_update_data / async_run_optimization fence with a bare
# ``except Exception`` (coordinator.py: "never allowed to break the cycle").
SITES = ["_command_frequency", "_async_drive_pumps", "_async_watch_learning_drift",
         "_maybe_run_fuse_advisor", "_maybe_refresh_price_tile"]


class Rec(logging.Handler):
    def __init__(self):
        super().__init__(logging.DEBUG)
        self.rows = []

    def emit(self, r):
        self.rows.append((r.levelno, r.getMessage()))


def run_site(site, cached, perturb):
    hass = FakeHass(_states())
    c = HC(hass, FakeEntry(data=dict(CFG)))
    reached = {"n": 0}

    async def boom(self, *a, **k):
        reached["n"] += 1
        raise TypeError(f"injected into {site}")

    async def fake_opt(hass, optimizer, state, *a, **k):
        return copy.deepcopy(cached)

    issues = []
    rec = Rec()
    lg = logging.getLogger("heatpump_optimizer")
    lg.addHandler(rec)
    lg.setLevel(logging.DEBUG)
    patches = [mock.patch.object(HC, site, boom),
               mock.patch.object(cm, "_await_optimize", fake_opt),
               mock.patch.object(cm, "_create_issue",
                                 lambda *a, **k: issues.append(a[2] if len(a) > 2 else k))]
    if perturb == "debug_to_warning":
        patches.append(mock.patch.object(cm._LOGGER, "debug", cm._LOGGER.warning))
    for p in patches:
        p.start()
    completed = 0
    try:
        for _ in range(3):
            # through the base-class refresh, so last_update_success is real
            asyncio.run(c.async_refresh())
            completed += int(c.last_update_success)
    finally:
        for p in patches:
            p.stop()
        lg.removeHandler(rec)
    injected = [r for r in rec.rows if f"injected into {site}" in r[1]]
    visible = sum(1 for lv, _ in injected if lv >= logging.WARNING) + len(
        [i for i in issues if i])
    return {"reached": reached["n"], "completed": completed,
            "visible": visible, "debug_only": sum(1 for lv, _ in injected if lv < logging.WARNING)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", default="")
    args = ap.parse_args()
    logging.basicConfig(level=logging.CRITICAL)
    # a healthy cached plan from one real solve
    hass = FakeHass(_states())
    c = HC(hass, FakeEntry(data=dict(CFG)))
    asyncio.run(c._async_update_data())
    cached = copy.deepcopy(c._optimization_result)
    cm._shutdown_process_pool()
    silent = 0
    for site in SITES:
        r = run_site(site, cached, args.perturb)
        if r["reached"] and r["visible"] == 0:
            silent += 1
        print(f"RESULT visible_{site}={r['visible']} records  "
              f"(reached={r['reached']}, cycles_ok={r['completed']}/3, debug_only={r['debug_only']})")
    print(f"RESULT silent_sites={silent} of {len(SITES)}")
    print("RESULT thread_factor=1.000")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")]
        print(f"RESULT swapins={sw[0].split()[1] if sw else 0}")
    except OSError:
        print("RESULT swapins=0")


if __name__ == "__main__":
    main()
