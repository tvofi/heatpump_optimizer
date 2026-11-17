"""D17-v1 V2 flow harness for D17-s1-02, D17-s2-03, D17-s2-05 (own walks and metrics).

Run from the export root: PYTHONPATH=tests/hastub python3 $HOME/vout/D17-v1/harness/v2_flow.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import myrig  # noqa: E402,F401  (path setup)
from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.data_entry_flow import AbortFlow  # noqa: E402
from heatpump_optimizer import config_flow, const  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402


async def sub(flow, step, ans):
    try:
        return await getattr(flow, f"async_step_{step}")(ans)
    except AbortFlow as e:
        return {"type": "abort", "reason": e.reason}


async def quick_entry(qs_over=None, prefill=None):
    flow = config_flow.HeatPumpOptimizerConfigFlow()
    flow.hass = FakeHass()
    r = await sub(flow, "user", {"name": "V5", const.CONF_TIBBER_TOKEN: "x", const.CONF_WEATHER_ENTITY: "weather.w"})
    r = await sub(flow, "user_sensors", {const.CONF_INDOOR_TEMP_ENTITY: "sensor.a", const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.b"})
    from heatpump_optimizer import presets as P
    qs = {const.CONF_BUILDING_STRUCTURE: P.STRUCTURE_TIMBER_SLAB, const.CONF_BUILDING_ERA: P.ERA_1980_2005,
          const.CONF_BUILDING_FOUNDATION: P.FOUNDATION_NONE, const.CONF_HEATED_AREA: 120.0,
          const.CONF_UPPER_EMITTER: P.EMITTER_RADIATORS, const.CONF_LOWER_EMITTER: P.EMITTER_RADIATORS,
          "two_zone": False, "buffer_tank": False, "dhw_tank": False, "wood_furnace": False, "wood_buffer_tank": False}
    qs.update(qs_over or {})
    r = await sub(flow, "quick_setup", qs)
    step = r.get("step_id")
    if step == "device_prefill":
        r = await sub(flow, "device_prefill", prefill or {})
    nxt = r.get("step_id")
    r = await sub(flow, "finish_now", {})
    if r.get("step_id") == "setup_overview":
        r = await sub(flow, "setup_overview", {})
    return r, nxt


async def s2_05():
    n = 0
    for choice in ("menu", "close"):
        r, nxt = await quick_entry(prefill={"after_save": choice})
        d = r.get("data") or {}
        n += "after_save" in d
        print(f"RESULT s2-05 choice={choice} type={r.get('type')} next_after_prefill={nxt} after_save_in_data={'after_save' in d}")
    r, nxt = await quick_entry(prefill={})
    print(f"RESULT s2-05 null(no choice posted) after_save_in_data={'after_save' in (r.get('data') or {})}")
    print(f"RESULT s2-05 entries_with_after_save={n} of 2")


async def s2_03():
    for wf, wt in ((True, True), (False, False)):
        r, _ = await quick_entry(qs_over={"wood_furnace": wf, "wood_buffer_tank": wt, "buffer_tank": wt})
        d = r.get("data") or {}
        p = ThermalParameters.from_config(d)
        print(f"RESULT s2-03 wood_furnace={wf} wood_tank={wt} type={r.get('type')} "
              f"wood_tank_configured={p.wood_tank_configured} two_tank_modelled={p.two_tank_modelled} "
              f"topology={p.topology_layout} mixing_valve_mode={d.get('mixing_valve_mode')!r} "
              f"wood_keys={sorted(k for k in d if 'wood' in k)}")
        if wf:
            d2 = dict(d)
            d2[const.CONF_WOOD_TANK_TOP_ENTITY] = "sensor.wood_top"
            p2 = ThermalParameters.from_config(d2)
            print(f"RESULT s2-03 +probe wood_tank_configured={p2.wood_tank_configured} two_tank_modelled={p2.two_tank_modelled} topology={p2.topology_layout}")
            d3 = dict(d2, mixing_valve_mode="smart_write")
            p3 = ThermalParameters.from_config(d3)
            print(f"RESULT s2-03 +probe+valve(smart_write) two_tank_modelled={p3.two_tank_modelled} topology={p3.topology_layout}")


async def s1_02():
    """Options comfort page: entry stores weekday day comfort 21.0; the form shows the
    weekend day field computed = 21.0; submit weekday 23.0 and the weekend field at 21.0.
    Metric: per computed field, is the shown value stored (or does the effective config
    resolve to the new weekday value)."""
    from heatpump_optimizer.entry_config import EntryConfig
    pairs = [(const.CONF_COMFORT_TEMP_DAY, 21.0, 23.0, [const.CONF_COMFORT_TEMP_DAY_WEEKEND, const.CONF_HOLIDAY_COMFORT_DAY]),
             (const.CONF_COMFORT_TEMP_NIGHT, 19.0, 17.5, [const.CONF_COMFORT_TEMP_NIGHT_WEEKEND, const.CONF_HOLIDAY_COMFORT_NIGHT]),
             (const.CONF_DAY_START_HOUR, 6, 8, [const.CONF_DAY_START_HOUR_WEEKEND, const.CONF_HOLIDAY_DAY_START_HOUR]),
             (const.CONF_DAY_END_HOUR, 22, 20, [const.CONF_DAY_END_HOUR_WEEKEND, const.CONF_HOLIDAY_DAY_END_HOUR])]
    lost = kept = 0
    null_lost = 0
    for src, a, b, comp in pairs:
        for change in (True, False):
            hass = FakeHass()
            entry = FakeEntry(data={const.CONF_INDOOR_TEMP_ENTITY: "sensor.a", src: a}, options={}, entry_id="v5f")
            hass.config_entries.entries.append(entry)
            flow = config_flow.HeatPumpOptimizerConfigFlow.async_get_options_flow(entry)
            flow.hass = hass
            form = await flow.async_step_comfort(None)
            # build the submission from the form's own defaults, sections nested
            import voluptuous as vol
            ans = {}
            loc = {}
            for key, val in form["data_schema"].schema.items():
                if type(val).__name__ == "section":
                    inner = {}
                    for k2 in val.schema.schema:
                        dflt = getattr(k2, "default", vol.UNDEFINED)
                        if dflt is not vol.UNDEFINED:
                            inner[str(k2)] = dflt() if callable(dflt) else dflt
                        loc[str(k2)] = str(key)
                    ans[str(key)] = inner
                else:
                    dflt = getattr(key, "default", vol.UNDEFINED)
                    if dflt is not vol.UNDEFINED:
                        ans[str(key)] = dflt() if callable(dflt) else dflt
                    loc[str(key)] = None
            shown = {c: (ans.get(loc[c], {}) if loc.get(c) else ans).get(c) for c in comp}

            def put(k, v):
                if loc.get(k):
                    ans[loc[k]][k] = v
                else:
                    ans[k] = v
            if change:
                put(src, b)
            for c in comp:
                put(c, a)  # keep what the form shows (== a)
            r = await flow.async_step_comfort(ans)
            opts = r.get("data") if r.get("type") == "create_entry" else getattr(flow, "_options", None) or entry.options
            if r.get("type") == "create_entry":
                entry.options = dict(r["data"])
            merged = {**entry.data, **entry.options}
            ec = EntryConfig.from_mapping(merged)
            for c in comp:
                v = getattr(ec, c, None)
                eff = v if v is not None else getattr(ec, src, None)
                ok = abs(float(eff) - float(a)) < 1e-9
                tag = "change" if change else "null"
                print(f"RESULT s1-02 {tag} src={src} {a}->{b if change else a} field={c} shown={shown[c]} "
                      f"stored={c in entry.options} effective={eff} kept_ok={ok} (result type {r.get('type')}, step {r.get('step_id')})")
                if change:
                    lost += not ok
                    kept += ok
                else:
                    null_lost += not ok
    print(f"RESULT s1-02 kept_value_lost={lost} of {lost + kept}; null_lost={null_lost}")


if __name__ == "__main__":
    for f in (s2_05, s2_03, s1_02):
        try:
            asyncio.run(f())
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            print(f"RESULT {f.__name__} ERROR {type(e).__name__}: {e}")
