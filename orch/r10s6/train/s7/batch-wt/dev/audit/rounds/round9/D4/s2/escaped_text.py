"""D4-s2 harness: an error text the flow shows carries literal "\\u00XX" escapes.

Metric (one line): for the error keys the real config-flow ``dhw`` step and
options-flow ``hot_water`` step RETURN when the hot water minimum is within 5 °C
of the setpoint, the number of (flow, language) error texts whose displayed
string contains a literal backslash-u escape (regex ``\\\\u[0-9a-fA-F]{4}``), and
the number of garbled characters in them.

Count key: the ``errors`` values the production steps deliver, looked up where
the frontend looks (``<flow>.error.<key>`` of translations/en.json and sv.json)
AFTER json.loads -- i.e. the text a user reads. Home Assistant's frontend formats
it with ICU MessageFormat, in which a backslash is not an escape character, so the
sequence is printed verbatim (inference: no HA frontend here).

Command (from the export root):
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub \
      /home/claude/venv314/bin/python tools/audit/round9/D4/s2/escaped_text.py [--perturb]
    --perturb  the one-edit fix in memory: decode the literal escapes in the loaded
               translation texts (write the characters themselves) -> both counts go to 0.

Expected at baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (tolerance exact, counts):
    RESULT escaped_error_texts_reached=4 (config+options x en+sv), RESULT garbled_chars_sv=9 per text,
    RESULT garbled_chars_en=1 per text; null control RESULT escaped_other_error_texts=0 (every other
    error text of both flows); seam RESULT escaped_texts_all_files=6 (strings.json, en.json, sv.json x config/options).
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

from heatpump_optimizer import config_flow, const  # noqa: E402

_P0 = time.process_time()
_T0 = time.thread_time()
PERTURB = "--perturb" in sys.argv
ESC = re.compile(r"\\u[0-9a-fA-F]{4}")
COMP = pathlib.Path("custom_components/heatpump_optimizer")


def _load(name):
    tree = json.loads((COMP / name).read_text())
    if PERTURB:
        def fix(node):
            if isinstance(node, dict):
                return {k: fix(v) for k, v in node.items()}
            if isinstance(node, str):
                return ESC.sub(lambda m: chr(int(m.group(0)[2:], 16)), node)
            return node
        tree = fix(tree)
    return tree


FILES = {"en": _load("translations/en.json"), "sv": _load("translations/sv.json")}


async def _drive():
    # Config flow, dhw page: the shipped defaults with the minimum 2 °C under the setpoint.
    flow = config_flow.HeatPumpOptimizerConfigFlow()
    flow.hass = FakeHass()
    page = await flow.async_step_dhw()
    answers = {}
    for key in page["data_schema"].schema:
        try:
            answers[str(key.schema)] = key.default()
        except Exception:
            pass
    answers[const.CONF_DHW_SETPOINT] = 55.0
    answers[const.CONF_DHW_MIN_TEMP] = 53.0
    cfg = await flow.async_step_dhw(answers)
    # Options flow, hot water page: same pair.
    oflow = config_flow.HeatPumpOptimizerOptionsFlow(
        FakeEntry(data={"tibber_token": "x", "weather_entity": "weather.home"},
                  options={const.CONF_DHW_SETPOINT: 55.0})
    )
    oflow.hass = FakeHass()
    opt = await oflow.async_step_hot_water({
        "schedule": {const.CONF_DHW_WINDOWS: "06:00-08:30, 17:00-22:00"},
        "temperatures": {const.CONF_DHW_MIN_TEMP: 53.0, const.CONF_DHW_SETPOINT: 55.0},
    })
    return {"config": cfg, "options": opt}


res = asyncio.run(_drive())
reached = 0
chars = {"en": 0, "sv": 0}
reached_keys = {}
for flow_name, result in res.items():
    keys = sorted(set((result.get("errors") or {}).values()))
    reached_keys[flow_name] = keys
    print(f"# {flow_name}: step={result.get('step_id')} errors={result.get('errors')}")
    for lang, tree in FILES.items():
        for key in keys:
            text = tree[flow_name]["error"].get(key, "")
            hits = ESC.findall(text)
            if hits:
                reached += 1
                chars[lang] = len(hits)
                print(f"#   {lang} {flow_name}.error.{key}: {text}")
print(f"RESULT escaped_error_texts_reached={reached} count")
print(f"RESULT garbled_chars_en={chars['en']} count")
print(f"RESULT garbled_chars_sv={chars['sv']} count")

# Null control: every OTHER error text of both flows, same languages.
other = 0
for lang, tree in FILES.items():
    for flow_name in ("config", "options"):
        for key, text in tree[flow_name]["error"].items():
            if key in reached_keys.get(flow_name, []):
                continue
            other += bool(ESC.search(text))
print(f"RESULT escaped_other_error_texts={other} count")


# Seam: every translation leaf in every shipped language file.
def _leaves(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from _leaves(v, f"{path}.{k}")
    elif isinstance(node, str):
        yield path, node


seam = 0
for name in ["../strings.json"] + sorted(p.name for p in (COMP / "translations").glob("*.json")):
    tree = FILES.get(name[:-5]) or _load(f"translations/{name}")
    for path, text in _leaves(tree):
        if ESC.search(text):
            seam += 1
            print(f"#   seam {name}{path}")
print(f"RESULT escaped_texts_all_files={seam} count")

_p, _t = time.process_time() - _P0, time.thread_time() - _T0
print(f"RESULT thread_factor={(_p / _t) if _t > 0 else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    _swap = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")]
    print(f"RESULT swapins={_swap[0].split()[1] if _swap else 0}")
except OSError:
    print("RESULT swapins=0")
