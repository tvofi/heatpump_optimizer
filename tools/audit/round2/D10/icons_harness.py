#!/usr/bin/env python3
"""Icon translations: the D10-13 numbers, before and after the fix (#189).

What it measures (one line each; every number is an exact count, tolerance 0):

  attr_icon_assignments   ``_attr_icon`` assignments in the four entity
                          platform files, by AST                       [D10-13]
  attr_icon_static        of those, string-literal class attributes
                          (the movable kind)                           [D10-13]
  attr_icon_dynamic       of those, computed or instance-level (the kind
                          that must stay in code)                      [D10-13]
  icons_json_exists       1 if custom_components/heatpump_optimizer/
                          icons.json exists                            [D10-13]
  icons_json_entries      entity-icon entries in icons.json, summed over
                          platforms                                    [D10-13]
  device_class_duplicates static icons exactly equal to the entity's
                          device-class default (removed, not ported -- the
                          quality-scale rule forbids overriding the device
                          class in the same context)                   [D10-13]
  device_class_rendered   entities with neither an ``_attr_icon`` nor a
                          registry entry whose device class renders the
                          icon anyway (the after-state of the four
                          duplicates above)                            [D10-13]
  entities_rendering_icon translation-keyed entity classes that still
                          render an icon, over all of them -- via
                          ``_attr_icon`` at the baseline, via the registry
                          or a device-class default after; this not moving
                          is the null control: the fix changes WHERE the
                          icons live, not how many entities have one  [D10-13]
  registry_coverage       registry entries over the movable roster (all
                          translation-keyed classes minus the ones leaning
                          on a device-class default)                    [D10-13]

Command, from the repository root:

    PYTHONPATH=tests/hastub python tools/audit/round2/D10/icons_harness.py

``HPO_ICONS_PACKAGE=<dir>`` re-points the harness at another copy of the
package (the baseline is materialised with ``git archive`` this way).

Instrumented symbol: the entity platform ASTs (``custom_components/
heatpump_optimizer/{sensor,binary_sensor,switch,button}.py``) together with
the production artifacts ``strings.json`` and ``icons.json``. Perturbations
under which the numbers must move: deleting ``icons.json`` drops
icons_json_exists to 0, icons_json_entries to 0, entities_rendering_icon to
60/64 and registry_coverage to 0.000; re-adding any one ``_attr_icon`` pin
(e.g. ``_attr_icon = "mdi:cash"`` on ``SpaceCostSensor``) raises
attr_icon_assignments and attr_icon_static by 1; stripping one entry from
icons.json lowers icons_json_entries, entities_rendering_icon and
registry_coverage together.

Expected, at the baseline origin/main (87645f8, re-measured identical at the
6d83f0b merge-base; v6.2.x–6.3.5, 2026-09-02), Apple M1:
  attr_icon_assignments=64 attr_icon_static=64 attr_icon_dynamic=0
  icons_json_exists=0 icons_json_entries=0 device_class_duplicates=4
  device_class_rendered=0 entities_rendering_icon=64/64
  registry_coverage=0.000 of 64 movable icons (nothing leans at the baseline)
After the #189 fix:
  attr_icon_assignments=0 attr_icon_static=0 attr_icon_dynamic=0
  icons_json_exists=1 icons_json_entries=60 device_class_duplicates=0
  device_class_rendered=4 entities_rendering_icon=64/64
  registry_coverage=1.000 of 60 movable icons

Writes nothing. Nothing here is a timing, but the contract's thread_factor,
load1 and swapins lines are printed for completeness.
"""
from __future__ import annotations

import os

for _threads in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_threads, "1")

import ast
import json
import re
import resource
import sys
import time
from pathlib import Path

PACKAGE = Path(os.environ.get("HPO_ICONS_PACKAGE", "custom_components/heatpump_optimizer"))
PLATFORMS = ("sensor.py", "binary_sensor.py", "switch.py", "button.py")

# Home Assistant's own device-class default icons, transcribed from
# homeassistant/components/sensor/icons.json and binary_sensor/icons.json
# (entity_component sections, HA 2026.9). These are what an entity with the
# device class and no icon of its own renders; an icon equal to one of these
# is a device-class duplicate and is removed rather than ported.
SENSOR_DC_DEFAULTS = {
    "temperature": "mdi:thermometer",
    "power": "mdi:flash",
    "energy": "mdi:lightning-bolt",
    "energy_storage": "mdi:car-battery",
    "frequency": "mdi:sine-wave",
    "irradiance": "mdi:sun-wireless",
    "volume_storage": "mdi:storage-tank",
    "monetary": "mdi:cash",
    "timestamp": "mdi:clock",
}
BINARY_DC_DEFAULTS = {
    "problem": "mdi:check-circle",
    "window": "mdi:window-closed",
    "heat": "mdi:thermometer",
}

_MDI = re.compile(r"^mdi:[a-z0-9-]+$")


