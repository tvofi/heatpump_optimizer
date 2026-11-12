#!/usr/bin/env python3
"""The block-switch mutants, driven without a solve.

``tests/features.py`` already states these checks. This script states them
again so a mutation drive can kill the new sites without that script's
solves: each check is the predicate one operator flips.

    PYTHONPATH=tests/hastub python3 tests/block_duty.py
"""
from __future__ import annotations

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from dataclasses import replace
from types import SimpleNamespace

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState, Results  # noqa: E402
from heatpump_optimizer import boost as boost_mod  # noqa: E402
from heatpump_optimizer import entity as entity_mod  # noqa: E402
from heatpump_optimizer import pump_arbiter as arb  # noqa: E402
from heatpump_optimizer import setpoint_check  # noqa: E402
from heatpump_optimizer import switch as switch_mod  # noqa: E402
from heatpump_optimizer.const import (  # noqa: E402
    ECONOMY_ABSOLUTE_FLOOR,
    MODE_AUTO,
    SPACE_PUMP_FLOOR_MARGIN_C,
)
from heatpump_optimizer.dhw_schedule import parse_windows  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402

UTC = timezone.utc
R = Results("block duty")
NOW = datetime(2026, 7, 1, 12, 0, tzinfo=UTC)
entity_mod.publish_then_refresh = lambda _ent: None


def check(name: str, fn) -> None:
    try:
        ok = fn()
        detail = "" if ok else "predicate false"
    except Exception as exc:  # noqa: BLE001 - a mutant that raises is a kill
        ok, detail = False, f"{type(exc).__name__}: {exc}"
    R.check(name, bool(ok), detail)


class _Coord:
    def __init__(self, snap=None, data=None):
        self._snap = snap
        self.data = data if data is not None else {}
        self.hass = FakeHass()
        self._current_action = {}
        self.refreshed = 0
        self.entry = SimpleNamespace(entry_id="block-duty")

    def arbiter_inputs(self):
        return self._snap

    def adopt_action(self, action):
        self._current_action = action

    async def async_request_refresh(self):
        self.refreshed += 1


def _snap(**kw):
    return arb.ArbiterInputs(
        hass=None,
        config=kw.get("config") or {},
        mode=kw.get("mode", MODE_AUTO),
        plan=kw.get("plan"),
        plan_stale=kw.get("stale", False),
        entry_released=False,
        state=kw.get("state") or SimpleNamespace(
            room_temperature=21.0, outdoor_temperature=5.0, dhw_temperature=50.0,
        ),
        thermal=None,
        params=kw.get("params") or SimpleNamespace(
            dhw_min_temp=40.0, dhw_demand_windows=[],
        ),
        action=kw.get("action") or {},
        measured_power_kw=None,
        disinfecting=kw.get("disinfecting", False),
    )


