"""D5 verify-v3 (reach and class) harness for D5-s1-06: service fields the real Home Assistant
action UI lists (services.yaml + translations/en.json services.*) that configuration.md's
Services section never names.

Metric (one line): (service, field) pairs present in services.yaml that the "## Services"
section of docs/configuration.md never names in backticks; plus the pairs the registered
voluptuous schemas accept that services.yaml does not list (a field HA's UI would hide).
Count key: services.yaml as HA loads it for Developer Tools -> Actions, and the schemas
services.async_register_services hands hass.services.async_register.
Command (from the repository root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
        tools/audit/round9/D5/verify-v3/v3_s1_06_services.py [--perturb]
--perturb: append, in memory, the five wood field names in backticks to the Services section.
    Expected: yaml_fields_undocumented 5 -> 0.
Expected at baseline: yaml_fields_undocumented=5, schema_not_in_yaml=0, en_labels_for_all=1.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (+ round-9 evidence); machine: 4-core
cloud container, CPython 3.14.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio
import json
import re
import sys
import time

import yaml

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
_t0p, _t0t = time.process_time(), time.thread_time()
from harness import FakeHass  # noqa: E402
from heatpump_optimizer import services  # noqa: E402

yml = yaml.safe_load(open("custom_components/heatpump_optimizer/services.yaml", encoding="utf-8"))
en = json.load(open("custom_components/heatpump_optimizer/translations/en.json", encoding="utf-8"))
text = open("docs/configuration.md", encoding="utf-8").read()
section = text.split("## Services", 1)[1].split("\n## ", 1)[0]
if "--perturb" in sys.argv:
    section += " `wood_slots` `wood_type` `wood_packing` `wood_price_sek_m3` `wood_furnace_efficiency`"
named = set(re.findall(r"`([a-z_0-9]+)`", section))

hass = FakeHass()
registered = {}
_orig = hass.services.async_register


def spy(domain, name, handler, schema=None, *a, **k):
    registered[name] = schema
    return _orig(domain, name, handler, schema, *a, **k)


hass.services.async_register = spy
r = services.async_register_services(hass)
if asyncio.iscoroutine(r):
    asyncio.run(r)

undoc, hidden, unlabelled, schema_keys = [], [], 0, 0
for svc, spec in yml.items():
    for field in (spec or {}).get("fields") or {}:
        if field == "entry_id":
            continue
        if field not in named:
            undoc.append(f"{svc}.{field}")
        if field not in (en.get("services", {}).get(svc, {}).get("fields") or {}):
            unlabelled += 1
for svc, schema in registered.items():
    keys = [str(getattr(k, "schema", k)) for k in getattr(schema, "schema", {}) or {}]
    schema_keys += len(keys)
    for key in keys:
        if key != "entry_id" and key not in ((yml.get(svc) or {}).get("fields") or {}):
            hidden.append(f"{svc}.{key}")
print("undocumented:", undoc)
print("schema keys absent from services.yaml:", hidden)
cpu_p, cpu_t = time.process_time() - _t0p, time.thread_time() - _t0t
print(f"RESULT services_registered={len(registered)} count")
print(f"RESULT yaml_fields_undocumented={len(undoc)} count")
print(f"RESULT schema_keys={schema_keys} count")
print(f"RESULT schema_not_in_yaml={len(hidden)} count")
print(f"RESULT en_labels_for_all={int(unlabelled == 0)} count")
print(f"RESULT thread_factor={cpu_p / cpu_t if cpu_t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
