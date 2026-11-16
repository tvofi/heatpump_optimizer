#!/usr/bin/env python3
"""D12-s1 cell harness: every d12-cells level, one real setup and one full coordinator cycle with a solve.

Metric (one line): fail_cells = number of `enumerate.py d12-cells` level lines whose run(s) break the
D12.M4 usability bar (setup, cycle-or-named-refusal, published plan, entities evaluate) or whose
production-DELIVERED plant (published dhw_enabled / two_zone_enabled / pv_enabled, describe_setup's
wood, the plan's dhw/lower-zone series, the horizon's pv surplus, sensor availability) disagrees with
the plant the cell DECLARES (built independently of production, from the spec below).

Count key (COMMON.md): every check compares the value production delivers (coordinator data dict,
OptimizationResult, describe_setup, entity `available`/`native_value`) with the cell's declaration;
nothing reads back the config the harness wrote.

Command (export root):
    PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D12/s1/cells.py \
        [--shrink none|dhw|wood|pv|zone|sensor] [--invent-zone] [--cell 'level x=y'] [--ledger OUT.tsv] [--dump DIR]
  --shrink X   D12.M6: drop X from the config handed to production while the cell's declaration keeps it
               (the plant shrinks under an unchanged expectation); fail_cells must rise in every cell
               whose plant holds X.
  --fix-zone-auto  in memory, two_zone_mode 'auto' decided by zone-key presence (the documented rule).
  --fix-plan-zone  in memory, the published plan's zone series gated on the model's two_zone_enabled.
  --invent-zone  a one-line production perturbation in memory: ThermalParameters.from_config returns
               two_zone_enabled=True for every config; fail_cells must rise in every single-zone cell.
Expected (baseline 92d38ecb, export as handed to seat D12-s1, box B4): see REPORT.md; counts are exact.
Machine: box B4 (4 vCPU container), Python 3.14, numpy/scipy per tests/requirements-ci.txt.
Cells it cannot drive (ha_version_*, surface *) are printed as SKIP with the reason; `card_cells.mjs`
and `blueprints.py` beside this file drive the surface lines.
"""
import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")
import argparse, asyncio, copy, importlib, json, logging, re, subprocess, sys, time, tempfile
from datetime import timedelta
from unittest import mock

sys.path[:0] = ["tests", "custom_components"]
import harness  # noqa: E402  (inserts paths, stubs)
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
import numpy as np  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
import profiles  # noqa: E402
from heatpump_optimizer import const as C  # noqa: E402
from heatpump_optimizer import coordinator as cm, price_model as pm, open_meteo as om_mod  # noqa: E402
from heatpump_optimizer import thermal_model as tm, config_flow as cf  # noqa: E402
import heatpump_optimizer as integ  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
START = __import__("datetime").datetime(2026, 1, 15, 0, 0, tzinfo=__import__("datetime").timezone.utc)
PLATFORMS = tuple(str(getattr(p, "value", p)) for p in integ.PLATFORM_LIST)

# ---------------------------------------------------------------- the plant pieces (the declaration)
def T(v, unit="°C"):
    return FakeState(str(v), unit=unit, attributes={"unit_of_measurement": unit} if unit else {})

