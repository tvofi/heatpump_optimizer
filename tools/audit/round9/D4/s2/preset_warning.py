"""D4-s2 harness: the zones page holds derived values but never shows the overwrite warning.

Metric (one line): with the building questionnaire's derivation armed on a
two-zone install, the number of questionnaire-derived fields
(``config_flow.DERIVED_THERMAL_KEYS``) the real options flow renders on a page
whose displayed description (translations en/sv, placeholders substituted) does
NOT contain the preset-overwrite warning -- counted per language.

Count key: the field keys the production ``async_step_thermal_model`` /
``async_step_thermal_model_zones`` render, intersected with DERIVED_THERMAL_KEYS,
and the description text the frontend would show: the page's ``description``
from translations/<lang>.json formatted with the ``description_placeholders``
the step RETURNED. A step that computes the warning but whose description never
references it counts; a text a fix adds to the description does not need the
step to change.

Command (from the export root):
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub \
      /home/claude/venv314/bin/python tools/audit/round9/D4/s2/preset_warning.py [--perturb] [--disarmed]
    --perturb   one-edit fix in memory: append "\\n\\n{preset_warning}" to
                options.step.thermal_model_zones.description in both languages -> 0
    --disarmed  null control: building_preset_enabled False -> the warning is "" everywhere,
                so the unwarned count equals the derived-field count and the warned count is 0

Expected at baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (tolerance exact, counts):
    RESULT derived_fields_rendered=10, RESULT unwarned_derived_fields_en=6, _sv=6,
    RESULT warned_derived_fields_en=4 (thermal_model's own four)
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
import sys
import time

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass  # noqa: E402

import golden  # noqa: E402
from heatpump_optimizer import config_flow, const  # noqa: E402

_P0 = time.process_time()
_T0 = time.thread_time()
PERTURB = "--perturb" in sys.argv
DISARMED = "--disarmed" in sys.argv
COMP = pathlib.Path("custom_components/heatpump_optimizer")
FILES = {l: json.loads((COMP / f"translations/{l}.json").read_text()) for l in ("en", "sv")}
if PERTURB:
    for tree in FILES.values():
        tree["options"]["step"]["thermal_model_zones"]["description"] += "\n\n{preset_warning}"


def _walk(schema):
    for key, value in (schema.schema.items() if schema else []):
        inner = golden._nested_schema(value)
        if inner is not None:
            yield from _walk(inner)
        else:
            yield str(getattr(key, "schema", key))


# A two-zone install whose questionnaire derivation is armed: the derived values
# stored, as the building page's save writes them.
answers = {
    const.CONF_BUILDING_STRUCTURE: "timber_slab", const.CONF_BUILDING_ERA: "1980_2005",
    const.CONF_BUILDING_FOUNDATION: "none", const.CONF_HEATED_AREA: 140.0,
    const.CONF_UPPER_EMITTER: "radiators", const.CONF_LOWER_EMITTER: "floor",
}
seed = {const.CONF_UPPER_FLOOR_THERMAL_MASS: 3.0}
derived = config_flow._derive_preset(answers, seed)
options = {**seed, **derived, const.CONF_BUILDING_PRESET_ENABLED: not DISARMED}

rendered = 0
unwarned = {"en": 0, "sv": 0}
warned = {"en": 0, "sv": 0}
for lang in FILES:
    hass = FakeHass()
    hass.config.language = lang
    flow = config_flow.HeatPumpOptimizerOptionsFlow(
        FakeEntry(data={"tibber_token": "x", "weather_entity": "weather.home"}, options=options)
    )
    flow.hass = hass
    warning = config_flow.PRESET_WARNING[lang]
    for step in ("thermal_model", "thermal_model_zones"):
        result = asyncio.run(getattr(flow, f"async_step_{step}")())
        keys = [k for k in _walk(result.get("data_schema")) if k in config_flow.DERIVED_THERMAL_KEYS]
        shown = FILES[lang]["options"]["step"][step].get("description", "").format(
            **(result.get("description_placeholders") or {})
        )
        has = warning in shown
        if lang == "en":
            rendered += len(keys)
        (warned if has else unwarned)[lang] += len(keys)
        print(f"# {lang} {step}: derived fields={keys} warning shown={has}")

print(f"# derived keys stored: {sorted(k for k in derived if k in config_flow.DERIVED_THERMAL_KEYS)}")
print(f"RESULT derived_fields_rendered={rendered} count")
for lang in FILES:
    print(f"RESULT unwarned_derived_fields_{lang}={unwarned[lang]} count")
    print(f"RESULT warned_derived_fields_{lang}={warned[lang]} count")

_p, _t = time.process_time() - _P0, time.thread_time() - _T0
print(f"RESULT thread_factor={(_p / _t) if _t > 0 else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    _swap = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")]
    print(f"RESULT swapins={_swap[0].split()[1] if _swap else 0}")
except OSError:
    print("RESULT swapins=0")
