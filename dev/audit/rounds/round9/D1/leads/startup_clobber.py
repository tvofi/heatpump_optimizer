"""D1-s2-52: a store writer that runs before its store's startup read lands replaces the persisted state.

Metric: of 5 stores (energy_totals, ledger, thermal_learning, price_model, accuracy), count those
whose persisted learned marker is lost after a restart in which the store's writer runs while the
startup load (spawned fire-and-forget in the coordinator __init__) is still in flight. Count key:
the value the restarted coordinator holds after every load has landed (the production loader's
own result), per marker: energy total_energy_kwh, ledger operation_score, thermal-learning
house_heat_loss_scale, price-model days_seen, accuracy comfort learned_weight.
Rig: a real asyncio loop; hass.async_create_task is loop.create_task; the stub Store's async_load
first awaits a latency (Home Assistant reads the file in an executor job; a load that finds a
save pending returns the pending data -- both give the loader the fresh defaults).
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/leads/startup_clobber.py [--after-read] [--wait]
Expected: lost=5 of 5 (exact); --after-read (null control: writers run after the loads land) -> 0;
  --wait (perturbation: every save first awaits QuarantiningStore.async_wait_for_read) -> 0.
Control seam: async_set_mode, the one writer that already waits, loses nothing (mode_arm_lost=0).
Tasks start eagerly, as hass.async_create_task does; a lazy task factory makes even the waiting
writer lose (async_wait_for_read finds no read in flight), which is a rig artefact.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, machine B10 cloud container, CPython 3.14.0rc2.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _rig  # noqa: E402
import asyncio
from harness import FakeHass, FakeEntry
from homeassistant.helpers import storage
from heatpump_optimizer.store import QuarantiningStore

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


class LoopHass(FakeHass):
    # Home Assistant's hass.async_create_task starts the task eagerly (eager_start=True):
    # it runs to its first suspension -- here the load's executor read -- before returning.
    def async_create_task(self, coro):
        return asyncio.Task(coro, loop=asyncio.get_running_loop(), eager_start=True)


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
    hass = LoopHass()
    hass.states.set("sensor.indoor", _rig.FakeState("21.0"))
    hass.states.set("sensor.outdoor", _rig.FakeState("-3.0"))
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=_rig.base_config()))
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
        return markers(coord)
    if AFTER:
        await asyncio.sleep(LATENCY * 3)
    if mode_arm:
        await coord.async_set_mode("auto", refresh=False)
    else:
        for key in writers:
            await getattr(coord, WRITERS[key])()
    await asyncio.sleep(LATENCY * 3)  # every load lands
    return markers(coord)


def run():
    storage.Store.async_load = slow_load
    if WAIT:
        QuarantiningStore.async_save = waiting_save
    try:
        _rig.freeze()
        storage._reset_store_disk()
        want = asyncio.run(session(True, []))
        got = asyncio.run(session(False, list(WRITERS)))
        lost = [k for k in WRITERS if got[k] != want[k]]
        storage._reset_store_disk()
        asyncio.run(session(True, []))
        got_mode = asyncio.run(session(False, [], mode_arm=True))
        mode_lost = int(got_mode["accuracy"] != want["accuracy"])
    finally:
        storage.Store.async_load = _orig_load
        QuarantiningStore.async_save = _orig_save
    print(f"RESULT lost={len(lost)} stores_of_5")
    print("RESULT lost_stores=" + (",".join(lost) or "none"))
    print(f"RESULT mode_arm_lost={mode_lost} of_1")
    print("RESULT detail=" + "; ".join(f"{k}:{want[k]}->{got[k]}" for k in WRITERS))


run()
_rig.tail()
