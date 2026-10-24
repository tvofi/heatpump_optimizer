"""D8-s1 (round 10) entity matrix: D8.M1 + D8.M2.

Metric: per (cell, entity) violations of the D8.M2 per-entity contract, counted by
class; key = the value the entity's own property returns (native_value / is_on /
hvac_action / extra_state_attributes) after the real coordinator built its payload.
Cells: coordinator_scenarios() (5) plus feature overlays on coord_minimal. Each cell
runs a light first refresh, a solved cycle A, then changed inputs and solved cycle B.

Run (from repo root):
  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D8/s1/matrix.py [--dump CELL]
Baseline 17f1c55fad1b, machine: macOS arm64 (B4 light seat). Counts are exact.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import json
import math
import sys
import time
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np  # noqa: E402
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from golden import START, coordinator_scenarios  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import sensor, binary_sensor, button, climate, switch  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

try:
    import orjson
except ImportError:  # pragma: no cover
    orjson = None

STRINGS = json.loads(open("custom_components/heatpump_optimizer/strings.json").read())["entity"]

UNITS = {
    "temperature": {"°C", "°F", "K"},
    "power": {"W", "kW", "MW"},
    "energy": {"Wh", "kWh", "MWh"},
    "duration": {"d", "h", "min", "s", "ms"},
    "humidity": {"%"},
    "volume": {"L", "m³", "mL", "gal"},
    "volume_storage": {"L", "m³", "mL", "gal"},
    "water": {"L", "m³", "gal"},
    "power_factor": {"%", None},
    "battery": {"%"},
    "wind_speed": {"m/s", "km/h"},
    "irradiance": {"W/m²"},
}

BASE = coordinator_scenarios()["coord_minimal"]
STATES = {
    "sensor.indoor": "21.4", "sensor.outdoor": "-3.0", "sensor.tank": "48.0",
    "sensor.hp_power": "1.2",
    "sensor.upper": "21.0", "sensor.lower": "21.6", "sensor.wood_top": "70",
    "sensor.wood_bottom": "40", "sensor.house_power": "2.0", "sensor.pv": "0.5",
    "binary_sensor.home": "on",
}
COMMON = {
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
}
OVERLAYS = {
    "dhw": {"dhw_tank_volume": 200.0, "dhw_setpoint": 55.0, "dhw_min_temperature": 45.0,
            "dhw_temp_entity": "sensor.tank"},
    "two_zone": coordinator_scenarios()["coord_two_zone"],
    "valve_storage": {"dhw_tank_volume": 200.0, const.CONF_TOPOLOGY_LAYOUT: const.TOPOLOGY_SINGLE_TANK_VALVE},
    "two_tank": {"dhw_tank_volume": 200.0, const.CONF_TOPOLOGY_LAYOUT: const.TOPOLOGY_TWO_TANK_4WAY,
                 "buffer_tank_volume": 300.0},
    "coil": {"dhw_tank_volume": 200.0, const.CONF_DHW_WOOD_COIL_ENABLED: True,
             const.CONF_WOOD_FURNACE_ENABLED: True},
    "wood": {const.CONF_WOOD_FURNACE_ENABLED: True, const.CONF_WOOD_TANK_TOP_ENTITY: "sensor.wood_top",
             const.CONF_WOOD_TANK_BOTTOM_ENTITY: "sensor.wood_bottom", const.CONF_WOOD_TANK_VOLUME: 500.0},
    "ecl110": {const.CONF_ECL110_DISPLACE_SET_TOPIC: "ecl/set", const.CONF_ECL110_STATE_TOPIC: "ecl/state"},
    "pv": {"pv_enabled": True, "pv_peak_kw": 8.0, "pv_export_price": 0.3,
           const.CONF_PV_PRODUCTION_ENTITY: "sensor.pv"},
    "capacity": {"peak_tariff_enabled": True, "peak_tariff_price_per_kw": 45.0,
                 const.CONF_HOUSE_POWER_ENTITY: "sensor.house_power"},
    "grid_fee": coordinator_scenarios()["coord_grid_fee"],
    "tuya_dhw_only": {"dhw_tank_volume": 200.0, "dhw_temp_entity": "sensor.tank",
                      const.CONF_HEAT_PUMP_MODE_ENTITY: "select.hp_mode"},
    "min_modulation": {const.CONF_HEAT_PUMP_MAX_POWER: 12.0, const.CONF_HEAT_PUMP_MIN_POWER: 1.0},
    "tuya_dhw_only_min": {"dhw_tank_volume": 200.0, "dhw_temp_entity": "sensor.tank",
                          const.CONF_HEAT_PUMP_MODE_ENTITY: "select.hp_mode",
                          const.CONF_HEAT_PUMP_MAX_POWER: 12.0, const.CONF_HEAT_PUMP_MIN_POWER: 1.0},
    "away": {"away_enabled": True, const.CONF_AWAY_PRESENCE_ENTITY: "binary_sensor.home"},
}


SWEEP = 16
SWEEP_CELLS = {"min+tuya_dhw_only", "min+tuya_dhw_only_min", "min+min_modulation", "coord_dhw", "coord_all_features"}


def cells():
    out = {}
    for name, cfg in coordinator_scenarios().items():
        out[name] = {**cfg, **COMMON}
    for name, ov in OVERLAYS.items():
        out[f"min+{name}"] = {**BASE, **COMMON, **ov}
    return out


def _seed(coord, shift):
    coord._prices = [
        {"total": round(0.6 + 0.5 * ((h + shift) % 12) / 12.0 + 0.1 * shift, 4),
         "starts_at": (START + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
        for h in range(48)
    ]
    coord._weather_forecast = [
        {"datetime": (START + timedelta(hours=h)).isoformat(),
         "temperature": -5.0 - 2.0 * shift + 3.0 * (h % 24) / 24.0,
         "wind_speed": 3.0, "precipitation": 0.0, "humidity": 85.0}
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)]


def build(cfg, patch=None, sweep=0):
    states = {k: FakeState(v) for k, v in STATES.items()}
    states["select.hp_mode"] = FakeState("DHW (Hot Water)", attributes={"options": [
        "Cooling", "Heating", "DHW (Hot Water)", "Cooling + DHW", "Heating + DHW"]})
    hass = FakeHass(states)
    entry = FakeEntry(data=dict(cfg))
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    entry.runtime_data = coord
    _seed(coord, 0)
    snaps = []

    async def first():
        await coord._update_current_state()
        coord.data = coord._build_data_dict()

    async def _noop(*_a, **_k):
        return None

    for _name in ("_fetch_tibber_prices", "_fetch_weather_forecast",
                  "_fetch_solar_forecast", "_async_learn_price_shape"):
        setattr(coord, _name, _noop)
    coord._skip_solve_once = False

    async def cycle():
        # The production cycle (HA's _async_update_data), network fetches stubbed.
        coord.data = await coord._async_update_data()
        if patch:
            patch(coord)

    asyncio.run(first())
    asyncio.run(cycle())
    snaps.append(snapshot(hass, entry, coord))
    _seed(coord, 1)
    hass.states._states["sensor.indoor"] = FakeState("20.6")
    hass.states._states["sensor.outdoor"] = FakeState("-7.0")
    hass.states._states["sensor.tank"] = FakeState("38.0")
    asyncio.run(cycle())
    snaps.append(snapshot(hass, entry, coord))
    if sweep:
        # Walk the clock a quarter-hour at a time so the operating-state
        # oracle meets DHW-only and minimum-modulation steps, not only step 0.
        for k in range(1, sweep + 1):
            dt_util.freeze(START + timedelta(minutes=15 * k))
            asyncio.run(cycle())
            snaps.append(snapshot(hass, entry, coord))
        dt_util.freeze(START)
    return coord, snaps


def _entities(hass, entry):
    out = []
    for mod in (sensor, binary_sensor, button, climate, switch):
        added = []

        def add(ents, *_a, **_k):
            for e in ents:
                e.hass = hass
            added.extend(ents)

        asyncio.run(mod.async_setup_entry(hass, entry, add))
        out += [(mod.__name__.rsplit(".", 1)[-1], e) for e in added]
    return out


def _state(platform, e):
    if platform == "sensor":
        return e.native_value
    if platform in ("binary_sensor", "switch"):
        return e.is_on
    if platform == "climate":
        return e.hvac_action
    return None


def enabled_default(e):
    return bool(getattr(e, "entity_registry_enabled_default",
                        getattr(e, "_attr_entity_registry_enabled_default", True)))


def snapshot(hass, entry, coord):
    snap = {}
    for platform, e in _entities(hass, entry):
        key = f"{platform}:{getattr(e, '_attr_translation_key', None) or type(e).__name__}"
        try:
            st = _state(platform, e)
            err = None
        except Exception as exc:  # noqa: BLE001
            st, err = None, f"{type(exc).__name__}: {exc}"
        try:
            attrs = e.extra_state_attributes if hasattr(e, "extra_state_attributes") else None
        except Exception as exc:  # noqa: BLE001
            attrs, err = None, err or f"attrs {type(exc).__name__}: {exc}"
        snap[key] = {
            "platform": platform, "cls": type(e).__name__, "state": st, "attrs": attrs, "err": err,
            "available": getattr(e, "available", True),
            "dc": str(getattr(e, "device_class", None) or getattr(e, "_attr_device_class", None) or "") or None,
            "sc": str(getattr(e, "_attr_state_class", None) or "") or None,
            "unit": getattr(e, "_attr_native_unit_of_measurement", None)
            if platform == "sensor" else getattr(e, "_attr_unit_of_measurement", None),
            "options": getattr(e, "_attr_options", None),
            "tk": getattr(e, "_attr_translation_key", None),
            "cat": getattr(e, "_attr_entity_category", None),
            "on": enabled_default(e),
            "uid": getattr(e, "_attr_unique_id", None),
        }
    ca = dict((coord.data or {}).get("current_action") or {})
    snap["__action__"] = {"platform": "_", "state": ca, "err": None}
    return snap


def oracle(cell, snap):
    """Operating-state entities against the plan's own draw (D8.M2)."""
    out = []
    ca = snap["__action__"]["state"]
    space = float(ca.get("power") or 0.0)
    dhw = float(ca.get("dhw_power") or 0.0)
    on = bool(ca.get("heat_pump_on"))
    running = on and (space + dhw) > 0.05
    st = {k: r["state"] for k, r in snap.items()}
    hv = st.get("climate:heat_pump_optimizer")
    if hv is not None and (str(hv).endswith("heating") or str(hv) == "heating") != running:
        out.append(("climate_action_vs_plan", f"{cell}|climate", f"hvac_action={hv} space={space} dhw={dhw} on={on}"))
    rp = st.get("sensor:recommended_power")
    want = round(space + dhw, 2) if on else 0.0
    if rp is not None and abs(float(rp) - want) > 0.011:
        out.append(("recommended_power_vs_plan", f"{cell}|recommended_power", f"{rp} vs {want}"))
    sp = st.get("sensor:plan_space_heating")
    if sp == "heating now" and not (on and space > 0.05):
        out.append(("space_plan_heating_vs_plan", f"{cell}|plan_space_heating", f"space={space} dhw={dhw} on={on}"))
    if sp not in (None, "heating now") and on and space > 0.05:
        out.append(("space_plan_idle_vs_plan", f"{cell}|plan_space_heating", f"{sp}; space={space} on={on}"))
    dp = st.get("sensor:plan_dhw_heating")
    if dp == "heating now" and not (on and dhw > 0.05):
        out.append(("dhw_plan_heating_vs_plan", f"{cell}|plan_dhw_heating", f"space={space} dhw={dhw} on={on}"))
    if dp not in (None, "heating now") and on and dhw > 0.05:
        out.append(("dhw_plan_idle_vs_plan", f"{cell}|plan_dhw_heating", f"{dp}; dhw={dhw} on={on}"))
    hpa = st.get("sensor:heat_pump_action")
    if hpa in ("idle", "off") and running:
        out.append(("action_mode_vs_plan", f"{cell}|heat_pump_action", f"{hpa} while drawing {space + dhw}"))
    return out


