"""Shared rig for the D1-s2 round-11 harnesses (store fuzz, staleness).

Not a harness itself: imported by store_fuzz.py and staleness.py in this
directory. It builds a coordinator on a REAL asyncio loop whose
``async_create_task`` schedules (FakeHass closes coroutines), so the
constructor's spawned store loads and every task a cycle spawns actually run,
and their exceptions are collected. ``_await_optimize`` is replaced by an
in-process memo (the first call solves for real, later calls reuse that plan)
unless ``real_solve=True``: the store and staleness steps measure the loop-side
cycle, and a process-pool solve per mutant costs ~9 s wall on this box.

Run from the repository root with PYTHONPATH=tests/hastub.
"""
from __future__ import annotations

import os

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

import asyncio
import logging
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
for p in (ROOT / "tests", ROOT / "tests" / "hastub", ROOT / "custom_components"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from harness import FakeHass, FakeEntry, FakeState  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import coordinator as coord_mod  # noqa: E402
from heatpump_optimizer import store as store_mod  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from homeassistant.helpers import storage as storage_stub  # noqa: E402
from homeassistant.util import dt as dtu  # noqa: E402

ENTRY_ID = "test_entry"
T0 = datetime(2026, 1, 20, 12, 0, tzinfo=timezone.utc)


class SchedHass(FakeHass):
    """FakeHass whose async_create_task schedules on the running loop."""

    def __init__(self, states=None):
        super().__init__(states)
        self.tasks: list[asyncio.Task] = []

    def async_create_task(self, coro, *a, **k):
        t = asyncio.get_running_loop().create_task(coro)
        self.tasks.append(t)
        return t

    def async_create_background_task(self, coro, *a, **k):
        return self.async_create_task(coro)


class Capture(logging.Handler):
    def __init__(self):
        super().__init__(logging.DEBUG)
        self.records: list[logging.LogRecord] = []

    def emit(self, record):
        self.records.append(record)


CAP = Capture()
_pkg_log = logging.getLogger("heatpump_optimizer")
_pkg_log.addHandler(CAP)
_pkg_log.setLevel(logging.DEBUG)
_pkg_log.propagate = False


def mark() -> int:
    return len(CAP.records)


def since(m: int, level=logging.WARNING):
    return [r for r in CAP.records[m:] if r.levelno >= level]


def template(r: logging.LogRecord) -> str:
    return f"{r.levelname}:{r.name}:{r.msg}"


# --- the solve: real once, memoised after --------------------------------
_MEMO: dict = {}


async def _memo_optimize(hass, optimizer, inputs):
    if "r" not in _MEMO:
        _MEMO["r"] = await hass.async_add_executor_job(coord_mod.optimize_in_process, optimizer, inputs)
    return _MEMO["r"]


async def _inproc_optimize(hass, optimizer, inputs):
    return await hass.async_add_executor_job(coord_mod.optimize_in_process, optimizer, inputs)


# --- best-effort step failures (repeats log at DEBUG, so count them here) --
FENCED: list[str] = []
_real_fence = coord_mod._best_effort_cycle_step


async def _counting_fence(step, message):
    try:
        out = step()
        if hasattr(out, "__await__"):
            await out
    except Exception as err:  # noqa: BLE001
        FENCED.append(f"{message} :: {type(err).__name__}: {err}")
        coord_mod._FENCED_CAUSES.add((message, f"{type(err).__name__}: {err}"))
        return None


def base_states(extra=None):
    st = {"sensor.indoor": FakeState("21.4"), "sensor.outdoor": FakeState("-3.0")}
    st.update(extra or {})
    return st


def base_config(extra=None):
    cfg = {
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
        const.CONF_DHW_TANK_VOLUME: 180.0,
    }
    cfg.update(extra or {})
    return cfg


def price_stub(coord, *, raise_after=None, counter=None):
    """Replace the Tibber fetch: 38 h of hourly prices around the clock."""
    async def _prices():
        if counter is not None:
            counter["n"] = counter.get("n", 0) + 1
            if raise_after is not None and counter["n"] > raise_after:
                raise RuntimeError("injected price fetch failure")
        s0 = dtu.now().replace(minute=0, second=0, microsecond=0)
        coord._prices = [
            {"total": round(0.6 + 0.5 * (h % 12) / 12, 4),
             "starts_at": (s0 + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
            for h in range(-2, 36)
        ]
    coord._fetch_tibber_prices = _prices


async def drain(hass: SchedHass, timeout=20.0):
    """Await every scheduled task; return the exceptions they raised."""
    excs = []
    deadline = time.monotonic() + timeout
    seen = set()
    while True:
        pending = [t for t in hass.tasks if not t.done()]
        if not pending:
            break
        if time.monotonic() > deadline:
            excs.append(f"TIMEOUT: {len(pending)} task(s) still pending")
            for t in pending:
                t.cancel()
            break
        await asyncio.wait(pending, timeout=1.0)
    for t in hass.tasks:
        if id(t) in seen or not t.done() or t.cancelled():
            continue
        seen.add(id(t))
        e = t.exception()
        if e is not None:
            excs.append(f"{type(e).__name__}: {e}")
    hass.tasks.clear()
    return excs


def reset_globals():
    coord_mod._FENCED_CAUSES.clear()
    store_mod._NEWER_ON_DISK.clear()
    FENCED.clear()


def patches(real_solve=False):
    return [
        mock.patch.object(coord_mod, "_await_optimize", _inproc_optimize if real_solve else _memo_optimize),
        mock.patch.object(coord_mod, "_best_effort_cycle_step", _counting_fence),
    ]


def load_avg():
    try:
        return os.getloadavg()[0]
    except OSError:
        return -1.0


def thread_factor(proc0, thr0):
    import time as _t
    p = _t.process_time() - proc0
    th = _t.thread_time() - thr0
    return p / th if th > 0 else 1.0


def swapins():
    try:
        import resource
        return resource.getrusage(resource.RUSAGE_SELF).ru_majflt
    except Exception:  # noqa: BLE001
        return 0


PRICE_CALLS = {"n": 0, "raise_from": None, "exc": None}


def _prices_now():
    s0 = dtu.now().replace(minute=0, second=0, microsecond=0)
    return [{"total": round(0.6 + 0.5 * (h % 12) / 12, 4),
             "starts_at": (s0 + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
            for h in range(-2, 36)]


async def _pull_prices(session, cfg, state):
    PRICE_CALLS["n"] += 1
    rf = PRICE_CALLS["raise_from"]
    if rf is not None and PRICE_CALLS["n"] >= rf:
        raise PRICE_CALLS["exc"] or RuntimeError("injected price fetch failure")
    return "ok", _prices_now()


def price_patches():
    """Patch below the real ``_fetch_tibber_prices`` (pull_prices + session), so its handling runs."""
    PRICE_CALLS.update(n=0, raise_from=None, exc=None)
    return [mock.patch.object(coord_mod, "pull_prices", _pull_prices),
            mock.patch.object(coord_mod, "async_get_clientsession", lambda hass: object())]
