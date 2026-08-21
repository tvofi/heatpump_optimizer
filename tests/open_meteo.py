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

    def get(url: str, params: dict) -> dict:
        full = url + "?" + urllib.parse.urlencode(params)
        with urllib.request.urlopen(full, timeout=20, context=ssl_context) as resp:
            return json.load(resp)

    fc = get(
        om.OPEN_METEO_FORECAST_URL,
        {
            "latitude": lat,
            "longitude": lon,
            "minutely_15": "shortwave_radiation",
            "hourly": "shortwave_radiation",
            "daily": "sunrise,sunset",
            "timezone": "UTC",
            "forecast_days": 2,
        },
    )
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

    sat = get(
        om.OPEN_METEO_SATELLITE_URL,
        {
            "latitude": lat,
            "longitude": lon,
            "hourly": "shortwave_radiation",
            "models": om.OPEN_METEO_SATELLITE_MODEL,
            "timezone": "UTC",
            "temporal_resolution": "native",
        },
    )
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
