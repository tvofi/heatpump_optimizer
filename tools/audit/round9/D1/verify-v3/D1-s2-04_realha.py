"""V3 reach for D1-s2-04 (five cycle-path guards log a persistent failure at DEBUG) under real HA.

Metric: per site, with the callee replaced by one that raises (the finder's fault
model), 3 real DataUpdateCoordinator.async_refresh cycles of the REAL coordinator on
a REAL hass whose logging was set up by homeassistant.bootstrap.async_enable_logging
and whose `logger` and `system_log` integrations were set up with empty config
(an install that never configured logging). Reported per site: emitted = records of
the injected error that pass the integration logger's effective level (what reaches
home-assistant.log), system_log = entries of it in the system_log integration (what
Settings > System > Logs shows), cycles_ok. Plus debug_enabled = 1 if the
integration logger is enabled for DEBUG under those defaults.
Count key: logging records carrying the injected message, as HA's handlers get them.
One real solve seeds a cached plan; _await_optimize returns it afterwards (as the
finder's guards.py does), to keep CPU off a shared box.
Perturbation --debug-to-warning: the coordinator logger's debug routed to warning
in memory -> emitted and system_log become 3 per site.

Command:  /root/venvha/bin/python tools/audit/round9/D1/verify-v3/D1-s2-04_realha.py [--debug-to-warning]
Baseline 1936d5ca (+6f51db2c evidence); G1 cloud container; homeassistant 2026.2.3.
"""
import os
_H = os.path.join(os.path.dirname(os.path.abspath(__file__)), "D1-1_realha.py")
exec(compile(open(_H).read(), _H, "exec"))

import asyncio
import copy
import logging
from datetime import timedelta
from unittest import mock

PERTURB = "--debug-to-warning" in sys.argv
SITES = ["_command_frequency", "_async_drive_pumps", "_async_watch_learning_drift",
         "_maybe_run_fuse_advisor", "_maybe_refresh_price_tile"]


class Rec(logging.Handler):
    def __init__(self):
        super().__init__(logging.NOTSET)
        self.rows = []

    def emit(self, r):
        self.rows.append(r)


async def main():
    hass = await make_hass()
    from homeassistant.bootstrap import async_enable_logging
    from homeassistant.setup import async_setup_component
    from homeassistant.util import dt as dt_util
    logfile = os.path.join(hass.config.config_dir, "home-assistant.log")
    await async_enable_logging(hass, False, None, logfile, True)
    from homeassistant import loader
    loader.async_setup(hass)
    from homeassistant.config_entries import ConfigEntries
    hass.config_entries = ConfigEntries(hass, {})
    await hass.config_entries.async_initialize()
    await async_setup_component(hass, "logger", {})
    await async_setup_component(hass, "system_log", {})
    from heatpump_optimizer import coordinator as cm
    HC = cm.HeatPumpOptimizerCoordinator
    now = dt_util.now().replace(minute=0, second=0, microsecond=0)
    hass.states.async_set("sensor.indoor", "21.4", {"unit_of_measurement": "°C"})
    hass.states.async_set("sensor.outdoor", "-3.0", {"unit_of_measurement": "°C"})
    hass.states.async_set("sensor.prices", "0.5", {"raw_today": [
        {"start": (now + timedelta(hours=h)).isoformat(), "value": round(0.5 + 0.1 * (h % 4), 3)}
        for h in range(48)]})
    cfg = {"indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
           "price_source": "entity", "price_entity": "sensor.prices"}
    seed = HC(hass, make_entry(dict(cfg), entry_id="seed"))
    await asyncio.sleep(0.1)
    await seed._async_update_data()
    cached = copy.deepcopy(seed._optimization_result)
    debug_enabled = int(cm._LOGGER.isEnabledFor(logging.DEBUG))
    rec = Rec()
    logging.getLogger().addHandler(rec)
    silent = 0
    for site in SITES:
        reached = {"n": 0}

        async def boom(self, *a, _s=site, **k):
            reached["n"] += 1
            raise TypeError(f"injected into {_s}")

        async def fake_opt(*a, **k):
            return copy.deepcopy(cached)
        c = HC(hass, make_entry(dict(cfg), entry_id=f"e_{site}"))
        await asyncio.sleep(0.1)
        patches = [mock.patch.object(HC, site, boom), mock.patch.object(cm, "_await_optimize", fake_opt)]
        if PERTURB:
            patches.append(mock.patch.object(cm._LOGGER, "debug", cm._LOGGER.warning))
        rec.rows.clear()
        ok = 0
        with patches[0], patches[1], (patches[2] if PERTURB else mock.patch.object(cm, "_LOGGER", cm._LOGGER)):
            for _ in range(3):
                await c.async_refresh()
                ok += int(c.last_update_success)
        await asyncio.sleep(0.2)
        hits = [r for r in rec.rows if f"injected into {site}" in r.getMessage()
                or f"injected into {site}" in str(r.args)]
        emitted = sum(1 for r in hits if logging.getLogger(r.name).isEnabledFor(r.levelno))
        sl = hass.data.get("system_log")
        entries = sl.records.to_list() if sl is not None and hasattr(sl, "records") else []
        in_ui = sum(1 for e in entries if f"injected into {site}" in str(e))
        if reached["n"] and emitted == 0 and in_ui == 0:
            silent += 1
        print(f"RESULT emitted_{site}={emitted} records (reached={reached['n']}, cycles_ok={ok}/3, system_log={in_ui})")
    print(f"RESULT debug_enabled={debug_enabled} flag")
    print(f"RESULT silent_sites={silent} of {len(SITES)}")

asyncio.run(main())
tail()
os._exit(0)
