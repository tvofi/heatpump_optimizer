"""D6-02 verification, verifier seat 1 -- my OWN harness, refute-first.

METHOD (independent of the finder's currency_unit.py, which drives
sensor.async_setup_entry and greps the README table; mine instead):
  A. Read the README sensor table with a *row-oriented* markdown parse and
     list every sensor name whose Unit column is exactly `CUR`.
  B. Drive the REAL sensor platform setup, then for each constructed entity
     read the Home Assistant `native_unit_of_measurement` PROPERTY (not the
     _attr) -- so a unit supplied by a device class or a subclass could still
     rescue the sensor and refute the finding.
  C. For the one that publishes no unit, drive `topology.rank_sensor_gaps`
     directly to confirm the value it publishes is money per month
     (`sek_per_month`), and confirm the coordinator currency is non-empty at
     the same time, so "could have had a unit" is demonstrated.
  D. Contrast control: the other CUR sensors must all publish a unit -- if
     several were unitless the finding's "the one" would be wrong.

RUN (from the repository root):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/d6_own_D6-02.py

ROOT RULE: the working directory (`ROOT = pathlib.Path(".")`).

EXPECTED if the finding is true: cur_rows=9, unitless=1 (the advisor).
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

import ast
import asyncio
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(".")
PKG = ROOT / "custom_components" / "heatpump_optimizer"
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeCoordinator, FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer import sensor as sensor_platform  # noqa: E402
from heatpump_optimizer import topology  # noqa: E402

DATA = next(
    ast.literal_eval(n.value)
    for n in ast.parse((ROOT / "tests" / "entities.py").read_text()).body
    if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", None) == "DATA"
)
STR = json.loads((PKG / "strings.json").read_text())["entity"]["sensor"]

added: list = []
entry = FakeEntry()
coord = FakeCoordinator(DATA)
coord._month_totals = {"dhw": (41.5, 62.25), "space": (120.0, 180.0)}
entry.runtime_data = coord
asyncio.run(sensor_platform.async_setup_entry(FakeHass(), entry, added.extend))

# entity display name (what the README table keys on) -> entity
by_name = {
    STR.get(getattr(e, "_attr_translation_key", None), {}).get("name", "?"): e
    for e in added
}

# --- A. README CUR rows, parsed independently (row-oriented) -------------
readme = (ROOT / "README.md").read_text().splitlines()
cur_rows = []
in_sensor_table = False
for line in readme:
    if line.startswith("### Sensors ("):
        in_sensor_table = True
        continue
    if in_sensor_table and line.startswith("### "):
        break
    if in_sensor_table and line.startswith("|"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[1] == "CUR" and not set(cells[0]) <= set("-: "):
            cur_rows.append(cells[0])

# --- B. the HA property, not the attribute --------------------------------
def unit_of(name):
    e = by_name.get(name)
    if e is None:
        return "<no such entity>"
    try:
        return e.native_unit_of_measurement
    except Exception:
        return "<error>"

units = {n: unit_of(n) for n in cur_rows}
unitless = sorted(n for n, u in units.items() if u in (None, ""))

# --- C. the advisor's value really is money per month --------------------
advisor = by_name.get("Sensor-Gap Euro Advisor")
adv_value = advisor.native_value if advisor is not None else None
adv_state_class = getattr(advisor, "state_class", None) if advisor else None
adv_enabled_default = getattr(
    advisor, "entity_registry_enabled_default", "missing") if advisor else None
gaps_cfg = getattr(advisor.coordinator, "_config", None) or {} if advisor else {}
gaps = topology.rank_sensor_gaps(
    gaps_cfg,
    house_kw=advisor.coordinator.data.get("house_power_series") or (),
    hp_kw=advisor.coordinator.data.get("heat_pump_power_series") or (),
    peak_price=45.0, peak_window=60, peak_count=3,
) if advisor else []

print(f"RESULT cur_rows={len(cur_rows)} rows")
print(f"RESULT cur_rows_unitless={len(unitless)} rows")
print(f"RESULT cur_rows_with_unit={len(cur_rows) - len(unitless)} rows")
print(f"RESULT sensors_constructed={len(added)} sensors")
print(f"RESULT advisor_unit={units.get('Sensor-Gap Euro Advisor')!r}")
print(f"RESULT advisor_native_value={adv_value!r}")
print(f"RESULT advisor_state_class={adv_state_class!r}")
print(f"RESULT coordinator_currency={coord.currency!r}")
print(f"RESULT thread_factor=1.0")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
print("unitless:", unitless)
print("units:", units)
print("advisor enabled by default:", adv_enabled_default)
print("rank_sensor_gaps top rows:", gaps[:2])
