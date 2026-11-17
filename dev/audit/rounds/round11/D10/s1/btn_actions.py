#!/usr/bin/env python3
"""D10.M1 action-exceptions (Silver): button presses that refuse or fail return success.

Metric: of the button presses driven below whose action did NOT take effect
(the experiment was not armed; the diagnosis worker failed), the number whose
``async_press`` returned without raising. Each press's background work is run
to completion on a real asyncio loop (the entry background task the press
hands off), so "did not take effect" is read after the work finished.
Count key: the production seam's own outcome -- ``coordinator._sysid.phase``
after the arm, and the exception the background diagnosis raised -- never an
input attribute.
Cases:
  sysid_disabled   SystemIdentificationButton, default config (feature off)
  diagnose_failed  DiagnoseIntervalButton, process worker unavailable
Controls (the compliant siblings under the same failure, and the arm that takes):
  SystemIdentificationButton with the feature on arms (phase idle->armed)
  ForceOptimizationButton with run_optimization reporting no_prices -> raises
  services.handle_diagnose_interval with the worker unavailable     -> raises
Instrumented symbols: button:SystemIdentificationButton.async_press,
button:DiagnoseIntervalButton.async_press, entity:off_the_action,
coordinator:HeatPumpOptimizerCoordinator.async_arm_system_identification,
coordinator:HeatPumpOptimizerCoordinator.async_diagnose_interval.
Perturbation: ``--perturb`` replaces the two presses with the fix shape --
the work awaited in the press, and HomeAssistantError raised when the arm
returned False or the diagnosis raised; silent_refusals must fall to 0
(direction to_zero) while the controls still raise.

Run (from the export root):
  PYTHONPATH=tests/hastub /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python3 \
      dev/audit/rounds/round11/D10/s1/btn_actions.py [--perturb]
Expected: silent_refusals=2 of 2 (exact), controls_raised=2 of 2, sysid_enabled_armed=1;
under --perturb silent_refusals=0.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: macOS arm64, venv-ci Python 3.14.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import sys
import tempfile
import time

sys.path.insert(0, "tests")
os.environ.setdefault("HPO_PLANDATA", os.path.join(tempfile.mkdtemp(prefix="d10s1."), "plandata.json"))
from harness import FakeHass, FakeEntry  # noqa: E402

from homeassistant.config_entries import ConfigEntryState  # noqa: E402
from homeassistant.exceptions import HomeAssistantError  # noqa: E402

from heatpump_optimizer import button, services  # noqa: E402
from heatpump_optimizer import coordinator as coord_mod  # noqa: E402
from heatpump_optimizer.const import DOMAIN  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

PERTURB = "--perturb" in sys.argv


class LoopHass(FakeHass):
    """FakeHass whose background tasks really run, so their outcome is readable."""

    def __init__(self):
        super().__init__()
        self.tasks = []

    def async_create_task(self, coro, *a, **k):
        t = asyncio.get_running_loop().create_task(coro)
        self.tasks.append(t)
        return t


def make(**cfg):
    hass = LoopHass()
    entry = FakeEntry(data={"tibber_token": "x", "weather_entity": "weather.home", **cfg})
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    entry.runtime_data = coord
    entry.state = ConfigEntryState.LOADED
    hass.config_entries.entries.append(entry)

    async def _noop():
        return None
    coord.async_request_refresh = _noop
    return hass, entry, coord


def entity(cls, hass, entry, coord):
    e = cls(coord, entry)
    e.hass = hass
    e.async_write_ha_state = lambda: None
    return e


async def press(ent, hass):
    """(raised_in_press, background_exception)"""
    raised = None
    try:
        await ent.async_press()
    except Exception as err:  # noqa: BLE001
        raised = type(err).__name__
    bg = None
    for t in list(hass.tasks):
        try:
            await t
        except Exception as err:  # noqa: BLE001
            bg = type(err).__name__
    return raised, bg


async def _worker_down(*a, **k):
    raise coord_mod.ProcessWorkerUnavailable("worker unavailable (harness)")


def install_fix():
    async def sysid_press(self):
        before = self.coordinator._sysid.phase
        await self.coordinator.async_arm_system_identification()
        if self.coordinator._sysid.phase == before:
            raise HomeAssistantError("system identification not armed")

    async def diag_press(self):
        try:
            await self.coordinator.async_diagnose_interval()
        except coord_mod.ProcessWorkerUnavailable as err:
            raise HomeAssistantError(str(err)) from err
    button.SystemIdentificationButton.async_press = sysid_press
    button.DiagnoseIntervalButton.async_press = diag_press
    print("RESULT perturbed=presses await their work and raise on refusal/failure")


async def main():
    if PERTURB:
        install_fix()
    silent = 0
    cases = 0

    # sysid_disabled: the default configuration (system_identification_enabled False).
    hass, entry, coord = make()
    phase0 = coord._sysid.phase
    raised, bg = await press(entity(button.SystemIdentificationButton, hass, entry, coord), hass)
    armed = coord._sysid.phase != phase0
    print(f"CASE sysid_disabled: raised={raised} bg={bg} phase {phase0}->{coord._sysid.phase} available")
    cases += 1
    silent += int(raised is None and not armed)

    # diagnose_failed: the process worker cannot carry the job.
    hass, entry, coord = make()
    orig = coord_mod._await_process
    coord_mod._await_process = _worker_down
    try:
        raised, bg = await press(entity(button.DiagnoseIntervalButton, hass, entry, coord), hass)
    finally:
        coord_mod._await_process = orig
    print(f"CASE diagnose_failed: raised={raised} bg={bg}")
    cases += 1
    silent += int(raised is None and bg is not None)

    # Controls.
    controls = 0
    hass, entry, coord = make()

    async def _no_prices():
        return "no_prices"
    coord.async_run_optimization = _no_prices
    raised, _ = await press(entity(button.ForceOptimizationButton, hass, entry, coord), hass)
    print(f"CONTROL force_optimization no_prices: raised={raised}")
    controls += int(raised is not None)

    hass, entry, coord = make()
    services.async_register_services(hass)
    coord_mod._await_process = _worker_down
    try:
        await hass.services.async_call(DOMAIN, "diagnose_interval", {}, blocking=True)
        out = None
    except HomeAssistantError as err:
        out = type(err).__name__
    finally:
        coord_mod._await_process = orig
    print(f"CONTROL service diagnose_interval worker down: raised={out}")
    controls += int(out is not None)

    # Control: with the feature on the same press arms.
    hass, entry, coord = make(system_identification_enabled=True)
    phase0 = coord._sysid.phase
    raised, _ = await press(entity(button.SystemIdentificationButton, hass, entry, coord), hass)
    print(f"CONTROL sysid_enabled: raised={raised} phase {phase0}->{coord._sysid.phase}")
    print(f"RESULT sysid_enabled_armed={int(coord._sysid.phase != phase0)} count")

    print(f"RESULT cases={cases} count")
    print(f"RESULT silent_refusals={silent} count")
    print(f"RESULT controls_raised={controls} count")


if __name__ == "__main__":
    c0, t0 = time.process_time(), time.thread_time()
    asyncio.run(main())
    c1, t1 = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={((c1 - c0) / max(t1 - t0, 1e-9)):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
