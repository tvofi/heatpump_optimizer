"""D10-s2 gold rule diagnostics: Download diagnostics, driven with every option
that can hold a location, carries no part of a coordinate.

Arms (each a real coordinator after one input cycle, Open-Meteo solar on, so
the published solar_diagnostics carries the coordinate it requests for, and
the debug collection on holding one payload snapshot, so the bundle half is
in the download):
  options  - CONF_SOLAR_LOCATION set in entry.options
  data     - CONF_SOLAR_LOCATION set in entry.data
  home     - no solar location; hass.config's home coordinate is the fallback
  tracker  - home arm plus the away presence option on a device_tracker whose
             state carries latitude/longitude attributes
Metric: leaks = occurrences, in json.dumps of the returned payload, of the
coordinate's latitude or longitude written to 2 or more decimals (either
rounding), summed over the arms.
Key: the text of the payload async_get_config_entry_diagnostics returns.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D10/s2/diag_locations.py [--perturb]
Expected at baseline 92d38ecb: RESULT leaks=0 (each arm 0), exact.
--perturb empties diagnostics.TO_REDACT's location keys in memory (the
keyed pass then keeps them): leaks rises above 0.
Instrumented symbol: heatpump_optimizer.diagnostics:async_get_config_entry_diagnostics
Machine: local macOS box B2, Python 3.14 venv-ci.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _census as c  # noqa: E402
from harness import FakeState  # noqa: E402
from heatpump_optimizer import const, debugger, diagnostics  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from homeassistant.components import recorder as ha_recorder  # noqa: E402
from homeassistant.components.recorder import history as ha_history  # noqa: E402
from homeassistant.helpers import entity_registry as er  # noqa: E402
import types  # noqa: E402
from datetime import timedelta  # noqa: E402


def _state(value, at, attrs):
    return types.SimpleNamespace(state=value, attributes=dict(attrs), last_updated=at,
                                 last_reported=None)
from heatpump_optimizer.open_meteo import OpenMeteoSolar  # noqa: E402

TMP = __import__("tempfile").mkdtemp()
LAT, LON = 61.987654, 23.456789
NEEDLES = [f"{v:.{d}f}" for v in (LAT, LON) for d in (2, 3, 4, 5, 6)] + ["61.98", "23.45"]
LOC = {"latitude": LAT, "longitude": LON}

if "--perturb" in sys.argv:
    diagnostics.TO_REDACT = {k for k in diagnostics.TO_REDACT if k not in const.LOCATION_KEYS}


def run(arm):
    extra = {"solar_forecast_source": const.SOLAR_SOURCE_OPEN_METEO}
    states = {}
    if arm == "data":
        extra[const.CONF_SOLAR_LOCATION] = dict(LOC)
    if arm == "tracker":
        extra["away_enabled"] = True
        extra[const.CONF_AWAY_PRESENCE_ENTITY] = "device_tracker.phone"
        states["device_tracker.phone"] = FakeState("not_home", attributes={**LOC, "gps_accuracy": 12})
    hass, entry, coord = c.build(extra, states)
    if arm == "options":
        entry.options = {const.CONF_SOLAR_LOCATION: dict(LOC)}
    if arm in ("home", "tracker"):
        hass.config.latitude, hass.config.longitude = LAT, LON
    hass.config.path = lambda *parts: str(Path(TMP, *parts))
    coord._open_meteo = OpenMeteoSolar(hass, LAT, LON)
    coord.data = coord._build_data_dict()
    # The debug collection on, holding one payload snapshot of this cycle:
    # the bundle half of the download.
    collector = debugger.DebugCollector(hass, entry.entry_id, lambda coro: coro.close())
    debugger._COLLECTORS[coord] = collector
    collector.record(coord, coord.data, dt_util.utcnow())
    # The replay half: a recorder holding a day of the inputs' states and of
    # the Solar Irradiance sensor, whose attributes publish the coordinate
    # (sensor.SolarIrradianceSensor.extra_state_attributes).
    ha_recorder.install(hass)
    hass.config.time_zone = "UTC"
    entry.minor_version = 1
    now = dt_util.utcnow()
    solar_attrs = coord._open_meteo.diagnostics()
    er.async_get(hass).add("sensor.heat_pump_optimizer_solar_irradiance", unique_id="s",
                           config_entry_id=entry.entry_id, platform=const.DOMAIN)
    collector.started_at = now - timedelta(hours=13)
    hours = [now - timedelta(hours=h, minutes=1) for h in range(12, 0, -1)]
    ha_history.record(hass, "sensor.heat_pump_optimizer_solar_irradiance",
                      [_state("120", at, solar_attrs) for at in hours])
    ha_history.record(hass, "sensor.indoor", [_state("21.0", at, {"unit_of_measurement": "°C"})
                                              for at in hours])
    if arm == "tracker":
        ha_history.record(hass, "device_tracker.phone",
                          [_state("not_home", at, {**LOC, "gps_accuracy": 12}) for at in hours])
    payload = asyncio.run(diagnostics.async_get_config_entry_diagnostics(hass, entry))
    text = json.dumps(payload, default=str)
    seeded = json.dumps(coord.data, default=str)
    debug = payload.get("debug") or {}
    replay = (debug.get("manifest") or {}).get("replay")
    print(f"ARM {arm} replay manifest: {replay}; replay half present: {debug.get('replay') is not None}")
    return sum(text.count(n) for n in set(NEEDLES)), sum(seeded.count(n) for n in set(NEEDLES)), len(text)


total = 0
for arm in ("options", "data", "home", "tracker"):
    leaks, seeded, size = run(arm)
    total += leaks
    print(f"RESULT leaks_{arm}={leaks} count")
    print(f"RESULT seeded_{arm}={seeded} count")
    print(f"RESULT payload_bytes_{arm}={size} bytes")
print(f"RESULT leaks={total} count")
c.stats()
