"""D10 verify-v3 (round 9), D10-s1-01 in REAL Home Assistant core 2026.2.3.

Metric (one line): arms, of five, in which a fresh user flow driven through the
real FlowManager with the entry's CURRENT effective identity answers (token +
identity entity slots of data|options) is NOT aborted already_configured
(RESULT dup_accepted); beside it, arms where the ORIGINAL answers (no entry
holds them any more) ARE aborted already_configured (RESULT stale_refused), and
the real HA end state: entries of the domain after the duplicate flow
(RESULT entries_after_dup_max).
Arms: control_none, reconfigure (real SOURCE_RECONFIGURE flow), reauth (started
by the real ConfigEntry.async_start_reauth, driven through the FlowManager),
options_token and options_indoor (real OptionsFlowManager, entities page).
The fresh flow is user -> user_sensors (the sectioned schema, validated by the
real FlowManager) -> finish_now menu -> setup_overview -> create_entry.
Perturbation (--fix): hass.config_entries.async_update_entry is wrapped so a
write that changes data/options re-stamps unique_id=config_flow.entry_identity
({**data, **options}) through the real API's unique_id argument.
Expected: baseline dup_accepted=3 stale_refused=3; --fix 0 and 0; control arms 0.
Exact (counts).

Run:  /home/claude/havenv/bin/python tools/audit/round9/D10/verify-v3/realha_uid.py [--fix]
      (from the repository root, WITHOUT tests/hastub on PYTHONPATH)
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (+ round-9 evidence).
Machine: G2-V3 cloud container, 4 vCPU, CPython 3.14.0rc2, HA core 2026.2.3.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _realha as R  # noqa: E402  (env shims; must precede HA imports)

import asyncio  # noqa: E402
import logging  # noqa: E402

import voluptuous as vol  # noqa: E402
from homeassistant import config_entries  # noqa: E402
from homeassistant.data_entry_flow import section  # noqa: E402
from homeassistant.helpers import config_validation as cv  # noqa: E402
import voluptuous_serialize  # noqa: E402

logging.basicConfig(level=logging.CRITICAL)
FIX = "--fix" in sys.argv
CLOCK = R.Clock()

from custom_components.heatpump_optimizer import config_flow, const  # noqa: E402

config_flow.async_get_clientsession = lambda hass, verify_ssl=True: R.Session(200)

CREDS = {"name": "Heat Pump Optimizer", const.CONF_TIBBER_TOKEN: "tok-a",
         const.CONF_WEATHER_ENTITY: "weather.home"}
SENSORS = {const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.pump_a",
           const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor_a"}


def sectioned(schema, flat):
    """Place flat answers into the sections of the real form schema."""
    out = {}
    for key, val in schema.schema.items():
        name = str(key)
        if isinstance(val, section):
            inner = {k: flat[k] for k in (str(x) for x in val.schema.schema) if k in flat}
            out[name] = inner
        elif name in flat:
            out[name] = flat[name]
    return out


async def fresh(hass, answers):
    mgr = hass.config_entries.flow
    res = await mgr.async_init(R.DOMAIN, context={"source": config_entries.SOURCE_USER})
    creds = {k: v for k, v in answers.items() if k in CREDS}
    sensors = {k: v for k, v in answers.items() if k not in CREDS}
    res = await mgr.async_configure(res["flow_id"], creds)
    if res.get("step_id") != "user_sensors":
        return res
    res = await mgr.async_configure(res["flow_id"], sectioned(res["data_schema"], sensors))
    for _ in range(6):
        if res["type"] in ("abort", "create_entry"):
            return res
        if res["type"] == "menu":
            res = await mgr.async_configure(res["flow_id"], {"next_step_id": "finish_now"})
        else:
            res = await mgr.async_configure(res["flow_id"], {})
    return res


def initial_data(serialised):
    """The frontend's computeInitialHaFormData over a serialised schema
    (same rules as tools/audit/round9/D12/verify-v3/realha_flows.py)."""
    data = {}
    for field in serialised:
        name = field["name"]
        desc = field.get("description") or {}
        if desc.get("suggested_value") is not None:
            data[name] = desc["suggested_value"]
        elif "default" in field:
            data[name] = field["default"]
        elif field.get("type") == "expandable":
            data[name] = initial_data(field["schema"])
    return data


def untouched_with(res, flat):
    ser = voluptuous_serialize.convert(res["data_schema"], custom_serializer=cv.custom_serializer)
    data = initial_data(ser)
    for key, val in res["data_schema"].schema.items():
        name = str(key)
        if isinstance(val, section):
            for k in (str(x) for x in val.schema.schema):
                if k in flat:
                    data.setdefault(name, {})[k] = flat[k]
        elif name in flat:
            data[name] = flat[name]
    return data


def identity_answers(entry):
    eff = {**entry.data, **entry.options}
    return {k: eff[k] for k in set(CREDS) | set(SENSORS) if eff.get(k)}


async def run_arm(arm):
    hass = await R.make_hass()
    for eid, st in (("weather.home", "sunny"), ("switch.pump_a", "on"),
                    ("sensor.indoor_a", "21"), ("sensor.indoor_new", "21")):
        hass.states.async_set(eid, st)
    if FIX:
        real = hass.config_entries.async_update_entry

        def restamp(entry, **kw):
            changed = real(entry, **kw)
            uid = config_flow.entry_identity({**entry.data, **entry.options})
            if entry.unique_id != uid and "unique_id" not in kw:
                real(entry, unique_id=uid)
            return changed

        hass.config_entries.async_update_entry = restamp
    original = {**CREDS, **SENSORS}
    res = await fresh(hass, original)
    assert res["type"] == "create_entry", res
    entry = res["result"]
    if arm == "reconfigure":
        mgr = hass.config_entries.flow
        r = await mgr.async_init(R.DOMAIN, context={"source": config_entries.SOURCE_RECONFIGURE,
                                                    "entry_id": entry.entry_id})
        r = await mgr.async_configure(r["flow_id"], {**CREDS, const.CONF_TIBBER_TOKEN: "tok-b"})
        r = await mgr.async_configure(r["flow_id"], dict(SENSORS))
        assert r.get("reason") == "reconfigure_successful", r
    elif arm == "reauth":
        entry.async_start_reauth(hass)
        await hass.async_block_till_done()
        flows = [f for f in hass.config_entries.flow.async_progress_by_handler(R.DOMAIN)
                 if f["context"].get("source") == config_entries.SOURCE_REAUTH]
        assert flows, "no reauth flow"
        r = await hass.config_entries.flow.async_configure(
            flows[0]["flow_id"], {const.CONF_TIBBER_TOKEN: "tok-b"})
        assert r.get("reason") == "reauth_successful", r
    elif arm in ("options_token", "options_indoor"):
        mgr = hass.config_entries.options
        r = await mgr.async_init(entry.entry_id)
        for step in ("advanced", "entities"):
            if r["type"] == "menu":
                r = await mgr.async_configure(r["flow_id"], {"next_step_id": step})
        assert r.get("step_id") == "entities", r
        change = ({const.CONF_TIBBER_TOKEN: "tok-b"} if arm == "options_token"
                  else {const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor_new"})
        cur = identity_answers(entry)
        cur.pop("name", None)
        posted = untouched_with(r, change)
        r = await mgr.async_configure(r["flow_id"], posted)
        if r["type"] in ("menu", "form"):
            mgr.async_abort(r["flow_id"])
        k, v = next(iter(change.items()))
        assert {**entry.data, **entry.options}.get(k) == v, (arm, r)
    await hass.async_block_till_done()
    now_ans = identity_answers(entry)
    now_res = await fresh(hass, now_ans)
    n_after = len(hass.config_entries.async_entries(R.DOMAIN))
    old_res = await fresh(hass, original) if now_res["type"] != "create_entry" else None
    if now_res["type"] == "create_entry":
        # remove the duplicate before the stale probe, so it probes E alone
        await hass.config_entries.async_remove(now_res["result"].entry_id)
        old_res = await fresh(hass, original)
    changed = now_ans != original
    dup = now_res["type"] != "abort" or now_res.get("reason") != "already_configured"
    stale = changed and old_res["type"] == "abort" and old_res.get("reason") == "already_configured"
    print(f"arm={arm:15s} changed={changed!s:5s} fresh(current)->{now_res['type']}/"
          f"{now_res.get('reason', '')} entries_after={n_after} fresh(original)->"
          f"{old_res['type']}/{old_res.get('reason', '')} "
          f"uid_follows={entry.unique_id == config_flow.entry_identity({**entry.data, **entry.options})}")
    await hass.async_stop(force=True)
    return int(dup), int(stale), n_after


async def main():
    arms = ["control_none", "reconfigure", "reauth", "options_token", "options_indoor"]
    dup = stale = nmax = 0
    for arm in arms:
        d, s, n = await run_arm(arm)
        dup, stale, nmax = dup + d, stale + s, max(nmax, n)
    print(f"MODE {'fix' if FIX else 'baseline'}  ha_version={R.HA_VERSION}")
    print(f"RESULT dup_accepted={dup} arms")
    print(f"RESULT stale_refused={stale} arms")
    print(f"RESULT entries_after_dup_max={nmax} entries")
    print(f"RESULT arms={len(arms)} count")


asyncio.run(main())
R.footer(CLOCK)
