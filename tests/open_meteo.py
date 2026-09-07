"""Tests for the Open-Meteo solar irradiance client.

Runs standalone: it stubs the small parts of Home Assistant that
``open_meteo.py`` imports, so no Home Assistant install or ``/tmp/hastub`` is
needed.

    python tests/open_meteo.py            # offline, fixture-driven
    HEATPUMP_LIVE=1 python tests/open_meteo.py   # also checks the real API

The live check exists because the one thing fixtures cannot catch is Open-Meteo
changing its response shape or its timestamp convention. It is opt-in so the
suite never fails because of someone's network.
"""
from __future__ import annotations

import asyncio
import importlib.util
import os
import sys
import types
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "custom_components", "heatpump_optimizer")


def _install_ha_stubs() -> None:
    """Minimal stand-ins for the third-party imports the module makes."""
    if "aiohttp" not in sys.modules:
        try:
            import aiohttp  # noqa: F401
        except ImportError:
            # Only referenced inside the network paths, which the offline
            # checks do not exercise. Stubbed so the pure parsing and
            # alignment logic can be tested without installing it.
            aiohttp_stub = types.ModuleType("aiohttp")

            class ClientTimeout:  # noqa: D401 - stub
                def __init__(self, total=None):
                    self.total = total

            class ClientSession:  # noqa: D401 - stub
                pass

            aiohttp_stub.ClientTimeout = ClientTimeout
            aiohttp_stub.ClientSession = ClientSession
            sys.modules["aiohttp"] = aiohttp_stub

    if "homeassistant" in sys.modules:
        return

    ha = types.ModuleType("homeassistant")
    ha.__path__ = []
    core = types.ModuleType("homeassistant.core")

    class HomeAssistant:  # noqa: D401 - stub
        """Placeholder; the client only stores the reference."""

    core.HomeAssistant = HomeAssistant

    helpers = types.ModuleType("homeassistant.helpers")
    helpers.__path__ = []
    aiohttp_client = types.ModuleType("homeassistant.helpers.aiohttp_client")
    aiohttp_client.async_get_clientsession = lambda hass: None

    sys.modules.update(
        {
            "homeassistant": ha,
            "homeassistant.core": core,
            "homeassistant.helpers": helpers,
            "homeassistant.helpers.aiohttp_client": aiohttp_client,
        }
    )


