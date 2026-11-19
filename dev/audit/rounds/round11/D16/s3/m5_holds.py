"""D16.M5 (hold and release): from each reachable state of every log_held hold, is there a path to "writes again" with no person?

Metric, per hold: ``writes_again_<hold>`` = the service calls to the held entity that production makes after the
held condition is entered and then cleared by the plant alone (a reading that comes back, a write that stops
failing, a target the plan moves, a clock that passes), within the window stated per section; a person's
action (a restart, an option change, a service call, a mode toggle) is never part of the path.
Count key: ``hass.services.calls`` entries whose ``entity_id`` is the held entity (the value the production
seam delivered), recorded after the hold was entered.

Command (from the export root):
    PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D16/s3/m5_holds.py [--perturb retry_off_restore]
Expected at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (exact, counts):
    RESULT writes_again_off_restore_failed_while_off=0        (finding: no automatic retry while Off)
    RESULT space_setpoint_final_while_off=25                  (the optimizer's gate, not the captured 45)
    RESULT null_restore_without_failure=1 / null_space_final=45 (the restore the harness can see)
    RESULT person_toggle_restores=1                           (only a person's Auto->Off->... toggle releases it)
    RESULT writes_again_off_restore_neutral_failed_while_off=0, heat_curve_offset_final_while_off=3 (the neutral
           consumer's path, off_restore.py:253/256: the heat-curve offset keeps the optimizer's +3 K)
    every other writes_again_* >= 1 and every gates_no_write_* >= 1 (non-findings)
    --perturb retry_off_restore: writes_again_off_restore_failed_while_off=1, space_setpoint_final_while_off=45,
                                 writes_again_off_restore_neutral_failed_while_off=1, heat_curve_offset_final_while_off=0
Machine: box B11 (shared). Plant: m6_restore.py's coord_all_features plus actuator slots; the harness builds the plan.
Instrumented symbols: off_restore:async_restore/_restore_baseline (key off_restore_<key>),
pump_arbiter:_arbitrate/_space_target/_arm_space, heat_curve:write_displace/write_persistent/_write_persistent_target/_send,
coordinator:_command_valve_target/_await_optimize/_await_off_loop/_note_solve_failure/_price_series/_weather_series/
_fetch_solar_forecast, inputs:InputReader._age_gate.
"""
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import time  # noqa: E402

_T_PROC0, _T_THR0 = time.process_time(), time.thread_time()
sys.path[:0] = [os.path.dirname(os.path.abspath(__file__)), "tests", "custom_components"]

import argparse  # noqa: E402
import asyncio  # noqa: E402
import itertools  # noqa: E402
from datetime import timedelta, timezone  # noqa: E402

import m6_restore as plant  # noqa: E402  (its builders; it disables logging)
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer import coordinator as cmod  # noqa: E402
from heatpump_optimizer import heat_curve, log_latch, off_restore, pump_arbiter  # noqa: E402
from heatpump_optimizer.const import MODE_AUTO, MODE_OFF  # noqa: E402
from heatpump_optimizer.entry_config import EntryConfig  # noqa: E402
from heatpump_optimizer.inputs import InputReader  # noqa: E402

T0 = plant.T0
_IDS = itertools.count()


def result(name, value, unit="calls"):
    print(f"RESULT {name}={value} {unit}")


def calls_to(hass, entity, since=0):
    return sum(1 for _d, _s, data in hass.services.calls[since:] if (data or {}).get("entity_id") == entity)


def install(kind):
    undo = []
    if kind == "retry_off_restore":
        orig = pump_arbiter._arbitrate

        async def arbitrate(coord, held, inp, mode, now):
            # The one-line release under test: an Off pass retries an armed restore.
            if inp.mode == MODE_OFF:
                await off_restore.async_restore(inp.hass, coord.entry, inp.config, "mode_off")
            await orig(coord, held, inp, mode, now)
        pump_arbiter._arbitrate = arbitrate
        undo.append(lambda: setattr(pump_arbiter, "_arbitrate", orig))
    return undo