# entity key -> (entity_id, state, feature it belongs to or None)
ENT = {
    C.CONF_INDOOR_TEMP_ENTITY: ("sensor.indoor", T(21.4), None),
    C.CONF_OUTDOOR_TEMP_ENTITY: ("sensor.outdoor", T(-3.0), None),
    C.CONF_LOWER_FLOOR_TEMP_ENTITY: ("sensor.lower", T(20.6), "zone"),
    C.CONF_FLOOR_RETURN_TEMP_ENTITY: ("sensor.floor_return", T(26.5), "zone"),
    C.CONF_BUFFER_TANK_TEMP_ENTITY: ("sensor.buffer", T(41.5), None),
    C.CONF_DHW_TEMP_ENTITY: ("sensor.dhw", T(51.5), "dhw"),
    C.CONF_DHW_INLET_ENTITY: ("sensor.dhw_inlet", T(8.5), "dhw"),
    C.CONF_DHW_SETPOINT_ENTITY: ("number.dhw_setpoint", T(52.0), "dhw"),
    C.CONF_DHW_HYSTERESIS_ENTITY: ("number.dhw_hyst", T(5.0, "K"), "dhw"),
    C.CONF_DHW_DISINFECTION_SWITCH_ENTITY: ("switch.dhw_disinfect", FakeState("off"), "dhw"),
    C.CONF_VVC_PUMP_ENTITY: ("switch.vvc", FakeState("off"), "dhw"),
    C.CONF_HEAT_PUMP_DHW_BOOSTER_ENTITY: ("binary_sensor.dhw_booster", FakeState("off"), "dhw"),
    C.CONF_HEAT_PUMP_SUPPLY_TEMP_ENTITY: ("sensor.supply", T(35.0), None),
    C.CONF_HEAT_PUMP_RETURN_TEMP_ENTITY: ("sensor.return", T(30.0), None),
    C.CONF_VALVE_OUTLET_TEMP_ENTITY: ("sensor.valve_outlet", T(33.0), "wood"),
    C.CONF_WOOD_TANK_TOP_ENTITY: ("sensor.wood_top", T(62.0), "wood"),
    C.CONF_WOOD_TANK_BOTTOM_ENTITY: ("sensor.wood_bottom", T(41.0), "wood"),
    C.CONF_EXTERNAL_HEAT_ENTITY: ("binary_sensor.stove", FakeState("off"), "wood"),
    C.CONF_MIXING_VALVE_TARGET_ENTITY: ("number.valve_target", T(32.0), "valve"),
    C.CONF_MIXING_VALVE_WRITE_ENTITY: ("number.valve_write", T(32.0), "valve"),
    C.CONF_POWER_ENTITY: ("sensor.hp_power", T(1500, "W"), None),
    C.CONF_ENERGY_ENTITY: ("sensor.hp_energy", T(1234.5, "kWh"), None),
    C.CONF_HEAT_ENERGY_ENTITY: ("sensor.hp_heat_energy", T(3456.0, "kWh"), None),
    C.CONF_THERMAL_POWER_ENTITY: ("sensor.hp_thermal", T(4500, "W"), None),
    C.CONF_HOUSE_POWER_ENTITY: ("sensor.house_power", T(3000, "W"), None),
    C.CONF_COMPRESSOR_FREQ_ENTITY: ("sensor.hp_freq", T(45, "Hz"), None),
    C.CONF_FLOW_METER_ENTITY: ("sensor.flow", T(12.0, "L/min"), None),
    C.CONF_HEAT_PUMP_SWITCH_ENTITY: ("switch.hp", FakeState("on"), None),
    C.CONF_HEAT_PUMP_MODE_ENTITY: ("sensor.hp_mode", FakeState("heating"), None),
    C.CONF_HEAT_PUMP_DEFROST_ENTITY: ("binary_sensor.defrost", FakeState("off"), None),
    C.CONF_HEAT_PUMP_ONLINE_ENTITY: ("binary_sensor.online", FakeState("on"), None),
    C.CONF_HEAT_PUMP_FAULT_ENTITY: ("binary_sensor.fault", FakeState("off"), None),
    C.CONF_HEAT_PUMP_BACKUP_HEATER_ENTITY: ("binary_sensor.backup", FakeState("off"), None),
    C.CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY: ("binary_sensor.cap_limited", FakeState("off"), None),
    C.CONF_SPACE_SETPOINT_ENTITY: ("number.space_setpoint", T(21.0), None),
    C.CONF_SPACE_SETPOINT_LOW_LIMIT_ENTITY: ("number.space_lo", T(10.0), None),
    C.CONF_SPACE_SETPOINT_HIGH_LIMIT_ENTITY: ("number.space_hi", T(55.0), None),
    C.CONF_SPACE_HYSTERESIS_ENTITY: ("number.space_hyst", T(2.0, "K"), None),
    C.CONF_SPACE_PUMP_ENTITY: ("switch.space_pump", FakeState("on"), None),
    C.CONF_HEAT_CURVE_DISPLACE_ENTITY: ("number.displace", T(0.0, None), None),
    C.CONF_INDOOR_HUMIDITY_ENTITY: ("sensor.humidity", T(45.0, "%"), None),
    C.CONF_SOLAR_RADIATION_ENTITY: ("sensor.irradiance", T(150.0, "W/m²"), None),
    C.CONF_PV_PRODUCTION_ENTITY: ("sensor.pv", T(800, "W"), "pv"),
    C.CONF_PV_EXPORT_PRICE_ENTITY: ("sensor.pv_export", T(0.5, "SEK/kWh"), "pv"),
    C.CONF_GRID_FEE_ENTITY: ("sensor.grid_fee", T(0.3, "SEK/kWh"), None),
    C.CONF_PRICE_ENTITY: ("sensor.spot", None, None),  # state built from the price profile
    C.CONF_AWAY_PRESENCE_ENTITY: ("person.owner", FakeState("home"), None),
    C.CONF_HOLIDAY_CALENDAR_ENTITY: ("calendar.holidays", FakeState("off"), None),
}
# a temperature sensor whose entity is the published reading of that entity
READING = {"indoor_temp": C.CONF_INDOOR_TEMP_ENTITY, "lower_floor_temp": C.CONF_LOWER_FLOOR_TEMP_ENTITY,
           "buffer_tank_temp": C.CONF_BUFFER_TANK_TEMP_ENTITY, "dhw_temperature": C.CONF_DHW_TEMP_ENTITY}
READING_NEEDS = {"lower_floor_temp": "zone", "dhw_temperature": "dhw"}

BASE = {C.CONF_TIBBER_TOKEN: "x", C.CONF_WEATHER_ENTITY: "weather.home",
        "target_temperature": 21.0, "min_temperature": 17.0, "max_temperature": 23.0}
FEATURE_KEYS = {
    "dhw": {C.CONF_DHW_TANK_VOLUME: 200.0, "dhw_setpoint": 55.0, "dhw_min_temperature": 45.0,
            "dhw_windows": "06:00-08:30, 17:00-22:00"},
    "zone": {C.CONF_UPPER_FLOOR_THERMAL_MASS: 3.0, C.CONF_LOWER_FLOOR_THERMAL_MASS: 8.0,
             "upper_floor_heat_loss": 0.08, "lower_floor_heat_loss": 0.07},
    "pv": {C.CONF_PV_ENABLED: True, C.CONF_PV_PEAK_KW: 8.0, "pv_export_price": 0.3},
    "wood": {C.CONF_WOOD_FURNACE_ENABLED: True, C.CONF_WOOD_TANK_VOLUME: 500.0, C.CONF_WOOD_TYPE: "birch",
             C.CONF_WOOD_PACKING: "packed", C.CONF_WOOD_PRICE_SEK_M3: 900.0},
    "valve": {C.CONF_MIXING_VALVE_MODE: "smart_read"},
}


