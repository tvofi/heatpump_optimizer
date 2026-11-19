"""D17-s3 coverage: each shipped blueprint's contract with the integration, end to end (kind=blueprint).

Metric: per blueprint, one RESULT line per oracle, 1 when what the blueprint
reads or calls exists and behaves as its own description says, 0 otherwise;
``RESULT blueprints_examined`` counts blueprints. The oracle is the
blueprint's description and input help (and README.md "Blueprints"): its
default entity id must be an entity the integration creates; the attribute,
event and event-data names its triggers and templates read must be ones the
integration publishes, non-empty in a state that reaches them; the action it
calls must accept every option the blueprint offers. Entities come from the
platforms' real ``async_setup_entry``; events from the real notifier on a real
coordinator (rig.py, a recording ``hass.bus.async_fire``).

Key: the entity ids the platforms register, their published attributes, and
the event payloads fired on the bus.

Perturbation (``--perturb``): ``notifier:EVENT_DATA`` for the manual-plan
release event loses its ``steps`` key in memory; the notifications blueprint's
template-keys oracle drops to 0 (down).

Run:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
        dev/audit/rounds/round11/D17/s3/blueprints_e2e.py [--perturb]
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
import re  # noqa: E402
import time  # noqa: E402
from datetime import timedelta  # noqa: E402

import yaml  # noqa: E402
from harness import FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

logging.disable(logging.WARNING)
PERTURB = "--perturb" in sys.argv
BP = "blueprints/automation"
OK: dict[str, int] = {}
EXAMINED: set[str] = set()


class _Loader(yaml.SafeLoader):
    pass


_Loader.add_constructor("!input", lambda loader, node: {"!input": loader.construct_scalar(node)})


def load(name):
    with open(f"{BP}/{name}") as fh:
        return yaml.load(fh, Loader=_Loader)


def check(bp: str, name: str, cond: bool, note: str = "") -> None:
    EXAMINED.add(bp)
    OK[f"{bp}.{name}"] = int(bool(cond))
    print(f"RESULT {bp}.{name}={int(bool(cond))} bool" + (f"  # {note}" if note else ""))


def default_of(doc, key):
    return doc["blueprint"]["input"][key].get("default")


async def fresh(eid, states=None, **cfg):
    rig.freeze()
    inst = rig.Install(entry_id=eid, data=rig.base_config(**cfg), states=states)
    await inst.setup()
    await inst.cycle()
    return inst, await inst.all_entities()


async def b_ev():
    name = "charge_ev_from_grid_headroom.yaml"
    doc = load(name)
    eid = default_of(doc, "headroom_sensor")
    inst, E = await fresh("b_ev0")
    ent = E.get(eid)
    check(name, "default_entity_exists", ent is not None, eid)
    check(name, "unavailable_while_nothing_bounds", ent is not None and ent.available is False)
    states = {"sensor.house": FakeState("3000", attributes={"unit_of_measurement": "W", "device_class": "power"})}
    inst, E = await fresh("b_ev1", states=states, main_fuse_amperes=16, house_power_entity="sensor.house")
    ent = E[eid]
    attrs = ent.extra_state_attributes or {}
    limit = attrs.get("limit_kw")
    val = ent.native_value
    check(name, "min_limit_minus_house_draw_clamped",
          ent.available and limit is not None and val is not None and abs(val - max(0.0, limit - 3.0)) < 0.01,
          f"limit {limit} value {val}")


async def b_economy():
    name = "economy_mode_on_price_peak.yaml"
    doc = load(name)
    eid = default_of(doc, "price_sensor")
    inst, E = await fresh("b_eco")
    ent = E.get(eid)
    check(name, "default_entity_exists_and_reads_price",
          ent is not None and ent.native_value == inst.coord.data["current_price"], eid)
    from heatpump_optimizer import services

    opts = doc["blueprint"]["input"]["expensive_mode"]["selector"]["select"]["options"]
    ok = True
    for mode in opts:
        try:
            services.SERVICE_SCHEMA_SET_MODE({"mode": mode})
        except Exception:  # noqa: BLE001
            ok = False
    check(name, "every_offered_mode_accepted", ok, str(opts))
    stamp = inst.coord.data["last_optimization"]
    rig.advance(1)
    await inst.call("set_mode", {"mode": "economy"})
    d = inst.coord.data
    check(name, "set_mode_shows_in_plan_straight_away", d["mode"] == "economy" and d["last_optimization"] != stamp)


def template_keys(doc, alias):
    for opt in doc["action"][1]["choose"]:
        if opt.get("alias") == alias:
            text = yaml.dump(opt["sequence"])
            return set(re.findall(r"data\.([a-z_]+)", text))
    return set()


async def b_notifications():
    name = "notifications.yaml"
    doc = load(name)
    from heatpump_optimizer import notifier

    if PERTURB:
        notifier.EVENT_DATA[notifier.EVENT_MANUAL_PLAN_RELEASED] = tuple(
            k for k in notifier.EVENT_DATA[notifier.EVENT_MANUAL_PLAN_RELEASED] if k != "steps")
    events = [t["event_type"] for t in doc["trigger"]]
    check(name, "every_trigger_event_fired_by_integration", set(events) == set(notifier.EVENT_DATA), str(events))
    aliases = {"Monthly receipt": notifier.EVENT_MONTHLY_RECEIPT, "Comfort at risk": notifier.EVENT_COMFORT_AT_RISK,
               "Input gone stale": notifier.EVENT_INPUT_STALE, "Plan gone stale": notifier.EVENT_PLAN_STALE,
               "Manual plan released": notifier.EVENT_MANUAL_PLAN_RELEASED}
    missing = {a: sorted(template_keys(doc, a) - set(notifier.EVENT_DATA[e])) for a, e in aliases.items()}
    check(name, "template_keys_carried", not any(missing.values()), str(missing))
    # End to end: a cold house fires comfort-at-risk; a forced-off hot-water
    # pin that safety releases fires manual-plan-released; a stale indoor
    # reading fires input-stale. Each carries entry_id and the keys the
    # template reads, non-null.
    rig.BASE_STATES["sensor.indoor"] = ("16.0", {})
    inst, _E = await fresh("b_note")
    rig.BASE_STATES["sensor.indoor"] = ("21.4", {})
    s0 = dt_util.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    await inst.call("apply_manual_plan", {"space_slots": [], "dhw_slots": [],
                                          "expires_at": (s0 + timedelta(hours=12)).isoformat()})
    await inst.cycle()
    inst.hass.states.set("sensor.indoor", FakeState("21.0", last_updated=dt_util.now() - timedelta(hours=6)))
    rig.advance(15)
    await inst.cycle()
    fired = {}
    for ev, data in inst.fired:
        fired.setdefault(ev, data)
    for alias, ev in (("Comfort at risk", notifier.EVENT_COMFORT_AT_RISK),
                      ("Manual plan released", notifier.EVENT_MANUAL_PLAN_RELEASED),
                      ("Input gone stale", notifier.EVENT_INPUT_STALE)):
        data = fired.get(ev)
        need = template_keys(doc, alias) - {"cause", "peak_guard_suppressing"}
        good = data is not None and data.get("entry_id") == "b_note" and all(data.get(k) is not None for k in need)
        check(name, f"fires_{ev.split('optimizer_')[1]}_with_keys", good, str(data)[:160])


async def b_manual():
    name = "notify_on_manual_plan.yaml"
    doc = load(name)
    eid = default_of(doc, "plan_sensor")
    inst, E = await fresh("b_man")
    ent = E.get(eid)
    check(name, "default_entity_exists", ent is not None, eid)
    # The blueprint's condition reads ``attributes.get('manual_override') is
    # not none``: a key published with a None value reads as absent to it.
    absent_before = (ent.extra_state_attributes or {}).get("manual_override") is None
    s0 = dt_util.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=2)
    await inst.call("apply_manual_plan", {"space_slots": [{"start": s0.isoformat(),
                                                           "end": (s0 + timedelta(hours=1)).isoformat()}]})
    await inst.cycle()
    mo = (ent.extra_state_attributes or {}).get("manual_override")
    await inst.call("clear_manual_plan", {})
    await inst.cycle()
    absent_after = (ent.extra_state_attributes or {}).get("manual_override") is None
    print(f"RESULT {name}.key_published_while_unpinned={int('manual_override' in (ent.extra_state_attributes or {}))} bool")
    check(name, "manual_override_with_expiry_only_while_pinned",
          absent_before and isinstance(mo, dict) and mo.get("expires_at") and absent_after, str(mo)[:120])


async def b_wood():
    name = "notify_wood_cheaper_window.yaml"
    doc = load(name)
    eid = default_of(doc, "wood_sensor")
    states = {"sensor.woodtop": FakeState("60.0", attributes={"unit_of_measurement": "°C"})}
    inst, E = await fresh("b_wood", states=states, wood_furnace_enabled=True, wood_tank_top_entity="sensor.woodtop",
                          external_heat_detection_enabled=True, wood_type="birch", wood_packing="packed",
                          wood_price_sek_m3=100.0, wood_furnace_efficiency=75.0)
    ent = E.get(eid)
    check(name, "default_entity_exists", ent is not None, eid)
    attrs = ent.extra_state_attributes or {} if ent is not None else {}
    wins = attrs.get("cheaper_windows")
    shape = isinstance(wins, list) and all(isinstance(w, dict) and "start" in w and "end" in w for w in wins)
    check(name, "attributes_read_by_template",
          ent is not None and ent.available and shape and "lighting_start" in attrs and "lighting_end" in attrs
          and (not wins or attrs.get("lighting_start") is not None),
          f"available {ent.available if ent else None} windows {len(wins or [])} start {attrs.get('lighting_start')}")


async def main() -> None:
    t0, t1 = time.process_time(), time.thread_time()
    for fn in (b_ev, b_economy, b_notifications, b_manual, b_wood):
        try:
            await fn()
        except Exception as err:  # noqa: BLE001
            import traceback

            traceback.print_exc()
            print(f"RESULT {fn.__name__}.harness_error=1 bool  # {type(err).__name__}: {err}")
    print(f"RESULT blueprints_examined={len(EXAMINED)} count")
    print(f"RESULT oracles_failed={sum(1 for v in OK.values() if not v)} count")
    print(f"RESULT perturbed={int(PERTURB)} bool")
    rig.footer(t0, t1)


asyncio.run(main())
