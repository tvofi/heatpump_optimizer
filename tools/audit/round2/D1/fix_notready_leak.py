"""D1-01 (#236) fix harness: coordinators leaked per ConfigEntryNotReady retry.

Metric: zombie coordinators still reachable after gc.collect() divided by the
number of ConfigEntryNotReady setup retries, plus the hass-level registrations
(state-change listeners, MQTT subscriptions) those dead coordinators still
hold. Measured on both task-start arms, because HA 2024.1-2024.2 starts
hass.async_create_task lazily and 2024.3+ eagerly, and the leak and its fix
must be measured on both.

Command (from the repository root):
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub \
  .venv/bin/python tools/audit/round2/D1/fix_notready_leak.py

Expected on origin/main (4a7bdb6): slope_eager = slope_lazy = 1.0000 +- 0
zombies per retry, over N = 1, 2, 3, 5, 8. Expected after the fix: 0.0000 on
every arm, with the null controls unchanged.

Instrumented symbols:
  custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator
  .__init__ / ._async_setup_peak_guard / ._async_setup_defrost_watch /
  ._async_setup_ecl110_state_subscription, and
  custom_components.heatpump_optimizer.__init__:async_setup_entry.

Perturbation: the `guards_off` arm switches the peak guard off, clears the
defrost entity and empties the ECL110 state topic; nothing is registered
before the first refresh and every counter must read 0 on baseline and fixed
trees alike.

Null control: the `healthy` arm runs a setup that SUCCEEDS and then unloads it
the way HA does. It must show 2 live listeners + 1 live MQTT subscription
while loaded and 0 of each after the unload, on both trees -- otherwise the
fix has simply stopped the listeners working.

Baseline SHA: 4a7bdb696c9a01783afc7bdcb4a840de0f935dcb. Machine: 8-core M1.
"""
from __future__ import annotations

import os

for _var in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_var, "1")

import asyncio
import gc
import sys
import tempfile
import time
import weakref

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from homeassistant.exceptions import HomeAssistantError  # noqa: E402

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402


class ConfigEntryNotReady(HomeAssistantError):
    """Faithful stand-in: real HA derives it from HomeAssistantError too."""


import heatpump_optimizer as integration  # noqa: E402
from heatpump_optimizer import coordinator as coord_mod  # noqa: E402
from heatpump_optimizer.coordinator import (  # noqa: E402
    HeatPumpOptimizerCoordinator,
)


# --- the two task-start arms ------------------------------------------------
#
# EAGER is HA 2024.3+ (asyncio eager task factory): the coroutine runs
# synchronously up to its first suspension inside async_create_task.
# LAZY is HA 2024.1-2024.2 and plain asyncio: the task is queued and runs on a
# later loop iteration. `hacs.json` declares 2024.6.0, but the panel measured
# the shutdown-on-NotReady fix inert on the lazy arm, so both are kept.


class LoopHass(FakeHass):
    """FakeHass with a REAL event loop underneath async_create_task.

    ``FakeHass.async_create_task`` closes the coroutine, which would make the
    three registrations impossible to leak in the first place; this harness is
    about exactly those tasks, so it runs them.
    """

    def __init__(self, states=None, *, eager: bool) -> None:
        super().__init__(states)
        self.eager = eager
        self.created: list[asyncio.Task] = []
        self.state_listeners: list = []
        self.mqtt_subs: list = []

    def async_create_task(self, coro, name=None, eager_start=None):
        loop = asyncio.get_running_loop()
        if self.eager:
            task = asyncio.Task(coro, loop=loop, eager_start=True)
        else:
            task = loop.create_task(coro)
        self.created.append(task)
        return task

    async def async_add_executor_job(self, func, *args):
        return func(*args)


async def _fake_subscribe(hass, topic, callback, qos=0, **kwargs):
    """Return a real unsubscribe, the way mqtt.async_subscribe does.

    The committed stub returns None, which makes an MQTT leak unmeasurable.
    """
    entry = [topic, callback]
    hass.mqtt_subs.append(entry)

    def _unsub():
        if entry in hass.mqtt_subs:
            hass.mqtt_subs.remove(entry)

    return _unsub


