"""D10-s1 M1: one executed check per Bronze and Silver quality-scale rule.

Metric: per rule, one number from the production code (driven through the
stubs where a behaviour is asked, AST/text over the tree where a structure
is asked); printed as RESULT <rule>.<metric>=<value>. The status each number
implies is in REPORT.md's tier table. Rules the three finding harnesses in this
directory measure (unique-config-entry, action-exceptions, test-before-setup /
reauthentication-flow) are re-summarised here only by their controls.

Run (from the export root):
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D10/s1/rules_check.py
Expected: the values in REPORT.md, +- 0 (counts). Baseline
1936d5ca72a06556eeed4e8e5bf3dea520e517e1, machine: audit box B1. Root rule: cwd.
Perturbation (per-check sanity, --perturb): drops switch.py's PARALLEL_UPDATES
from the census in memory and flips the first entity's _attr_has_entity_name;
parallel_updates.platforms_declaring must move 6 -> 5 and has_entity_name.false
0 -> 1. The availability census is taken both ways in one run
(last_update_success True, then False): 53 -> 0 is its own control.
"""
from __future__ import annotations

import os

for _var in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_var, "1")

import ast  # noqa: E402
import asyncio  # noqa: E402
import importlib  # noqa: E402
import io  # noqa: E402
import json  # noqa: E402
import logging  # noqa: E402
import pathlib  # noqa: E402
import re  # noqa: E402
import struct  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from datetime import timedelta  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
import heatpump_optimizer as integration  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import coordinator as coordinator_module  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

PERTURB = "--perturb" in sys.argv
PKG = pathlib.Path("custom_components/heatpump_optimizer")
RESULTS: list[tuple[str, object]] = []


def res(name, value):
    RESULTS.append((name, value))
    print(f"RESULT {name}={value}")


def src(name):
    return (PKG / name).read_text(encoding="utf-8")


def func_nodes(tree, name):
    return [n for n in ast.walk(tree) if isinstance(n, (ast.AsyncFunctionDef, ast.FunctionDef)) and n.name == name]


def calls_in(node, attr):
    return sum(1 for n in ast.walk(node) if isinstance(n, ast.Call)
               and isinstance(n.func, ast.Attribute) and n.func.attr == attr)


# ---- Bronze -------------------------------------------------------------
init_tree = ast.parse(src("__init__.py"))
svc_tree = ast.parse(src("services.py"))
res("action_setup.register_calls_in_services_py", calls_in(svc_tree, "async_register"))
res("action_setup.register_or_remove_in_setup_entry_or_unload",
    sum(calls_in(f, a) for n in ("async_setup_entry", "async_unload_entry")
        for f in func_nodes(init_tree, n) for a in ("async_register", "async_remove")))
_hass = FakeHass()
asyncio.run(integration.async_setup(_hass, {}))
res("action_setup.services_registered_by_async_setup_without_entry",
    len(_hass.services.async_services().get(const.DOMAIN, {})))
yaml_services = re.findall(r"^([a-z_]+):\s*$", src("services.yaml"), re.M)
res("action_setup.services_yaml_entries", len(yaml_services))

manifest = json.loads(src("manifest.json"))
res("common_modules.coordinator_py_has_DataUpdateCoordinator_subclass",
    int("DataUpdateCoordinator" in src("coordinator.py") and "class HeatPumpOptimizerCoordinator(" in src("coordinator.py")))
res("common_modules.entity_py_has_CoordinatorEntity_base",
    int(bool(re.search(r"class HeatPumpOptimizerEntity\(.*CoordinatorEntity", src("entity.py")))))


def png_size(p):
    head = p.read_bytes()[:24]
    return struct.unpack(">II", head[16:24]) if head[:8] == b"\x89PNG\r\n\x1a\n" else None


res("brands.brand_icon_png_size", "x".join(map(str, png_size(PKG / "brand/icon.png") or ())))
res("brands.brand_logo_png_present", int((PKG / "brand/logo.png").exists()))

strings = json.loads(src("strings.json"))
for sec in ("config", "options"):
    steps = strings.get(sec, {}).get("step", {})
    fields = [(s, k) for s, v in steps.items() for k in v.get("data", {})]
    missing = [f for f in fields if f[1] not in steps[f[0]].get("data_description", {})]
    res(f"config_flow.{sec}_fields", len(fields))
    res(f"config_flow.{sec}_fields_without_data_description", len(missing))
