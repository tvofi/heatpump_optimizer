"""D10 verify-v2 for D10-s1-02: does the Optimize-now press surface a not-run solve?

Metric: over four injected outcome arms, count arms where the solve did not run
(async_run_optimization returned a non-None reason, or the price fetch raised
UpdateFailed) and ForceOptimizationButton.async_press, driven through the real
coordinator.async_force_optimization -> async_request_refresh ->
_async_update_data path, returns without raising (silent_presses). Also
reports, per arm, whether the entity-availability signal moved
(coordinator.last_update_success False), i.e. whether any other surface
reports the not-run press.
Count key: the exception (or none) the production async_press delivers.
Arms (outcome injected with mock.patch.object on production coordinator
methods, inputs untouched; the four fetch/learn steps are patched to no-ops so
only the injected outcome differs): ok (reason None, null control),
no_prices, solve_failed, fetch_failed (_fetch_tibber_prices raises UpdateFailed).
Service twin: services.handle_run_optimization under the same patch.
Perturbation: --perturb raise makes coordinator.async_force_optimization raise
HomeAssistantError when async_run_optimization returns a reason (the
coordinator-side one-line fix) -> silent_presses must drop by the reason arms (2).
Run: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D10/verify-v2/press_reason.py [--perturb raise]
Expected baseline: silent_presses=3 (no_prices, solve_failed, fetch_failed), control 0; raise: 1 (fetch_failed).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: G2-V2 cloud container, 4 cores, CPython 3.14.0rc2.
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, logging, sys, time  # noqa: E402
from types import SimpleNamespace  # noqa: E402
from unittest import mock  # noqa: E402
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from heatpump_optimizer import button, const, services  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as C  # noqa: E402
from homeassistant.config_entries import ConfigEntryState  # noqa: E402
from homeassistant.exceptions import HomeAssistantError  # noqa: E402
from homeassistant.helpers.update_coordinator import UpdateFailed  # noqa: E402
logging.disable(logging.CRITICAL)
PERTURB = "raise" in sys.argv


async def _noop(self, *a, **k): return None


def coord_for(arm):
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.0"))
    hass.states.set("sensor.outdoor", FakeState("-2.0"))
    cfg = {const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY, const.CONF_PRICE_ENTITY: "sensor.price",
           const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor", const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor"}
    entry = FakeEntry(data=cfg, entry_id=f"e_{arm}")
    c = C(hass, entry); entry.state = ConfigEntryState.LOADED; entry.runtime_data = c
    hass.config_entries.entries.append(entry)
    c._skip_solve_once = False
    return hass, entry, c


def patches(arm, calls):
    reason = {"ok": None, "no_prices": "no_prices", "solve_failed": "solve_failed", "fetch_failed": None}[arm]
    async def run(self):
        calls.append(reason); return reason
    async def fetch(self):
        if arm == "fetch_failed":
            raise UpdateFailed("injected price feed failure")
    ps = [mock.patch.object(C, "async_run_optimization", run),
          mock.patch.object(C, "_fetch_tibber_prices", fetch),
          mock.patch.object(C, "_fetch_weather_forecast", _noop),
          mock.patch.object(C, "_fetch_solar_forecast", _noop),
          mock.patch.object(C, "_async_learn_price_shape", _noop)]
    if PERTURB:
        async def force(self):
            await self.async_request_refresh()
            if calls and calls[-1] is not None:
                raise HomeAssistantError(calls[-1])
        ps.append(mock.patch.object(C, "async_force_optimization", force))
    return ps


async def outcome(coro):
    try:
        await coro; return "ok"
    except HomeAssistantError as e:
        return f"raised:{type(e).__name__}"


async def arm_run(arm):
    calls = []
    ps = patches(arm, calls)
    for p in ps: p.start()
    try:
        hass, entry, c = coord_for(arm)
        press = await outcome(button.ForceOptimizationButton(c, entry).async_press())
        avail = c.last_update_success
        hass2, _, c2 = coord_for(arm)
        svc = await outcome(services.handle_run_optimization(hass2, SimpleNamespace(data={}, hass=hass2)))
    finally:
        for p in ps: p.stop()
    not_run = arm != "ok"
    silent = int(not_run and press == "ok")
    print(f"arm={arm:13s} solve_calls={calls} press={press:26s} last_update_success={avail} service={svc} silent={silent}")
    return silent, int(not_run and avail)


async def main():
    s = q = 0
    for arm in ("ok", "no_prices", "solve_failed", "fetch_failed"):
        a, b = await arm_run(arm); s += a; q += b
    print(f"MODE {'raise' if PERTURB else 'baseline'}")
    print(f"RESULT silent_presses={s} arms")
    print(f"RESULT silent_and_still_available={q} arms")
    print("RESULT arms=4 count")

t0p, t0t = time.process_time(), time.thread_time()
asyncio.run(main())
dp, dt = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={dp/dt if dt else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    print("RESULT swapins=" + next(l.split()[1] for l in open('/proc/vmstat') if l.startswith('pswpin')))
except Exception:
    print("RESULT swapins=unknown")
