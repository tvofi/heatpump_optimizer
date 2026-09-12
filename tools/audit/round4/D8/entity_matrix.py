#!/usr/bin/env python3
"""D8 — every entity of every platform, over the topology x feature matrix.

METRIC: for each cell (a coordinator configuration) and each entity built by
the real ``async_setup_entry``, the number of entity-cells violating each
publication contract, counted over the whole matrix.  One ``RESULT`` line per
violation class; a class with zero violations still prints, so the harness is
falsifiable in both directions.

COMMAND (from the export root, nothing else on the path):

    PYTHONPATH=tests/hastub:/tmp/d8pkgs \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D8/entity_matrix.py

  ``/tmp/d8pkgs`` holds orjson 3.12.0 (``pip install --target /tmp/d8pkgs
  orjson``).  Without it the harness falls back to an orjson-default-mode
  emulation and says so on ``RESULT orjson_mode``.  Measured on this baseline:
  the two modes agree on attrs_numpy / attrs_nan / attrs_unserialisable.  The
  ONE class the emulation cannot compute is ``attrs_recorded_over_16k`` (it
  needs real byte counts) -- it prints 0 in emulated mode because it is
  skipped, not because it passed.  Run with real orjson for that number.

  ``--tz`` is the control arm; ``--no-solve`` skips the optimizer solve.

EXPECTED (baseline 7dd68dd327fe3dbfb09f3bd0fe38910c58877697, 8-core Apple M1):
    cells=75  entities_per_cell=74  entity_cells=5550  (exact, no tolerance)
    entity_category_declared=1500
    default arm (naive stub clock):   timestamp_naive=75
    control arm (``--tz``):           timestamp_naive=0
    both arms, identical:
      state_write_raises=0, unknown_with_data=0,
      enum_state_not_in_options=0, enum_missing_options_attr=0,
      measurement_non_numeric=0, unit_device_class_mismatch=0,
      unit_without_device_class_unlisted=0, device_state_class_impossible=0,
      attrs_numpy=0, attrs_nan=0, attrs_unserialisable=0,
      state_string_over_255=0, attrs_recorded_over_16k=0,
      attrs_recorder_unserialisable=0,
      stale_between_cycles=0, stale_dict_source_undecided=542,
      never_alive_enabled_default=12, never_available_enabled_default=6
  With ``--no-solve`` the plan-fed entities publish nothing, so
  unknown_with_data=75 and never_alive_enabled_default=20 instead; that arm is
  for fast structural iteration, not for the numbers above.

All counts are integers over a deterministic, network-free construction; they
are contention-immune.  No timing is reported.
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

import asyncio  # noqa: E402
import datetime as _dt  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
from collections import defaultdict  # noqa: E402
from datetime import timedelta  # noqa: E402
from zoneinfo import ZoneInfo  # noqa: E402
from pathlib import Path  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np  # noqa: E402

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.components.sensor import (  # noqa: E402
    DEVICE_CLASS_STATE_CLASSES as _DCSC,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.util import dt as dt_util  # noqa: E402

from golden import START, coordinator_scenarios  # noqa: E402

from heatpump_optimizer import binary_sensor, button, climate, sensor, switch  # noqa: E402
from heatpump_optimizer import datetime as datetime_platform  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

try:  # the serializer Home Assistant really uses
    import orjson

    ORJSON_MODE = "real"
except ModuleNotFoundError:  # pragma: no cover - fallback path
    orjson = None
    ORJSON_MODE = "emulated"

ROOT = Path("custom_components/heatpump_optimizer")

#: ``--no-solve`` builds the payload without running the optimizer.  The
#: default runs a real solve per cycle, which is the only way the plan-fed
#: entities (narrative, score, advisors, schedule) have anything to publish.
SOLVE = "--no-solve" not in sys.argv

#: CONTROL ARM.  ``tests/hastub``'s ``dt_util.now()`` returns whatever
#: ``freeze()`` was given, and ``golden.START`` is a NAIVE datetime; real
#: Home Assistant's ``dt_util.now()`` is always tz-aware.  Every sensor whose
#: value is ``dt_util.now()`` therefore looks naive under the stub and is
#: tz-aware on an installation.  ``--tz`` freezes an AWARE clock instead, so
#: the ``timestamp_naive`` count under the two arms separates a real defect
#: from this stub gap: a class that goes to zero under ``--tz`` is the gap.
TZ_ARM = "--tz" in sys.argv

PLATFORMS = {
    "sensor": sensor,
    "binary_sensor": binary_sensor,
    "button": button,
    "climate": climate,
    "switch": switch,
    "datetime": datetime_platform,
}

# ---------------------------------------------------------------------------
# The matrix: 5 coordinator topologies x 14 feature overlays
# ---------------------------------------------------------------------------

FEATURE_OVERLAYS: dict[str, dict] = {
    "none": {},
    "dhw": {
        "dhw_enabled": True,
        "dhw_tank_volume": 200.0,
        "dhw_setpoint": 55.0,
        "dhw_min_temperature": 45.0,
        "dhw_windows": "06:00-08:30, 17:00-22:00",
        "dhw_temp_entity": "sensor.dhw_temp",
    },
    "two_zone": {
        "upper_floor_thermal_mass": 3.0,
        "lower_floor_thermal_mass": 8.0,
        "upper_floor_heat_loss": 0.08,
        "lower_floor_heat_loss": 0.07,
        "upper_floor_temp_entity": "sensor.upper",
        "lower_floor_temp_entity": "sensor.lower",
    },
    "valve_storage": {
        "mixing_valve_mode": "smart_write",
        "mixing_valve_write_entity": "number.valve_target",
        "buffer_tank_volume": 500.0,
        "buffer_tank_temp_entity": "sensor.buffer",
    },
    "two_tank": {
        "mixing_valve_mode": "smart_write",
        "mixing_valve_write_entity": "number.valve_target",
        "upper_floor_thermal_mass": 3.0,
        "lower_floor_thermal_mass": 8.0,
        "upper_floor_heat_loss": 0.08,
        "lower_floor_heat_loss": 0.07,
        "wood_tank_top_entity": "sensor.wood_top",
        "wood_tank_bottom_entity": "sensor.wood_bottom",
        "wood_tank_volume": 750.0,
        "topology_layout": "two_tank_4way",
    },
    "coil": {
        "dhw_enabled": True,
        "dhw_tank_volume": 200.0,
        "dhw_wood_coil_enabled": True,
        "wood_furnace_enabled": True,
        "wood_tank_top_entity": "sensor.wood_top",
        "wood_tank_bottom_entity": "sensor.wood_bottom",
    },
    "wood": {
        "wood_furnace_enabled": True,
        "wood_type": "birch",
        "wood_price_sek_m3": 1200.0,
        "wood_furnace_efficiency": 0.75,
        "wood_tank_top_entity": "sensor.wood_top",
        "wood_tank_bottom_entity": "sensor.wood_bottom",
        "wood_tank_volume": 750.0,
    },
    "ecl110": {
        "ecl110_state_topic": "ecl110/flow_temp_control/displace",
        "ecl110_displace_set_topic": "ecl110/flow_temp_control/displace/set",
        "ecl110_command_topic": "ecl110/command",
        "ecl110_displace_min": -20.0,
        "ecl110_displace_max": 20.0,
    },
    "pv": {
        "pv_enabled": True,
        "pv_peak_kw": 8.0,
        "pv_export_price": 0.3,
        "pv_production_entity": "sensor.pv_now",
    },
    "capacity_tariff": {
        "peak_tariff_enabled": True,
        "peak_tariff_price_per_kw": 45.0,
        "peak_tariff_peaks_averaged": 3,
        "peak_tariff_window_minutes": 60,
    },
    "grid_fee": {
        "grid_fee_mode": "rules",
        "grid_fee_rules": "Mon-Fri 06:00-22:00 = 0.25",
        "grid_fee_fixed": 0.05,
    },
    "tuya": {
        "heat_pump_mode_entity": "select.pump_mode",
        "heat_pump_defrost_entity": "binary_sensor.pump_defrost",
        "heat_pump_online_entity": "binary_sensor.pump_online",
        "heat_pump_fault_entity": "binary_sensor.pump_fault",
        "compressor_freq_entity": "number.pump_freq",
        "compressor_freq_sensor": "sensor.pump_freq",
    },
    "probes": {
        "heat_pump_power_entity": "sensor.pump_power",
        "heat_pump_energy_entity": "sensor.pump_energy",
        "house_power_entity": "sensor.house_power",
        "floor_return_temp_entity": "sensor.floor_return",
        "solar_radiation_entity": "sensor.solar_rad",
        "indoor_humidity_entity": "sensor.humidity",
        "buffer_tank_temp_entity": "sensor.buffer",
        "dhw_temp_entity": "sensor.dhw_temp",
    },
    "away": {
        "away_enabled": True,
        "away_presence_entity": "input_boolean.holiday",
        "away_temperature": 17.0,
        "away_dhw_min_temperature": 40.0,
    },
    "all": {},  # filled below: every overlay merged
}
_merged: dict = {}
for _name, _ov in FEATURE_OVERLAYS.items():
    if _name != "all":
        _merged.update(_ov)
FEATURE_OVERLAYS["all"] = _merged


def _clock(when):
    """The frozen instant, aware under the ``--tz`` control arm.

    Every injected timestamp goes through this too: an aware clock beside
    naive price timestamps makes the coordinator discard the whole price
    series ("No published prices cover the planning horizon") and the solve
    is skipped, which would make the control arm prove nothing.
    """
    return when.replace(tzinfo=ZoneInfo("Europe/Stockholm")) if TZ_ARM else when


def _prices(offset: float, spread: float) -> list[dict]:
    return [
        {
            "total": round(offset + spread * (h % 12) / 12.0, 4),
            "starts_at": (_clock(START) + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(48)
    ]


def _weather(base_t: float, slope: float) -> list[dict]:
    return [
        {
            "datetime": (_clock(START) + timedelta(hours=h)).isoformat(),
            "temperature": base_t + slope * (h % 24) / 24.0,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "humidity": 85.0,
        }
        for h in range(48)
    ]


def _solar(peak: float) -> list[float]:
    return [max(0.0, peak * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)]


class TrackingDict(dict):
    """A published payload that records which keys an entity actually read.

    This is how each entity is mapped to its source keys: not by a hand table
    that rots, but by hooking the dict the entity reads.  ``coordinator.data``
    is the single input every entity has.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.reads: set[str] = set()
        self.recording = False

    def get(self, key, default=None):
        if self.recording:
            self.reads.add(key)
        return super().get(key, default)

    def __getitem__(self, key):
        if self.recording:
            self.reads.add(key)
        return super().__getitem__(key)

    def __contains__(self, key):
        if self.recording:
            self.reads.add(key)
        return super().__contains__(key)