class Spec:
    """A cell's declared plant: features, mapped entities, extra keys, the run's environment."""

    def __init__(self, feats=(), ents=(), extra=None, price="winter_typical", climate="winter_mild",
                 mode=None, language="en", ent_override=None):
        self.feats, self.ents, self.extra = set(feats), set(ents), dict(extra or {})
        self.price, self.climate, self.mode, self.language = price, climate, mode, language
        self.ent_override = dict(ent_override or {})

    def config(self, shrink=None):
        feats = set(self.feats) - ({shrink} if shrink in FEATURE_KEYS else set())
        ents = set(self.ents)
        if shrink == "sensor":
            ents.discard(C.CONF_INDOOR_TEMP_ENTITY)
        cfg = dict(BASE)
        for f in feats:
            cfg.update(FEATURE_KEYS[f])
        for e in ents:
            if shrink in FEATURE_KEYS and ENT[e][2] == shrink:
                continue  # the shrunk feature's own sensors go with it
            cfg[e] = ENT[e][0]
        cfg.update(self.extra)
        if shrink == "zone":
            cfg.pop(C.CONF_TWO_ZONE_MODE, None)
        return cfg


ALL_FEATS = ("dhw", "zone", "pv", "wood", "valve")
#: D12.md step 6's shrinks, as --shrink names them: one omitted sensor (the indoor thermometer), DHW, wood,
#: PV, one zone. Printed by --list-shrinks (the D12.M6 enumerator).
SHRINKS = ("dhw", "pv", "sensor", "wood", "zone")
REF_ENTS = tuple(k for k in ENT if k not in (C.CONF_MIXING_VALVE_WRITE_ENTITY,))


def minimal(**kw):
    return Spec(**kw)


def reference(**kw):
    feats = set(ALL_FEATS) | set(kw.pop("feats", ()))
    ents = set(REF_ENTS) | set(kw.pop("ents", ()))
    return Spec(feats=feats, ents=ents, **kw)


# ---------------------------------------------------------------- the cells
def entity_level(key, level):
    feat = ENT[key][2]
    extra = {}
    if key == C.CONF_PRICE_ENTITY:
        extra[C.CONF_PRICE_SOURCE] = "entity"
    if key == C.CONF_GRID_FEE_ENTITY:
        extra[C.CONF_GRID_FEE_MODE] = "entity"
    if key == C.CONF_MIXING_VALVE_WRITE_ENTITY:
        extra[C.CONF_MIXING_VALVE_MODE] = "smart_write"
    if key == C.CONF_AWAY_PRESENCE_ENTITY:
        extra[C.CONF_AWAY_ENABLED] = True
    if level == "present":
        return [("minimal+entity", Spec(feats={feat} if feat else (), ents={key}, extra=extra)),
                ("reference", reference(ents={key}, extra=extra))]
    # absent: the reference plant, feature still on, this one entity unmapped
    ref = reference(extra=extra)
    ref.ents.discard(key)
    return [("reference-entity", ref)]


