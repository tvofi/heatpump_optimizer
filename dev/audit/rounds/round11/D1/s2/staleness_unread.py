"""D1-s2 round 11, D1.M3: staleness for the d1-inputs slots the coordinator's watchdog never reads.

Metric (one line): per slot that staleness.py reports `unread`, through the
same phases on a real asyncio loop and the real cycle -- (h) healthy, (u)
unavailable, (r) back with a new value in one interval, (k) unknown, (f)
last_reported 90 min ahead, (s) 7 h with no report -- the value its own
consumer returns: an ``inputs.InputReader`` reading of it (any reader
instance, spied at ``InputReader._begin``), else the production getter named
in CONSUMERS. Counted defects per slot:
  dead_used            (u)/(k) the consumer still returns the healthy value
  stale_after_return   (r) the consumer does not return the new value
  past_limit_used      (s)/(f) a slot with a declared age limit
                       (const.INPUT_MAX_AGE_MINUTES / DHW_INLET_MAX_AGE_MINUTES)
                       still returns the old value
Slots with no read path at all are reported `write_only`/`no_consumer`.
Count key: the consumer's return value / the InputReading, never the state.

Command:
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/s2/staleness_unread.py [--slots A,B]
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (export). Machine: macOS arm64, shared box.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d1s2_lib as L  # noqa: E402

import argparse  # noqa: E402
import asyncio  # noqa: E402
import time  # noqa: E402
from datetime import timedelta  # noqa: E402

import staleness as S  # noqa: E402
from heatpump_optimizer import inputs as inputs_mod  # noqa: E402
from heatpump_optimizer import away as away_mod  # noqa: E402

C = L.const
CM = L.coord_mod

UNREAD = ["CONF_AWAY_PRESENCE_ENTITY", "CONF_AWAY_RETURN_ENTITY", "CONF_COMPRESSOR_FREQ_ENTITY",
          "CONF_COMPRESSOR_FREQ_SENSOR", "CONF_DHW_HYSTERESIS_ENTITY", "CONF_DHW_INLET_ENTITY",
          "CONF_DHW_SETPOINT_ENTITY", "CONF_EXTERNAL_HEAT_ENTITY", "CONF_GRID_FEE_ENTITY",
          "CONF_HEAT_CURVE_DISPLACE_ENTITY", "CONF_HEAT_PUMP_SWITCH_ENTITY", "CONF_HOLIDAY_CALENDAR_ENTITY",
          "CONF_INDOOR_HUMIDITY_ENTITY", "CONF_MIXING_VALVE_WRITE_ENTITY", "CONF_PRICE_ENTITY",
          "CONF_PV_EXPORT_PRICE_ENTITY", "CONF_PV_PRODUCTION_ENTITY", "CONF_SPACE_HYSTERESIS_ENTITY",
          "CONF_SPACE_PUMP_ENTITY", "CONF_SPACE_SETPOINT_ENTITY", "CONF_SPACE_SETPOINT_HIGH_LIMIT_ENTITY",
          "CONF_SPACE_SETPOINT_LOW_LIMIT_ENTITY", "CONF_VALVE_OUTLET_TEMP_ENTITY", "CONF_VVC_PUMP_ENTITY",
          "CONF_WEATHER_ENTITY", "CONF_WOOD_TANK_BOTTOM_ENTITY", "CONF_WOOD_TANK_TOP_ENTITY"]

GATES = {
    **S.GATES,
    "CONF_PV_PRODUCTION_ENTITY": {"pv_enabled": True, "pv_peak_kw": 6.0},
    "CONF_PV_EXPORT_PRICE_ENTITY": {"pv_enabled": True, "pv_peak_kw": 6.0},
    "CONF_AWAY_PRESENCE_ENTITY": {"away_enabled": True},
    "CONF_HOLIDAY_CALENDAR_ENTITY": {"away_enabled": True},
    "CONF_INDOOR_HUMIDITY_ENTITY": {"mold_guard_enabled": True},
    "CONF_SPACE_SETPOINT_HIGH_LIMIT_ENTITY": {"space_setpoint_unit": "flow", "space_setpoint_entity": "number.sp",
                                              "pump_duty_mode": "control"},
    "CONF_SPACE_SETPOINT_LOW_LIMIT_ENTITY": {"space_setpoint_unit": "flow", "space_setpoint_entity": "number.sp",
                                             "pump_duty_mode": "control"},
    "CONF_PRICE_ENTITY": {"price_source": "entity"},
}
#: A healthy state that exercises the consumer (a calendar that is on).
DOMAIN_OVERRIDE = {
    # the numeric arm of the slot (a probe); its flag arm is read unbounded by design (const.py)
    "CONF_EXTERNAL_HEAT_ENTITY": ("sensor", "45.0", {"unit_of_measurement": "°C", "device_class": "temperature"}),
    "CONF_HOLIDAY_CALENDAR_ENTITY": ("calendar", "on", {"start_time": "2026-01-20 00:00:00",
                                                        "end_time": "2026-01-23 00:00:00", "message": "holiday"}),
}

#: The production getter each direct-read slot's consumer calls (consumers.py's CONSUMER lines).
CONSUMERS = {
    "CONF_PV_PRODUCTION_ENTITY": lambda co, h, e: co._pv_measured_production(co._pv_config()),
    "CONF_DHW_INLET_ENTITY": lambda co, h, e: CM._dhw_inlet_c(h, e),
    "CONF_GRID_FEE_ENTITY": lambda co, h, e: CM._entity_price(h, e),
    "CONF_PV_EXPORT_PRICE_ENTITY": lambda co, h, e: CM._entity_price(h, e),
    "CONF_COMPRESSOR_FREQ_ENTITY": lambda co, h, e: co._freq_entity_reading()[0],
    "CONF_COMPRESSOR_FREQ_SENSOR": lambda co, h, e: co._freq_entity_reading()[0],
    "CONF_DHW_HYSTERESIS_ENTITY": lambda co, h, e: inputs_mod.read_temperature_delta_k(h, e),
    "CONF_SPACE_HYSTERESIS_ENTITY": lambda co, h, e: inputs_mod.read_temperature_delta_k(h, e),
    "CONF_DHW_SETPOINT_ENTITY": lambda co, h, e: inputs_mod.read_setpoint(h, e),
    "CONF_SPACE_SETPOINT_ENTITY": lambda co, h, e: inputs_mod.read_setpoint(h, e),
    "CONF_HEAT_CURVE_DISPLACE_ENTITY": lambda co, h, e: getattr(inputs_mod.number_reading(h, e), "value", None),
    "CONF_HOLIDAY_CALENDAR_ENTITY": lambda co, h, e: sorted(away_mod.holiday_dates(h, e, L.dtu.now())),
    "CONF_AWAY_PRESENCE_ENTITY": lambda co, h, e: co._entity_state(e),
    "CONF_HEAT_PUMP_SWITCH_ENTITY": lambda co, h, e: getattr(h.states.get(e), "state", None),
    # the pump-duty arbiter's own reader (pump_arbiter._reader), as _setpoint_limits_c reads them
    "CONF_SPACE_SETPOINT_HIGH_LIMIT_ENTITY": lambda co, h, e: _arb_read(co, h, C.CONF_SPACE_SETPOINT_HIGH_LIMIT_ENTITY),
    "CONF_SPACE_SETPOINT_LOW_LIMIT_ENTITY": lambda co, h, e: _arb_read(co, h, C.CONF_SPACE_SETPOINT_LOW_LIMIT_ENTITY),
}


def _arb_read(co, h, key):
    from heatpump_optimizer import pump_arbiter as PA
    r = PA._reader(h, dict(co.entry.data)).read(key)
    return r.value if r.ok else None
DECLARED_LIMIT = {"CONF_PV_PRODUCTION_ENTITY": C.INPUT_MAX_AGE_MINUTES[C.CONF_PV_PRODUCTION_ENTITY],
                  "CONF_DHW_INLET_ENTITY": getattr(CM, "DHW_INLET_MAX_AGE_MINUTES", None)}
#: Minutes since the last report in phase (s): a slot whose limit is longer is not past it there.
S_AGE = 420
WRITE_ONLY = {"CONF_MIXING_VALVE_WRITE_ENTITY", "CONF_SPACE_PUMP_ENTITY", "CONF_VVC_PUMP_ENTITY"}
SPY: dict = {}


async def drive(slot):
    key = getattr(C, slot)
    dom, st, attrs = DOMAIN_OVERRIDE.get(slot) or S.DOMAIN_OF.get(slot, S.TEMP)
    eid = f"{dom}.probe_{key}"
    t0 = L.T0
    base = {k: S.mkstate("sensor", v.state, {"unit_of_measurement": "°C"}, t0) for k, v in L.base_states().items()}
    states = dict(base)
    states[eid] = S.mkstate(dom, st, attrs, t0 - timedelta(minutes=1))
    states["number.sp"] = S.mkstate("number", "35", {"unit_of_measurement": "°C"}, t0)
    hass = L.SchedHass(states)
    coord = L.HeatPumpOptimizerCoordinator(hass, L.FakeEntry(data=L.base_config({key: eid, **GATES.get(slot, {})})))
    await L.drain(hass)
    SPY.clear()
    out = {"eid": eid}

    def at(m):
        now = t0 + timedelta(minutes=m)
        L.dtu.freeze(now)
        for k in base:
            hass.states.set(k, S.mkstate("sensor", base[k].state, base[k].attributes, now))
        return now

    async def phase(tag):
        SPY.pop(eid, None)
        try:
            await coord._async_update_data()
            err = None
        except Exception as e:  # noqa: BLE001
            err = repr(e)[:120]
        await L.drain(hass)
        r = SPY.get(eid)
        cons = None
        if slot in CONSUMERS:
            try:
                cons = CONSUMERS[slot](coord, hass, eid)
            except Exception as e:  # noqa: BLE001
                cons = f"raised {e!r}"[:100]
        out[tag] = {"err": err, "reader": None if r is None else {"ok": r.ok, "value": r.value, "text": r.text,
                                                                  "problem": r.problem, "age": r.age_minutes},
                    "consumer": cons}

    now = at(0)
    hass.states.set(eid, S.mkstate(dom, st, attrs, now - timedelta(minutes=1)))
    await phase("h")
    now = at(5)
    hass.states.set(eid, S.mkstate(dom, "unavailable", attrs, now))
    await phase("u")
    now = at(10)
    new = S.bumped(st)
    out["new"] = new
    hass.states.set(eid, S.mkstate(dom, new, attrs, now))
    await phase("r")
    now = at(15)
    hass.states.set(eid, S.mkstate(dom, "unknown", attrs, now))
    await phase("k")
    now = at(20)
    hass.states.set(eid, S.mkstate(dom, st, attrs, now, reported=now + timedelta(minutes=90)))
    await phase("f")
    now = at(25)
    hass.states.set(eid, S.mkstate(dom, st, attrs, now))
    await phase("h2")
    at(25 + 420)
    await phase("s")
    await coord.async_shutdown()
    await L.drain(hass, 5)
    return out


def val(p):
    if p["reader"] is not None:
        return p["reader"]["value"] if p["reader"]["ok"] else None
    return p["consumer"]


def classify(slot, res):
    if slot in WRITE_ONLY:
        return ["write_only"]
    if all(res[t]["reader"] is None for t in ("h", "u", "r")) and slot not in CONSUMERS:
        return ["no_consumer"]
    kinds = []
    hv = val(res["h"])
    if hv in (None, [], "unavailable"):
        kinds.append("healthy_unread")
        return kinds
    for t in ("u", "k"):
        v = val(res[t])
        if v is not None and v == hv and v not in ([],):
            kinds.append("dead_used")
            break
    if res["new"] != (DOMAIN_OVERRIDE.get(slot) or S.DOMAIN_OF.get(slot, S.TEMP))[1] and val(res["r"]) == hv:
        kinds.append("stale_after_return")
    lim = DECLARED_LIMIT.get(slot)
    if (lim is not None and lim < S_AGE) or (res["s"]["reader"] is not None and slot not in DECLARED_LIMIT):
        for t in ("f", "s"):
            v = val(res[t])
            if v is not None and v == val(res["h2"]):
                kinds.append("past_limit_used")
                break
    if any(res[t]["err"] for t in ("h", "u", "r", "k", "f", "h2", "s")):
        kinds.append("cycle_fail")
    return kinds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slots", default="")
    a = ap.parse_args()
    proc0, thr0 = time.process_time(), time.thread_time()
    real_begin = inputs_mod.InputReader._begin

    def spy_begin(self, key, max_age_minutes, entity_id=None):
        out = real_begin(self, key, max_age_minutes, entity_id)
        if out and out[0] is not None and out[0].entity_id is not None:
            SPY[out[0].entity_id] = out[0]
        return out
    inputs_mod.InputReader._begin = spy_begin
    slots = [s for s in a.slots.split(",") if s] or UNREAD
    totals = {}
    for slot in slots:
        L.reset_globals()
        ps = L.patches() + L.price_patches()
        for p in ps:
            p.start()
        L.dtu.freeze(L.T0)
        try:
            res = asyncio.run(drive(slot))
            kinds = classify(slot, res)
        except Exception as e:  # noqa: BLE001
            res, kinds = {"exc": repr(e)}, ["harness_error"]
        finally:
            L.dtu.freeze(None)
            for p in ps:
                p.stop()
        for k in kinds:
            totals[k] = totals.get(k, 0) + 1
        print(f"SLOT {slot}: {','.join(kinds) or 'held'}")
        for t in ("h", "u", "r", "k", "f", "s"):
            if t in res:
                print(f"   {t}: {res[t]}"[:300])
        if "exc" in res:
            print("   ", res["exc"])
    inputs_mod.InputReader._begin = real_begin
    print(f"RESULT slots={len(slots)} count")
    for k in ("dead_used", "stale_after_return", "past_limit_used", "healthy_unread", "write_only",
              "no_consumer", "cycle_fail", "harness_error"):
        print(f"RESULT {k}={totals.get(k, 0)} count")
    print(f"RESULT thread_factor={L.thread_factor(proc0, thr0):.3f}")
    print(f"RESULT load1={L.load_avg():.2f}")
    print(f"RESULT swapins={L.swapins()}")


if __name__ == "__main__":
    main()
