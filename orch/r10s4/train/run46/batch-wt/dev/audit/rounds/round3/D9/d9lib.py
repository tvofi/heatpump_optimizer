"""Shared scaffolding for the round-3 D9 harnesses (import-only, no RESULTs).

Not a harness: every harness in this directory imports this for the thread
pin, the path setup, the coordinator builder and the RESULT/telemetry
printers, so that the pin cannot be forgotten in one file and the numbers
stay comparable across files.

Run from the repository root with ``PYTHONPATH=tests/hastub``.
"""
from __future__ import annotations

import os

# The thread pin. Copied from tests/stress.py; must precede any numpy import,
# and this module is imported first by every harness here.
for _threads in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_threads, "1")

import datetime as _dt  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

ROOT = os.getcwd()
for _p in (
    os.path.join(ROOT, "tests"),
    os.path.join(ROOT, "tests", "hastub"),
    os.path.join(ROOT, "custom_components"),
):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np  # noqa: E402,F401

START = _dt.datetime(2026, 1, 15, 0, 0)


# --------------------------------------------------------------------------
# telemetry


def result(name, value, unit) -> None:
    text = f"{value:.6g}" if isinstance(value, float) else str(value)
    print(f"RESULT {name}={text} {unit}", flush=True)


def load1() -> float:
    try:
        return float(os.getloadavg()[0])
    except OSError:
        return float("nan")


def concurrent_stress() -> int:
    """`ps aux | grep -E "[s]tress\\.py|[t]ests/run\\.sh"`, counted."""
    try:
        out = subprocess.run(
            ["ps", "aux"], capture_output=True, text=True, timeout=20
        ).stdout
    except Exception:  # noqa: BLE001
        return -1
    n = 0
    for line in out.splitlines():
        if "stress.py" in line or "tests/run.sh" in line:
            if "grep" in line:
                continue
            n += 1
    return n


def swapins() -> int:
    """Cumulative machine swap-ins (``vm_stat``'s ``Swapins``), Darwin."""
    try:
        out = subprocess.run(
            ["vm_stat"], capture_output=True, text=True, timeout=20
        ).stdout
    except Exception:  # noqa: BLE001
        return -1
    for line in out.splitlines():
        if line.startswith("Swapins:"):
            return int(line.split(":")[1].strip().rstrip("."))
    return -1


def thread_factor() -> float:
    """process CPU / thread CPU over a fixed numpy workload, in this process."""
    a = np.random.default_rng(11).standard_normal((320, 320))
    p0, t0 = time.process_time(), time.thread_time()
    for _ in range(24):
        a @ a
    p1, t1 = time.process_time(), time.thread_time()
    dp, dt = p1 - p0, t1 - t0
    return (dp / dt) if dt > 0 else float("nan")


def telemetry(prefix: str = "") -> None:
    tf = thread_factor()
    result(f"{prefix}thread_factor", tf, "1")
    result(f"{prefix}load1", load1(), "1")
    result(f"{prefix}swapins", swapins(), "count")
    result(f"{prefix}concurrent_stress_procs", concurrent_stress(), "count")


# --------------------------------------------------------------------------
# a coordinator that has done one input cycle, with deterministic inputs


PRICE_PROFILES = {
    # the golden coordinator capture's own price shape
    "tibber_like": lambda h: round(0.6 + 0.5 * (h % 12) / 12.0, 4),
    # THE NULL CONTROL: a horizon with no price signal at all
    "flat": lambda h: 1.0,
}


def build_coordinator_cold(config_extra=None, *, profile="tibber_like", dhw=True):
    """A real HeatPumpOptimizerCoordinator with 48 h of deterministic inputs.

    Mirrors tests/entities.py:_honest_coordinator (one real input-read cycle)
    plus tests/golden.py:_capture_coordinator's injected 48 h of prices,
    weather and irradiance -- both are in the reuse table of
    tools/audit/README.md. Nothing here is a stub of a production symbol.
    """
    from harness import FakeEntry, FakeHass, FakeState
    from heatpump_optimizer import const
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
    from homeassistant.util import dt as dt_util

    dt_util.freeze(START)
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    config = {
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
        "tibber_token": "x",
        "weather_entity": "weather.home",
        "target_temperature": 21.0,
        "min_temperature": 17.0,
        "max_temperature": 23.0,
    }
    if dhw:
        config[const.CONF_DHW_TANK_VOLUME] = 180.0
    config.update(config_extra or {})
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=config))
    price = PRICE_PROFILES[profile]
    coord._prices = [
        {
            "total": price(h),
            "starts_at": (START + _dt.timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(48)
    ]
    coord._weather_forecast = [
        {
            "datetime": (START + _dt.timedelta(hours=h)).isoformat(),
            "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "humidity": 85.0,
        }
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [
        max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)
    ]
    return hass, coord


def build_coordinator(config_extra=None, *, profile="tibber_like", dhw=True):
    """``build_coordinator_cold`` plus the one real input-read cycle."""
    import asyncio

    hass, coord = build_coordinator_cold(config_extra, profile=profile, dhw=dhw)
    asyncio.run(coord._update_current_state())
    return hass, coord


async def abuild_coordinator(config_extra=None, *, profile="tibber_like", dhw=True):
    """The same, awaited: for a harness that already owns the event loop."""
    hass, coord = build_coordinator_cold(config_extra, profile=profile, dhw=dhw)
    await coord._update_current_state()
    return hass, coord


def inline_solves(monkey_target=None):
    """Force ``_await_optimize`` off the process worker and into this process.

    The solve's work is identical either way -- ``optimize_in_process`` is the
    same callable the child runs -- but a child interpreter's counters are
    invisible here, so every call-count harness runs the job in-process. This
    replaces coordinator._await_process ONLY; ``_await_optimize`` and
    ``optimize_in_process`` are the production symbols and are untouched.
    Returns a restore callable.
    """
    from heatpump_optimizer import coordinator as C

    original = C._await_process

    async def _inline(hass, fn, *args):
        return fn(*args)

    C._await_process = _inline

    def restore():
        C._await_process = original

    return restore


def break_worker():
    """Make the process route unavailable, so ``_await_optimize`` degrades.

    This is the #511 fallback exactly as production takes it: ``_await_optimize``
    catches ProcessWorkerUnavailable and re-submits through
    ``hass.async_add_executor_job``. Only ``_await_process`` is replaced; the
    fallback branch that runs is production's own. Returns a restore callable.
    """
    from heatpump_optimizer import coordinator as C

    original = C._await_process

    async def _broken(hass, fn, *args):
        raise C.ProcessWorkerUnavailable("D9 harness: process route disabled")

    C._await_process = _broken

    def restore():
        C._await_process = original

    return restore
