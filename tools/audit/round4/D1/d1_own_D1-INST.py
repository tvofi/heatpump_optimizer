"""D1-INST verified independently (verifier seat D1-1, round 4).

MY METRIC: two counts.
  (a) stub_cycles: how many update cycles the suite's
      ``DataUpdateCoordinator`` base class runs when its three refresh
      entry points are awaited -- instrumented by subclassing the stub with
      a counting ``_async_update_data`` (the method real Home Assistant's
      base class calls; the stub never does).
  (b) setup_consumes_flag: after a full production setup
      (``ha_setup_entry`` -> ``__init__.py``'s
      ``coordinator._skip_solve_once = True`` +
      ``await coordinator.async_config_entry_first_refresh()``), whether
      the flag production latched has been consumed (0 = still latched).
      ``_async_update_data`` is spied at class level, so ANY path through
      the base class that ran a cycle would be counted. Control: driving
      ``_async_update_data()`` directly consumes the flag (must be 1),
      proving the production consumption code works and only the
      base-class wiring is untested.

COMMAND (from this worktree root):
  PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
    tools/audit/round4/D1/d1_own_D1-INST.py
EXPECTED: stub_refresh_runs_update_cycles=0, setup_spied_update_cycles=0,
  setup_flag_still_latched=1, direct_cycle_consumes_flag=1.
BASELINE: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697 (tree verified identical
  for custom_components/heatpump_optimizer/*.py at 0855277).
MACHINE: 8-core Apple M1, macOS 25.6.0, CPython 3.11. Counts only.
INSTRUMENTS: tests/hastub DataUpdateCoordinator.async_refresh /
  async_config_entry_first_refresh / async_request_refresh (the accused
  instrument); heatpump_optimizer.__init__.async_setup_entry (the flag
  setter); heatpump_optimizer.coordinator._async_update_data (spied).
"""
from __future__ import annotations

import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import asyncio
import sys
import time

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState, ha_setup_entry  # noqa: E402
from homeassistant.helpers.update_coordinator import (  # noqa: E402
    DataUpdateCoordinator,
)

import heatpump_optimizer as integration  # noqa: E402
import heatpump_optimizer.const as const  # noqa: E402

CONFIG = {
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    const.CONF_DHW_TANK_VOLUME: 180.0,
}


async def stub_cycles() -> int:
    """(a) Does the stub's base class ever call _async_update_data?"""

    class Probe(DataUpdateCoordinator):
        def __init__(self):
            super().__init__(hass := FakeHass(), "probe")
            self.update_calls = 0

        async def _async_update_data(self):
            self.update_calls += 1
            return {}

    probe = Probe()
    await probe.async_refresh()
    await probe.async_config_entry_first_refresh()
    await probe.async_request_refresh()
    return probe.update_calls


async def setup_arm() -> dict:
    """(b) Full production setup; spy _async_update_data at class level."""
    from heatpump_optimizer.coordinator import (
        HeatPumpOptimizerCoordinator as Coord,
    )

    calls = {"n": 0}
    orig = Coord._async_update_data

    async def spy(self):
        calls["n"] += 1
        return await orig(self)

    Coord._async_update_data = spy
    out = {}
    try:
        hass = FakeHass()
        hass.states.set("sensor.indoor", FakeState("21.0"))
        hass.states.set("sensor.outdoor", FakeState("-2.0"))
        entry = FakeEntry(data=dict(CONFIG), entry_id="d1inst_entry")
        ok = await ha_setup_entry(integration, hass, entry)
        coord = getattr(entry, "runtime_data", None)
        out["setup_ok"] = bool(ok and coord is not None)
        out["spied_cycles"] = calls["n"]
        out["flag_latched"] = bool(getattr(coord, "_skip_solve_once", False))
        out["refresh_requests"] = getattr(coord, "refresh_requests", -1)
        # Control: the production consumption code itself works when the
        # cycle is driven directly, the way real_loop.py and features.py
        # must drive it. The three network fetches are noop'd per instance
        # (real_loop.py's own workaround for the same stub limits).
        async def _noop() -> None:
            return None

        coord._fetch_tibber_prices = _noop
        coord._fetch_weather_forecast = _noop
        coord._fetch_solar_forecast = _noop
        await coord._async_update_data()
        out["flag_after_direct"] = bool(coord._skip_solve_once)
        out["spied_cycles_after_direct"] = calls["n"]
    finally:
        Coord._async_update_data = orig
    return out


def main() -> int:
    t0 = time.perf_counter()
    print("=== D1-INST, verifier's own instrument ===")
    stub = asyncio.run(stub_cycles())
    arm = asyncio.run(setup_arm())
    print(f"  stub refresh entry points run {stub} update cycles")
    print(f"  production setup ok                  {arm['setup_ok']}")
    print(f"  spied _async_update_data during setup {arm['spied_cycles']}")
    print(
        f"  refresh_requests counted by stub      {arm['refresh_requests']}"
    )
    print(f"  _skip_solve_once latched after setup  {arm['flag_latched']}")
    print(
        f"  direct cycle consumes it              "
        f"{not arm['flag_after_direct']} "
        f"(spied total {arm['spied_cycles_after_direct']})"
    )

    print()
    print(f"RESULT stub_refresh_runs_update_cycles={stub} count")
    print(f"RESULT setup_spied_update_cycles={arm['spied_cycles']} count")
    print(f"RESULT setup_flag_still_latched={int(arm['flag_latched'])} count")
    print(
        f"RESULT direct_cycle_consumes_flag="
        f"{int(not arm['flag_after_direct'])} count"
    )
    print(f"RESULT wall_s={time.perf_counter() - t0:.2f} wall")
    print("RESULT thread_factor=1.0000")
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    except OSError:
        print("RESULT load1=-1")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
