#!/usr/bin/env python3
"""D1-s3-02: a SINGLE malformed entry inside an otherwise well-formed
`weather.get_forecasts` response (an external input HA hands the coordinator
verbatim, controlled by the weather integration, not by us) permanently
poisons ``self._weather_forecast`` with a non-dict item. Every later solve's
``_weather_series`` crashes on that element with ``AttributeError``. Because
``Coordinator._fetch_weather_forecast`` assigns
``self._weather_forecast = forecast_data`` BEFORE it finishes validating the
list (the per-entry solar-radiation loop that follows), the poisoned list is
already live when the crash happens, so the documented M2 self-heal path
("Nothing better exists: fabricate...", guarded by
``if state and not self._weather_forecast``) never fires -- the guard sees a
non-empty (poisoned) list and stays off. The result: the optimizer produces
NO PLAN on this cycle and every cycle after, for as long as
``self._weather_forecast`` holds the poisoned list -- which, since nothing
ever clears or re-validates it, is indefinitely, even once the weather
integration goes back to sending clean data (the coordinator never looks at
_weather_forecast's shape again once a fetch nominally "succeeds").

This is the guard-recovery failure the D1 brief singles out (method step 5):
"does it recover on the next cycle" -- here it provably does not, without a
config reload.

Metric definition: solves_recovered_out_of_n = count of N subsequent
``_forecast_arrays()`` calls, after ONE poisoned fetch, that complete without
raising, out of N total (each simulating one full refresh cycle with a
otherwise-healthy weather payload arriving on every later poll).

Instrumented symbols:
  heatpump_optimizer.coordinator.HeatPumpOptimizerCoordinator._fetch_weather_forecast
  heatpump_optimizer.coordinator.HeatPumpOptimizerCoordinator._weather_series
  heatpump_optimizer.coordinator.HeatPumpOptimizerCoordinator._forecast_arrays

Perturbation: in ``_fetch_weather_forecast``, validate `forecast_data` entries
BEFORE the assignment `self._weather_forecast = forecast_data` (drop
non-dict entries the way ``open_meteo._parse_block`` already drops malformed
samples) -- expected direction: solves_recovered_out_of_n rises from 0 to N
for the same poisoned-then-healthy payload sequence.

Null control: running the SAME N-cycle sequence with an all-healthy payload
throughout (never poisoned) must show 0 crashes (control_crashed == 0),
proving the crash is caused by the one bad entry, not the harness.

Command:
  cd <tree-root> && PYTHONPATH=tests/hastub \
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
    python3 tools/audit/round8/D1/s3_weather_poison.py

Expected: RESULT solves_recovered_out_of_n=0 count (of 5), tolerance 0
          RESULT control_crashed=0 count, tolerance 0

Baseline SHA: cdf82daabcfe3777d98b31489f36df5555ec9d82
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
from datetime import datetime, timedelta, timezone

_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "tests"))

from harness import FakeHass, FakeEntry, FakeState  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

N_CYCLES = 5


def _honest_coordinator(extra_config=None):
    """A coordinator that has completed one real input-read cycle (mirrors
    tests/entities.py:_honest_coordinator, reimplemented here so this
    harness does not have to import entities.py's whole check suite, which
    runs hundreds of assertions and sys.exit()s at import time)."""
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    config = {
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    }
    config.update(extra_config or {})
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=config))
    asyncio.run(coord._update_current_state())
    return hass, coord


def _healthy_forecast(now):
    return [
        {
            "datetime": (now + timedelta(hours=i)).isoformat(),
            "temperature": 5.0,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "solar_irradiance": 0.0,
        }
        for i in range(48)
    ]


def _poisoned_forecast(now):
    """Otherwise-healthy 48h forecast with ONE entry replaced by a bare
    string -- the shape a real weather integration produces when one of its
    own upstream API calls returns a malformed / truncated record and it
    passes the row through instead of dropping it (this is not hypothetical:
    #1090, cited in the D1 brief, is exactly this class of bug in a
    different producer)."""
    forecast = _healthy_forecast(now)
    forecast[5] = "malformed-entry"  # valid list element, wrong type
    return forecast


class _ServiceCallResult(dict):
    pass


def run(poison_first: bool) -> tuple[int, int]:
    """Returns (solves_ok, crashes) across N_CYCLES cycles."""
    weather_entity = "weather.home"
    hass, coord = _honest_coordinator(
        extra_config={const.CONF_WEATHER_ENTITY: weather_entity}
    )
    hass.states.set(
        weather_entity,
        FakeState("sunny", attributes={"temperature": 5.0, "wind_speed": 2.0}),
    )
    # Synthetic prices, bypassing the Tibber fetch, so `_forecast_arrays`
    # reaches `_weather_series` instead of short-circuiting on `no_prices`
    # (that early-return is a SEPARATE, unrelated guard from the one under
    # test here and must not mask it).
    now0 = datetime.now(timezone.utc)
    coord._prices = [
        {
            "start": (now0 + timedelta(hours=i)).isoformat(),
            "total": 0.20,
        }
        for i in range(48)
    ]

    async def fake_async_call(domain, service, data, blocking=True, return_response=True):
        now = datetime.now(timezone.utc)
        entity = data["entity_id"]
        payload = _poisoned_forecast(now) if fake_async_call.poison else _healthy_forecast(now)
        fake_async_call.poison = False  # only the FIRST call is poisoned
        return {entity: {"forecast": payload}}

    fake_async_call.poison = poison_first
    hass.services.async_call = fake_async_call

    solves_ok = 0
    crashes = 0
    for cycle in range(N_CYCLES):
        asyncio.run(coord._fetch_weather_forecast())
        try:
            arrays = coord._forecast_arrays(datetime.now(timezone.utc).astimezone())
            # touch the arrays the way the solve does, to force lazy work
            _ = list(arrays.outdoor_temps)
            solves_ok += 1
        except Exception:  # noqa: BLE001 - this IS the measurement
            crashes += 1
    return solves_ok, crashes


def main() -> None:
    solves_ok, crashes = run(poison_first=True)
    print(f"  poisoned-first sequence: solves_ok={solves_ok} crashes={crashes} (of {N_CYCLES})")
    control_ok, control_crashed = run(poison_first=False)
    print(f"  control (never poisoned): solves_ok={control_ok} crashes={control_crashed}")

    print(f"RESULT solves_recovered_out_of_n={solves_ok} count")
    print(f"RESULT crashes_after_poison={crashes} count")
    print(f"RESULT control_crashed={control_crashed} count")
    print(f"RESULT n_cycles={N_CYCLES} count")


if __name__ == "__main__":
    main()