# --------------------------------------------------------------------------
# off_restore.py:220/253/256 -- a restore that fails on the change into Off
# --------------------------------------------------------------------------
async def off_restore_failure(fail=True, entity="number.water_set"):
    """``entity``: number.water_set (a baseline consumer, off_restore.py:220) or number.offset (the heat
    curve's neutral consumer, off_restore.py:253/256)."""
    hass = FakeHass(plant.states())
    entry = FakeEntry(data=plant.config(), entry_id=f"m5s3_or_{next(_IDS)}")
    plant._LIVE[:] = [entry]
    c = plant.new_coord(hass, entry)
    await plant.drive(c)  # the space set-point now reads the optimizer's gate, 25; 45 is armed as its baseline
    real = hass.services.async_call
    state = {"fail": fail}

    async def flaky(domain, service, data=None, **kw):
        if state["fail"] and (data or {}).get("entity_id") == entity:
            hass.services.calls.append((domain, service, data))
            raise RuntimeError("device briefly unreachable")
        return await real(domain, service, data, **kw)
    hass.services.async_call = flaky
    await c.async_set_mode(MODE_OFF, refresh=False)
    plant.settle(hass) if not fail else hass.services.calls.clear()
    state["fail"] = False  # the device answers again; nobody touches anything
    mark = len(hass.services.calls)
    for minute in range(32, 32 + 6 * 60, 1):  # six hours of one-minute arbiter ticks, a cycle every 15 min
        dt_util.freeze(T0 + timedelta(minutes=minute))
        if minute % 15 == 2:
            await plant.cycle(c, minute)
        else:
            await pump_arbiter.apply(c)
    again = calls_to(hass, entity, mark)
    plant.settle(hass)
    final = hass.states.get(entity).state
    toggled = None
    if fail:
        # The only release at baseline: a person turns the optimizer back on and off again.
        await c.async_set_mode(MODE_AUTO, refresh=False)
        mark = len(hass.services.calls)
        await c.async_set_mode(MODE_OFF, refresh=False)
        toggled = calls_to(hass, entity, mark)
    return again, final, toggled


# --------------------------------------------------------------------------
# heat_curve.py -- the entity arm's holds, offset kind and persistent kind
# --------------------------------------------------------------------------
def hc_setup(kind="offset", value="0"):
    hass = FakeHass({"number.offset": FakeState(value, unit="K", attributes={"min": -10, "max": 10, "step": 1})})
    entry = FakeEntry(data={}, entry_id=f"m5s3_hc_{next(_IDS)}")
    cfg = EntryConfig.from_mapping({
        "heat_curve_displace_entity": "number.offset", "heat_curve_target_kind": kind,
        "heat_curve_persistent_min_dwell_minutes": 15,
    })
    return hass, entry, cfg


async def hc_offset():
    out = {}
    # heat_curve_entity (366/368): unavailable, then the reading returns.
    hass, entry, cfg = hc_setup(value="unavailable")
    await heat_curve.write_displace(hass, entry, cfg, 2)
    out["null_heat_curve_entity_while_unavailable"] = calls_to(hass, "number.offset")
    hass.states.get("number.offset").state = "0"
    mark = len(hass.services.calls)
    await heat_curve.write_displace(hass, entry, cfg, 2)
    out["heat_curve_entity"] = calls_to(hass, "number.offset", mark)
    # heat_curve_saturated (369): the range is narrower than the displace; the write still goes (log only).
    hass, entry, cfg = hc_setup()
    hass.states.get("number.offset").attributes.update({"min": -1, "max": 1})
    await heat_curve.write_displace(hass, entry, cfg, 3)
    out["gates_no_write_heat_curve_saturated"] = calls_to(hass, "number.offset")
    # heat_curve_write (399/401): the write raises once, then the device answers.
    hass, entry, cfg = hc_setup()
    real = hass.services.async_call
    st = {"fail": True}

    async def flaky(domain, service, data=None, **kw):
        if st["fail"]:
            raise RuntimeError("refused")
        return await real(domain, service, data, **kw)
    hass.services.async_call = flaky
    await heat_curve.write_displace(hass, entry, cfg, 2)
    st["fail"] = False
    await heat_curve.write_displace(hass, entry, cfg, 2)
    out["heat_curve_write"] = calls_to(hass, "number.offset")
    # heat_curve_not_held (376): the entity ignores 2 twice past the grace -> gave up; the plan moves to 3.
    hass, entry, cfg = hc_setup()
    held = heat_curve.state_for(entry)
    for _ in range(3):
        await heat_curve.write_displace(hass, entry, cfg, 2)
        held.written_at -= heat_curve.HELD_GRACE_S + 1  # the grace passes; the entity still reads 0
    gave_up = calls_to(hass, "number.offset")
    await heat_curve.write_displace(hass, entry, cfg, 2)
    out["null_heat_curve_not_held_same_target"] = calls_to(hass, "number.offset") - gave_up
    mark = len(hass.services.calls)
    await heat_curve.write_displace(hass, entry, cfg, 3)
    out["heat_curve_not_held"] = calls_to(hass, "number.offset", mark)
    # heat_curve_write_cap (383): the day's writes at the cap, then a day passes.
    hass, entry, cfg = hc_setup()
    held = heat_curve.state_for(entry)
    now = time.monotonic()
    held.writes.extend([now] * heat_curve.write_cap_per_day(cfg))
    await heat_curve.write_displace(hass, entry, cfg, 2)
    capped = calls_to(hass, "number.offset")
    held.writes = type(held.writes)(t - heat_curve._DAY_S - 1 for t in held.writes)
    await heat_curve.write_displace(hass, entry, cfg, 2)
    out["heat_curve_write_cap"] = calls_to(hass, "number.offset") - capped
    out["null_heat_curve_write_cap_while_capped"] = capped
    return out


