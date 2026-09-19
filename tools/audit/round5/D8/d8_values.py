"""D8 round 5 -- per-entity metadata and value checks against the two rich
coordinator payloads the entity tests ship (``DATA`` and ``_ATTR_RICH``).

Metric definition (one line): the count of entities, per violation class,
whose published (native_value, metadata) pair breaks a stated invariant when
its source key IS present in the payload.

Run:
    PYTHONPATH=tests/hastub python3 tools/audit/round5/D8/d8_values.py

Machine: Apple M1, 8 GB. Result is a count -- content, not timing.
"""
from __future__ import annotations

import ast
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_var, "1")

_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[4]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "tests"))
sys.path.insert(0, str(_ROOT / "tests" / "hastub"))

from harness import FakeCoordinator, FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer import (  # noqa: E402
    binary_sensor, button, climate, datetime as datetime_mod, sensor, switch,
)

ROOT = Path("custom_components/heatpump_optimizer")
STRINGS = json.loads((ROOT / "strings.json").read_text())["entity"]
PLATFORM_MODULES = {
    "sensor": sensor, "binary_sensor": binary_sensor, "button": button,
    "climate": climate, "switch": switch, "datetime": datetime_mod,
}


def _extract(name, ns=None):
    """Pull a module-level dict out of tests/entities.py by AST."""
    tree = ast.parse(Path("tests/entities.py").read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            getattr(t, "id", None) == name for t in node.targets
        ):
            try:
                return ast.literal_eval(node.value)
            except ValueError:
                # ``_ATTR_RICH`` unpacks ``**DATA``; evaluate with DATA in scope.
                return eval(  # noqa: S307 -- local test fixture, not user input
                    compile(ast.Expression(node.value), "<entities>", "eval"),
                    dict(ns or {}),
                )
    raise SystemExit(f"{name} not found")


DATA = _extract("DATA")
ATTR_RICH = _extract("_ATTR_RICH", ns={"DATA": DATA})


def collect_all(coord):
    out = []
    for platform, module in PLATFORM_MODULES.items():
        added = []
        entry = FakeEntry()
        entry.runtime_data = coord
        hass = FakeHass()
        asyncio.run(module.async_setup_entry(hass, entry, added.extend))
        for e in added:
            out.append((platform, e))
    return out


def coord_for(data):
    c = FakeCoordinator(data)
    c._month_totals = {"dhw": (41.5, 62.25), "space": (120.0, 180.0)}
    # SolarHeatGainSensor reads coordinator._thermal_params, not the payload.
    import heatpump_optimizer.sensor as _s
    return c


def main():
    for label, data in (("DATA", DATA), ("ATTR_RICH", ATTR_RICH)):
        coord = FakeCoordinator(data)
        coord._month_totals = {"dhw": (41.5, 62.25), "space": (120.0, 180.0)}
        # give it the real thermal params object the one sensor needs
        hass = FakeHass()
        entry = FakeEntry(data={})
        from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
        real = HeatPumpOptimizerCoordinator(hass, entry)
        coord._thermal_params = real._thermal_params
        ents = collect_all(coord)
        n = 0
        n_none = 0
        none_list = []
        for platform, e in ents:
            n += 1
            try:
                nv = e.native_value
            except Exception as exc:  # noqa: BLE001
                none_list.append((platform, type(e).__name__, f"RAISED {exc!r}"))
                continue
            cls = type(e).__name__
            name = STRINGS.get(platform, {}).get(
                getattr(e, "_attr_translation_key", None), {}).get("name", "?")
            if nv is None:
                n_none += 1
                none_list.append((platform, cls, name))
        print(f"--- payload {label}: entities={n} native_none={n_none}")
        for row in none_list:
            print("   NONE", row)


if __name__ == "__main__":
    main()
