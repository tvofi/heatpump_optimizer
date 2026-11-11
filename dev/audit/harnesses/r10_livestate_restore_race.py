"""R10-LIVESTATE (#2248): the startup session restore against a user write landing
inside its store-load await. A port of two finder harnesses that drove the restore's
old signature: dev/audit/rounds/round10/catchup/leads/l3_restore_race.py (lead L3)
and dev/audit/rounds/round10/D14/sweep-N-shared-config/probe_away_restore.py.

The restore is spawned the way the coordinator spawns it: through
boost.spawn_restore_session where the tree has it (the gate), else as a task of
boost.restore_session(coord, coord._away_state, ...) (the merge base). Both store
loads are held on an asyncio.Event; the writer runs as a task inside them, the gate
opens, and both finish. Persists are stubbed out.

Metrics:
  l3_differ_total -- scenarios, of 3, whose final state differs from the serial order
    (restore, then writer): A the user turns away off (async_set_away), B the user
    cancels a stored space boost (boost.set_channel), C a cycle replaces the live
    AwayState (as _resolve_away publishes one).
  l3_null_differ_total -- serial against serial, 0.
  probe_lost_midload -- stored override off; async_set_away(active=True) inside the
    load: 1 when the user's True is gone after both finish.
  probe_lost_null -- the same write after the restore, 0.
Expected at merge base fd7e289d0: l3 3 of 3, null 0; probe 1, null 0.
Expected at the R10-LIVESTATE head: l3 0 of 3, null 0; probe 0, null 0.

    PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/r10_livestate_restore_race.py
"""
import asyncio
from datetime import timedelta
from types import SimpleNamespace

from homeassistant.util import dt as dt_util

from heatpump_optimizer import away as away_mode
from heatpump_optimizer import boost
from heatpump_optimizer import coordinator as cmod

C = cmod.HeatPumpOptimizerCoordinator
GATED = hasattr(boost, "spawn_restore_session")


class Coord:
    """Weak-referenceable stub carrying what the real methods touch."""

    def __init__(self):
        self.hass = SimpleNamespace()
        self.entry = SimpleNamespace(entry_id="e1", options={})
        self._away_state = away_mode.AwayState()

    async def async_request_refresh(self):
        return None


def install(gate, stored):
    async def load_mapping(store, what):
        await gate.wait()
        return dict(stored["away" if "away" in what else "boost"])

    async def nop(*a, **k):
        return None

    away_mode.load_mapping = load_mapping
    boost.load_mapping = load_mapping
    away_mode.persist_override = nop
    boost.persist = nop
    boost._store = lambda coord: None
    away_mode._away_store = lambda coord: None


def spawn(coord):
    read = lambda e: (None, {})  # noqa: E731
    if GATED:
        held = []
        boost.spawn_restore_session(
            coord, lambda c: held.append(asyncio.ensure_future(c)) or held[0],
            lambda payload: C._adopt_away_override(coord, payload), {}, read)
        return held[0]
    return asyncio.ensure_future(boost.restore_session(coord, coord._away_state, {}, read))


async def run(stored, writer, observe, interleaved):
    gate = asyncio.Event()
    install(gate, stored)
    coord = Coord()
    restore = spawn(coord)
    if interleaved:
        task = asyncio.ensure_future(writer(coord))
        for _ in range(3):
            await asyncio.sleep(0)
        gate.set()
        await restore
        await asyncio.wait_for(task, 2.0)
    else:
        gate.set()
        await restore
        await writer(coord)
    return observe(coord)


async def l3_writer(coord, scenario):
    if scenario == "A":
        await C.async_set_away(coord, active=False, refresh=False)
    elif scenario == "B":
        await boost.set_channel(coord, boost.CHANNEL_SPACE, False, refresh=False)
    else:
        old = coord._away_state
        coord._away_state = away_mode.AwayState(
            override_active=old.override_active, override_return_iso=old.override_return_iso)


def l3_observe(scenario):
    if scenario == "B":
        return lambda coord: boost.held_for(coord).active(boost.CHANNEL_SPACE, dt_util.now())
    return lambda coord: coord._away_state.override_active


async def main():
    now = dt_util.now()
    l3 = {"away": {"active": True, "return_time": None, "migrated_helpers": True},
          "boost": {"space": {"until": (now + timedelta(hours=1)).isoformat()}}}
    differ = null = 0
    for s in "ABC":
        w = lambda c, s=s: l3_writer(c, s)  # noqa: E731
        serial = await run(l3, w, l3_observe(s), False)
        inter = await run(l3, w, l3_observe(s), True)
        again = await run(l3, w, l3_observe(s), False)
        print(f"RESULT scenario={s} serial={serial} interleaved={inter}")
        differ += int(serial != inter)
        null += int(serial != again)
    print(f"RESULT gated={int(GATED)}")
    print(f"RESULT l3_differ_total={differ} of 3")
    print(f"RESULT l3_null_differ_total={null} of 3")
    probe = {"away": {"active": False, "return_time": None, "migrated_helpers": True}, "boost": {}}
    on = lambda c: C.async_set_away(c, active=True, refresh=False)  # noqa: E731
    lost = lambda c: int(c._away_state.override_active is not True)  # noqa: E731
    print(f"RESULT probe_lost_midload={await run(probe, on, lost, True)} count")
    print(f"RESULT probe_lost_null={await run(probe, on, lost, False)} count")


asyncio.run(main())