def entity_classes() -> list[dict]:
    """Every entity class of the four platforms with its icon facts.

    The translation key is read from the ``__init__`` call that constructs
    the base (``super().__init__(coordinator, entry, key, translation_key)``
    or the platform's shared button base), the same place the runtime sets
    it; a device class is recognised as ``SensorDeviceClass.X`` /
    ``BinarySensorDeviceClass.X`` with X one of the defaults tables above.
    """
    strings = json.loads((PACKAGE / "strings.json").read_text())["entity"]
    classes: list[dict] = []
    for fname in PLATFORMS:
        platform = fname[:-3]
        known_keys = set(strings.get(platform, {}))
        tree = ast.parse((PACKAGE / fname).read_text())
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            entry = {
                "file": fname,
                "platform": platform,
                "class": node.name,
                "lineno": node.lineno,
                "icon": None,
                "icon_static": False,
                "translation_key": None,
                "device_class": None,
            }
            for stmt in node.body:
                pairs = []
                if isinstance(stmt, ast.Assign):
                    pairs = [(t, stmt.value) for t in stmt.targets]
                elif isinstance(stmt, ast.AnnAssign) and stmt.value is not None:
                    pairs = [(stmt.target, stmt.value)]
                for target, value in pairs:
                    if not isinstance(target, ast.Name):
                        continue
                    if target.id == "_attr_icon":
                        entry["icon_static"] = isinstance(value, ast.Constant)
                        try:
                            entry["icon"] = ast.literal_eval(value)
                        except (ValueError, TypeError):
                            entry["icon"] = "<dynamic>"
                    elif target.id == "_attr_translation_key":
                        try:
                            entry["translation_key"] = ast.literal_eval(value)
                        except (ValueError, TypeError):
                            pass
                    elif target.id == "_attr_device_class" and isinstance(
                        value, ast.Attribute
                    ):
                        entry["device_class"] = value.attr.lower()
                if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for call in ast.walk(stmt):
                        if not isinstance(call, ast.Call):
                            continue
                        callee = (
                            call.func.attr
                            if isinstance(call.func, ast.Attribute)
                            else getattr(call.func, "id", "")
                        )
                        if callee != "__init__":
                            continue
                        if len(call.args) >= 4:
                            try:
                                candidate = ast.literal_eval(call.args[3])
                            except (ValueError, TypeError):
                                continue
                            if isinstance(candidate, str) and candidate in known_keys:
                                entry["translation_key"] = (
                                    entry["translation_key"] or candidate
                                )
            if entry["icon"] is not None or entry["translation_key"] is not None:
                classes.append(entry)
    return classes


def device_class_default(platform: str, device_class: str | None) -> str | None:
    if device_class is None:
        return None
    if platform == "sensor":
        return SENSOR_DC_DEFAULTS.get(device_class)
    if platform == "binary_sensor":
        return BINARY_DC_DEFAULTS.get(device_class)
    return None


def main() -> int:
    _cpu0 = time.process_time()
    _thread0 = time.thread_time()

    classes = entity_classes()
    icon_classes = [c for c in classes if c["icon"] is not None]
    static = [c for c in icon_classes if c["icon_static"]]
    dynamic = [c for c in icon_classes if not c["icon_static"]]

    duplicates = sorted(
        f"{c['platform']}:{c['translation_key']} {c['icon']} == {c['device_class']} default"
        for c in static
        if c["icon"] == device_class_default(c["platform"], c["device_class"])
    )

    icons_path = PACKAGE / "icons.json"
    icons_json: dict = {}
    if icons_path.is_file():
        icons_json = json.loads(icons_path.read_text())
    registry = {
        platform: {
            key: spec.get("default")
            for key, spec in entries.items()
            if isinstance(spec, dict)
        }
        for platform, entries in (icons_json.get("entity") or {}).items()
    }

    registry_covered = 0
    rendered = 0
    leaning = []
    total = sum(1 for c in classes if c["translation_key"] is not None)
    for c in classes:
        if c["translation_key"] is None:
            continue
        entry = registry.get(c["platform"], {}).get(c["translation_key"])
        default = device_class_default(c["platform"], c["device_class"])
        if entry is not None:
            registry_covered += 1
            rendered += 1
        elif c["icon"] is not None:
            rendered += 1  # the baseline's mechanism: the class pin
        elif default is not None:
            rendered += 1  # no pin, no registry entry, the class renders it
            leaning.append(
                f"{c['platform']}:{c['translation_key']} renders {default} "
                f"via {c['device_class']}"
            )

    # The roster that must carry a registry entry: every translation-keyed
    # class minus the ones leaning on a device-class default. At the baseline
    # nothing leans (all 64 carry pins), after the fix the four removed
    # duplicates lean.
    movable = total - len(leaning)

    print(f"CLASSES {len(classes)} icon_bearing={len(icon_classes)}")
    for c in static:
        print(
            f"STATIC {c['file']}:{c['lineno']} {c['class']} "
            f"tk={c['translation_key']} icon={c['icon']} dc={c['device_class']}"
        )
    for c in dynamic:
        print(f"DYNAMIC {c['file']}:{c['lineno']} {c['class']} {c['icon']}")
    for line in duplicates:
        print(f"DEVICE_CLASS_DUPLICATE {line}")
    for line in sorted(leaning):
        print(f"DEVICE_CLASS_RENDERED {line}")
    for platform in sorted(registry):
        print(f"REGISTRY {platform} {len(registry[platform])} entries")

    print(f"RESULT attr_icon_assignments={len(icon_classes)} assignments")
    print(f"RESULT attr_icon_static={len(static)} assignments")
    print(f"RESULT attr_icon_dynamic={len(dynamic)} assignments")
    print(f"RESULT icons_json_exists={1 if icons_path.is_file() else 0} flag")
    print(
        "RESULT icons_json_entries="
        f"{sum(len(v) for v in registry.values())} entries"
    )
    print(f"RESULT device_class_duplicates={len(duplicates)} icons")
    print(f"RESULT device_class_rendered={len(leaning)} entities")
    print(f"RESULT entities_rendering_icon={rendered}/{total} entities")
    print(
        f"RESULT registry_coverage={registry_covered / movable if movable else float('nan'):.3f}"
        f" of {movable} movable icons"
    )

    cpu = time.process_time() - _cpu0
    thread = time.thread_time() - _thread0
    print(f"RESULT thread_factor={cpu / thread if thread else float('nan'):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(
        f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