def axis_level(axis, x):
    """[(arm, Spec)] for one non-entity level; None when the harness cannot drive it."""
    on_both = lambda **kw: [("minimal", Spec(**kw)), ("reference", reference(**kw))]
    if axis == "climate":
        return on_both(climate=x)
    if axis == "price_shape":
        return on_both(price=x)
    if axis == "operation_mode":
        return on_both(mode=x)
    if axis == "language":
        return on_both(language=x)
    if axis == "layout":
        need = {"no_valve": dict(feats={"dhw"}), "single_tank_valve": dict(feats={"valve"}),
                "two_tank_4way": dict(feats={"valve", "zone", "wood"}, ents={C.CONF_WOOD_TANK_TOP_ENTITY}),
                "valve_upper_direct_slab": dict(feats={"valve", "zone"}),
                "slab_shunt": dict(feats={"valve", "zone"})}[x]
        s = Spec(extra={C.CONF_TOPOLOGY_LAYOUT: x}, **need)
        r = reference(extra={C.CONF_TOPOLOGY_LAYOUT: x})
        if x == "no_valve":
            r.feats.discard("valve")
        if x == "valve_upper_direct_slab":
            r.ents -= {C.CONF_WOOD_TANK_TOP_ENTITY, C.CONF_WOOD_TANK_BOTTOM_ENTITY}
        return [("minimal+prereq", s), ("reference", r)]
    if axis == "two_zone_mode":
        if x == "on":
            return [("minimal", Spec(feats={"zone"}, extra={C.CONF_TWO_ZONE_MODE: x})),
                    ("reference", reference(extra={C.CONF_TWO_ZONE_MODE: x}))]
        if x == "off":
            r = reference(extra={C.CONF_TWO_ZONE_MODE: x})
            r.feats.discard("zone")  # declared: the zone keys stay stored, the model is single-zone
            r.extra.update(FEATURE_KEYS["zone"])
            return [("minimal", Spec(extra={C.CONF_TWO_ZONE_MODE: x})), ("reference", r)]
        return [("minimal", Spec(extra={C.CONF_TWO_ZONE_MODE: x})), ("reference", reference(extra={C.CONF_TWO_ZONE_MODE: x}))]
    if axis == "mixing_valve_mode":
        feats = set() if x == "none" else {"valve"}
        ents = {C.CONF_MIXING_VALVE_WRITE_ENTITY} if x == "smart_write" else set()
        r = reference(extra={C.CONF_MIXING_VALVE_MODE: x}, ents=ents)
        if x == "none":
            r.feats.discard("valve")
        return [("minimal", Spec(feats=feats, ents=ents, extra={C.CONF_MIXING_VALVE_MODE: x})), ("reference", r)]
    if axis == "valve_write_target":
        extra = {C.CONF_MIXING_VALVE_MODE: "smart_write", C.CONF_MIXING_VALVE_WRITE_TARGET_KIND: x}
        return [("minimal", Spec(feats={"valve"}, ents={C.CONF_MIXING_VALVE_WRITE_ENTITY}, extra=extra)),
                ("reference", reference(ents={C.CONF_MIXING_VALVE_WRITE_ENTITY}, extra=extra))]
    if axis in ("wood_type", "wood_packing"):
        key = C.CONF_WOOD_TYPE if axis == "wood_type" else C.CONF_WOOD_PACKING
        return [("minimal", Spec(feats={"wood"}, ents={C.CONF_WOOD_TANK_TOP_ENTITY}, extra={key: x})),
                ("reference", reference(extra={key: x}))]
    if axis == "combi_tank":
        extra = cf._combi_preset_fill({C.CONF_DHW_COMBI_TANK_TYPE: x, C.CONF_DHW_COMBI_TANK_ENABLED: True}, {})
        return [("minimal", Spec(feats={"dhw"}, extra=extra)), ("reference", reference(extra=extra))]
    if axis in ("structure", "foundation", "era", "emitter"):
        key = {"structure": C.CONF_BUILDING_STRUCTURE, "foundation": C.CONF_BUILDING_FOUNDATION,
               "era": C.CONF_BUILDING_ERA}.get(axis)
        out = []
        for arm, s in (("minimal", Spec()), ("reference", reference())):
            answers = {key: x} if key else {C.CONF_UPPER_EMITTER: x, C.CONF_LOWER_EMITTER: x}
            derived = cf._derive_preset(dict(answers), s.config())
            s.extra.update(answers)
            s.extra.update(derived)
            out.append((arm, s))
        return out
    if axis == "grid_fee_mode":
        extra = {C.CONF_GRID_FEE_MODE: x}
        ents = set()
        if x == "rules":
            extra.update({"grid_fee_rules": "Mon-Fri 06:00-22:00 = 0.25", "grid_fee_fixed": 0.05})
        if x == "entity":
            ents = {C.CONF_GRID_FEE_ENTITY}
        return [("minimal", Spec(ents=ents, extra=extra)), ("reference", reference(ents=ents, extra=extra))]
    if axis == "price_source":
        ents = {C.CONF_PRICE_ENTITY} if x == "entity" else set()
        return [("minimal", Spec(ents=ents, extra={C.CONF_PRICE_SOURCE: x})),
                ("reference", reference(ents=ents, extra={C.CONF_PRICE_SOURCE: x}))]
    if axis == "solar_source":
        extra = {"solar_source": x, C.CONF_SOLAR_LOCATION: {"latitude": 59.3, "longitude": 18.0}}
        return on_both(extra=extra)
    if axis in ("compressor_modulation", "heat_curve_target_kind", "pump_duty_mode", "space_setpoint_unit"):
        key = {"compressor_modulation": C.CONF_COMPRESSOR_MODULATION, "heat_curve_target_kind": C.CONF_HEAT_CURVE_TARGET_KIND,
               "pump_duty_mode": C.CONF_PUMP_DUTY_MODE, "space_setpoint_unit": C.CONF_SPACE_SETPOINT_UNIT}[axis]
        ents = {"compressor_modulation": {C.CONF_COMPRESSOR_FREQ_ENTITY}, "heat_curve_target_kind": {C.CONF_HEAT_CURVE_DISPLACE_ENTITY},
                "pump_duty_mode": {C.CONF_SPACE_PUMP_ENTITY}, "space_setpoint_unit": {C.CONF_SPACE_SETPOINT_ENTITY}}[axis]
        return [("minimal", Spec(ents=ents, extra={key: x})), ("reference", reference(extra={key: x}))]
    if axis in ("temperature_unit", "power_unit", "energy_unit", "flow_unit"):
        return unit_level(axis, x)
    return None


_TEMP_CONV = {"C": lambda c: c, "degC": lambda c: c, "°C": lambda c: c, "K": lambda c: c + 273.15,
              "F": lambda c: c * 9 / 5 + 32, "degF": lambda c: c * 9 / 5 + 32, "°F": lambda c: c * 9 / 5 + 32}