#: Every entity id an overlay names, with a plausible live reading, so the
#: freshness gates (``reading_ok``) see real inputs rather than a blind
#: install.  Cycle 2 rewrites each of these to the second value.
#: Units for the states whose readers demand one.  ``InputReader.read_power_kw``
#: refuses a state with no ``unit_of_measurement`` (``problem: unknown_unit``),
#: so without these the power, energy and irradiance probes read as configured
#: but unusable and every entity behind them is unavailable for a reason that
#: is the harness's, not the tree's.
STATE_UNITS: dict[str, str] = {
    "sensor.pump_power": "kW",
    "sensor.house_power": "kW",
    "sensor.pump_energy": "kWh",
    "sensor.solar_rad": "W/m²",
    "sensor.indoor": "°C",
    "sensor.outdoor": "°C",
    "sensor.dhw_temp": "°C",
    "sensor.upper": "°C",
    "sensor.lower": "°C",
    "sensor.buffer": "°C",
    "sensor.wood_top": "°C",
    "sensor.wood_bottom": "°C",
    "sensor.floor_return": "°C",
    "sensor.humidity": "%",
    "sensor.pv_now": "kW",
    "sensor.pump_freq": "Hz",
    "number.pump_freq": "Hz",
    "number.valve_target": "°C",
}