def _norm(x):
    s = str(x) if x is not None else None
    if s and "." in s and s.split(".")[0].isupper():
        s = s.split(".", 1)[1].lower()
    return s


def _nonserial(v, path, out):
    if isinstance(v, (np.generic, np.ndarray)):
        out.append(f"{path}:{type(v).__name__}")
    elif isinstance(v, float) and not math.isfinite(v):
        out.append(f"{path}:nonfinite")
    elif isinstance(v, dict):
        for k, x in v.items():
            if not isinstance(k, str):
                out.append(f"{path}.{k}:key-{type(k).__name__}")
            _nonserial(x, f"{path}.{k}", out)
    elif isinstance(v, (list, tuple)):
        for i, x in enumerate(v):
            _nonserial(x, f"{path}[{i}]", out)


def check(cell, snaps):
    viol = []
    a, b = snaps[0], snaps[1]
    for i, sn in enumerate(snaps):
        viol += oracle(f"{cell}@{i}", sn)
    for key, r in b.items():
        if key == "__action__":
            continue
        dc, sc, st = _norm(r["dc"]), _norm(r["sc"]), r["state"]
        tag = f"{cell}|{key}"
        if r["err"]:
            viol.append(("raises", tag, r["err"]))
            continue
        if r["platform"] == "sensor":
            if sc in ("measurement", "total", "total_increasing") and st is not None and (
                    isinstance(st, bool) or not isinstance(st, (int, float))):
                viol.append(("measurement_not_numeric", tag, repr(st)))
            if dc == "timestamp" and st is not None and (
                    not isinstance(st, datetime) or st.tzinfo is None):
                viol.append(("timestamp_not_aware", tag, repr(st)))
            if dc == "enum" and st is not None and st not in (r["options"] or []):
                viol.append(("enum_not_in_options", tag, repr(st)))
            if dc in UNITS and r["unit"] not in UNITS[dc]:
                viol.append(("unit_vs_device_class", tag, f"{dc}/{r['unit']}"))
            if dc == "monetary" and sc == "measurement":
                viol.append(("monetary_measurement", tag, sc))
        if r["tk"] and r["tk"] not in STRINGS.get(r["platform"], {}):
            viol.append(("untranslated", tag, r["tk"]))
        bad = []
        _nonserial(st, "state", bad)
        _nonserial(r["attrs"], "attrs", bad)
        if orjson is not None:
            try:
                orjson.dumps({"s": st if not isinstance(st, datetime) else st.isoformat(), "a": r["attrs"]},
                             option=orjson.OPT_NON_STR_KEYS | orjson.OPT_PASSTHROUGH_DATETIME,
                             default=lambda o: o.isoformat() if hasattr(o, "isoformat") else (_ for _ in ()).throw(TypeError(type(o).__name__)))
            except Exception as exc:  # noqa: BLE001
                bad.append(f"orjson:{exc}")
        if bad:
            viol.append(("not_serialisable", tag, ";".join(bad[:3])))
        if r["on"] and r["available"] and st is None and r["platform"] in ("sensor", "binary_sensor"):
            viol.append(("enabled_none", tag, "None"))
    return viol