def unit_level(axis, x):
    if axis == "temperature_unit":
        conv = _TEMP_CONV[x]
        over = {C.CONF_INDOOR_TEMP_ENTITY: T(round(conv(21.4), 2), x), C.CONF_OUTDOOR_TEMP_ENTITY: T(round(conv(-3.0), 2), x),
                C.CONF_BUFFER_TANK_TEMP_ENTITY: T(round(conv(41.5), 2), x)}
        ents = set(over)
    else:
        key, kw = {"power_unit": (C.CONF_POWER_ENTITY, 1.5), "energy_unit": (C.CONF_ENERGY_ENTITY, 1234.5),
                   "flow_unit": (C.CONF_FLOW_METER_ENTITY, None)}[axis]
        if axis == "flow_unit":
            lpm = 12.0
            per = {"L/h": lpm * 60, "L/min": lpm, "L/s": lpm / 60, "kg/h": lpm * 60, "kg/min": lpm, "kg/s": lpm / 60,
                   "m³/h": lpm * 60 / 1000, "m³/s": lpm / 60000}[x]
        else:
            tab = C.POWER_UNIT_TO_KW if axis == "power_unit" else getattr(C, "ENERGY_UNIT_TO_KWH", {"Wh": 1e-3, "kWh": 1.0, "MWh": 1e3})
            per = kw / tab[x]
        over = {key: T(round(per, 6), x)}
        ents = {key}
    return [("minimal", Spec(ents=ents, ent_override=over)), ("reference", reference(ent_override=over))]


def cell_specs(cell):
    m = re.fullmatch(r"level ([^=]+)=(.*)", cell)
    if not m:
        return None
    axis, x = m.groups()
    if axis.startswith("CONF_") and axis.endswith("_ENTITY"):
        return entity_level(getattr(C, axis), x)
    return axis_level(axis, x)


# ---------------------------------------------------------------- the environment
def price_rows(profile):
    p = profiles.prices(profile, START)
    rows = [{"start": (START + timedelta(minutes=15 * i)).isoformat(), "value": float(v)} for i, v in enumerate(p)]
    # profiles are 24 h of quarters; repeat the day for tomorrow
    rows += [{"start": (START + timedelta(days=1, minutes=15 * i)).isoformat(), "value": float(v)} for i, v in enumerate(p)]
    return rows


def weather_rows(profile):
    t, wind, rain, solar = profiles.weather(profile, START)
    out = []
    for h in range(48):
        i = (h * 4) % len(t)
        out.append({"datetime": (START + timedelta(hours=h)).isoformat(), "temperature": float(t[i]),
                    "wind_speed": float(wind[i]), "precipitation": float(rain[i]), "humidity": 80.0,
                    "solar_irradiance": float(solar[i])})
    return out


def make_hass(spec, cfg):
    hass = FakeHass()
    hass.config.language = spec.language
    rows = weather_rows(spec.climate)

    async def forecasts(call):
        return {"weather.home": {"forecast": rows}}
    hass.services.async_register("weather", "get_forecasts", forecasts)
    hass.states.set("weather.home", FakeState("cloudy", attributes={"temperature_unit": "°C", "wind_speed_unit": "m/s",
                                                                     "precipitation_unit": "mm", "temperature": rows[0]["temperature"]}))
    for key, (eid, state, _f) in ENT.items():
        if cfg.get(key) != eid:
            continue
        if key == C.CONF_PRICE_ENTITY:
            r = price_rows(spec.price)
            state = FakeState(str(r[0]["value"]), attributes={"raw_today": r[:96], "raw_tomorrow": r[96:],
                                                              "unit_of_measurement": "SEK/kWh"})
        hass.states.set(eid, spec.ent_override.get(key, state))
    return hass


def patches(spec):
    rows = price_rows(spec.price)

    async def tibber_post(session, token, body):
        tib = [{"total": r["value"], "startsAt": r["start"], "level": "NORMAL"} for r in rows]
        return 200, {"data": {"viewer": {"homes": [{"currentSubscription": {"priceInfo": {"today": tib[:96], "tomorrow": tib[96:]}}}]}}}

    async def solve(hass, optimizer, inputs):
        return await hass.async_add_executor_job(cm.optimize_in_process, optimizer, inputs)

    async def om_json(self, session, url, params):
        t, _w, _r, solar = profiles.weather(spec.climate, START)
        times = [(START + timedelta(minutes=15 * i)).strftime("%Y-%m-%dT%H:%M") for i in range(192)]
        vals = [float(solar[i % len(solar)]) for i in range(192)]
        hours = times[::4]
        return {"minutely_15": {"time": times, "shortwave_radiation": vals},
                "hourly": {"time": hours, "shortwave_radiation": vals[::4], "relative_humidity_2m": [80.0] * len(hours),
                           "snowfall": [0.0] * len(hours)}}
    return [mock.patch.object(pm, "_tibber_post", tibber_post),
            mock.patch.object(cm, "async_get_clientsession", lambda hass: object()),
            mock.patch.object(om_mod, "async_get_clientsession", lambda hass: object()),
            mock.patch.object(om_mod.OpenMeteoSolar, "_get_json", om_json),
            mock.patch.object(cm, "_await_optimize", solve)]