async def hc_persistent():
    out = {}
    hass, entry, cfg = hc_setup(kind="persistent", value="unavailable")
    dt_util.freeze(T0)
    await heat_curve.write_persistent(hass, entry, cfg, 2)  # 504: unavailable, refused
    refused = calls_to(hass, "number.offset")
    hass.states.get("number.offset").state = "0"
    await heat_curve.write_persistent(hass, entry, cfg, 2)
    out["heat_curve_entity_persistent"] = calls_to(hass, "number.offset") - refused
    # 551: the entity keeps reading 0 (the write before) -> missed, resent once, then latched; the plan moves.
    for k in range(1, 4):
        dt_util.freeze(T0 + timedelta(minutes=20 * k))
        await heat_curve.write_persistent(hass, entry, cfg, 2)
    latched = calls_to(hass, "number.offset")
    dt_util.freeze(T0 + timedelta(minutes=100))
    await heat_curve.write_persistent(hass, entry, cfg, 2)
    out["null_heat_curve_not_held_persistent_same_target"] = calls_to(hass, "number.offset") - latched
    dt_util.freeze(T0 + timedelta(minutes=120))
    mark = len(hass.services.calls)
    await heat_curve.write_persistent(hass, entry, cfg, 3)
    out["heat_curve_not_held_persistent"] = calls_to(hass, "number.offset", mark)
    # 531 saturated: log only.
    hass, entry, cfg = hc_setup(kind="persistent")
    hass.states.get("number.offset").attributes.update({"min": -1, "max": 1})
    dt_util.freeze(T0 + timedelta(days=2))
    await heat_curve.write_persistent(hass, entry, cfg, 3)
    out["gates_no_write_heat_curve_saturated_persistent"] = calls_to(hass, "number.offset")
    return out


# --------------------------------------------------------------------------
# off_restore.py:190 -- no baseline readable: the space write is refused until one is
# --------------------------------------------------------------------------
async def baseline_unreadable():
    st = plant.states()
    st["number.water_set"].state = "unavailable"
    hass = FakeHass(st)
    entry = FakeEntry(data=plant.config(), entry_id=f"m5s3_bl_{next(_IDS)}")
    plant._LIVE[:] = [entry]
    c = plant.new_coord(hass, entry)
    c._mode = MODE_AUTO
    c._optimization_result = plant.plan("dd--dd--")
    c._current_action = {"heat_pump_on": True, "displace_value": 0.0, "valve_target": 20.0}
    await plant.cycle(c, 1)
    refused = calls_to(hass, "number.water_set")
    entered = int("off_restore_baseline_pump_arbiter_space" in log_latch._HELD_CONDITIONS.get(entry, {}))
    hass.states.get("number.water_set").state = "45"  # the controller reports again
    mark = len(hass.services.calls)
    for minute in range(2, 6):
        dt_util.freeze(T0 + timedelta(minutes=minute))
        await pump_arbiter.apply(c)
    return entered, refused, calls_to(hass, "number.water_set", mark)


