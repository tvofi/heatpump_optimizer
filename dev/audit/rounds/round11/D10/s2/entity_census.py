"""D10-s2 gold entity rules, one count per rule, over every entity the six
platforms add through their real async_setup_entry (a real coordinator after
one input cycle; dev/audit/rounds/round11/D10/s2/_census.py).

Rules counted: devices, dynamic-devices/stale-devices (distinct devices),
entity-category, entity-device-class, entity-disabled-by-default,
entity-translations, icon-translations.

Metric (the finding's): impossible_pairs = sensors whose published
(device_class, state_class) pair Home Assistant's DEVICE_CLASS_STATE_CLASSES
table forbids (HA logs "is using state class ... which is impossible
considering device class" and the recorder compiles no sum).
Key: the entity's own device_class / state_class as the entity publishes them
(property where one exists, else the _attr_), never the class name.
Second metric: delta_bare = sensors publishing a temperature difference in
degC with no device class, while HA >= 2025.11.0 offers TEMPERATURE_DELTA.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D10/s2/entity_census.py [--perturb-state|--perturb-delta]
Expected at baseline 92d38ecb: impossible_pairs=3 (Space/DHW/Total Energy:
energy + measurement), delta_bare=3, exact.
--perturb-state sets sensor._AccumulatingSensor._attr_state_class to
TOTAL_INCREASING in memory: impossible_pairs -> 0 (the cost sensors keep
their own TOTAL). --perturb-delta sets ECL110DisplaceSensor's device class
to "temperature_delta": delta_bare -> 2.
Instrumented symbol: heatpump_optimizer.sensor:_AccumulatingSensor (and
heatpump_optimizer.sensor:async_setup_entry for the census).
Machine: local macOS box B2, Python 3.14 venv-ci.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _census as c  # noqa: E402
from heatpump_optimizer import sensor as sensor_mod  # noqa: E402

# Home Assistant core's own table (homeassistant/components/sensor/const.py
# DEVICE_CLASS_STATE_CLASSES, dev branch fetched 2026-11-16), the rows for
# every device class this integration uses.
HA_TABLE = {
    "apparent_power": {"measurement"}, "battery": {"measurement"},
    "energy": {"total", "total_increasing"}, "energy_storage": {"measurement"},
    "enum": set(), "frequency": {"measurement"}, "irradiance": {"measurement"},
    "monetary": {"total"}, "power": {"measurement"}, "temperature": {"measurement"},
    "temperature_delta": {"measurement"}, "timestamp": set(),
    "volume_storage": {"measurement"},
}

if "--perturb-state" in sys.argv:
    sensor_mod._AccumulatingSensor._attr_state_class = "total_increasing"
if "--perturb-delta" in sys.argv:
    sensor_mod.ECL110DisplaceSensor._attr_device_class = "temperature_delta"

ents, coord, entry = c.entities()


def pub(e, name):
    """What the entity publishes for ``name``: a class property, else _attr_."""
    for k in type(e).__mro__:
        if name in vars(k) and isinstance(vars(k)[name], property) and k.__module__.startswith("heatpump_optimizer"):
            return getattr(e, name)
    return getattr(e, f"_attr_{name}", None)


def enabled_default(e):
    v = pub(e, "entity_registry_enabled_default")
    return True if v is None else bool(v)


by_platform = Counter(p for p, _ in ents)
print("RESULT entities=%d count" % len(ents))
for p, n in sorted(by_platform.items()):
    print(f"RESULT entities_{p}={n} count")

# devices
devices = set()
no_device = 0
not_service = 0
for p, e in ents:
    info = e.device_info or {}
    ids = info.get("identifiers")
    if not ids:
        no_device += 1
        continue
    devices.add(frozenset(ids))
    if str(info.get("entry_type", "")).lower().rsplit(".", 1)[-1] != "service":
        not_service += 1
print(f"RESULT devices_no_device_info={no_device} count")
print(f"RESULT devices_not_service={not_service} count")
print(f"RESULT distinct_devices={len(devices)} count")

# entity-category
cats = Counter(str(pub(e, "entity_category")) for _, e in ents)
for k, v in sorted(cats.items()):
    print(f"RESULT category_{k.rsplit('.', 1)[-1].lower()}={v} count")
config_cat = [type(e).__name__ for p, e in ents
              if p in ("switch", "button", "datetime") and pub(e, "entity_category") is not None]
print(f"RESULT category_on_controls={len(config_cat)} count")

# entity-device-class
impossible, delta_bare, unit_no_class = [], [], []
for p, e in ents:
    if p != "sensor":
        continue
    dc, sc = pub(e, "device_class"), pub(e, "state_class")
    unit = pub(e, "native_unit_of_measurement")
    dc_s = None if dc is None else str(dc).rsplit(".", 1)[-1].lower()
    sc_s = None if sc is None else str(sc).rsplit(".", 1)[-1].lower()
    if dc_s and sc_s and dc_s in HA_TABLE and sc_s not in HA_TABLE[dc_s]:
        impossible.append(f"{type(e).__name__}:{dc_s}+{sc_s}")
    if dc_s is None and unit in ("°C", "K"):
        delta_bare.append(type(e).__name__)
    if dc_s is None and unit:
        unit_no_class.append(f"{type(e).__name__}[{unit}]")
for x in impossible:
    print("IMPOSSIBLE", x)
for x in delta_bare:
    print("DELTA_BARE", x)
print("UNIT_NO_CLASS", ", ".join(unit_no_class))
print(f"RESULT impossible_pairs={len(impossible)} count")
print(f"RESULT delta_bare={len(delta_bare)} count")
print(f"RESULT unit_without_device_class={len(unit_no_class)} count")
print(f"RESULT with_device_class={sum(pub(e, 'device_class') is not None for _, e in ents)} count")

# entity-disabled-by-default
off = [type(e).__name__ for _, e in ents if not enabled_default(e)]
print("DISABLED", ", ".join(off))
print(f"RESULT disabled_by_default={len(off)} count")

# entity-translations
cat = {n: c.load_json(f) for n, f in (("strings", "strings.json"), ("en", "translations/en.json"),
                                      ("sv", "translations/sv.json"), ("de", "translations/de.json"))}
miss_name, miss_state, named = 0, 0, 0
for p, e in ents:
    key = e._attr_translation_key
    if getattr(e, "_attr_name", None) not in (None,):
        named += 1
    for d in cat.values():
        node = d.get("entity", {}).get(p, {}).get(key) or {}
        miss_name += not node.get("name")
        for o in (getattr(e, "_attr_options", None) or []):
            miss_state += o not in node.get("state", {})
print(f"RESULT translation_name_missing={miss_name} count")
print(f"RESULT translation_state_missing={miss_state} count")
print(f"RESULT hardcoded_name={named} count")
print(f"RESULT no_translation_key={sum(not e._attr_translation_key for _, e in ents)} count")

# icon-translations
icons = c.load_json("icons.json")["entity"]
pinned = sum(hasattr(e, "_attr_icon") or any("icon" in vars(k) for k in type(e).__mro__
             if k.__module__.startswith("heatpump_optimizer")) for _, e in ents)
icon_missing = sum(e._attr_translation_key not in icons.get(p, {}) for p, e in ents)
print(f"RESULT icon_pinned_in_code={pinned} count")
print(f"RESULT icon_translation_missing={icon_missing} count")
c.stats()