class LogTap(logging.Handler):
    def __init__(self):
        super().__init__(logging.WARNING)
        self.lines = []

    def emit(self, record):
        self.lines.append(f"{record.levelname} {record.name}: {record.getMessage()[:200]}")


# ---------------------------------------------------------------- one run and its checks
async def run_one(spec, shrink=None):
    """(fails, facts): every M4 bar broken, keyed on what production delivered."""
    cfg = spec.config(shrink)
    hass = make_hass(spec, cfg)
    entry = FakeEntry(data=cfg)
    fails, facts = [], {}
    # 1 setup, through the integration's own async_setup_entry
    try:
        ok = await integ.async_setup_entry(hass, entry)
        coord = entry.runtime_data
        if not ok:
            fails.append("setup returned False")
    except Exception as err:  # noqa: BLE001 - a raise is the observable
        refused = getattr(err, "translation_key", None)
        fails.append(f"setup raised {type(err).__name__}: {err}"[:200] + ("" if not refused else f" (named {refused})"))
        return fails, facts
    # 2 entities, through every platform's async_setup_entry
    ents = []
    for plat in PLATFORMS:
        mod = importlib.import_module(f"heatpump_optimizer.{plat}")

        def add(es, *a, **k):
            for e in es:
                e.hass = hass
            ents.extend(es)
        try:
            await mod.async_setup_entry(hass, entry, add)
        except Exception as err:  # noqa: BLE001
            fails.append(f"platform {plat} setup raised {type(err).__name__}: {err}"[:200])
    # 3 one full cycle (what the background first solve runs)
    data = None
    try:
        data = await coord._async_update_data()
        coord.data = data
    except Exception as err:  # noqa: BLE001
        key = getattr(err, "translation_key", None)
        facts["refusal"] = key or f"{type(err).__name__}: {err}"
        if not key:
            fails.append(f"cycle raised unnamed {type(err).__name__}: {err}"[:200])
    res = coord._optimization_result
    if data is not None and spec.mode in (None, "auto", "economy"):
        if res is None or str(res.status).startswith("failed"):
            fails.append(f"no plan published (status={getattr(res, 'status', None)}, optimization_status={data.get('optimization_status')})")
    # 4 entities evaluate
    for e in ents:
        for attr in ("native_value", "extra_state_attributes", "available", "is_on", "current_option", "hvac_mode"):
            try:
                getattr(e, attr, None)
            except Exception as err:  # noqa: BLE001
                fails.append(f"entity {getattr(e, '_key', type(e).__name__)}.{attr} raised {type(err).__name__}: {err}"[:200])
    # 5 the delivered plant against the declared plant
    if data is not None:
        decl = spec.feats
        for feat, key in (("dhw", "dhw_enabled"), ("zone", "two_zone_enabled"), ("pv", "pv_enabled")):
            if bool(data.get(key)) != (feat in decl):
                fails.append(f"published {key}={data.get(key)} but the cell declares {feat}={'on' if feat in decl else 'off'}")
        setup = coord.describe_setup()
        wood_on = bool((setup.get("wood") or {}).get("present")) if isinstance(setup.get("wood"), dict) else bool(setup.get("wood"))
        if wood_on != ("wood" in decl):
            fails.append(f"describe_setup wood={setup.get('wood')!r:.80} but the cell declares wood={'on' if 'wood' in decl else 'off'}")
        facts["layout"] = setup.get("layout")
        if res is not None:
            if "dhw" not in decl and float(np.nansum(np.asarray(res.dhw_power_schedule or [0.0], float))) > 1e-9:
                fails.append(f"plan heats a hot-water tank the cell does not have: sum dhw_power={float(np.nansum(res.dhw_power_schedule)):.3f}")
            rows = ((data.get("space_plan") or {}).get("forecast") or [])
            zone_rows = sum(1 for row in rows if row.get("lower") is not None or row.get("upper") is not None)
            if "zone" not in decl and zone_rows:
                # keyed on the PUBLISHED plan (the space-plan sensor's forecast rows), not the result object
                fails.append(f"plan carries a lower-zone trajectory the cell does not have ({zone_rows}/{len(rows)} published rows carry upper/lower)")
        try:
            pv = coord._forecast_arrays().pv_surplus
            if "pv" not in decl and float(np.nansum(np.abs(np.asarray(pv, float)))) > 1e-9:
                fails.append("horizon carries PV surplus the cell does not have")
        except Exception as err:  # noqa: BLE001
            fails.append(f"_forecast_arrays raised {type(err).__name__}: {err}"[:200])
        mapped = spec.config().keys() if shrink is None else spec.config().keys()
        for e in ents:
            k = getattr(e, "_key", None)
            if k not in READING:
                continue
            slot = READING[k]
            need = READING_NEEDS.get(k)
            declared = slot in spec.ents and (need is None or need in decl)
            try:
                avail = bool(e.available)
                val = e.native_value
            except Exception:  # noqa: BLE001 - already counted above
                continue
            if avail and slot not in spec.ents:
                fails.append(f"sensor {k} available ({val}) with no entity mapped: a fabricated reading")
            if declared and not avail:
                fails.append(f"sensor {k} unavailable although its entity is mapped")
    try:
        await coord.async_shutdown()
    except Exception:  # noqa: BLE001
        pass
    facts["entities"] = len(ents)
    facts["states"] = entity_states(ents) if DUMP else None
    return fails, facts