res("config_flow.manifest_config_flow", int(bool(manifest.get("config_flow"))))

res("dependency_transparency.requirements", len(manifest.get("requirements", [])))
res("dependency_transparency.requirements_not_plain_pypi_spec",
    sum(1 for r in manifest.get("requirements", []) if not re.fullmatch(r"[A-Za-z0-9_.\-]+[<>=!~]=?[0-9.]+", r)))

docs_text = pathlib.Path("README.md").read_text(encoding="utf-8") + "".join(
    p.read_text(encoding="utf-8") for p in pathlib.Path("docs").glob("*.md")
    if not p.name.startswith("plan-") and p.name != "HANDOVER.md")
res("docs_actions.services_not_named_in_readme_or_user_docs",
    sum(1 for s in yaml_services if s not in docs_text))
res("docs_triggers.device_trigger_modules", int((PKG / "device_trigger.py").exists()))
res("docs_conditions.device_condition_modules", int((PKG / "device_condition.py").exists()))
readme = pathlib.Path("README.md").read_text(encoding="utf-8")
res("docs_high_level_description.readme_what_it_does_heading", int("## What it does" in readme))
res("docs_installation_instructions.readme_installation_heading", int("## Installation" in readme))
res("docs_removal_instructions.readme_removal_heading", int("### Removal" in readme))

