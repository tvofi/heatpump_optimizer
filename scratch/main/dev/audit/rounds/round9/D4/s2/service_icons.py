"""D4-s2 harness: no registered service has an icon in icons.json.

Metric (one line): of the services the production
``services.async_register_services`` registers for the domain, the number with
no entry under ``icons.json["services"]`` (Home Assistant's service-icon
translation key), against the entity icons of the same file as control.

Count key: the service names the production registration DELIVERS to
``hass.services`` (not services.yaml's keys), looked up in
custom_components/heatpump_optimizer/icons.json as Home Assistant's frontend
does for a service action (``services.<service>`` -> ``mdi:*``, or
``{"service": "mdi:*"}``).

Command (from the export root):
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub \
      /home/claude/venv314/bin/python tools/audit/round9/D4/s2/service_icons.py [--perturb]
    --perturb  in-memory icons.json edit: a "services" block with one mdi icon per
               registered service -> services_without_icon goes to 0.
Null control: RESULT entity_keys_without_icon -- the same file's entity section, which
the suite already pins (0).

Expected at baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (tolerance exact, counts):
    RESULT services_registered=12, RESULT services_without_icon=12, RESULT entity_keys_without_icon=0,
    RESULT service_names_or_fields_untranslated=0
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

import json
import pathlib
import sys
import time

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeHass  # noqa: E402

from heatpump_optimizer import const, services  # noqa: E402

_P0 = time.process_time()
_T0 = time.thread_time()
COMP = pathlib.Path("custom_components/heatpump_optimizer")
icons = json.loads((COMP / "icons.json").read_text())

hass = FakeHass()
services.async_register_services(hass)
registered = sorted(hass.services._registry.get(const.DOMAIN, {}))
if "--perturb" in sys.argv:
    icons["services"] = {name: {"service": "mdi:heat-pump"} for name in registered}

have = icons.get("services", {})
missing = [s for s in registered if not (
    isinstance(have.get(s), str) or (isinstance(have.get(s), dict) and have[s].get("service"))
)]
print(f"# registered: {registered}")
print(f"# without icon: {missing}")
print(f"RESULT services_registered={len(registered)} count")
print(f"RESULT services_without_icon={len(missing)} count")

# Control: the entity section of the same file, keyed on the strings' own entity keys.
strings = json.loads((COMP / "strings.json").read_text())
ent_missing = [
    f"{plat}.{key}"
    for plat, keys in strings.get("entity", {}).items()
    for key in keys
    if key not in icons.get("entity", {}).get(plat, {})
]
print(f"RESULT entity_keys_without_icon={len(ent_missing)} count")

# Also: every registered service and each of its schema fields has a name in en and sv.
_untrans = 0
_nfields = 0
for _lang in ("en", "sv"):
    _tree = json.loads((COMP / f"translations/{_lang}.json").read_text()).get("services", {})
    for _name in registered:
        _schema = hass.services._schemas.get((const.DOMAIN, _name))
        _fields = [str(getattr(k, "schema", k)) for k in (getattr(_schema, "schema", None) or {})] \
            if isinstance(getattr(_schema, "schema", None), dict) else []
        _nfields += len(_fields)
        if _name not in _tree:
            _untrans += 1
            continue
        _untrans += sum(1 for f in _fields if f not in _tree[_name].get("fields", {}))
print(f"RESULT service_fields_checked={_nfields} count")
print(f"RESULT service_names_or_fields_untranslated={_untrans} count")

_p, _t = time.process_time() - _P0, time.thread_time() - _T0
print(f"RESULT thread_factor={(_p / _t) if _t > 0 else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    _swap = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")]
    print(f"RESULT swapins={_swap[0].split()[1] if _swap else 0}")
except OSError:
    print("RESULT swapins=0")
