"""D1-s2 round 11, D1.M3: staleness per d1-inputs line, the watchdog and the age readings.

Metric (one line): per configured input slot, on a real asyncio loop and the
real ``_async_update_data`` cycle, the watchdog's reading of the slot
(``coord._input_health.readings``) and the published ``input_ages_minutes`` /
``problem_inputs`` after: (h) healthy, (u) unavailable, (r) back with a new
value inside one interval, (k) unknown, (f) ``last_reported`` 90 min in the
future, (j) the host clock jumped back 2 h after a healthy read, (s) the clock
jumped 6 h forward with no new report. Counted defects per slot:
  stale_after_return   (r) reading not ok, or its value is not the new value
  missing_not_flagged  (u)/(k) reading ok -- a dead input read as measured
  future_accepted      (f) reading ok with a negative age, or a negative published age
  neg_age_after_jump   (j) a negative age published
  stale_not_flagged    (s) reading ok past its own max_age_minutes
  unread               the slot never reaches the watchdog (reported, not a defect by itself)
Count key: the watchdog's own InputReading (value, ok, age_minutes) and the
published payload, never the planted state.

Command:
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/s2/staleness.py [--slots CONF_A,CONF_B] [--verbose]
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (export). Machine: macOS arm64, shared box.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d1s2_lib as L  # noqa: E402

import argparse  # noqa: E402
import asyncio  # noqa: E402
import subprocess  # noqa: E402
import time  # noqa: E402
from datetime import timedelta  # noqa: E402

C = L.const
FakeState = L.FakeState

TEMP = ("sensor", "21.0", {"unit_of_measurement": "°C", "device_class": "temperature"})
DOMAIN_OF = {
    "CONF_PRICE_ENTITY": ("sensor", "1.10", {"unit_of_measurement": "SEK/kWh"}),
    "CONF_WEATHER_ENTITY": ("weather", "cloudy", {"temperature": -3.0, "humidity": 80, "wind_speed": 3.0}),
    "CONF_HEAT_PUMP_SWITCH_ENTITY": ("switch", "on", {}),
    "CONF_SPACE_SETPOINT_ENTITY": ("number", "21.0", {"unit_of_measurement": "°C"}),
    "CONF_SOLAR_RADIATION_ENTITY": ("sensor", "120", {"unit_of_measurement": "W/m²"}),
    "CONF_POWER_ENTITY": ("sensor", "1500", {"unit_of_measurement": "W", "device_class": "power"}),
    "CONF_THERMAL_POWER_ENTITY": ("sensor", "4500", {"unit_of_measurement": "W", "device_class": "power"}),
    "CONF_ENERGY_ENTITY": ("sensor", "1234.5", {"unit_of_measurement": "kWh", "device_class": "energy", "state_class": "total_increasing"}),
    "CONF_HEAT_ENERGY_ENTITY": ("sensor", "3456.5", {"unit_of_measurement": "kWh", "device_class": "energy", "state_class": "total_increasing"}),
    "CONF_HOUSE_POWER_ENTITY": ("sensor", "2500", {"unit_of_measurement": "W", "device_class": "power"}),
    "CONF_COMPRESSOR_FREQ_ENTITY": ("number", "40", {"unit_of_measurement": "Hz"}),
    "CONF_COMPRESSOR_FREQ_SENSOR": ("sensor", "40", {"unit_of_measurement": "Hz", "device_class": "frequency"}),
    "CONF_FLOW_METER_ENTITY": ("sensor", "12.0", {"unit_of_measurement": "L/min"}),
    "CONF_HEAT_PUMP_MODE_ENTITY": ("select", "heating", {"options": ["heating", "hot_water", "off"]}),
    "CONF_HEAT_PUMP_DEFROST_ENTITY": ("binary_sensor", "off", {}),
    "CONF_HEAT_PUMP_ONLINE_ENTITY": ("binary_sensor", "on", {}),
    "CONF_HEAT_PUMP_FAULT_ENTITY": ("binary_sensor", "off", {}),
    "CONF_HEAT_PUMP_BACKUP_HEATER_ENTITY": ("binary_sensor", "off", {}),
    "CONF_HEAT_PUMP_DHW_BOOSTER_ENTITY": ("binary_sensor", "off", {}),
    "CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY": ("binary_sensor", "off", {}),
    "CONF_INDOOR_HUMIDITY_ENTITY": ("sensor", "45", {"unit_of_measurement": "%", "device_class": "humidity"}),
    "CONF_DHW_SETPOINT_ENTITY": ("number", "50", {"unit_of_measurement": "°C"}),
    "CONF_DHW_HYSTERESIS_ENTITY": ("number", "5", {"unit_of_measurement": "K"}),
    "CONF_SPACE_HYSTERESIS_ENTITY": ("number", "2", {"unit_of_measurement": "K"}),
    "CONF_DHW_DISINFECTION_SWITCH_ENTITY": ("switch", "off", {}),
    "CONF_VVC_PUMP_ENTITY": ("switch", "on", {}),
    "CONF_MIXING_VALVE_WRITE_ENTITY": ("number", "35", {"unit_of_measurement": "°C"}),
    "CONF_EXTERNAL_HEAT_ENTITY": ("binary_sensor", "off", {}),
    "CONF_SPACE_PUMP_ENTITY": ("switch", "on", {}),
    "CONF_HEAT_CURVE_DISPLACE_ENTITY": ("number", "0", {}),
    "CONF_GRID_FEE_ENTITY": ("sensor", "0.25", {"unit_of_measurement": "SEK/kWh"}),
    "CONF_PV_EXPORT_PRICE_ENTITY": ("sensor", "0.40", {"unit_of_measurement": "SEK/kWh"}),
    "CONF_PV_PRODUCTION_ENTITY": ("sensor", "800", {"unit_of_measurement": "W", "device_class": "power"}),
    "CONF_AWAY_PRESENCE_ENTITY": ("binary_sensor", "on", {}),
    "CONF_AWAY_RETURN_ENTITY": ("sensor", "2026-01-25T12:00:00+00:00", {"device_class": "timestamp"}),
    "CONF_HOLIDAY_CALENDAR_ENTITY": ("calendar", "off", {}),
    "CONF_DHW_TEMP_ENTITY": ("sensor", "50.0", {"unit_of_measurement": "°C", "device_class": "temperature"}),
    "CONF_DHW_INLET_ENTITY": ("sensor", "8.0", {"unit_of_measurement": "°C", "device_class": "temperature"}),
    "CONF_BUFFER_TANK_TEMP_ENTITY": ("sensor", "40.0", {"unit_of_measurement": "°C", "device_class": "temperature"}),
    "CONF_HEAT_PUMP_SUPPLY_TEMP_ENTITY": ("sensor", "35.0", {"unit_of_measurement": "°C", "device_class": "temperature"}),
    "CONF_HEAT_PUMP_RETURN_TEMP_ENTITY": ("sensor", "30.0", {"unit_of_measurement": "°C", "device_class": "temperature"}),
    "CONF_FLOOR_RETURN_TEMP_ENTITY": ("sensor", "28.0", {"unit_of_measurement": "°C", "device_class": "temperature"}),
    "CONF_MIXING_VALVE_TARGET_ENTITY": ("sensor", "35.0", {"unit_of_measurement": "°C", "device_class": "temperature"}),
    "CONF_VALVE_OUTLET_TEMP_ENTITY": ("sensor", "60.0", {"unit_of_measurement": "°C", "device_class": "temperature"}),
    "CONF_WOOD_TANK_TOP_ENTITY": ("sensor", "70.0", {"unit_of_measurement": "°C", "device_class": "temperature"}),
    "CONF_WOOD_TANK_BOTTOM_ENTITY": ("sensor", "40.0", {"unit_of_measurement": "°C", "device_class": "temperature"}),
    "CONF_SPACE_SETPOINT_LOW_LIMIT_ENTITY": ("sensor", "20.0", {"unit_of_measurement": "°C", "device_class": "temperature"}),
    "CONF_SPACE_SETPOINT_HIGH_LIMIT_ENTITY": ("sensor", "50.0", {"unit_of_measurement": "°C", "device_class": "temperature"}),
    "CONF_LOWER_FLOOR_TEMP_ENTITY": ("sensor", "20.5", {"unit_of_measurement": "°C", "device_class": "temperature"}),
    "CONF_INDOOR_TEMP_ENTITY": ("sensor", "21.4", {"unit_of_measurement": "°C", "device_class": "temperature"}),
    "CONF_OUTDOOR_TEMP_ENTITY": ("sensor", "-3.0", {"unit_of_measurement": "°C", "device_class": "temperature"}),
}
#: Gates a slot needs before anything reads it (the config flow's ``when=``).
GATES = {
    "CONF_VALVE_OUTLET_TEMP_ENTITY": {"wood_furnace_enabled": True},
    "CONF_WOOD_TANK_TOP_ENTITY": {"wood_furnace_enabled": True},
    "CONF_WOOD_TANK_BOTTOM_ENTITY": {"wood_furnace_enabled": True},
    "CONF_EXTERNAL_HEAT_ENTITY": {"wood_furnace_enabled": True},
}


def enumerate_slots():
    out = subprocess.run([sys.executable, "tools/audit/enumerate.py", "d1-inputs"], capture_output=True, text=True, check=True)
    return [line.split()[1] for line in out.stdout.splitlines() if line.startswith("input ")]


def bumped(value: str) -> str:
    try:
        return f"{float(value) + 0.5:.1f}"
    except ValueError:
        return value


def mkstate(dom, st, attrs, stamp, reported=None):
    return FakeState(st, attributes=dict(attrs), last_updated=stamp, last_reported=reported or stamp)


def reading_for(coord, eid):
    h = coord._input_health
    if h is None:
        return None
    for k, r in h.readings.items():
        if r.entity_id == eid:
            return k, r
    return None


async def cycle(coord, hass):
    try:
        d = await coord._async_update_data()
        err = None
    except Exception as e:  # noqa: BLE001
        d, err = None, f"{type(e).__name__}: {e}"
    await L.drain(hass)
    return d, err


async def drive(slot: str, verbose=False):
    key = getattr(C, slot)
    dom, st, attrs = DOMAIN_OF.get(slot, TEMP)
    eid = f"{dom}.probe_{key}"
    base = L.base_states()
    t0 = L.T0
    base = {k: mkstate("sensor", v.state, {"unit_of_measurement": "°C", "device_class": "temperature"}, t0)
            for k, v in base.items()}
    states = dict(base)
    states[eid] = mkstate(dom, st, attrs, t0 - timedelta(minutes=1))
    cfg = L.base_config({key: eid, **GATES.get(slot, {})})
    if slot in ("CONF_INDOOR_TEMP_ENTITY", "CONF_OUTDOOR_TEMP_ENTITY"):
        states.pop("sensor.indoor" if slot == "CONF_INDOOR_TEMP_ENTITY" else "sensor.outdoor", None)
    hass = L.SchedHass(states)
    coord = L.HeatPumpOptimizerCoordinator(hass, L.FakeEntry(data=cfg))
    await L.drain(hass)
    res = {"slot": slot, "eid": eid}
    now = t0

    def at(minutes):
        nonlocal now
        now = t0 + timedelta(minutes=minutes)
        L.dtu.freeze(now)
        for k in base:  # the healthy core keeps reporting
            hass.states.set(k, mkstate("sensor", base[k].state, base[k].attributes, now))

    def pub_age(d):
        if not d:
            return None
        hit = reading_for(coord, eid)
        return (d.get("input_ages_minutes") or {}).get(hit[0]) if hit else None

    def snap(tag, d, err):
        hit = reading_for(coord, eid)
        r = hit[1] if hit else None
        res[tag] = {"err": err, "read": bool(hit), "ok": (r.ok if r else None), "value": (r.value if r else None),
                    "text": (r.text if r else None), "age": (r.age_minutes if r else None), "problem": (r.problem if r else None), "max_age": (r.max_age_minutes if r else None),
                    "pub_age": pub_age(d), "in_problems": bool(d and eid in (d.get("problem_inputs") or []))}

    at(0)
    hass.states.set(eid, mkstate(dom, st, attrs, now - timedelta(minutes=1)))
    snap("h", *await cycle(coord, hass))
    at(5)
    hass.states.set(eid, mkstate(dom, "unavailable", attrs, now))
    snap("u", *await cycle(coord, hass))
    at(10)
    new = bumped(st)
    hass.states.set(eid, mkstate(dom, new, attrs, now))
    snap("r", *await cycle(coord, hass))
    res["new"] = new
    at(15)
    hass.states.set(eid, mkstate(dom, "unknown", attrs, now))
    snap("k", *await cycle(coord, hass))
    at(20)
    hass.states.set(eid, mkstate(dom, st, attrs, now, reported=now + timedelta(minutes=90)))
    snap("f", *await cycle(coord, hass))
    at(25)
    hass.states.set(eid, mkstate(dom, st, attrs, now))
    snap("h2", *await cycle(coord, hass))
    # host clock back 2 h: every stamp now lies ahead of the clock
    at(25 - 120)
    snap("j", *await cycle(coord, hass))
    # forward 7 h with no new report from the probe
    at(25 + 420)
    snap("s", *await cycle(coord, hass))
    await coord.async_shutdown()
    await L.drain(hass, 5)
    return res


def classify(res):
    kinds = []
    if not res["h"]["read"]:
        return ["unread"]
    r = res["r"]
    if not r["ok"]:
        kinds.append("stale_after_return")
    elif res["new"] != DOMAIN_OF.get(res["slot"], TEMP)[1] and r["value"] is not None \
            and r["value"] == res["h"]["value"]:
        kinds.append("stale_after_return")
    s = res["s"]
    if s["ok"] and s["age"] is not None and isinstance(s["max_age"], (int, float)) and s["age"] > s["max_age"]:
        kinds.append("stale_not_flagged")
    for t in ("u", "k"):
        if res[t]["ok"]:
            kinds.append("missing_not_flagged")
            break
    f = res["f"]
    if (f["ok"] and f["age"] is not None and f["age"] < 0) or (f["pub_age"] is not None and f["pub_age"] < 0):
        kinds.append("future_accepted")
    j = res["j"]
    if (j["pub_age"] is not None and j["pub_age"] < 0) or (j["ok"] and j["age"] is not None and j["age"] < 0):
        kinds.append("neg_age_after_jump")
    for t in ("h", "u", "r", "k", "f", "h2", "j", "s"):
        if res[t]["err"]:
            kinds.append("cycle_fail")
            break
    return kinds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slots", default="")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    proc0, thr0 = time.process_time(), time.thread_time()
    slots = [s for s in a.slots.split(",") if s] or enumerate_slots()
    totals = {}
    for slot in slots:
        L.reset_globals()
        ps = L.patches() + L.price_patches()
        for p in ps:
            p.start()
        L.dtu.freeze(L.T0)
        try:
            res = asyncio.run(drive(slot, a.verbose))
            kinds = classify(res)
        except Exception as e:  # noqa: BLE001
            res, kinds = {"exc": repr(e)}, ["harness_error"]
        finally:
            L.dtu.freeze(None)
            for p in ps:
                p.stop()
        for k in kinds:
            totals[k] = totals.get(k, 0) + 1
        print(f"SLOT {slot}: {','.join(kinds) or 'held'}")
        if a.verbose or (kinds and kinds != ["unread"]):
            for t in ("h", "u", "r", "k", "f", "h2", "j", "s"):
                if t in res:
                    print(f"   {t}: {res[t]}")
            if "exc" in res:
                print("   ", res["exc"])
    print(f"RESULT slots={len(slots)} count")
    for k in ("unread", "stale_after_return", "missing_not_flagged", "future_accepted",
              "neg_age_after_jump", "stale_not_flagged", "cycle_fail", "harness_error"):
        print(f"RESULT {k}={totals.get(k, 0)} count")
    print(f"RESULT thread_factor={L.thread_factor(proc0, thr0):.3f}")
    print(f"RESULT load1={L.load_avg():.2f}")
    print(f"RESULT swapins={L.swapins()}")


if __name__ == "__main__":
    main()
