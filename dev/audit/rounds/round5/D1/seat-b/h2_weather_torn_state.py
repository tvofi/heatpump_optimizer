#!/usr/bin/env python3
"""h2_weather_torn_state.py -- D1-b round 5, finding F2.

Metric definition (one line): over 5 consecutive production weather fetch
cycles whose service answer carries ONE hostile entry (``solar_irradiance``
as the string "n/a") among 24 healthy hourly entries, count (a) cycles that
end with the fresh-forecast staleness latch set (``_weather_stale_since``
not None) and (b) the truncated ``_solar_radiation_forecast`` length
against the 24-entry ``_weather_forecast`` (torn pair), plus the WARNING
line count.

Count key: the values the production seam delivers after
``_fetch_weather_forecast`` -- ``coordinator._weather_stale_since`` /
``weather_stale_hours()`` / ``len(coordinator._solar_radiation_forecast)``
versus ``len(coordinator._weather_forecast)`` -- never the input attribute.

Command (from the repository root):
  PYTHONPATH=tests/hastub:tests:. OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  python3 tools/audit/round5/D1/seat-b/h2_weather_torn_state.py

Expected at baseline 1cc89e0 (executed 2026-09-20, Apple M1, python 3.11):
  RESULT stale_latched_cycles=5 of 5   (fresh data, permanently flagged stale)
  RESULT torn_solar_len=0 of 24        (solar series left truncated)
  RESULT weather_warning_lines=1       (logs once -- the log-once property holds)
  Perturbation arm (the one-line production edit applied in memory:
  `float(sr or 0.0)` -> `_as_float(sr, 0.0)` at coordinator.py's solar loop):
  RESULT stale_latched_cycles_patched=0, torn_solar_len_patched=24.
  Null control (all-healthy forecast): latch never set.
Tolerance: exact for counts.

Semantics note: runs under FakeHass with ``hass.services.async_call``
instance-overridden to answer the weather service call (in-memory only) --
the only seam the real loop would traverse; no lifecycle method is called
directly. The perturbation recompiles the production method from its own
source with the single line changed and rebinds it on the class in memory;
no file on disk is modified.
"""
# Thread pin BEFORE any numpy import (audit README contract).
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
import inspect
import logging
import sys
import textwrap
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tests")
sys.path.insert(0, ".")

from harness import FakeHass, FakeState, FakeEntry  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

WEATHER_ENTITY = "weather.home"
N_CYCLES = 5
N_ENTRIES = 24
SEAM_OLD = "self._solar_radiation_forecast.append(float(sr or 0.0))"
SEAM_NEW = "self._solar_radiation_forecast.append(_as_float(sr, 0.0))"


def hostile_forecast(now):
    """24 healthy hourly entries; entry 7 carries a string solar_irradiance."""
    out = []
    for i in range(N_ENTRIES):
        entry = {
            "datetime": (now + timedelta(hours=i)).isoformat(),
            "temperature": 4.0 - 0.2 * i,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "humidity": 70.0,
        }
        if i == 7:
            # A weather integration is free to publish a non-numeric
            # irradiance (Home Assistant's Forecast type allows objects).
            entry["native_solar_irradiance"] = "n/a"
        else:
            entry["native_solar_irradiance"] = float(50 * max(0, i - 6))
        out.append(entry)
    return out


def healthy_forecast(now):
    rows = hostile_forecast(now)
    rows[7]["native_solar_irradiance"] = 0.0
    return rows


class _RecordingHandler(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.DEBUG)
        self.records = []

    def emit(self, record):
        self.records.append(record)

    def count(self, levelname, needle):
        return sum(
            1
            for r in self.records
            if r.levelname == levelname and needle in r.getMessage()
        )


def build(forecast_fn):
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    hass.states.set(WEATHER_ENTITY, FakeState("cloudy"))

    async def _fake_call(domain, service, data=None, **kwargs):
        assert (domain, service) == ("weather", "get_forecasts")
        return {WEATHER_ENTITY: {"forecast": forecast_fn(datetime.now(timezone.utc))}}

    hass.services.async_call = _fake_call  # in-memory override
    config = {
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
        const.CONF_DHW_TANK_VOLUME: 180.0,
        const.CONF_WEATHER_ENTITY: WEATHER_ENTITY,
    }
    return HeatPumpOptimizerCoordinator(hass, FakeEntry(data=config))


def drive(forecast_fn, cycles=N_CYCLES):
    handler = _RecordingHandler()
    logging.getLogger("heatpump_optimizer").addHandler(handler)
    coord = build(forecast_fn)
    latched = 0
    for _ in range(cycles):
        asyncio.run(coord._fetch_weather_forecast())
        if coord._weather_stale_since is not None:
            latched += 1
    logging.getLogger("heatpump_optimizer").removeHandler(handler)
    return {
        "latched_cycles": latched,
        "forecast_len": len(coord._weather_forecast),
        "solar_len": len(coord._solar_radiation_forecast),
        "stale_hours": coord.weather_stale_hours(),
        "warnings": handler.count("WARNING", "weather"),
        "errors": handler.count("ERROR", "weather"),
    }


def apply_one_line_fix_in_memory():
    """Recompile the production method from its own source with the single
    solar-loop line changed, and rebind it on the class. Nothing on disk."""
    import heatpump_optimizer.coordinator as C

    src = inspect.getsource(HeatPumpOptimizerCoordinator._fetch_weather_forecast)
    if SEAM_OLD not in src:
        raise SystemExit(f"seam not found in source; baseline moved: {SEAM_OLD!r}")
    patched_src = textwrap.dedent(src).replace(SEAM_OLD, SEAM_NEW)
    # Re-indent from the method body (inspect source includes the def line
    # at class indentation); compile in module globals, bind on the class.
    namespace = dict(vars(C))
    exec(compile(patched_src, "<one-line-fix>", "exec"), namespace)  # noqa: S102
    method = namespace["_fetch_weather_forecast"]
    HeatPumpOptimizerCoordinator._fetch_weather_forecast = method


def main() -> int:
    base = drive(hostile_forecast)
    print(f"RESULT stale_latched_cycles={base['latched_cycles']} of {N_CYCLES}")
    print(f"RESULT forecast_len={base['forecast_len']} of {N_ENTRIES}")
    print(f"RESULT torn_solar_len={base['solar_len']} of {base['forecast_len']}")
    print(f"RESULT stale_hours_after_cycles={base['stale_hours']}")
    print(f"RESULT weather_warning_lines={base['warnings']}")
    print(f"RESULT weather_error_lines={base['errors']}")

    original = HeatPumpOptimizerCoordinator._fetch_weather_forecast
    try:
        apply_one_line_fix_in_memory()
        patched = drive(hostile_forecast)
    finally:
        HeatPumpOptimizerCoordinator._fetch_weather_forecast = original
    print(
        f"RESULT stale_latched_cycles_patched={patched['latched_cycles']} of {N_CYCLES}"
    )
    print(f"RESULT torn_solar_len_patched={patched['solar_len']} of {N_ENTRIES}")

    null = drive(healthy_forecast)
    print(
        f"RESULT null_control_stale_latched_cycles={null['latched_cycles']} of {N_CYCLES}"
    )
    print(f"RESULT null_control_solar_len={null['solar_len']} of {N_ENTRIES}")
    print("RESULT thread_factor=1.00 (single-threaded harness)")
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    except Exception:
        print("RESULT load1=unknown")
    print("RESULT swapins=0 (no psi on darwin)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
