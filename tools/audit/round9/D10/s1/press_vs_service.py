"""D10-s1 action-exceptions: the Optimize-now button vs the run_optimization action.

Metric: over three input arms on one real coordinator each, count
  silent_presses = arms where the run_optimization service action, called on
                   that coordinator state, raises HomeAssistantError (the solve
                   did not run) while ForceOptimizationButton.async_press, pressed
                   on the same state, returns normally.
Count key: the exception (or its absence) that the production callables
button:ForceOptimizationButton.async_press and services:handle_run_optimization
deliver to their caller; the solve outcome is observed by wrapping
coordinator:HeatPumpOptimizerCoordinator.async_run_optimization (instrument,
the return value passes through untouched) and last_update_success.

Arms (inputs only, via the configured price entity):
  prices_ok    48 h of future quarter-hour prices -> the solve runs (null control:
               both return normally, counts 0)
  stale_prices only yesterday's prices -> fetch 'ok', solve refused 'no_prices'
  feed_down    price entity missing -> fetch fails (UpdateFailed, swallowed by
               the coordinator refresh)
Perturbation: --fix swaps ForceOptimizationButton.async_press for the one-line
fix "reason = await coordinator.async_run_optimization(); raise
HomeAssistantError if reason" (in memory). Expected: baseline silent_presses=2,
--fix silent_presses=0; prices_ok stays 0 in both.

Run (from the export root):
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D10/s1/press_vs_service.py [--fix]
Expected +- 0 (counts). Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1,
machine: audit box B1 (Linux container). Root rule: cwd (sys.path 'tests').
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

import asyncio  # noqa: E402
import logging  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from datetime import timedelta  # noqa: E402
from types import SimpleNamespace  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from heatpump_optimizer import button, const, services  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from homeassistant.config_entries import ConfigEntryState  # noqa: E402
from homeassistant.exceptions import HomeAssistantError  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

logging.disable(logging.CRITICAL)
FIX = "--fix" in sys.argv

if FIX:
    async def _fixed_press(self):
        reason = await self.coordinator.async_run_optimization()
        if reason is not None:
            raise HomeAssistantError(f"optimization did not run: {reason}")

    button.ForceOptimizationButton.async_press = _fixed_press


def price_rows(start, n):
    return [{"start": (start + timedelta(minutes=15 * i)).isoformat(),
             "value": 0.8 + 0.4 * ((i // 4) % 12) / 12.0} for i in range(n)]


def build(arm):
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.0"))
    hass.states.set("sensor.outdoor", FakeState("-2.0"))
    now = dt_util.now().replace(minute=0, second=0, microsecond=0)
    if arm == "prices_ok":
        rows = price_rows(now - timedelta(hours=1), 4 * 49)
    elif arm == "stale_prices":
        rows = price_rows(now - timedelta(hours=30), 4 * 24)
    else:
        rows = None
    if rows is not None:
        hass.states.set("sensor.price", FakeState("0.9", attributes={
            "raw_today": rows, "unit_of_measurement": "SEK/kWh"}))
    cfg = {
        const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY,
        const.CONF_PRICE_ENTITY: "sensor.price",
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    }
    entry = FakeEntry(data=cfg, entry_id=f"e_{arm}")
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    entry.state = ConfigEntryState.LOADED
    entry.runtime_data = coord
    hass.config_entries.entries.append(entry)
    reasons = []
    inner = coord.async_run_optimization

    async def observed():
        r = await inner()
        reasons.append(r)
        return r

    coord.async_run_optimization = observed
    return hass, entry, coord, reasons


async def outcome(coro):
    try:
        await coro
        return "ok"
    except HomeAssistantError as err:
        return f"raised:{type(err).__name__}"


async def warm(coord):
    """One price fetch first, as a loaded coordinator has had (input only)."""
    try:
        await coord._fetch_tibber_prices()
    except Exception:  # noqa: BLE001 - the feed_down arm's UpdateFailed
        pass


async def run_arm(arm):
    hass, entry, coord, reasons = build(arm)
    await warm(coord)
    press = await outcome(button.ForceOptimizationButton(coord, entry).async_press())
    press_reasons, press_success = list(reasons), coord.last_update_success
    hass2, entry2, coord2, reasons2 = build(arm)
    await warm(coord2)
    call = SimpleNamespace(data={}, hass=hass2)
    svc = await outcome(services.handle_run_optimization(hass2, call))
    silent = int(svc != "ok" and press == "ok")
    print(f"arm={arm:13s} press={press:26s} press_solve={press_reasons} "
          f"refresh_ok={press_success}  service={svc:26s} service_solve={reasons2}  silent={silent}")
    return silent


async def main():
    arms = ["prices_ok", "stale_prices", "feed_down"]
    silent = 0
    for arm in arms:
        silent += await run_arm(arm)
    print(f"MODE {'fix' if FIX else 'baseline'}")
    print(f"RESULT silent_presses={silent} arms")
    print(f"RESULT arms={len(arms)} count")


t0p, t0t = time.process_time(), time.thread_time()
asyncio.run(main())
dp, dt = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={dp / dt if dt else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    with open("/proc/vmstat") as fh:
        print("RESULT swapins=" + next(l.split()[1] for l in fh if l.startswith("pswpin")))
except (OSError, StopIteration):
    print("RESULT swapins=unknown")
