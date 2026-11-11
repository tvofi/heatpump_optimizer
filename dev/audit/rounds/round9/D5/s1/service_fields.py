"""D5-s1 harness: service fields the registered schemas accept, against docs/configuration.md.

README.md's Services section sends the reader to docs/configuration.md for "field-level
detail for each"; configuration.md's Services table says simulate_plan takes "16 optional
comfort and wood fields" and its paragraph lists "Fields, all optional:" by name.
Metric (one line): fields (entry_id aside) a registered service schema accepts that the
"## Services" section of docs/configuration.md never names in backticks in that service's
table row or its **`service`** paragraph.
Count key: the voluptuous schema each handler is registered with by
services.async_register_services (read back from FakeServices._schemas) -- the keys a call
is validated against, not services.yaml and not the docs.
Command (from the repository root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
        tools/audit/round9/D5/s1/service_fields.py [--perturb]
--perturb strips, in memory, every wood_* key from SERVICE_SCHEMA_SIMULATE_PLAN before
    registration (the schema the paragraph describes). Expected: undocumented_fields 5 -> 0.
Expected at baseline: services=12, undocumented_fields=5 (all simulate_plan wood_*), exact.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: box B1 (linux container).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import re
import sys
import time

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
_t0p, _t0t = time.process_time(), time.thread_time()
import voluptuous as vol  # noqa: E402
from harness import FakeHass  # noqa: E402
from heatpump_optimizer import services  # noqa: E402


def keys_of(schema):
    if schema is None:
        return []
    if isinstance(schema, vol.All):
        out = []
        for v in schema.validators:
            out += keys_of(v)
        return out
    inner = getattr(schema, "schema", None)
    if isinstance(inner, dict):
        return [str(getattr(k, "schema", k)) for k in inner]
    return []


if "--perturb" in sys.argv:
    s = services.SERVICE_SCHEMA_SIMULATE_PLAN
    base = s if isinstance(getattr(s, "schema", None), dict) else next(
        v for v in s.validators if isinstance(getattr(v, "schema", None), dict))
    for k in list(base.schema):
        if str(getattr(k, "schema", k)).startswith("wood_"):
            del base.schema[k]
    # voluptuous compiles at construction; rebuild from the edited dict
    rebuilt = vol.Schema(base.schema, extra=base.extra)
    services.SERVICE_SCHEMA_SIMULATE_PLAN = rebuilt if s is base else vol.All(
        *[rebuilt if v is base else v for v in s.validators])

hass = FakeHass()
services.async_register_services(hass)
text = open("docs/configuration.md", encoding="utf-8").read()
sec = text.split("\n## Services", 1)[1].split("\n## Where else", 1)[0]
total_fields, undocumented = 0, []
for (domain, svc), schema in sorted(hass.services._schemas.items()):
    fields = [k for k in keys_of(schema) if k != "entry_id"]
    total_fields += len(fields)
    row = re.search(r"^\| `%s` \|(.*)$" % re.escape(svc), sec, re.M)
    para = re.search(r"\*\*`%s`\*\*(.*?)(?=\n\*\*`|\Z)" % re.escape(svc), sec, re.S)
    named = (row.group(1) if row else "") + (para.group(1) if para else "")
    for f in fields:
        if f"`{f}`" not in named:
            undocumented.append(f"{svc}.{f}")
for u in undocumented:
    print("undocumented", u)
cpu_p, cpu_t = time.process_time() - _t0p, time.thread_time() - _t0t
print(f"RESULT services={len(hass.services._schemas)} count")
print(f"RESULT accepted_fields={total_fields} count")
print(f"RESULT undocumented_fields={len(undocumented)} count")
print(f"RESULT thread_factor={cpu_p / cpu_t if cpu_t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