DUMP = False


def _slug(s):
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", s.lower())).strip("_")


_EN = None


def entity_states(ents):
    """{entity_id: {state, attributes}} the way Home Assistant would name them, for the card harness."""
    global _EN
    if _EN is None:
        _EN = json.load(open("custom_components/heatpump_optimizer/translations/en.json"))["entity"]
    out = {}
    for e in ents:
        eid = getattr(e, "entity_id", None)  # entity.py sets heat_pump_optimizer_<translation key>
        if not eid:
            continue
        try:
            st = e.native_value if hasattr(e, "native_value") else getattr(e, "is_on", None)
            if isinstance(st, bool):
                st = "on" if st else "off"
            if not e.available:
                st = "unavailable"
            attrs = getattr(e, "extra_state_attributes", None) or {}
        except Exception:  # noqa: BLE001
            continue
        out[eid] = {"state": "unknown" if st is None else str(st), "attributes": json.loads(json.dumps(attrs, default=str))}
    return out


def _zone_presence_rule():
    """--fix-zone-auto: ThermalParameters.from_config with two_zone_mode 'auto' (or absent) decided by the
    presence of a zone key, the rule the docstring at thermal_model.py's two_zone_mode block states."""
    real = tm.ThermalParameters.from_config.__func__
    keys = tuple(getattr(C, k) for k in ("CONF_UPPER_FLOOR_THERMAL_MASS", "CONF_LOWER_FLOOR_THERMAL_MASS",
                                         "CONF_INTER_ZONE_TRANSFER", "CONF_RADIATOR_POWER_FRACTION"))

    def fixed(cls, config, *a, **k):
        p = real(cls, config, *a, **k)
        if str(config.get(C.CONF_TWO_ZONE_MODE, C.DEFAULT_TWO_ZONE_MODE)) == C.TWO_ZONE_MODE_AUTO:
            want = any(key in config for key in keys)
            if p.two_zone_enabled != want:
                p = __import__("dataclasses").replace(p, two_zone_enabled=want)
        return p
    return mock.patch.object(tm.ThermalParameters, "from_config", classmethod(fixed))


FIX_ZONE = False
FIX_PLAN_ZONE = False


def _plan_zone_gate():
    """--fix-plan-zone: _build_plan_views told the zone count by the model (params.two_zone_enabled), not by
    whether the result happens to carry upper/lower trajectories (coordinator.py, `two_zone = bool(...)`)."""
    real = cm.HeatPumpOptimizerCoordinator._build_plan_views

    def gated(self, result):
        if not cm._ctx_of(self)._thermal_params.two_zone_enabled:
            result = __import__("dataclasses").replace(result, upper_temp_trajectory=[], lower_temp_trajectory=[])
        return real(self, result)
    return mock.patch.object(cm.HeatPumpOptimizerCoordinator, "_build_plan_views", gated)


REUSE = {}
REUSED = [0]


def run_cell(cell, shrink=None, invent_zone=False):
    specs = cell_specs(cell)
    if specs is None:
        return None
    results = []
    for arm, spec in specs:
        key = f"{cell} [{arm}]"
        if shrink and not invent_zone and not FIX_ZONE and not FIX_PLAN_ZONE and key in REUSE and spec.config(shrink) == spec.config(None):
            # The shrink leaves this arm's config byte-identical, so production receives exactly the
            # unshrunk run's input; its result is the --reuse file's (same harness, same tree).
            REUSED[0] += 1
            results.append((arm, list(REUSE[key]), {}))
            continue
        tap = LogTap()
        logging.getLogger().addHandler(tap)
        ps = patches(spec)
        if invent_zone:
            real = tm.ThermalParameters.from_config.__func__

            def forced(cls, config, *a, **k):
                p = real(cls, config, *a, **k)
                return p if p.two_zone_enabled else __import__("dataclasses").replace(p, two_zone_enabled=True)
            ps.append(mock.patch.object(tm.ThermalParameters, "from_config", classmethod(forced)))
        if FIX_ZONE:
            ps.append(_zone_presence_rule())
        if FIX_PLAN_ZONE:
            ps.append(_plan_zone_gate())
        for p in ps:
            p.start()
        dt_util.freeze(START + timedelta(hours=6))
        try:
            fails, facts = asyncio.run(run_one(spec, shrink))
        finally:
            dt_util.freeze(None)
            for p in reversed(ps):
                p.stop()
            logging.getLogger().removeHandler(tap)
        results.append((arm, fails, facts))
    return results


# ---------------------------------------------------------------- driver
def universe():
    out = subprocess.run([sys.executable, "-I", "tools/audit/enumerate.py", "d12-cells", "--repo", "."],
                         capture_output=True, text=True, check=True).stdout.splitlines()
    return [l.split("\t")[0] for l in out]