def _load_module():
    """Load open_meteo.py with its relative import of .const intact."""
    _install_ha_stubs()

    pkg = types.ModuleType("hpo")
    pkg.__path__ = [SRC]
    sys.modules["hpo"] = pkg

    for name in ("const", "open_meteo"):
        spec = importlib.util.spec_from_file_location(
            f"hpo.{name}", os.path.join(SRC, f"{name}.py")
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[f"hpo.{name}"] = module
        spec.loader.exec_module(module)

    return sys.modules["hpo.open_meteo"]


om = _load_module()

FAILS = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global FAILS
    print(("  ok   " if cond else "  FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        FAILS += 1


def approx(a, b, tol=1e-6) -> bool:
    return a is not None and abs(a - b) <= tol


UTC = timezone.utc


def block(start_hour: int, values, step_minutes: int = 60) -> dict:
    """Build an Open-Meteo style time block starting at ``start_hour``."""
    base = datetime(2026, 8, 21, start_hour, 0, tzinfo=UTC)
    times = [
        (base + timedelta(minutes=step_minutes * i)).strftime("%Y-%m-%dT%H:%M")
        for i in range(len(values))
    ]
    return {"time": times, "shortwave_radiation": list(values)}


print("== parsing ==")

hourly = om._parse_block(block(0, [0.0, 0.0, 100.0, 300.0, 500.0]), "shortwave_radiation")
check("parses an hourly block", len(hourly.times) == 5)
check("infers hourly resolution", hourly.resolution == timedelta(hours=1))
check(
    "times are timezone aware UTC",
    hourly.times[0] == datetime(2026, 8, 21, 0, 0, tzinfo=UTC),
)

quarter = om._parse_block(
    block(6, [10.0, 20.0, 30.0, 40.0], step_minutes=15), "shortwave_radiation"
)
check("infers 15 minute resolution", quarter.resolution == timedelta(minutes=15))

ten = om._parse_block(
    block(6, [60.0] * 6, step_minutes=10), "shortwave_radiation"
)
check("infers 10 minute resolution", ten.resolution == timedelta(minutes=10))

# Nulls are how Open-Meteo pads a model that has not run that far ahead, and how
# the satellite archive marks an unusable image. Treating them as 0.0 would read
# as darkness and suppress real solar gain.
nulled = om._parse_block(
    block(0, [100.0, None, 300.0, None, 500.0]), "shortwave_radiation"
)
check("drops null samples rather than zeroing them", len(nulled.times) == 3)
# A single missing sample must not double the inferred resolution, which would
# smear every value across twice its true span. Interleaved nulls genuinely
# cannot be recovered from, but Open-Meteo's nulls are trailing padding.
gapped = om._parse_block(
    {
        "time": [
            "2026-08-21T00:00",
            "2026-08-21T01:00",
            "2026-08-21T03:00",
            "2026-08-21T04:00",
        ],
        "shortwave_radiation": [100.0, 200.0, 400.0, 500.0],
    },
    "shortwave_radiation",
)
check("a single gap does not inflate resolution", gapped.resolution == timedelta(hours=1))

junk = om._parse_block(
    block(0, [100.0, -5.0, 99999.0, "abc", 400.0]), "shortwave_radiation"
)
check("rejects negative, absurd and non-numeric values", len(junk.times) == 2)

# A malformed `time` entry is the one bad field that is not a value: the skip
# has to cost its own sample and nothing else. Letting the ValueError out of
# _parse_block propagates through fetch() and discards the whole forecast --
# a usable block thrown away because one stamp in it was unreadable. (#251)
try:
    stamped = om._parse_block(
        {
            "time": [
                "2026-08-21T00:00",
                "2026-08-21T01:60",
                "2026-08-21T02:00",
                "2026-08-21T03:00",
            ],
            "shortwave_radiation": [100.0, 200.0, 300.0, 400.0],
        },
        "shortwave_radiation",
    )
    stamped_err = None
except Exception as _stamp_err:  # noqa: BLE001
    stamped, stamped_err = None, _stamp_err
check(
    "one malformed timestamp costs its own sample, not the whole block (#251)",
    stamped_err is None
    and stamped.values == (100.0, 300.0, 400.0)
    and stamped.resolution == timedelta(hours=1),
    f"raised {stamped_err!r}"
    if stamped_err is not None
    else f"got {stamped.values} at {stamped.resolution}",
)

check(
    "an unusable block yields an empty series",
    not om._parse_block({"time": ["2026-08-21T00:00"], "shortwave_radiation": [1.0]}, "shortwave_radiation"),
)
check("a missing block yields an empty series", not om._parse_block({}, "shortwave_radiation"))


print("\n== end-of-interval timestamp convention ==")

# Open-Meteo labels a sample with the END of its averaging window, so the value
# stamped 03:00 describes 02:00-03:00. Reading it as the start would shift every
# value one interval, which around sunrise is the difference between darkness
# and full sun.
conv = om._parse_block(block(0, [0.0, 0.0, 0.0, 400.0, 800.0]), "shortwave_radiation")
check(
    "value stamped 03:00 covers 02:00-03:00",
    approx(
        conv.mean_over(
            datetime(2026, 8, 21, 2, 0, tzinfo=UTC),
            datetime(2026, 8, 21, 3, 0, tzinfo=UTC),
        ),
        400.0,
    ),
)
check(
    "the preceding hour 01:00-02:00 is still dark",
    approx(
        conv.mean_over(
            datetime(2026, 8, 21, 1, 0, tzinfo=UTC),
            datetime(2026, 8, 21, 2, 0, tzinfo=UTC),
        ),
        0.0,
    ),
)
check(
    "series start is one resolution before the first stamp",
    conv.start == datetime(2026, 8, 20, 23, 0, tzinfo=UTC),
)


print("\n== resampling onto optimizer steps ==")

# An hourly series must answer a 15 minute question, because the optimizer's
# grid is 15 minutes regardless of what the API happens to publish.
check(
    "hourly series answers a 15 minute step",
    approx(
        conv.mean_over(
            datetime(2026, 8, 21, 2, 0, tzinfo=UTC),
            datetime(2026, 8, 21, 2, 15, tzinfo=UTC),
        ),
        400.0,
    ),
)

# A 10 minute observed series straddles 15 minute steps, so the result must be
# an overlap-weighted mean, not the nearest sample.
obs = om._parse_block(
    {
        "time": [
            "2026-08-21T10:00",
            "2026-08-21T10:10",
            "2026-08-21T10:20",
            "2026-08-21T10:30",
        ],
        "shortwave_radiation": [100.0, 200.0, 300.0, 400.0],
    },
    "shortwave_radiation",
)
# Step 10:00-10:15 overlaps the 10:10 sample (09:60-10:10 -> 10 min) and the
# 10:20 sample (10:10-10:20 -> 5 min): (200*10 + 300*5) / 15 = 233.33
check(
    "10 minute series is overlap-weighted onto a 15 minute step",
    approx(
        obs.mean_over(
            datetime(2026, 8, 21, 10, 0, tzinfo=UTC),
            datetime(2026, 8, 21, 10, 15, tzinfo=UTC),
        ),
        (200.0 * 10 + 300.0 * 5) / 15,
        1e-9,
    ),
)

check(
    "a window entirely outside the series returns None",
    obs.mean_over(
        datetime(2026, 8, 22, 10, 0, tzinfo=UTC),
        datetime(2026, 8, 22, 10, 15, tzinfo=UTC),
    )
    is None,
)
# Barely touching the end of the series must not pass as a covered answer.
check(
    "a barely-overlapping window returns None instead of a misleading value",
    obs.mean_over(
        datetime(2026, 8, 21, 10, 28, tzinfo=UTC),
        datetime(2026, 8, 21, 11, 28, tzinfo=UTC),
    )
    is None,
)
check("an inverted window returns None", obs.mean_over(
    datetime(2026, 8, 21, 10, 15, tzinfo=UTC),
    datetime(2026, 8, 21, 10, 0, tzinfo=UTC),
) is None)


print("\n== freshness ==")

now = datetime(2026, 8, 21, 10, 35, tzinfo=UTC)
check("latest_before picks the newest past sample", approx(obs.latest_before(now, timedelta(minutes=90)), 400.0))
check(
    "a stale series is rejected",
    obs.latest_before(datetime(2026, 8, 21, 23, 0, tzinfo=UTC), timedelta(minutes=90))
    is None,
)
check(
    "a sample whose interval has not finished is not treated as current",
    approx(
        obs.latest_before(datetime(2026, 8, 21, 10, 15, tzinfo=UTC), timedelta(minutes=90)),
        200.0,
    ),
)


print("\n== source precedence ==")

client = om.OpenMeteoSolar(hass=None, latitude=60.061, longitude=16.995)
check("a fresh client reports unavailable", not client.available)
check(
    "an unavailable client returns None rather than 0",
    client.irradiance_for(datetime(2026, 8, 21, 10, 0, tzinfo=UTC), timedelta(minutes=15))
    is None,
)

client._forecast = om._parse_block(
    {
        "time": [
            "2026-08-21T10:00",
            "2026-08-21T10:15",
            "2026-08-21T10:30",
            "2026-08-21T10:45",
            "2026-08-21T11:00",
        ],
        "shortwave_radiation": [500.0, 500.0, 500.0, 500.0, 500.0],
    },
    "shortwave_radiation",
)
check("forecast alone is used when there is no observation",
      approx(client.irradiance_for(datetime(2026, 8, 21, 10, 0, tzinfo=UTC), timedelta(minutes=15)), 500.0))

client._observed = obs
# Observation is measurement, forecast is prediction: for a step that already
# happened the measurement must win.
check(
    "observed satellite data overrides the forecast where both exist",
    approx(
        client.irradiance_for(datetime(2026, 8, 21, 10, 0, tzinfo=UTC), timedelta(minutes=15)),
        (200.0 * 10 + 300.0 * 5) / 15,
        1e-9,
    ),
)
check(
    "forecast still covers steps beyond the observed horizon",
    approx(client.irradiance_for(datetime(2026, 8, 21, 10, 30, tzinfo=UTC), timedelta(minutes=15)), 500.0),
)
check("current_irradiance prefers the newest observation", approx(client.current_irradiance(now), 400.0))
check("coordinate matching tolerates float noise", client.matches(60.0610000001, 16.995))
check("coordinate matching rejects a different place", not client.matches(59.0, 16.995))

d = client.diagnostics()
check("diagnostics report both series", d["forecast_points"] == 5 and d["observed_points"] == 4)


print("\n== small getters, and current_irradiance's forecast fallback ==")

# The three getters are asserted against three DISTINCT, non-default objects
# planted in the client's private state. Comparing a getter to the private
# attribute it reads pins nothing: __init__ assigns _forecast and _observed the
# SAME module-level `_EMPTY` singleton and _last_success `None`, so
# `client.forecast is client._forecast` is `_EMPTY is _EMPTY` and
# `client.last_success is client._last_success` is `None is None` -- both true
# whatever the property body returns. That is tests/README.md's "a test that
# cannot fail" class. Naming the OTHER series in each check is what makes a
# getter that returns the wrong series, or the untouched default, fail.
ident_client = om.OpenMeteoSolar(hass=None, latitude=3.0, longitude=4.0)
ident_forecast = om._parse_block(block(0, [0.0, 0.0, 0.0, 400.0, 800.0]), "shortwave_radiation")
ident_observed = om._parse_block(block(0, [11.0, 22.0, 33.0, 44.0, 55.0]), "shortwave_radiation")
ident_stamp = datetime(2026, 8, 21, 5, 0, tzinfo=UTC)
# A fixture precondition, deliberately an assert and not a check(): it guards
# the three checks below from silently degenerating back into tautologies if
# _parse_block ever starts returning the _EMPTY singleton here. It is not a
# check because no single-line production mutation can make it fail while
# leaving it reachable -- such a mutation aborts this script 250 lines earlier
# -- and a check whose firing cannot be demonstrated is the defect being fixed.
assert (
    ident_forecast is not ident_observed
    and ident_forecast is not om._EMPTY
    and ident_observed is not om._EMPTY
), "getter fixture degenerated: the planted series are not distinct"
ident_client._forecast = ident_forecast
ident_client._observed = ident_observed
ident_client._last_success = ident_stamp
check(
    "forecast property returns the forecast series, not the observed one",
    ident_client.forecast is ident_forecast and ident_client.forecast is not ident_observed,
    f"got {ident_client.forecast.values}",
)
check(
    "observed property returns the observed series, not the forecast one",
    ident_client.observed is ident_observed and ident_client.observed is not ident_forecast,
    f"got {ident_client.observed.values}",
)
check(
    "last_success property returns the recorded timestamp, not None",
    ident_client.last_success is ident_stamp,
    f"got {ident_client.last_success!r}",
)

getter_client = om.OpenMeteoSolar(hass=None, latitude=1.0, longitude=2.0)
getter_client._forecast = conv  # built above: hourly, 00:00-04:00, [0,0,0,400,800]
check(
    "current_irradiance falls back to the forecast when there is no observation",
    # now=04:00, 15 min lookback [03:45,04:00) sits entirely inside the
    # 03:00-04:00 sample (stamped 04:00, value 800.0) with full weight.
    approx(getter_client.current_irradiance(datetime(2026, 8, 21, 4, 0, tzinfo=UTC)), 800.0),
)


print("\n== _parse_block edges not reached above ==")

check(
    "latest_before returns None when no sample is at or before the moment asked",
    obs.latest_before(datetime(2026, 8, 21, 9, 0, tzinfo=UTC), timedelta(minutes=90)) is None,
)
check(
    "duplicate timestamps with no positive gap yield an empty series",
    not om._parse_block(
        {"time": ["2026-08-21T00:00", "2026-08-21T00:00"], "shortwave_radiation": [1.0, 2.0]},
        "shortwave_radiation",
    ),
)


print("\n== HTTP fetch layer (fake aiohttp session) ==")


class _FakeResponse:
    """Duck-types aiohttp's response as an async context manager."""

    def __init__(self, status=200, payload=None, json_exc=None):
        self.status = status
        self._payload = payload
        self._json_exc = json_exc

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def json(self, content_type=None):
        if self._json_exc is not None:
            raise self._json_exc
        return self._payload


class _FakeSession:
    """Pops one canned response (or raises a canned exception) per .get()."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append(url)
        item = self._responses.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item


def run(coro):
    return asyncio.run(coro)


fc = om.OpenMeteoSolar(hass=None, latitude=60.061, longitude=16.995)

check(
    "_get_json returns the parsed body on HTTP 200",
    run(fc._get_json(_FakeSession([_FakeResponse(200, {"hourly": {}})]), "http://x", {}))
    == {"hourly": {}},
)
check(
    # The body is byte-for-byte the one the 200 check above proves _get_json
    # ACCEPTS, so the status guard is the only thing left that can reject it.
    # With `_FakeResponse(500, None)` the None body trips the later non-dict
    # guard and this passes whether or not the status guard exists at all --
    # the 500 is then never what makes it fail.
    "_get_json returns None on a non-200 status carrying an otherwise-good body",
    run(fc._get_json(_FakeSession([_FakeResponse(500, {"hourly": {}})]), "http://x", {}))
    is None,
)
check(
    "_get_json swallows a transport exception rather than raising",
    run(fc._get_json(_FakeSession([ConnectionError("dns failure")]), "http://x", {})) is None,
)
check(
    "_get_json rejects a non-dict body",
    run(fc._get_json(_FakeSession([_FakeResponse(200, [1, 2, 3])]), "http://x", {})) is None,
)
check(
    "_get_json rejects a body carrying Open-Meteo's own error flag",
    run(
        fc._get_json(
            _FakeSession([_FakeResponse(200, {"error": True, "reason": "bad params"})]),
            "http://x",
            {},
        )
    )
    is None,
)

# _fetch_forecast: the request fails outright.
check(
    "_fetch_forecast returns the empty series when the request fails",
    not run(fc._fetch_forecast(_FakeSession([_FakeResponse(500, None)]))),
)

# _fetch_forecast: hourly block only (no minutely_15). The humidity (#21) and
# snowfall (#30) side series must land on the client from the SAME response
# even though the caller only asked for irradiance.
hourly_body = {
    "time": [f"2026-08-21T{h:02d}:00" for h in range(6)],
    "shortwave_radiation": [0.0, 0.0, 100.0, 300.0, 500.0, 400.0],
    "relative_humidity_2m": [80.0, 80.0, 75.0, 70.0, 65.0, 68.0],
    "snowfall": [0.0, 0.0, 0.0, 0.1, 0.0, 0.0],
}
fc2 = om.OpenMeteoSolar(hass=None, latitude=60.061, longitude=16.995)
hourly_series = run(fc2._fetch_forecast(_FakeSession([_FakeResponse(200, {"hourly": hourly_body})])))
check(
    "_fetch_forecast falls back to the hourly block with no minutely_15",
    len(hourly_series.times) == 6 and hourly_series.resolution == timedelta(hours=1),
)
check(
    "_fetch_forecast parses the humidity side series onto the client (#21)",
    len(fc2._humidity.times) == 6,
)
check(
    "_fetch_forecast parses the snowfall side series onto the client (#30)",
    len(fc2._snowfall.times) == 6,
)

# minutely_15 present and spanning close to the hourly block's own horizon:
# the finer series must win.
fine_times = [
    (datetime(2026, 8, 21, 0, 0, tzinfo=UTC) + timedelta(minutes=15 * i)).strftime(
        "%Y-%m-%dT%H:%M"
    )
    for i in range(24)
]
fc3 = om.OpenMeteoSolar(hass=None, latitude=60.061, longitude=16.995)
fine_series = run(
    fc3._fetch_forecast(
        _FakeSession(
            [
                _FakeResponse(
                    200,
                    {
                        "hourly": hourly_body,
                        "minutely_15": {"time": fine_times, "shortwave_radiation": [50.0] * 24},
                    },
                )
            ]
        )
    )
)
check(
    "_fetch_forecast prefers the 15 minute series when it spans the horizon",
    fine_series.resolution == timedelta(minutes=15),
)

# minutely_15 present but covering only the first 15 minutes of a 30 HOUR
# hourly horizon -- far short of "close to the end" -- so the hourly block,
# not the sparse fine one, must win.
hourly_times_long = [
    (datetime(2026, 8, 21, 0, 0, tzinfo=UTC) + timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M")
    for h in range(30)
]
hourly_body_long = {
    "time": hourly_times_long,
    "shortwave_radiation": [0.0] * 30,
    "relative_humidity_2m": [70.0] * 30,
    "snowfall": [0.0] * 30,
}
fc4 = om.OpenMeteoSolar(hass=None, latitude=60.061, longitude=16.995)
short_series = run(
    fc4._fetch_forecast(
        _FakeSession(
            [
                _FakeResponse(
                    200,
                    {
                        "hourly": hourly_body_long,
                        "minutely_15": {"time": fine_times[:2], "shortwave_radiation": [50.0, 60.0]},
                    },
                )
            ]
        )
    )
)
check(
    "_fetch_forecast falls back to hourly when the 15 minute series is too short",
    short_series.resolution == timedelta(hours=1),
)

# _fetch_observed: the request fails, and the happy path.
check(
    "_fetch_observed returns the empty series when the request fails",
    not run(fc._fetch_observed(_FakeSession([_FakeResponse(500, None)]))),
)
obs_series = run(fc._fetch_observed(_FakeSession([_FakeResponse(200, {"hourly": hourly_body})])))
check("_fetch_observed parses the satellite hourly block", len(obs_series.times) == 6)


print("\n== async_refresh orchestration ==")

_orig_get_session = om.async_get_clientsession


class _StubHass:
    pass


def _patch_session(fake):
    om.async_get_clientsession = lambda hass: fake


good_body = {"hourly": hourly_body}
now_refresh = datetime(2026, 8, 21, 12, 0, tzinfo=UTC)

# Both endpoints succeed: last_success is set and a pre-existing failure
# streak clears (the "recovered" log branch needs _failures already nonzero).
_patch_session(_FakeSession([_FakeResponse(200, good_body), _FakeResponse(200, good_body)]))
refresh_client = om.OpenMeteoSolar(hass=_StubHass(), latitude=60.061, longitude=16.995)
refresh_client._failures = 2
ok = run(refresh_client.async_refresh(now_refresh, force=True))
check(
    "a successful refresh reports available and clears a prior failure streak",
    ok is True and refresh_client._failures == 0 and refresh_client._last_success == now_refresh,
    f"available={ok} failures={refresh_client._failures} last_success={refresh_client._last_success}",
)

# Both endpoints fail, twice in a row: never raises, the previous series
# survives untouched, and the streak counts 1 then 2 (the first-failure
# warning and the subsequent-failure debug branches).
_patch_session(_FakeSession([_FakeResponse(500, None), _FakeResponse(500, None)]))
fail_client = om.OpenMeteoSolar(hass=_StubHass(), latitude=60.061, longitude=16.995)
fail_client._forecast = hourly_series  # simulate a previously successful refresh
first_ok = run(fail_client.async_refresh(now_refresh, force=True))
check(
    "a failed refresh does not raise and keeps the previous series",
    first_ok is True and fail_client._forecast is hourly_series and fail_client._failures == 1,
    f"ok={first_ok} failures={fail_client._failures}",
)
_patch_session(_FakeSession([_FakeResponse(500, None), _FakeResponse(500, None)]))
run(fail_client.async_refresh(now_refresh + timedelta(minutes=25), force=True))
check(
    "a second consecutive failure keeps counting rather than resetting",
    fail_client._failures == 2,
    str(fail_client._failures),
)

# Throttling: a call inside the minimum refresh interval, without force,
# must not touch the network at all.
_patch_session(_FakeSession([_FakeResponse(200, good_body), _FakeResponse(200, good_body)]))
throttle_client = om.OpenMeteoSolar(hass=_StubHass(), latitude=60.061, longitude=16.995)
run(throttle_client.async_refresh(now_refresh, force=True))
throttled_session = _FakeSession([])  # any .get() call here would IndexError
_patch_session(throttled_session)
throttle_result = run(throttle_client.async_refresh(now_refresh + timedelta(minutes=1), force=False))
check(
    "a refresh inside the minimum interval is skipped without touching the network",
    throttle_result is True and throttled_session.calls == [],
    f"result={throttle_result} calls={throttled_session.calls}",
)

om.async_get_clientsession = _orig_get_session


if os.environ.get("HEATPUMP_LIVE"):
    print("\n== live API ==")
    import json
    import ssl
    import urllib.parse
    import urllib.request

    # Home Assistant's aiohttp stack has a working trust store; a bare
    # python.org interpreter on macOS often does not, so use certifi's bundle
    # when it is available rather than disabling verification.
    try:
        import certifi

        ssl_context = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        ssl_context = ssl.create_default_context()

    lat, lon = 60.061, 16.995

    def q(params: dict) -> str:
        return "?" + urllib.parse.urlencode(params)

    # Each fetch is spelled with its production endpoint directly in the
    # request expression -- the live check must not be pointable anywhere
    # but the endpoints the module under test itself uses.
    with urllib.request.urlopen(
        om.OPEN_METEO_FORECAST_URL + q(
            {
                "latitude": lat,
                "longitude": lon,
                "minutely_15": "shortwave_radiation",
                "hourly": "shortwave_radiation",
                "daily": "sunrise,sunset",
                "timezone": "UTC",
                "forecast_days": 2,
            }
        ),
        timeout=20,
        context=ssl_context,
    ) as resp:
        fc = json.load(resp)
    fine = om._parse_block(fc.get("minutely_15", {}), "shortwave_radiation")
    coarse = om._parse_block(fc.get("hourly", {}), "shortwave_radiation")
    check("live forecast returns hourly data", bool(coarse))
    check("live forecast still offers 15 minute data", bool(fine))
    check("live 15 minute resolution is as expected", fine.resolution == timedelta(minutes=15))

    # Re-verify the timestamp convention against the sun itself: the first
    # non-zero sample must be the one whose interval contains sunrise.
    sunrise = datetime.fromisoformat(fc["daily"]["sunrise"][0]).replace(tzinfo=UTC)
    day = sunrise.date()
    first = next(
        (t for t, v in zip(coarse.times, coarse.values) if v > 0 and t.date() == day),
        None,
    )
    check("live data has daylight", first is not None)
    if first is not None:
        check(
            "timestamps still mark the END of the interval",
            first - timedelta(hours=1) <= sunrise <= first,
            f"sunrise={sunrise} first_nonzero={first}",
        )

    with urllib.request.urlopen(
        om.OPEN_METEO_SATELLITE_URL + q(
            {
                "latitude": lat,
                "longitude": lon,
                "hourly": "shortwave_radiation",
                "models": om.OPEN_METEO_SATELLITE_MODEL,
                "timezone": "UTC",
                "temporal_resolution": "native",
            }
        ),
        timeout=20,
        context=ssl_context,
    ) as resp:
        sat = json.load(resp)
    observed = om._parse_block(sat.get("hourly", {}), "shortwave_radiation")
    check("live satellite archive returns data", bool(observed))
    if observed:
        age = datetime.now(UTC) - observed.end
        check(
            "satellite archive is current enough to represent 'now'",
            age < timedelta(minutes=om.OPEN_METEO_OBSERVED_MAX_AGE_MINUTES),
            f"age={age}",
        )


print("\n" + ("%d CHECK(S) FAILED" % FAILS if FAILS else "ALL OPEN-METEO CHECKS PASSED"))
sys.exit(1 if FAILS else 0)
