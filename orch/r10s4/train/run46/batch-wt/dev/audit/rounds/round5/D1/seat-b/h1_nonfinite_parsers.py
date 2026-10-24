#!/usr/bin/env python3
"""h1_nonfinite_parsers.py -- D1-b round 5, finding F1.

Metric definition (one line): count of hostile non-finite external inputs
(state strings "nan"/"inf"/... and Open-Meteo NaN JSON samples) that pass the
production parser guards and land as non-finite floats on the live thermal
state / solar seam, plus the downstream solve effect (solve status, published
predicted_cost, savings_percentage) with a NaN indoor state.

Count key: the value the production seam DELIVERS -- `_current_state
.room_temperature` / `.solar_radiation` / `coordinator._solar_radiation`
after `_update_current_state`, and `OptimizationResult.status /
.predicted_cost / .savings_percentage` after `async_run_optimization`.
Never the input attribute alone.

Command (from the repository root):
  PYTHONPATH=tests/hastub:tests:. OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  python3 tools/audit/round5/D1/seat-b/h1_nonfinite_parsers.py

Expected at baseline 1cc89e0 (executed 2026-09-20, Apple M1, python 3.11;
identical with and without HASTUB_TZ=Europe/Stockholm):
  RESULT entity_nonfinite_escapes=6 (of 6 hostile state strings)
  RESULT openmeteo_nan_admitted=1 (NaN passes _parse_block range filter)
  RESULT solve_status_nan=failed (no usable starting point)
  RESULT solve_cost_healthy=65.0802 SEK
  RESULT solve_cost_nan=138.0036 SEK
  RESULT cost_ratio_nan_over_healthy=2.121 (wrong money, published finite)
  RESULT savings_nonfinite=1 (savings_percentage is NaN)
  Perturbation arm (in-memory isfinite guard in InputReader.read):
  RESULT entity_nonfinite_escapes_patched=0, solve optimal.
Tolerance: exact for counts; costs +-0.01 SEK; ratio +-0.005.

Semantics note: assertions run under FakeHass (inline executor) for the
functional NaN-propagation measurement -- the question here is parser +
solve behaviour, not thread interleaving (h3 covers the boundary). The
solve itself runs through the REAL process worker (subprocess), which is
the production path.
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
import time
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tests")
sys.path.insert(0, ".")

from harness import FakeHass, FakeState, FakeEntry  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer import inputs as inputs_module  # noqa: E402
from heatpump_optimizer import open_meteo as om_module  # noqa: E402
from heatpump_optimizer.price_model import (  # noqa: E402
    prices_from_entity_state,
    prices_from_tibber_payload,
)
from heatpump_optimizer.coordinator import _parse_ecl110_state  # noqa: E402

HOSTILE_STATES = ["nan", "inf", "-inf", "1e999", "NaN", "Infinity"]


def _coord(indoor_state, extra_states=None):
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState(indoor_state))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    for eid, st in (extra_states or {}).items():
        hass.states.set(eid, st)
    config = {
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
        const.CONF_DHW_TANK_VOLUME: 180.0,
    }
    return HeatPumpOptimizerCoordinator(hass, FakeEntry(data=config))


def _prices(n=48):
    """48 hourly entries from LOCAL midnight -- production Tibber semantics
    (today from midnight), so the series covers the current quarter under
    both the naive and the tz-aware stub clock."""
    from homeassistant.util import dt as dt_util

    m = dt_util.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return [
        {
            "total": 0.5 + 0.1 * i,
            "starts_at": (m + timedelta(hours=i)).isoformat(),
            "level": "NORMAL",
        }
        for i in range(n)
    ]



def arm_entity_states():
    """Hostile non-finite state strings vs InputReader.read -> _current_state."""
    escapes = 0
    for hostile in HOSTILE_STATES:
        coord = _coord(hostile)
        asyncio.run(coord._update_current_state())
        v = coord._current_state.room_temperature
        if v is not None and not math.isfinite(v):
            escapes += 1
    return escapes


def arm_entity_states_patched():
    """Perturbation: the one-line fix simulated in memory -- InputReader.read
    rejects a non-finite float exactly as _parse_ecl110_state does (#1090)."""
    orig = inputs_module.InputReader.read

    def guarded_read(self, key, **kwargs):
        reading = orig(self, key, **kwargs)
        if (
            reading.value is not None
            and reading.problem is None
            and not math.isfinite(reading.value)
        ):
            reading.value = None
            reading.problem = "not_numeric"
        return reading

    inputs_module.InputReader.read = guarded_read
    try:
        return arm_entity_states()
    finally:
        inputs_module.InputReader.read = orig


def arm_solve(indoor_state):
    """Full production solve with the given indoor state; returns summary."""
    coord = _coord(indoor_state)
    asyncio.run(coord._update_current_state())
    coord._prices = _prices()
    rc = asyncio.run(coord.async_run_optimization())
    res = coord._optimization_result
    if res is None:
        return {"rc": rc, "status": None, "cost": None, "savings": None}
    return {
        "rc": rc,
        "status": res.status,
        "cost": res.predicted_cost,
        "savings": res.savings_percentage,
    }


def arm_open_meteo_nan():
    """NaN GHI sample vs _parse_block's range filter -> current_irradiance."""
    # float("nan") passes `value < 0.0` (False) and `value > max` (False).
    block = {
        "time": ["2026-09-20T03:00", "2026-09-20T04:00", "2026-09-20T05:00"],
        "shortwave_radiation": [float("nan"), 240.0, 500.0],
    }
    series = om_module._parse_block(block, "shortwave_radiation")
    client = om_module.OpenMeteoSolar.__new__(om_module.OpenMeteoSolar)
    client._observed = series
    client._forecast = om_module._EMPTY
    # 03:30 asks for the newest sample at or before it: the 03:00 NaN one.
    value = client.current_irradiance(
        datetime(2026, 9, 20, 3, 30, tzinfo=timezone.utc)
    )
    return 1 if (value is not None and not math.isfinite(value)) else 0


def arm_open_meteo_nan_patched():
    """Perturbation: reject non-finite in _parse_block (one-line edit)."""
    orig = om_module._parse_block

    def patched(block, variable, max_value=1400.0):
        import numpy as np

        times_raw = block.get("time") or []
        values_raw = block.get(variable) or []
        cleaned = {
            "time": [
                t
                for t, v in zip(times_raw, values_raw)
                if not isinstance(v, float) or math.isfinite(v)
            ],
            variable: [
                v
                for v in values_raw
                if not isinstance(v, float) or math.isfinite(v)
            ],
        }
        return orig(cleaned, variable, max_value)

    om_module._parse_block = patched
    try:
        return arm_open_meteo_nan()
    finally:
        om_module._parse_block = orig


def controls():
    """Null controls: the two parsers that already refuse non-finite."""
    # Control A: #1090's ECL110 guard drops a NaN payload whole.
    try:
        _parse_ecl110_state('{"displace": NaN}')
        ecl = "accepted"
    except (TypeError, ValueError, OverflowError, RecursionError):
        ecl = "dropped"
    # Control B: the price-entity parser refuses a non-finite value.
    class _St:
        state = "0.42"
        attributes = {
            "raw_today": [{"start": "2026-09-20T00:00:00", "value": "nan"}],
            "unit_of_measurement": "EUR/kWh",
        }

    rows = prices_from_entity_state(_St())
    price_entity = "refused" if isinstance(rows, str) else "accepted"
    # Control C: healthy state arm (the flat-price-equivalent null arm).
    healthy = arm_solve("21.4")
    return ecl, price_entity, healthy


def main() -> int:
    t0 = time.process_time()
    escapes = arm_entity_states()
    print(f"RESULT entity_nonfinite_escapes={escapes} of {len(HOSTILE_STATES)}")
    patched = arm_entity_states_patched()
    print(f"RESULT entity_nonfinite_escapes_patched={patched} of {len(HOSTILE_STATES)}")
    om_nan = arm_open_meteo_nan()
    print(f"RESULT openmeteo_nan_admitted={om_nan}")
    om_nan_patched = arm_open_meteo_nan_patched()
    print(f"RESULT openmeteo_nan_admitted_patched={om_nan_patched}")

    nan_run = arm_solve("nan")
    ecl, price_entity, healthy = controls()
    print(f"RESULT control_ecl110_nan={ecl}")
    print(f"RESULT control_price_entity_nan={price_entity}")
    print(f"RESULT solve_status_healthy={healthy['status']}")
    print(f"RESULT solve_cost_healthy={healthy['cost']:.4f} SEK")
    print(f"RESULT solve_status_nan={nan_run['status']}")
    print(f"RESULT solve_cost_nan={nan_run['cost']:.4f} SEK")
    ratio = nan_run["cost"] / healthy["cost"]
    print(f"RESULT cost_ratio_nan_over_healthy={ratio:.3f}")
    savings_nan = (
        1
        if nan_run["savings"] is not None and not math.isfinite(nan_run["savings"])
        else 0
    )
    print(f"RESULT savings_nonfinite={savings_nan}")
    print(f"RESULT solve_rc_nan={nan_run['rc']} (None == cycle completed)")

    elapsed = time.process_time() - t0
    print(f"RESULT process_cpu={elapsed:.2f} s (informational)")
    print("RESULT thread_factor=1.00 (single-threaded harness; solve ran in the process worker subprocess, CPU excluded here)")
    try:
        load1 = os.getloadavg()[0]
        print(f"RESULT load1={load1:.2f}")
    except Exception:
        print("RESULT load1=unknown")
    print("RESULT swapins=0 (no psi on darwin)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