# --------------------------------------------------------------------------
# pump_arbiter.py:630/642 -- an indoor-declared space set-point whose minimum cannot hold the room
# --------------------------------------------------------------------------
async def misdeclared():
    st = plant.states()
    st["number.water_set"] = FakeState("45", attributes={"min": 25, "max": 63})
    hass = FakeHass(st)
    cfg = {**plant.config(), "space_setpoint_unit": "indoor"}
    entry = FakeEntry(data=cfg, entry_id=f"m5s3_md_{next(_IDS)}")
    plant._LIVE[:] = [entry]
    c = plant.new_coord(hass, entry)
    c._mode = MODE_AUTO
    c._optimization_result = plant.plan("ssssssss")
    c._current_action = {"heat_pump_on": True}
    dt_util.freeze(T0 + timedelta(minutes=1))
    await pump_arbiter.apply(c)
    held = calls_to(hass, "number.water_set")
    entered = int("space_target_flow_declared:number.water_set" in log_latch._HELD_CONDITIONS.get(hass, {}))
    # Only the entity's declared range (an integration's attribute or a person's option) can release it.
    hass.states.get("number.water_set").attributes["min"] = 5
    mark = len(hass.services.calls)
    dt_util.freeze(T0 + timedelta(minutes=2))
    await pump_arbiter.apply(c)
    return entered, held, calls_to(hass, "number.water_set", mark)


# --------------------------------------------------------------------------
# coordinator.py:7747/7763 -- the valve write
# --------------------------------------------------------------------------
async def valve():
    hass = FakeHass(plant.states())
    entry = FakeEntry(data=plant.config(), entry_id=f"m5s3_v_{next(_IDS)}")
    c = plant.new_coord(hass, entry)
    c._mode = MODE_AUTO
    c._current_action = {"valve_target": 20.0}
    real = hass.services.async_call
    st = {"fail": True}

    async def flaky(domain, service, data=None, **kw):
        if st["fail"] and (data or {}).get("entity_id") == "number.valve":
            raise RuntimeError("valve offline")
        return await real(domain, service, data, **kw)
    hass.services.async_call = flaky
    await c._command_valve_target()
    st["fail"] = False
    await c._command_valve_target()
    again = calls_to(hass, "number.valve")
    # 7747: flow kind without two zones -- a configuration the latch names; release is an option change.
    hass2 = FakeHass(plant.states())
    entry2 = FakeEntry(data={**plant.config(), "mixing_valve_write_target_kind": "flow"}, entry_id=f"m5s3_v2_{next(_IDS)}")
    c2 = plant.new_coord(hass2, entry2)
    c2._mode = MODE_AUTO
    c2._current_action = {"valve_target": 20.0}
    await c2._command_valve_target()
    return again, calls_to(hass2, "number.valve")


# --------------------------------------------------------------------------
# coordinator.py:2148/2153, 2322/2340 -- an off-loop job or a solve that outran the worker's deadline
# --------------------------------------------------------------------------
async def worker_timeout():
    hass = FakeHass()
    orig = cmod._await_process
    st = {"n": 0}

    async def flaky(_hass, fn, *args):
        st["n"] += 1
        if st["n"] == 1:
            raise cmod.ProcessWorkerTimeout("the worker outran its deadline")
        return "plan"
    cmod._await_process = flaky
    delivered_opt = 0
    delivered_off = 0
    try:
        for _ in range(2):
            try:
                delivered_opt += (await cmod._await_optimize(hass, object(), None)) == "plan"
            except Exception:  # noqa: BLE001 - the cycle's UpdateFailed
                pass
        st["n"] = 0

        def job():
            return "plan"
        for _ in range(2):
            try:
                delivered_off += (await cmod._await_off_loop(hass, job)) == "plan"
            except cmod.ProcessWorkerTimeout:
                pass
    finally:
        cmod._await_process = orig
    return delivered_opt, delivered_off


