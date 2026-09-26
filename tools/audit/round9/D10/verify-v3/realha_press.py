"""D10 verify-v3 (round 9), D10-s1-02 in REAL Home Assistant core 2026.2.3.

The entry is created by the real config flow (price-entity source, no
network), set up by the real ConfigEntries (async_setup_entry, platforms,
first refresh, the background first solve), and both actions are invoked the
way a user or an automation invokes them: hass.services.async_call("button",
"press", {entity_id: <Optimize now>}, blocking=True) through the real
ButtonEntity, and hass.services.async_call(DOMAIN, "run_optimization",
blocking=True) through the real ServiceRegistry.

Metrics (one line each):
  silent_presses    arms where the press returned without an exception AND no
                    solve completed with reason None during the press
                    (coordinator.async_run_optimization observed, return value
                    passed through) -- the phenomenon, my definition;
  finder_metric     arms where the service raised HomeAssistantError while the
                    press on the same state returned normally (the finder's);
  debounced_presses arms where a press made within the real Debouncer's 10 s
                    cooldown of the previous refresh request returned before
                    any solve started (the stub models the same Debouncer,
                    tests/ha_contract.py "Debouncer"; measured here on the real one).
Arms (state changed AFTER a healthy setup, then the cooldown is waited out):
  prices_ok (null control), stale_prices (only yesterday's prices on the entity),
  feed_down (price entity removed from the state machine).
Perturbation (--fix): ForceOptimizationButton.async_press replaced in memory by
"reason = await coordinator.async_run_optimization(); raise HomeAssistantError
if reason" -- silent_presses on stale_prices must go to 0.
Second perturbation (--fix-fetch): the press fetches prices first (UpdateFailed
-> HomeAssistantError), then solves and raises on a reason code; stale_prices
and feed_down must then RAISE (silent 0 by propagation, not by solving on the
cached prices, which is how --fix reaches 0 in real HA).
Expected: baseline silent_presses=2 (stale_prices, feed_down), prices_ok 0;
see the report for the measured finder_metric. Exact (counts).
Wall: ~60-80 s (waits out the real 10 s refresh cooldown per arm).

Run:  /home/claude/havenv/bin/python tools/audit/round9/D10/verify-v3/realha_press.py [--fix]
      (from the repository root, WITHOUT tests/hastub on PYTHONPATH)
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (+ round-9 evidence).
Machine: G2-V3 cloud container, 4 vCPU, CPython 3.14.0rc2, HA core 2026.2.3.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _realha as R  # noqa: E402

import asyncio  # noqa: E402
import logging  # noqa: E402
from datetime import timedelta  # noqa: E402

from homeassistant import config_entries  # noqa: E402
from homeassistant.exceptions import HomeAssistantError  # noqa: E402
from homeassistant.helpers import entity_registry as er  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

logging.basicConfig(level=logging.CRITICAL)
FIX = "--fix" in sys.argv
CLOCK = R.Clock()

from custom_components.heatpump_optimizer import button, config_flow, const  # noqa: E402
from custom_components.heatpump_optimizer import coordinator as coord_mod  # noqa: E402

if FIX:
    async def _fixed_press(self):
        reason = await self.coordinator.async_run_optimization()
        if reason is not None:
            raise HomeAssistantError(f"optimization did not run: {reason}")

    button.ForceOptimizationButton.async_press = _fixed_press

FIX2 = "--fix-fetch" in sys.argv
if FIX2:
    from homeassistant.helpers.update_coordinator import UpdateFailed

    async def _fixed_press_fetch(self):
        try:
            await self.coordinator._fetch_tibber_prices()
        except UpdateFailed as err:
            raise HomeAssistantError(f"optimization did not run: {err}") from err
        reason = await self.coordinator.async_run_optimization()
        if reason is not None:
            raise HomeAssistantError(f"optimization did not run: {reason}")

    button.ForceOptimizationButton.async_press = _fixed_press_fetch

REASONS = []
_inner = coord_mod.HeatPumpOptimizerCoordinator.async_run_optimization


async def _observed(self, *a, **k):
    REASONS.append("start")
    r = await _inner(self, *a, **k)
    REASONS.append(r)
    return r


coord_mod.HeatPumpOptimizerCoordinator.async_run_optimization = _observed


def rows(start, n):
    return [{"start": (start + timedelta(minutes=15 * i)).isoformat(),
             "value": 0.8 + 0.4 * ((i // 4) % 12) / 12.0} for i in range(n)]


def set_prices(hass, rs):
    hass.states.async_set("sensor.price", "0.9", {"raw_today": rs, "unit_of_measurement": "SEK/kWh"})


async def outcome(coro):
    try:
        await coro
        return "ok"
    except HomeAssistantError as err:
        return f"raised:{type(err).__name__}"


async def setup(hass):
    now = dt_util.now().replace(minute=0, second=0, microsecond=0)
    set_prices(hass, rows(now - timedelta(hours=1), 4 * 49))
    hass.states.async_set("sensor.indoor", "21.0", {"unit_of_measurement": "°C", "device_class": "temperature"})
    hass.states.async_set("sensor.outdoor", "-2.0", {"unit_of_measurement": "°C", "device_class": "temperature"})
    hass.states.async_set("weather.home", "sunny")
    mgr = hass.config_entries.flow
    r = await mgr.async_init(R.DOMAIN, context={"source": config_entries.SOURCE_USER})
    r = await mgr.async_configure(r["flow_id"], {
        "name": "HPO", const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY,
        const.CONF_PRICE_ENTITY: "sensor.price", const.CONF_WEATHER_ENTITY: "weather.home"})
    assert r.get("step_id") == "user_sensors", r
    r = await mgr.async_configure(r["flow_id"], {})
    for _ in range(6):
        if r["type"] in ("abort", "create_entry"):
            break
        if r["type"] == "menu":
            r = await mgr.async_configure(r["flow_id"], {"next_step_id": "finish_now"})
        else:
            r = await mgr.async_configure(r["flow_id"], {})
    assert r["type"] == "create_entry", r
    entry = r["result"]
    hass.config_entries.async_update_entry(entry, options={
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor", const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor"})
    await hass.async_block_till_done(wait_background_tasks=True)
    return entry


async def run_arm(arm):
    hass = await R.make_hass()
    entry = await setup(hass)
    assert entry.state is config_entries.ConfigEntryState.LOADED, entry.state
    await hass.async_block_till_done(wait_background_tasks=True)
    reg = er.async_get(hass)
    btn = next(e.entity_id for e in reg.entities.values()
               if e.config_entry_id == entry.entry_id and e.unique_id.endswith("force_optimization"))
    # debounce probe: a press straight after the setup refresh request
    REASONS.clear()
    await hass.services.async_call("button", "press", {"entity_id": btn}, blocking=True)
    debounced = int("start" not in REASONS)
    await hass.async_block_till_done(wait_background_tasks=True)
    if arm == "stale_prices":
        now = dt_util.now().replace(minute=0, second=0, microsecond=0)
        set_prices(hass, rows(now - timedelta(hours=30), 4 * 24))
    elif arm == "feed_down":
        hass.states.async_remove("sensor.price")
    coord = entry.runtime_data
    # wait out the real Debouncer: a deferred call re-arms its cooldown, so
    # poll until no timer is pending (bounded)
    for _ in range(80):
        await asyncio.sleep(0.5)
        deb = coord._debounced_refresh
        if deb._timer_task is None and not deb._execute_lock.locked():
            break
    await hass.async_block_till_done(wait_background_tasks=True)
    REASONS.clear()
    press = await outcome(hass.services.async_call("button", "press", {"entity_id": btn}, blocking=True))
    press_reasons, press_ok = list(REASONS), coord.last_update_success
    REASONS.clear()
    svc = await outcome(hass.services.async_call(R.DOMAIN, "run_optimization", {}, blocking=True))
    svc_reasons = list(REASONS)
    solved = None in press_reasons
    silent = int(press == "ok" and not solved)
    finder = int(svc != "ok" and press == "ok")
    print(f"arm={arm:13s} press={press:26s} press_solve={press_reasons} refresh_ok={press_ok} "
          f"service={svc:26s} service_solve={svc_reasons} silent={silent} finder={finder} "
          f"debounced_first_press={debounced}")
    await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_stop(force=True)
    return silent, finder, debounced


async def main():
    arms = ["prices_ok", "stale_prices", "feed_down"]
    tot = [0, 0, 0]
    for arm in arms:
        for i, v in enumerate(await run_arm(arm)):
            tot[i] += v
    print(f"MODE {'fix' if FIX else 'fix-fetch' if FIX2 else 'baseline'}  ha_version={R.HA_VERSION}")
    print(f"RESULT silent_presses={tot[0]} arms")
    print(f"RESULT finder_metric={tot[1]} arms")
    print(f"RESULT debounced_presses={tot[2]} arms")
    print(f"RESULT arms={len(arms)} count")


asyncio.run(main())
R.footer(CLOCK)
