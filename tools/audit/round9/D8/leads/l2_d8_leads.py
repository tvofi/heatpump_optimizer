#!/usr/bin/env python3
"""Leads seat L2, round 9: six D8 leads measured on the sensor/binary_sensor platforms.

METRIC (one line per section; every count keys on what the entity property RETURNS --
  native_value / is_on / available / entity_registry_enabled_default /
  extra_state_attributes -- after real coordinator cycles, never on the payload):
  A boost_off     arms (5 topologies x space/DHW boost, optimizer mode off) in which the
                  actuated action has heat_pump_on=True but Heat Pump Action reads off/idle,
                  or its power_kw / Recommended Power differ from commanded_power_kw(action).
                  Control: the same boosts at mode auto.
  B indoor_gate   sensor/binary_sensor entities available with a reading indoor thermometer
                  and unavailable once it stops reading, whose gate is NOT a measurement
                  gate (neither a _reading_key probe nor _MeasuredStoreMixin's "a store is
                  sensed"): plan, money or advisory values hidden with the thermometer.
  C heavy_day     no-hot-water topologies in which DHW Heavy Day Demand is available or
                  enabled by default.
  D valve_default cells with a throttling mixing-valve mode in which Valve Target
                  Recommendation publishes a value while its registry default is off; plus
                  cells without a valve in which it is available and unknown.
  E narrative     Home Assistant config languages for which the Plan Narrative sensor's
                  published `language` differs from the language HA is configured in
                  (a language the narrative has no table for must fall back to en).
  F solar_coords  decimal places of latitude/longitude on Solar Irradiance's state
                  attributes (recorded) against diagnostics.py's COORDINATE_PLACES.
RUN (export root):
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D8/leads/l2_d8_leads.py
  --perturb label        HeatPumpActionSensor.native_value reads the optimizer mode label
                         ('off' while mode is off)            -> A boost_off_mismatch goes UP
  --perturb gate         CurrentPowerSensor (Recommended Power).available also requires the indoor reading
                         -> B non_measured_hidden goes UP by 1 per topology
  --perturb valve        ValveTargetRecommendationSensor's default follows the valve mode
                         -> D valve_value_but_default_off goes to 0
  --perturb narrative    the coordinator's language read is pinned to "en" -> E goes UP
  --only ABCDEF          run only the named sections (default all)
EXPECTED at 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (exact, deterministic counts), measured:
  boost_off_arms=7 boost_off_mismatch=0 (control 0)      --perturb label     -> 7
  indoor_hidden_measured=20 non_measured_hidden=0        --perturb gate      -> 5
  no_dhw_topologies=3 heavy_day_on_no_dhw=0
  valve_value_but_default_off=5 valve_unknown_available_no_valve=5
                                                         --perturb valve     -> 0 (and 5)
  narrative_language_mismatch=0                          --perturb narrative -> 2
  solar_attr_coordinate_places=5 vs diagnostics_coordinate_places=1
  thread_factor 1.000, load1 0.98-1.94 during the leads fan-out.
MACHINE: leads box (4-core Linux container), CPython from /home/claude/venv314.
Clock frozen at golden.START + 3h05m. Substituted: Tibber/weather/solar fetchers
(injected series, the golden capture's way) and OpenMeteoSolar.async_refresh (no network).
Writes only HPO_PLANDATA under a tempfile.mkdtemp() root.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import asyncio
import logging
import sys
import tempfile
import time
from datetime import timedelta

sys.path[:0] = ["tests", "tests/hastub", "custom_components"]
logging.disable(logging.CRITICAL)
os.environ["HPO_PLANDATA"] = os.path.join(tempfile.mkdtemp(prefix="l2d8-"), "plandata")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from golden import START, coordinator_scenarios  # noqa: E402
from heatpump_optimizer import (  # noqa: E402
    binary_sensor, boost, const, diagnostics, mixing_valve, open_meteo, sensor,
)
from heatpump_optimizer import coordinator as cm  # noqa: E402
from heatpump_optimizer.entity import commanded_power_kw  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--perturb", choices=["label", "gate", "valve", "narrative"])
ap.add_argument("--only", default="ABCDEF", help="sections to run, e.g. --only B")
ARGS = ap.parse_args()
P0, T0 = time.process_time(), time.thread_time()

# ------------------------------------------------------------------ perturbations
if ARGS.perturb == "label":
    _orig_hpa = sensor.HeatPumpActionSensor.native_value.fget

    def _hpa(self):  # noqa: ANN001
        if self.coordinator.mode == const.MODE_OFF:
            return "off"
        return _orig_hpa(self)

    sensor.HeatPumpActionSensor.native_value = property(_hpa)
if ARGS.perturb == "gate":
    _orig_rp = sensor.CurrentPowerSensor.available.fget

    def _rp(self):  # noqa: ANN001
        return bool(_orig_rp(self) and sensor._reading_ok(self.coordinator, "upper_floor_temperature"))

    sensor.CurrentPowerSensor.available = property(_rp)
if ARGS.perturb == "valve":
    sensor.ValveTargetRecommendationSensor.entity_registry_enabled_default = property(
        lambda self: mixing_valve.is_throttling(self.coordinator._config.get("mixing_valve_mode")))
if ARGS.perturb == "narrative":
    _orig_view = cm.HeatPumpOptimizerCoordinator._narrative_view

    def _view(self):  # noqa: ANN001
        saved = self.hass.config.language
        self.hass.config.language = "en"
        try:
            return _orig_view(self)
        finally:
            self.hass.config.language = saved

    cm.HeatPumpOptimizerCoordinator._narrative_view = _view


async def _noop(*_a, **_k):
    return None


def _inject(coord, shift: float) -> None:
    coord._prices = [
        {"total": round(0.6 + shift + 0.5 * (h % 12) / 12.0, 4),
         "starts_at": (START + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
        for h in range(48)]
    coord._weather_forecast = [
        {"datetime": (START + timedelta(hours=h)).isoformat(),
         "temperature": -5.0 - 4 * shift + 3.0 * (h % 24) / 24.0,
         "wind_speed": 3.0, "precipitation": 0.0, "humidity": 85.0}
        for h in range(48)]
    coord._solar_radiation_forecast = [
        max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)]


def build(config: dict, indoor: str | None = "21.4", language: str = "en",
          keep_solar_fetch: bool = False):
    hass = FakeHass()
    hass.config.language = language
    cfg = dict(config)
    cfg[const.CONF_INDOOR_TEMP_ENTITY] = "sensor.indoor"
    cfg[const.CONF_OUTDOOR_TEMP_ENTITY] = "sensor.outdoor"
    hass.states.set("sensor.indoor", FakeState(indoor if indoor is not None else "unavailable"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    entry = FakeEntry(data=cfg)
    coord = cm.HeatPumpOptimizerCoordinator(hass, entry)
    coord._fetch_tibber_prices = _noop
    coord._fetch_weather_forecast = _noop
    if not keep_solar_fetch:
        coord._fetch_solar_forecast = _noop
    coord._async_learn_price_shape = _noop
    entry.runtime_data = coord
    ents: list = []
    asyncio.run(sensor.async_setup_entry(hass, entry, ents.extend))
    asyncio.run(binary_sensor.async_setup_entry(hass, entry, ents.extend))
    return hass, coord, ents


def cycle(coord, shift: float) -> None:
    async def run():
        _inject(coord, shift)
        coord.data = await coord._async_update_data()
        coord.last_update_success = True
    asyncio.run(run())


def enabled_default(e) -> bool:
    return bool(getattr(e, "entity_registry_enabled_default",
                        getattr(e, "_attr_entity_registry_enabled_default", True)))


def by_key(ents, key):
    return next(e for e in ents if getattr(e, "_attr_translation_key", "") == key)


SCEN = coordinator_scenarios()
dt_util.freeze(START + timedelta(hours=3, minutes=5))
try:
    # ---------------------------------------------------------------- A boost_off
    if "A" in ARGS.only:
        mism = ctrl = arms = 0
        for name, cfg in SCEN.items():
            hass, coord, ents = build(cfg)
            cycle(coord, 0.0)
            hpa, rp = by_key(ents, "heat_pump_action"), by_key(ents, "recommended_power")
            for channel in ("space", "dhw"):
                if channel == "dhw" and not coord.data.get("dhw_enabled"):
                    continue
                for mode in (const.MODE_OFF, const.MODE_AUTO):
                    coord._mode = mode
                    boost.held_for(coord).until.clear()
                    boost.held_for(coord).set(channel, True, dt_util.now())
                    cycle(coord, 0.3)
                    action = coord.data.get("current_action") or {}
                    want = commanded_power_kw(action)
                    attrs = hpa.extra_state_attributes or {}
                    bad = bool(action.get("heat_pump_on")) and (
                        hpa.native_value in ("off", "idle")
                        or attrs.get("power_kw") != want or rp.native_value != want)
                    print(f"# A {name} boost_{channel} mode={mode}: action.mode={action.get('mode')} "
                          f"on={action.get('heat_pump_on')} kW={want} -> HPA={hpa.native_value} "
                          f"power_kw={attrs.get('power_kw')} RP={rp.native_value}{'  MISMATCH' if bad else ''}")
                    if mode == const.MODE_OFF:
                        arms += 1
                        mism += bad
                    else:
                        ctrl += bad
                boost.held_for(coord).until.clear()
        print(f"RESULT boost_off_arms={arms} count")
        print(f"RESULT boost_off_mismatch={mism} count")
        print(f"RESULT boost_auto_control_mismatch={ctrl} count")

    # ---------------------------------------------------------------- B indoor_gate
    if "B" in ARGS.only:
        hidden_nonmeasured = hidden_measured = 0
        for name, cfg in SCEN.items():
            _, c1, e1 = build(cfg, indoor="21.4")
            cycle(c1, 0.0)
            _, c2, e2 = build(cfg, indoor=None)
            cycle(c2, 0.0)
            for a, b in zip(e1, e2):
                if a.available and not b.available:
                    # A measurement gate: the entity's own probe (_reading_key) or the
                    # thermal-battery "at least one store sensed" gate, whose value is
                    # derived from the measured stores and is fabricated without them.
                    measured = bool(getattr(type(b), "_reading_key", "")) or isinstance(
                        b, sensor._MeasuredStoreMixin)
                    print(f"# B {name}: hidden without indoor reading: {type(b).__name__} "
                          f"measured={measured}")
                    if measured:
                        hidden_measured += 1
                    else:
                        hidden_nonmeasured += 1
        print(f"RESULT indoor_hidden_measured={hidden_measured} count")
        print(f"RESULT non_measured_hidden={hidden_nonmeasured} count")

    # ---------------------------------------------------------------- C heavy_day
    if "C" in ARGS.only:
        heavy_on = no_dhw = 0
        for name, cfg in SCEN.items():
            _, coord, ents = build(cfg)
            cycle(coord, 0.0)
            if coord.data.get("dhw_enabled"):
                continue
            no_dhw += 1
            hd = next(e for e in ents if type(e).__name__ == "DHWHeavyDaySensor")
            print(f"# C {name}: available={hd.available} enabled_default={enabled_default(hd)}")
            heavy_on += bool(hd.available or enabled_default(hd))
        print(f"RESULT no_dhw_topologies={no_dhw} count")
        print(f"RESULT heavy_day_on_no_dhw={heavy_on} count")

    # ---------------------------------------------------------------- D valve_default
    if "D" in ARGS.only:
        valve_bad = unknown_avail = 0
        for name, cfg in SCEN.items():
            for arm in ("no_valve", "manual"):
                c = dict(cfg)
                if arm == "manual":
                    c.update({"mixing_valve_mode": mixing_valve.MODE_MANUAL,
                              "mixing_valve_target": 21.0})
                else:
                    c["mixing_valve_mode"] = mixing_valve.MODE_NONE
                _, coord, ents = build(c)
                cycle(coord, 0.0)
                vt = by_key(ents, "valve_target_recommendation")
                val, dflt, av = vt.native_value, enabled_default(vt), vt.available
                print(f"# D {name} {arm}: value={val} available={av} enabled_default={dflt} "
                      f"reason={(vt.extra_state_attributes or {}).get('reason')!r}")
                if arm == "manual" and val is not None and not dflt:
                    valve_bad += 1
                if arm == "no_valve" and av and val is None:
                    unknown_avail += 1
        print(f"RESULT valve_value_but_default_off={valve_bad} count")
        print(f"RESULT valve_unknown_available_no_valve={unknown_avail} count")

    # ---------------------------------------------------------------- E narrative
    if "E" in ARGS.only:
        lang_mism = 0
        for lang, want in (("en", "en"), ("sv", "sv"), ("sv-SE", "sv"), ("de", "en")):
            _, coord, ents = build(SCEN["coord_minimal"], language=lang)
            cycle(coord, 0.0)
            pn = by_key(ents, "plan_narrative")
            got = (pn.extra_state_attributes or {}).get("language")
            line = ((pn.extra_state_attributes or {}).get("lines") or [""])[0]
            print(f"# E hass.config.language={lang}: narrative language={got} (want {want}) first line={line!r}")
            lang_mism += got != want
        print(f"RESULT narrative_language_mismatch={lang_mism} count")

    # ---------------------------------------------------------------- F solar_coords
    if "F" in ARGS.only:
        async def _no_refresh(self, *_a, **_k):  # noqa: ANN001
            return None

        open_meteo.OpenMeteoSolar.async_refresh = _no_refresh
        hass, coord, ents = build({**SCEN["coord_minimal"],
                                   const.CONF_SOLAR_FORECAST_SOURCE: const.SOLAR_SOURCE_OPEN_METEO},
                                  keep_solar_fetch=True)
        hass.config.latitude, hass.config.longitude = 59.334591, 18.063240
        cycle(coord, 0.0)
        si = by_key(ents, "solar_irradiance")
        attrs = si.extra_state_attributes or {}
        lat = attrs.get("latitude")
        places = len(repr(lat).split(".")[1]) if isinstance(lat, float) else None
        unrec = "latitude" in getattr(si, "_unrecorded_attributes", frozenset())
        print(f"# F solar attrs latitude={lat} longitude={attrs.get('longitude')} unrecorded={unrec}; "
              f"hass.config.latitude={hass.config.latitude}")
        print(f"RESULT solar_attr_coordinate_places={places} places")
        print(f"RESULT diagnostics_coordinate_places={diagnostics.COORDINATE_PLACES} places")
finally:
    dt_util.freeze(None)

_p, _t = time.process_time() - P0, time.thread_time() - T0
print(f"RESULT thread_factor={(_p / _t) if _t > 0 else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    _sw = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")]
    print(f"RESULT swapins={_sw[0].split()[1] if _sw else 0}")
except OSError:
    print("RESULT swapins=na")
