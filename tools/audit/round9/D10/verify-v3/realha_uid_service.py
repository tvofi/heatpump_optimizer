"""D10 verify-v3 (round 9), D10-s1-01 seam census: the assign_entity SERVICE
(services.py handle_assign_entity, the card's click-to-assign) in REAL Home
Assistant core 2026.2.3 -- a write seam outside config_flow.py, so outside the
finding's seam_rule.

Metric (one line): arms (of 2) in which, after the real
hass.services.async_call(DOMAIN, "assign_entity", {key, entity_id}) on a
LOADED entry, a fresh user flow through the real FlowManager submitting the
entry's current effective identity answers is NOT aborted already_configured
(RESULT dup_accepted). Arms: control (no service call) and assign_indoor
(indoor_temp_entity -> sensor.indoor_new).
Perturbation (--fix): hass.config_entries.async_update_entry wrapped to
re-stamp unique_id = config_flow.entry_identity({**data, **options}).
Expected: baseline dup_accepted=1 (assign_indoor), --fix 0; control 0. Exact.

Run:  /home/claude/havenv/bin/python tools/audit/round9/D10/verify-v3/realha_uid_service.py [--fix]
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
from homeassistant.data_entry_flow import section  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

logging.basicConfig(level=logging.CRITICAL)
FIX = "--fix" in sys.argv
CLOCK = R.Clock()

from custom_components.heatpump_optimizer import config_flow, const  # noqa: E402

USER = {"name": "HPO", const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY,
        const.CONF_PRICE_ENTITY: "sensor.price", const.CONF_WEATHER_ENTITY: "weather.home"}
SENS = {const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor_a"}


def sectioned(schema, flat):
    out = {}
    for key, val in schema.schema.items():
        name = str(key)
        if isinstance(val, section):
            inner = {k: flat[k] for k in (str(x) for x in val.schema.schema) if k in flat}
            if inner:
                out[name] = inner
        elif name in flat:
            out[name] = flat[name]
    return out


async def fresh(hass, sensors):
    mgr = hass.config_entries.flow
    r = await mgr.async_init(R.DOMAIN, context={"source": config_entries.SOURCE_USER})
    r = await mgr.async_configure(r["flow_id"], dict(USER))
    r = await mgr.async_configure(r["flow_id"], sectioned(r["data_schema"], sensors))
    for _ in range(6):
        if r["type"] in ("abort", "create_entry"):
            return r
        r = await mgr.async_configure(r["flow_id"], {"next_step_id": "finish_now"} if r["type"] == "menu" else {})
    return r


async def run_arm(arm):
    hass = await R.make_hass()
    now = dt_util.now().replace(minute=0, second=0, microsecond=0)
    rows = [{"start": (now - timedelta(hours=1) + timedelta(minutes=15 * i)).isoformat(),
             "value": 0.9} for i in range(4 * 49)]
    hass.states.async_set("sensor.price", "0.9", {"raw_today": rows, "unit_of_measurement": "SEK/kWh"})
    hass.states.async_set("weather.home", "sunny")
    for e in ("sensor.indoor_a", "sensor.indoor_new"):
        hass.states.async_set(e, "21.0", {"unit_of_measurement": "°C", "device_class": "temperature"})
    if FIX:
        real = hass.config_entries.async_update_entry

        def restamp(entry, **kw):
            changed = real(entry, **kw)
            uid = config_flow.entry_identity({**entry.data, **entry.options})
            if entry.unique_id != uid and "unique_id" not in kw:
                real(entry, unique_id=uid)
            return changed

        hass.config_entries.async_update_entry = restamp
    r = await fresh(hass, SENS)
    assert r["type"] == "create_entry", r
    entry = r["result"]
    await hass.async_block_till_done(wait_background_tasks=True)
    assert entry.state is config_entries.ConfigEntryState.LOADED, entry.state
    if arm == "assign_indoor":
        await hass.services.async_call(R.DOMAIN, "assign_entity", {
            "key": const.CONF_INDOOR_TEMP_ENTITY, "entity_id": "sensor.indoor_new"}, blocking=True)
        await hass.async_block_till_done(wait_background_tasks=True)
    eff = {**entry.data, **entry.options}
    cur = {const.CONF_INDOOR_TEMP_ENTITY: eff.get(const.CONF_INDOOR_TEMP_ENTITY)}
    res = await fresh(hass, cur)
    dup = int(res["type"] != "abort" or res.get("reason") != "already_configured")
    print(f"arm={arm:14s} indoor_now={cur[const.CONF_INDOOR_TEMP_ENTITY]} fresh(current)->{res['type']}/"
          f"{res.get('reason', '')} entries={len(hass.config_entries.async_entries(R.DOMAIN))} "
          f"uid_follows={entry.unique_id == config_flow.entry_identity(eff)}")
    await hass.async_stop(force=True)
    return dup


async def main():
    dup = 0
    for arm in ("control", "assign_indoor"):
        dup += await run_arm(arm)
    print(f"MODE {'fix' if FIX else 'baseline'}  ha_version={R.HA_VERSION}")
    print(f"RESULT dup_accepted={dup} arms")
    print("RESULT arms=2 count")


asyncio.run(main())
R.footer(CLOCK)
