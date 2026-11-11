"""D4-s2 harness: help texts spell units differently from the selectors beside them.

Metric (one line): over every field the real config and options flows render,
the number of (field, language) help texts (data_description) that write a
temperature as "<number> C" or an area as "m2" -- while the flows' own selectors
use "°C" and "m²" -- per language.

Count key: the help text the frontend shows for a RENDERED field
(``<flow>.step.<page>[.sections.<s>].data_description.<key>`` of
translations/<lang>.json), matched by ``\\d C\\b`` (a digit, a space, a bare C)
and ``\\bm2\\b``; the selectors' own units are read off the rendered
``NumberSelector`` configs as the house style (control).

Command (from the export root):
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub \
      /home/claude/venv314/bin/python tools/audit/round9/D4/s2/unit_typography.py [--perturb]
    --perturb  in-memory text fix: "<n> C" -> "<n> °C", "m2" -> "m²" in the loaded
               translations -> both counts go to 0.

Expected at baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (tolerance exact, counts):
    RESULT selector_units_degC=31, RESULT selector_units_bareC=0 (house style);
    RESULT bare_unit_help_texts_en=8, RESULT bare_unit_help_texts_sv=8
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
import json
import pathlib
import re
import sys
import time

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass  # noqa: E402

import golden  # noqa: E402
from heatpump_optimizer import config_flow as cf, const  # noqa: E402

_P0 = time.process_time()
_T0 = time.thread_time()
PERTURB = "--perturb" in sys.argv
BARE = re.compile(r"(\d) C\b|\bm2\b")
COMP = pathlib.Path("custom_components/heatpump_optimizer")
FILES = {l: json.loads((COMP / f"translations/{l}.json").read_text()) for l in ("en", "sv")}


def _fix(text):
    return BARE.sub(lambda m: f"{m.group(1)} °C" if m.group(1) else "m²", text)


def _walk(schema, sec=None):
    for key, value in (schema.schema.items() if schema else []):
        inner = golden._nested_schema(value)
        if inner is not None:
            yield from _walk(inner, str(key))
        else:
            yield sec, str(getattr(key, "schema", key)), value


units = {"°C": 0, "C": 0, "m²": 0, "m2": 0}
hits = {"en": set(), "sv": set()}


def _score(flow_name, result):
    step = result.get("step_id")
    for sec, key, value in _walk(result.get("data_schema")):
        unit = (getattr(value, "config", None) or {}).get("unit_of_measurement")
        if unit in units:
            units[unit] += 1
        for lang, tree in FILES.items():
            node = tree[flow_name]["step"].get(step, {})
            if sec is not None:
                node = (node.get("sections") or {}).get(sec, {})
            text = node.get("data_description", {}).get(key, "")
            if PERTURB:
                text = _fix(text)
            if BARE.search(text):
                hits[lang].add((flow_name, step, key))


init = cf.HeatPumpOptimizerConfigFlow()
init.hass = FakeHass()
for s in ("user", "user_sensors", "quick_setup", "temperature", "building_describe",
          "building_extras", "thermal", "zones", "dhw", "weather_sensitivity"):
    _score("config", asyncio.run(getattr(init, f"async_step_{s}")()))
flow = cf.HeatPumpOptimizerOptionsFlow(FakeEntry(
    data={"tibber_token": "x", "weather_entity": "weather.home"},
    options={const.CONF_WOOD_FURNACE_ENABLED: True}))
flow.hass = FakeHass()
for s in cf.HeatPumpOptimizerOptionsFlow._MENU_LABELS:
    _score("options", asyncio.run(getattr(flow, f"async_step_{s}")()))

for lang in hits:
    for h in sorted(hits[lang]):
        print(f"#   {lang} {'.'.join(h)}")
print(f"RESULT selector_units_degC={units['°C']} count")
print(f"RESULT selector_units_bareC={units['C']} count")
print(f"RESULT selector_units_m2_superscript={units['m²']} count")
print(f"RESULT bare_unit_help_texts_en={len(hits['en'])} count")
print(f"RESULT bare_unit_help_texts_sv={len(hits['sv'])} count")

_p, _t = time.process_time() - _P0, time.thread_time() - _T0
print(f"RESULT thread_factor={(_p / _t) if _t > 0 else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    _swap = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")]
    print(f"RESULT swapins={_swap[0].split()[1] if _swap else 0}")
except OSError:
    print("RESULT swapins=0")
