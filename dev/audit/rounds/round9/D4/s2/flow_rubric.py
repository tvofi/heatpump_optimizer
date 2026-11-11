"""D4-s2 harness: the config/options flow rubric numbers (D4.M2), per page.

Metric (one line): per page the real flows render, the field count, the number of
sections, the rendered fields with no label / no help text in translations/en.json
and sv.json, and the number of sv texts identical to en; plus the screens from
install to a created entry on each first-run path (the flow's own step_ids).

Count key: the field keys the production ``async_step_<page>`` RETURNS (sections
flattened), looked up where the frontend looks for that flow and step.

Command (from the export root):
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub \
      /home/claude/venv314/bin/python tools/audit/round9/D4/s2/flow_rubric.py
Perturbation (for the rendered-help count): --drop-help removes one data_description
(config.step.temperature.target_temperature) in memory -> missing_help_total goes up by 1.

Expected at baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (tolerance exact, counts):
    RESULT pages=39, RESULT missing_label_total=0, RESULT missing_help_total=0 (defaults render),
    RESULT max_fields_on_a_page=24, RESULT flat_pages_over_10_fields=5,
    RESULT sv_labels_identical_to_en=0, RESULT unsupplied_placeholders=0,
    RESULT screens_finish_now=4, RESULT screens_quick=7, RESULT screens_expert=10
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
from heatpump_optimizer import config_flow as cf, const  # noqa: E402

_P0 = time.process_time()
_T0 = time.thread_time()
COMP = pathlib.Path("custom_components/heatpump_optimizer")
FILES = {l: json.loads((COMP / f"translations/{l}.json").read_text()) for l in ("en", "sv")}
if "--drop-help" in sys.argv:
    del FILES["en"]["config"]["step"]["temperature"]["data_description"]["target_temperature"]


def _walk(schema, sec=None):
    for key, value in (schema.schema.items() if schema else []):
        inner = golden._nested_schema(value)
        if inner is not None:
            yield from _walk(inner, str(key))
        else:
            yield sec, str(getattr(key, "schema", key))


rows = []
placeholder_gaps = []


def _placeholders(flow_name, result):
    """Braces a shown text references that the step did not supply (rendered verbatim)."""
    import re as _re
    given = set((result.get("description_placeholders") or {}).keys())
    for lang, tree in FILES.items():
        node = tree[flow_name]["step"].get(result.get("step_id"), {})
        texts = [node.get("description", ""), node.get("title", "")]
        texts += list((node.get("data_description") or {}).values())
        for sec in (node.get("sections") or {}).values():
            texts += [sec.get("description", ""), sec.get("name", "")]
            texts += list((sec.get("data_description") or {}).values())
        used = set().union(*[set(_re.findall(r"\{(\w+)\}", t or "")) for t in texts])
        for name in sorted(used - given):
            placeholder_gaps.append(f"{lang}:{flow_name}.{result.get('step_id')}:{name}")


def _score(flow_name, result):
    step = result.get("step_id")
    _placeholders(flow_name, result)
    if result.get("type") != "form":
        rows.append((flow_name, step, "menu", len(result.get("menu_options") or {}), 0, 0, 0, 0))
        return
    fields = list(_walk(result.get("data_schema")))
    sections = {s for s, _ in fields if s}
    miss_l = miss_h = 0
    for lang, tree in FILES.items():
        node = tree[flow_name]["step"].get(step, {})
        for sec, key in fields:
            n = node if sec is None else (node.get("sections") or {}).get(sec, {})
            if lang == "en":
                miss_l += key not in n.get("data", {})
                miss_h += key not in n.get("data_description", {})
    en_node = FILES["en"][flow_name]["step"].get(step, {})
    sv_node = FILES["sv"][flow_name]["step"].get(step, {})
    same = sum(1 for k, v in en_node.get("data", {}).items() if sv_node.get("data", {}).get(k) == v)
    rows.append((flow_name, step, "form", len(fields), len(sections), miss_l, miss_h, same))


init = cf.HeatPumpOptimizerConfigFlow()
init.hass = FakeHass()
for s in ("user", "user_sensors", "finish_setup", "quick_setup", "device_prefill", "temperature",
          "building", "building_describe", "building_extras", "thermal", "zones", "dhw",
          "weather_sensitivity", "setup_overview"):
    _score("config", asyncio.run(getattr(init, f"async_step_{s}")()))
flow = cf.HeatPumpOptimizerOptionsFlow(FakeEntry(
    data={"tibber_token": "x", "weather_entity": "weather.home"},
    options={const.CONF_WOOD_FURNACE_ENABLED: True}))
flow.hass = FakeHass()
for s in ["init", "advanced"] + list(cf.HeatPumpOptimizerOptionsFlow._MENU_LABELS):
    _score("options", asyncio.run(getattr(flow, f"async_step_{s}")()))

print("# flow      page                    kind  fields sections no_label no_help sv==en_labels")
for r in rows:
    print(f"# {r[0]:8} {r[1]:24} {r[2]:5} {r[3]:6} {r[4]:8} {r[5]:8} {r[6]:7} {r[7]:6}")
forms = [r for r in rows if r[2] == "form"]
print(f"RESULT pages={len(rows)} count")
print(f"RESULT max_fields_on_a_page={max(r[3] for r in forms)} count")
print(f"RESULT flat_pages_over_10_fields={sum(1 for r in forms if r[3] > 10 and r[4] == 0)} count")
print(f"RESULT missing_label_total={sum(r[5] for r in forms)} count")
print(f"RESULT missing_help_total={sum(r[6] for r in forms)} count")
print(f"RESULT sv_labels_identical_to_en={sum(r[7] for r in forms)} count")
print(f"RESULT unsupplied_placeholders={len(placeholder_gaps)} count {placeholder_gaps}")


# Screens from install to create_entry, each page submitted as pre-filled.
def _prefilled(result):
    out = {}
    for key in (result.get("data_schema").schema if result.get("data_schema") else {}):
        try:
            out[str(key.schema)] = key.default()
        except Exception:
            pass
    return out


async def _path(kind):
    f = cf.HeatPumpOptimizerConfigFlow()
    f.hass = FakeHass()
    seen = ["user"]
    r = await f.async_step_user({"name": "HPO", const.CONF_PRICE_SOURCE: "entity",
                                 const.CONF_PRICE_ENTITY: "sensor.nordpool",
                                 const.CONF_WEATHER_ENTITY: "weather.home"})
    while r.get("type") in ("form", "menu"):
        step = r["step_id"]
        seen.append(step)
        if len(seen) > 30:
            return seen, "loop"
        if r["type"] == "menu":
            # The finish menu is met again after a sub-path; the second time, finish.
            again = seen.count("finish_setup") > 1
            choice = {"finish_setup": "finish_now" if again else {
                          "quick": "quick_setup", "finish_now": "finish_now",
                          "expert": "temperature"}[kind],
                      "building": "thermal"}[step]
            r = await getattr(f, f"async_step_{choice}")()
            continue
        if step == "device_prefill":
            r = await f.async_step_device_prefill({cf._PREFILL_DEVICE: None})
            continue
        r = await getattr(f, f"async_step_{step}")(_prefilled(r))
    return seen, r.get("type")


for kind in ("finish_now", "quick", "expert"):
    seen, end = asyncio.run(_path(kind))
    print(f"# path {kind}: {' -> '.join(seen)} -> {end}")
    print(f"RESULT screens_{kind}={len(seen)} count")

_p, _t = time.process_time() - _P0, time.thread_time() - _T0
print(f"RESULT thread_factor={(_p / _t) if _t > 0 else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    _swap = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")]
    print(f"RESULT swapins={_swap[0].split()[1] if _swap else 0}")
except OSError:
    print("RESULT swapins=0")
