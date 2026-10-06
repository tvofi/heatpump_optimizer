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
from types import SimpleNamespace

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState, Results  # noqa: E402
from heatpump_optimizer import boost as boost_mod  # noqa: E402
from heatpump_optimizer import entity as entity_mod  # noqa: E402
from heatpump_optimizer import pump_arbiter as arb  # noqa: E402
from heatpump_optimizer import switch as switch_mod  # noqa: E402
from heatpump_optimizer.const import (  # noqa: E402
    ECONOMY_ABSOLUTE_FLOOR,
    MODE_AUTO,
    SPACE_PUMP_FLOOR_MARGIN_C,
)
from heatpump_optimizer.dhw_schedule import parse_windows  # noqa: E402

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
    check(
        "a cycle inside the horizon releases DHW",
        lambda: boost_mod.block_release_reason(due, "dhw", NOW) == boost_mod.RELEASE_LEGIONELLA,
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

    return R.close("BLOCK DUTY CHECKS")


if __name__ == "__main__":
    raise SystemExit(main())
