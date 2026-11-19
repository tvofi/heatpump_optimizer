#!/usr/bin/env python3
"""D8.M5 (round 11, seat D8-s3): the entity matrix, graduated to test shape.

Metric: per violation class, the count of (cell, cycle, entity) triples breaking it, over every
entity every platform's real async_setup_entry builds (sensor, binary_sensor, button, switch,
climate, datetime) in each tests/golden.py:coordinator_scenarios() topology plus an
all-inputs-lit cell, across two cycles whose prices and forecasts differ. Deterministic (clock
frozen at golden.START by the fixtures, no network): the harness runs the matrix twice and
prints matrix_nondeterministic, the count of triples whose published (state, attributes)
differed between the two identical runs. Key: the value the entity publishes (native_value /
is_on / state, extra_state_attributes), never the payload.
Classes: measurement_non_numeric, timestamp_naive, enum_off_list, unit_on_non_numeric_class,
state_class_impossible, not_json_serialisable (numpy scalar, NaN/inf, unknown type),
stale_between_cycles (a sensor whose source key moved but the state did not) -- the last is
informational: the payload-key map is not derivable for every sensor, so it counts only
sensors whose own _payload_path exists in both cycles' data.
Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D8/s3/m5_matrix.py [--perturb numpy|accum-total-increasing]
Measured at baseline 92d38ecb64: state_class_impossible=36 (3 energy accumulators x 6 cells x 2 cycles),
every other class 0, matrix_nondeterministic 0, exact. --perturb accum-total-increasing sets
sensor:_AccumulatingSensor._attr_state_class TOTAL_INCREASING in memory -> state_class_impossible to 0.
Perturbation: --perturb numpy wraps sensor.HeatPumpOptimizerSensorBase's published native_value
in numpy.float64 for float states after the base class's scrub (in memory) ->
not_json_serialisable up.
Machine: macOS arm64 local seat.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, json, math, sys, time
from datetime import date, datetime, timedelta
from enum import Enum
sys.path[:0] = ["tests", "custom_components"]
_p0, _t0 = time.process_time(), time.thread_time()

import numpy as np  # noqa: E402
from golden import START, coordinator_scenarios  # noqa: E402
from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.components.sensor import (  # noqa: E402
    DEVICE_CLASS_STATE_CLASSES, NON_NUMERIC_DEVICE_CLASSES, SensorDeviceClass, SensorStateClass)
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer import sensor, binary_sensor, button, switch, climate  # noqa: E402
from heatpump_optimizer import datetime as dt_mod  # noqa: E402

PLATFORMS = (sensor, binary_sensor, button, switch, climate, dt_mod)
CLASSES = ("measurement_non_numeric", "timestamp_naive", "enum_off_list",
           "unit_on_non_numeric_class", "state_class_impossible", "not_json_serialisable",
           "property_raised", "stale_between_cycles")


def cells():
    c = dict(coordinator_scenarios())
    c["coord_all_inputs_lit"] = {
        **c["coord_all_features"],
        "dhw_temp_entity": "sensor.tank", "lower_floor_temp_entity": "sensor.lower",
        "floor_return_temp_entity": "sensor.ret", "buffer_tank_temp_entity": "sensor.buf",
        "mixing_valve_mode": "manual",
    }
    return c


def inject(coord, shift):
    coord._prices = [{"total": round(0.6 + shift + 0.5 * ((h + int(shift * 10)) % 12) / 12.0, 4),
                      "starts_at": (START + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
                     for h in range(48)]
    coord._weather_forecast = [{"datetime": (START + timedelta(hours=h)).isoformat(),
                                "temperature": -5.0 - 4 * shift + 3.0 * (h % 24) / 24.0,
                                "wind_speed": 3.0, "precipitation": 0.0, "humidity": 85.0}
                               for h in range(48)]
    coord._solar_radiation_forecast = [max(0.0, (200.0 + 100 * shift) * (1 - abs(12 - (h % 24)) / 12.0))
                                       for h in range(48)]
    coord.data = coord._build_data_dict()


def build(config):
    hass = FakeHass()
    entry = FakeEntry(data=config)
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    inject(coord, 0.0)
    entry.runtime_data = coord
    out = []
    for mod in PLATFORMS:
        def add(ents, _o=out):
            for e in ents:
                e.hass = hass
            _o.extend(ents)
        asyncio.run(mod.async_setup_entry(hass, entry, add))
    return coord, out


def bad_json(v, path="v"):
    """First non-orjson-clean leaf, or None. orjson rejects numpy scalars and NaN/inf."""
    if v is None or isinstance(v, (bool, str)):
        return None
    if isinstance(v, (np.generic, np.ndarray)):
        return f"{path}:{type(v).__name__}"
    if isinstance(v, int):
        return None
    if isinstance(v, float):
        return None if math.isfinite(v) else f"{path}:nonfinite"
    if isinstance(v, (datetime, date, Enum)):
        return None
    if isinstance(v, dict):
        for k, x in v.items():
            r = bad_json(x, f"{path}.{k}")
            if r:
                return r
        return None
    if isinstance(v, (list, tuple)):
        for i, x in enumerate(v):
            r = bad_json(x, f"{path}[{i}]")
            if r:
                return r
        return None
    return f"{path}:{type(v).__name__}"


def state_of(e):
    for attr in ("native_value", "is_on", "current_temperature", "native_value"):
        if hasattr(type(e), attr) or hasattr(e, attr):
            try:
                return getattr(e, attr)
            except Exception as exc:  # noqa: BLE001
                raise RuntimeError(f"{attr}: {exc!r}")
    return None


def publish(e):
    st = state_of(e)
    attrs = getattr(e, "extra_state_attributes", None)
    return st, attrs


def check(e, st, attrs, viol, tag):
    dc = getattr(e, "device_class", None)
    sc = getattr(e, "state_class", getattr(e, "_attr_state_class", None))
    unit = getattr(e, "native_unit_of_measurement", getattr(e, "_attr_native_unit_of_measurement", None))
    eid = e.entity_id
    if e.entity_id.startswith("sensor."):
        if sc in (SensorStateClass.MEASUREMENT, SensorStateClass.TOTAL, SensorStateClass.TOTAL_INCREASING) \
                and st is not None and (isinstance(st, bool) or not isinstance(st, (int, float))):
            viol["measurement_non_numeric"].append(f"{tag} {eid}={st!r}")
        if dc in (SensorDeviceClass.TIMESTAMP,) and st is not None and \
                (not isinstance(st, datetime) or st.tzinfo is None):
            viol["timestamp_naive"].append(f"{tag} {eid}={st!r}")
        if dc in (SensorDeviceClass.ENUM,) and st is not None:
            opts = getattr(e, "options", getattr(e, "_attr_options", None)) or []
            if st not in opts:
                viol["enum_off_list"].append(f"{tag} {eid}={st!r}")
        if dc in NON_NUMERIC_DEVICE_CLASSES and unit is not None:
            viol["unit_on_non_numeric_class"].append(f"{tag} {eid} unit={unit}")
        if sc is not None and dc in DEVICE_CLASS_STATE_CLASSES and sc not in DEVICE_CLASS_STATE_CLASSES[dc]:
            viol["state_class_impossible"].append(f"{tag} {eid} {dc}/{sc}")
    b = bad_json(st, "state") or bad_json(attrs, "attrs")
    if b:
        viol["not_json_serialisable"].append(f"{tag} {eid} {b}")


def dig(d, path):
    for k in path:
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return d


def run_matrix():
    viol = {c: [] for c in CLASSES}
    pubs = {}
    triples = 0
    for name, cfg in cells().items():
        coord, ents = build(cfg)
        snap = {}
        for cycle, shift in ((1, 0.0), (2, 0.3)):
            if cycle == 2:
                inject(coord, shift)
            for e in ents:
                tag = f"{name}/c{cycle}"
                triples += 1
                try:
                    st, attrs = publish(e)
                except Exception as exc:  # noqa: BLE001
                    viol["property_raised"].append(f"{tag} {e.entity_id} {exc!r}")
                    continue
                check(e, st, attrs, viol, tag)
                pubs[(name, cycle, e.entity_id)] = repr((st, attrs))
                path = getattr(e, "_payload_path", None)
                if path:
                    snap.setdefault(e.entity_id, []).append((dig(coord.data, path), st))
        for eid, pairs in snap.items():
            if len(pairs) == 2:
                (s1, v1), (s2, v2) = pairs
                if isinstance(s1, (int, float)) and isinstance(s2, (int, float)) and s1 != s2 and v1 == v2:
                    viol["stale_between_cycles"].append(f"{name} {eid} src {s1}->{s2} state {v1}")
    return viol, pubs, triples


def main():
    if "--perturb" in sys.argv and sys.argv[sys.argv.index("--perturb") + 1] == "numpy":
        base = sensor.HeatPumpOptimizerSensorBase
        # Wrap every concrete sensor's native_value read after the scrub.
        import heatpump_optimizer.sensor as smod
        for nm in dir(smod):
            cls = getattr(smod, nm)
            if isinstance(cls, type) and issubclass(cls, base) and isinstance(
                    getattr(cls, "native_value", None), property):
                p = cls.native_value

                def _wrap(self, _p=p):
                    v = _p.fget(self)
                    return np.float64(v) if isinstance(v, float) else v
                cls.native_value = property(_wrap)
    if "--perturb" in sys.argv and sys.argv[sys.argv.index("--perturb") + 1] == "accum-total-increasing":
        # One-line production edit, in memory: the accumulator base's declared state class.
        sensor._AccumulatingSensor._attr_state_class = SensorStateClass.TOTAL_INCREASING
    v1, p1, n = run_matrix()
    v2, p2, _ = run_matrix()
    nondet = sum(1 for k in p1 if p1.get(k) != p2.get(k)) + len(set(p2) ^ set(p1))
    for c in CLASSES:
        for line in v1[c][:15]:
            print(f"VIOLATION {c} {line}")
    print(f"RESULT triples={n} count")
    for c in CLASSES:
        print(f"RESULT {c}={len(v1[c])} count")
    print(f"RESULT matrix_nondeterministic={nondet} count")
    tc = time.thread_time() - _t0
    print(f"RESULT thread_factor={(time.process_time() - _p0) / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


main()