def main() -> int:
    check("BLOCK_HOURS is 2", lambda: boost_mod.BLOCK_HOURS == 2)
    check(
        "the boost lead stays two hours while both constants are 2",
        lambda: boost_mod._MAX_LEAD == timedelta(hours=2)
        and boost_mod._BLOCK_LEAD == timedelta(hours=2),
    )

    life = boost_mod.BoostState()
    life.set("space", True, NOW, block=True)
    check(
        "a block is live until its own end and not after",
        lambda: life.block_active(boost_mod.CHANNEL_SPACE, NOW)
        and life.block_active(
            "space", NOW + timedelta(hours=2) - timedelta(seconds=1)
        )
        and not life.block_active("space", NOW + timedelta(hours=2)),
    )
    ended = boost_mod.BoostState()
    ended.blocked["space"] = NOW
    ended.expire(NOW)
    check(
        "expiry at the end drops the block and does not settle a block",
        lambda: "space" not in ended.blocked and ended.space_settle_until is None,
    )

    far = boost_mod.BoostState()
    far.blocked["space"] = NOW + timedelta(hours=5)
    far.expire(NOW)
    check(
        "a block dated more than two hours ahead is clamped to two hours",
        lambda: far.blocked.get("space") == NOW + timedelta(hours=2),
    )

    space_boost = boost_mod.BoostState()
    space_boost.set("space", True, NOW)
    space_boost.set("space", True, NOW, block=True)
    check(
        "a space block replacing a live boost sets the settling tail and clears the boost",
        lambda: space_boost.until == {}
        and "space" in space_boost.blocked
        and space_boost.space_settle_until is not None,
    )
    dhw_only = boost_mod.BoostState()
    dhw_only.set("dhw", True, NOW)
    dhw_only.set("dhw", True, NOW, block=True)
    check(
        "a DHW block replacing a boost does not set the space settling tail",
        lambda: dhw_only.space_settle_until is None and "dhw" in dhw_only.blocked,
    )
    back = boost_mod.BoostState()
    back.set("space", True, NOW, block=True)
    back.set("space", True, NOW)
    check(
        "a later boost clears the block",
        lambda: back.blocked == {} and "space" in back.until,
    )

    base = {
        "power": 1.2, "dhw_power": 0.4, "dhw_heating_active": True,
        "heat_pump_on": True, "mode": "normal", "power_normalized": 0.3,
    }
    plain = dict(base)
    boost_mod.overlay(plain, boost_mod.BoostState(), max_power=6.0, max_temp=24.0, ecl_max=8.0)
    check("no block leaves the action unchanged", lambda: plain == base)
    space_held = boost_mod.BoostState()
    space_held.set("space", True, NOW, block=True)
    space_action = dict(base)
    boost_mod.overlay(space_action, space_held, max_power=6.0, max_temp=24.0, ecl_max=8.0)
    check(
        "a space block zeroes space power and not the supply switch",
        lambda: space_action["power"] == 0.0
        and space_action["power_normalized"] == 0.0
        and space_action["heat_pump_on"] is True
        and space_action["dhw_power"] == 0.4,
    )
    no_norm = {"power": 1.2, "dhw_power": 0.4, "heat_pump_on": True}
    no_norm_held = boost_mod.BoostState()
    no_norm_held.set("space", True, NOW, block=True)
    boost_mod.overlay(no_norm, no_norm_held, max_power=6.0, max_temp=24.0, ecl_max=8.0)
    check(
        "a space block does not invent power_normalized",
        lambda: "power_normalized" not in no_norm and no_norm["power"] == 0.0,
    )
    dhw_action = dict(base)
    dhw_held = boost_mod.BoostState()
    dhw_held.set("dhw", True, NOW, block=True)
    boost_mod.overlay(dhw_action, dhw_held, max_power=6.0, max_temp=24.0, ecl_max=8.0)
    check(
        "a DHW block zeroes hot water",
        lambda: dhw_action["dhw_power"] == 0.0
        and dhw_action["dhw_heating_active"] is False
        and dhw_action["power"] == 1.2,
    )

    warm = _snap()
    check(
        "no floor is a reason",
        lambda: boost_mod.block_release_reason(_Coord(warm), "dhw", NOW, warm) is None
        and boost_mod.block_release_reason(_Coord(warm), "space", NOW, warm) is None,
    )
    due = _Coord(warm, {"dhw_legionella_due_in_hours": 1.0, "horizon_hours": 24.0})
    overdue = _Coord(warm, {"dhw_legionella_due_in_hours": -2.0, "horizon_hours": 24.0})
    check(
        "a due or overdue cycle inside the horizon releases DHW",
        lambda: boost_mod.block_release_reason(due, "dhw", NOW) == boost_mod.RELEASE_LEGIONELLA
        and boost_mod.block_release_reason(overdue, "dhw", NOW) == boost_mod.RELEASE_LEGIONELLA,
    )
    edge = _Coord(warm, {"dhw_legionella_due_in_hours": 24.0, "horizon_hours": 24.0})
    check(
        "a cycle exactly at the horizon does not release",
        lambda: boost_mod.block_release_reason(edge, "dhw", NOW) is None,
    )
    hold = _snap(disinfecting=True)
    check(
        "a live disinfection hold releases DHW",
        lambda: boost_mod.block_release_reason(_Coord(hold), "dhw", NOW, hold)
        == boost_mod.RELEASE_DISINFECTION,
    )
    tank_params = SimpleNamespace(
        dhw_min_temp=45.0, dhw_demand_windows=parse_windows("00:00-23:59"),
    )
    tank = _snap(
        state=SimpleNamespace(room_temperature=21.0, outdoor_temperature=5.0, dhw_temperature=45.0),
        params=tank_params,
    )
    check(
        "the tank at its minimum inside a window releases DHW",
        lambda: boost_mod.block_release_reason(_Coord(tank), "dhw", NOW, tank)
        == boost_mod.RELEASE_TANK,
    )
    closed_params = SimpleNamespace(
        dhw_min_temp=45.0, dhw_demand_windows=parse_windows("00:00-01:00"),
    )
    closed = _snap(
        state=SimpleNamespace(room_temperature=21.0, outdoor_temperature=5.0, dhw_temperature=45.0),
        params=closed_params,
    )
    check(
        "the tank at its minimum outside a demand window does not release",
        lambda: boost_mod.block_release_reason(_Coord(closed), "dhw", NOW, closed) is None,
    )
    room_at = ECONOMY_ABSOLUTE_FLOOR + SPACE_PUMP_FLOOR_MARGIN_C
    room = _snap(state=SimpleNamespace(room_temperature=room_at, outdoor_temperature=5.0))
    above = _snap(state=SimpleNamespace(
        room_temperature=room_at + 0.1, outdoor_temperature=5.0,
    ))
    check(
        "the room floor releases at the margin and not above it",
        lambda: boost_mod.block_release_reason(_Coord(room), "space", NOW, room)
        == boost_mod.RELEASE_ROOM
        and boost_mod.block_release_reason(_Coord(above), "space", NOW, above) is None,
    )
    plan = SimpleNamespace(timestamps=[NOW], optimal_setpoints=[21.0], predictive_info={})
    cold = _snap(
        state=SimpleNamespace(room_temperature=18.0, outdoor_temperature=-11.0),
        plan=plan,
    )
    check(
        "the cold rail releases a space block",
        lambda: boost_mod.block_release_reason(_Coord(cold), "space", NOW, cold)
        == boost_mod.RELEASE_COLD,
    )
    rail = SimpleNamespace(state=SimpleNamespace(
        outdoor_temperature=arb.COLD_RAIL_C, room_temperature=18.0,
    ), plan_stale=False, plan=plan)
    below = SimpleNamespace(state=SimpleNamespace(
        outdoor_temperature=arb.COLD_RAIL_C - 0.1, room_temperature=18.0,
    ), plan_stale=False, plan=plan)
    check(
        "the cold rail is strict below its threshold",
        lambda: arb.block_cold_lease(rail, NOW) is False
        and arb.block_cold_lease(below, NOW) is True,
    )
    missing = SimpleNamespace(state=SimpleNamespace(
        outdoor_temperature=-11.0, room_temperature=None,
    ), plan_stale=False, plan=plan)
    check(
        "a missing room below the rail counts",
        lambda: arb.block_cold_lease(missing, NOW) is True,
    )
    sysid = _snap(action={"mode": "system_identification"})
    stale = _snap(stale=True)
    check(
        "sysid and a stale plan release a block",
        lambda: boost_mod.block_release_reason(_Coord(sysid), "space", NOW, sysid)
        == boost_mod.RELEASE_SYSID
        and boost_mod.block_release_reason(_Coord(stale), "dhw", NOW, stale)
        == boost_mod.RELEASE_STALE,
    )
    check(
        "no snapshot is not a reason",
        lambda: boost_mod.block_release_reason(_Coord(None), "dhw", NOW) is None,
    )

    apply_c = _Coord(
        warm, {"dhw_legionella_due_in_hours": 1.0, "horizon_hours": 24.0, "dhw_enabled": True},
    )
    boost_mod.adopt_plan(apply_c, {"power": 1.0, "dhw_power": 0.5, "heat_pump_on": True})
    boost_mod.held_for(apply_c).set("dhw", True, boost_mod.dt_util.now(), block=True)
    saved = []

    async def _save(_data):
        saved.append(_data)

    real_store = boost_mod._store

    def _mem_store(_coord):
        return SimpleNamespace(async_save=_save, async_load=lambda: None)

    scheduled = []

    def _schedule(coro):
        scheduled.append(coro)
        coro.close()

    apply_c.hass.async_create_task = _schedule
    boost_mod._store = _mem_store
    try:
        boost_mod.apply(apply_c, boost_mod.BoostOverlay(6.0, 24.0, 8.0))
    finally:
        boost_mod._store = real_store
    check(
        "a due cycle releases the block before the overlay and asks to persist",
        lambda: "dhw" not in boost_mod.held_for(apply_c).blocked
        and apply_c._current_action["dhw_power"] == 0.5
        and len(scheduled) == 1,
    )

    bare = SimpleNamespace(data={}, hass=FakeHass())
    check(
        "a coordinator with no arbiter inputs has no release reason",
        lambda: boost_mod.block_release_reason(bare, "space", NOW) is None,
    )
    unmapped = SimpleNamespace(data=None, hass=FakeHass(), arbiter_inputs=lambda: warm)
    check(
        "a non-mapping payload is not a legionella reason",
        lambda: boost_mod.block_release_reason(unmapped, "dhw", NOW, warm) is None,
    )
    planned = _snap(plan=SimpleNamespace(
        timestamps=[NOW], optimal_setpoints=[21.0],
        predictive_info={"dhw_windows": "00:00-23:59"},
    ), params=SimpleNamespace(dhw_min_temp=45.0, dhw_demand_windows=[]),
        state=SimpleNamespace(room_temperature=21.0, outdoor_temperature=5.0, dhw_temperature=45.0),
    )
    check(
        "a planned demand window releases the tank floor",
        lambda: boost_mod.block_release_reason(_Coord(planned), "dhw", NOW, planned)
        == boost_mod.RELEASE_TANK,
    )

    clock = boost_mod.dt_util.now()
    loaded = _Coord(warm)
    loaded.entry = SimpleNamespace(entry_id="restore-block")

    class _Mem:
        def __init__(self, *a, **k):
            pass

        async def async_load(self):
            return {
                "dhw": {"until": (clock + timedelta(hours=1)).isoformat()},
                "block_space": {"until": (clock + timedelta(hours=1)).isoformat()},
                "block_dhw": {"until": clock.isoformat()},
            }

        async def async_save(self, data):
            return None

    real = boost_mod.QuarantiningStore
    boost_mod.QuarantiningStore = _Mem
    try:
        asyncio.run(boost_mod.restore(loaded))
    finally:
        boost_mod.QuarantiningStore = real
    held = boost_mod.held_for(loaded)
    check(
        "restore keeps a future block and a future boost, not one dated now",
        lambda: "dhw" in held.until and "space" in held.blocked and "dhw" not in held.blocked,
    )
    exact = _Coord(warm)
    exact.entry = SimpleNamespace(entry_id="restore-exact")
    fixed_now = datetime(2026, 8, 1, 12, 0, tzinfo=UTC)
    real_now = boost_mod.dt_util.now

    class _Exact:
        def __init__(self, *a, **k):
            pass

        async def async_load(self):
            return {"block_dhw": {"until": fixed_now.isoformat()}}

        async def async_save(self, data):
            return None

    boost_mod.dt_util.now = lambda: fixed_now
    boost_mod.QuarantiningStore = _Exact
    try:
        asyncio.run(boost_mod.restore(exact))
    finally:
        boost_mod.dt_util.now = real_now
        boost_mod.QuarantiningStore = real
    check(
        "a block dated at this instant is not still live",
        lambda: "dhw" not in boost_mod.held_for(exact).blocked,
    )

    stale_block = _Coord(warm, {"dhw_legionella_due_in_hours": 1.0, "horizon_hours": 24.0})
    boost_mod.held_for(stale_block).blocked["dhw"] = clock - timedelta(hours=3)
    dropped = boost_mod.release_blocked(stale_block, warm, clock)
    check(
        "an already-expired block is not released",
        lambda: dropped is False and "dhw" in boost_mod.held_for(stale_block).blocked,
    )
    live = _Coord(warm)
    boost_mod.held_for(live).set("space", True, clock, block=True)
    check(
        "a live block with no floor is kept",
        lambda: boost_mod.release_blocked(live, warm, clock) is False
        and "space" in boost_mod.held_for(live).blocked,
    )

    refresh = _Coord(warm)
    asyncio.run(boost_mod.set_block(refresh, "dhw", True))
    check(
        "turning a block on refreshes",
        lambda: refresh.refreshed == 1 and "dhw" in boost_mod.held_for(refresh).blocked,
    )
    refused = _Coord(warm, {"dhw_legionella_due_in_hours": 1.0, "horizon_hours": 24.0})
    asyncio.run(boost_mod.set_block(refused, "dhw", True, refresh=False))
    check(
        "a due cycle refuses the on-press",
        lambda: "dhw" not in boost_mod.held_for(refused).blocked,
    )

    entry = FakeEntry()
    sw_coord = _Coord(warm)
    sw_coord.data = {"dhw_enabled": True}
    block_sw = switch_mod.BlockDhwSwitch(sw_coord, entry)
    boost_sw = switch_mod.BoostDhwSwitch(sw_coord, entry)
    boost_mod.held_for(sw_coord).set("dhw", True, boost_mod.dt_util.now(), block=True)
    check("a block switch reads the block channel", lambda: block_sw.is_on is True)
    check("a boost switch does not read the block channel", lambda: boost_sw.is_on is False)
    boost_mod.held_for(sw_coord).blocked.clear()
    boost_mod.held_for(sw_coord).set("dhw", True, boost_mod.dt_util.now())
    check("a boost switch reads the boost channel", lambda: boost_sw.is_on is True)
    why_coord = _Coord(warm, {"dhw_legionella_due_in_hours": 1.0, "horizon_hours": 24.0})
    why = switch_mod.BlockDhwSwitch(why_coord, entry)
    boost_why = switch_mod.BoostDhwSwitch(why_coord, entry)
    check(
        "the block switch says why and the boost switch does not",
        lambda: why.extra_state_attributes == {"block_release": boost_mod.RELEASE_LEGIONELLA}
        and boost_why.extra_state_attributes is None,
    )
    quiet = switch_mod.BlockSpaceSwitch(_Coord(warm), entry)
    check("a block with no floor publishes no attribute", lambda: quiet.extra_state_attributes is None)
    press = _Coord(warm)
    press_sw = switch_mod.BlockSpaceSwitch(press, entry)
    asyncio.run(press_sw.async_turn_on())
    check(
        "the block press holds the block channel",
        lambda: "space" in boost_mod.held_for(press).blocked
        and "space" not in boost_mod.held_for(press).until,
    )

    none_duty = arb._without_block(_Coord(warm), None, NOW)
    both = arb._without_block(_Coord(warm), "both", NOW)
    c = _Coord(warm)
    boost_mod.held_for(c).set("space", True, NOW, block=True)
    check(
        "no block leaves the duty, including None",
        lambda: none_duty is None and both == "both",
    )
    dhw_only_block = _Coord(warm)
    boost_mod.held_for(dhw_only_block).set("dhw", True, NOW, block=True)
    check(
        "a space block turns both into dhw, space into idle, and idle stays idle",
        lambda: arb._without_block(c, "both", NOW) == "dhw"
        and arb._without_block(c, "space", NOW) == "idle"
        and arb._without_block(c, "idle", NOW) == "idle"
        and arb._without_block(c, None, NOW) == "dhw",
    )
    check(
        "a DHW block turns both into space",
        lambda: arb._without_block(dhw_only_block, "both", NOW) == "space",
    )
    equal = SimpleNamespace(
        state=SimpleNamespace(outdoor_temperature=-11.0, room_temperature=21.0),
        plan_stale=False,
        plan=SimpleNamespace(timestamps=[NOW], optimal_setpoints=[21.0]),
    )
    check(
        "the cold lease is strict: a room at the plan is not below it",
        lambda: arb.block_cold_lease(equal, NOW) is False,
    )
    arb_coord = _Coord(
        warm, {"dhw_legionella_due_in_hours": 1.0, "horizon_hours": 24.0, "dhw_enabled": True},
    )
    boost_mod.held_for(arb_coord).set("dhw", True, boost_mod.dt_util.now(), block=True)
    arb_held = arb.state_for(arb_coord)
    asyncio.run(arb._arbitrate(arb_coord, arb_held, warm, "observe", boost_mod.dt_util.now()))
    check(
        "the arbiter releases a block a floor forbids before it serves a duty",
        lambda: "dhw" not in boost_mod.held_for(arb_coord).blocked,
    )
    both_off = _Coord(warm)
    boost_mod.held_for(both_off).set("space", True, NOW, block=True)
    boost_mod.held_for(both_off).set("dhw", True, NOW, block=True)
    check(
        "both channels blocked is idle",
        lambda: arb._without_block(both_off, "both", NOW) == "idle",
    )

    disinfection_checks()
    hysteresis_checks()
    return R.close("BLOCK DUTY CHECKS")