def main():
    dump = sys.argv[sys.argv.index("--dump") + 1] if "--dump" in sys.argv else None
    t0p, t0t = time.process_time(), time.thread_time()
    dt_util.freeze(START)
    allv = []
    unchanged = {}
    try:
        for cell, cfg in cells().items():
            coord, snaps = build(cfg, sweep=SWEEP if cell in SWEEP_CELLS else 0)
            v = check(cell, snaps)
            allv += v
            print("ACTION", cell, snaps[0]["__action__"]["state"].get("mode"),
                  {k: snaps[1]["__action__"]["state"].get(k) for k in ("mode", "power", "dhw_power", "power_normalized", "heat_pump_on")})
            for k, r in snaps[1].items():
                if k == "__action__":
                    continue
                same = repr(r["state"]) == repr(snaps[0].get(k, {}).get("state"))
                unchanged.setdefault(k, []).append(same)
            if dump == cell:
                for k, r in sorted(x for x in snaps[1].items() if x[0] != "__action__"):
                    print("DUMP", k, repr(snaps[0].get(k, {}).get("state")), "->", repr(r["state"]),
                          r["dc"], r["sc"], r["unit"], "on" if r["on"] else "off",
                          "avail" if r["available"] else "UNAVAIL")
                ca = coord.data.get("current_action")
                print("DUMP current_action", {k: ca.get(k) for k in ("mode", "power", "dhw_power", "power_normalized", "heat_pump_on")})
    finally:
        dt_util.freeze(None)
    from collections import Counter
    c = Counter(x[0] for x in allv)
    for cls, tag, det in sorted(allv):
        print("VIOL", cls, tag, det)
    for k, lst in sorted(unchanged.items()):
        if all(lst):
            print("STATIC", k)
    for cls in ("raises", "measurement_not_numeric", "timestamp_not_aware", "enum_not_in_options",
                "unit_vs_device_class", "monetary_measurement", "untranslated", "not_serialisable",
                "enabled_none", "climate_action_vs_plan", "recommended_power_vs_plan",
                "space_plan_heating_vs_plan", "space_plan_idle_vs_plan", "dhw_plan_heating_vs_plan",
                "dhw_plan_idle_vs_plan", "action_mode_vs_plan"):
        print(f"RESULT {cls}={c.get(cls, 0)} count")
    print(f"RESULT cells={len(cells())} count")
    tf = (time.process_time() - t0p) / max(time.thread_time() - t0t, 1e-9)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
