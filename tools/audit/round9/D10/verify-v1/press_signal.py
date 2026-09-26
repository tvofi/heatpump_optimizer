"""D10-s1-02 verify-v1: does a not-run Optimize-now press leave ANY HA-visible signal?

Metric: over three price arms (prices_ok, stale_prices, feed_down), count
  press_returned_ok  = arms where button:ForceOptimizationButton.async_press
                       returns without an exception while the solve did not
                       run (coordinator:async_run_optimization returned a
                       reason code, or was never reached);
  fully_silent       = of those, arms where the press also created no repair
                       issue (hass.issues via the issue_registry stub) and left
                       coordinator.last_update_success True -- nothing a user or
                       automation can observe.
Count key: the exception from async_press, the solve's own reason code (the
return value passes through untouched), hass.issues and last_update_success.
Perturbation: --fresh gives the stale_prices arm 48 h of current prices
(input only). Expected: press_returned_ok 2 -> 1, fully_silent 1 -> 0.
Null control: prices_ok counts 0 in both runs.

Run (repo root):
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D10/verify-v1/press_signal.py [--fresh]
Expected +-0 (counts). Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (evidence
tree 6f51db2c). Machine: 4-core Linux cloud container, shared. Root rule: cwd.
"""
from __future__ import annotations

import os

for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_var, "1")

import asyncio  # noqa: E402
import logging  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from datetime import timedelta  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from heatpump_optimizer import button, const  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from homeassistant.config_entries import ConfigEntryState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

logging.disable(logging.CRITICAL)
FRESH = "--fresh" in sys.argv


def rows(start, n):
    return [{"start": (start + timedelta(minutes=15 * i)).isoformat(),
             "value": 0.8 + 0.4 * ((i // 4) % 12) / 12.0} for i in range(n)]


async def arm(name):
    hass = FakeHass()
    hass.issues = []
    hass.states.set("sensor.indoor", FakeState("21.0"))
    hass.states.set("sensor.outdoor", FakeState("-2.0"))
    now = dt_util.now().replace(minute=0, second=0, microsecond=0)
    if name == "prices_ok" or (name == "stale_prices" and FRESH):
        r = rows(now - timedelta(hours=1), 4 * 49)
    elif name == "stale_prices":
        r = rows(now - timedelta(hours=30), 4 * 24)
    else:
        r = None
    if r is not None:
        hass.states.set("sensor.price", FakeState("0.9", attributes={
            "raw_today": r, "unit_of_measurement": "SEK/kWh"}))
    entry = FakeEntry(data={
        const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY,
        const.CONF_PRICE_ENTITY: "sensor.price",
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor"}, entry_id=f"e_{name}")
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    entry.state = ConfigEntryState.LOADED
    entry.runtime_data = coord
    hass.config_entries.entries.append(entry)
    reasons = []
    inner = coord.async_run_optimization

    async def observed():
        x = await inner()
        reasons.append(x)
        return x

    coord.async_run_optimization = observed
    issues_before = len(hass.issues)
    try:
        await button.ForceOptimizationButton(coord, entry).async_press()
        raised = False
    except Exception:  # noqa: BLE001
        raised = True
    ran = reasons == [None]
    new_issues = len(hass.issues) - issues_before
    ok_not_run = int((not raised) and not ran)
    silent = int(ok_not_run and new_issues == 0 and coord.last_update_success)
    print(f"arm={name:13s} raised={raised} solve={reasons} issues_created={new_issues} "
          f"last_update_success={coord.last_update_success} ok_not_run={ok_not_run} silent={silent}")
    return ok_not_run, silent, name == "prices_ok"


async def main():
    ok = sil = ctrl = 0
    for name in ("prices_ok", "stale_prices", "feed_down"):
        a, b, c = await arm(name)
        if c:
            ctrl += a + b
        else:
            ok += a
            sil += b
    print(f"MODE {'fresh' if FRESH else 'baseline'}")
    print(f"RESULT press_returned_ok={ok} arms")
    print(f"RESULT fully_silent={sil} arms")
    print(f"RESULT control_prices_ok={ctrl} count")


t0p, t0t = time.process_time(), time.thread_time()
asyncio.run(main())
dp, dt = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={dp / dt if dt else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
with open("/proc/vmstat") as fh:
    print("RESULT swapins=" + next(l.split()[1] for l in fh if l.startswith("pswpin")))
