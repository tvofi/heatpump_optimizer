"""Verifier-2 probe for D1-INST (the update_coordinator stub defect).

METRIC (mine): (a) ``stub_refresh_cycles_run`` -- how many times
``_async_update_data`` actually executes when the coordinator's
``async_refresh`` and ``async_config_entry_first_refresh`` are awaited
under ``tests/hastub`` (the stub's answer must be 0, while
``refresh_requests`` increments); (b) ``skip_flag_after_setup`` -- whether
``_skip_solve_once`` is still armed after a full real ``async_setup_entry``
under the stub (1 = armed, i.e. the stubbed first refresh did not consume
it); (c) ``skip_flag_after_direct_call`` -- 0, consumed by the direct
``_async_update_data`` call the suite makes in features.py:16288/16690.

COMMAND (from the worktree root):
  PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
    tools/audit/round4/D1/verify2_d1inst.py

EXPECTED: stub_refresh_cycles_run=0, refresh_requests=2,
  skip_flag_after_setup=1, skip_flag_after_direct_call=0.
BASELINE: branch head 0855277
MACHINE:  8-core Apple M1, macOS 25.6.0, CPython 3.11
INSTRUMENTS: tests/hastub/homeassistant/helpers/update_coordinator.py
  DataUpdateCoordinator.async_refresh / async_config_entry_first_refresh,
  against heatpump_optimizer.__init__.async_setup_entry's refresh wiring.
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

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState, ha_setup_entry  # noqa: E402

import heatpump_optimizer as integration  # noqa: E402
import heatpump_optimizer.const as const  # noqa: E402

CONFIG = {
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    const.CONF_DHW_TANK_VOLUME: 180.0,
}


async def main() -> int:
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    entry = FakeEntry(data=dict(CONFIG))
    entry.entry_id = "inst_probe"
    ok = await ha_setup_entry(integration, hass, entry)
    coord = entry.runtime_data

    cycles = {"n": 0}
    _real = coord._async_update_data

    async def _counted():
        cycles["n"] += 1
        return await _real()

    coord._async_update_data = _counted
    await coord.async_refresh()
    await coord.async_config_entry_first_refresh()
    stub_cycles = cycles["n"]
    requests = coord.refresh_requests

    armed_after_setup = int(bool(coord._skip_solve_once))
    # Seed a horizon and no-op the three fetches (the stub session has no
    # HTTP), so the direct refresh takes the light path as setup would.
    from datetime import timedelta

    from homeassistant.util import dt as dt_util

    now = dt_util.now().replace(minute=0, second=0, microsecond=0)
    coord._prices = [
        {"total": 0.6, "starts_at": (now + timedelta(hours=h)).isoformat(),
         "level": "NORMAL"}
        for h in range(48)
    ]
    coord._weather_forecast = [
        {"datetime": (now + timedelta(hours=h)).isoformat(),
         "temperature": -5.0, "wind_speed": 3.0, "precipitation": 0.0,
         "humidity": 85.0}
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [0.0] * 48

    async def _noop():
        return None

    coord._fetch_tibber_prices = _noop
    coord._fetch_weather_forecast = _noop
    coord._fetch_solar_forecast = _noop
    await coord._async_update_data()
    armed_after_direct = int(bool(coord._skip_solve_once))

    print("=== D1-INST verifier-2 probe ===")
    print(f"  setup ok                       {ok}")
    print(f"  _async_update_data runs after 2 stub refreshes: {stub_cycles}")
    print(f"  refresh_requests counter                      {requests}")
    print(f"  _skip_solve_once armed after setup            {armed_after_setup}")
    print(f"  ... after one direct _async_update_data       {armed_after_direct}")

    print()
    print(f"RESULT stub_refresh_cycles_run={stub_cycles} count")
    print(f"RESULT refresh_requests={requests} count")
    print(f"RESULT skip_flag_after_setup={armed_after_setup} count")
    print(f"RESULT skip_flag_after_direct_call={armed_after_direct} count")
    print("RESULT thread_factor=1.0000")
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    except OSError:
        print("RESULT load1=-1")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
