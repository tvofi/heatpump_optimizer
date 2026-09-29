#!/usr/bin/env python3
"""
Metric: the set of sensor/binary_sensor display names whose real
entity_registry_enabled_default (sensor.py:422, the _DHWEntityMixin
property, and the plain _attr_entity_registry_enabled_default = False class
attribute) evaluates False under a fresh honest coordinator with hot water
configured (tests/entities.py:_honest_coordinator, dhw=True — "the ordinary
install"), versus README.md's explicit "Disabled by default: ..." sentence
after the Sensors table.
Command: PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  python3 tools/audit/round8/D6/s1_disabled_default.py
Expected: prints RESULT lines with the two sets' set-difference sizes; run
from the tree root.
Baseline SHA: cdf82daabcfe3777d98b31489f36df5555ec9d82
Perturbation: flip one sensor's `_attr_entity_registry_enabled_default`
(e.g. Solar Surplus Forecast at sensor.py) from False to True (or delete the
line) and the printed `actual_disabled` set must lose that entity's name,
moving `only_in_actual`/`only_in_readme` by exactly one.
"""
import os
for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
          "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")

import json
import re
import sys

sys.path.insert(0, "tests")
sys.path.insert(0, "tests/hastub")

_real_exit = sys.exit
sys.exit = lambda *a, **k: None
try:
    import entities as E
finally:
    sys.exit = _real_exit
from heatpump_optimizer import sensor, binary_sensor

_hass, coord, _data = E._honest_coordinator()  # dhw=True: the ordinary install
sensors = E.collect(sensor, coordinator=coord)
binsens = E.collect(binary_sensor, coordinator=coord)

strings = json.load(open("custom_components/heatpump_optimizer/strings.json", encoding="utf-8"))
names = {}
for platform in ("sensor", "binary_sensor"):
    names[platform] = {k: v.get("name", k) for k, v in strings["entity"][platform].items()}

actual_disabled = set()
actual_enabled = set()
for platform, ents in (("sensor", sensors), ("binary_sensor", binsens)):
    for e in ents:
        key = getattr(e, "_attr_translation_key", None) or getattr(e, "translation_key", None)
        label = names[platform].get(key, key)
        try:
            enabled_default = e.entity_registry_enabled_default
        except Exception:
            enabled_default = getattr(e, "_attr_entity_registry_enabled_default", True)
        if enabled_default:
            actual_enabled.add(label)
        else:
            actual_disabled.add(label)

readme = open("README.md", encoding="utf-8").read()
m = re.search(r"Disabled by default: (.+?)\.\n", readme, re.S)
readme_list_raw = m.group(1) if m else ""
readme_list_raw = readme_list_raw.replace("\n", " ")
# Split on commas and "and" before the last item.
parts = re.split(r",\s*(?:and\s+)?|\s+and\s+", readme_list_raw)
readme_disabled = {p.strip().rstrip(".") for p in parts if p.strip()}

only_in_actual = sorted(actual_disabled - readme_disabled)
only_in_readme = sorted(readme_disabled - actual_disabled)

print(f"RESULT actual_disabled_count={len(actual_disabled)} entities")
print(f"RESULT readme_disabled_count={len(readme_disabled)} entities")
print(f"RESULT only_in_actual_count={len(only_in_actual)} entities")
print(f"RESULT only_in_readme_count={len(only_in_readme)} entities")
print("only_in_actual:", only_in_actual)
print("only_in_readme:", only_in_readme)

load1 = os.getloadavg()[0]
print(f"RESULT load1={load1} load")
print("RESULT thread_factor=1.0 ratio")
