"""Lead L3 (catch-up verifier, group `leads`): boost.restore_session races writers of
the same state across its store-load await.

restore_session (spawned from the coordinator constructor, coordinator.py ~2647) awaits
away_mode.restore_override then boost.restore; each awaits load_mapping(store) and then
assigns the STORED values unconditionally (away.apply_override_payload; boost.restore's
held.until[channel] = parsed), and the away half writes into the AwayState object bound
at spawn time.

Real asyncio loop; the two load_mapping calls are gated on an asyncio.Event so a writer
runs inside the load await. Metric: scenarios whose final state differs from the serial
order (restore completes, then the writer runs). Three scenarios:
  A. away: stored override active; the user turns away off (coordinator.async_set_away,
     the real method on a stub self) during the load.
  B. boost: stored space boost until now+1h; the user cancels it (boost.set_channel)
     during the load.
  C. object identity: a cycle's _resolve_away replaces coord._away_state during the load
     (simulated: a fresh AwayState copied from the old fields, as _resolve_away builds it).
Null: the same three run serially -> 0 differ.
Perturbation (in memory, two halves of one fix): A/B -- the writer awaits the restore
task first ("writers wait for the restore"); C -- apply_override_payload is redirected
to coord._away_state at apply time instead of the spawn-time object -> 0 differ.
Command (tree root): PYTHONPATH=tests/hastub:custom_components python dev/audit/rounds/round10/catchup/leads/l3_restore_race.py
Baseline: origin/main d749c986d. Machine: tvofi mac, 8 cores. Not a timing number: the
interleaving is forced by the gate, so load1/thread_factor do not bear on it; reach in
real HA depends on the startup store-load window, which this harness does not measure.
"""
import asyncio
from datetime import timedelta
from types import SimpleNamespace

from homeassistant.util import dt as dt_util

from heatpump_optimizer import away as away_mode
from heatpump_optimizer import boost
from heatpump_optimizer import coordinator as cmod

NOW = dt_util.now()
STORED = {
    "away": {"active": True, "return_time": None, "migrated_helpers": True},
    "boost": {"space": {"until": (NOW + timedelta(hours=1)).isoformat()}},
}


class Coord:
    """Weak-referenceable stub carrying what the real methods touch."""

    def __init__(self):
        self.hass = SimpleNamespace()
        self.entry = SimpleNamespace(entry_id="e1", options={})
        self._away_state = away_mode.AwayState()

    async def async_request_refresh(self):
        return None


def install_gate(gate):
    async def load_mapping(store, what):
        await gate.wait()
        return dict(STORED["away" if "away" in what else "boost"])

    async def nop(*a, **k):
        return None

    away_mode.load_mapping = load_mapping
    boost.load_mapping = load_mapping
    away_mode.persist_override = nop
    boost.persist = nop
    boost._store = lambda coord: None
    away_mode._away_store = lambda coord: None


async def writer(coord, scenario):
    if scenario == "A":
        await cmod.HeatPumpOptimizerCoordinator.async_set_away(coord, active=False, refresh=False)
    elif scenario == "B":
        await boost.set_channel(coord, boost.CHANNEL_SPACE, False, refresh=False)
    else:
        old = coord._away_state
        coord._away_state = away_mode.AwayState(
            override_active=old.override_active,
            override_return_iso=old.override_return_iso,
        )


def observe(coord, scenario):
    if scenario == "B":
        return boost.held_for(coord).active(boost.CHANNEL_SPACE, dt_util.now())
    return coord._away_state.override_active


async def one(scenario, mode, fixed):
    gate = asyncio.Event()
    install_gate(gate)
    coord = Coord()
    state_arg = coord._away_state
    restore_apply = away_mode.apply_override_payload
    if fixed:
        # Fix half 2: apply the stored payload to the coordinator's live AwayState,
        # not the object bound at spawn time.
        away_mode.apply_override_payload = lambda st, payload: restore_apply(coord._away_state, payload)
    task = asyncio.create_task(boost.restore_session(coord, state_arg, {}, lambda e: (None, {})))
    if mode == "serial":
        gate.set()
        await task
        await writer(coord, scenario)
    else:
        await asyncio.sleep(0)  # restore is now parked on the load
        if fixed and scenario != "C":
            gate.set()
            await task  # fix half 1: the writer awaits the restore first
            await writer(coord, scenario)
        else:
            await writer(coord, scenario)
            gate.set()
            await task
    away_mode.apply_override_payload = restore_apply
    return observe(coord, scenario)


async def main():
    for fixed in (False, True):
        label = "perturbed" if fixed else "main"
        differ = 0
        for scenario in ("A", "B", "C"):
            serial = await one(scenario, "serial", fixed)
            inter = await one(scenario, "interleaved", fixed)
            d = int(serial != inter)
            differ += d
            print(f"RESULT {label} scenario={scenario} serial={serial} interleaved={inter} differs={d}")
        print(f"RESULT {label} differ_total={differ} of 3")
    # Null: serial against serial.
    nd = 0
    for s in "ABC":
        nd += int(await one(s, "serial", False) != await one(s, "serial", False))
    print(f"RESULT null serial_vs_serial differ_total={nd} of 3")


asyncio.run(main())
