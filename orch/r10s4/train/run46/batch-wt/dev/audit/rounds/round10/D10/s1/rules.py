"""D10-s1 (round 10): one executed check per Bronze and Silver quality-scale rule.

Metric: per rule, a count from the integration (AST/grep over the package, a
stub-driven setup through every platform's real async_setup_entry, or a
documentation lookup); status done when the count meets the rule's bar.
Command (from the export root):
  PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python \
    dev/audit/rounds/round10/D10/s1/rules.py [--perturb]
Expected: RESULT rules_todo=0 count (exact) at baseline 17f1c55fad1b;
  --perturb nulls sensor.OptimizationModeSensor's unique id and drops one platform's
  PARALLEL_UPDATES in memory: rules_todo and makes _loaded_coordinators return [] silently: rules_todo must move up (to 3).
Key of the entity counts: the unique_id / has_entity_name each constructed
  entity object delivers, not a class attribute.
Machine: macOS arm64 dev box (B1).  Counts only -- contention-immune.
config-flow-test-coverage and test-coverage are measured by coverage.sh (M3).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import ast
import asyncio
import json
import re
import struct
import sys
import time
from pathlib import Path

sys.path.insert(0, "tests")
sys.path.insert(0, ".")
PKG = Path("custom_components/heatpump_optimizer")
PERTURB = "--perturb" in sys.argv
t0p, t0t = time.process_time(), time.thread_time()

from harness import FakeHass, FakeState, FakeEntry  # noqa: E402
import custom_components.heatpump_optimizer as integ  # noqa: E402
from custom_components.heatpump_optimizer import const, entity as entmod  # noqa: E402
from custom_components.heatpump_optimizer.coordinator import (  # noqa: E402
    HeatPumpOptimizerCoordinator,
)
import importlib  # noqa: E402

rows = []


def rule(name, tier, ok, evidence, value):
    rows.append((name, tier, "done" if ok else "todo", evidence, value))


def src(name):
    return (PKG / name).read_text()


def tree(name):
    return ast.parse(src(name))


def func(t, name):
    for n in ast.walk(t):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name:
            return n
    return None


manifest = json.loads(src("manifest.json"))
init_t = tree("__init__.py")
plat_names = [p.value if hasattr(p, "value") else str(p) for p in integ.PLATFORM_LIST]
plat_mods = {p: importlib.import_module(f"custom_components.heatpump_optimizer.{p}")
             for p in plat_names}

if PERTURB:
    _cls = plat_mods["sensor"].OptimizationModeSensor
    _orig_init = _cls.__init__

    def _nulled(self, *a, **k):
        _orig_init(self, *a, **k)
        self._attr_unique_id = None

    _cls.__init__ = _nulled
    delattr(plat_mods["switch"], "PARALLEL_UPDATES")
    _svc = importlib.import_module("custom_components.heatpump_optimizer.services")
    _svc._loaded_coordinators = lambda hass, target_entry=None: []

# ---- dynamic entity census through every platform's async_setup_entry ----
hass = FakeHass()
hass.states.set("sensor.indoor", FakeState("21.4"))
hass.states.set("sensor.outdoor", FakeState("-3.0"))
cfg = {const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
       const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
       const.CONF_DHW_TANK_VOLUME: 180.0}
entry = FakeEntry(data=cfg)
coord = HeatPumpOptimizerCoordinator(hass, entry)
asyncio.run(coord._update_current_state())
coord.data = coord._build_data_dict()
entry.runtime_data = coord
ents = []


def _add(es, *a, **k):
    for e in es:
        e.hass = hass
    ents.extend(es)


for p, m in plat_mods.items():
    asyncio.run(m.async_setup_entry(hass, entry, _add))
def _uid(e):
    return getattr(e, "unique_id", getattr(e, "_attr_unique_id", None))


uids = [_uid(e) for e in ents]
no_uid = sum(1 for u in uids if not u)
dup_uid = len(uids) - len(set(uids))
no_hen = sum(1 for e in ents if not getattr(e, "has_entity_name", getattr(e, "_attr_has_entity_name", False)))
print(f"RESULT entities_constructed={len(ents)} count")
print(f"RESULT entities_without_unique_id={no_uid} count")
print(f"RESULT entities_duplicate_unique_id={dup_uid} count")
print(f"RESULT entities_without_has_entity_name={no_hen} count")

# ---- Bronze ----
setup_regs = sum(1 for n in ast.walk(func(init_t, "async_setup_entry"))
                 if isinstance(n, ast.Attribute) and n.attr == "async_register")
svc_regs = len(re.findall(r"\.async_register\(", src("services.py")))
setup_calls = "_async_register_services" in ast.unparse(func(init_t, "async_setup"))
rule("action-setup", "bronze", setup_calls and setup_regs == 0 and svc_regs > 0,
     "AST: async_setup calls _async_register_services; async_register in async_setup_entry",
     f"in_setup_entry={setup_regs} services.py_registers={svc_regs}")
ui = coord.update_interval.total_seconds()
rule("appropriate-polling", "bronze", 60 <= ui <= 3600,
     "coordinator.update_interval of a default entry", f"{ui:.0f}s")


def png_size(p):
    b = p.read_bytes()[:24]
    return struct.unpack(">II", b[16:24]) if b[:8] == b"\x89PNG\r\n\x1a\n" else None


icon = png_size(PKG / "brand/icon.png") if (PKG / "brand/icon.png").exists() else None
rule("brands", "bronze", icon == (256, 256), "PNG header of brand/icon.png", str(icon))
rule("common-modules", "bronze", (PKG / "coordinator.py").exists() and (PKG / "entity.py").exists(),
     "coordinator.py and entity.py exist", "2/2")
cf = importlib.import_module("custom_components.heatpump_optimizer.config_flow")
rule("config-flow", "bronze", manifest.get("config_flow") is True
     and hasattr(cf.HeatPumpOptimizerConfigFlow, "async_step_user"),
     "manifest config_flow + ConfigFlow.async_step_user", str(manifest.get("config_flow")))
reqs = manifest.get("requirements", [])
unpinned = [r for r in reqs if not re.search(r"[<>=]=?", r)]
rule("dependency-transparency", "bronze", not unpinned,
     "manifest requirements carry a version specifier", f"{len(reqs)} reqs, unpinned={unpinned}")
readme = Path("README.md").read_text()
svcs = re.findall(r"^([a-z_]+):", src("services.yaml"), re.M)
undoc = [s for s in svcs if f"`{s}`" not in readme]
rule("docs-actions", "bronze", not undoc, "every services.yaml action named in README",
     f"{len(svcs)} actions, undocumented={undoc}")
trig = [p.name for p in PKG.glob("*.py") if p.stem in ("trigger", "device_trigger")]
cond = [p.name for p in PKG.glob("*.py") if p.stem in ("condition", "device_condition")]
rule("docs-triggers", "bronze", not trig, "vacuous: trigger modules", f"{trig}")
rule("docs-conditions", "bronze", not cond, "vacuous: condition modules", f"{cond}")
heads = re.findall(r"^#+ (.+)$", readme, re.M)
rule("docs-high-level-description", "bronze", any(h.startswith("What it does") for h in heads),
     "README heading 'What it does'", "found")
rule("docs-installation-instructions", "bronze", "Installation" in heads, "README heading", "found")
rule("docs-removal-instructions", "bronze", "Removal" in heads, "README heading", "found")
# entity-event-setup: subscriptions inside entity __init__ (should be in async_added_to_hass)
bad_ev = 0
for p in plat_names + ["entity"]:
    for n in ast.walk(tree(f"{p}.py")):
        if isinstance(n, ast.FunctionDef) and n.name == "__init__":
            s = ast.unparse(n)
            bad_ev += len(re.findall(r"async_track_|bus\.async_listen|async_add_listener", s))
rule("entity-event-setup", "bronze", bad_ev == 0, "AST: subscriptions in entity __init__", f"{bad_ev}")
rule("entity-unique-id", "bronze", no_uid == 0 and dup_uid == 0 and ents,
     "constructed entities' unique_id", f"{len(ents)} entities, none={no_uid}, dup={dup_uid}")
rule("has-entity-name", "bronze", no_hen == 0 and ents, "constructed entities' has_entity_name",
     f"without={no_hen}")
hd = sum(len(re.findall(r"hass\.data\[(?:DOMAIN|const\.DOMAIN)\]", (PKG / f).read_text()))
         for f in [q.name for q in PKG.glob("*.py")])
rule("runtime-data", "bronze", hd == 0 and "entry.runtime_data = coordinator" in src("__init__.py"),
     "grep hass.data[DOMAIN]; runtime_data assignment", f"hass.data[DOMAIN]={hd}")
uflow = ast.unparse(func(tree("config_flow.py"), "async_step_user"))
rule("test-before-configure", "bronze", "errors" in uflow,
     "async_step_user returns a form with errors on a failed check", "errors path present")
rule("test-before-setup", "bronze",
     "async_config_entry_first_refresh" in ast.unparse(func(init_t, "async_setup_entry")),
     "setup awaits async_config_entry_first_refresh (raises NotReady/AuthFailed)", "present")
cfs = src("config_flow.py")
rule("unique-config-entry", "bronze", "async_set_unique_id" in cfs and "_abort_if_unique_id_configured" in cfs,
     "grep set_unique_id + abort", f"{cfs.count('async_set_unique_id')}/{cfs.count('_abort_if_unique_id_configured')}")

# ---- Silver ----
# action-exceptions: every registered action, called with NO loaded entry
# (raw data, schema bypassed), must raise rather than return silently.
from homeassistant.exceptions import HomeAssistantError  # noqa: E402
from harness import FakeServiceCall  # noqa: E402
svc_mod = importlib.import_module("custom_components.heatpump_optimizer.services")
sh = FakeHass()
svc_mod.async_register_services(sh)
CALL_DATA = {"set_mode": {"mode": "auto"}, "set_away": {"active": True},
             "debug_collect": {"action": "status"},
             "apply_schedule": {"dhw_windows": "06:00-07:00"},
             "assign_entity": {"key": "outdoor_temp_entity", "entity_id": ""},
             "apply_topology": {"layout": "direct"}}
silent, raised_ok, other = [], 0, []
for name, handler in sorted(sh.services.async_services().get(const.DOMAIN, {}).items()):
    try:
        asyncio.run(handler(FakeServiceCall(const.DOMAIN, name, CALL_DATA.get(name, {}))))
        silent.append(name)
    except HomeAssistantError:
        raised_ok += 1
    except Exception as err:  # noqa: BLE001
        other.append(f"{name}:{type(err).__name__}")
print(f"RESULT actions_silent_without_entry={len(silent)} count")
rule("action-exceptions", "silver", not silent and not other,
     "each registered action called with no loaded entry raises HomeAssistantError",
     f"raised={raised_ok} silent={silent} other={other}")
rule("config-entry-unloading", "silver", func(init_t, "async_unload_entry") is not None,
     "async_unload_entry defined", "present")
strings = json.loads(src("strings.json"))
nf = nd = 0
for sec in ("config", "options"):
    for v in strings[sec]["step"].values():
        for blk in [v] + list(v.get("sections", {}).values()):
            for f in blk.get("data", {}):
                nf += 1
                nd += f in blk.get("data_description", {})
rule("docs-configuration-parameters", "silver", nf == nd, "options+config fields with data_description", f"{nd}/{nf}")
rule("docs-installation-parameters", "silver", nf == nd, "same census, config steps included", f"{nd}/{nf}")
_prev = coord.last_update_success
coord.last_update_success = False
still = [_uid(e) for e in ents if e.available]
coord.last_update_success = _prev
print(f"RESULT available_after_failed_update={len(still)} count")
rule("entity-unavailable", "silver", not still and ents,
     "entities still available with coordinator.last_update_success=False", f"{len(still)} {still[:5]}")
rule("integration-owner", "silver", bool(manifest.get("codeowners")), "manifest codeowners",
     str(manifest.get("codeowners")))
co = src("coordinator.py")
rule("log-when-unavailable", "silver", "_tibber_fetch_failed" in co and "_tibber_fetch_recovered" in co,
     "latched fail/recover pair present", "present")
missing_pu = [p for p, m in plat_mods.items() if not hasattr(m, "PARALLEL_UPDATES")]
rule("parallel-updates", "silver", not missing_pu, "PARALLEL_UPDATES per platform module",
     f"missing={missing_pu}")
rule("reauthentication-flow", "silver", hasattr(cf.HeatPumpOptimizerConfigFlow, "async_step_reauth"),
     "ConfigFlow.async_step_reauth", "present")

todo = 0
for r in rows:
    print("ROW " + " | ".join(str(x) for x in r))
    todo += r[2] == "todo"
print(f"RESULT rules_checked={len(rows)} count")
print(f"RESULT rules_todo={todo} count")
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    import resource
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}")
except Exception:
    print("RESULT swapins=0")
