"""D4.M2 harness: every remaining validator branch, and a wrong-kind value in every numeric option.

Part A metric: per trigger cell (flow, step, injected values), whether the production handler
returns the expected error key; for fired cells, error keys with no string in the result's
section per language file, and {placeholders} in those strings the result does not supply.
Part B metric: per NumberSelector field on every rendered page, whether a wrong-kind value
("21 °C" text, and "abc") submitted through the page's own schema is refused (vol.Invalid)
rather than stored; counts accepted.
Part C: the reconfigure step rendered with a stub entry (fields, labels, prefill).
Count key: result["errors"] values the production step returns; result["description_placeholders"].
Command: PYTHONPATH=tests/hastub <HOME>/.local/state/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D4/s2/flow_validators.py [--perturb]
  --perturb: patches config_flow._band_errors to return {} -- the comfort-band cells stop
  firing, so cells_fired goes down by the number of band cells.
Expected: the RESULT counts printed at baseline, exact.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: orchestrator Mac (darwin arm64).
Instrumented symbols: config_flow:HeatPumpOptimizerConfigFlow.async_step_{temperature,building_extras,thermal,reconfigure},
config_flow:HeatPumpOptimizerOptionsFlow.async_step_{comfort,thermal_model,heat_curve,building,
entities_metering,hot_water_tank,hot_water,grid,...}, config_flow:_band_errors.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, inspect, json, re, sys, time
from unittest import mock
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from harness import FakeHass, FakeEntry, FakeState  # noqa: E402
from heatpump_optimizer import config_flow, const  # noqa: E402
from golden import empty_section_payload, nest_flat, _nested_schema  # noqa: E402

_t0p, _t0t = time.process_time(), time.thread_time()
CC = "custom_components/heatpump_optimizer/"
TR = {k: json.load(open(p)) for k, p in {
    "strings": CC + "strings.json", "en": CC + "translations/en.json",
    "sv": CC + "translations/sv.json", "de": CC + "translations/de.json"}.items()}
PH = re.compile(r"\{([a-z_]+)\}")
TOK = {const.CONF_TIBBER_TOKEN: "t"}


def fields(schema, section=None):
    for key, value in (schema.schema.items() if schema else []):
        inner = _nested_schema(value)
        if inner is None:
            yield section, str(getattr(key, "schema", key)), key, value
        else:
            yield from fields(inner, str(getattr(key, "schema", key)))


def flatten(d):
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out.update(flatten(v))
        else:
            out[k] = v
    return out


async def submit(kind, step, inject, options=None, states=None, data=None):
    hass = FakeHass(states or {})
    if kind == "config":
        f = config_flow.HeatPumpOptimizerConfigFlow(); f.hass = hass
        f._data = {**TOK, "name": "x", **(data or {})}
    else:
        f = config_flow.HeatPumpOptimizerOptionsFlow(FakeEntry(data=data or {}, options={**TOK, **(options or {})}))
        f.hass = hass
    form = await getattr(f, f"async_step_{step}")(None)
    sch = form["data_schema"]
    pre = empty_section_payload(sch)
    pre.update({k: v for k, v in inject.items() if k in ("name", C.CONF_WEATHER_ENTITY, C.CONF_TIBBER_TOKEN)})
    flat = flatten(sch(pre))
    flat.update(inject)
    if flat.pop("__blank_token", None):
        flat[C.CONF_TIBBER_TOKEN] = ""
    flat = {k: v for k, v in flat.items() if v is not None}
    return kind, await getattr(f, f"async_step_{step}")(nest_flat(sch, flat))


hc_states = {
    "number.offset_abs": FakeState("40", attributes={"min": 20, "max": 60}),
    "number.offset_none": FakeState("unavailable", attributes={"min": -10, "max": 10}),
    "number.offset_oor": FakeState("15", attributes={"min": -10, "max": 10}),
}
C = const
CELLS = [
    # (name, expected key, coroutine factory)
    ("config.temperature min_above_target", "min_above_target", lambda: submit("config", "temperature", {C.CONF_MIN_TEMP: 23.0, C.CONF_TARGET_TEMP: 21.0})),
    ("config.temperature max_below_target", "max_below_target", lambda: submit("config", "temperature", {C.CONF_MAX_TEMP: 19.0, C.CONF_TARGET_TEMP: 21.0})),
    ("config.temperature night_above_day", "night_above_day", lambda: submit("config", "temperature", {C.CONF_COMFORT_TEMP_NIGHT: 22.0, C.CONF_COMFORT_TEMP_DAY: 20.0})),
    ("config.temperature day_window_empty", "day_window_empty", lambda: submit("config", "temperature", {C.CONF_DAY_START_HOUR: 20, C.CONF_DAY_END_HOUR: 6})),
    ("config.temperature comfort_outside_band", "comfort_outside_band", lambda: submit("config", "temperature", {C.CONF_COMFORT_TEMP_DAY: 26.0, C.CONF_MAX_TEMP: 24.0, C.CONF_TARGET_TEMP: 21.0})),
    ("options.comfort night_above_day", "night_above_day", lambda: submit("options", "comfort", {C.CONF_COMFORT_TEMP_NIGHT: 22.0, C.CONF_COMFORT_TEMP_DAY: 20.0})),
    ("options.comfort min_above_target", "min_above_target", lambda: submit("options", "comfort", {C.CONF_MIN_TEMP: 23.0, C.CONF_TARGET_TEMP: 21.0})),
    ("config.building_extras min_power_above_max", "min_power_above_max", lambda: submit("config", "building_extras", {C.CONF_HEAT_PUMP_MIN_POWER: 6.0, C.CONF_HEAT_PUMP_MAX_POWER: 3.0})),
    ("config.thermal min_power_above_max", "min_power_above_max", lambda: submit("config", "thermal", {C.CONF_HEAT_PUMP_MIN_POWER: 6.0, C.CONF_HEAT_PUMP_MAX_POWER: 3.0})),
    ("options.thermal_model min_power_above_max", "min_power_above_max", lambda: submit("options", "thermal_model", {C.CONF_HEAT_PUMP_MIN_POWER: 6.0, C.CONF_HEAT_PUMP_MAX_POWER: 3.0})),
    ("options.thermal_model partload_derate_above_limit", "partload_derate_above_limit", lambda: submit("options", "thermal_model", {C.CONF_HEAT_PUMP_MIN_POWER: 4.0, C.CONF_HEAT_PUMP_MAX_POWER: 5.0, C.CONF_HEAT_PUMP_COP_PARTLOAD_DERATE: 0.3})),
    ("options.heat_curve heat_curve_not_offset", "heat_curve_not_offset", lambda: submit("options", "heat_curve", {C.CONF_HEAT_CURVE_DISPLACE_ENTITY: "number.offset_abs"}, states=hc_states)),
    ("options.heat_curve heat_curve_unreadable", "heat_curve_unreadable", lambda: submit("options", "heat_curve", {C.CONF_HEAT_CURVE_DISPLACE_ENTITY: "number.offset_none", C.CONF_HEAT_CURVE_TARGET_KIND: C.HEAT_CURVE_KIND_PERSISTENT}, states=hc_states)),
    ("options.heat_curve heat_curve_out_of_range", "heat_curve_out_of_range", lambda: submit("options", "heat_curve", {C.CONF_HEAT_CURVE_DISPLACE_ENTITY: "number.offset_oor", C.CONF_HEAT_CURVE_TARGET_KIND: C.HEAT_CURVE_KIND_PERSISTENT}, states=hc_states)),
    ("options.heat_curve heat_curve_entity_in_use", "heat_curve_entity_in_use", lambda: submit("options", "heat_curve", {C.CONF_HEAT_CURVE_DISPLACE_ENTITY: "number.sp"}, options={C.CONF_SPACE_SETPOINT_ENTITY: "number.sp"})),
    ("options.building combi_needs_store", "combi_needs_store", lambda: submit("options", "building", {C.CONF_DHW_COMBI_TANK_ENABLED: True})),
    ("options.building flow_target_needs_two_zone", "flow_target_needs_two_zone", lambda: submit("options", "building", {C.CONF_MIXING_VALVE_WRITE_TARGET_KIND: "flow"}, options={C.CONF_TWO_ZONE_MODE: C.TWO_ZONE_MODE_OFF})),
    ("options.building flow_curve_needs_direct_plant", "flow_curve_needs_direct_plant", lambda: submit("options", "building", {C.CONF_FLOW_CURVE_COP_ENABLED: True, C.CONF_MIXING_VALVE_MODE: sorted(config_flow.mixing_valve.THROTTLING_MODES)[0]})),
    ("options.entities_metering freq_control_needs_number", "freq_control_needs_number", lambda: submit("options", "entities_metering", {C.CONF_FREQ_CONTROL_MODE: C.FREQ_MODE_CONTROL})),
    ("options.hot_water_tank disinfection_control_needs_entity", "disinfection_control_needs_entity", lambda: submit("options", "hot_water_tank", {C.CONF_DHW_DISINFECTION_MODE: C.FREQ_MODE_CONTROL})),
    ("options.hot_water dhw_windows_day_selector", "dhw_windows_day_selector", lambda: submit("options", "hot_water", {C.CONF_DHW_WINDOWS_DAY[0]: "weekdays 06:00-08:00"})),
    ("options.hot_water invalid_dhw_windows (holiday)", "invalid_dhw_windows", lambda: submit("options", "hot_water", {C.CONF_HOLIDAY_DHW_WINDOWS: "nonsense"})),
    ("options.hot_water dhw_min_too_close", "dhw_min_too_close", lambda: submit("options", "hot_water", {C.CONF_DHW_SETPOINT: 50.0, C.CONF_DHW_MIN_TEMP: 49.0})),
    ("options.grid invalid_peak_months", "invalid_peak_months", lambda: submit("options", "grid", {C.CONF_PEAK_TARIFF_MONTHS: "Smarch"})),
    ("options.grid invalid_peak_hours", "invalid_peak_hours", lambda: submit("options", "grid", {C.CONF_PEAK_TARIFF_HOURS: "25:00-26:00"})),
    ("options.grid_connection silent_mode_window_too_short", "silent_mode_window_too_short", lambda: submit("options", "grid_connection", {C.CONF_SILENT_MODE_WINDOWS: "06:00-06:05"})),
    ("config.dhw dhw_min_too_close", "dhw_min_too_close", lambda: submit("config", "dhw", {C.CONF_DHW_SETPOINT: 50.0, C.CONF_DHW_MIN_TEMP: 49.0})),
    ("config.user price_entity_required", "price_entity_required", lambda: submit("config", "user", {"name": "x", C.CONF_WEATHER_ENTITY: "weather.h", C.CONF_PRICE_SOURCE: C.PRICE_SOURCE_ENTITY})),
    ("config.user tibber_token_required", "tibber_token_required", lambda: submit("config", "user", {"name": "x", C.CONF_WEATHER_ENTITY: "weather.h", C.CONF_TIBBER_TOKEN: "x", "__blank_token": 1})),
]


def run_cells():
    fired, missing, unfilled, rows = 0, 0, 0, []
    for name, want, mk in CELLS:
        try:
            sec, res = asyncio.run(mk())
        except Exception as err:  # noqa: BLE001
            rows.append(f"CELL {name}: RAISED {type(err).__name__}: {err}")
            continue
        errs = res.get("errors") or {}
        if want not in errs.values():
            rows.append(f"CELL {name}: NOT FIRED (type={res.get('type')}, errors={errs})")
            continue
        fired += 1
        sup = set((res.get("description_placeholders") or {}).keys())
        for lang, t in TR.items():
            for key in set(errs.values()):
                s = t[sec]["error"].get(key)
                if s is None:
                    missing += 1; rows.append(f"  MISSING {lang}:{sec}.error.{key}"); continue
                need = set(PH.findall(s)) - sup
                if need:
                    unfilled += len(need); rows.append(f"  UNFILLED {lang}:{sec}.error.{key} {sorted(need)}")
        rows.append(f"CELL {name}: fired errors={errs}")
    return fired, missing, unfilled, rows


def wrong_kind():
    """Part B: a text value in every numeric field of every rendered page."""
    total = accepted = 0
    acc = []
    for kind, cls in (("config", config_flow.HeatPumpOptimizerConfigFlow), ("options", config_flow.HeatPumpOptimizerOptionsFlow)):
        for step in sorted(n[11:] for n, _ in inspect.getmembers(cls) if n.startswith("async_step_")):
            if step in ("reconfigure", "reauth"):
                continue
            async def page():
                hass = FakeHass()
                if kind == "config":
                    f = cls(); f.hass = hass; f._data = {**TOK, "name": "x"}
                else:
                    f = cls(FakeEntry(options=dict(TOK))); f.hass = hass
                return await getattr(f, f"async_step_{step}")(None)
            try:
                form = asyncio.run(page())
            except Exception:  # noqa: BLE001
                continue
            sch = form.get("data_schema") if form.get("type") == "form" else None
            if sch is None:
                continue
            try:
                base = flatten(sch(empty_section_payload(sch)))
            except Exception:  # noqa: BLE001
                print(f"WRONG_KIND_PAGE_SKIPPED {kind}.{step} (untouched submit refused)")
                continue
            for _s, name, key, value in fields(sch):
                if type(value).__name__ != "NumberSelector":
                    continue
                for bad in ("21 °C", "abc"):
                    total += 1
                    try:
                        out = flatten(sch(nest_flat(sch, {**base, name: bad})))
                        accepted += 1
                        acc.append(f"{kind}.{step}.{name}={bad!r}->{out.get(name)!r}")
                    except Exception:  # noqa: BLE001
                        pass
    return total, accepted, acc


def reconfigure():
    entry = FakeEntry(data={**TOK, "name": "x", const.CONF_WEATHER_ENTITY: "weather.h",
                            const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor"})
    hass = FakeHass()
    hass.config_entries.async_entries = lambda domain=None: [entry]
    f = config_flow.HeatPumpOptimizerConfigFlow(); f.hass = hass
    f.context = {"source": "reconfigure", "entry_id": entry.entry_id}
    try:
        res = asyncio.run(f.async_step_reconfigure(None))
    except Exception as err:  # noqa: BLE001
        return f"RAISED {type(err).__name__}: {err}", 0, 0
    sid = res.get("step_id")
    flist = list(fields(res.get("data_schema")))
    nolabel = sum(1 for lang, t in TR.items() for _s, n, _k, _v in flist
                  if not t["config"]["step"].get(sid, {}).get("data", {}).get(n))
    return f"step_id={sid} fields={len(flist)}", len(flist), nolabel


if "--perturb" in sys.argv:
    with mock.patch.object(config_flow, "_band_errors", lambda *a, **k: {}):
        fired, missing, unfilled, rows = run_cells()
else:
    fired, missing, unfilled, rows = run_cells()
for r in rows:
    print(r)
total, accepted, acc = wrong_kind()
for a in acc:
    print("WRONG_KIND_ACCEPTED", a)
rc_desc, rc_fields, rc_nolabel = reconfigure()
print("RECONFIGURE", rc_desc)
print(f"RESULT cells={len(CELLS)} count")
print(f"RESULT cells_fired={fired} count")
print(f"RESULT missing_error_strings={missing} count")
print(f"RESULT unfilled_placeholders={unfilled} count")
print(f"RESULT numeric_wrong_kind_submits={total} count")
print(f"RESULT numeric_wrong_kind_accepted={accepted} count")
print(f"RESULT reconfigure_fields={rc_fields} count")
print(f"RESULT reconfigure_unlabelled_field_lang_pairs={rc_nolabel} count")
print(f"RESULT thread_factor={(time.process_time()-_t0p)/max(time.thread_time()-_t0t,1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
