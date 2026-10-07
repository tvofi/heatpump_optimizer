"""D4-s2 harness: a money field on the options flow that shows SEK to a non-SEK install.

Metric (one line): across every options-flow page the real
``HeatPumpOptimizerOptionsFlow`` renders for an install whose Home Assistant
currency is EUR (wood furnace on, so its block renders), the number of
NumberSelector fields whose unit_of_measurement names a currency other than
``currency.resolve_currency(hass)``.

Count key: the ``unit_of_measurement`` the production selector DELIVERS to the
form (``selector.config``), per rendered field -- not the field's key, whose
legacy ``_sek_`` spelling is storage and not display. A fix that derives the
unit from ``resolve_currency(hass)`` (as the grid-fee and compressor fields
already do through ``_ByHass``) moves the count; renaming a key does not.

Command (from the export root):
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub \
      /home/claude/venv314/bin/python tools/audit/round9/D4/s2/currency_units.py [--currency EUR] [--perturb]
    --currency SEK  null control: the instance currency the hard-coded unit happens to fit -> 0
    --perturb       in-memory one-row fix: the wood-price row's widget becomes
                    _ByHass(lambda hass: _number(0, 10000, 10, f"{resolve_currency(hass)}/m³")) -> 0

Expected at baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (tolerance exact, counts):
    RESULT money_fields=4, RESULT foreign_currency_units=1 (EUR) ; 0 under --currency SEK ; 0 under --perturb
Machine: B9 cloud container (4 cores, Linux); counts are contention-immune.
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
import re
import sys
import time

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass  # noqa: E402

import golden  # noqa: E402  (schema walk helper _nested_schema)
from heatpump_optimizer import config_flow, const  # noqa: E402
from heatpump_optimizer.currency import resolve_currency  # noqa: E402

_P0 = time.process_time()
_T0 = time.thread_time()

CURRENCY = sys.argv[sys.argv.index("--currency") + 1] if "--currency" in sys.argv else "EUR"
PERTURB = "--perturb" in sys.argv
CODES = re.compile(r"\b(SEK|EUR|NOK|DKK|GBP|USD|CHF|PLN)\b")

if PERTURB:
    rows = list(config_flow._OPTION_FIELDS)
    for i, row in enumerate(rows):
        if row.key == const.CONF_WOOD_PRICE_SEK_M3:
            rows[i] = row._replace(
                widget=config_flow._ByHass(
                    lambda hass: config_flow._number(0, 10000, 10, f"{resolve_currency(hass)}/m³")
                )
            )
    config_flow._OPTION_FIELDS = tuple(rows)


def _walk(schema):
    for key, value in (schema.schema.items() if schema else []):
        inner = golden._nested_schema(value)
        if inner is not None:
            yield from _walk(inner)
        else:
            yield str(getattr(key, "schema", key)), value


# Wood furnace on and the booleans that gate blocks, so every money field renders.
OPTIONS = {
    const.CONF_WOOD_FURNACE_ENABLED: True,
    const.CONF_EXTERNAL_HEAT_ENABLED: True,
}
hass = FakeHass()
hass.config.currency = CURRENCY
flow = config_flow.HeatPumpOptimizerOptionsFlow(
    FakeEntry(data={"tibber_token": "x", "weather_entity": "weather.home"}, options=OPTIONS)
)
flow.hass = hass
resolved = resolve_currency(hass)

money, foreign = [], []
for step in config_flow.HeatPumpOptimizerOptionsFlow._MENU_LABELS:
    result = asyncio.run(getattr(flow, f"async_step_{step}")())
    for key, value in _walk(result.get("data_schema")):
        unit = (getattr(value, "config", None) or {}).get("unit_of_measurement") or ""
        codes = CODES.findall(unit)
        if not codes:
            continue
        money.append((step, key, unit))
        if any(c != resolved for c in codes):
            foreign.append((step, key, unit))

print(f"# instance currency={CURRENCY} resolved={resolved} perturb={PERTURB}")
for step, key, unit in money:
    mark = "FOREIGN" if (step, key, unit) in foreign else "ok"
    print(f"#   {mark:7} {step}.{key}: {unit}")
print(f"RESULT money_fields={len(money)} count")
print(f"RESULT foreign_currency_units={len(foreign)} count")

# The static surfaces of the same unit, which no hass can resolve (services.yaml's
# selector unit and the service field's own description text): reported beside the
# rendered count, not part of it, and unmoved by --perturb (it edits the form row only).
import json  # noqa: E402
import pathlib  # noqa: E402

_comp = pathlib.Path("custom_components/heatpump_optimizer")
_static = []
for _n, _line in enumerate((_comp / "services.yaml").read_text().splitlines(), 1):
    if "unit_of_measurement" in _line and CODES.search(_line):
        _static.append(f"services.yaml:{_n}: {_line.strip()}")


def _texts(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from _texts(v, f"{path}.{k}")
    elif isinstance(node, str):
        yield path, node


for _path, _text in _texts(json.loads((_comp / "translations/en.json").read_text())):
    if CODES.search(_text):
        _static.append(f"en.json{_path}: {_text}")
for _s in _static:
    print(f"#   static {_s}")
print(f"RESULT static_fixed_currency_texts={len(_static)} count")

_p, _t = time.process_time() - _P0, time.thread_time() - _T0
print(f"RESULT thread_factor={(_p / _t) if _t > 0 else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    _swap = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")]
    print(f"RESULT swapins={_swap[0].split()[1] if _swap else 0}")
except OSError:
    print("RESULT swapins=0")