STATE_TABLE: dict[str, tuple[str, str]] = {
    "sensor.indoor": ("21.4", "19.8"),
    "sensor.outdoor": ("-3.0", "6.5"),
    "sensor.dhw_temp": ("52.0", "47.5"),
    "sensor.upper": ("21.1", "19.4"),
    "sensor.lower": ("20.6", "19.1"),
    "sensor.buffer": ("41.0", "36.0"),
    "sensor.wood_top": ("78.0", "52.0"),
    "sensor.wood_bottom": ("44.0", "31.0"),
    "sensor.pv_now": ("2.6", "0.4"),
    "sensor.pump_freq": ("48.0", "31.0"),
    "number.pump_freq": ("48.0", "31.0"),
    "number.valve_target": ("34.0", "29.0"),
    "select.pump_mode": ("heat", "hot_water"),
    "binary_sensor.pump_defrost": ("off", "on"),
    "binary_sensor.pump_online": ("on", "on"),
    "binary_sensor.pump_fault": ("off", "off"),
    "input_boolean.holiday": ("off", "on"),
    "sensor.pump_power": ("2.20", "0.85"),
    "sensor.pump_energy": ("1234.5", "1236.9"),
    "sensor.house_power": ("3.90", "2.10"),
    "sensor.floor_return": ("31.5", "27.0"),
    "sensor.solar_rad": ("180.0", "30.0"),
    "sensor.humidity": ("41.0", "48.0"),
}