# --------------------------------------------------------------------------
# Latches that gate no actuator write: the latch held on, a fresh plan's cycle still writes
# --------------------------------------------------------------------------
async def gates_no_write():
    hass = FakeHass(plant.states())
    hass.config.latitude = None  # no home location: the Open-Meteo coordinate latch
    cfg = {**plant.config(), "solar_forecast_source": "open_meteo",
           "solar_location": {"latitude": "north", "longitude": "east"}}
    entry = FakeEntry(data=cfg, entry_id=f"m5s3_g_{next(_IDS)}")
    plant._LIVE[:] = [entry]
    c = plant.new_coord(hass, entry)
    # Enter each fetch / solve latch through production itself.
    c._prices, c._weather_forecast = [], []
    c._price_series(4, T0, 0)                                     # 7234 no_prices
    c._prices = [{"total": 1.0, "starts_at": (T0 - timedelta(days=3)).isoformat()}]
    c._price_series(4, T0, 0)                                     # 7250 prices_uncovered
    try:
        c._weather_series(4, T0, 0)                               # 7312 no_weather_forecast
    except Exception:  # noqa: BLE001
        pass
    await c._fetch_solar_forecast()                               # 7169 solar_location, 7185 solar_coordinate
    cmod._note_solve_failure(c, RuntimeError("solver diverged"))  # 703 solve_failure
    held = sorted(log_latch._HELD_CONDITIONS.get(c, {}))
    c._mode = MODE_AUTO
    c._optimization_result = plant.plan("dd--dd--")
    c._current_action = {"heat_pump_on": True, "displace_value": 0.0, "valve_target": 20.0}
    await plant.cycle(c, 1)
    return held, len(hass.services.calls)


# --------------------------------------------------------------------------
# inputs.py:1070 -- an input stamped ahead of the clock reads stale until the clock passes it
# --------------------------------------------------------------------------
def future_stamp():
    stamp = T0 + timedelta(minutes=10)
    hass = FakeHass({"sensor.indoor": FakeState("21.0", unit="°C", last_updated=stamp)})
    cfg = {"indoor_temp_entity": "sensor.indoor"}
    clock = {"now": T0}
    reader = InputReader(hass, cfg, now=lambda: clock["now"])
    before = reader.read("indoor_temp_entity").problem
    clock["now"] = stamp + timedelta(minutes=1)
    after = InputReader(hass, cfg, now=lambda: clock["now"]).read("indoor_temp_entity").problem
    return before, after


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", choices=("none", "retry_off_restore"), default="none")
    args = ap.parse_args()
    dt_util.DEFAULT_TIME_ZONE = timezone.utc
    undo = install(args.perturb)
    try:
        again, final, toggled = asyncio.run(off_restore_failure())
        result("writes_again_off_restore_failed_while_off", again)
        result("space_setpoint_final_while_off", final, "degC")
        result("person_toggle_restores", toggled)
        again, final, toggled = asyncio.run(off_restore_failure(entity="number.offset"))
        result("writes_again_off_restore_neutral_failed_while_off", again)
        result("heat_curve_offset_final_while_off", final, "K")
        result("person_toggle_restores_neutral", toggled)
        n_again, n_final, _ = asyncio.run(off_restore_failure(fail=False))
        result("null_restore_without_failure_later_writes", n_again)
        result("null_space_final", n_final, "degC")

        for k, v in asyncio.run(hc_offset()).items():
            result(("" if k.startswith(("null_", "gates_")) else "writes_again_") + k, v)
        for k, v in asyncio.run(hc_persistent()).items():
            result(("" if k.startswith(("null_", "gates_")) else "writes_again_") + k, v)
        entered, refused, back = asyncio.run(baseline_unreadable())
        result("off_restore_baseline_latch_entered", entered, "bool")
        result("off_restore_baseline_unreadable_refused", refused)
        result("writes_again_off_restore_baseline", back)
        entered, held, released = asyncio.run(misdeclared())
        result("space_target_flow_declared_latch_entered", entered, "bool")
        result("space_target_flow_declared_held", held)
        result("writes_after_entity_range_fixed_space_target_flow_declared", released)
        again, flow_cfg = asyncio.run(valve())
        result("writes_again_valve_write", again)
        result("valve_flow_needs_two_zone_writes", flow_cfg)
        opt, off = asyncio.run(worker_timeout())
        result("writes_again_process_worker_timeout_plans", opt, "plans")
        result("writes_again_off_loop_timeout_jobs", off, "jobs")
        held, writes = asyncio.run(gates_no_write())
        print(f"# latches held on the coordinator: {held}")
        result("gates_no_write_latches_held", len(held), "latches")
        result("gates_no_write_cycle_writes", writes)
        before, after = future_stamp()
        print(f"# future stamp: before={before} after={after}")
        result("future_stamp_released_by_clock", int(before == "stale" and after is None), "bool")
    finally:
        for u in undo:
            u()
        dt_util.freeze(None)
    proc, thr = time.process_time() - _T_PROC0, time.thread_time() - _T_THR0
    print(f"RESULT thread_factor={proc / thr if thr else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    import resource
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}")


if __name__ == "__main__":
    main()
