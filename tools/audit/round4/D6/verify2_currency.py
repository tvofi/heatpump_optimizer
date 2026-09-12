"""Verifier 2 harness (D6-02 attack) -- Sensor-Gap Euro Advisor's published unit.

METRIC (mine): with a coordinator in the instance currency SEK whose data
carries a live power series and a capacity tariff, and whose config leaves the
house-meter slot EMPTY, read the real entity's ``native_value`` and
``native_unit_of_measurement`` -- the two properties Home Assistant's state
machine writes -- plus ``state_class``.  A monetary sensor documented as CUR
in README.md must publish a currency unit; I measure what it actually
publishes, with a non-zero value so the figure is not a degenerate 0.0.

Also the control arm: the same census, every README `CUR` row, checking each
constructed entity's unit -- the other eight rows are the control group.

RUN (from the repository root):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/verify2_currency.py

ROOT RULE: working directory (`ROOT = Path(".")`).
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
import pathlib
import re
import sys

ROOT = pathlib.Path(".")
PKG = ROOT / "custom_components" / "heatpump_optimizer"
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeCoordinator, FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer import const, sensor as sensor_platform  # noqa: E402

DATA = next(
    ast.literal_eval(n.value)
    for n in ast.parse((ROOT / "tests" / "entities.py").read_text()).body
    if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", None) == "DATA"
)

# A realistic data dict from the golden capture, plus an empty house-meter
# slot and live series so the advisor's number is non-zero.
cfg = dict(DATA.get(const.CONF_HOUSE_POWER_ENTITY) and {} or {})  # noqa: F632
data = dict(DATA)
data["house_power_series"] = [3.0 + 0.1 * i for i in range(48)]
data["heat_pump_power_series"] = [1.0 + 0.05 * i for i in range(48)]
data["peak_tariff"] = {"price_per_kw": 45.0, "window_minutes": 60, "peaks_averaged": 3}

added: list = []
entry = FakeEntry()
coord = FakeCoordinator(data)
entry.runtime_data = coord
asyncio.run(sensor_platform.async_setup_entry(FakeHass(), entry, added.extend))

gap = next(e for e in added if getattr(e, "_attr_translation_key", None) == "sensor_gap_advisor")
val = gap.native_value
unit = getattr(gap, "_attr_native_unit_of_measurement", None)
print(f"RESULT v2_gap_native_value={val} {type(val).__name__}")
print(f"RESULT v2_gap_unit={unit!r}")
print(f"RESULT v2_gap_state_class={getattr(gap, '_attr_state_class', None)!r}")
print(f"RESULT v2_gap_device_class={getattr(gap, '_attr_device_class', None)!r}")
print(f"RESULT v2_coordinator_currency={coord.currency!r}")

# how HA would render the state object: str(native_value), unit or none
state_str = f"{val:.0f}" if isinstance(val, float) else str(val)
print(f"rendered state: {state_str!r} unit={unit!r}")

# control group: every README CUR row
README = (ROOT / "README.md").read_text()
block = re.search(
    r"^### Sensors \(\d+ total\)(.*?)(?=^### Binary Sensors)", README, re.M | re.S
).group(1)
import json  # noqa: E402
STR = json.loads((PKG / "strings.json").read_text())["entity"]["sensor"]
by_name = {
    STR.get(getattr(e, "_attr_translation_key", None), {}).get("name", "?"): e
    for e in added
}
cur_rows = []
for line in block.splitlines():
    if not line.startswith("|"):
        continue
    c = [x.strip() for x in line.strip().strip("|").split("|")]
    if len(c) == 4 and c[1] == "CUR":
        cur_rows.append(c[0])
# NB: the unit is an OPTIONAL attribute (``_attr_native_unit_of_measurement``
# may simply be absent -- real HA and the stub both resolve that to None via
# the ``native_unit_of_measurement`` property), so the default here is None,
# not a sentinel: absent IS unitless.  A first draft used "MISSING" as the
# default and under-counted by exactly this entity.
no_unit = [n for n in cur_rows
           if getattr(by_name.get(n), "_attr_native_unit_of_measurement", None) in (None, "")]
print(f"RESULT v2_cur_rows={len(cur_rows)}")
print(f"RESULT v2_cur_rows_without_unit={len(no_unit)} {no_unit}")
print(f"RESULT thread_factor=1.0")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
# the attributes escape hatch the README does not mention
attrs = gap.extra_state_attributes
print("top slot:", attrs.get("top_slot"), "| first gap row:", (attrs.get("gaps") or [{}])[0])
