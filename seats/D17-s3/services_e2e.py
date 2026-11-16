"""D17-s3 coverage: every documented service effect, end to end (D17.M1-M3, kind=service).

Metric: per service, one RESULT line per oracle, 1 when the documented effect
is observable and 0 when it is not; ``RESULT services_examined`` counts the
services driven. Each oracle is the documented sentence (strings.json
``services.<name>``, README.md "Services", docs/configuration.md "Services")
made a check on the published payload, the entry's stored config, the
entities, or the action's answer -- written from the docs before reading the
handler. Every call goes through ``hass.services.async_call`` and the schema
the integration registered, on a real coordinator set up through
``__init__.async_setup_entry`` (rig.py), with cycles, a restart (new hass,
same entry id and stored options, shared Store disk) and the reload an
options write triggers.

Key: the published payload ``coordinator.data`` and ``entry.options`` as the
reloaded coordinator reads them back; never a handler's private state.

Perturbation (``--perturb``): ``coordinator:HeatPumpOptimizerCoordinator.async_set_mode``
replaced in memory by one that ignores the mode; the set_mode oracles drop
to 0 (down). Findings ride their own harnesses (f01-f03).

Run:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
        dev/audit/rounds/round11/D17/s3/services_e2e.py [--perturb]
Expected (baseline): every oracle 1 except run_optimization.publishes_new_price=0
  (D17-s3-01) and restore_learned_snapshot.refuses_unevidenced=0 (D17-s3-03), so
  oracles_failed=2; exact.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B13 (shared, 3 seats).
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig  # noqa: E402

import asyncio  # noqa: E402
import json  # noqa: E402
import logging  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timedelta  # noqa: E402

from harness import FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

logging.disable(logging.WARNING)
PERTURB = "--perturb" in sys.argv
OK: dict[str, int] = {}
EXAMINED: set[str] = set()


def check(service: str, name: str, cond: bool, note: str = "") -> None:
    EXAMINED.add(service)
    OK[f"{service}.{name}"] = int(bool(cond))
    print(f"RESULT {service}.{name}={int(bool(cond))} bool" + (f"  # {note}" if note else ""))


async def raises(coro) -> str | None:
    try:
        await coro
    except Exception as err:  # noqa: BLE001
        return type(err).__name__
    return None


def total(d) -> float:
    return sum(float(x["power"]) for x in d["schedule"])


async def fresh(eid, **cfg):
    rig.freeze()
    inst = rig.Install(entry_id=eid, data=rig.base_config(**cfg))
    await inst.setup()
    await inst.cycle()
    return inst


async def s_run_optimization():
    inst = await fresh("s_run")
    rig.advance(1)
    inst.hass.states.set("sensor.prices", FakeState("2.0", attributes={"raw_today": rig.price_rows(48, 2.0)}))
    await inst.call("run_optimization")
    check("run_optimization", "publishes_new_price", inst.coord.data["schedule"][0]["price"] == 2.0,
          f"published {inst.coord.data['schedule'][0]['price']}")
    # The refusal state ("fewer than four electricity price steps") is not
    # reachable through an entity feed: a two-row feed is 8 known quarter
    # steps and the price prior fills the horizon, so the solve can run.
    inst.hass.states.set("sensor.prices", FakeState("2.0", attributes={"raw_today": rig.price_rows(2, 2.0)}))
    d = await inst.cycle()
    err = await raises(inst.call("run_optimization"))
    print(f"RESULT run_optimization.two_row_feed_known_steps={d.get('price_known_steps')} count")
    print(f"RESULT run_optimization.two_row_feed_plan_steps={len(d['schedule'])} count")
    check("run_optimization", "runs_when_solve_can_run", err is None, str(err))


async def s_set_away():
    inst = await fresh("s_away")
    rt = (dt_util.now() + timedelta(hours=30)).replace(microsecond=0)
    await inst.call("set_away", {"return_time": rt.isoformat()})
    d = await inst.cycle()
    check("set_away", "time_while_off_stores_without_on",
          d["away_override_return_time"] is not None and not d["away_active"])
    await inst.call("set_away", {"active": True})
    d = await inst.cycle()
    sp = max(x["setpoint"] for x in d["schedule"])
    check("set_away", "on_sets_back_plan", d["away_active"] and sp <= 16.5, f"max setpoint {sp}")
    await inst.restart()
    d = await inst.cycle()
    check("set_away", "survives_restart", d["away_active"] and d["away_override_return_time"] == rt.isoformat())
    # recovery: return inside (estimate + margin) -> the plan reaches the floor by the return
    rig.BASE_STATES["sensor.indoor"] = ("17.0", {})
    inst2 = await fresh("s_away2")
    rt2 = (dt_util.now() + timedelta(hours=30)).replace(microsecond=0)
    await inst2.call("set_away", {"active": True, "return_time": rt2.isoformat()})
    d = await inst2.cycle()
    est = float(d["away_recovery_hours"] or 0.0)
    rt3 = (dt_util.now() + timedelta(hours=est + 0.5)).replace(microsecond=0)
    await inst2.call("set_away", {"return_time": rt3.isoformat()})
    d = await inst2.cycle()
    before = [x for x in d["schedule"] if datetime.fromisoformat(x["time"]) <= rt3]
    room = before[-1]["room_temp"] if before else None
    check("set_away", "recovery_reaches_floor_by_return",
          d["away_recovery_active"] and room is not None and room >= d["min_temperature"] - 0.05,
          f"est {est} h, room at return {room}")
    rig.BASE_STATES["sensor.indoor"] = ("21.4", {})
    await inst.call("set_away", {"active": False})
    d = await inst.cycle()
    check("set_away", "off_clears_return", not d["away_active"] and d["away_override_return_time"] is None)


def spike_rows(now):
    now = now.replace(minute=0, second=0, microsecond=0)
    return [{"start": (now + timedelta(hours=h)).isoformat(),
             "value": 5.0 if 2 <= h < 9 else 0.1} for h in range(48)]


async def s_set_mode():
    inst = await fresh("s_mode")
    inst.hass.states.set("sensor.prices", FakeState("0.1", attributes={"raw_today": spike_rows(dt_util.now())}))
    d_auto = await inst.cycle()
    auto_min = min(x["room_temp"] for x in d_auto["schedule"])
    from heatpump_optimizer import coordinator as cmod

    bands: list = []
    orig = cmod.HeatPumpOptimizerCoordinator._solve_hubs

    def hook(self, *a, **k):
        out = orig(self, *a, **k)
        bands.append(out[0].min_temp)
        return out

    cmod.HeatPumpOptimizerCoordinator._solve_hubs = hook
    try:
        await inst.call("set_mode", {"mode": "economy"})
        published_now = inst.coord.data["mode"] == "economy"
        d = await inst.cycle()
    finally:
        cmod.HeatPumpOptimizerCoordinator._solve_hubs = orig
    eco_min = min(x["room_temp"] for x in d["schedule"])
    floor = float(d["min_temperature"])
    # "Lets the plan take the house up to 1.5 °C below your comfort floor": the
    # solve's floor is widened by 1.5, never below 15 (the permission). Whether
    # the plan uses it is the objective's call (lead to D0).
    check("set_mode", "economy_widens_solve_floor",
          d["mode"] == "economy" and bands and abs(bands[-1] - max(15.0, floor - 1.5)) < 1e-6,
          f"solve floor {bands[-1] if bands else None}, configured {floor}, auto min {auto_min:.2f}, economy min {eco_min:.2f}")
    check("set_mode", "mode_published_without_waiting", published_now)
    await inst.restart()
    d = await inst.cycle()
    check("set_mode", "mode_survives_restart", d["mode"] == "economy")
    await inst.call("set_mode", {"mode": "off"})
    d = await inst.cycle()
    check("set_mode", "off_disables", d["current_action"].get("heat_pump_on") is False and d["mode"] == "off")
    await inst.call("set_mode", {"mode": "boost"})
    d = await inst.cycle()
    check("set_mode", "boost_max_power", d["current_action"].get("power_normalized") == 1.0)
    await inst.call("set_mode", {"mode": "comfort"})
    d = await inst.cycle()
    check("set_mode", "comfort_holds", d["current_action"].get("mode") == "comfort")


async def s_set_thermal_parameters():
    inst = await fresh("s_tp", two_zone_mode="off")
    a = total(inst.coord.data)
    await inst.call("set_thermal_parameters", {"house_heat_loss_coefficient": 0.35})
    b = await inst.cycle()
    check("set_thermal_parameters", "single_zone_hlc_moves_plan", total(b) - a > 1.0, f"{a:.1f}->{total(b):.1f}")
    await inst.restart()
    r = await inst.cycle()
    check("set_thermal_parameters", "value_survives_restart", abs(total(r) - total(b)) < 1.0)
    err = await raises(inst.call("set_thermal_parameters", {"dhw_windows": "25:00-26:00"}))
    check("set_thermal_parameters", "refuses_unparseable_windows", err is not None, str(err))
    err = await raises(inst.call("set_thermal_parameters", {"quiet_off_windows": "07:00-08:00"}))
    check("set_thermal_parameters", "refuses_off_overlapping_dhw", err is not None, str(err))
    inst2 = await fresh("s_tp2", two_zone_mode="off")
    await inst2.call("set_thermal_parameters", {"quiet_off_windows": "01:00-04:00"})
    d = await inst2.cycle()
    off = [x["power"] for x in d["schedule"] if 1 <= datetime.fromisoformat(x["time"]).hour < 4]
    dhw = [x.get("dhw_power") or 0.0 for x in (d.get("dhw_plan") or {}).get("forecast", [])
           if 1 <= datetime.fromisoformat(x["t"]).hour < 4]
    check("set_thermal_parameters", "quiet_off_plans_nothing",
          len(off) > 0 and max(off) == 0.0 and (not dhw or max(dhw) == 0.0), f"max space {max(off) if off else None}")


async def s_simulate_plan():
    rig.freeze()
    inst = rig.Install(entry_id="s_sim")
    await inst.setup(settle=False)
    err = await raises(inst.call("simulate_plan", {"target_temp": 20.0}, settle=False))
    check("simulate_plan", "fails_before_first_plan", err is not None, str(err))
    await inst.settle()
    await inst.cycle()
    cfg = dict(inst.coord.effective_config)
    plan = json.dumps(inst.coord.data["schedule"], default=str)
    r = await inst.call("simulate_plan", {"target_temp": 23.0})
    res = (r or {}).get("results", {}).get("s_sim", {})
    check("simulate_plan", "returns_cost_difference", isinstance(res.get("cost_delta"), (int, float)))
    check("simulate_plan", "does_not_disturb",
          dict(inst.coord.effective_config) == cfg and json.dumps(inst.coord.data["schedule"], default=str) == plan)
    r2 = await inst.call("simulate_plan", {"target_temp": 18.0})
    res2 = (r2 or {}).get("results", {}).get("s_sim", {})
    check("simulate_plan", "rapid_repeat_returns_previous",
          res2.get("rate_limited") is True and res2.get("cost_delta") == res.get("cost_delta"))


async def s_apply_schedule():
    inst = await fresh("s_sched")
    req = {"day_start_hour": 6, "day_end_hour": 21, "comfort_temp_day": 21.5, "target_temperature": 21.0,
           "dhw_setpoint": 56, "dhw_min_temperature": 45, "dhw_windows": "06:00-08:00",
           "quiet_silent_windows": "22:00-23:00", "quiet_off_windows": "01:00-03:00",
           "silent_mode_power_fraction": 0.7}
    await inst.call("apply_schedule", req)
    stored = all(inst.entry.options.get(k) is not None for k in req)
    await inst.reload()
    d = await inst.cycle()
    eff = inst.coord.effective_config
    check("apply_schedule", "writes_all_ten", stored and all(eff.get(k) is not None for k in req))
    check("apply_schedule", "next_plan_uses_them",
          d["day_end_hour"] == 21 and d["comfort_temp_day"] == 21.5 and d["dhw_setpoint"] == 56.0
          and d["dhw_windows"] == "06:00-08:00")
    await inst.restart()
    await inst.cycle()
    check("apply_schedule", "target_survives_reload", inst.coord.target_temperature == 21.0)
    err = await raises(inst.call("apply_schedule", {"dhw_min_temperature": 55.5}))
    check("apply_schedule", "refuses_no_deadband", err is not None, str(err))


async def s_manual_plan():
    inst = await fresh("s_man")
    s0 = (dt_util.now() + timedelta(hours=3)).replace(minute=0, second=0, microsecond=0)
    r = await inst.call("apply_manual_plan", {
        "space_slots": [{"start": s0.isoformat(), "end": (s0 + timedelta(hours=2)).isoformat()}],
        "dhw_slots": []})
    exp = datetime.fromisoformat(r["applied"]["s_man"]["expires_at"])
    check("apply_manual_plan", "expiry_defaults_20h", abs((exp - dt_util.now()).total_seconds() - 72000) < 120)
    d = await inst.cycle()
    mp = d.get("manual_plan") or {}
    check("apply_manual_plan", "override_published", mp.get("active") is True)
    pinned = [x["power"] for x in d["schedule"] if s0 <= datetime.fromisoformat(x["time"]) < s0 + timedelta(hours=2)]
    check("apply_manual_plan", "pinned_slot_runs", len(pinned) == 8 and min(pinned) > 0.0, f"{pinned}")
    released = {r_["step"] for r_ in mp.get("released_dhw") or []}
    dhw_on = [i for i, x in enumerate((d.get("dhw_plan") or {}).get("forecast", [])) if (x.get("dhw_power") or 0) > 0]
    check("apply_manual_plan", "empty_dhw_list_forces_off_or_reports", all(i in released for i in dhw_on),
          f"dhw on steps {dhw_on[:5]}, released {sorted(released)[:5]}")
    await inst.restart()
    d = await inst.cycle()
    check("apply_manual_plan", "survives_restart", (d.get("manual_plan") or {}).get("active") is True)
    await inst.call("clear_manual_plan", {})
    gone_now = (inst.coord.data or {}).get("manual_plan") is None
    d = await inst.cycle()
    check("clear_manual_plan", "drops_pins_immediately", gone_now and d.get("manual_plan") is None)


async def s_reset_heat_loss():
    inst = await fresh("s_rhl")
    inst.coord._apply_house_heat_loss_scale(1.3)
    inst.coord._apply_lower_floor_loss_ratio(1.2)
    d = await inst.cycle()
    stamp = d["last_optimization"]
    rig.advance(1)
    cw = d["comfort_weight"]
    await inst.call("reset_heat_loss_learners", {"learners": ["house_heat_loss_scale"]})
    d = inst.coord.data
    check("reset_heat_loss_learners", "named_learner_to_one",
          d["house_heat_loss_scale"] == 1.0 and d["lower_floor_loss_ratio"] == 1.2)
    check("reset_heat_loss_learners", "replans_straight_away", d["last_optimization"] != stamp)
    check("reset_heat_loss_learners", "others_left_alone", d["comfort_weight"] == cw)
    await inst.call("reset_heat_loss_learners", {})
    d = await inst.cycle()  # a second request inside the debouncer's 10 s cooldown trails it
    check("reset_heat_loss_learners", "empty_resets_both", d["lower_floor_loss_ratio"] == 1.0)


async def s_factory_reset():
    inst = await fresh("s_fr")
    await inst.call("apply_schedule", {"comfort_temp_day": 22.5})
    await inst.reload()
    await inst.cycle()
    inst.coord._apply_house_heat_loss_scale(1.4)
    await inst.coord._async_save_thermal_learning()
    await inst.call("set_mode", {"mode": "economy"})
    r = await inst.call("factory_reset", {"entry_id": "s_fr", "scope": "both"})
    check("factory_reset", "answers_entry_and_scope", r == {"reset": "s_fr", "scope": "both"})
    await inst.reload()
    d = await inst.cycle()
    check("factory_reset", "settings_and_learners_default",
          d["comfort_temp_day"] == 21.0 and d["house_heat_loss_scale"] == 1.0)
    check("factory_reset", "keeps_sensors_and_mode",
          inst.coord.effective_config.get("indoor_temp_entity") == "sensor.indoor" and d["mode"] == "economy")
    await inst.call("restore_learned_snapshot", {})
    await inst.reload()
    d = await inst.cycle()
    check("restore_learned_snapshot", "undoes_factory_reset",
          d["comfort_temp_day"] == 22.5 and d["house_heat_loss_scale"] == 1.4)
    inst2 = await fresh("s_rs")
    err = await raises(inst2.call("restore_learned_snapshot", {}))
    check("restore_learned_snapshot", "refuses_unevidenced", err is not None, "D17-s3-03")


async def s_diagnose():
    inst = await fresh("s_diag")
    for _ in range(6):
        rig.advance(15)
        await inst.cycle()
    r = await inst.call("diagnose_interval", {})
    rep = (r or {}).get("diagnosis", {}).get("s_diag") or {}
    check("diagnose_interval", "returns_attribution", "unexplained" in rep and "residual" in rep)
    ents = await inst.all_entities()
    acc = ents["sensor.heat_pump_optimizer_prediction_accuracy"]
    check("diagnose_interval", "published_on_accuracy_sensor",
          (acc.extra_state_attributes or {}).get("last_diagnosis") == rep)


async def s_debug():
    inst = await fresh("s_dbg")
    await inst.call("debug_collect", {"action": "start"})
    on = inst.entry.options.get("debug_collect_enabled") is True
    await inst.reload()
    await inst.cycle()
    await inst.cycle()
    st = (await inst.call("debug_collect", {"action": "status"}))["debug"]["s_dbg"]
    check("debug_collect", "start_turns_option_on_and_collects", on and st["active"] and st["rows"] > 0, json.dumps(st))
    await inst.call("debug_collect", {"action": "stop"})
    st = (await inst.call("debug_collect", {"action": "status"}))["debug"]["s_dbg"]
    check("debug_collect", "stop_ends_it", not st["active"] and st["final"])


async def s_assign():
    states = {"sensor.buffer": FakeState("35.0", attributes={"unit_of_measurement": "°C", "device_class": "temperature"}),
              "switch.thing": FakeState("on"), "number.valve": FakeState("20", attributes={"min": 5, "max": 30})}
    rig.freeze()
    inst = rig.Install(entry_id="s_asg", states=states)
    await inst.setup()
    await inst.cycle()
    await inst.call("assign_entity", {"key": "buffer_tank_temp_entity", "entity_id": "sensor.buffer"})
    await inst.reload()
    d = await inst.cycle()
    check("assign_entity", "assigned_sensor_read", d.get("buffer_tank_temperature") == 35.0)
    await inst.call("assign_entity", {"key": "buffer_tank_temp_entity", "entity_id": ""})
    check("assign_entity", "empty_clears", inst.entry.options.get("buffer_tank_temp_entity") is None)
    err = await raises(inst.call("assign_entity", {"key": "buffer_tank_temp_entity", "entity_id": "sensor.nope"}))
    check("assign_entity", "refuses_missing_entity", err is not None)
    err = await raises(inst.call("assign_entity", {"key": "buffer_tank_temp_entity", "entity_id": "switch.thing"}))
    check("assign_entity", "refuses_wrong_domain", err is not None)
    await inst.call("assign_entity", {"key": "mixing_valve_target_entity", "entity_id": "number.valve", "manual_setpoint": 20.5})
    ok_valve = inst.entry.options.get("mixing_valve_target") == 20.5
    await inst.call("assign_entity", {"key": "buffer_tank_temp_entity", "entity_id": "sensor.buffer", "manual_setpoint": 25})
    check("assign_entity", "manual_setpoint_only_on_valve", ok_valve and inst.entry.options.get("mixing_valve_target") == 20.5)


async def s_topology():
    inst = await fresh("s_topo")
    err = await raises(inst.call("apply_topology", {"layout": "two_tank_4way"}))
    check("apply_topology", "refuses_unsupported_by_config", err is not None)
    err = await raises(inst.call("apply_topology", {"layout": "separate_slab_shunt"}))
    check("apply_topology", "refuses_non_selectable", err is not None)
    await inst.call("apply_topology", {"layout": "no_valve", "positions": {"heat_pump": [1, 2]}, "dhw": False})
    await inst.reload()
    d = await inst.cycle()
    check("apply_topology", "stores_layout_and_dhw_toggle",
          inst.entry.options.get("topology_layout") == "no_valve" and d["dhw_enabled"] is False)


async def main() -> None:
    from heatpump_optimizer import coordinator as cmod

    if PERTURB:
        async def ignore(self, mode, *, refresh=True):
            return None

        cmod.HeatPumpOptimizerCoordinator.async_set_mode = ignore
    t0, t1 = time.process_time(), time.thread_time()
    for fn in (s_run_optimization, s_set_away, s_set_mode, s_set_thermal_parameters, s_simulate_plan,
               s_apply_schedule, s_manual_plan, s_reset_heat_loss, s_factory_reset, s_diagnose,
               s_debug, s_assign, s_topology):
        try:
            await fn()
        except Exception as err:  # noqa: BLE001
            print(f"RESULT {fn.__name__}.harness_error=1 bool  # {type(err).__name__}: {err}")
    print(f"RESULT services_examined={len(EXAMINED)} count")
    print(f"RESULT oracles_failed={sum(1 for v in OK.values() if not v)} count")
    print(f"RESULT perturbed={int(PERTURB)} bool")
    rig.footer(t0, t1)


asyncio.run(main())