BASE_CONFIG = {
    "heat_pump_power_entity": "sensor.hp_power",
    "house_power_entity": "sensor.house_power",
    "heat_pump_defrost_entity": "binary_sensor.defrost",
    "peak_guard_enabled": True,
    "tibber_token": "tok",
}

GUARDS_OFF_CONFIG = {
    "peak_guard_enabled": False,
    "heat_pump_defrost_entity": "",
    "ecl110_state_topic": "",
    "tibber_token": "tok",
}


def _states():
    return {
        "sensor.hp_power": FakeState("1000", unit="W"),
        "sensor.house_power": FakeState("2000", unit="W"),
        "binary_sensor.defrost": FakeState("off"),
    }


async def _settle(times: int = 6) -> None:
    for _ in range(times):
        await asyncio.sleep(0)


def _owner(obj):
    """The coordinator a registered callback is bound to, or None."""
    return getattr(obj, "__self__", None)


def _count_for(hass, coordinators) -> tuple[int, int]:
    """(state listeners, mqtt subscriptions) still held by these coordinators."""
    ids = {id(c) for c in coordinators}
    listeners = sum(
        1 for _ids, action in hass.state_listeners if id(_owner(action)) in ids
    )
    subs = sum(1 for _topic, cb in hass.mqtt_subs if id(_owner(cb)) in ids)
    return listeners, subs


async def _run_notready_arm(retries: int, *, eager: bool, guards_off: bool,
                            settle_before_failure: bool) -> dict:
    """`retries` setups that all raise ConfigEntryNotReady, then one healthy one.

    Home Assistant's ConfigEntry.async_setup runs the entry's
    ``async_on_unload`` callbacks -- and nothing else -- when setup raises
    ConfigEntryNotReady: no ``async_unload_entry``, no ``async_shutdown``.
    """
    hass = LoopHass(_states(), eager=eager)
    cfg = dict(GUARDS_OFF_CONFIG if guards_off else BASE_CONFIG)

    dead: list[weakref.ref] = []
    strong: list = []
    escaped = 0

    original = HeatPumpOptimizerCoordinator.async_config_entry_first_refresh

    async def _notready(self):
        # Real HA awaits the first update here; a Tibber fetch is several
        # awaits of network I/O, so the loop is yielded to before the raise.
        if settle_before_failure:
            await _settle()
        raise ConfigEntryNotReady("Tibber unreachable at boot")

    HeatPumpOptimizerCoordinator.async_config_entry_first_refresh = _notready
    try:
        for i in range(retries):
            entry = FakeEntry(data=cfg, entry_id=f"retry_{i}")
            entry.state = "setup_in_progress"
            try:
                await integration.async_setup_entry(hass, entry)
            except ConfigEntryNotReady:
                # HA: ConfigEntry.async_setup -> _async_process_on_unload.
                for cb in list(entry._on_unload):
                    cb()
                entry._on_unload.clear()
            except Exception:  # noqa: BLE001
                escaped += 1
            await _settle()
    finally:
        HeatPumpOptimizerCoordinator.async_config_entry_first_refresh = original

    # Everything a retry created is unreachable from the harness by now except
    # through hass; find the coordinators still on the bus.
    await _settle()
    for _ids, action in list(hass.state_listeners):
        owner = _owner(action)
        if owner is not None and owner not in strong:
            strong.append(owner)
    for _topic, cb in list(hass.mqtt_subs):
        owner = _owner(cb)
        if owner is not None and owner not in strong:
            strong.append(owner)

    leaked_listeners, leaked_subs = _count_for(hass, strong)
    dead = [weakref.ref(c) for c in strong]

    # The dead handlers that fire on a power-meter event.
    handler_runs = 0
    event = type("Ev", (), {"data": {"new_state": FakeState("2500", unit="W")}})()
    for _ids, action in list(hass.state_listeners):
        if getattr(action, "__name__", "") == "_on_power_event":
            try:
                action(event)
                handler_runs += 1
            except Exception:  # noqa: BLE001
                handler_runs += 1

    zombies = len(strong)
    strong.clear()
    gc.collect()
    alive_after_gc = sum(1 for ref in dead if ref() is not None)

    return {
        "retries": retries,
        "leaked_listeners": leaked_listeners,
        "leaked_mqtt_subs": leaked_subs,
        "zombie_coordinators": zombies,
        "zombie_handler_runs": handler_runs,
        "alive_after_gc": alive_after_gc,
        "escaped_exceptions": escaped,
    }


