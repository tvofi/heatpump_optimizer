"""D10-s2 gold rule reconfiguration-flow: a reconfigure takes effect.

The reconfigure step writes the first screen's answers into entry.data
(config_flow.HeatPumpOptimizerConfigFlow._async_save_reconfigure). The
coordinator runs on entry.options laid over entry.data (EntryConfig over
{**data, **options}), and the options flow's Entities page stores the same
keys in entry.options. So after one Options save of that page, a reconfigure
that changes a sensor or the price feed writes a value the running config
never reads, and the reopened form is prefilled from data, not from what runs.

Arms:  options_saved - the entry's Entities options page saved once through
                       the real options flow (indoor sensor moved to
                       sensor.indoor_b), then a reconfigure choosing
                       sensor.indoor_c and weather.other.
       null          - the same reconfigure on an entry that never saved options.
Metric: shadowed = first-screen keys whose reconfigured answer differs from the
effective configuration ({**entry.data, **entry.options}) after the
reconfigure returned reconfigure_successful.
Key: the effective configuration the coordinator is built from, read after the
flow, never the flow's own return.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D10/s2/reconfig_shadow.py [--perturb]
Expected at baseline 92d38ecb: RESULT shadowed_options_saved>=2,
RESULT shadowed_null=0, exact.
--perturb wraps _async_save_reconfigure in memory so it also drops the
first-screen keys from entry.options: shadowed_options_saved -> 0.
Instrumented symbol: heatpump_optimizer.config_flow:HeatPumpOptimizerConfigFlow._async_save_reconfigure
Machine: local macOS box B2, Python 3.14 venv-ci.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _census as c  # noqa: E402
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.data_entry_flow import AbortFlow  # noqa: E402
from golden import _presented_fields  # noqa: E402  (tests/golden.py's flattener)
from heatpump_optimizer import config_flow, const  # noqa: E402

DATA = {
    config_flow.CONF_NAME: "Heat Pump Optimizer",
    const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY,
    const.CONF_PRICE_ENTITY: "sensor.prices",
    const.CONF_WEATHER_ENTITY: "weather.home",
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor_a",
}
RECONF_CREDS = {
    config_flow.CONF_NAME: "Heat Pump Optimizer",
    const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY,
    const.CONF_PRICE_ENTITY: "sensor.prices",
    const.CONF_WEATHER_ENTITY: "weather.other",
}
RECONF_SENSORS = {const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor_c"}

if "--perturb" in sys.argv:
    _orig = config_flow.HeatPumpOptimizerConfigFlow._async_save_reconfigure

    async def _patched(self, user_input):
        entry = self._reconfigure_entry
        keys = {str(getattr(m, "schema", m)) for m in config_flow._first_screen_schema(self.hass).schema}
        entry.options = {k: v for k, v in entry.options.items() if k not in keys}
        return await _orig(self, user_input)

    config_flow.HeatPumpOptimizerConfigFlow._async_save_reconfigure = _patched


def hass_with_states():
    hass = FakeHass()
    for eid in ("sensor.prices", "sensor.indoor_a", "sensor.indoor_b", "sensor.indoor_c"):
        hass.states.set(eid, FakeState("21.0"))
    for eid in ("weather.home", "weather.other"):
        hass.states.set(eid, FakeState("cloudy"))
    return hass


async def submit(flow, step, answers):
    try:
        return await getattr(flow, f"async_step_{step}")(answers)
    except AbortFlow as err:
        return {"type": "abort", "reason": err.reason}


async def arm(save_options):
    hass = hass_with_states()
    entry = FakeEntry(data=dict(DATA), entry_id="e1", unique_id=config_flow.entry_identity(DATA))
    hass.config_entries.entries.append(entry)
    if save_options:
        opts = config_flow.HeatPumpOptimizerOptionsFlow(entry)
        opts.hass = hass
        form = await opts.async_step_entities(None)
        # Submit the page as the frontend does: every field at its shown
        # value, the indoor sensor changed.
        answers = {}
        for key, _v in _presented_fields(form["data_schema"]):
            name = str(getattr(key, "schema", key))
            sv = (getattr(key, "description", None) or {}).get("suggested_value")
            dv = key.default() if callable(getattr(key, "default", None)) else None
            val = sv if sv is not None else dv
            if val is not None:
                answers[name] = val
        answers[const.CONF_INDOOR_TEMP_ENTITY] = "sensor.indoor_b"
        answers[config_flow.CONF_AFTER_SAVE] = config_flow.AFTER_SAVE_CLOSE
        res = await submit(opts, "entities", answers)
        if res.get("type") == "create_entry":
            entry.options = dict(res["data"])
        print(f"OPTIONS_SAVE type={res.get('type')} errors={res.get('errors')} keys={sorted(entry.options)}")
    flow = config_flow.HeatPumpOptimizerConfigFlow()
    flow.hass = hass
    flow.context = {"source": "reconfigure", "entry_id": "e1"}
    first = await flow.async_step_reconfigure(None)
    prefill = {str(getattr(k, "schema", k)): (getattr(k, "description", None) or {}).get("suggested_value")
               for k in first["data_schema"].schema}
    res = await submit(flow, "reconfigure", dict(RECONF_CREDS))
    if res.get("step_id") == "user_sensors":
        sensors_form = res
        prefill.update({str(getattr(k, "schema", k)): (getattr(k, "description", None) or {}).get("suggested_value")
                        for k in sensors_form["data_schema"].schema})
        res = await submit(flow, "user_sensors", dict(RECONF_SENSORS))
    effective = {**entry.data, **entry.options}
    asked = {**RECONF_CREDS, **RECONF_SENSORS}
    shadowed = sorted(k for k, v in asked.items() if effective.get(k) != v)
    stale_prefill = sorted(k for k in (const.CONF_INDOOR_TEMP_ENTITY,)
                           if save_options and prefill.get(k) != {**DATA, **entry.options}.get(k)
                           and k not in RECONF_SENSORS)
    print(f"ARM save_options={save_options} result={res.get('type')}/{res.get('reason')} "
          f"prefill_indoor={prefill.get(const.CONF_INDOOR_TEMP_ENTITY)} shadowed={shadowed} "
          f"effective_indoor={effective.get(const.CONF_INDOOR_TEMP_ENTITY)} "
          f"effective_weather={effective.get(const.CONF_WEATHER_ENTITY)}")
    return len(shadowed), res, prefill


n_saved, res_saved, prefill_saved = asyncio.run(arm(True))
n_null, res_null, _ = asyncio.run(arm(False))
print(f"RESULT shadowed_options_saved={n_saved} count")
print(f"RESULT shadowed_null={n_null} count")
print(f"RESULT reconfigure_reported_success={int(res_saved.get('reason') == 'reconfigure_successful')} count")
print(f"RESULT prefill_shows_running_indoor={int(prefill_saved.get(const.CONF_INDOOR_TEMP_ENTITY) == 'sensor.indoor_b')} count")
c.stats()