def _dhw_snap(*, action=None, disinfecting=False, configured=55.0, cycle=True,
              disinfection=60.0, attrs=None, entity="number.dhw", reading=55.0):
    """A control snapshot over a hot water set-point number, 30 to 65 degC by default.

    ``params`` are the production ``ThermalParameters``, so the cycle's
    temperature is the one its owner states, never a copy in this script.
    """
    snap = _snap(
        config={"pump_duty_mode": "control", "dhw_setpoint_entity": entity},
        params=ThermalParameters(dhw_setpoint=configured, dhw_legionella_temp=disinfection,
                                 dhw_legionella_enabled=cycle, dhw_min_temp=40.0),
        action=action, disinfecting=disinfecting,
    )
    states = {} if entity is None else {
        "number.dhw": FakeState(str(reading), attributes=attrs or {"min": 30, "max": 65, "step": 1}),
    }
    return replace(snap, hass=FakeHass(states))


def _combi_snap(force, **booking):
    """``_dhw_snap`` on an active combi store holding 2 L of potable water, under the limit."""
    snap = _dhw_snap(**booking)
    return replace(snap, params=replace(
        snap.params, dhw_enabled=True, dhw_combi_tank_enabled=True, combi_potable_volume_l=2.0,
        dhw_combi_legionella_force=force, mixing_valve_mode="manual", buffer_tank_volume=300.0,
    ))


