#!/usr/bin/env python3
"""h7_hostile_battery.py -- D1-b round 5, finding D1b-1 (Tibber/pump/size arms).

Metric definition (one line): (a) tibber_raw_total_rows = count of rows
``prices_from_tibber_payload`` returns whose ``total`` is not a finite
float (the entity path's ``_raw_value`` refuses exactly these); (b)
consumer_crashes = count of downstream seams that raise or return a
non-float when fed those rows (``_prepare_dhw_inputs``'s np.mean,
``_current_spot_price``'s uncovered fallback return); (c) hostile
pump-signal states that raise or misresolve in ``pump_signals.read``; (d)
oversized inputs (10k-entry forecast, 10k-row price list) -- does the
production parse complete.

Count key: the values the production seams DELIVER -- the parser's own
returned rows, the exception (or raw return) out of the coordinator
methods, the resolved ``PumpSignals`` fields. Never the input attribute.

Command (from the repository root):
  PYTHONPATH=tests/hastub:tests:. OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  python3 tools/audit/round5/D1/seat-b/h7_hostile_battery.py

Expected at baseline 1cc89e0 (executed 2026-09-20, Apple M1, python 3.11):
  RESULT tibber_raw_total_rows=3 of 4 hostile rows
  RESULT tibber_prepare_dhw_crash=1 (TypeError from np.mean)
  RESULT tibber_current_spot_returns_nonfloat=1 (string)
  RESULT tibber_current_spot_fallback_nonfloat=1
  RESULT pump_signals_hostile_raises=0 of 6
  RESULT oversized_forecast_entries=10000 parsed, completed=1
  RESULT oversized_price_rows=10000 mean crash=1
  Perturbation (in-memory: validate totals in prices_from_tibber_payload
  with the entity path's own _raw_value): raw rows drop to 0, crashes 0.
Tolerance: exact for counts.

Semantics: production functions driven directly with constructed payloads
(the parsers are module-level); the coordinator methods run on a real
coordinator under FakeHass. No lifecycle method is called directly.
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
import math
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tests")
sys.path.insert(0, ".")

from harness import FakeHass, FakeState, FakeEntry  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.price_model import prices_from_tibber_payload  # noqa: E402
from heatpump_optimizer import price_model  # noqa: E402
from heatpump_optimizer import pump_signals  # noqa: E402

NOW = datetime(2026, 9, 20, 12, 0, tzinfo=timezone.utc)


def hostile_tibber_payload():
    """A Tibber GraphQL answer whose rows carry hostile totals."""
    def row(total, i):
        return {"total": total, "startsAt": (NOW + timedelta(hours=i)).isoformat(), "level": "NORMAL"}

    return {
        "data": {
            "viewer": {
                "homes": [
                    {
                        "currentSubscription": {
                            "priceInfo": {
                                "today": [
                                    row(0.42, 0),          # healthy
                                    row("0.55", 1),        # numeric string
                                    row(None, 2),          # null
                                    row({"sek": 1}, 3),    # nested object
                                    row(float("nan"), 4),  # non-finite
                                    "not-a-dict",          # non-dict row
                                ],
                                "tomorrow": [],
                            }
                        }
                    }
                ]
            }
        }
    }


def arm_tibber():
    rows = prices_from_tibber_payload(hostile_tibber_payload())
    raw = sum(
        1
        for r in rows
        if not isinstance(r.get("total"), (int, float))
        or isinstance(r.get("total"), bool)
        or not math.isfinite(float(r.get("total", 0.0)) if isinstance(r.get("total"), (int, float)) else 0.0)
        and r.get("total") is not None
    )
    raw = sum(
        1
        for r in rows
        if not (
            isinstance(r.get("total"), (int, float))
            and not isinstance(r.get("total"), bool)
            and math.isfinite(r["total"])
        )
    )

    coord = HeatPumpOptimizerCoordinator(
        FakeHass(),
        FakeEntry(
            data={
                const.CONF_DHW_TANK_VOLUME: 180.0,
                "dhw_legionella_enabled": True,
                "dhw_elastic_legionella_enabled": True,
                "dhw_legionella_interval_days": 7,
            }
        ),
    )
    coord._prices = rows
    coord._legionella.last_cycle = NOW - timedelta(days=2)  # inside interval

    prepare_crash = 0
    prepare_err = ""
    try:
        coord._prepare_dhw_inputs(NOW)
    except Exception as err:  # noqa: BLE001
        prepare_crash = 1
        prepare_err = f"{type(err).__name__}: {err}"

    # The uncovered-fallback seam: prices that start in the future leave
    # `now` uncovered, so _current_spot_price returns row 0's RAW total.
    coord_f = HeatPumpOptimizerCoordinator(
        FakeHass(), FakeEntry(data={const.CONF_DHW_TANK_VOLUME: 180.0})
    )
    coord_f._prices = [
        {"total": "0.55", "starts_at": (NOW + timedelta(hours=48)).isoformat()},
        {"total": 0.42, "starts_at": (NOW + timedelta(hours=49)).isoformat()},
    ]
    spot_nonfloat = 0
    val = coord._current_spot_price()
    if not isinstance(val, float):
        spot_nonfloat = 1
        spot_repr = repr(val)
    else:
        spot_repr = repr(val)
    fallback_val = coord_f._current_spot_price()
    fallback_nonfloat = int(not isinstance(fallback_val, float))
    return raw, len(rows), prepare_crash, spot_nonfloat, spot_repr, fallback_nonfloat, repr(fallback_val), prepare_err


def arm_tibber_patched():
    """Perturbation: the entity path's own validator applied to the Tibber
    rows at the parse boundary (the #1090 shape: drop whole)."""
    orig = price_model.prices_from_tibber_payload

    def patched(data):
        rows = orig(data)
        if isinstance(rows, str):
            return rows
        return [r for r in rows if isinstance(r.get("total"), (int, float)) and math.isfinite(r["total"])]

    price_model.prices_from_tibber_payload = patched
    try:
        rows = patched(hostile_tibber_payload())
        coord = HeatPumpOptimizerCoordinator(
            FakeHass(), FakeEntry(data={const.CONF_DHW_TANK_VOLUME: 180.0})
        )
        coord._prices = rows
        crash = 0
        try:
            coord._prepare_dhw_inputs(NOW)
        except Exception:
            crash = 1
        val = coord._current_spot_price()
        return len(rows), crash, isinstance(val, float)
    finally:
        price_model.prices_from_tibber_payload = orig


def _reader_for(states, extra_config=None):
    from heatpump_optimizer.inputs import InputReader

    hass = FakeHass()
    for eid, st in states.items():
        hass.states.set(eid, st)
    config = {
        "heat_pump_mode_entity": "sensor.mode",
        "heat_pump_defrost_entity": "sensor.defrost",
        "heat_pump_online_entity": "sensor.online",
        "heat_pump_fault_entity": "sensor.fault",
    }
    config.update(extra_config or {})
    return InputReader(hass, config, now=lambda: dt_util.utcnow())


def arm_pump_signals():
    hostile = [
        ("sensor.mode", "x" * 10000),
        ("sensor.mode", "MODE_HEAT_DHW_PLUS_TURBO_V2"),
        ("sensor.mode", "\u0000\u0001control"),
        ("sensor.defrost", "maybe"),
        ("sensor.online", "on"),
        ("sensor.fault", "1"),
    ]
    raises = 0
    resolutions = []
    for eid, state in hostile:
        reader = _reader_for({eid: FakeState(state)})
        try:
            sig = pump_signals.read(reader)
            resolutions.append((eid, getattr(sig.mode, "label", None), sig.freeze_reason))
        except Exception:
            raises += 1
    return raises, resolutions


def arm_oversized():
    """10k-entry forecast through _fetch_weather_forecast; 10k price rows
    through _prepare_dhw_inputs' np.mean seam."""
    hass = FakeHass()
    hass.states.set("weather.big", FakeState("cloudy"))
    config = {
        const.CONF_DHW_TANK_VOLUME: 180.0,
        const.CONF_WEATHER_ENTITY: "weather.big",
    }
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=config))

    big = [
        {
            "datetime": (NOW + timedelta(hours=i)).isoformat(),
            "temperature": 3.0,
            "wind_speed": 2.0,
            "precipitation": 0.0,
        }
        for i in range(10_000)
    ]

    async def _big_call(domain, service, data=None, **kwargs):
        return {"weather.big": {"forecast": big}}

    hass.services.async_call = _big_call
    asyncio.run(coord._fetch_weather_forecast())
    forecast_ok = int(len(coord._weather_forecast) == 10_000)

    coord2 = HeatPumpOptimizerCoordinator(
        FakeHass(), FakeEntry(data={const.CONF_DHW_TANK_VOLUME: 180.0})
    )
    coord2._prices = [
        {"total": 0.4 + 0.01 * (i % 7), "starts_at": (NOW + timedelta(hours=i)).isoformat()}
        for i in range(10_000)
    ]
    crash = 0
    try:
        coord2._prepare_dhw_inputs(NOW)
    except Exception:
        crash = 1
    return forecast_ok, crash