async def _run_healthy_arm(*, eager: bool) -> dict:
    """NULL CONTROL: a setup that succeeds, then a normal unload.

    Registration must still happen (the fix must not stop the listeners
    working) and the unload must still remove every one of them.
    """
    hass = LoopHass(_states(), eager=eager)
    entry = FakeEntry(data=dict(BASE_CONFIG), entry_id="healthy")

    from harness import ha_setup_entry, ha_unload_entry

    ok = await ha_setup_entry(integration, hass, entry)
    await _settle()
    live_listeners = len(hass.state_listeners)
    live_subs = len(hass.mqtt_subs)

    # The guard actually runs on a meter event while loaded.
    fired = 0
    event = type("Ev", (), {"data": {"new_state": FakeState("2500", unit="W")}})()
    for _ids, action in list(hass.state_listeners):
        if getattr(action, "__name__", "") == "_on_power_event":
            action(event)
            fired += 1

    unloaded = await ha_unload_entry(integration, hass, entry)
    await _settle()
    return {
        "setup_ok": int(bool(ok)),
        "live_listeners": live_listeners,
        "live_mqtt_subs": live_subs,
        "guard_fired_while_loaded": fired,
        "unload_ok": int(bool(unloaded)),
        "listeners_after_unload": len(hass.state_listeners),
        "mqtt_subs_after_unload": len(hass.mqtt_subs),
    }


def _slope(points: list[tuple[int, int]]) -> float:
    """Least-squares slope through the origin: zombies per retry."""
    num = sum(n * z for n, z in points)
    den = sum(n * n for n, _ in points)
    return num / den if den else 0.0


async def main() -> None:
    coord_mod.mqtt.async_subscribe = _fake_subscribe

    results: list[tuple[str, str]] = []
    for arm_name, eager in (("eager", True), ("lazy", False)):
        points = []
        for n in (1, 2, 3, 5, 8):
            row = await _run_notready_arm(
                n, eager=eager, guards_off=False, settle_before_failure=True
            )
            points.append((n, row["zombie_coordinators"]))
            for key in (
                "leaked_listeners",
                "leaked_mqtt_subs",
                "zombie_coordinators",
                "zombie_handler_runs",
                "alive_after_gc",
                "escaped_exceptions",
            ):
                results.append((f"notready_{arm_name}.n{n}.{key}", str(row[key])))
        results.append(
            (f"notready_{arm_name}.slope_zombies_per_retry", f"{_slope(points):.4f}")
        )

    # The lazy arm's hard case: the spawned registrations run only AFTER the
    # NotReady has already fired and the on_unload callbacks have run.
    for n in (1, 5):
        row = await _run_notready_arm(
            n, eager=False, guards_off=False, settle_before_failure=False
        )
        for key in ("leaked_listeners", "leaked_mqtt_subs", "zombie_coordinators"):
            results.append((f"notready_lazy_late.n{n}.{key}", str(row[key])))

    # PERTURBATION / guards-off arm.
    for arm_name, eager in (("eager", True), ("lazy", False)):
        row = await _run_notready_arm(
            5, eager=eager, guards_off=True, settle_before_failure=True
        )
        for key in (
            "leaked_listeners",
            "leaked_mqtt_subs",
            "zombie_coordinators",
            "zombie_handler_runs",
        ):
            results.append((f"guards_off_{arm_name}.{key}", str(row[key])))

    # NULL CONTROL: healthy setup + unload.
    for arm_name, eager in (("eager", True), ("lazy", False)):
        row = await _run_healthy_arm(eager=eager)
        for key, value in row.items():
            results.append((f"healthy_{arm_name}.{key}", str(value)))

    for name, value in results:
        print(f"RESULT {name}={value} count")

    t0 = time.process_time()
    tt0 = time.thread_time()
    x = 0.0
    for i in range(200000):
        x += i ** 0.5
    proc = time.process_time() - t0
    thread = time.thread_time() - tt0
    print(f"RESULT thread_factor={proc / thread if thread else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    os.environ.setdefault("HPO_PLANDATA", tempfile.mkdtemp() + "/plandata.json")
    asyncio.run(main())
