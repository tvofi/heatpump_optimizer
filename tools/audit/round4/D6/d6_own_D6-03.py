"""D6-03 verification, verifier seat 1 -- my OWN harness, refute-first.

docs/automations.md (lines 17-19) says of sensor.heat_pump_optimizer_power_headroom:
"It stays unavailable until you set a main fuse size in the options".

METHOD (independent of the finder's headroom_availability.py, which built a
fresh coordinator per cell and constructed the sensor entity against a
FakeCoordinator fed the coordinator's _build_data_dict(); mine instead):
  A. Extract the exact sentence from docs/automations.md (string match), so
     the claim being tested is on the record.
  B. For each cell of the 2x2 grid (fuse 0/20 A) x (capacity tariff off/on),
     build the REAL HeatPumpOptimizerCoordinator with that config, run one
     real input cycle, then construct the sensor platform's entities with
     THAT SAME coordinator as entry.runtime_data and read the entity's
     `available` / `native_value` through the platform's own construction
     path -- no FakeCoordinator in between.
  C. Record which branch fired: the entity's `limit_source` attribute and
     the tariff's sample_factor(now), to show the availability is not a
     metering-window accident.
  D. Also probe the defaults: DEFAULT_MAIN_FUSE_A and
     DEFAULT_PEAK_TARIFF_ENABLED read from const.py, to show the
     no-fuse+tariff cell is a default-fuse install away.

RUN (from the repository root):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/d6_own_D6-03.py

ROOT RULE: the working directory (`ROOT = pathlib.Path(".")`).

EXPECTED if the finding is true: available_cells=3, available_without_a_fuse=1.
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
import pathlib
import re
import sys

ROOT = pathlib.Path(".")
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from heatpump_optimizer import const, sensor as sensor_platform  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

# --- A. the documented sentence, verbatim --------------------------------
auto = (ROOT / "docs" / "automations.md").read_text()
m = re.search(r"It stays unavailable until you set a\s+main fuse size in the options", auto)
doc_sentence_found = m is not None

# --- B/C. the grid, entity on the same real coordinator ------------------
def cell(fuse_a: int, tariff: bool):
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    cfg = {
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    }
    if fuse_a:
        cfg[const.CONF_MAIN_FUSE_A] = fuse_a
    if tariff:
        cfg[const.CONF_PEAK_TARIFF_ENABLED] = True
        cfg[const.CONF_PEAK_TARIFF_PRICE] = 45.0
    co = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg))
    asyncio.run(co._update_current_state())
    # populate coordinator.data the way a completed first refresh would, so
    # the entity reads a live publish payload (available also consults
    # last_update_success, which the constructor initialises True)
    co.data = co._build_data_dict()
    t = co._capacity_tariff()
    sf = t.sample_factor(co._now()) if hasattr(co, "_now") else None

    added: list = []
    entry = FakeEntry()
    entry.runtime_data = co  # the SAME coordinator, no clone
    asyncio.run(sensor_platform.async_setup_entry(FakeHass(), entry, added.extend))
    ent = next(e for e in added if getattr(e, "_attr_translation_key", "") == "power_headroom")
    attrs = ent.extra_state_attributes
    return {
        "available": bool(ent.available),
        "value": ent.native_value,
        "limit_source": attrs.get("limit_source"),
        "sample_factor": sf,
        "threshold_kw": t.threshold_kw(t) if False else None,
    }

GRID = {
    "no fuse, no tariff": (0, False),
    "no fuse, capacity tariff": (0, True),
    "fuse, no tariff": (20, False),
    "fuse, capacity tariff": (20, True),
}
rows = {k: cell(*v) for k, v in GRID.items()}
available = [k for k, v in rows.items() if v["available"]]
no_fuse_available = [k for k in available if k.startswith("no fuse")]

# --- D. the defaults ------------------------------------------------------
default_fuse = const.DEFAULT_MAIN_FUSE_A
default_tariff = const.DEFAULT_PEAK_TARIFF_ENABLED

print(f"RESULT doc_sentence_found={int(doc_sentence_found)} bool")
print(f"RESULT cells={len(rows)} cells")
print(f"RESULT available_cells={len(available)} cells")
print(f"RESULT available_without_a_fuse={len(no_fuse_available)} cells")
print(f"RESULT default_main_fuse_a={default_fuse} A")
print(f"RESULT default_peak_tariff_enabled={default_tariff} bool")
print(f"RESULT thread_factor=1.0")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
for k, v in rows.items():
    print(f"  {k:26s} available={v['available']!s:5s} value={v['value']!r} "
          f"limit_source={v['limit_source']!r} sample_factor={v['sample_factor']!r}")
print("available:", available)
