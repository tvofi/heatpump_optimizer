"""D1.M4 executor boundary: does any job handed across the executor boundary
share a mutable object with the live coordinator?

Metric (one line): per submission site, the number of distinct mutable
objects (list, dict, set, ndarray, or an instance with a __dict__) reachable
from the job's arguments (depth 4) that are also reachable from the live
coordinator (depth 3) at the moment of submission (``shared_<site>``).
Count key: object identity (``id``) of what the production call actually
passes to ``coordinator._run_in_process`` -- the real seam every solve,
what-if and diagnosis crosses; pickling happens later, inside the executor
thread, so a shared object the loop writes meanwhile is torn state.

Command (from the export root):
    PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python \
        tools/audit/round9/D1/s2/executor_share.py [--perturb no_snapshot_copy]
Expected at baseline: shared_solve=0, shared_simulate=0, shared_diagnose=0
(exact). Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: B4.

Perturbation ``no_snapshot_copy``: ``_solve_snapshot`` returns the live state
and an optimizer over the live params/config (the deepcopies removed, in
memory); shared_solve must move up.
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")
os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")

import argparse
import asyncio
import enum
import logging
import sys
from datetime import date, datetime, timedelta
from unittest import mock

import numpy as np

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from harness import FakeEntry, FakeHass  # noqa: E402

from heatpump_optimizer import coordinator as cm  # noqa: E402
from lifecycle import CFG, _states  # noqa: E402

_IMM = (int, float, complex, str, bytes, bool, type(None), datetime, date,
        timedelta, enum.Enum, type, np.generic)


def _mutable(o):
    if isinstance(o, _IMM) or callable(o) and not hasattr(o, "__dict__"):
        return False
    if isinstance(o, (tuple, frozenset)):
        return False
    return isinstance(o, (list, dict, set, np.ndarray)) or hasattr(o, "__dict__")


def _children(o):
    if isinstance(o, dict):
        return list(o.values())
    if isinstance(o, (list, tuple, set, frozenset)):
        return list(o)[:200]
    if isinstance(o, np.ndarray):
        return []
    d = getattr(o, "__dict__", None)
    if isinstance(d, dict):
        return list(d.values())
    slots = getattr(type(o), "__slots__", ())
    return [getattr(o, s, None) for s in slots]


def _named_children(o, name):
    if isinstance(o, dict):
        return [(v, f"{name}[{k!r}]") for k, v in list(o.items())]
    if isinstance(o, (list, tuple, set, frozenset)):
        return [(v, f"{name}[{i}]") for i, v in enumerate(list(o)[:200])]
    if isinstance(o, np.ndarray):
        return []
    d = getattr(o, "__dict__", None)
    if isinstance(d, dict):
        return [(v, f"{name}.{k}") for k, v in d.items()]
    slots = getattr(type(o), "__slots__", ())
    return [(getattr(o, s, None), f"{name}.{s}") for s in slots]


NAMES: dict[int, str] = {}


def reach(roots, depth, skip=(), names=None):
    seen: dict[int, object] = {}
    frontier = [(r, n) for r, n in (roots if names else [(r, "?") for r in roots])]
    for _ in range(depth):
        nxt = []
        for o, nm in frontier:
            if id(o) in seen or any(o is s for s in skip):
                continue
            if isinstance(o, (asyncio.AbstractEventLoop, logging.Logger)) or type(o).__module__.startswith(("asyncio", "concurrent", "harness", "homeassistant", "logging", "threading")):
                continue
            if _mutable(o):
                seen[id(o)] = o
                if names:
                    NAMES.setdefault(id(o), nm)
            nxt.extend(_named_children(o, nm))
        frontier = nxt
    return seen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", default="")
    args = ap.parse_args()
    logging.basicConfig(level=logging.CRITICAL)
    hass = FakeHass(_states())
    c = cm.HeatPumpOptimizerCoordinator(hass, FakeEntry(data=dict(CFG)))
    shared: dict[str, list[str]] = {}
    site = {"name": None}
    orig = cm._run_in_process

    def spy(fn, fargs):
        NAMES.clear()
        live = reach([(v, f"coord.{k}") for k, v in vars(c).items() if k not in ("hass",)], 3,
                     skip=(c.hass,), names=True)
        # the coordinator itself is never shipped (not picklable); its
        # members are what could be
        sent = reach([fargs], 5)
        both = [f"{type(o).__name__}@{NAMES.get(i, '?')}" for i, o in sent.items() if i in live]
        shared.setdefault(site["name"], []).extend(both)
        return orig(fn, fargs)

    patches = [mock.patch.object(cm, "_run_in_process", spy)]
    if args.perturb == "no_snapshot_copy":
        def snap(self):
            ctx = self._ctx
            return ctx._current_state, cm._warm_seeded(
                self, cm.HeatPumpOptimizer(cm.ThermalModel(ctx._thermal_params), ctx._opt_config))
        patches.append(mock.patch.object(cm.HeatPumpOptimizerCoordinator, "_solve_snapshot", snap))
    for p in patches:
        p.start()
    try:
        async def go():
            site["name"] = "solve"
            await c._async_update_data()
            await c._async_update_data()
            site["name"] = "simulate"
            await c.async_simulate({"target_temp": 20.0})
            site["name"] = "diagnose"
            diag = c._capture_diagnosis_inputs()
            c._last_interval_record = {
                "when": cm.dt_util.now().isoformat(timespec="seconds"),
                "state": diag["state"], "planned": diag["planned"], "dt_hours": 0.25,
                "realised": {"electrical_power": 1.0, "outdoor_temp": -3.0,
                             "solar_radiation": 0.0},
                "actual": 21.3,
            }
            await c.async_diagnose_interval()
        asyncio.run(go())
    finally:
        for p in patches:
            p.stop()
        cm._shutdown_process_pool()
    for name in ("solve", "simulate", "diagnose"):
        objs = shared.get(name, [])
        print(f"RESULT shared_{name}={len(objs)} objects  {sorted(set(objs))[:12]}")
    print(f"RESULT submissions_seen={len(shared)} sites")
    print("RESULT thread_factor=1.000")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")]
        print(f"RESULT swapins={sw[0].split()[1] if sw else 0}")
    except OSError:
        print("RESULT swapins=0")


if __name__ == "__main__":
    main()
