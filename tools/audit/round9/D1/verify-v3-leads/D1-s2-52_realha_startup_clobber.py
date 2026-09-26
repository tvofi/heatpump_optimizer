"""V3 verify of D1-s2-52: reproduce the startup-clobber race on a REAL HeatPumpOptimizerCoordinator
over genuine Home Assistant 2026.2.3 (no tests/hastub), using the REAL QuarantiningStore/Store
(real orjson round trip through a real disk file) and REAL asyncio eager-start tasks
(hass.async_create_task on the real HomeAssistant instance), not a stand-in.

Metric: of 5 stores (energy_totals, ledger, thermal_learning, price_model, accuracy), count
whose persisted learned marker is lost after a restart in which the store's writer runs while
the startup load (spawned via the coordinator's real hass.async_create_task, eager-started, in
__init__) is still in flight -- the real Store's read is a real
hass.async_add_executor_job(json_util.load_json, path) call, so the added latency below models
a genuine executor-thread suspension, not a stub artefact.

Command (no tests/hastub on the path):
    PYTHONPATH=custom_components:tests /root/venvha/bin/python \
        tools/audit/round9/D1/verify-v3-leads/D1-s2-52_realha_startup_clobber.py [--after-read] [--wait]
Expected: lost=5 of 5 (exact), matching the stub's startup_clobber.py; --after-read -> 0;
--wait (async_save awaits async_wait_for_read first) -> 0. mode_arm_lost=0 of 1 (the one
writer, async_set_mode, that already waits).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Home Assistant 2026.2.3 (venvha).
"""
import sys
sys.path.insert(0, "tools/audit/round9/D1/verify-v3-leads")
import _realha_rig as rig  # noqa: E402 (thread pin + shim inside, before numpy)
import asyncio  # noqa: E402
import tempfile  # noqa: E402
import homeassistant.core as core  # noqa: E402
from homeassistant.helpers import storage  # noqa: E402
from heatpump_optimizer.store import QuarantiningStore  # noqa: E402
from harness import FakeEntry  # noqa: E402

AFTER = "--after-read" in sys.argv
WAIT = "--wait" in sys.argv
LATENCY = 0.2

_orig_load = storage.Store.async_load
_orig_save = QuarantiningStore.async_save


async def slow_load(self):
    await asyncio.sleep(LATENCY)
    return await _orig_load(self)


async def waiting_save(self, data):
    await self.async_wait_for_read()
    return await _orig_save(self, data)


class EagerHass(core.HomeAssistant):
    """Real HomeAssistant, with async_create_task started eagerly, exactly as
    the genuine hass.async_create_task does (eager_start=True since HA 2024.3)."""

    def async_create_task(self, coro, name=None, eager_start=True):
        return asyncio.ensure_future(coro) if not eager_start else asyncio.Task(
            coro, loop=asyncio.get_running_loop(), eager_start=True
        )


def markers(c):
    return {
        "energy": c._energy_totals["total_energy_kwh"],
        "ledger": c._operation_score,
        "thermal": c._house_heat_loss_scale,
        "price": sorted(c._price_days_seen),
        "accuracy": c._comfort_learner.learned_weight,
    }


WRITERS = {
    "energy": "_async_save_energy_totals",
    "ledger": "_async_save_ledger",
    "thermal": "_async_save_thermal_learning",
    "price": "_async_save_price_model",
    "accuracy": "_async_save_accuracy",
}


