"""D8 round 5 -- dump every sensor's metadata and published value from the
rich DATA payload, so type/unit/device-class mismatches are visible.

    PYTHONPATH=tests/hastub python3 tools/audit/round5/D8/meta.py
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_var, "1")

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tests"))

from harness import FakeCoordinator, FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer import (  # noqa: E402
    binary_sensor, button, climate, datetime as datetime_mod, sensor, switch,
)

ROOT = Path("custom_components/heatpump_optimizer")
_STRINGS = json.loads((ROOT / "strings.json").read_text())["entity"]

# Import DATA by executing entities.main? No -- reuse the production module
# plus a local copy of the payload the entity tests use.
import runpy  # noqa: E402

# The rich payload lives in tests/entities.py which runs checks at import.
# Pull it out with a source-level copy instead of importing.
import ast  # noqa: E402

_src = Path("tests/entities.py").read_text()
_tree = ast.parse(_src)
DATA = None
for node in _tree.body:
    if isinstance(node, ast.Assign) and any(
        getattr(t, "id", None) == "DATA" for t in node.targets
    ):
        DATA = ast.literal_eval(node.value)
assert DATA, "DATA not found"

PLATFORM_MODULES = {
    "sensor": sensor, "binary_sensor": binary_sensor, "button": button,
    "climate": climate, "switch": switch, "datetime": datetime_mod,
}


def collect(module, coordinator):
    added = []

    def add_entities(entities):
        added.extend(entities)

    hass = FakeHass()
    entry = FakeEntry()
    entry.runtime_data = coordinator
    asyncio.run(module.async_setup_entry(hass, entry, add_entities))
    return added


def name_of(platform, entity):
    key = getattr(entity, "_attr_translation_key", None)
    return _STRINGS.get(platform, {}).get(key, {}).get("name", f"<untranslated {platform}:{key}>")


def main():
    coord = FakeCoordinator(DATA)
    coord._month_totals = {"dhw": (41.5, 62.25), "space": (120.0, 180.0)}
    for platform, module in PLATFORM_MODULES.items():
        for e in collect(module, coord):
            tkey = getattr(e, "_attr_translation_key", None)
            dc = getattr(e, "_attr_device_class", None)
            sc = getattr(e, "_attr_state_class", None)
            unit = getattr(e, "_attr_native_unit_of_measurement", None)
            cat = getattr(e, "_attr_entity_category", None)
            opts = getattr(e, "_attr_options", None)
            nv = None
            try:
                nv = e.native_value
            except Exception as exc:  # noqa: BLE001
                nv = f"ERR:{exc!r}"
            print(
                f"{platform:14s} {name_of(platform, e)!r:44s} dc={str(dc):32s} "
                f"sc={str(sc):32s} unit={str(unit):10s} cat={str(cat):22s} nv={nv!r}"
                + (f" opts={opts}" if opts else "")
            )


if __name__ == "__main__":
    main()
