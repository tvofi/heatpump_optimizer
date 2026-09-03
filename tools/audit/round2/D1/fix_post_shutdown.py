"""D1-02 (#237) fix harness: actuations issued after async_shutdown returned.

Metric: ``switch.``/``mqtt.`` service calls and store writes issued by a
coordinator AFTER its own ``async_shutdown()`` coroutine returned, for one
reload that begins while a scheduled refresh is inside the executor.

Deliberately BLIND, per the panel's determinism ruling: the shutdown fires at
three fixed delays with no synchronisation to the solve thread and NO sleep
inside ``optimize``. The window is the whole solve, so no contrived pause is
needed to land in it. A `between` control fires the shutdown when no refresh
is in flight at all and must read 0.

Command (from the repository root):
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub \
  .venv/bin/python tools/audit/round2/D1/fix_post_shutdown.py

Expected on origin/main (4a7bdb6): 3 post-shutdown service calls and 2
post-shutdown store writes on every mid-solve trial; 0/0 on the `between`
control. The three calls are one switch command plus two mqtt.publish -- the
finding recorded `switch.turn_on`, this scenario's plan happens to command
`switch.turn_off` at the anchor instant; same path, same count. Expected after
the fix: 0/0 everywhere, with the control arm's uninterrupted cycle still
issuing its 3 calls and its store writes BEFORE the shutdown.

Instrumented symbols:
  custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator
  ._async_update_data / .async_run_optimization / .async_shutdown /
  ._apply_action.

Perturbation: the `no_switch` arm removes the switch entity from the config;
the post-shutdown service-call count must drop by exactly the one switch
command on the baseline tree (3 -> 2).

Baseline SHA: 4a7bdb696c9a01783afc7bdcb4a840de0f935dcb. Machine: 8-core M1.
The executor is a REAL ThreadPoolExecutor -- ``FakeHass.async_add_executor_job``
runs inline and would measure nothing about the executor boundary
(tools/audit/README.md).
"""
from __future__ import annotations

import os

for _var in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_var, "1")

import asyncio
import concurrent.futures
import sys
import time
from datetime import timedelta

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from homeassistant.helpers import storage as storage_stub  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402

from heatpump_optimizer import coordinator as coord_mod  # noqa: E402
from heatpump_optimizer.coordinator import (  # noqa: E402
    HeatPumpOptimizerCoordinator,
)
from heatpump_optimizer.const import MODE_AUTO  # noqa: E402


START = dt_util.parse_datetime("2025-01-15T00:00:00+01:00")

CONFIG = {
    "tibber_token": "tok",
    "heat_pump_switch_entity": "switch.heat_pump",
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
    "peak_guard_enabled": False,
}


class SeqServices:
    """Records every service call with a monotonically increasing sequence."""

    def __init__(self) -> None:
        self.calls: list[tuple[int, str, str]] = []
        self.seq = 0

    async def async_call(self, domain, service, data=None, **kwargs):
        self.seq += 1
        self.calls.append((self.seq, domain, service))
        return None

    def async_register(self, *a, **k):
        return None

    def async_remove(self, *a, **k):
        return None

    def async_services(self):
        return {}


class ExecHass(FakeHass):
    """A real event loop and a REAL thread pool behind async_add_executor_job."""

    def __init__(self, states=None) -> None:
        super().__init__(states)
        self.services = SeqServices()
        self.state_listeners = []
        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=2)

    def async_create_task(self, coro, name=None, eager_start=None):
        return asyncio.get_running_loop().create_task(coro)

    async def async_add_executor_job(self, func, *args):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.pool, func, *args)


async def _publish(*a, **k):
    """mqtt.async_publish, routed through the recording service registry."""
    hass = a[0]
    await hass.services.async_call("mqtt", "publish", {})