BASE_INPUTS = {
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
}


def build_coordinator(config: dict):
    hass = FakeHass()
    cfg = {**BASE_INPUTS, **config}
    for eid, (first, _second) in STATE_TABLE.items():
        hass.states.set(eid, FakeState(first, unit=STATE_UNITS.get(eid)))
    entry = FakeEntry(data=cfg)
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    return hass, entry, coord


def run_cycle(
    coord,
    hass,
    *,
    offset: float,
    spread: float,
    base_t: float,
    peak: float,
    slot: int,
    solve: bool,
):
    """One full coordinator cycle: read inputs, solve, publish."""
    for eid, values in STATE_TABLE.items():
        hass.states.set(eid, FakeState(values[slot], unit=STATE_UNITS.get(eid)))
    coord._prices = _prices(offset, spread)
    coord._weather_forecast = _weather(base_t, 3.0)
    coord._solar_radiation_forecast = _solar(peak)
    asyncio.run(coord._update_current_state())
    coord._prices = _prices(offset, spread)
    coord._weather_forecast = _weather(base_t, 3.0)
    coord._solar_radiation_forecast = _solar(peak)
    coord._forecast_arrays()
    if solve:
        asyncio.run(coord.async_run_optimization())
    data = TrackingDict(coord._build_data_dict())
    coord.data = data
    return data


def collect(module, hass, entry, coord):
    added: list = []
    entry.runtime_data = coord
    asyncio.run(module.async_setup_entry(hass, entry, lambda e: added.extend(e)))
    return added


# ---------------------------------------------------------------------------
# Serialisation checks
# ---------------------------------------------------------------------------

_JSON_SCALARS = (str, int, float, bool, type(None))


def scan_value(value, path="", *, numpy=None, nan=None, other=None):
    """Walk a published attribute tree, collecting the three defect classes."""
    numpy = [] if numpy is None else numpy
    nan = [] if nan is None else nan
    other = [] if other is None else other
    if isinstance(value, (np.generic, np.ndarray)):
        numpy.append(path)
        return numpy, nan, other
    if isinstance(value, bool) or value is None:
        return numpy, nan, other
    if isinstance(value, float):
        if not math.isfinite(value):
            nan.append(path)
        return numpy, nan, other
    if isinstance(value, (int, str)):
        return numpy, nan, other
    if isinstance(value, dict):
        for k, v in value.items():
            if not isinstance(k, str):
                other.append(f"{path}[non-str key {k!r}]")
            scan_value(v, f"{path}.{k}", numpy=numpy, nan=nan, other=other)
        return numpy, nan, other
    if isinstance(value, (list, tuple)):
        for i, v in enumerate(value):
            scan_value(v, f"{path}[{i}]", numpy=numpy, nan=nan, other=other)
        return numpy, nan, other
    if isinstance(value, (_dt.datetime, _dt.date, _dt.time)):
        return numpy, nan, other
    other.append(f"{path}<{type(value).__name__}>")
    return numpy, nan, other


def orjson_ok(value) -> bool:
    if orjson is not None:
        try:
            orjson.dumps(value)
            return True
        except Exception:
            return False
    _, _, other = scan_value(value)
    numpy_hits, _, _ = scan_value(value)
    return not other and not numpy_hits


# ---------------------------------------------------------------------------
# Device-class / unit consistency, transcribed from Home Assistant's
# homeassistant/components/sensor/const.py DEVICE_CLASS_UNITS.
# Only the classes this integration uses are listed; an unlisted class is
# reported separately rather than silently passing.
# ---------------------------------------------------------------------------

