#!/usr/bin/env python3
"""D1-s3-01: a malformed Open-Meteo `hourly` field (valid JSON, wrong shape)
crashes OpenMeteoSolar.async_refresh with an uncaught AttributeError, despite
its own docstring's contract "Never raises: a weather API being down must not
stop the optimizer". The exception then propagates out of
Coordinator._fetch_solar_forecast into _async_update_data's outer
`except Exception`, turning ONE malformed solar response into an UpdateFailed
for the WHOLE cycle (prices, weather, solve all skipped that poll) instead of
the documented graceful degrade-to-cached-irradiance.

Metric definition: cycles_crashed = count, out of N synthetic Open-Meteo
`hourly` payload shapes that are valid JSON (lists, strings, ints, nested
non-dict container -- the payload the reference API would send if it changed
its shape, or if a proxy/CDN mangled the body), for which
OpenMeteoSolar.async_refresh(...) raises instead of returning False/using
cached data.

Instrumented symbol:
  custom_components.heatpump_optimizer.open_meteo.OpenMeteoSolar.async_refresh
  (drives custom_components.heatpump_optimizer.open_meteo._parse_block via
  OpenMeteoSolar._fetch_forecast / _fetch_observed)

Perturbation: guard `_parse_block`'s two block-shape reads (or
`_fetch_forecast`/`_fetch_observed`) with `if not isinstance(block, dict):
return _EMPTY` (one line each site) -- under that fix crashed_count must fall
to 0 for the same payload set; expected direction: strictly decreases.

Null control: a HEALTHY hourly payload (dict, well-formed) run through the
same harness must NOT crash (control_crashed == 0), confirming the crash is a
consequence of the shape mismatch and not of harness plumbing.

Command:
  cd <tree-root> && PYTHONPATH=tests/hastub \
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
    python3 tools/audit/round8/D1/s3_openmeteo_hostile.py

Expected: RESULT cycles_crashed=5 count (>=1, tolerance 0 -- deterministic)
          RESULT control_crashed=0 count (tolerance 0)

Baseline SHA: cdf82daabcfe3777d98b31489f36df5555ec9d82
Machine: cloud 4-vCPU container (see BASELINE.md); this is a pure-Python
count, no timing, so it needs no load1/thread_factor.
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
import traceback
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from custom_components.heatpump_optimizer import open_meteo as om  # noqa: E402


class _FakeClock:
    def __init__(self, when):
        self._when = when


class _FakeResponse:
    def __init__(self, status, payload):
        self.status = status
        self._payload = payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def json(self, content_type=None):
        return self._payload


class _FakeSession:
    """One canned response per `.get(...)` call, in order."""

    def __init__(self, responses):
        self._responses = list(responses)

    def get(self, url, params=None, timeout=None):
        return self._responses.pop(0)


HEALTHY_HOURLY = {
    "time": [
        "2026-08-21T00:00",
        "2026-08-21T01:00",
        "2026-08-21T02:00",
    ],
    "shortwave_radiation": [0.0, 0.0, 100.0],
    "relative_humidity_2m": [80.0, 79.0, 78.0],
    "snowfall": [0.0, 0.0, 0.0],
}

# Hostile-but-valid-JSON shapes a real HTTP response can legally carry for the
# `hourly` key: a schema change, a proxy that flattens dicts to arrays, a
# truncated/garbled body that still parses as JSON, or an error body whose
# `error` flag itself got dropped by a caching layer.
HOSTILE_HOURLY_SHAPES = [
    [],                                   # array instead of object
    [1, 2, 3],                            # array of numbers
    "shortwave_radiation",                # bare string
    42,                                   # bare int
    {"time": "not-a-list", "shortwave_radiation": 5},  # dict but scalar fields
]


def _make_client():
    hass = object()  # never touched: async_get_clientsession is bypassed below
    client = om.OpenMeteoSolar(hass, 60.0, 24.0)
    return client


def run_case(hourly_value) -> tuple[bool, str]:
    """Returns (crashed, detail) for one hostile `hourly` payload, driven
    through the real async_refresh -> _fetch_forecast/_fetch_observed ->
    _get_json -> _parse_block seam, with the network call stubbed to hand
    back the hostile JSON body (parsing succeeded; aiohttp's own layer is not
    what we are testing)."""
    client = _make_client()

    # async_refresh calls async_get_clientsession(hass); patch the module
    # function it uses so no real HTTP happens.
    forecast_body = {"hourly": hourly_value, "minutely_15": {}}
    observed_body = {"hourly": hourly_value}
    session = _FakeSession(
        [_FakeResponse(200, forecast_body), _FakeResponse(200, observed_body)]
    )
    om.async_get_clientsession = lambda hass: session  # module-level patch point

    now = datetime(2026, 8, 21, 6, 0, tzinfo=timezone.utc)
    try:
        asyncio.run(client.async_refresh(now, force=True))
        return False, "ok"
    except Exception:  # noqa: BLE001 - this is exactly what we are counting
        return True, traceback.format_exc(limit=1).splitlines()[-1]


def main() -> None:
    crashed = 0
    for shape in HOSTILE_HOURLY_SHAPES:
        did_crash, detail = run_case(shape)
        tag = "CRASH" if did_crash else "ok"
        print(f"  shape={shape!r:40.40} -> {tag} ({detail})")
        if did_crash:
            crashed += 1

    control_crashed, control_detail = run_case(HEALTHY_HOURLY)
    control_crashed = 1 if control_crashed else 0
    print(f"  control(healthy) -> {'CRASH' if control_crashed else 'ok'} ({control_detail})")

    print(f"RESULT cycles_crashed={crashed} count")
    print(f"RESULT control_crashed={control_crashed} count")
    print(f"RESULT hostile_shapes_tried={len(HOSTILE_HOURLY_SHAPES)} count")


if __name__ == "__main__":
    main()