def _build(config: dict) -> tuple[ExecHass, HeatPumpOptimizerCoordinator]:
    hass = ExecHass(
        {
            "sensor.indoor": FakeState("21.0", unit="°C"),
            "sensor.outdoor": FakeState("-5.0", unit="°C"),
        }
    )
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=dict(config)))
    coord._mode = MODE_AUTO
    coord._skip_solve_once = False
    coord._prices = [
        {
            "total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
            "starts_at": (START + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(48)
    ]
    coord._weather_forecast = [
        {
            "datetime": (START + timedelta(hours=h)).isoformat(),
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

    # The four input steps are not what this measures: they are network and
    # sensor reads, and stubbing them keeps the injected forecast above.
    async def _noop():
        return None

    coord._update_current_state = _noop
    coord._fetch_tibber_prices = _noop
    coord._fetch_weather_forecast = _noop
    coord._fetch_solar_forecast = _noop
    coord._async_learn_price_shape = _noop
    return hass, coord


def _store_writes() -> int:
    return sum(storage_stub.SAVE_COUNTS.values())


async def _trial(delay: float, config: dict) -> dict:
    """One blind trial: start the scheduled refresh, wait `delay`, shut down."""
    hass, coord = _build(config)
    task = hass.async_create_task(coord._async_update_data())
    await asyncio.sleep(delay)

    calls_before = len(hass.services.calls)
    writes_before = _store_writes()
    await coord.async_shutdown()
    mark_calls = len(hass.services.calls)
    mark_writes = _store_writes()

    try:
        await asyncio.wait_for(asyncio.shield(task), timeout=60)
    except (asyncio.CancelledError, asyncio.TimeoutError):
        pass
    except Exception:  # noqa: BLE001
        pass
    await asyncio.sleep(0)

    post_calls = hass.services.calls[mark_calls:]
    # Idle threads left behind by twenty trials inflate time.process_time()
    # and with it the thread_factor the contract asks for.
    hass.pool.shutdown(wait=False)
    return {
        "in_flight_at_shutdown": int(not task.done() or task.cancelled()),
        "calls_before_shutdown": calls_before,
        "post_shutdown_service_calls": len(post_calls),
        "post_shutdown_actuations": sum(
            1 for _s, d, _srv in post_calls if d in ("switch", "mqtt")
        ),
        "post_shutdown_detail": "+".join(
            f"{d}.{s}" for _q, d, s in post_calls
        )
        or "none",
        "post_shutdown_store_writes": _store_writes() - mark_writes,
        "writes_before_shutdown": writes_before,
    }


async def _healthy_cycle(config: dict) -> dict:
    """NULL CONTROL: a cycle that is never interrupted still actuates and saves."""
    hass, coord = _build(config)
    before_writes = _store_writes()
    await coord._async_update_data()
    actuations = sum(
        1 for _s, d, _srv in hass.services.calls if d in ("switch", "mqtt")
    )
    detail = "+".join(f"{d}.{s}" for _q, d, s in hass.services.calls) or "none"
    writes = _store_writes() - before_writes
    # ... and a shutdown BETWEEN solves actuates nothing more.
    mark = len(hass.services.calls)
    mark_w = _store_writes()
    await coord.async_shutdown()
    await asyncio.sleep(0.05)
    hass.pool.shutdown(wait=False)
    return {
        "cycle_actuations": actuations,
        "cycle_detail": detail,
        "cycle_store_writes": writes,
        "between_post_shutdown_calls": len(hass.services.calls) - mark,
        "between_post_shutdown_writes": _store_writes() - mark_w,
    }


async def main() -> None:
    coord_mod.mqtt.async_publish = _publish
    dt_util.freeze(START)
    results: list[tuple[str, str]] = []
    try:
        # Time one uninterrupted cycle so the blind delays are known to land
        # inside the solve rather than after it.
        t0 = time.monotonic()
        control = await _healthy_cycle(CONFIG)
        cycle_s = time.monotonic() - t0
        results.append(("control.cycle_seconds", f"{cycle_s:.3f}"))
        for key, value in control.items():
            results.append((f"control.{key}", str(value)))

        trials = 20
        for delay in (0.01, 0.05, 0.15):
            hits = 0
            calls_total = 0
            writes_total = 0
            detail = "none"
            for _ in range(trials):
                row = await _trial(delay, CONFIG)
                calls_total += row["post_shutdown_actuations"]
                writes_total += row["post_shutdown_store_writes"]
                if row["post_shutdown_actuations"]:
                    hits += 1
                    detail = row["post_shutdown_detail"]
            tag = f"blind_{delay:g}s"
            results.append((f"{tag}.trials", str(trials)))
            results.append((f"{tag}.trials_with_post_shutdown_actuation", str(hits)))
            results.append(
                (
                    f"{tag}.post_shutdown_actuations_per_trial",
                    f"{calls_total / trials:.4f}",
                )
            )
            results.append(
                (
                    f"{tag}.post_shutdown_store_writes_per_trial",
                    f"{writes_total / trials:.4f}",
                )
            )
            results.append((f"{tag}.detail", detail))

        # PERTURBATION: without the switch entity the switch.turn_on is gone.
        no_switch = dict(CONFIG)
        no_switch.pop("heat_pump_switch_entity")
        row = await _trial(0.05, no_switch)
        for key in ("post_shutdown_actuations", "post_shutdown_detail"):
            results.append((f"no_switch.{key}", str(row[key])))
    finally:
        dt_util.freeze(None)

    for name, value in results:
        print(f"RESULT {name}={value} count")

    t0 = time.process_time()
    tt0 = time.thread_time()
    x = 0.0
    for i in range(200000):
        x += i ** 0.5
    proc = time.process_time() - t0
    thread = time.thread_time() - tt0
    print(f"RESULT thread_factor={proc / thread if thread else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    asyncio.run(main())
