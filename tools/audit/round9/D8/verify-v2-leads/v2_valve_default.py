#!/usr/bin/env python3
"""Verifier V2 (independent), D8-s3-61: ValveTargetRecommendationSensor's
registry default vs. whether the entity's value is actually gated by config.

METRIC: across the 5 golden coordinator_scenarios() topologies x the 4
mixing_valve modes (none, manual, smart_read, smart_write), the count of cells
where native_value is not None while entity_registry_enabled_default (a class
attribute, never a property in the baseline) is False -- the same claim as the
finder's, widened from 2 arms (no_valve/manual) to all 4 modes, and measured
directly off the class attribute rather than the instance property, to check
the finder did not miss a per-mode gate.
RUN (export root):
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D8/verify-v2-leads/v2_valve_default.py [--perturb]
EXPECTED at 1936d5ca72a06556eeed4e8e5bf3dea520e517e1: value_but_default_off=10
  (5 topologies x 2 throttling modes: manual, smart_write; smart_read does not
  set a target so is excluded by construction -- see RESULT rows), 0 for
  none/smart_read x 5 = 10 cells at value=None; --perturb -> 0.
Baseline SHA 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: this box (see
RESULT load1/thread_factor below).
Instrumented: heatpump_optimizer.sensor:ValveTargetRecommendationSensor
  (native_value, entity_registry_enabled_default) over
  heatpump_optimizer.mixing_valve:is_throttling.
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
os.environ["HPO_PLANDATA"] = os.path.join(tempfile.mkdtemp(prefix="v2d8-"), "plandata")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from golden import START, coordinator_scenarios  # noqa: E402
from heatpump_optimizer import const, mixing_valve, sensor  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--perturb", action="store_true")
ARGS = ap.parse_args()
P0, T0 = time.process_time(), time.thread_time()

if ARGS.perturb:
    sensor.ValveTargetRecommendationSensor.entity_registry_enabled_default = property(
        lambda self: mixing_valve.is_throttling(self.coordinator._config.get("mixing_valve_mode")))


async def _noop(*_a, **_k):
    return None


def _inject(coord) -> None:
    coord._prices = [
        {"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
         "starts_at": (START + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
        for h in range(48)]
    coord._weather_forecast = [
        {"datetime": (START + timedelta(hours=h)).isoformat(),
         "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
         "wind_speed": 3.0, "precipitation": 0.0, "humidity": 85.0}
        for h in range(48)]
    coord._solar_radiation_forecast = [
        max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)]


def build(config: dict):
    hass = FakeHass()
    cfg = dict(config)
    cfg[const.CONF_INDOOR_TEMP_ENTITY] = "sensor.indoor"
    cfg[const.CONF_OUTDOOR_TEMP_ENTITY] = "sensor.outdoor"
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    entry = FakeEntry(data=cfg)
    coord = cm.HeatPumpOptimizerCoordinator(hass, entry)
    coord._fetch_tibber_prices = _noop
    coord._fetch_weather_forecast = _noop
    coord._fetch_solar_forecast = _noop
    coord._async_learn_price_shape = _noop
    entry.runtime_data = coord
    ents: list = []
    asyncio.run(sensor.async_setup_entry(hass, entry, ents.extend))
    return coord, ents


def cycle(coord) -> None:
    async def run():
        _inject(coord)
        coord.data = await coord._async_update_data()
        coord.last_update_success = True
    asyncio.run(run())


def enabled_default(e) -> bool:
    return bool(getattr(e, "entity_registry_enabled_default",
                        getattr(e, "_attr_entity_registry_enabled_default", True)))


SCEN = coordinator_scenarios()
MODES = [mixing_valve.MODE_NONE, mixing_valve.MODE_MANUAL,
         mixing_valve.MODE_SMART_READ, mixing_valve.MODE_SMART_WRITE]
dt_util.freeze(START + timedelta(hours=3, minutes=5))
try:
    value_but_default_off = value_and_default_on = no_value_default_off_ok = 0
    per_mode = {m: [0, 0] for m in MODES}  # [has_value, no_value]
    for name, cfg in SCEN.items():
        for mode in MODES:
            c = dict(cfg)
            c["mixing_valve_mode"] = mode
            if mode != mixing_valve.MODE_NONE:
                c["mixing_valve_target"] = 21.0
                c["mixing_valve_read_entity"] = "sensor.valve_pos"
                c["mixing_valve_write_entity"] = "number.valve_target"
            coord, ents = build(c)
            cycle(coord)
            vt = next(e for e in ents if getattr(e, "_attr_translation_key", "") ==
                      "valve_target_recommendation")
            val, dflt = vt.native_value, enabled_default(vt)
            throttling = mixing_valve.is_throttling(mode)
            print(f"# mode={mode} topo={name}: value={val} enabled_default={dflt} "
                  f"is_throttling={throttling}")
            if val is not None:
                per_mode[mode][0] += 1
                if not dflt:
                    value_but_default_off += 1
                else:
                    value_and_default_on += 1
            else:
                per_mode[mode][1] += 1
                if not dflt:
                    no_value_default_off_ok += 1
    for m in MODES:
        print(f"RESULT mode_{m}_has_value={per_mode[m][0]} count")
        print(f"RESULT mode_{m}_no_value={per_mode[m][1]} count")
    print(f"RESULT value_but_default_off={value_but_default_off} count")
    print(f"RESULT value_and_default_on={value_and_default_on} count")
    print(f"RESULT no_value_default_off_ok={no_value_default_off_ok} count")
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
