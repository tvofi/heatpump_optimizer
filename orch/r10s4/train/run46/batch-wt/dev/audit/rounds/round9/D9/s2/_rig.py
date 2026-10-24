"""Shared rig for the D9-s2 round-9 harnesses (not a harness itself).

Drives the REAL coordinator cycle (``HeatPumpOptimizerCoordinator._async_update_data``)
through ``tests/replay.py:run_fixture`` over the committed synthetic fixture,
optionally repeated for N days by shifting every timestamp in it (states and
the ISO datetimes inside attributes, e.g. the price sensor's raw_today), and
installs class-level hooks that record, per cycle:

  * process/thread CPU of the whole cycle (update + the entity sweep replay does);
  * CPU spent inside executor jobs (FakeHass.async_add_executor_job runs the job
    inline, so "loop-thread work" = cycle CPU - executor-job CPU);
  * entries into optimizer._multi_start_minimize, attributed to the coordinator
    path on the stack (main / simulate / diagnose / other);
  * the coordinator instance, so a harness can size its collections.

Root rule: resolves the repository root from the current working directory
(run from the export root, as the harness contract requires), NOT from __file__.
Writes only under a tempfile.mkdtemp() root.
"""
from __future__ import annotations

import os

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

import json
import re
import sys
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path.cwd()
for _p in (ROOT / "tests" / "hastub", ROOT / "tests", ROOT / "custom_components",
           ROOT / "tools" / "replay"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

FIXTURE = ROOT / "tests" / "replay" / "synthetic-dhw-only.json"
os.environ.setdefault(
    "HASTUB_TZ", json.loads(FIXTURE.read_text()).get("time_zone") or "UTC")
_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def _shift(node, delta: timedelta):
    if isinstance(node, str) and _ISO.match(node):
        try:
            return (datetime.fromisoformat(node) + delta).isoformat()
        except ValueError:
            return node
    if isinstance(node, list):
        return [_shift(v, delta) for v in node]
    if isinstance(node, dict):
        return {k: _shift(v, delta) for k, v in node.items()}
    return node


def fixture_for_days(days: int, options: dict | None = None) -> Path:
    """The committed one-day fixture, repeated ``days`` times end to end,
    with ``options`` merged into the config entry's options."""
    if days <= 1 and not options:
        return FIXTURE
    fx = json.loads(FIXTURE.read_text())
    if options:
        fx["entry"]["options"] = {**fx["entry"]["options"], **options}
    if days <= 1:
        tmp = Path(tempfile.mkdtemp(prefix="d9s2-fx-"))
        path = tmp / "synthetic-options.json"
        path.write_text(json.dumps(fx))
        return path
    start = datetime.fromisoformat(fx["window"]["start"])
    end = datetime.fromisoformat(fx["window"]["end"])
    span = end - start
    states = {}
    for eid, rows in fx["states"].items():
        out = []
        for d in range(days):
            delta = span * d
            for row in rows:
                upd, state, attrs, rep = row
                # The first row of a day only carries its attributes forward;
                # keep them explicit on every copy so a later day is self-contained.
                out.append([_shift(upd, delta), state,
                            _shift(attrs, delta) if attrs is not None else None,
                            _shift(rep, delta)])
        # rows of later days sorted after earlier ones by construction; drop
        # any copied row that precedes the previous copy's last row.
        out.sort(key=lambda r: datetime.fromisoformat(r[0]))
        states[eid] = out
    fx["states"] = states
    fx["window"]["end"] = (start + span * days).isoformat()
    tmp = Path(tempfile.mkdtemp(prefix="d9s2-fx-"))
    path = tmp / f"synthetic-{days}d.json"
    path.write_text(json.dumps(fx))
    return path


class Probe:
    def __init__(self) -> None:
        self.cycles: list[dict] = []
        self.coord = None
        self.cur: dict | None = None
        self.exec_depth = 0
        self.after_cycle = []  # callbacks(probe, coord, data)


PROBE = Probe()


def _path_of_stack() -> str:
    f = sys._getframe(2)
    names = []
    while f is not None:
        names.append(f.f_code.co_name)
        f = f.f_back
    for key, label in (("_maybe_refresh_price_tile", "price_tile"),
                       ("_maybe_run_fuse_advisor", "fuse_advisor"),
                       ("async_simulate", "simulate"),
                       ("async_diagnose_interval", "diagnose"),
                       ("async_run_optimization", "main")):
        if key in names:
            return label
    return "other"


def install(extra_update_wrap=None) -> None:
    from harness import FakeHass
    from heatpump_optimizer import coordinator as cm
    from heatpump_optimizer import optimizer as om

    real_init = cm.HeatPumpOptimizerCoordinator.__init__

    def init(self, *a, **k):
        real_init(self, *a, **k)
        PROBE.coord = self

    cm.HeatPumpOptimizerCoordinator.__init__ = init

    real_exec = FakeHass.async_add_executor_job

    async def add_exec(self, func, *args):
        if PROBE.cur is None or PROBE.exec_depth:
            return await real_exec(self, func, *args)
        PROBE.exec_depth += 1
        t0 = time.thread_time()
        try:
            return await real_exec(self, func, *args)
        finally:
            PROBE.exec_depth -= 1
            PROBE.cur["exec_cpu"] += time.thread_time() - t0
            PROBE.cur["exec_jobs"].append(getattr(func, "__name__", repr(func)))

    FakeHass.async_add_executor_job = add_exec

    real_msm = om._multi_start_minimize

    def msm(*a, **k):
        if PROBE.cur is not None:
            p = _path_of_stack()
            PROBE.cur["solves"][p] = PROBE.cur["solves"].get(p, 0) + 1
        return real_msm(*a, **k)

    om._multi_start_minimize = msm

    real_listeners = cm.HeatPumpOptimizerCoordinator.async_update_listeners

    def listeners(self, *a, **k):
        if PROBE.cur is not None:
            PROBE.cur["listener_updates"] += 1
        return real_listeners(self, *a, **k)

    cm.HeatPumpOptimizerCoordinator.async_update_listeners = listeners

    real_upd = cm.HeatPumpOptimizerCoordinator._async_update_data
    if extra_update_wrap is not None:
        real_upd = extra_update_wrap(real_upd)

    async def upd(self):
        PROBE.cur = {"exec_cpu": 0.0, "exec_jobs": [], "solves": {}, "listener_updates": 0}
        t0p, t0t = time.process_time(), time.thread_time()
        try:
            data = await real_upd(self)
        finally:
            PROBE.cur["proc_cpu"] = time.process_time() - t0p
            PROBE.cur["thread_cpu"] = time.thread_time() - t0t
            PROBE.cycles.append(PROBE.cur)
            cur, PROBE.cur = PROBE.cur, None
        for cb in PROBE.after_cycle:
            cb(PROBE, self, data)
        return data

    cm.HeatPumpOptimizerCoordinator._async_update_data = upd


def run(days: int = 1, step_minutes: int | None = None, inject: str | None = None,
        options: dict | None = None) -> dict:
    """One replay through replay.run_fixture with the hooks installed."""
    import replay

    real_sweep = replay.sweep

    def sweep(entities, action, errors, t):
        t0 = time.thread_time()
        out = real_sweep(entities, action, errors, t)
        if PROBE.cycles:
            PROBE.cycles[-1]["sweep_cpu"] = time.thread_time() - t0
            PROBE.cycles[-1]["records"] = out
            PROBE.cycles[-1]["entities"] = entities
        return out

    replay.sweep = sweep
    path = fixture_for_days(days, options)
    return replay.run_fixture(path, step_minutes, inject)


def load1() -> float:
    try:
        return os.getloadavg()[0]
    except OSError:
        return float("nan")


def swapins() -> int:
    try:
        for line in Path("/proc/vmstat").read_text().splitlines():
            if line.startswith("pswpin "):
                return int(line.split()[1])
    except OSError:
        pass
    return -1


def tail(thread_factor: float) -> None:
    print(f"RESULT thread_factor={thread_factor:.4f}")
    print(f"RESULT load1={load1():.2f}")
    print(f"RESULT swapins={swapins()}")