def _written(snap, duty):
    return arb.desired(_Coord(snap), snap, duty, NOW).dhw_setpoint


#: Every row of ``desired`` and every way a step books a cycle: the grid the
#: null controls drive, so a row that bypasses the cycle's answer is in it.
_DUTIES = (None, "idle", "space", "dhw", "both")
_BOOKINGS = ({}, {"action": {"dhw_reason": "legionella"}}, {"disinfecting": True},
             {"action": {"dhw_reason": "legionella"}, "disinfecting": True})


def _fix_value(snap, *, arbiter=True):
    """The hot-water repair once the arbiter wrote this step's answer (none
    with ``arbiter`` false), the pump reading the snapshot's value: ``None``
    when it stands down, else the value its Fix writes."""
    coord = _Coord(snap)
    own = arb.desired(coord, snap, "dhw", NOW).dhw_setpoint
    if arbiter and own is not None:
        arb.state_for(coord).written["dhw_setpoint"] = (own, NOW)
    hass = snap.hass
    setpoint_check._dhw(hass, snap.config, snap.params, lambda pump: arb.dhw_gated(coord, pump))
    raised = [i for i in getattr(hass, "issues", []) if i[1] == setpoint_check.ISSUE_DHW]
    return raised[0][2]["data"]["value"] if raised else None


def _step(step):
    """The hot-water entity's attributes, 30 to 80 degC, on ``step``."""
    return {"min": 30, "max": 80, "step": step}


#: The census of ``_dhw_write``'s cycle rounding paths: every step size an
#: entity states here, and everyday/disinfection pairs below, at and above
#: each other, on and off each step, up to the 70 degC cap.
_GRID_STEPS = (0.1, 0.5, 1, 2, 5)
_GRID_TEMPS = (50.0, 55.0, 57.0, 58.0, 60.0, 60.2, 60.3, 60.4, 60.7, 62.0, 69.6, 70.0, 72.0)


def _cycle_grid_over_hard_max():
    """Every (step, everyday, disinfection) whose cycle write exceeds the hard
    maximum the same parameters state, or is no write at all; asserts the
    grid holds all three orderings first, so a narrowed grid refuses."""
    pairs = [(e, d) for e in _GRID_TEMPS[:-1] for d in _GRID_TEMPS]
    assert {(d > e) - (d < e) for e, d in pairs} == {-1, 0, 1}
    bad = []
    for step in _GRID_STEPS:
        for e, d in pairs:
            snap = _dhw_snap(disinfecting=True, configured=e, disinfection=d, attrs=_step(step))
            w = _written(snap, "dhw")
            if w is None or w > snap.params.dhw_hard_max_temp + 1e-9:
                bad.append((step, e, d, w, snap.params.dhw_hard_max_temp))
    return bad


#: The no-cycle arms of the census: the cycle enabled and not running (no
#: booking, the switch not held), and the cycle disabled (switch held).
_NOCYCLE_ARMS = {"idle": dict(cycle=True), "disabled": dict(cycle=False, disinfecting=True)}


def _nocycle_grid_over_limit(arm):
    """Every (step, everyday, disinfection) whose no-cycle write in ``arm``
    exceeds the charge limit (``dhw_max_temp``) the same parameters state, or
    is no write at all. Asserts its preconditions first: every row is one no
    cycle runs on, and every step size but the finest holds an off-step
    everyday set-point, so a narrowed grid refuses."""
    kw = _NOCYCLE_ARMS[arm]
    pairs = [(e, d) for e in _GRID_TEMPS[:-1] for d in _GRID_TEMPS]
    assert all(any(abs(e / s - round(e / s)) > 1e-9 for e in _GRID_TEMPS[:-1]) for s in _GRID_STEPS[1:])
    bad = []
    for step in _GRID_STEPS:
        for e, d in pairs:
            snap = _dhw_snap(configured=e, disinfection=d, attrs=_step(step), **kw)
            assert (snap.params.dhw_cycle_temp is None) == (arm == "disabled") and not snap.action
            assert snap.params.dhw_cycle_temp is None or not snap.disinfecting
            w = _written(snap, "dhw")
            if w is None or w > snap.params.dhw_max_temp + 1e-9:
                bad.append((step, e, d, w, snap.params.dhw_max_temp))
    return bad


def _repair_grid_over_hard_max():
    """Every (step, everyday, disinfection) whose repair Fix, on an install the
    arbiter does not write and a pump reading of 30, exceeds the tank's hard
    maximum the repair's own parameters state."""
    bad = []
    for step in _GRID_STEPS:
        for e in _GRID_TEMPS[:-1]:
            for d in _GRID_TEMPS:
                snap = _dhw_snap(configured=e, disinfection=d, attrs=_step(step), reading=30.0)
                fix = _fix_value(snap, arbiter=False)
                if fix is None or fix > snap.params.dhw_hard_max_temp + 1e-9:
                    bad.append((step, e, d, fix, snap.params.dhw_hard_max_temp))
    return bad