async def session(seed, writers, mode_arm=False):
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
    d = tempfile.mkdtemp()
    hass = EagerHass(d)
    hass.states = core.StateMachine(hass.bus, hass.loop)
    ts = rig.NOW.timestamp()
    hass.states.async_set("sensor.indoor", "21.0", timestamp=ts)
    hass.states.async_set("sensor.outdoor", "-3.0", timestamp=ts)
    entry = FakeEntry(data=rig.base_config())
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    if seed:
        await asyncio.sleep(LATENCY * 3)  # first session: let its (empty) loads land
        for k in coord._energy_totals:
            coord._energy_totals[k] = 1234.5
        coord._operation_score = 77.0
        coord._apply_house_heat_loss_scale(1.3)
        coord._price_days_seen = {"2026-01-10", "2026-01-11"}
        coord._comfort_learner.learned_weight = 7.5
        for name in WRITERS.values():
            await getattr(coord, name)()
        return markers(coord), d
    if AFTER:
        await asyncio.sleep(LATENCY * 3)
    if mode_arm:
        await coord.async_set_mode("boost")
    else:
        for name in writers:
            await getattr(coord, WRITERS[name])()
    await asyncio.sleep(LATENCY * 3)
    return markers(coord), d


async def main():
    stops = rig.freeze_now()
    try:
        storage.Store.async_load = slow_load
        if WAIT:
            QuarantiningStore.async_save = waiting_save
        seeded, storage_dir = await session(seed=True, writers=())
        # Point every coordinator at the same on-disk .storage the seed wrote to,
        # by monkeypatching hass.config.path via a fixed config dir instead of a
        # fresh tempdir per session -- simplest: reuse the directory HomeAssistant
        # picked for the seed run.
        import homeassistant.core as core_mod

        class FixedDirHass(core_mod.HomeAssistant):
            def __new__(cls):
                return super().__new__(cls, storage_dir)

            def __init__(self):
                super().__init__(storage_dir)

        async def restart_writer(name):
            from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
            hass = FixedDirHass()
            hass.async_create_task = EagerHass.async_create_task.__get__(hass, FixedDirHass)
            hass.states = core_mod.StateMachine(hass.bus, hass.loop)
            ts = rig.NOW.timestamp()
            hass.states.async_set("sensor.indoor", "21.0", timestamp=ts)
            hass.states.async_set("sensor.outdoor", "-3.0", timestamp=ts)
            from harness import FakeEntry as FE
            entry = FE(data=rig.base_config())
            coord = HeatPumpOptimizerCoordinator(hass, entry)
            if AFTER:
                await asyncio.sleep(LATENCY * 3)
            await getattr(coord, WRITERS[name])()
            await asyncio.sleep(LATENCY * 3)
            return markers(coord)

        lost = 0
        detail = []
        for name in WRITERS:
            m = await restart_writer(name)
            ok = {
                "energy": m["energy"] == 1234.5,
                "ledger": m["ledger"] == 77.0,
                "thermal": m["thermal"] == 1.3,
                "price": m["price"] == sorted(seeded["price"]),
                "accuracy": m["accuracy"] == 7.5,
            }[name]
            lost += not ok
            detail.append(f"{name}:{seeded[name]}->{m[name]}")

        async def restart_mode():
            from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
            hass = FixedDirHass()
            hass.async_create_task = EagerHass.async_create_task.__get__(hass, FixedDirHass)
            hass.states = core_mod.StateMachine(hass.bus, hass.loop)
            ts = rig.NOW.timestamp()
            hass.states.async_set("sensor.indoor", "21.0", timestamp=ts)
            hass.states.async_set("sensor.outdoor", "-3.0", timestamp=ts)
            from harness import FakeEntry as FE
            entry = FE(data=rig.base_config())
            coord = HeatPumpOptimizerCoordinator(hass, entry)
            if AFTER:
                await asyncio.sleep(LATENCY * 3)
            await coord.async_set_mode("boost")
            await asyncio.sleep(LATENCY * 3)
            return coord._mode

        mode_after = await restart_mode()
        mode_lost = int(mode_after != "boost")

        print(f"RESULT real_lost={lost} stores_of_5")
        print(f"RESULT real_detail={'; '.join(detail)}")
        print(f"RESULT real_mode_arm_lost={mode_lost} of_1")
    finally:
        storage.Store.async_load = _orig_load
        QuarantiningStore.async_save = _orig_save
        for p in stops:
            p.stop()


asyncio.run(main())
rig.tail()