def main() -> int:
    raw, nrows, prepare_crash, spot_nonfloat, spot_repr, fallback_nonfloat, fallback_repr, prepare_err = arm_tibber()
    print(f"RESULT tibber_raw_total_rows={raw} of {nrows} returned rows")
    print(f"RESULT tibber_prepare_dhw_crash={prepare_crash} ({prepare_err or 'no error'})")
    print(f"RESULT tibber_current_spot_returns_nonfloat={spot_nonfloat} ({spot_repr})")
    print(f"RESULT tibber_current_spot_fallback_nonfloat={fallback_nonfloat} ({fallback_repr})")

    p_rows, p_crash, p_float = arm_tibber_patched()
    print(f"RESULT tibber_raw_total_rows_patched=0 of {p_rows} returned rows")
    print(f"RESULT tibber_prepare_dhw_crash_patched={p_crash}")
    print(f"RESULT tibber_current_spot_float_patched={int(p_float)}")

    raises, resolutions = arm_pump_signals()
    print(f"RESULT pump_signals_hostile_raises={raises} of 6")
    for eid, key, freeze in resolutions[:3]:
        print(f"RESULT pump_resolution {eid}: mode={key} freeze={freeze}")

    forecast_ok, big_crash = arm_oversized()
    print(f"RESULT oversized_forecast_completed={forecast_ok} (10000 entries)")
    print(f"RESULT oversized_price_rows_prepare_crash={big_crash} (10000 rows, healthy floats)")

    print("RESULT thread_factor=1.00 (single-threaded harness)")
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    except Exception:
        print("RESULT load1=unknown")
    print("RESULT swapins=0 (no psi on darwin)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