def disinfection_checks() -> None:
    """A disinfection cycle holds its own temperature, not the everyday set-point."""
    written = _written
    check(
        "a commanded or held disinfection cycle writes its temperature, not the configured set-point",
        lambda: written(_dhw_snap(action={"dhw_reason": "legionella"}), "dhw") == 60.0
        and written(_dhw_snap(disinfecting=True), "both") == 60.0
        and written(_dhw_snap(), "dhw") == 55.0,
    )
    check(
        "a configured set-point above the disinfection temperature is never lowered to it",
        lambda: written(_dhw_snap(disinfecting=True, configured=62.0), "dhw") == 62.0,
    )
    check(
        "every row a cycle step can take writes the cycle's temperature, the idle and baseline rows too",
        lambda: all(written(_dhw_snap(action={"dhw_reason": "legionella"}), d) == 60.0
                    for d in (None, "idle", "dhw", "both")),
    )
    check(
        "the cycle's temperature is the thermal parameters' own answer, not a copy",
        lambda: written(_dhw_snap(disinfecting=True, disinfection=58.0), "dhw")
        == ThermalParameters(dhw_setpoint=55.0, dhw_legionella_temp=58.0).dhw_cycle_temp == 58.0,
    )
    check(
        "a cycle never lowers the tank: an everyday set-point above the disinfection temperature is the cycle's and the ceiling's",
        lambda: ThermalParameters(dhw_setpoint=62.0, dhw_legionella_temp=60.0).dhw_cycle_temp == 62.0
        and ThermalParameters(dhw_setpoint=62.0, dhw_legionella_temp=60.0).dhw_hard_max_temp == 62.0
        and ThermalParameters(dhw_setpoint=62.0, dhw_legionella_enabled=False).dhw_cycle_temp is None,
    )
    check(
        "an off-step disinfection temperature above the everyday set-point is written on the step at or "
        "below it, never above the tank's hard maximum",
        lambda: written(_dhw_snap(disinfecting=True, disinfection=60.3), "dhw") == 60.0
        and written(_dhw_snap(disinfecting=True, disinfection=60.3, attrs=_step(5)), "dhw") == 60.0
        and written(_dhw_snap(disinfecting=True, disinfection=62.0, attrs=_step(5)), "dhw") == 60.0
        and written(_dhw_snap(disinfecting=True, disinfection=60.7, attrs=_step(0.5)), "dhw") == 60.5
        and written(_dhw_snap(disinfecting=True, disinfection=60.0, attrs=_step(5)), "dhw") == 60.0,
    )
    check(
        "a cycle whose temperature is an off-step everyday set-point (the disinfection temperature at or "
        "below it) writes the step at or below it, as 49a45dd8 and the same install's everyday step do",
        lambda: all(written(_dhw_snap(**b, configured=60.4, disinfection=60.2), "dhw") == 60.0
                    for b in _BOOKINGS)
        and all(written(_dhw_snap(**b, configured=57.0, disinfection=50.0, attrs=_step(5)), "dhw") == 55.0
                for b in _BOOKINGS)
        and written(_dhw_snap(disinfecting=True, configured=57.0, disinfection=57.0, attrs=_step(5)), "dhw") == 55.0
        and written(_dhw_snap(cycle=False, disinfecting=True, configured=57.0, disinfection=50.0,
                              attrs=_step(5)), "dhw") == 55.0,
    )
    check(
        "an everyday set-point the nearest step rounds up is held below it on a cycle: the tank's hard "
        "maximum is the everyday set-point there (the everyday step's own nearest write is main's)",
        lambda: written(_dhw_snap(disinfecting=True, configured=58.0, disinfection=50.0, attrs=_step(5)), "dhw") == 55.0
        and written(_dhw_snap(configured=58.0, disinfection=50.0, attrs=_step(5)), "dhw") == 55.0,
    )
    check(
        "no no-cycle write exceeds the charge limit (dhw_max_temp), the cycle enabled and not running "
        "or disabled, over every step size and everyday set-point on and off the step",
        lambda: _nocycle_grid_over_limit("idle") == [] and _nocycle_grid_over_limit("disabled") == [],
    )
    check(
        "an off-step everyday set-point is written on the step at or below it, never rounded up "
        "(everyday 58, step 5: 55, not 60; everyday 60.7, step 1: 60), the cycle idle or disabled",
        lambda: all(written(_dhw_snap(configured=58.0, attrs=_step(5), **kw), d) == 55.0
                    and written(_dhw_snap(configured=60.7, attrs=_step(1), **kw), d) == 60.0
                    and written(_dhw_snap(configured=60.3, attrs=_step(0.5), **kw), d) == 60.0
                    for kw in _NOCYCLE_ARMS.values() for d in (None, "idle", "dhw", "both")),
    )
    check(
        "a charge limit below the entity's minimum writes the entity's minimum, never a value it refuses",
        lambda: written(_dhw_snap(configured=25.0, cycle=False), "dhw") == 30.0
        and written(_dhw_snap(configured=25.4, cycle=False, attrs={"min": 30.5, "max": 65, "step": 0.5}), "dhw") == 30.5
        and written(_dhw_snap(configured=25.0, cycle=False, attrs={"min": 30.4, "max": 65, "step": 1}), "dhw") == 31.0
        and written(_dhw_snap(configured=30.6, cycle=False, attrs={"min": 30.4, "max": 65, "step": 1}), "dhw") == 31.0
        and written(_dhw_snap(configured=72.0, cycle=False, attrs={"min": 70, "max": 80, "step": 1}), "dhw") == 70.0
        and written(_dhw_snap(configured=58.0, cycle=False, attrs={"max": 65, "step": 5}), "dhw") == 55.0,
    )
    check(
        "the hot-water repair's Fix never exceeds the tank's hard maximum it is judged against, over every "
        "step size and pair, and an off-step floor's repair stands down at the step below it",
        lambda: _repair_grid_over_hard_max() == []
        and _fix_value(_dhw_snap(disinfection=60.3, reading=60.0), arbiter=False) is None
        and _fix_value(_dhw_snap(disinfection=60.3, reading=59.0), arbiter=False) == 60.0
        and _fix_value(_dhw_snap(disinfection=60.3, reading=60.0 - setpoint_check.MIXING_VALVE_WRITE_EPSILON),
                       arbiter=False) is None
        and _fix_value(_dhw_snap(disinfection=72.0, reading=69.0, attrs=_step(1)), arbiter=False) == 70.0,
    )
    check(
        "a disinfection temperature above 70 degC is written at the tank's 70 degC hard maximum",
        lambda: written(_dhw_snap(disinfecting=True, disinfection=72.0,
                                  attrs={"min": 30, "max": 80, "step": 1}), "dhw") == 70.0,
    )
    check(
        "no cycle write exceeds the tank's hard maximum, over every step size and the disinfection "
        "temperature below, at and above the everyday set-point, on and off the step",
        lambda: _cycle_grid_over_hard_max() == [],
    )
    check(
        "a disinfection temperature above the entity's range stays bounded at its maximum",
        lambda: written(_dhw_snap(disinfecting=True, attrs={"min": 30, "max": 58, "step": 1}), "dhw") == 58.0,
    )
    check(
        "the space-only gate stays a gate on a booked step, but a held cycle turns it into Heating + DHW",
        lambda: written(_dhw_snap(action={"dhw_reason": "legionella"}), "space") == 30.0
        and written(_dhw_snap(), "space") == 30.0
        and written(_dhw_snap(disinfecting=True), "space") == 60.0,
    )
    check(
        "null control: a disabled cycle writes the everyday set-point on every row and booking",
        lambda: all(written(_dhw_snap(cycle=False, **b), d) == (30.0 if d == "space" and not b.get("disinfecting") else 55.0)
                    for d in _DUTIES for b in _BOOKINGS),
    )
    check(
        "a combi store at or under the potable limit runs no cycle: a booked or held step writes the "
        "everyday set-point, unless the cycle is forced (#3398's predicate, read through the cycle's owner)",
        lambda: not _combi_snap(False).params.legionella_cycle_active
        and _combi_snap(True).params.legionella_cycle_active
        and all(written(_combi_snap(False, **b), "dhw") == 55.0 and written(_combi_snap(True, **b), "dhw") == 60.0
                for b in _BOOKINGS[1:]),
    )
    check(
        "null control: an everyday set-point at or above the disinfection temperature is written as is",
        lambda: all(written(_dhw_snap(configured=c, **b), d) == (30.0 if d == "space" and not b.get("disinfecting") else c)
                    for c in (60.0, 62.0) for d in _DUTIES for b in _BOOKINGS),
    )
    check(
        "null control: no hot-water set-point entity is no hot-water write on any row",
        lambda: all(written(_dhw_snap(entity=None, **b), d) is None for d in _DUTIES for b in _BOOKINGS),
    )
    check(
        "the arbiter's own everyday write raises no disinfection-floor repair: it writes the cycle itself",
        lambda: _fix_value(_dhw_snap()) is None,
    )
    check(
        "a person's value beside the arbiter's write still raises the repair, its Fix on the floor",
        lambda: _fix_value(_dhw_snap(reading=50.0)) == 60.0,
    )
    check(
        "null control: with no arbiter write the pump's own set-point must still permit the cycle",
        lambda: _fix_value(_dhw_snap(entity=None)) is None
        and _fix_value(_dhw_snap(), arbiter=False) == 60.0
        and _fix_value(_dhw_snap(reading=60.0), arbiter=False) is None,
    )
    check(
        "null control: a disabled cycle and an everyday set-point at the disinfection temperature raise nothing",
        lambda: _fix_value(_dhw_snap(cycle=False)) is None
        and _fix_value(_dhw_snap(configured=60.0, reading=60.0)) is None,
    )