DEVICE_CLASS_UNITS: dict[str, set | None] = {
    "temperature": {"°C", "°F", "K"},
    "power": {"W", "kW", "MW", "GW", "TW", "mW"},
    "energy": {"Wh", "kWh", "MWh", "GWh", "TWh", "J", "kJ", "MJ", "GJ", "cal",
               "kcal", "Mcal", "Gcal"},
    "monetary": None,  # any currency
    "irradiance": {"W/m²", "BTU/(h⋅ft²)"},
    "duration": {"d", "h", "min", "s", "ms", "µs"},
    "timestamp": set(),  # no unit at all
    "enum": set(),  # no unit at all
    "humidity": {"%"},
    "pressure": {"Pa", "hPa", "kPa", "bar", "cbar", "mbar", "mmHg", "inHg", "psi"},
    "frequency": {"Hz", "kHz", "MHz", "GHz"},
    "volume": {"L", "mL", "gal", "fl. oz.", "m³", "ft³", "CCF"},
    "water": {"L", "gal", "m³", "ft³", "CCF"},
    "battery": {"%"},
    "speed": {"ft/s", "in/d", "in/h", "in/s", "km/h", "kn", "m/s", "mph",
              "mm/d", "mm/s"},
    "current": {"A", "mA"},
    "voltage": {"V", "mV", "µV", "kV", "MV"},
    "energy_storage": {"Wh", "kWh", "MWh", "GWh", "TWh", "J", "kJ", "MJ", "GJ",
                       "cal", "kcal", "Mcal", "Gcal"},
    "volume_storage": {"L", "mL", "gal", "fl. oz.", "m³", "ft³", "CCF"},
}

#: Binary sensor device classes carry no unit at all (upstream has no
#: BinarySensorDeviceClass unit table); listed so they are not reported as
#: "unlisted" and so a unit on one is caught.
BINARY_DEVICE_CLASSES = {
    "battery", "battery_charging", "carbon_monoxide", "cold", "connectivity",
    "door", "garage_door", "gas", "heat", "light", "lock", "moisture",
    "motion", "moving", "occupancy", "opening", "plug", "power", "presence",
    "problem", "running", "safety", "smoke", "sound", "tamper", "update",
    "vibration", "window",
}


DEVICE_CLASS_STATE_CLASSES_STR = {
    str(k): {str(v) for v in vals}
    for k, vals in _DCSC.items()
}


def main() -> int:
    counts: dict[str, int] = defaultdict(int)
    detail: dict[str, list[str]] = defaultdict(list)
    alive: dict = {}
    seen: dict = {}
    cells = 0
    entities_per_cell: set[int] = set()
    entity_cells = 0

    scenarios = coordinator_scenarios()
    dt_util.freeze(_clock(START))
    try:
        for topo_name, topo_cfg in scenarios.items():
            for feat_name, overlay in FEATURE_OVERLAYS.items():
                cell = f"{topo_name}+{feat_name}"
                cfg = {**topo_cfg, **overlay}
                hass, entry, coord = build_coordinator(cfg)

                # --- cycle 1 ------------------------------------------------
                dt_util.freeze(_clock(START))
                data1 = run_cycle(
                    coord, hass, offset=0.6, spread=0.5, base_t=-5.0,
                    peak=200.0, slot=0, solve=SOLVE,
                )
                snap1: dict[tuple[str, str], dict] = {}
                built = 0
                for pname, module in PLATFORMS.items():
                    ents = collect(module, hass, entry, coord)
                    built += len(ents)
                    for ent in ents:
                        key = (pname, ident(ent))
                        snap1[key] = probe(ent, pname, data1)
                cells += 1
                entities_per_cell.add(built)
                entity_cells += built

                # --- cycle 2: materially different inputs, clock advanced ---
                dt_util.freeze(_clock(START + timedelta(hours=3)))
                data2 = run_cycle(
                    coord, hass, offset=1.9, spread=2.4, base_t=8.0,
                    peak=40.0, slot=1, solve=SOLVE,
                )
                snap2: dict[tuple[str, str], dict] = {}
                for pname, module in PLATFORMS.items():
                    for ent in collect(module, hass, entry, coord):
                        snap2[(pname, ident(ent))] = probe(ent, pname, data2)

                grade(cell, snap1, snap2, data1, data2, counts, detail, alive, seen)
    finally:
        dt_util.freeze(None)

    never_alive = sorted(
        f"{p}|{e}"
        for (p, e), n in alive.items()
        if n == 0 and seen[(p, e)]["enabled"]
    )
    never_available = sorted(
        f"{p}|{e}"
        for (p, e) in seen
        if seen[(p, e)]["available"] == 0 and seen[(p, e)]["enabled"]
    )
    detail["never_alive_enabled_default"] = never_alive
    detail["never_available_enabled_default"] = never_available
    counts["never_alive_enabled_default"] = len(never_alive)
    counts["never_available_enabled_default"] = len(never_available)

    print(f"# cells={cells} entities_per_cell={sorted(entities_per_cell)}")
    print(f"RESULT arm={'tz_aware' if TZ_ARM else 'naive_stub_clock'} arm")
    print(f"RESULT orjson_mode={ORJSON_MODE} mode")
    print(f"RESULT cells={cells} count")
    print(f"RESULT entities_per_cell={sorted(entities_per_cell)[0]} count")
    print(f"RESULT entity_cells={entity_cells} count")
    for name in (
        "state_write_raises",
        "entity_category_declared",
        "unknown_with_data",
        "enum_state_not_in_options",
        "enum_missing_options_attr",
        "measurement_non_numeric",
        "timestamp_naive",
        "unit_device_class_mismatch",
        "unit_without_device_class_unlisted",
        "device_state_class_impossible",
        "attrs_numpy",
        "attrs_nan",
        "attrs_unserialisable",
        "stale_between_cycles",
        "stale_dict_source_undecided",
        "state_string_over_255",
        "attrs_recorded_over_16k",
        "attrs_recorder_unserialisable",
        "never_alive_enabled_default",
        "never_available_enabled_default",
    ):
        print(f"RESULT {name}={counts[name]} entity_cells")

    arm = "tz" if TZ_ARM else "naive"
    out = Path(f"tools/audit/round4/D8/matrix_detail_{arm}.json")
    out.write_text(
        json.dumps(
            {k: sorted(set(v)) for k, v in detail.items()}, indent=1, sort_keys=True
        )
    )
    print(f"# detail written to {out}")
    # Harness contract (tools/audit/README.md): the three conditions lines.
    # This harness reports COUNTS only -- no wall, CPU or RSS number -- so the
    # thread factor cannot contaminate anything here; the pin is applied
    # anyway, above the numpy import, and stated so a reader need not infer it.
    import resource

    print("RESULT thread_factor=1.00 ratio")
    print("RESULT timing_results_reported=0 count")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap} count")
    print(f"RESULT load1={os.getloadavg()[0]:.2f} load")
    return 0


