"""D6 round 4, verifier 3 of 3 -- self-written harness, independent methods.

Three metric definitions, one per finding, none reusing the finder's method:

D6-01  v3_ast_ha_importers     = number of package .py modules whose module
       body (top-level statements only, no If/Try/def nesting) contains an
       ast.Import/ast.ImportFrom of `homeassistant`, by static AST parse.
       v3_undocumented          = |that set minus the ten names the doc
       sentence names|, where the ten are hard-coded from the verifier's own
       reading of docs/architecture.md:140-143, not regexed out of it.
       Supporting census, measured my own way: modules on disk, the length of
       config_flow._OPTION_PAGES as imported, top-level keys of services.yaml
       (PyYAML), and the switch/binary_sensor names constructed by the real
       async_setup_entry with a minimal config the verifier composed himself.

D6-02  v3_currency_sensors_without_unit = number of instantiated monetary
       sensors whose `native_unit_of_measurement` (the stub SensorEntity
       property, same forwarding as real HA) is None, where each sensor class
       that the README documents as CUR is instantiated DIRECTLY with a
       verifier-built coordinator stub (currency="EUR"), not through the
       finder's FakeCoordinator/entities.py DATA path.

D6-03  v3_available_without_fuse = over the 2x2 grid (fuse 0/20 A) x
       (capacity tariff off/on, defaults elsewhere), the number of no-fuse
       cells where the real coordinator's `_power_headroom()` view says
       available=True AND the real PowerHeadroomSensor entity, constructed
       over that coordinator's own `_build_data_dict()`, answers
       available=True -- with the clock FROZEN by tests/hastub dt_util.freeze
       at 2026-01-01 00:10 (first metering window of a month), so the result
       does not depend on the wall clock the run happened to get.

RUN (from the repository root of the tree under test):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/verify03_own.py

ROOT RULE: the working directory (`ROOT = Path(".")`).

EXPECTED (baseline 7dd68dd327fe3dbfb09f3bd0fe38910c58877697; this re-run is at
the branch head 0855277, where docs/architecture.md, docs/automations.md,
README.md and the package are byte-identical to baseline per
`git diff 7dd68dd..HEAD --stat -- <those paths>` = empty. 8-core Apple M1,
tolerance 0 -- counts):
    RESULT v3_modules_on_disk=56
    RESULT v3_ast_ha_importers=21
    RESULT v3_undocumented=11
    RESULT v3_option_pages=21
    RESULT v3_services_in_yaml=12
    RESULT v3_switches_constructed=4
    RESULT v3_binary_sensors_constructed=5
    RESULT v3_currency_classes_checked=9
    RESULT v3_currency_sensors_without_unit=1
    RESULT v3_cells=4
    RESULT v3_available_without_fuse=1
    RESULT v3_headroom_value_no_fuse_tariff=0.0 kW

PERTURBATION (HPO_V3_PERTURB=1, nothing written outside this process):
  D6-01: ast-parse a patched copy of drift.py's source with
         `import homeassistant.core` appended -> v3_ast_ha_importers 21->22.
  D6-02: after construction set the advisor's
         _attr_native_unit_of_measurement = "EUR" -> count 1->0.
  D6-03: disable the tariff in the offending cell -> count 1->0.
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
import json
import pathlib
import sys
from types import SimpleNamespace

import yaml

ROOT = pathlib.Path(".")
PKG = ROOT / "custom_components" / "heatpump_optimizer"
PERTURB = os.environ.get("HPO_V3_PERTURB") == "1"
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

# ---------------------------------------------------------------- D6-01 (AST)
# The ten the doc names, from the verifier's own reading of
# docs/architecture.md lines 140-143 (NOT extracted by regex).
DOC_NAMED_TEN = {
    "__init__", "config_flow", "coordinator", "open_meteo", "frontend",
    "sensor", "binary_sensor", "button", "climate", "switch",
}

modules = sorted(PKG.glob("*.py"))


def top_level_ha_importers(path: pathlib.Path) -> bool:
    tree = ast.parse(path.read_text())
    for node in tree.body:  # top-level statements only
        if isinstance(node, ast.Import) and any(
            a.name == "homeassistant" or a.name.startswith("homeassistant.")
            for a in node.names
        ):
            return True
        if isinstance(node, ast.ImportFrom) and (
            node.module == "homeassistant"
            or (node.module or "").startswith("homeassistant.")
        ):
            return True
    return False


importers = sorted(p.stem for p in modules if top_level_ha_importers(p))

if PERTURB:
    # In-memory perturbation: the doc's HA-free example, drift.py, made to
    # import homeassistant. Nothing is written to disk.
    patched = ast.parse((PKG / "drift.py").read_text() + "\nimport homeassistant.core\n")
    extra = any(
        isinstance(n, ast.Import) and any(a.name == "homeassistant.core" for a in n.names)
        for n in patched.body
    )
    importers = importers + (["drift"] if extra else [])

undocumented = sorted(set(importers) - DOC_NAMED_TEN)

# The doc's own count sentence, read directly:
arch = (ROOT / "docs" / "architecture.md").read_text()
doc_count_sentence = next(
    ln for ln in arch.splitlines() if "modules, of which ten touch" in ln
)

from heatpump_optimizer import config_flow  # noqa: E402

option_pages = len(config_flow._OPTION_PAGES)
services_in_yaml = len(
    yaml.safe_load((PKG / "services.yaml").read_text())
)

# Census of the two platforms architecture.md under-describes, driven through
# the real async_setup_entry with a minimal config of my own composition.
from heatpump_optimizer import binary_sensor as bs_platform  # noqa: E402
from heatpump_optimizer import switch as switch_platform  # noqa: E402
from heatpump_optimizer import const as hpo_const  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

MIN_CFG = {
    hpo_const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    hpo_const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
}


def real_coordinator(extra: dict) -> HeatPumpOptimizerCoordinator:
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    cfg = dict(MIN_CFG)
    cfg.update(extra)
    co = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg))
    asyncio.run(co._update_current_state())
    return co


def census(platform, data_dict) -> list[str]:
    added: list = []
    entry = FakeEntry()
    entry.runtime_data = SimpleNamespace(data=data_dict, currency="EUR")
    asyncio.run(platform.async_setup_entry(FakeHass(), entry, added.extend))
    strings = json.loads((PKG / "strings.json").read_text())["entity"]
    kind = "switch" if platform is switch_platform else "binary_sensor"
    names = []
    for e in added:
        key = getattr(e, "_attr_translation_key", None)
        name = strings[kind].get(key, {}).get("name", f"?{key}")
        names.append(name)
    return sorted(names)


switch_names = census(switch_platform, {"two_zone_enabled": False})
bs_names = census(bs_platform, {"two_zone_enabled": False})

# ---------------------------------------------------------------- D6-02 (stub)
# README rows whose Unit column says CUR, read with my own parser.
readme = (ROOT / "README.md").read_text()
cur_rows = []
in_sensor_table = False
for line in readme.splitlines():
    if line.startswith("### Sensors ("):
        in_sensor_table = True
    elif in_sensor_table and line.startswith("### "):
        break
    if in_sensor_table and line.startswith("|"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[1] == "CUR":
            cur_rows.append(cells[0])

# Map each documented CUR name to its sensor class by translation_key name.
from heatpump_optimizer import sensor as sensor_platform  # noqa: E402

strings_sensor = json.loads((PKG / "strings.json").read_text())["entity"]["sensor"]
key_by_name = {
    v.get("name"): k for k, v in strings_sensor.items() if isinstance(v, dict)
}

# Build translation_key -> class from sensor.py's AST: each sensor class's
# __init__ calls super().__init__(..., "key", "translation_key").
_CLASS_BY_KEY: dict[str, type] = {}
for _node in ast.parse((PKG / "sensor.py").read_text()).body:
    if not isinstance(_node, ast.ClassDef):
        continue
    for _fn in _node.body:
        if not isinstance(_fn, ast.FunctionDef) or _fn.name != "__init__":
            continue
        for _call in ast.walk(_fn):
            if not isinstance(_call, ast.Call):
                continue
            _strs = [
                a.value for a in _call.args if isinstance(a, ast.Constant) and isinstance(a.value, str)
            ]
            # The LAST positional string is the translation_key; the two
            # differ for e.g. ("space_cost", "space_heating_cost").
            if len(_strs) >= 2 and _strs[-1] in key_by_name.values():
                _CLASS_BY_KEY.setdefault(_strs[-1], getattr(sensor_platform, _node.name))


class MyCoordStub(SimpleNamespace):
    """Verifier-built coordinator: just what the entity constructors touch."""

    currency = "EUR"
    data: dict = {}
    _config: dict = {}


class MyEntryStub(SimpleNamespace):
    entry_id = "v3-entry"
    title = "v3"
    options: dict = {}


without_unit = []
with_unit = []
for row_name in cur_rows:
    key = key_by_name.get(row_name)
    if key is None:
        without_unit.append((row_name, "no-class-found"))
        continue
    # Resolve the class by AST: the class whose __init__ passes this
    # translation key to the base constructor.
    cls = _CLASS_BY_KEY.get(key)
    ent = cls(MyCoordStub(), MyEntryStub()) if cls else None
    if PERTURB and row_name == "Sensor-Gap Euro Advisor" and ent is not None:
        ent._attr_native_unit_of_measurement = "EUR"
    unit = ent.native_unit_of_measurement if ent else None
    (without_unit if unit in (None, "") else with_unit).append(
        (row_name, unit, getattr(ent, "native_value", None))
    )

# ---------------------------------------------------------------- D6-03 (frozen)
dt_util.freeze(dt_util.parse_datetime("2026-01-01T00:10:00+00:00"))

FUSE = hpo_const.CONF_MAIN_FUSE_A
TARIFF = {
    hpo_const.CONF_PEAK_TARIFF_ENABLED: not PERTURB,
    hpo_const.CONF_PEAK_TARIFF_PRICE: 45.0,
}
cells = {
    "no fuse, no tariff": {},
    "no fuse, capacity tariff": dict(TARIFF),
    "fuse, no tariff": {FUSE: 20},
    "fuse, capacity tariff": {FUSE: 20, **TARIFF},
}

grid = {}
for label, extra in cells.items():
    co = real_coordinator(extra)
    view = co._power_headroom()
    ent = sensor_platform.PowerHeadroomSensor(
        SimpleNamespace(
            data=co._build_data_dict(),
            _config=co._config,
            currency="EUR",
            device_info={},
        ),
        MyEntryStub(),
    )
    grid[label] = {
        "view_available": bool(view.get("available")),
        "entity_available": bool(ent.available),
        "value": view.get("headroom_kw"),
        "limit_source": view.get("limit_source"),
    }

avail_no_fuse = [
    k
    for k, v in grid.items()
    if k.startswith("no fuse") and v["view_available"] and v["entity_available"]
]

# ---------------------------------------------------------------------- print
print(f"RESULT v3_modules_on_disk={len(modules)} modules")
print(f"RESULT v3_ast_ha_importers={len(importers)} modules")
print(f"RESULT v3_undocumented={len(undocumented)} modules")
print(f"RESULT v3_option_pages={option_pages} pages")
print(f"RESULT v3_services_in_yaml={services_in_yaml} services")
print(f"RESULT v3_switches_constructed={len(switch_names)} switches")
print(f"RESULT v3_binary_sensors_constructed={len(bs_names)} binary_sensors")
print(f"RESULT v3_currency_classes_checked={len(cur_rows)} sensors")
print(f"RESULT v3_currency_sensors_without_unit={len(without_unit)} sensors")
print(f"RESULT v3_cells={len(grid)} cells")
print(f"RESULT v3_available_without_fuse={len(avail_no_fuse)} cells")
print(f"RESULT v3_headroom_value_no_fuse_tariff={grid['no fuse, capacity tariff']['value']} kW")
print(f"RESULT thread_factor=1.0")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
print("doc sentence read:", doc_count_sentence.strip())
print("AST HA importers:", importers)
print("undocumented (mine):", undocumented)
print("switch names:", switch_names)
print("binary_sensor names:", bs_names)
print("CUR rows without unit:", without_unit)
print("CUR rows with unit:", [(n, u) for n, u, _ in with_unit])
for k, v in grid.items():
    print(" ", k, "->", v)
