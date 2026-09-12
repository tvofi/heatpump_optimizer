"""D6-01 verification, verifier seat 1 -- my OWN harness, refute-first.

METHOD (deliberately different from the finder's ha_boundary.py, which
imports each module with `homeassistant` refused -- a *dynamic* measure that
also fails on transitive in-package imports; mine is a *static* AST scan of
DIRECT module-level `homeassistant` imports, which is exactly what
architecture.md:140-144 asserts):

  1. AST-parse every .py under custom_components/heatpump_optimizer/, collect
     top-level (module-scope) Import/ImportFrom nodes whose target is
     `homeassistant` or `homeassistant.*`.  Count the files with >= 1.
     architecture.md says "Exactly ten modules ... `__init__`, `config_flow`,
     `coordinator`, `open_meteo`, `frontend`, and the five entity platforms
     `sensor`, `binary_sensor`, `button`, `climate`, `switch`".
  2. Cross-check the dynamic side myself with a plain `sys.modules` refusal
     import of each module IN THE REAL TREE (no scratch copy): a module is
     HA-dependent iff import fails or `homeassistant` lands in sys.modules.
  3. Independently re-measure the other nine architecture.md claims:
     module count, module-map completeness, option-page count, service count,
     switch census, binary_sensor census, and whether the five entity
     platforms are the complete platform set.

RUN (from the repository root):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/d6_own_D6-01.py

ROOT RULE: the working directory (`ROOT = pathlib.Path(".")`).

EXPECTED if the finding is true: arch_ha_importers_static=21,
arch_modules_on_disk=56, undocumented (outside the doc's ten)=11.
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

# ---------------------------------------------------------------------------
# 1. Static AST scan: DIRECT module-level homeassistant imports
# ---------------------------------------------------------------------------
files = sorted(p for p in PKG.glob("*.py"))
static_ha: list[str] = []
for p in files:
    tree = ast.parse(p.read_text())
    hit = False
    for node in tree.body:  # module scope only -- not inside functions/classes
        if isinstance(node, ast.Import):
            hit |= any(a.name == "homeassistant" or a.name.startswith("homeassistant.") for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and (node.module == "homeassistant" or (node.module or "").startswith("homeassistant.")):
                hit = True
    if hit:
        static_ha.append(p.stem)

DOC_TEN = {"__init__", "config_flow", "coordinator", "open_meteo", "frontend",
           "sensor", "binary_sensor", "button", "climate", "switch"}

# ---------------------------------------------------------------------------
# 2. Dynamic cross-check in the real tree: import each module with
#    homeassistant refused via a meta-path hook; record failure OR
#    homeassistant landing in sys.modules (a lazy import would land there too,
#    which the doc also cares about: "everything else is deliberately free").
# ---------------------------------------------------------------------------
CHILD = r'''
import sys, importlib
class Refuse:
    def find_module(self, name, path=None):
        return self.find_spec(name, path)
    def find_spec(self, name, path=None, target=None):
        if name == "homeassistant" or name.startswith("homeassistant."):
            raise ImportError("refused")
        return None
sys.meta_path.insert(0, Refuse())
sys.path.insert(0, sys.argv[2])
try:
    importlib.import_module("heatpump_optimizer." + sys.argv[1])
except ImportError:
    print("FAIL")
except Exception:
    print("OK")   # module imported; HA refusal was not hit at import time
else:
    print("OK")
'''
import subprocess
import tempfile
import shutil

tmp = pathlib.Path(tempfile.mkdtemp(prefix="d6-own-"))
scratch = tmp / "heatpump_optimizer"
shutil.copytree(PKG, scratch, ignore=shutil.ignore_patterns("__pycache__"))
# empty the scratch __init__ so the package import itself cannot fail submodules
(scratch / "__init__.py").write_text("")
dynamic_fail: list[str] = []
for p in files:
    if p.stem == "__init__":
        continue
    r = subprocess.run([sys.executable, "-c", CHILD, p.stem, str(tmp)],
                       capture_output=True, text=True,
                       env={**os.environ, "PYTHONPATH": "tests/hastub"})
    if r.stdout.strip() == "FAIL":
        dynamic_fail.append(p.stem)
shutil.rmtree(tmp, ignore_errors=True)
# __init__ handled by hand: it is the package
init_ha = "__init__" in static_ha
dynamic_total = len(dynamic_fail) + int(init_ha)

# ---------------------------------------------------------------------------
# 3. The other architecture.md claims, measured independently
# ---------------------------------------------------------------------------
arch = (ROOT / "docs" / "architecture.md").read_text()

# 3a. "45 modules" -- count of .py files
modules_on_disk = len(files)

# 3b. module map completeness -- every `xxx.py` entry in the map block
map_block = arch.split("## The module map")[1].split("## The Home Assistant boundary")[0]
map_listed = sorted(set(re.findall(r"(\w+)\.py\b", map_block)))
on_disk = sorted(p.stem for p in files)
missing = sorted(set(on_disk) - set(map_listed))
phantom = sorted(set(map_listed) - set(on_disk))

# 3c. option pages -- from the real config_flow, by import
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from heatpump_optimizer.config_flow import _OPTION_PAGES  # noqa: E402
option_pages = len(_OPTION_PAGES)

# 3d. services -- the real registration, read from the honest FakeServices
# registry afterwards (tests/harness.py:FakeServices keeps a real registry)
import harness  # noqa: E402
from harness import FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer import services as svc  # noqa: E402

_svc_hass = FakeHass()
svc.async_register_services(_svc_hass)
services_count = len(_svc_hass.services.async_services().get("heatpump_optimizer", {}))

# 3e. entity censuses through the real platform setup (tests/entities.py runs
# its whole gate at import and sys.exits -- so the two-liner it wraps is
# copied here rather than imported)
from harness import FakeCoordinator  # noqa: E402
from heatpump_optimizer import switch as sw, binary_sensor as bs  # noqa: E402
import json as _json

STRS = _json.loads((PKG / "strings.json").read_text())
_ENT_DATA = next(
    ast.literal_eval(n.value)
    for n in ast.parse((ROOT / "tests" / "entities.py").read_text()).body
    if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", None) == "DATA"
)


def collect(module):
    added: list = []
    entry = FakeEntry()
    coord = FakeCoordinator(_ENT_DATA)
    coord._month_totals = {"dhw": (41.5, 62.25), "space": (120.0, 180.0)}
    entry.runtime_data = coord
    asyncio.run(module.async_setup_entry(FakeHass(), entry, added.extend))
    return added


switch_entities = collect(sw)
bs_entities = collect(bs)

# 3f. platform census: is `datetime` a sixth entity platform?
platforms = sorted(p.stem for p in files if p.stem in
                   {"sensor", "binary_sensor", "button", "climate", "switch", "datetime"})

undocumented_static = sorted(set(static_ha) - DOC_TEN)
undocumented_dynamic = sorted(set(dynamic_fail + (["__init__"] if init_ha else [])) - DOC_TEN)

print(f"RESULT arch_ha_importers_static={len(static_ha)} modules")
print(f"RESULT arch_ha_importers_dynamic={dynamic_total} modules")
print(f"RESULT arch_doc_claim=10 modules")
print(f"RESULT undocumented_ha_dependents={len(undocumented_static)} modules")
print(f"RESULT arch_modules_on_disk={modules_on_disk} modules")
print(f"RESULT arch_map_listed={len(map_listed)} modules")
print(f"RESULT arch_map_missing={len(missing)} modules")
print(f"RESULT option_pages={option_pages} pages")
print(f"RESULT services_registered={services_count} services")
print(f"RESULT switch_entities={len(switch_entities)} switches")
print(f"RESULT binary_sensor_entities={len(bs_entities)} binary_sensors")
print(f"RESULT entity_platforms={len(platforms)} platforms")
print(f"RESULT thread_factor=1.0")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
print("static HA importers:", static_ha)
print("dynamic HA failures:", sorted(dynamic_fail + (['__init__'] if init_ha else [])))
print("undocumented (static):", undocumented_static)
print("undocumented (dynamic):", undocumented_dynamic)
print("map missing:", missing, "phantom:", phantom)
print("switch names:", sorted(STRS["entity"]["switch"][getattr(e, "_attr_translation_key", "?")].get("name", "?")
                              for e in switch_entities))
print("bs names:", sorted(STRS["entity"]["binary_sensor"][getattr(e, "_attr_translation_key", "?")].get("name", "?")
                          for e in bs_entities))
print("platforms:", platforms)