def main():
    global DUMP
    ap = argparse.ArgumentParser()
    ap.add_argument("--shrink", default="none", choices=["none", *SHRINKS])
    ap.add_argument("--invent-zone", action="store_true")
    ap.add_argument("--list-shrinks", action="store_true",
                    help="D12.M6's enumerator: print the plant shrinks D12.md step 6 names, one per line, and exit")
    ap.add_argument("--fix-zone-auto", action="store_true")
    ap.add_argument("--wood-ready", action="store_true",
                    help="the wood feature also carries the external-heat flag and a furnace efficiency, so the wood-fuel advisor is ready")
    ap.add_argument("--fix-plan-zone", action="store_true")
    ap.add_argument("--cell", action="append")
    ap.add_argument("--ledger")
    ap.add_argument("--dump")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--decl", help="write {cell [arm]: declared features} for every driven cell and exit (no production run)")
    ap.add_argument("--results", help="write {cell [arm]: [fails]} here")
    ap.add_argument("--reuse", help="an unperturbed --results file: arms a shrink leaves byte-identical reuse it")
    a = ap.parse_args()
    if a.list_shrinks:
        print("\n".join(SHRINKS))
        return
    DUMP = bool(a.dump)
    if a.wood_ready:
        FEATURE_KEYS["wood"].update({C.CONF_EXTERNAL_HEAT_ENABLED: True, C.CONF_WOOD_FURNACE_EFFICIENCY: 70.0})
    global FIX_ZONE
    FIX_ZONE = a.fix_zone_auto
    global FIX_PLAN_ZONE
    FIX_PLAN_ZONE = a.fix_plan_zone
    logging.basicConfig(level=logging.CRITICAL)
    cells = a.cell or universe()
    if a.decl:
        out = {}
        for cell in cells:
            for arm, spec in (cell_specs(cell) or []):
                out[f"{cell} [{arm}]"] = sorted(spec.feats)
        json.dump(out, open(a.decl, "w"), indent=0, sort_keys=True)
        print(f"RESULT declared_plants={len(out)} count")
        return
    if a.reuse:
        REUSE.update(json.load(open(a.reuse)))
    per_arm = {}
    shrink = None if a.shrink == "none" else a.shrink
    t0, w0 = time.process_time(), time.perf_counter()
    import threading
    th0 = time.thread_time()
    n_run = n_fail = n_skip = 0
    runs = fail_runs = 0
    ledger, dumps = [], {}
    fail_by_reason = {}
    for cell in cells:
        if "/._" in cell or "=._" in cell:
            print(f"SKIP {cell}\texport artefact: an untracked AppleDouble file, not a baseline item")
            n_skip += 1
            continue
        res = run_cell(cell, shrink, a.invent_zone)
        if res is None:
            print(f"SKIP {cell}\tnot driven by this harness (ha_version_*: no Home Assistant but tests/hastub; surface: card_cells.mjs / blueprints.py)")
            n_skip += 1
            continue
        n_run += 1
        for arm, fails, _f in res:
            per_arm[f"{cell} [{arm}]"] = fails
        bad = [(arm, f) for arm, fails, _ in res for f in fails]
        runs += len(res)
        fail_runs += sum(1 for _arm, fails, _ in res if fails)
        if bad:
            n_fail += 1
        for arm, f in bad:
            r = re.sub(r"[-\d.]+", "#", f)[:110]
            fail_by_reason.setdefault(r, []).append(f"{cell} [{arm}]")
        if not a.quiet or bad:
            print(("FAIL " if bad else "PASS ") + cell + "\t" + "; ".join(f"[{arm}] {f}" for arm, f in bad[:4]))
        ledger.append(f"{cell}\tsimulation\tdev/audit/rounds/round11/D12/s1/cells.py --cell '{cell}' ({'FAIL' if bad else 'PASS'}: "
                      f"{len(res)} run(s), setup+cycle+solve+entities+delivered-plant)")
        if DUMP:
            for arm, _f, facts in res:
                dumps[f"{cell} [{arm}]"] = facts.get("states")
    th = time.thread_time() - th0
    cpu = time.process_time() - t0
    print("\nfailure reasons (pattern -> cells):")
    for r, cs in sorted(fail_by_reason.items(), key=lambda kv: -len(kv[1])):
        print(f"  {len(cs):4d}  {r}")
        for c in cs[:3]:
            print(f"          e.g. {c}")
    if a.results:
        with open(a.results, "w") as fh:
            json.dump(per_arm, fh, indent=0, sort_keys=True)
    if a.ledger:
        with open(a.ledger, "w") as fh:
            fh.write("# cell\tsource\tasserting test (D12-s1, written by cells.py)\n" + "\n".join(ledger) + "\n")
    if a.dump:
        os.makedirs(a.dump, exist_ok=True)
        with open(os.path.join(a.dump, "states.json"), "w") as fh:
            json.dump(dumps, fh)
    print(f"RESULT cells_run={n_run} count")
    print(f"RESULT cells_skipped={n_skip} count")
    print(f"RESULT runs={runs} count")
    print(f"RESULT runs_reused={REUSED[0]} count")
    print(f"RESULT fail_cells={n_fail} count")
    print(f"RESULT fail_runs={fail_runs} count")
    print(f"RESULT shrink={a.shrink} invent_zone={int(a.invent_zone)} fix_zone_auto={int(a.fix_zone_auto)} fix_plan_zone={int(a.fix_plan_zone)}")
    print(f"RESULT cpu_s={cpu:.1f} s (provisional)")
    print(f"RESULT thread_factor={cpu / th if th else float('nan'):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = 0
    try:
        sw = int([l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1])
    except Exception:  # noqa: BLE001
        pass
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
