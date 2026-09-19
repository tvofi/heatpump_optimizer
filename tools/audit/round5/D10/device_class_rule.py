#!/usr/bin/env python3
"""D10 round-5 — entity-device-class (Gold) rule instrument.

METRIC DEFINITION (one line): the count of sensor entities delivered by the
real `sensor.async_setup_entry` whose `unit_of_measurement` has exactly one
Home Assistant `SensorDeviceClass` (`DEVICE_CLASS_UNITS`) and whose
`device_class` is `None` — i.e. a device class is possible for the value and
is not set (the Gold rule "Entities use device classes where possible").

COMMAND (run from the repository root):
    PYTHONPATH=tests/hastub python3 tools/audit/round5/D10/device_class_rule.py

EXPECTED: RESULT sensors_missing_applicable_device_class=11 count (exactly);
RESULT sensors_total=59 count; RESULT sensors_with_device_class=32 count;
RESULT sensor_entities_missing_device_class=14 count (superset that also
counts the ambiguous-unit sensors). The offender list is printed beside the
line, keyed on each entity's `_attr_translation_key`.

INSTRUMENTED SYMBOL: custom_components/heatpump_optimizer/sensor.py:async_setup_entry
(the harness calls it and reads the entities it appends; `device_class` is the
stub's own `SensorEntity.device_class` property, not a private attribute).

PERTURBATION: add `_attr_device_class = SensorDeviceClass.MONETARY` to class
`PredictedCostSensor` in sensor.py (a one-line production edit) ->
sensors_missing_applicable_device_class falls 11 -> 10. Removing the device
class from `SpaceCostSensor` (which has monetary) makes it rise 11 -> 12. The
count keys on the delivered entity's `device_class`, which an honest fix
rewrites.

THE UNIT -> DEVICE CLASS MAP, stated rather than inferred, because the count
keys on it: only units that name exactly ONE HA `SensorDeviceClass` in
`homeassistant.components.sensor.const.DEVICE_CLASS_UNITS` are counted:
  °C -> temperature, kWh -> energy, kW -> power, Hz -> frequency,
  W/m² -> irradiance, L -> volume_storage,
and a unit shaped like an ISO-4217 code (`[A-Z]{3}`, e.g. SEK) -> monetary.
`%` is deliberately EXCLUDED (it maps to battery and to humidity and is
therefore not "possible" in the rule's sense) and so is `SEK/kWh` (a rate, not
a device-class unit). Both exclusions are visible in the reported totals.

BASELINE SHA: eaa2a06af16a1b5b006f58a0f36cc92131f80225 (origin/main, round 5).
MACHINE: 8-core Apple M1, 8 GB, macOS Darwin 25.6.0, Python 3.11.5.
"""
from __future__ import annotations

import os

for _v in (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import importlib  # noqa: E402
import pathlib  # noqa: E402
import re  # noqa: E402
import resource  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[4]

#: Units naming exactly one HA SensorDeviceClass, copied from
#: homeassistant/components/sensor/const.py:DEVICE_CLASS_UNITS. ISO-4217
#: currency codes are matched by shape (the integration's currency is config-
#: driven, `coordinator.currency`), everything else by exact unit.
UNIT_TO_CLASS = {
    "°C": "temperature",
    "kWh": "energy",
    "kW": "power",
    "Hz": "frequency",
    "W/m²": "irradiance",
    "L": "volume_storage",
}
CURRENCY = re.compile(r"[A-Z]{3}")


def device_class_possible(unit: str | None) -> str | None:
    if unit is None:
        return None
    if CURRENCY.fullmatch(unit):
        return "monetary"
    return UNIT_TO_CLASS.get(unit)


def unit_of(entity) -> str | None:
    for attr in ("unit_of_measurement", "_attr_native_unit_of_measurement",
                 "_attr_unit_of_measurement"):
        val = getattr(entity, attr, None)
        if val is not None:
            return val
    return None


def main() -> None:
    start_wall = time.time()
    sys.path.insert(0, str(ROOT / "tests"))
    # NOTE: tests/harness.py inserts "custom_components" at sys.path[0] on
    # import, so the package dir is chosen AFTER it, or it is shadowed.
    from harness import FakeCoordinator, FakeEntry, FakeHass
    # HPO_DC_PKG lets the perturbation arm run against an edited COPY of the
    # package, so a re-take does not write into the tree under measurement:
    #   cp -r custom_components/heatpump_optimizer $T/custom_components/  # edit copy
    #   HPO_DC_PKG=$T/custom_components PYTHONPATH=tests/hastub python3 <this>
    pkg = os.environ.get("HPO_DC_PKG", str(ROOT / "custom_components"))
    sys.path.insert(0, pkg)
    importlib.invalidate_caches()
    assert pathlib.Path(importlib.import_module("heatpump_optimizer").__file__).resolve().is_relative_to(
        pathlib.Path(pkg).resolve()
    ), "resolved package is not the one under test"

    coord = FakeCoordinator({})
    coord._month_totals = {"dhw": (41.5, 62.25), "space": (120.0, 180.0)}
    entry = FakeEntry()
    entry.runtime_data = coord

    mod = importlib.import_module("heatpump_optimizer.sensor")
    added: list = []
    asyncio.run(mod.async_setup_entry(FakeHass(), entry, added.extend))

    total = len(added)
    with_dc = 0
    missing_any = 0
    missing_applicable: list[tuple[str, str]] = []
    for e in added:
        dc = getattr(e, "device_class", None)
        unit = unit_of(e)
        if dc is not None:
            with_dc += 1
            continue
        if unit is None:
            continue
        missing_any += 1
        cls = device_class_possible(unit)
        if cls is not None:
            missing_applicable.append(
                (getattr(e, "_attr_translation_key", e.__class__.__name__), unit, cls)
            )

    n = len(missing_applicable)
    print(f"RESULT sensors_total={total} count")
    print(f"RESULT sensors_with_device_class={with_dc} count")
    print(f"RESULT sensor_entities_missing_device_class={missing_any} count")
    print(f"RESULT sensors_missing_applicable_device_class={n} count"
          f"  # unit maps to one HA SensorDeviceClass but device_class is None")
    for key, unit, cls in sorted(missing_applicable):
        print(f"       offender {key} unit={unit} -> {cls}")

    tf = 1.0
    try:
        tf = time.process_time() / max(time.thread_time(), 1e-9)
    except Exception:  # noqa: BLE001
        pass
    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = float("nan")
    print(f"RESULT thread_factor={tf:.4f} ratio")
    print(f"RESULT load1={load1:.3f} load")
    print(f"RESULT swapins={int(resource.getrusage(resource.RUSAGE_SELF).ru_majflt)} count")
    print(f"RESULT wall_s={time.time() - start_wall:.3f} s")


if __name__ == "__main__":
    main()