PLATFORM_MODULES = ["sensor", "binary_sensor", "button", "switch", "climate", "datetime"]
ev_bad = 0
for mod in PLATFORM_MODULES + ["entity"]:
    tree = ast.parse(src(f"{mod}.py"))
    for fn in [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        if fn.name == "async_added_to_hass":
            continue
        for n in ast.walk(fn):
            if isinstance(n, ast.Call):
                name = getattr(n.func, "attr", getattr(n.func, "id", ""))
                if name.startswith("async_track_") or name == "async_listen":
                    ev_bad += 1
res("entity_event_setup.subscriptions_outside_async_added_to_hass", ev_bad)


def price_rows(start, n):
    return [{"start": (start + timedelta(minutes=15 * i)).isoformat(),
             "value": 0.8 + 0.4 * ((i // 4) % 12) / 12.0} for i in range(n)]


hass = FakeHass()
hass.states.set("sensor.indoor", FakeState("21.0"))
hass.states.set("sensor.outdoor", FakeState("-2.0"))
now = dt_util.now().replace(minute=0, second=0, microsecond=0)
hass.states.set("sensor.price", FakeState("0.9", attributes={
    "raw_today": price_rows(now - timedelta(hours=1), 4 * 49), "unit_of_measurement": "SEK/kWh"}))
entry = FakeEntry(data={
    const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY, const.CONF_PRICE_ENTITY: "sensor.price",
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor", const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    const.CONF_DHW_TANK_VOLUME: 180.0})
logging.disable(logging.CRITICAL)
from homeassistant.helpers import update_coordinator as _uc  # noqa: E402
_seen_interval = []
_orig_init = _uc.DataUpdateCoordinator.__init__


def _rec_init(self, *a, **k):
    _seen_interval.append(k.get("update_interval"))
    _orig_init(self, *a, **k)


_uc.DataUpdateCoordinator.__init__ = _rec_init
asyncio.run(integration.async_setup_entry(hass, entry))
_uc.DataUpdateCoordinator.__init__ = _orig_init
coord = entry.runtime_data
res("runtime_data.entry_runtime_data_is_coordinator",
    int(type(coord).__name__ == "HeatPumpOptimizerCoordinator"))
res("runtime_data.hass_data_domain_keys", len([k for k in hass.data if str(k) == const.DOMAIN]))
res("appropriate_polling.update_interval_minutes", _seen_interval[-1].total_seconds() / 60)

entities = []
for mod in PLATFORM_MODULES:
    m = importlib.import_module(f"heatpump_optimizer.{mod}")
    asyncio.run(m.async_setup_entry(hass, entry, lambda es, *_a, **_k: entities.extend(es)))
if PERTURB and entities:
    entities[0]._attr_has_entity_name = False
uids = [getattr(e, "unique_id", None) or getattr(e, "_attr_unique_id", None) for e in entities]
res("entity_unique_id.entities", len(entities))
res("entity_unique_id.missing", sum(1 for u in uids if not u))
res("entity_unique_id.duplicates", len(uids) - len(set(uids)))
res("has_entity_name.false", sum(1 for e in entities if not getattr(e, "has_entity_name", getattr(e, "_attr_has_entity_name", False))))

src_cf = src("config_flow.py")
res("test_before_configure.validate_tibber_token_calls_in_flow", src_cf.count("await validate_tibber_token("))

# ---- Silver ---------------------------------------------------------------
pu = []
for mod in PLATFORM_MODULES:
    m = importlib.import_module(f"heatpump_optimizer.{mod}")
    if PERTURB and mod == "switch":
        continue
    if hasattr(m, "PARALLEL_UPDATES"):
        pu.append(f"{mod}={m.PARALLEL_UPDATES}")
res("parallel_updates.platforms_declaring", len(pu))
res("parallel_updates.platforms", len(PLATFORM_MODULES))
print("INFO parallel_updates " + ",".join(pu))

res("integration_owner.codeowners", len(manifest.get("codeowners", [])))

coord.last_update_success = True
up = sum(1 for e in entities if e.available)
coord.last_update_success = False
avail_failed = sum(1 for e in entities if e.available)
res("entity_unavailable.available_while_ok", up)
res("entity_unavailable.available_while_failed", avail_failed)
coord.last_update_success = True

ok = asyncio.run(integration.async_unload_entry(hass, entry))
res("config_entry_unloading.unload_ok", int(bool(ok)))
res("config_entry_unloading.coordinator_shutdown_called", int(bool(getattr(coord, "base_shutdown_called", False))))

# log-when-unavailable: three failed Tibber fetches and a recovery.
logging.disable(logging.NOTSET)
buf = io.StringIO()
handler = logging.StreamHandler(buf)
handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
lg = logging.getLogger("custom_components.heatpump_optimizer")
lg2 = logging.getLogger("heatpump_optimizer")
for lgr in (lg, lg2):
    lgr.addHandler(handler)
    lgr.setLevel(logging.DEBUG)


class _Resp:
    def __init__(self, status):
        self.status = status

    async def json(self):
        return {"data": {"viewer": {"homes": [{"currentSubscription": {"priceInfo": {
            "today": [{"total": 1.0, "startsAt": (now + timedelta(hours=h)).isoformat(), "level": "NORMAL"} for h in range(24)],
            "tomorrow": []}}}]}}}

    async def __aenter__(self):
        return self

    async def __aexit__(self, *e):
        return False


class _Sess:
    status = 500

    def post(self, *a, **k):
        return _Resp(self.status)


sess = _Sess()
coordinator_module.async_get_clientsession = lambda h, verify_ssl=True: sess
h2 = FakeHass()
c2 = coordinator_module.HeatPumpOptimizerCoordinator(h2, FakeEntry(data={const.CONF_TIBBER_TOKEN: "t"}))
for _ in range(3):
    try:
        asyncio.run(c2._fetch_tibber_prices())
    except Exception:  # noqa: BLE001
        pass
sess.status = 200
try:
    asyncio.run(c2._fetch_tibber_prices())
except Exception:  # noqa: BLE001
    pass
log = buf.getvalue().splitlines()
res("log_when_unavailable.error_lines_over_3_failures", sum(1 for l in log if l.startswith("ERROR") and "ibber" in l))
res("log_when_unavailable.info_recovery_lines", sum(1 for l in log if l.startswith("INFO") and "recovered" in l))

res("reauthentication_flow.async_step_reauth_defined", int("async def async_step_reauth(" in src_cf))

t_p, t_t = time.process_time(), time.thread_time()
print(f"RESULT thread_factor={t_p / t_t if t_t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    with open("/proc/vmstat") as fh:
        print("RESULT swapins=" + next(l.split()[1] for l in fh if l.startswith("pswpin")))
except (OSError, StopIteration):
    print("RESULT swapins=unknown")