def ident(ent) -> str:
    return getattr(ent, "entity_id", None) or getattr(
        ent, "_attr_unique_id", type(ent).__name__
    )


def probe(ent, platform: str, data: TrackingDict) -> dict:
    """One entity's published surface plus the payload keys it read."""
    data.reads = set()
    data.recording = True
    try:
        if platform in ("sensor", "number"):
            value = ent.native_value
        elif platform == "binary_sensor":
            value = ent.is_on
        elif platform == "climate":
            value = ent.current_temperature
        elif platform == "switch":
            value = ent.is_on
        elif platform == "datetime":
            value = ent.native_value
        else:
            value = None
        reads = set(data.reads)
        try:
            attrs = ent.extra_state_attributes
        except Exception as exc:  # pragma: no cover
            attrs = {"__raised__": repr(exc)}
        try:
            available = bool(ent.available)
        except Exception:
            available = True
        state_error = None
        if platform == "sensor":
            try:
                ent.state
            except Exception as exc:
                state_error = f"{type(exc).__name__}: {exc}"
    finally:
        data.recording = False
    return {
        "value": value,
        "reads": reads,
        "attrs": attrs,
        "available": available,
        "cls": type(ent).__name__,
        # HARNESS TRAP, and the reason these are read from ``_attr_*`` and not
        # from the public property: ``tests/hastub``'s SensorEntity declares
        # NO ``device_class``, ``state_class`` or ``entity_category``
        # property.  ``getattr(ent, "device_class")`` therefore returns None
        # for every entity in the tree, and a check keyed on it counts zero
        # for a reason that has nothing to do with the code under test.
        "device_class": _str(
            getattr(ent, "device_class", None)
            if getattr(ent, "device_class", None) is not None
            else getattr(ent, "_attr_device_class", None)
        ),
        "state_class": _str(
            getattr(ent, "state_class", None)
            if getattr(ent, "state_class", None) is not None
            else getattr(ent, "_attr_state_class", None)
        ),
        "unit": getattr(ent, "native_unit_of_measurement", None),
        "options": getattr(ent, "options", None)
        or getattr(ent, "_attr_options", None),
        "translation_key": getattr(ent, "_attr_translation_key", None),
        "enabled_default": getattr(
            ent, "_attr_entity_registry_enabled_default", True
        ),
        "entity_category": _str(
            getattr(ent, "entity_category", None)
            if getattr(ent, "entity_category", None) is not None
            else getattr(ent, "_attr_entity_category", None)
        ),
        # The state write Home Assistant really performs: the stub mirrors
        # upstream's three refusals (unit on a non-numeric device class,
        # enum options without the enum device class, a state outside the
        # declared options), each of which raises on EVERY state write on a
        # real install.
        "state_error": state_error,
        "unrecorded": _unrecorded(type(ent)),
    }


