"""D17-s1 second pass: each option the first sweep (h_sweep.py) saw move nothing, or
whose save the rig had broken, re-run in the plan state its own description names.

Metric: per (option, named state), whether saving the option through its real options
page, restarting (fresh coordinator from the saved entry) and running the stated
number of full cycles (clock +15 min each, solve inline) moves a channel against the
same arm at the form default: plan / writes (hass.services.calls, plus the MQTT
subscriptions and the debug collector rows where the option is wired at entry setup) /
publish (the data dict less a key named like the option). Count key: NOEFFECT when no
channel moves in the named state, the state taken from the option's description.

Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D17/s1/h_states.py [--only step.field ...]
Expected: RESULT states_examined=30, RESULT states_noeffect=3 (learning.system_identification_enabled,
quick_setup.wood_buffer_tank, thermal_model.compressor_modulation) (exact, a count)
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B13
Perturbation: --perturb-ignore drops entry.options before the restart: every option the
flow stores in options becomes NOEFFECT (states_noeffect goes up).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402
from unittest import mock  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig  # noqa: E402
from harness import FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import coordinator as cmod  # noqa: E402

UTC = timezone.utc
THU6 = datetime(2026, 1, 15, 6, 0, tzinfo=UTC)
PLAN_KEYS = ("space_plan", "dhw_plan", "schedule", "current_action", "predicted_cost", "total_cost",
             "dhw_cost", "space_cost", "baseline_cost", "predicted_savings")
VOLATILE = {"last_optimization", "next_optimization", "solve_time_ms"}
PERTURB = "--perturb-ignore" in sys.argv

MODE_ST = {"select.hp_mode": FakeState("heat", attributes={"options": ["heat", "dhw", "heat_dhw", "cool"]})}
FLOW_ST = {"number.flow": FakeState("35", attributes={"min": 20, "max": 60, "step": 0.5})}
HC_ST = {"number.curve": FakeState("0", unit="K", attributes={"min": -10, "max": 10, "step": 0.5})}
HC5_ST = {"number.curve": FakeState("5", unit="K", attributes={"min": -10, "max": 10, "step": 0.5})}
POWER = {"heat_pump_power_entity": "sensor.hp_power"}
POWER_ST = {"sensor.hp_power": FakeState("1500", unit="W")}
PEAK = {"peak_tariff_enabled": True}


def seed_peaks(coord, days=("2026-01-10", "2026-01-11", "2026-01-12"), peaks=(2.0, 2.0, 2.0)):
    t = coord._peak_tracker
    t.month, t.peaks, t.peak_days = "2026-01", list(peaks), list(days)


def seed_peaks_same_day(coord):
    seed_peaks(coord, ("2026-01-15", "2026-01-15", "2026-01-12"), (2.6, 2.4, 2.0))


def seed_sun(coord):
    now = dt_util.now()
    coord._solar_radiation_forecast = [max(0.0, 450.0 * (1 - abs(12 - ((now.hour + h) % 24)) / 4.0))
                                       for h in range(48)]


def learned_day_short_prices(coord):
    """Two complete published days before today (the learner folds complete days), today to 23:00."""
    start = THU6.replace(hour=0) - timedelta(days=2)
    coord._prices = [{"total": round(0.4 + 0.8 * (1 if 7 <= (h % 24) < 20 else 0) + 0.05 * (h % 24) / 24.0, 4),
                      "starts_at": (start + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
                     for h in range(48 + 23)]


def short_prices(coord):
    coord._prices = [p for p in coord._prices
                     if datetime.fromisoformat(p["starts_at"]) < THU6.replace(hour=23, minute=0)]


async def mqtt_post(coord, hass, entry, obs):
    subs = []

    async def fake_sub(_hass, topic, cb, qos=0, **_k):
        subs.append(topic)
        return lambda: None

    with mock.patch.object(cmod.mqtt, "async_subscribe", fake_sub):
        await coord._async_setup_ecl110_state_subscription()
    obs["mqtt_subscriptions"] = subs


async def debugger_post(coord, hass, entry, obs):
    from heatpump_optimizer import debugger
    entry.async_create_background_task = lambda h, coro, name=None: hass.async_create_task(coro)
    await debugger.async_setup_debugger(hass, entry, coord)
    col = debugger.collector_for(coord)
    obs["debug_collector"] = None if col is None else "present"
    obs["_collector"] = col


async def guard_post(coord, hass, entry, obs):
    """Entry setup registers the meter listener; then the meter reports, as HA fires it."""
    await coord._async_setup_peak_guard()
    listeners = [a for ids, a in getattr(hass, "state_listeners", [])
                 if "sensor.house_power" in (ids if isinstance(ids, (list, tuple)) else [ids])]
    obs["guard_listeners"] = len(listeners)
    st = hass.states.get("sensor.house_power")
    t0 = dt_util.now()
    for i in range(60):  # one reading a minute through the whole hour window
        dt_util.freeze(t0 + timedelta(minutes=i))
        ev = type("Ev", (), {"data": {"entity_id": "sensor.house_power", "new_state": st, "old_state": st}})()
        for a in listeners:
            r = a(ev)
            if asyncio.iscoroutine(r):
                await r
    for t in list(getattr(hass, "_tasks", [])):
        try:
            await t
        except Exception:  # noqa: BLE001
            pass
    obs["guard_suppressing"] = coord._peak_guard.suppressing
    dt_util.freeze(t0)


async def override_post(coord, hass, entry, obs):
    coord.record_setpoint_override(23.0)


# item -> list of (state name, change value, same-page extras, other-page prerequisites,
#                  hass states, now, seed, cycles, post hook, post-cycle hook)
def A(name, value, same=None, pre=None, states=None, now=THU6, seed=None, cycles=1, post=None, after=None):
    return dict(name=name, value=value, same=same or {}, pre=pre or {}, states=states or {}, now=now,
                seed=seed, cycles=cycles, post=post, after=after)


def stale(age_h):
    return {"sensor.outdoor": FakeState("-3.0", last_updated=THU6 - timedelta(hours=age_h),
                                        last_reported=THU6 - timedelta(hours=age_h))}


def collector_rows(coord, hass, entry, obs):
    col = obs.pop("_collector", None)
    rows = getattr(col, "rows", None) if col is not None else None
    if rows is None and col is not None:
        rows = getattr(col, "_rows", None)
    obs["debug_rows"] = None if rows is None else len(rows)


ARMS = {
    "entities_pump.heat_pump_return_temp_entity": [
        A("control flow set-point (pump_duty_mode doc: 5 K above the first fresh return reading)",
          "sensor.hp_return", same={"pump_duty_mode": "control", "heat_pump_mode_entity": "select.hp_mode"},
          pre={"space_setpoint_entity": "number.flow", "space_setpoint_unit": "flow"},
          states={**MODE_ST, **FLOW_ST, "sensor.hp_return": FakeState("41", unit="°C")})],
    "entities_pump.space_hysteresis_entity": [
        A(f"control flow set-point, return {ret} C, 8 cycles ({label})", "sensor.sp_hyst",
          same={"pump_duty_mode": "control", "heat_pump_mode_entity": "select.hp_mode",
                "heat_pump_return_temp_entity": "sensor.hp_return"},
          pre={"space_setpoint_entity": "number.flow", "space_setpoint_unit": "flow"},
          states={**MODE_ST, **FLOW_ST, "sensor.sp_hyst": FakeState("8", unit="K"),
                  "sensor.hp_return": FakeState(str(ret), unit="°C")}, now=now, cycles=8)
        for ret, now, label in ((30, THU6, "06:00"), (30, datetime(2026, 1, 15, 14, 0, tzinfo=UTC), "14:00 dear"))],
    "entities_pump.heat_pump_supply_temp_entity": [
        A("supply lift priced, 6 cycles", "sensor.hp_supply", pre={"flow_curve_cop_enabled": True},
          states={"sensor.hp_supply": FakeState("55", unit="°C")}, cycles=6)],
    "grid.peak_tariff_distinct_days": [A("peaks recorded, two on today", False, same=PEAK, seed=seed_peaks_same_day)],
    "grid.peak_tariff_weekdays_only": [A("saturday, peaks recorded", True,
                                         same={**PEAK, "peak_tariff_offpeak_factor": 0.0}, seed=seed_peaks,
                                         now=datetime(2026, 1, 17, 6, 0, tzinfo=UTC))],
    "grid.peak_tariff_hours": [A("peaks recorded", "07:00-19:00", same={**PEAK, "peak_tariff_offpeak_factor": 0.0},
                                 seed=seed_peaks)],
    "grid.peak_tariff_offpeak_factor": [A("peaks recorded", 0.0, same={**PEAK, "peak_tariff_hours": "07:00-19:00"},
                                          seed=seed_peaks)],
    "grid_connection.peak_guard_enabled": [
        A(f"peaks recorded, house {kw} kW, heat curve entity", True,
          pre={**PEAK, "house_power_entity": "sensor.house_power", "heat_curve_displace_entity": "number.curve"},
          states={"sensor.house_power": FakeState(str(kw * 1000), unit="W"), **HC_ST}, seed=seed_peaks, cycles=1,
          post=guard_post)
        for kw in (1.7, 9.0)],
    "grid_connection.peak_guard_margin_kw": [
        A(f"guard on, peaks recorded, house {kw} kW", 0.1, same={"peak_guard_enabled": True},
          pre={**PEAK, "house_power_entity": "sensor.house_power", "heat_curve_displace_entity": "number.curve"},
          states={"sensor.house_power": FakeState(str(kw * 1000), unit="W"), **HC_ST}, seed=seed_peaks, cycles=1,
          post=guard_post)
        for kw in (1.7, 9.0)],
    "grid_fees.contract_fixed_price": [A("metered, 4 cycles", 0.9, pre=POWER, states=POWER_ST, cycles=4)],
    "heat_curve.ecl110_state_topic": [A("entry setup subscribes", "ecl/state", same={"ecl110_displace_set_topic": "ecl/d"},
                                        post=mqtt_post)],
    "heat_curve.heat_curve_target_kind": [A("entity holds a stored curve value 5, 3 cycles", "persistent",
                                            same={"heat_curve_displace_entity": "number.curve"}, states=HC5_ST, cycles=3)],
    "heat_curve.heat_curve_persistent_band_k": [
        A("persistent, 3 cycles", 0.5, same={"heat_curve_displace_entity": "number.curve",
                                             "heat_curve_target_kind": "persistent"}, states=HC_ST, cycles=3)],
    "heat_curve.heat_curve_persistent_min_dwell_minutes": [
        A("persistent, 12 cycles (3 h)", 180, same={"heat_curve_displace_entity": "number.curve",
                                                    "heat_curve_target_kind": "persistent"}, states=HC_ST, cycles=12)],
    "heat_curve.heat_curve_persistent_writes_per_day": [
        A("persistent, 3 cycles", 0, same={"heat_curve_displace_entity": "number.curve",
                                           "heat_curve_target_kind": "persistent"}, states=HC_ST, cycles=3)],
    "hot_water_pumps.vvc_lead_minutes": [
        A("90 min before the 17:00 window", 120, same={"vvc_pump_entity": "switch.vvc"},
          states={"switch.vvc": "off"}, now=datetime(2026, 1, 15, 15, 30, tzinfo=UTC))],
    "learning.comfort_learning_enabled": [A("one override then a cycle", True, post=override_post, cycles=2)],
    "learning.debug_collect_enabled": [A("entry setup starts collection, 2 cycles", True, post=debugger_post,
                                         cycles=2, after=collector_rows)],
    "learning.staleness_watchdog_enabled": [A(f"outdoor sensor {h} h old", False, states=stale(h)) for h in (3, 12)],
    "learning.staleness_max_age_scale": [A(f"outdoor sensor {h} h old", 10.0, states=stale(h)) for h in (3, 12)],
    "learning.system_identification_enabled": [
        A("mild cheap night, 8 cycles", True, states={"sensor.outdoor": "6.0"},
          now=datetime(2026, 1, 15, 0, 0, tzinfo=UTC), cycles=8)],
    "learning.price_prior_enabled": [A("06:00, prices end at 23:00", False, seed=short_prices),
                                     A("two complete days published before, today's end at 23:00, 2 cycles", False,
                                       seed=learned_day_short_prices, cycles=2)],
    "quick_setup.wood_buffer_tank": [A("furnace on, no probe", True, same={"wood_furnace": True})],
    "solar_pv.pv_system_efficiency": [A("sunny noon", 0.3, same={"pv_enabled": True, "pv_peak_kw": 8.0}, seed=seed_sun,
                                        now=datetime(2026, 1, 15, 10, 0, tzinfo=UTC))],
    "solar_pv.pv_enabled": [A("sunny noon", True, same={"pv_peak_kw": 8.0}, seed=seed_sun,
                              now=datetime(2026, 1, 15, 10, 0, tzinfo=UTC))],
    "solar_pv.pv_peak_kw": [A("sunny noon", 20.0, same={"pv_enabled": True}, seed=seed_sun,
                              now=datetime(2026, 1, 15, 10, 0, tzinfo=UTC))],
    "solar_pv.pv_export_price": [A("sunny noon", 2.0, same={"pv_enabled": True, "pv_peak_kw": 8.0}, seed=seed_sun,
                                   now=datetime(2026, 1, 15, 10, 0, tzinfo=UTC))],
    "thermal_model.compressor_modulation": [A("min power 1.5 kW", "on_off", same={"heat_pump_min_power": 1.5})],
    "thermal_model.house_heat_loss_coefficient": [A("single zone", 0.6, pre={"two_zone_mode": "off"})],
    "thermal_model.house_thermal_mass": [A("single zone", 40.0, pre={"two_zone_mode": "off"}),
                                         A("two zone", 40.0, pre={"two_zone_mode": "on"})],
}


def canon(o):
    return json.loads(json.dumps(o, default=str, sort_keys=True).replace("NaN", "null"),
                      parse_float=lambda s: round(float(s), 6))


async def run_arm(step, field, arm, changed):
    flow, entry, hass = rig.new_flow(options=arm["pre"])
    for k, v in arm["states"].items():  # the flow validates against the live states
        hass.states.set(k, v if isinstance(v, FakeState) else FakeState(str(v)))
    form = await getattr(flow, f"async_step_{step}")(None)
    answers = rig.schema_defaults(form)
    own = {k: v for k, v in arm["pre"].items() if rig.field_section(form, k) is not False}
    pairs = list(own.items()) + list(arm["same"].items()) + ([(field, arm["value"])] if changed else [])
    for f, v in pairs:
        sec = rig.field_section(form, f)
        (answers if sec in (None, False) else answers.setdefault(sec, {}))[f] = v
    res = await rig.submit(flow, step, answers)
    if PERTURB:
        entry.options = {}
    hass2, coord = rig.build_coord(entry, states=arm["states"], now=arm["now"], seed=arm["seed"])
    obs = {}
    if arm["post"] is not None and arm["post"] is not override_post:
        await arm["post"](coord, hass2, entry, obs)
    data = None
    for i in range(arm["cycles"]):
        dt_util.freeze(arm["now"] + timedelta(minutes=15 * i))
        if arm["post"] is override_post and i == 1:
            await override_post(coord, hass2, entry, obs)
        data = await rig.run_cycles_async(coord, 1)
        coord.data = data
        coord.async_update_listeners()  # what a refresh does after the update: listeners observe
    if arm["after"] is not None:
        arm["after"](coord, hass2, entry, obs)
    stored = {**entry.data, **entry.options}
    return res, stored, data, list(hass2.services.calls), obs


def fp(data, calls, obs, field):
    d = {k: v for k, v in data.items() if k not in VOLATILE}
    return (canon({k: d.get(k) for k in PLAN_KEYS}),
            canon([calls, obs]),
            canon({k: v for k, v in d.items() if k not in PLAN_KEYS and k != field}))


async def main(argv):
    only = [a for a in argv if not a.startswith("--")]
    rows, noeffect = [], []
    for item, arms in ARMS.items():
        if only and item not in only:
            continue
        step, field = item.split(".")
        moved_any, detail = False, []
        for arm in arms:
            r0, s0, d0, c0, o0 = await run_arm(step, field, arm, False)
            r1, s1, d1, c1, o1 = await run_arm(step, field, arm, True)
            f0, f1 = fp(d0, c0, o0, field), fp(d1, c1, o1, field)
            ch = [n for n, x, y in zip(("plan", "writes", "publish"), f0, f1) if x != y]
            keys = sorted(k for k in f1[2] if f0[2].get(k) != f1[2].get(k))[:8] if "publish" in ch else []
            moved_any |= bool(ch)
            detail.append(f"[{arm['name']}: saved={r1.get('type')}/{r1.get('step_id')} err={r1.get('errors')} "
                          f"stored={s1.get(field, '<absent>')!r} moved={ch} {keys} obs0={ {k: v for k, v in o0.items()} } "
                          f"obs1={ {k: v for k, v in o1.items()} }]")
        rows.append(item)
        if not moved_any:
            noeffect.append(item)
        print(f"ROW {item} {'EFFECT' if moved_any else 'NOEFFECT'} " + " ".join(detail), flush=True)
    print(f"RESULT states_examined={len(rows)}")
    print(f"RESULT states_noeffect={len(noeffect)}")
    print("NOEFFECT", " ".join(noeffect))
    print(f"RESULT thread_factor={rig.thread_factor()}")
    print(f"RESULT load1={rig.load1()}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))
