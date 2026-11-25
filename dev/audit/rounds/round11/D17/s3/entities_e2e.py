"""D17-s3 coverage: every user-actuated entity's documented effect, end to end (kind=entity).

Metric: per entity, one RESULT line per oracle, 1 when the documented effect
(README.md "Buttons", "Switches, climate and datetime entities", and
docs/configuration.md where it says more) is observable and 0 when it is not;
``RESULT entities_examined`` counts entities driven. Each entity is created by
its platform's real ``async_setup_entry`` on a real coordinator (rig.py) and
driven through its own method (``async_press``, ``async_turn_on``,
``async_set_temperature``, ``async_set_value`` ...), with cycles at a frozen
clock that is advanced to test the two-hour expiries, and a restart.

Key: the published payload's current action and plan, the entity's own
state properties, and the stored config read back after a restart.

Perturbation (``--perturb``): ``boost:_MAX_LEAD`` and ``boost:_BLOCK_LEAD``
(the boost and block windows) set to one hour in memory -- the four timed
switches' "on for two hours" oracles drop to 0 (down).

Run:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
        dev/audit/rounds/round11/D17/s3/entities_e2e.py [--perturb]
Expected (baseline): every oracle 1; exact.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B13 (shared, 3 seats).
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig  # noqa: E402

import asyncio  # noqa: E402
import logging  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402

from harness import FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

logging.disable(logging.WARNING)
PERTURB = "--perturb" in sys.argv
OK: dict[str, int] = {}
EXAMINED: set[str] = set()
P = "heat_pump_optimizer"


def check(entity: str, name: str, cond: bool, note: str = "") -> None:
    EXAMINED.add(entity)
    OK[f"{entity}.{name}"] = int(bool(cond))
    print(f"RESULT {entity}.{name}={int(bool(cond))} bool" + (f"  # {note}" if note else ""))


async def fresh(eid, when=None, states=None, **cfg):
    rig.freeze(when)
    inst = rig.Install(entry_id=eid, data=rig.base_config(**cfg), states=states)
    await inst.setup()
    await inst.cycle()
    return inst, await inst.all_entities()


async def press(inst, ent):
    await ent.async_press()
    await inst.settle()


async def e_buttons():
    inst, E = await fresh("e_btn", comfort_learning_enabled=True, system_identification_enabled=False)
    b = E[f"button.{P}_optimize_now"]
    rig.advance(1)
    inst.hass.states.set("sensor.prices", FakeState("2.0", attributes={"raw_today": rig.price_rows(48, 2.0)}))
    await press(inst, b)
    check("button.optimize_now", "forces_run_and_publishes", inst.coord.data["schedule"][0]["price"] == 2.0)
    inst.coord._optimization_running = True
    check("button.optimize_now", "unavailable_in_flight", b.available is False)
    inst.coord._optimization_running = False

    s = E[f"button.{P}_learning_run_system_identification"]
    await press(inst, s)
    d = await inst.cycle()
    check("button.learning_run_system_identification", "inert_while_option_off",
          d["system_identification"]["phase"] == "idle")
    inst2, E2 = await fresh("e_sid", system_identification_enabled=True)
    await press(inst2, E2[f"button.{P}_learning_run_system_identification"])
    d = await inst2.cycle()
    check("button.learning_run_system_identification", "arms_when_allowed",
          d["system_identification"]["phase"] == "armed")

    cl = E[f"climate.{P}"]
    for t in (21.0, 21.5, 22.0):
        await cl.async_set_temperature(temperature=t)
        await inst.settle()
    d = await inst.cycle()
    moved = d["comfort_learning"]["overrides"] > 0 and d["comfort_learning"]["learned"] != d["comfort_learning"]["configured"]
    await press(inst, E[f"button.{P}_learning_reset_comfort_weight"])
    d = await inst.cycle()
    check("button.learning_reset_comfort_weight", "undoes_tuning",
          moved and d["comfort_learning"]["learned"] == d["comfort_learning"]["configured"]
          and d["comfort_weight"] == d["comfort_learning"]["configured"])

    inst.coord._apply_house_heat_loss_scale(1.3)
    inst.coord._apply_lower_floor_loss_ratio(1.2)
    await inst.cycle()
    await press(inst, E[f"button.{P}_learning_reset_heat_loss"])
    d = await inst.cycle()
    check("button.learning_reset_heat_loss", "both_to_one",
          d["house_heat_loss_scale"] == 1.0 and d["lower_floor_loss_ratio"] == 1.0)

    fin = E[f"button.{P}_learning_finalize_debug"]
    off_unavail = fin.available is False
    await inst.call("debug_collect", {"action": "start"})
    await inst.reload()
    await inst.cycle()
    await inst.cycle()
    E3 = await inst.all_entities()
    fin = E3[f"button.{P}_learning_finalize_debug"]
    avail = fin.available
    await press(inst, fin)
    st = (await inst.call("debug_collect", {"action": "status"}))["debug"]["e_btn"]
    check("button.learning_finalize_debug", "gated_and_ends_collection",
          off_unavail and avail and st["final"] and fin.available is False)

    inst4, E4 = await fresh("e_diag")
    for _ in range(6):
        rig.advance(15)
        await inst4.cycle()
    await press(inst4, E4[f"button.{P}_diagnose_last_interval"])
    acc = E4[f"sensor.{P}_prediction_accuracy"]
    diag = (acc.extra_state_attributes or {}).get("last_diagnosis") or {}
    check("button.diagnose_last_interval", "published_on_accuracy_sensor", "unexplained" in diag)


async def e_climate():
    inst, E = await fresh("e_clim")
    cl = E[f"climate.{P}"]
    await cl.async_set_temperature(temperature=22.5)
    await inst.settle()
    d = await inst.cycle()
    check("climate.heat_pump_optimizer", "target_is_comfort_target",
          cl.native_target_temperature == 22.5 and max(x["setpoint"] for x in d["schedule"]) >= 22.0)
    await inst.restart()
    await inst.cycle()
    cl = (await inst.all_entities())[f"climate.{P}"]
    check("climate.heat_pump_optimizer", "target_survives_restart", cl.native_target_temperature == 22.5)
    good = True
    for preset, mode in (("comfort", "comfort"), ("economy", "economy"), ("boost", "boost"), ("auto", "auto")):
        await cl.async_set_preset_mode(preset)
        await inst.settle()
        good &= inst.coord.mode == mode and cl.preset_mode == preset
    check("climate.heat_pump_optimizer", "presets_set_modes", good)
    good = True
    for hv, mode in (("off", "off"), ("heat", "comfort"), ("auto", "auto")):
        await cl.async_set_hvac_mode(hv)
        await inst.settle()
        good &= inst.coord.mode == mode
    check("climate.heat_pump_optimizer", "hvac_modes", good)
    inst2, E2 = await fresh("e_clim2", comfort_learning_enabled=True)
    await E2[f"climate.{P}"].async_set_temperature(temperature=21.5)
    await inst2.settle()
    d = await inst2.cycle()
    check("climate.heat_pump_optimizer", "records_comfort_observation_when_learning",
          d["comfort_learning"]["overrides"] == 1)


async def e_away():
    inst, E = await fresh("e_away")
    sw, dt_e = E[f"switch.{P}_away"], E[f"datetime.{P}_away_return"]
    await sw.async_turn_on()
    await inst.settle()
    d = await inst.cycle()
    check("switch.away", "turns_setback_on", sw.is_on and d["away_active"] and d["away_source"] == "service")
    rt = (dt_util.now() + timedelta(hours=40)).replace(microsecond=0)
    await dt_e.async_set_value(rt)
    await inst.settle()
    d = await inst.cycle()
    check("datetime.away_return", "sets_return_through_set_away",
          d["away_override_return_time"] == rt.isoformat() and dt_e.native_value == rt)
    await inst.restart()
    d = await inst.cycle()
    E = await inst.all_entities()
    sw, dt_e = E[f"switch.{P}_away"], E[f"datetime.{P}_away_return"]
    check("datetime.away_return", "survives_restart", dt_e.native_value == rt)
    await sw.async_turn_off()
    await inst.settle()
    d = await inst.cycle()
    check("switch.away", "turns_off_and_clears_return", not sw.is_on and not d["away_active"] and dt_e.native_value is None)


async def e_timed():
    noon = datetime(2026, 1, 14, 12, 0, tzinfo=timezone.utc)
    cold = {"sensor.tank": FakeState("33.0", attributes={"unit_of_measurement": "°C"})}
    for key, act in (("boost_space", "space"), ("dhw_boost", "dhw"), ("block_space", "space"), ("block_dhw", "dhw")):
        rig.BASE_STATES["sensor.indoor"] = ("19.4", {}) if key == "block_space" else ("21.4", {})
        when, states = noon, cold
        if key == "block_dhw":
            # The tank plans a pre-heat now (16:30, 39 °C, the 17:00 window ahead): a block has something to hold.
            when = datetime(2026, 1, 14, 16, 30, tzinfo=timezone.utc)
            states = {"sensor.tank": FakeState("39.0", attributes={"unit_of_measurement": "°C"})}
        inst, E = await fresh(f"e_{key}", when=when, states=states, dhw_temp_entity="sensor.tank")
        sw = E[f"switch.{P}_{key}"]
        before = inst.coord.data["current_action"]
        await sw.async_turn_on()
        await inst.settle()
        d = await inst.cycle()
        a = d["current_action"]
        if key == "boost_space":
            effect = a.get("power_normalized") == 1.0 and inst.coord.mode == "auto"
        elif key == "dhw_boost":
            effect = (a.get("dhw_power") or 0) >= 3.0 and inst.coord.mode == "auto"
        elif key == "block_space":
            effect = (a.get("power_normalized") or 0) == 0.0 and (before.get("power_normalized") or 0) > 0
        else:
            effect = (a.get("dhw_power") or 0) == 0.0 and (before.get("dhw_power") or 0) > 0
        check(f"switch.{key}", "on_applies_effect", sw.is_on and effect,
              f"before {before.get('power_normalized')}/{before.get('dhw_power')} after {a.get('power_normalized')}/{a.get('dhw_power')}")
        await inst.restart()
        await inst.cycle()
        sw = (await inst.all_entities())[f"switch.{P}_{key}"]
        on_after_restart = sw.is_on
        rig.advance(119)
        still = sw.is_on
        rig.advance(2)
        d = await inst.cycle()
        check(f"switch.{key}", "holds_two_hours_across_restart_then_expires",
              on_after_restart and still and not sw.is_on, f"{on_after_restart} {still} {sw.is_on}")
    rig.BASE_STATES["sensor.indoor"] = ("21.4", {})
    # Without hot water the two DHW switches are unavailable, disabled by default, and heat nothing.
    inst, E = await fresh("e_nodhw")
    rig.freeze()
    inst = rig.Install(entry_id="e_nodhw2", data=rig.base_config(dhw=False))
    await inst.setup()
    await inst.cycle()
    E = await inst.all_entities()
    ok = True
    for key in ("dhw_boost", "block_dhw"):
        sw = E[f"switch.{P}_{key}"]
        ok &= sw.available is False and getattr(sw, "entity_registry_enabled_default", True) is False
    await E[f"switch.{P}_dhw_boost"].async_turn_on()
    await inst.settle()
    d = await inst.cycle()
    check("switch.dhw_boost", "no_dhw_unavailable_and_no_heat", ok and not (d["current_action"].get("dhw_power") or 0))
    # A safety floor releases a space block and the switch says why.
    rig.BASE_STATES["sensor.indoor"] = ("15.2", {})
    inst, E = await fresh("e_blkrel")
    sw = E[f"switch.{P}_block_space"]
    await sw.async_turn_on()
    await inst.settle()
    await inst.cycle()
    check("switch.block_space", "safety_release_says_why",
          not sw.is_on and (sw.extra_state_attributes or {}).get("block_release") is not None,
          f"is_on {sw.is_on} attrs {sw.extra_state_attributes}")
    rig.BASE_STATES["sensor.indoor"] = ("21.4", {})


async def e_optimizer_active():
    inst, E = await fresh("e_oa")
    sw = E[f"switch.{P}_optimizer_active"]
    await inst.call("set_mode", {"mode": "economy"})
    await sw.async_turn_on()
    await inst.settle()
    keeps = inst.coord.mode == "economy"
    await sw.async_turn_off()
    await inst.settle()
    d = await inst.cycle()
    off = inst.coord.mode == "off" and not sw.is_on and d["current_action"].get("heat_pump_on") is False
    await sw.async_turn_on()
    await inst.settle()
    check("switch.optimizer_active", "on_only_from_off_and_off_disables",
          keeps and off and inst.coord.mode == "auto" and sw.is_on)
    await sw.async_turn_off()
    await inst.settle()
    await inst.restart()
    await inst.cycle()
    sw = (await inst.all_entities())[f"switch.{P}_optimizer_active"]
    check("switch.optimizer_active", "off_survives_restart", not sw.is_on and inst.coord.mode == "off")


async def main() -> None:
    from heatpump_optimizer import boost

    if PERTURB:
        boost._MAX_LEAD = timedelta(hours=1)
        boost._BLOCK_LEAD = timedelta(hours=1)
    t0, t1 = time.process_time(), time.thread_time()
    for fn in (e_buttons, e_climate, e_away, e_timed, e_optimizer_active):
        try:
            await fn()
        except Exception as err:  # noqa: BLE001
            import traceback

            traceback.print_exc()
            print(f"RESULT {fn.__name__}.harness_error=1 bool  # {type(err).__name__}: {err}")
    print(f"RESULT entities_examined={len(EXAMINED)} count")
    print(f"RESULT oracles_failed={sum(1 for v in OK.values() if not v)} count")
    print(f"RESULT perturbed={int(PERTURB)} bool")
    rig.footer(t0, t1)


asyncio.run(main())
