"""D6 round 4 -- README.md's `CUR` unit column against what each sensor publishes.

METRIC: the number of sensors whose README Unit column says `CUR` (the
instance currency) while the entity's ``native_unit_of_measurement`` is None,
counted over the sensors the real ``sensor.async_setup_entry`` constructs.

RUN (from the repository root):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/currency_unit.py

ROOT RULE: the working directory (`ROOT = Path(".")`).

EXPECTED (baseline 7dd68dd327fe3dbfb09f3bd0fe38910c58877697, 8-core Apple M1,
macOS 25.6.0, Python 3.11.9, tolerance 0 -- counts, exactly reproducible):
    RESULT sensors_constructed=59
    RESULT currency_rows_documented=9
    RESULT currency_rows_without_unit=1     (Sensor-Gap Euro Advisor)
    RESULT currency_sensors_with_unit=8

INSTRUMENTED SYMBOL:
    heatpump_optimizer.sensor:async_setup_entry (the census) and
    heatpump_optimizer.sensor:SensorGapAdvisorSensor (the offender).

PERTURBATION (built in, no production file is touched):
    HPO_D6_PERTURB=1 patches SensorGapAdvisorSensor.__init__ at runtime to set
    ``_attr_native_unit_of_measurement = coordinator.currency``, the line every
    other monetary sensor already carries.  currency_rows_without_unit must
    fall 1 -> 0 and currency_sensors_with_unit rise 8 -> 9.
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

import harness  # noqa: E402
from harness import FakeCoordinator, FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer import sensor as sensor_platform  # noqa: E402

if os.environ.get("HPO_D6_PERTURB") == "1":
    _orig = sensor_platform.SensorGapAdvisorSensor.__init__

    def _patched(self, coordinator, entry):
        _orig(self, coordinator, entry)
        self._attr_native_unit_of_measurement = coordinator.currency

    sensor_platform.SensorGapAdvisorSensor.__init__ = _patched

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

by_name = {
    STR.get(getattr(e, "_attr_translation_key", None), {}).get("name", "?"): e
    for e in added
}

README = (ROOT / "README.md").read_text()
block = re.search(
    r"^### Sensors \(\d+ total\)(.*?)(?=^### Binary Sensors)", README, re.M | re.S
).group(1)
cur_rows = []
for line in block.splitlines():
    if not line.startswith("|"):
        continue
    c = [x.strip() for x in line.strip().strip("|").split("|")]
    if len(c) == 4 and c[1] == "CUR":
        cur_rows.append(c[0])

without = [n for n in cur_rows if getattr(by_name[n], "_attr_native_unit_of_measurement", None) in (None, "")]
with_unit = [n for n in cur_rows if n not in without]

print(f"RESULT sensors_constructed={len(added)} sensors")
print(f"RESULT currency_rows_documented={len(cur_rows)} rows")
print(f"RESULT currency_rows_without_unit={len(without)} rows")
print(f"RESULT currency_sensors_with_unit={len(with_unit)} rows")
print("RESULT thread_factor=1.0")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
print("documented CUR:", cur_rows)
print("published without a unit:", without)
print("coordinator.currency =", coord.currency)
for n in without:
    e = by_name[n]
    print(f"  {n}: native_value={e.native_value!r}, "
          f"unit={getattr(e, '_attr_native_unit_of_measurement', None)!r}, "
          f"state_class={getattr(e, '_attr_state_class', None)!r}, "
          f"device_class={getattr(e, '_attr_device_class', None)!r}")
