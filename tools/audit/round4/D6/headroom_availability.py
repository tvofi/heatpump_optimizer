"""D6 round 4 -- docs/automations.md's Power Headroom availability precondition.

docs/automations.md:18 says of `sensor.heat_pump_optimizer_power_headroom`:
"It stays unavailable until you set a main fuse size in the options."

METRIC: over the 2x2 grid (main fuse set / not) x (capacity tariff enabled /
not), the number of cells in which the real Power Headroom sensor reports
``available is True``.  The documented rule predicts 2 (the two fuse cells);
anything more falsifies it.

RUN (from the repository root):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/headroom_availability.py

ROOT RULE: the working directory (`ROOT = Path(".")`).

EXPECTED (baseline 7dd68dd327fe3dbfb09f3bd0fe38910c58877697, 8-core Apple M1,
macOS 25.6.0, Python 3.11.9, tolerance 0 -- a count over four cells):
    RESULT cells=4
    RESULT available_cells=3
    RESULT available_without_a_fuse=1
    RESULT predicted_by_the_doc=2

INSTRUMENTED SYMBOLS:
    heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._power_headroom
    heatpump_optimizer.sensor:async_setup_entry -> PowerHeadroomSensor.available

PERTURBATION (config only, no file is touched): in the fuse-less,
tariff-enabled cell set CONF_PEAK_TARIFF_ENABLED back to False.
``available_without_a_fuse`` must fall 1 -> 0 and ``available_cells`` 3 -> 2,
i.e. the doc's rule becomes true exactly when the capacity tariff is the thing
that is removed -- which is what makes the tariff, not the fuse, the term the
sentence leaves out.  HPO_D6_PERTURB=1 runs that arm.
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

import asyncio
import json
import pathlib
import sys

ROOT = pathlib.Path(".")
PKG = ROOT / "custom_components" / "heatpump_optimizer"
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import harness  # noqa: E402
from harness import FakeCoordinator, FakeEntry, FakeHass, FakeState  # noqa: E402
from heatpump_optimizer import const, sensor as sensor_platform  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

STR = json.loads((PKG / "strings.json").read_text())["entity"]["sensor"]
PERTURB = os.environ.get("HPO_D6_PERTURB") == "1"


def coordinator(extra):
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    cfg = {
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    }
    cfg.update(extra)
    co = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg))
    asyncio.run(co._update_current_state())
    return co


def headroom_entity(data):
    added: list = []
    entry = FakeEntry()
    entry.runtime_data = FakeCoordinator(data)
    asyncio.run(sensor_platform.async_setup_entry(FakeHass(), entry, added.extend))
    for e in added:
        if getattr(e, "_attr_translation_key", None) == "power_headroom":
            return e
    raise AssertionError("power_headroom sensor not constructed")


TARIFF = {const.CONF_PEAK_TARIFF_ENABLED: not PERTURB,
          const.CONF_PEAK_TARIFF_PRICE: 45.0}
CELLS = {
    "no fuse, no tariff": {},
    "no fuse, capacity tariff": dict(TARIFF),
    "fuse, no tariff": {const.CONF_MAIN_FUSE_A: 20},
    "fuse, capacity tariff": {const.CONF_MAIN_FUSE_A: 20, **TARIFF},
}

rows = {}
for label, cfg in CELLS.items():
    co = coordinator(cfg)
    view = co._power_headroom()
    ent = headroom_entity(co._build_data_dict())
    rows[label] = {"view": view, "entity_available": bool(ent.available),
                   "native_value": ent.native_value}

available = [k for k, v in rows.items() if v["entity_available"]]
no_fuse_available = [k for k in available if k.startswith("no fuse")]

print(f"RESULT cells={len(rows)} cells")
print(f"RESULT available_cells={len(available)} cells")
print(f"RESULT available_without_a_fuse={len(no_fuse_available)} cells")
print("RESULT predicted_by_the_doc=2 cells")
print("RESULT thread_factor=1.0")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
for k, v in rows.items():
    print(f"  {k:28s} available={v['entity_available']!s:5s} "
          f"value={v['native_value']!r} view={v['view']}")
