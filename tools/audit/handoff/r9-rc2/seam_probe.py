"""RC2 probe: do queued switch turn-offs survive a restart?

Real Home Assistant core (the installed version), the real ``switch``
component and its entity-service path (so PARALLEL_UPDATES is honoured as the
installed HA honours it), the tree's real coordinator and switch platform, and
the real Store on a temp config dir. Only ``_async_update_data`` is replaced:
it sleeps SOLVE seconds (the Pi's 30-70 s solve), publishes the two payload
keys the v6.6.12 switches read, and saves the accuracy store at the end, as the
real cycle does after a completed solve.

Usage: python queue_probe.py <tree> <solve_s> <gap_s> <stop_after_s>
  phase 1: all four on (fast solve), settle, stop -- the stores say "on".
  phase 2: restart, settle, then four single-entity turn_off calls fired as
           websocket calls are (background tasks), <gap_s> apart, with a
           <solve_s> solve; stop <stop_after_s> after the first tap.
  phase 3: restart, settle, print is_on and what the coordinator holds.
"""
import asyncio
import logging
import sys
import tempfile
import time
import typing
from datetime import timedelta

if not hasattr(typing, "ByteString"):  # 3.14 dropped it; mashumaro names it
    typing.ByteString = bytes  # type: ignore[attr-defined]

TREE = sys.argv[1]
sys.path.insert(0, TREE)
logging.basicConfig(level=logging.WARNING)

from homeassistant import bootstrap, loader  # noqa: E402
from homeassistant.core import HomeAssistant  # noqa: E402
from homeassistant.helpers.entity_platform import EntityPlatform  # noqa: E402
from homeassistant.setup import async_setup_component  # noqa: E402
from homeassistant.config_entries import ConfigEntryState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

import custom_components.heatpump_optimizer.coordinator as cmod  # noqa: E402
import custom_components.heatpump_optimizer.switch as smod  # noqa: E402

DOMAIN = "heatpump_optimizer"
IDS = [
    "switch.heat_pump_optimizer_optimizer_active",
    "switch.heat_pump_optimizer_away",
    "switch.heat_pump_optimizer_dhw_boost",
    "switch.heat_pump_optimizer_boost_space",
]
solve_s = {"v": 0.05}


async def _stub_update(self):
    await asyncio.sleep(solve_s["v"])
    data = dict(self.data or {})
    data["mode"] = self._mode
    data["away_override_active"] = bool(self._away_state.override_active)
    data["dhw_enabled"] = True
    await self._async_save_accuracy()
    return data


cmod.HeatPumpOptimizerCoordinator._async_update_data = _stub_update


class Entry:
    def __init__(self, hass):
        self.data = {"dhw_enabled": True}
        self.options = {}
        self.entry_id = "probe_entry"
        self.version = 1
        self.minor_version = 1
        self.domain = DOMAIN
        self.title = "probe"
        self.unique_id = None
        self.state = ConfigEntryState.LOADED
        self.pref_disable_polling = False
        self._on_unload = []
        self._hass = hass
        self.subentries = {}

    def add_update_listener(self, listener):
        return lambda: None

    def async_on_unload(self, func):
        self._on_unload.append(func)

    def async_create_background_task(self, hass, coro, name, eager_start=True):
        return hass.async_create_background_task(coro, name)


async def boot(cfg):
    from homeassistant import config_entries
    hass = HomeAssistant(cfg)
    loader.async_setup(hass)
    hass.config_entries = config_entries.ConfigEntries(hass, {})
    await bootstrap.async_load_base_functionality(hass)
    hass.set_state(__import__("homeassistant.core", fromlist=["CoreState"]).CoreState.running)
    await hass.async_block_till_done()
    assert await async_setup_component(hass, "switch", {})
    from types import MappingProxyType
    entry = config_entries.ConfigEntry(
        data={"dhw_enabled": True}, discovery_keys=MappingProxyType({}), domain=DOMAIN,
        entry_id="probe_entry", minor_version=1, options={}, source="user",
        subentries_data=None, title="probe", unique_id=None, version=1)
    hass.config_entries._entries[entry.entry_id] = entry
    entry._async_set_state(hass, ConfigEntryState.LOADED, None)
    coord = cmod.HeatPumpOptimizerCoordinator(hass, entry)
    entry.runtime_data = coord
    await asyncio.sleep(0.5)  # the spawned store loads land
    await hass.async_block_till_done()
    await coord.async_refresh()
    platform = EntityPlatform(
        hass=hass, logger=logging.getLogger("probe"), domain="switch",
        platform_name=DOMAIN, platform=smod, scan_interval=timedelta(seconds=30),
        entity_namespace=None,
    )
    platform.config_entry = entry
    ents = [smod.OptimizerEnableSwitch(coord, entry), smod.AwaySwitch(coord, entry),
            smod.BoostDhwSwitch(coord, entry), smod.BoostSpaceSwitch(coord, entry)]
    await platform.async_add_entities(ents)
    await hass.async_block_till_done()
    return hass, coord, ents


async def stop(hass, coord):
    await coord.async_shutdown()
    await hass.async_stop()



MODE = sys.argv[2]

async def main():
    import json
    results = {}
    cases = {
        "house_thermal_mass": (lambda c: c.async_update_thermal_params({"house_thermal_mass": 77.0}),
                               lambda c: c._ctx._thermal_params.room_thermal_mass),
        "house_heat_loss_coefficient": (lambda c: c.async_update_thermal_params({"house_heat_loss_coefficient": 0.123}),
                               lambda c: round(c._ctx._thermal_params.heat_loss_coefficient, 3)),
        "dhw_legionella_temp": (lambda c: c.async_update_thermal_params({"dhw_legionella_temp": 66.0}),
                               lambda c: c._ctx._thermal_params.dhw_legionella_temp),
        "ecl110_displace_max": (lambda c: c.async_update_thermal_params({"ecl110_displace_max": 3.0}),
                               lambda c: c._ctx._thermal_params.ecl110_displace_max),
        "target_temperature": (lambda c: c.async_set_target_temperature(21.5),
                               lambda c: c._ctx._opt_config.target_temp),
        "arm_system_identification": (lambda c: c.async_arm_system_identification(),
                               lambda c: c._sysid.phase),
        "set_mode_economy": (lambda c: c.async_set_mode("economy"), lambda c: c._mode),
    }
    for name, (setter, reader) in cases.items():
        cfg = tempfile.mkdtemp(prefix="rc2seam")
        solve_s["v"] = 0.05
        hass, coord, ents = await boot(cfg)
        before = reader(coord)
        solve_s["v"] = 30 if MODE == "nocycle" else 0.05
        await asyncio.sleep(11)
        t = hass.async_create_background_task(setter(coord), "ws:setter")
        await asyncio.sleep(2)
        if MODE == "cycle":
            await coord.async_refresh()
        set_value = reader(coord)
        await stop(hass, coord)
        solve_s["v"] = 0.05
        hass, coord, ents = await boot(cfg)
        after = reader(coord)
        await stop(hass, coord)
        kept = (after == set_value) and (set_value != before)
        print(f"SEAM[{MODE}] {name}: default={before!r} set={set_value!r} after_restart={after!r} kept={kept}", flush=True)


asyncio.run(main())