def _unrecorded(cls) -> frozenset:
    """Home Assistant unions ``_unrecorded_attributes`` over the MRO."""
    out: set = set()
    for base in cls.__mro__:
        out |= set(getattr(base, "_unrecorded_attributes", None) or ())
    return frozenset(out)


def _str(v):
    return None if v is None else str(getattr(v, "value", v))


def _same(a, b) -> bool:
    try:
        return a == b or (
            isinstance(a, float)
            and isinstance(b, float)
            and math.isnan(a)
            and math.isnan(b)
        )
    except Exception:
        return repr(a) == repr(b)


def grade(cell, snap1, snap2, data1, data2, counts, detail, alive, seen) -> None:
    for key, p1 in snap1.items():
        platform, eid = key
        p2 = snap2.get(key, p1)
        tag = f"{cell}|{platform}|{eid}"

        # 1. unknown while its source data exists
        if p1["value"] is None and p1["available"]:
            live = [
                k
                for k in p1["reads"]
                if k in data1 and data1.get(k) not in (None, "", [], {})
            ]
            if live:
                counts["unknown_with_data"] += 1
                detail["unknown_with_data"].append(f"{tag} reads={sorted(live)}")

        # 1b. the state write Home Assistant performs raises
        if p1.get("state_error"):
            counts["state_write_raises"] += 1
            detail["state_write_raises"].append(f"{tag} {p1['state_error']}")

        # 1c. declared DIAGNOSTIC/CONFIG category, counted for the ordering half
        if p1["entity_category"] is not None:
            counts["entity_category_declared"] += 1

        # 2. ENUM
        if p1["device_class"] == "enum":
            opts = p1["options"]
            if not opts:
                counts["enum_missing_options_attr"] += 1
                detail["enum_missing_options_attr"].append(tag)
            elif p1["value"] is not None and p1["value"] not in opts:
                counts["enum_state_not_in_options"] += 1
                detail["enum_state_not_in_options"].append(
                    f"{tag} value={p1['value']!r} options={opts}"
                )

        # 3. MEASUREMENT must be numeric
        if p1["state_class"] == "measurement" and p1["value"] is not None:
            if isinstance(p1["value"], bool) or not isinstance(
                p1["value"], (int, float)
            ):
                counts["measurement_non_numeric"] += 1
                detail["measurement_non_numeric"].append(
                    f"{tag} value={p1['value']!r}"
                )

        # 4. TIMESTAMP must be tz-aware
        if p1["device_class"] == "timestamp" and p1["value"] is not None:
            v = p1["value"]
            if not isinstance(v, _dt.datetime) or v.tzinfo is None:
                counts["timestamp_naive"] += 1
                detail["timestamp_naive"].append(f"{tag} value={v!r}")

        # 5. unit consistent with device class
        dc, unit = p1["device_class"], p1["unit"]
        if dc is not None and platform == "binary_sensor":
            if dc not in BINARY_DEVICE_CLASSES:
                counts["unit_without_device_class_unlisted"] += 1
                detail["unit_without_device_class_unlisted"].append(f"{tag} dc={dc}")
            elif unit not in (None, ""):
                counts["unit_device_class_mismatch"] += 1
                detail["unit_device_class_mismatch"].append(
                    f"{tag} binary dc={dc} unit={unit!r} (must have none)"
                )
        elif dc is not None:
            allowed = DEVICE_CLASS_UNITS.get(dc, "UNLISTED")
            if allowed == "UNLISTED":
                counts["unit_without_device_class_unlisted"] += 1
                detail["unit_without_device_class_unlisted"].append(f"{tag} dc={dc}")
            elif allowed is not None:
                if allowed == set():
                    if unit not in (None, ""):
                        counts["unit_device_class_mismatch"] += 1
                        detail["unit_device_class_mismatch"].append(
                            f"{tag} dc={dc} unit={unit!r} (must have none)"
                        )
                elif unit not in allowed:
                    counts["unit_device_class_mismatch"] += 1
                    detail["unit_device_class_mismatch"].append(
                        f"{tag} dc={dc} unit={unit!r} allowed={sorted(allowed)}"
                    )

        # 5b. device class / state class pair, upstream's
        #     DEVICE_CLASS_STATE_CLASSES (the stub carries it verbatim).
        if dc is not None and p1["state_class"] is not None:
            allowed_sc = DEVICE_CLASS_STATE_CLASSES_STR.get(dc)
            if allowed_sc is not None and p1["state_class"] not in allowed_sc:
                counts["device_state_class_impossible"] += 1
                detail["device_state_class_impossible"].append(
                    f"{tag} dc={dc} sc={p1['state_class']} allowed={sorted(allowed_sc)}"
                )

        # 5c. the state STRING Home Assistant writes.  Upstream refuses a
        #     state longer than MAX_LENGTH_STATE_STATE (255) with
        #     InvalidStateError and the entity keeps its previous state.
        if isinstance(p1["value"], str) and len(p1["value"]) > 255:
            counts["state_string_over_255"] += 1
            detail["state_string_over_255"].append(
                f"{tag} len={len(p1['value'])}"
            )

        # 6. attributes serialisable
        attrs = p1["attrs"]
        if attrs is not None:
            npy, nan, other = scan_value(attrs, path=eid)
            if npy:
                counts["attrs_numpy"] += 1
                detail["attrs_numpy"].append(f"{tag} {npy[:3]}")
            if nan:
                counts["attrs_nan"] += 1
                detail["attrs_nan"].append(f"{tag} {nan[:3]}")
            if other or not orjson_ok(attrs):
                counts["attrs_unserialisable"] += 1
                detail["attrs_unserialisable"].append(f"{tag} {other[:3]}")
            # The recorder drops a state's attributes whole above
            # MAX_STATE_ATTRS_BYTES (16384) -- so the size that matters is
            # the one AFTER _unrecorded_attributes is removed.
            if orjson is not None and isinstance(attrs, dict):
                recorded = {
                    k: v for k, v in attrs.items() if k not in p1["unrecorded"]
                }
                try:
                    nbytes = len(orjson.dumps(recorded))
                except Exception:
                    nbytes = 0
                    counts["attrs_recorder_unserialisable"] += 1
                if nbytes > 16384:
                    counts["attrs_recorded_over_16k"] += 1
                    detail["attrs_recorded_over_16k"].append(f"{tag} {nbytes}B")

        # 7. staleness: value identical across two cycles while every payload
        #    key it read changed.  Both halves are required, so an entity that
        #    legitimately reads nothing volatile is not accused.
        read_keys = [k for k in p1["reads"] if k in data1 and k in data2]
        moved = [k for k in read_keys if not _same(data1.get(k), data2.get(k))]
        # A source key holding a dict or a list is NOT decisive: an entity
        # that summarises one field of a changed dict ("96 steps", a
        # recommended whole-degree setpoint) is honest when its own scalar
        # does not move.  Only an entity whose every source key is a SCALAR
        # that moved, and whose published value did not, is stale.
        scalar_sources = all(
            not isinstance(data1.get(k), (dict, list, tuple)) for k in read_keys
        )
        if (
            read_keys
            and moved
            and len(moved) == len(read_keys)
            and _same(p1["value"], p2["value"])
            and p1["value"] is not None
        ):
            if scalar_sources:
                counts["stale_between_cycles"] += 1
                detail["stale_between_cycles"].append(
                    f"{tag} value={p1['value']!r} moved={sorted(moved)}"
                )
            else:
                counts["stale_dict_source_undecided"] += 1
                detail["stale_dict_source_undecided"].append(
                    f"{tag} value={p1['value']!r} moved={sorted(moved)}"
                )

        # 8. an ENABLED-BY-DEFAULT entity that never had a value anywhere is
        #    aggregated by the caller; record the per-cell facts here.
        alive[(platform, eid)] = alive.get((platform, eid), 0) + (
            1 if (p1["available"] and p1["value"] is not None) else 0
        )
        seen[(platform, eid)] = {
            "n": seen.get((platform, eid), {}).get("n", 0) + 1,
            "enabled": p1["enabled_default"],
            "category": p1["entity_category"],
            "available": seen.get((platform, eid), {}).get("available", 0)
            + (1 if p1["available"] else 0),
        }


if __name__ == "__main__":
    raise SystemExit(main())