def _hyst_snap(hysteresis=None, *, action=None, space=None, disinfecting=False, reading=55.0):
    """``_dhw_snap`` (real parameters, a 0.1 step number) over a state with the pump's hysteresis."""
    snap = _dhw_snap(action=action, disinfecting=disinfecting, reading=reading,
                     attrs={"min": 30, "max": 75, "step": 0.1})
    return replace(snap, state=SimpleNamespace(
        room_temperature=21.0, outdoor_temperature=5.0, dhw_temperature=52.0,
        dhw_start_hysteresis_k=hysteresis, space_start_hysteresis_k=space,
    ))


def hysteresis_checks() -> None:
    """The pump's own start hysteresis: read, planned, written and logged."""
    import ast
    import pathlib

    import numpy as np

    from heatpump_optimizer import dhw_planner as planner
    from heatpump_optimizer import inputs as inputs_mod
    from heatpump_optimizer import thermal_model as tm

    # 1. The reading is a temperature difference.
    hass = FakeHass({
        "sensor.k2": FakeState("2", unit="K"), "sensor.f9": FakeState("9", unit="\u00b0F"),
        "sensor.c3": FakeState("3", unit="\u00b0C"), "sensor.nu": FakeState("4"),
        "sensor.k20": FakeState("20", unit="K"), "sensor.k0": FakeState("0", unit="K"),
        "sensor.big": FakeState("25"), "sensor.neg": FakeState("-1"),
        "sensor.na": FakeState("unavailable"), "sensor.pct": FakeState("2", unit="%"),
    })
    read = lambda e: inputs_mod.read_temperature_delta_k(hass, e)  # noqa: E731
    check("a hysteresis in K reads as it stands", lambda: read("sensor.k2") == 2.0)
    check("a hysteresis in degF is scaled by 5/9, not offset", lambda: abs(read("sensor.f9") - 5.0) < 1e-9)
    check("a hysteresis in degC reads as it stands", lambda: read("sensor.c3") == 3.0)
    check("a hysteresis with no unit is taken as K", lambda: read("sensor.nu") == 4.0)
    check("the bounds of the hysteresis range, 20 K and 0 K, are readings",
          lambda: read("sensor.k20") == 20.0 and read("sensor.k0") == 0.0
          and inputs_mod.TEMPERATURE_DELTA_MAX_K == 20.0)
    check("a hysteresis outside 0 to 20 K, unavailable, in a non-temperature unit, unset or unknown is no reading",
          lambda: read("sensor.big") is None and read("sensor.neg") is None
          and read("sensor.na") is None and read("sensor.pct") is None
          and read(None) is None and read("sensor.nowhere") is None)

    # 2. One lift.
    lift = tm.start_flow_min_lift_k
    half = {"flow_min_lift_k": 0.5}
    check("a heating hysteresis above the configured lift is the lift",
          lambda: lift(half, 2.0) == 2.0 and lift({}, 7.0) == 7.0)
    check("a heating hysteresis at or below the configured lift, or none, leaves the configured lift",
          lambda: lift(half, None) == 0.5 and lift(half, 0.3) == 0.5 and lift(half, 0.0) == 0.5
          and lift({}, None) == tm.FLOW_MIN_LIFT_K)
    check("null control: no hysteresis gives configured_flow_min_lift_k exactly",
          lambda: all(lift(c, None) == tm.configured_flow_min_lift_k(c)
                      for c in ({}, half, {"flow_min_lift_k": 0.0}, {"flow_min_lift_k": "x"}, None)))

    # 3. The start temperature.
    below = tm.dhw_start_below_c
    check("the start temperature is the target less the hysteresis",
          lambda: below(55, 4) == 51.0)
    check("no target, or a hysteresis that is missing, zero or negative, is no start temperature",
          lambda: below(55, None) is None and below(55, 0) is None and below(55, -1) is None
          and below(None, 4) is None)

    # 4. The step targets, on real parameters.
    cyc = ThermalParameters(dhw_setpoint=55.0, dhw_legionella_temp=60.0, dhw_legionella_enabled=True)
    nocyc = ThermalParameters(dhw_setpoint=55.0, dhw_legionella_temp=60.0, dhw_legionella_enabled=False)
    check("precondition: the cycle is 60 over a 55 set-point, and absent where disabled",
          lambda: cyc.dhw_cycle_temp == 60.0 and nocyc.dhw_cycle_temp is None)
    check("the step target is the everyday set-point, or the cycle's on a cycle step",
          lambda: tm.dhw_step_target_c(cyc, False) == 55.0 and tm.dhw_step_target_c(cyc, True) == 60.0)
    check("null control: with no cycle active a cycle step holds the everyday set-point",
          lambda: tm.dhw_step_target_c(nocyc, True) == 55.0)
    check("each step's start temperature is its own target less the hysteresis, the cycle step the cycle's",
          lambda: list(planner.dhw_start_temps(cyc, 4.0, 6, 3)) == [51, 51, 51, 56, 51, 51]
          and list(planner.dhw_start_temps(cyc, 4.0, 6, None)) == [51.0] * 6)
    check("with no or zero hysteresis no step has a start temperature",
          lambda: planner.dhw_start_temps(cyc, None, 6, 3) is None
          and planner.dhw_start_temps(cyc, 0.0, 6, 3) is None)

    # 5. One owner of the target: what the arbiter writes.
    check("the arbiter writes dhw_step_target_c: the everyday set-point with no cycle booked",
          lambda: arb._dhw_write(_hyst_snap(4.0)) == tm.dhw_step_target_c(cyc, False))
    check("the arbiter writes dhw_step_target_c: the cycle's temperature on a booked legionella step",
          lambda: arb._dhw_write(_hyst_snap(4.0, action={"dhw_reason": "legionella"}))
          == tm.dhw_step_target_c(cyc, True) == 60.0)

    # 6. Which steps the pump starts.
    startable = planner.startable_steps
    check("a step opens on a tank below its start temperature, or follows or is a charge",
          lambda: list(startable(np.array([0, 0, 1, 0, 0.]), np.array([54, 52, 50, 53, 50.9, 50.]),
                                 np.full(5, 51.0))) == [False, False, True, True, True])
    check("a tank exactly at the start temperature, not charging, does not start",
          lambda: list(startable(np.zeros(2), np.array([51.0, 51.0, 51.0]), np.full(2, 51.0)))
          == [False, False])

    check("with no start condition every step is startable",
          lambda: list(startable(np.zeros(3), np.array([60.0, 60.0, 60.0]), None)) == [True] * 3)

    # 7. Dropping the charges the pump would not start.
    def temps_of(plan):
        # 1 K lost per step, 3 K gained per charging step, from 54 degC.
        out = [54.0]
        for p in plan:
            out.append(out[-1] - 1.0 + (3.0 if p > 0 else 0.0))
        return np.array(out)

    plan = np.array([1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0])
    kept = plan.copy()
    drop = planner.drop_unstartable
    check("a charge begun above its start temperature is dropped whole; the first step and a cooled tank's run are kept",
          lambda: list(drop(plan, np.full(8, 51.0), temps_of)) == [1, 0, 0, 0, 0, 0, 0, 1])
    check("a tank exactly at the start temperature does not start",
          lambda: list(drop(np.array([0.0, 0.0, 1.0]), np.full(3, 52.0),
                            lambda p: np.array([54.0, 53.0, 52.0, 55.0]))) == [0, 0, 0])
    check("a run is judged against its own step's start temperature (a disinfection step's is higher)",
          lambda: list(drop(plan, np.where(np.arange(8) == 2, 56.0, 51.0), temps_of))
          == [1, 0, 1, 1, 0, 0, 0, 0])
    check("dropping unstartable charges does not mutate its input", lambda: np.array_equal(plan, kept))
    check("a run at the first step is kept on a warm tank, with nothing planned at the horizon's end",
          lambda: list(drop(np.array([1.0, 0.0, 0.0]), np.full(3, 51.0), temps_of)) == [1, 0, 0])

    # 8. The repair loop.
    def raises(_plan):
        raise AssertionError("temps_of must not be read")

    marker = np.array([0.0, 1.0])
    check("with no start temperature the repair's own answer stands and no trajectory is read",
          lambda: planner.place_startable(plan, None, raises, lambda plan: marker) is marker)
    calls, original = [], plan

    def stubborn(plan):
        calls.append(1)
        return original.copy()

    check("a repair that keeps re-placing the unstartable plan still leaves a plan with none, in bounded rounds",
          lambda: list(planner.place_startable(plan, np.full(8, 51.0), temps_of, stubborn))
          == list(drop(plan, np.full(8, 51.0), temps_of))
          and 1 <= len(calls) <= planner.STARTABLE_ROUNDS)
    check("an identity repair leaves the dropped plan",
          lambda: list(planner.place_startable(plan, np.full(8, 51.0), temps_of, lambda plan: plan))
          == list(drop(plan, np.full(8, 51.0), temps_of)))

    # 9. End to end, on the real optimizer.
    solved = {}

    def solve(hysteresis):
        if hysteresis not in solved:
            solved[hysteresis] = _solve_winter_mild(hysteresis)
        return solved[hysteresis]

    def late_runs(hysteresis):
        sched, temps = solve(hysteresis)
        on = sched > 0.0
        return sum(1 for i in range(1, on.size) if on[i] and not on[i - 1] and temps[i] >= 51.0)

    check("precondition: with no hysteresis the plan begins a charge on a tank at or above 51 degC",
          lambda: late_runs(None) > 0)
    check("with a 4 K hysteresis no planned charge after step 0 begins at or above 51 degC",
          lambda: late_runs(4.0) == 0)
    check("null control: a zero hysteresis plans exactly as none",
          lambda: np.array_equal(solve(0.0)[0], solve(None)[0]))

    def under_floor(hysteresis):
        # Degree-steps of the simulated tank under the 45 degC minimum.
        return float(np.clip(45.0 - solve(hysteresis)[1], 0.0, None).sum())

    check("what the start condition bars is re-bought where the pump starts: the tank is no further "
          "under its minimum with a 4 K hysteresis than with none",
          lambda: under_floor(4.0) <= under_floor(None) + 0.5)

    # 10. The ledger.
    def held_row(snap):
        held = arb.ArbiterState()
        arb._observe(held, snap, "dhw", NOW)
        return held.step

    check("the ledger's start temperature is the written set-point less the hysteresis",
          lambda: held_row(_hyst_snap(4.0))["start_below"] == 51.0)
    check("the ledger's start temperature on a booked cycle step is the cycle's less the hysteresis",
          lambda: held_row(_hyst_snap(4.0, action={"dhw_reason": "legionella"}))["start_below"] == 56.0)
    check("null control: with no hysteresis read the ledger has no start temperature",
          lambda: held_row(_hyst_snap(None))["start_below"] is None)
    row = {"start": NOW, "planned": "dhw", "tank": 52.0, "measured": True, "ran": False,
           "dhw_mode": False, "start_below": 51.0}

    def verdict(tank=52.0, **over):
        return arb._verdict({**row, "tank": tank, **over}, tank)["verdict"]

    check("an idle hot water step on a tank above the start temperature is not-startable",
          lambda: verdict() == "not-startable")
    check("an idle hot water step on a tank exactly at the start temperature is not-startable",
          lambda: verdict(51.0) == "not-startable")
    check("an idle hot water step on a tank below the start temperature is idle-instead",
          lambda: verdict(50.0) == "idle-instead")
    check("an idle hot water step with no start temperature, or a row without the key, is idle-instead",
          lambda: verdict(start_below=None) == "idle-instead"
          and arb._verdict({k: v for k, v in row.items() if k != "start_below"}, 52.0)["verdict"]
          == "idle-instead")
    check("a planned both step idle above the start temperature is idle-instead",
          lambda: verdict(planned="both") == "idle-instead")
    check("a hot water step that ran the space pump on a warm tank is space-instead",
          lambda: verdict(ran=True) == "space-instead")

    # 11. The heating write at the modulation floor.
    def floor_write(config, state):
        full = {"flow_heat_c": 48.0, "space_setpoint_entity": "number.flow",
                "heat_pump_return_temp_entity": "sensor.ret", **config}
        states = {"number.flow": FakeState("40", attributes={"min": 20, "max": 70, "step": 0.1}),
                  "sensor.ret": FakeState("27.0", unit="\u00b0C")}
        at = datetime(2026, 1, 10, 6, 0, tzinfo=UTC)
        return arb._flow_target(SimpleNamespace(
            config=full, hass=FakeHass(states), state=state, thermal=SimpleNamespace(params=None),
            params=SimpleNamespace(min_electrical_power=1.5, max_electrical_power=5.5),
            plan=SimpleNamespace(timestamps=[at], power_schedule=[1.5]), action=None,
        ), "space", at)

    def heat_state(**kw):
        return SimpleNamespace(outdoor_temperature=0.0, buffer_tank_temperature=40.0,
                               floor_return_temperature=None, **kw)

    lifted = {"flow_min_lift_k": 0.5}
    bare = floor_write(lifted, heat_state())
    check("precondition: the floor write is the return plus the configured lift",
          lambda: abs(bare - 27.5) < 1e-9)
    check("a heating hysteresis above the lift moves the floor write to return + hysteresis",
          lambda: abs(floor_write(lifted, heat_state(space_start_hysteresis_k=2.0)) - bare - 1.5) < 1e-9
          and abs(floor_write(lifted, heat_state(space_start_hysteresis_k=2.0)) - 29.0) < 1e-9)
    check("null control: a hysteresis below the lift, or none, writes what a state without the attribute writes",
          lambda: floor_write(lifted, heat_state(space_start_hysteresis_k=0.3)) == bare
          and floor_write(lifted, heat_state(space_start_hysteresis_k=None)) == bare)

    # 12. The lift has one owner.
    root = pathlib.Path("custom_components/heatpump_optimizer")
    stray, bad_calls, sites = [], [], 0
    for path in sorted(root.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = {getattr(node, "id", None), getattr(node, "attr", None)}
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names |= {a.name.split(".")[-1] for a in node.names}
            if "configured_flow_min_lift_k" in names and path.name != "thermal_model.py":
                stray.append(path.name)
            if path.name == "thermal_model.py" or not isinstance(node, ast.Call):
                continue
            fn = node.func
            if (getattr(fn, "id", None) or getattr(fn, "attr", None)) != "modulation_floor_flow_c":
                continue
            sites += 1
            third = node.args[2] if len(node.args) > 2 else next(
                (k.value for k in node.keywords if k.arg == "lift_k"), None)
            callee = None if not isinstance(third, ast.Call) else (
                getattr(third.func, "id", None) or getattr(third.func, "attr", None))
            if callee != "start_flow_min_lift_k":
                bad_calls.append((path.name, node.lineno))
    check("precondition: the census finds a call of modulation_floor_flow_c outside thermal_model",
          lambda: sites >= 1)
    check("configured_flow_min_lift_k is referenced by no module but its owner",
          lambda: not stray)
    check("every floor call outside thermal_model takes its lift from start_flow_min_lift_k",
          lambda: not bad_calls)

    # 13. The hot water minimum above the start temperature.
    def raised(floor, entity="sensor.h"):
        hass = FakeHass({"sensor.h": FakeState("4", unit="K")})
        params = ThermalParameters(dhw_setpoint=55.0, dhw_legionella_enabled=False, dhw_min_temp=floor)
        config = {"dhw_hysteresis_entity": entity} if entity else {}
        setpoint_check._dhw_start(hass, config, params)
        return [i for i in getattr(hass, "issues", []) if i[1] == setpoint_check.ISSUE_DHW_START]

    check("a minimum above the start temperature raises dhw_minimum_above_start with its figures",
          lambda: setpoint_check.ISSUE_DHW_START == "dhw_minimum_above_start"
          and len(raised(52.0)) == 1
          and raised(52.0)[0][2]["translation_placeholders"]
          == {"floor": "52.0", "start": "51.0", "target": "55.0", "hysteresis": "4.0"})
    check("a minimum below the start temperature raises nothing", lambda: raised(45.0) == [])
    check("a minimum exactly at the start temperature raises nothing", lambda: raised(51.0) == [])
    check("with no hysteresis entity configured a minimum of 52 raises nothing",
          lambda: raised(52.0, entity=None) == [])

    # 14. The coordinator reads both into the state.
    def read_state(config):
        from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
        h = FakeHass({"sensor.dh": FakeState("4", unit="K"), "sensor.sh": FakeState("2", unit="K"),
                      "sensor.indoor": FakeState("21.4"), "sensor.outdoor": FakeState("-3.0")})
        coord = HeatPumpOptimizerCoordinator(h, FakeEntry(data={
            "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor", **config}))
        asyncio.run(coord._update_current_state())
        return coord._current_state

    both = read_state({"dhw_hysteresis_entity": "sensor.dh", "space_hysteresis_entity": "sensor.sh"})
    none = read_state({})
    check("the coordinator's input read puts both hysteresis sensors into the state",
          lambda: both.dhw_start_hysteresis_k == 4.0 and both.space_start_hysteresis_k == 2.0)
    check("null control: with neither entity configured both state fields are None",
          lambda: none.dhw_start_hysteresis_k is None and none.space_start_hysteresis_k is None)


def _solve_winter_mild(hysteresis):
    """The 24 h solve of ``dev/audit/harnesses/r10_dhw_start_hysteresis.py`` (winter_typical, winter_mild, 53 degC)."""
    import numpy as np
    from profiles import house, prices, solve_inputs, weather
    from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
    from heatpump_optimizer.thermal_model import ThermalModel, ThermalState

    begin = datetime(2026, 1, 15, 0, 0)
    cfg = house()
    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = True
    opt = HeatPumpOptimizer(ThermalModel(params), OptimizationConfig(
        horizon_hours=24, time_step_minutes=15, target_temp=cfg["target_temperature"],
        min_temp=cfg["min_temperature"], max_temp=cfg["max_temperature"]))
    outdoor, wind, rain, sun = weather("winter_mild", begin)
    state = ThermalState(
        room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=float(outdoor[0]),
        dhw_temperature=53.0, dhw_hours_since_legionella=20.0, upper_floor_temperature=21.0,
        lower_floor_temperature=21.0, buffer_tank_temperature=40.0)
    state.dhw_start_hysteresis_k = hysteresis
    result = opt.optimize(inputs=solve_inputs(
        initial_state=state, prices=np.asarray(prices("winter_typical", begin), dtype=float),
        outdoor_temps=outdoor, wind_speeds=wind, precipitation=rain, solar_radiation=sun,
        start_time=begin))
    return (np.asarray(result.dhw_power_schedule, dtype=float),
            np.asarray(result.dhw_temp_trajectory, dtype=float))


if __name__ == "__main__":
    raise SystemExit(main())
