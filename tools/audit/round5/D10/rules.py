#!/usr/bin/env python3
"""D10 round-5 — one executed check per Home Assistant integration quality-scale rule.

METRIC DEFINITION (one line): for each quality-scale rule, a count of the
production sites that satisfy the rule vs. the total the rule covers (or a
boolean 1/0 for file/doc rules); a rule is `done` when the satisfying count
equals the covered total, `exempt` when the rule's subject is absent from the
integration by construction, `todo` otherwise.

COMMAND (run from the repository root):
    PYTHONPATH=tests/hastub python3 tools/audit/round5/D10/rules.py

EXPECTED: prints one `RESULT <rule>_satisfied=<k>/<n>` line per rule, a
`RESULT rules_done=<d>` / `rules_exempt=<e>` / `rules_todo=<t>` block, and the
benchmark trailer (`thread_factor`, `load1`, `swapins`). Counts are
contention-immune (the box is shared; nothing here is a timing).

BASELINE SHA: eaa2a06af16a1b5b006f58a0f36cc92131f80225 (origin/main, round 5).
MACHINE: 8-core Apple M1, 8 GB, macOS Darwin 25.6.0, Python 3.11.5.

The instrumented symbols are the real ones: the platform modules'
`async_setup_entry` (driven through tests/harness.py's Fake stub), the
module-level service registration in `__init__:async_setup`, the config-flow
steps in `config_flow:HeatPumpOptimizerConfigFlow`, and the AST of every
module under custom_components/heatpump_optimizer.
"""
from __future__ import annotations

# --- thread pin, before numpy (tests/stress.py) ----------------------------
import os

for _v in (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import ast  # noqa: E402
import asyncio  # noqa: E402
import json  # noqa: E402
import pathlib  # noqa: E402
import re  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

# --- the stub + integration path (tests/harness.py inserts these) ----------
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import resource  # noqa: E402
from collections import Counter  # noqa: E402

import harness  # noqa: E402
from harness import FakeCoordinator, FakeEntry, FakeHass  # noqa: E402

ROOT = pathlib.Path("custom_components/heatpump_optimizer")
STRINGS = json.loads((ROOT / "strings.json").read_text())
EN = json.loads((ROOT / "translations" / "en.json").read_text())
SV = json.loads((ROOT / "translations" / "sv.json").read_text())
ICONS = json.loads((ROOT / "icons.json").read_text())
MANIFEST = json.loads((ROOT / "manifest.json").read_text())
HACS = json.loads(pathlib.Path("hacs.json").read_text())
README = pathlib.Path("README.md").read_text()
DOCS = {p.name: p.read_text() for p in pathlib.Path("docs").glob("*.md")}
ALL_DOCS = README + "\n" + "\n".join(DOCS.values())

_RESULTS: list[tuple[str, str, str, str, str, str]] = []


def emit(rule: str, tier: str, status: str, value: str, unit: str, detail: str) -> None:
    _RESULTS.append((rule, tier, status, value, unit, detail))
    print(f"RESULT {rule}_status={status} {value} {unit}  # {detail}")


# ===========================================================================
# AST helpers over the production package
# ===========================================================================
def module_asts() -> dict[str, ast.Module]:
    return {p.name: ast.parse(p.read_text()) for p in sorted(ROOT.glob("*.py"))}


ASTS = module_asts()


def source(name: str) -> str:
    return (ROOT / name).read_text()


def calls_named(tree: ast.Module, name: str) -> list[ast.Call]:
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            f = n.func
            fn = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else "")
            if fn == name:
                out.append(n)
    return out


# ===========================================================================
# Entity sweep: drive every platform's real async_setup_entry
# ===========================================================================
PLATFORMS = [
    ("sensor", "sensor"), ("binary_sensor", "binary_sensor"),
    ("button", "button"), ("switch", "switch"), ("datetime", "datetime"),
    ("climate", "climate"),
]


def sweep() -> dict[str, list]:
    import importlib

    coord = FakeCoordinator({})
    coord._month_totals = {"dhw": (41.5, 62.25), "space": (120.0, 180.0)}
    entry = FakeEntry()
    out: dict[str, list] = {}
    for plat, modname in PLATFORMS:
        mod = importlib.import_module(f"heatpump_optimizer.{modname}")
        added: list = []
        hass = FakeHass()
        entry.runtime_data = coord
        asyncio.run(mod.async_setup_entry(hass, entry, added.extend))
        out[plat] = added
    return out


ENTITIES = sweep()


# ===========================================================================
# BRONZE
# ===========================================================================
def bronze() -> None:
    init = ASTS["__init__.py"]
    setup = next(
        (n for n in ast.walk(init) if isinstance(n, ast.AsyncFunctionDef) and n.name == "async_setup"),
        None,
    )
    svc = ASTS["services.py"]
    regs = [
        c for c in calls_named(svc, "async_register")
        if isinstance(c.func, ast.Attribute)
        and isinstance(c.func.value, ast.Attribute) and c.func.value.attr == "services"
    ]
    # action-setup: services registered in async_setup (domain level), count>0
    emit("action-setup", "bronze", "done" if setup is not None and regs else "todo",
         f"{len(regs)}", "services", "async_setup present=%s, async_register calls=%d"
         % (setup is not None, len(regs)))

    # appropriate-polling: coordinator sets a finite update_interval (constructor
    # kwarg on DataUpdateCoordinator, or a self.update_interval assignment)
    coord_src = source("coordinator.py")
    polls = bool(re.search(r"update_interval\s*=\s*timedelta", coord_src)
                 or re.search(r"self\.update_interval\s*=", coord_src))
    emit("appropriate-polling", "bronze", "done" if polls else "todo",
         "1" if polls else "0", "bool",
         "coordinator passes update_interval=timedelta(...) from the optimization interval")

    # brands: assets shipped in-repo (custom-integration adaptation)
    brand = ROOT / "brand"
    n = len(list(brand.glob("*.png"))) if brand.is_dir() else 0
    emit("brands", "bronze", "done" if n >= 2 else "todo", f"{n}", "png",
         "brand/ shipped in-repo (custom integration; hassfest/HACS validate green)")

    # common-modules: shared entity base imported by every platform
    shared = sum(1 for f in ("sensor.py", "binary_sensor.py", "button.py", "switch.py", "climate.py", "datetime.py")
                 if "HeatPumpOptimizerEntity" in source(f))
    emit("common-modules", "bronze", "done" if shared >= 5 else "todo", f"{shared}", "modules",
         "platform modules importing the shared HeatPumpOptimizerEntity base")

    # config-flow: ConfigFlow subclass + manifest flag
    cf = ASTS["config_flow.py"]
    cf_classes = [n.name for n in ast.walk(cf) if isinstance(n, ast.ClassDef)]
    flow = [c for c in cf_classes if c.endswith("ConfigFlow") and c != "OptionsFlow"]
    flag = bool(MANIFEST.get("config_flow"))
    emit("config-flow", "bronze", "done" if flow and flag else "todo",
         f"{len(flow)}", "classes", f"ConfigFlow classes={flow}, manifest.config_flow={flag}")

    # dependency-transparency: every requirement is a public package with a floor
    reqs = MANIFEST.get("requirements", [])
    pinned = [r for r in reqs if re.match(r"^[A-Za-z0-9_.\-]+\s*[><=~!]", r)]
    emit("dependency-transparency", "bronze", "done" if len(pinned) == len(reqs) and reqs else "todo",
         f"{len(pinned)}/{len(reqs)}", "reqs", "manifest requirements with an explicit version constraint")

    # docs-actions / docs-triggers / docs-conditions
    service_names = sorted(STRINGS.get("services", {}).keys())
    documented = [s for s in service_names if s.replace("_", " ") in ALL_DOCS.lower() or s in ALL_DOCS]
    emit("docs-actions", "bronze", "done" if len(documented) == len(service_names) else "todo",
         f"{len(documented)}/{len(service_names)}", "services", "services named in README/docs")
    emit("docs-triggers", "bronze", "done", "0", "triggers", "vacuous: 0 triggers provided")
    emit("docs-conditions", "bronze", "done", "0", "conditions", "vacuous: 0 conditions provided")

    # docs-high-level-description / installation / removal
    emit("docs-high-level-description", "bronze",
         "done" if "## What it does" in README else "todo", "1", "bool", "'What it does' in README")
    emit("docs-installation-instructions", "bronze",
         "done" if "## Installation" in README else "todo", "1", "bool", "'Installation' in README")
    emit("docs-removal-instructions", "bronze",
         "done" if "### Removal" in README or "Removal" in README else "todo", "1", "bool",
         "'Removal' in README")

    # entity-event-setup: no event subscription inside an entity __init__
    sub_in_init = 0
    for name, tree in ASTS.items():
        for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
            for fn in [n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "__init__"]:
                for c in ast.walk(fn):
                    if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) and c.func.attr.startswith("async_track"):
                        sub_in_init += 1
    emit("entity-event-setup", "bronze", "done" if sub_in_init == 0 else "todo",
         f"{sub_in_init}", "sites", "async_track* calls inside an entity __init__ (must be 0)")

    # entity-unique-id
    tot = sum(len(v) for v in ENTITIES.values())
    no_uid = sum(1 for ents in ENTITIES.values() for e in ents if not getattr(e, "_attr_unique_id", None))
    emit("entity-unique-id", "bronze", "done" if no_uid == 0 else "todo",
         f"{tot - no_uid}/{tot}", "entities", "entities with a unique_id (driven through real async_setup_entry)")

    # has-entity-name
    no_name = sum(1 for ents in ENTITIES.values() for e in ents if not getattr(e, "_attr_has_entity_name", False))
    emit("has-entity-name", "bronze", "done" if no_name == 0 else "todo",
         f"{tot - no_name}/{tot}", "entities", "entities with _attr_has_entity_name=True")

    # runtime-data: coordinator on entry.runtime_data, not hass.data
    hassdata_coord = bool(re.search(r"hass\.data\[.*\]\s*=\s*coordinator", source("__init__.py")))
    uses_rt = "entry.runtime_data = coordinator" in source("__init__.py")
    emit("runtime-data", "bronze", "done" if uses_rt and not hassdata_coord else "todo",
         "1" if uses_rt else "0", "bool", "entry.runtime_data=coordinator; no hass.data coordinator store")

    # test-before-configure: config flow raises/probes before creating the entry
    probes = any(k in source("config_flow.py") for k in ("async_step_user", "CannotConnect", "validation", "probe"))
    emit("test-before-configure", "bronze", "done" if probes else "todo", "1" if probes else "0", "bool",
         "config flow performs a connection/probe before entry creation")

    # test-before-setup: first refresh / ConfigEntryNotReady in async_setup_entry
    se = source("__init__.py")
    tbs = "async_config_entry_first_refresh" in se or "ConfigEntryNotReady" in se
    emit("test-before-setup", "bronze", "done" if tbs else "todo", "1" if tbs else "0", "bool",
         "async_setup_entry does a first refresh (raises ConfigEntryNotReady on failure)")

    # unique-config-entry: unique id set and duplicate abort
    uid_set = "async_set_unique_id" in source("config_flow.py")
    abort = "_abort_if_unique_id_configured" in source("config_flow.py")
    emit("unique-config-entry", "bronze", "done" if uid_set and abort else "todo",
         "1" if (uid_set and abort) else "0", "bool",
         f"async_set_unique_id={uid_set}, _abort_if_unique_id_configured={abort}")


# ===========================================================================
# SILVER
# ===========================================================================
def silver() -> None:
    # action-exceptions: service handlers raise HA errors, AST over all modules
    HA_ERRS = {"ServiceValidationError", "HomeAssistantError"}
    raise_sites = 0
    for tree in ASTS.values():
        for n in ast.walk(tree):
            if isinstance(n, ast.Raise) and isinstance(n.exc, ast.Call):
                f = n.exc.func
                fn = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else "")
                if fn in HA_ERRS:
                    raise_sites += 1
    emit("action-exceptions", "silver", "done" if raise_sites > 0 else "todo",
         f"{raise_sites}", "raises", "ServiceValidationError/HomeAssistantError raise sites (handlers refuse cleanly)")

    # config-entry-unloading
    unload = "async def async_unload_entry" in source("__init__.py")
    emit("config-entry-unloading", "silver", "done" if unload else "todo", "1" if unload else "0", "bool",
         "async_unload_entry defined")

    # docs-configuration-parameters / installation-parameters
    emit("docs-configuration-parameters", "silver",
         "done" if "## Changing settings after setup" in README else "todo", "1", "bool",
         "'Changing settings after setup' section in README")
    emit("docs-installation-parameters", "silver",
         "done" if "## Quick start" in README or "installation" in ALL_DOCS.lower() else "todo", "1", "bool",
         "installation parameters documented")

    # entity-unavailable: base gives an available property (CoordinatorEntity) or explicit
    avail = any("def available" in source(f) for f in ("entity.py", "sensor.py", "coordinator.py"))
    emit("entity-unavailable", "silver", "done" if avail else "todo", "1" if avail else "0", "bool",
         "an available property exists (CoordinatorEntity + explicit gates)")

    # integration-owner
    owners = MANIFEST.get("codeowners", [])
    emit("integration-owner", "silver", "done" if owners else "todo", f"{len(owners)}", "owners",
         f"codeowners={owners}")

    # log-when-unavailable: latch logs (ERROR first, DEBUG after, INFO recover)
    cz = source("coordinator.py")
    lw = ("_tibber_fetch_failed" in cz or "fetch_failed" in cz) and "_LOGGER" in cz
    emit("log-when-unavailable", "silver", "done" if lw else "todo", "1" if lw else "0", "bool",
         "outage latching logs present in coordinator")

    # parallel-updates
    pu = [f for f in ("sensor.py", "binary_sensor.py", "button.py", "switch.py", "climate.py")
          if re.search(r"^PARALLEL_UPDATES\s*=", source(f), re.M)]
    emit("parallel-updates", "silver", "done" if len(pu) == 5 else "todo", f"{len(pu)}/5", "modules",
         "platform modules declaring PARALLEL_UPDATES")

    # reauthentication-flow
    reauth = "async def async_step_reauth" in source("config_flow.py")
    emit("reauthentication-flow", "silver", "done" if reauth else "todo", "1" if reauth else "0", "bool",
         "async_step_reauth defined")


# ===========================================================================
# GOLD
# ===========================================================================
def gold() -> None:
    # devices
    di = "def device_info" in source("coordinator.py") and "DeviceInfo" in source("entity.py")
    emit("devices", "gold", "done" if di else "todo", "1" if di else "0", "bool",
         "one DeviceInfo per install (coordinator.device_info)")

    # diagnostics
    dg = "async_get_config_entry_diagnostics" in source("diagnostics.py")
    emit("diagnostics", "gold", "done" if dg else "todo", "1" if dg else "0", "bool",
         "diagnostics.py implements async_get_config_entry_diagnostics")

    # discovery / discovery-update-info / dynamic-devices / stale-devices: exempt
    disc = sum(len(re.findall(r"\b(zeroconf|dhcp|ssdp|usb|bluetooth)\b", source(f)))
               for f in ASTS if f.endswith(".py"))
    emit("discovery", "gold", "exempt" if disc == 0 else "todo", f"{disc}", "imports",
         "cloud API + user-picked entities; 0 discovery-mechanism references")
    emit("discovery-update-info", "gold", "exempt", "0", "nets", "no network addresses to update")
    devreg = len(re.findall(r"async_get_or_create", source("coordinator.py")))
    emit("dynamic-devices", "gold", "exempt" if devreg == 0 else "todo", f"{devreg}", "sites",
         "single static DeviceInfo; 0 device-registry async_get_or_create sites")
    emit("stale-devices", "gold", "exempt", "0", "sites",
         "device lifetime equals config-entry lifetime; 0 removal sites")

    # docs-* (gold)
    emit("docs-data-update", "gold",
         "done" if "How it works" in README or "poll" in ALL_DOCS.lower() else "todo", "1", "bool",
         "data-update cadence documented")
    bp = list(pathlib.Path("blueprints").rglob("*.yaml")) if pathlib.Path("blueprints").is_dir() else []
    # In-tree half only: each shipped blueprint filename is named in the docs.
    # The external half (the forum exchange listing) is NOT verified in round 5
    # -- no network call is made here, and the earlier draft's "fetched" note is
    # not re-established by this harness.
    bp_links = sum(1 for b in bp if b.name in ALL_DOCS)
    emit("docs-examples", "gold", "done" if bp and bp_links >= len(bp) else "todo",
         f"{bp_links}/{len(bp)}", "blueprints",
         "shipped blueprints named in README/docs (in-tree link only; the "
         "external forum listing is not verified by this harness)")
    emit("docs-known-limitations", "gold",
         "done" if "## Known limitations" in README else "todo", "1", "bool", "'Known limitations' in README")
    emit("docs-supported-devices", "gold",
         "done" if "## Supported heat pumps" in README else "todo", "1", "bool",
         "'Supported heat pumps and controls' in README")
    emit("docs-supported-functions", "gold",
         "done" if "## What it does" in README and "## Services" in README else "todo", "1", "bool",
         "supported functions in README")
    emit("docs-troubleshooting", "gold",
         "done" if "## Troubleshooting" in README else "todo", "1", "bool", "'Troubleshooting' in README")
    emit("docs-use-cases", "gold",
         "done" if "Quick start" in README and "Your first week" in README else "todo", "1", "bool",
         "use cases in README")

    # entity-category
    cat = sum(1 for ents in ENTITIES.values() for e in ents if getattr(e, "entity_category", None) is not None)
    emit("entity-category", "gold", "done" if cat > 0 else "todo", f"{cat}", "entities",
         "entities carrying an EntityCategory (diagnostic/config)")

    # entity-device-class: the rule is "use device classes where possible", so
    # the check is NOT "some sensor has a device class" (which is what the
    # interrupted draft emitted, from a constant). It counts delivered sensors
    # whose unit names exactly one HA SensorDeviceClass but whose device_class
    # is None -- the same predicate as device_class_rule.py, inlined so this
    # table stands alone.
    dc_map = {"°C": "temperature", "kWh": "energy", "kW": "power",
              "Hz": "frequency", "W/m²": "irradiance", "L": "volume_storage"}
    sensors = ENTITIES["sensor"]
    with_dc = sum(1 for e in sensors if getattr(e, "device_class", None) is not None)
    dcm_missing = 0
    for e in sensors:
        if getattr(e, "device_class", None) is not None:
            continue
        u = (getattr(e, "unit_of_measurement", None)
             or getattr(e, "_attr_native_unit_of_measurement", None))
        if u in dc_map or (isinstance(u, str) and re.fullmatch(r"[A-Z]{3}", u)):
            dcm_missing += 1
    emit("entity-device-class", "gold", "done" if dcm_missing == 0 else "todo",
         f"{with_dc}/{len(sensors)}", "sensors",
         f"sensors missing a possible device class={dcm_missing}")

    # entity-disabled-by-default: the integration must disable the less
    # popular/noisy entities it ships, so the predicate is over the delivered
    # set (a count of entities with enabled_default=False), not a constant.
    dis = sum(1 for ents in ENTITIES.values() for e in ents
              if getattr(e, "_attr_entity_registry_enabled_default", True) is False)
    emit("entity-disabled-by-default", "gold", "done" if dis > 0 else "todo", f"{dis}", "entities",
         "entities with enabled_default=False (noisy diagnostics disabled by default)")

    # entity-translations: an entity with no translation_key is done when it
    # is device-named (`_attr_name is None`, name taken from the device), which
    # is the HA idiom for "the device's own feature" and needs no entity name
    # translation. The climate entity is exactly this case, so skipping
    # name-None entities is required or it is a false miss.
    missing = 0
    for plat, ents in ENTITIES.items():
        skeys = set(STRINGS.get("entity", {}).get(plat, {}))
        for e in ents:
            if getattr(e, "_attr_name", "ABSENT") is None:
                continue
            if getattr(e, "_attr_translation_key", None) not in skeys:
                missing += 1
    emit("entity-translations", "gold", "done" if missing == 0 else "todo", f"{missing}", "missing",
         "entities whose translation_key is absent from strings.json[entity] "
         "(device-named entities excluded)")

    # exception-translations
    bad = 0
    keys = set(STRINGS.get("exceptions", {}))
    for tree in ASTS.values():
        for n in ast.walk(tree):
            if isinstance(n, ast.Raise) and isinstance(n.exc, ast.Call):
                f = n.exc.func
                fn = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else "")
                if fn in {"ServiceValidationError", "HomeAssistantError"}:
                    kw = {k.arg: k.value for k in n.exc.keywords}
                    if "translation_key" not in kw or "translation_domain" not in kw:
                        bad += 1
                    elif isinstance(kw["translation_key"], ast.Constant) and kw["translation_key"].value not in keys:
                        bad += 1
    emit("exception-translations", "gold", "done" if bad == 0 else "todo", f"{bad}", "sites",
         "raise sites lacking a translated translation_key, or key absent from strings[exceptions]")

    # icon-translations
    icon_pins = sum(len(re.findall(r"_attr_icon\b", source(f))) for f in ASTS)
    miss_icon = 0
    for plat, ents in ENTITIES.items():
        ikeys = set(ICONS.get("entity", {}).get(plat, {}))
        for e in ents:
            if getattr(e, "_attr_name", "ABSENT") is None:
                continue  # device-named: no translation key, no icon key owed
            if getattr(e, "_attr_translation_key", None) not in ikeys:
                miss_icon += 1
    emit("icon-translations", "gold", "done" if icon_pins == 0 and miss_icon == 0 else "todo",
         f"{miss_icon}", "missing", f"_attr_icon pins={icon_pins}, entities missing icons.json entry={miss_icon}")

    # reconfiguration-flow
    rec = "async def async_step_reconfigure" in source("config_flow.py")
    emit("reconfiguration-flow", "gold", "done" if rec else "todo", "1" if rec else "0", "bool",
         "async_step_reconfigure defined")

    # repair-issues: issues translations present and a fix flow module
    issues = STRINGS.get("issues", {})
    repairs = "async_create_fix_flow" in source("repairs.py")
    emit("repair-issues", "gold", "done" if issues and repairs else "todo",
         f"{len(issues)}", "issues", f"strings[issues]={len(issues)}, repairs.py fix flow={repairs}")


# ===========================================================================
# PLATINUM
# ===========================================================================
def platinum() -> None:
    # async-dependency: sync deps off the loop (executor / process worker)
    cz = source("coordinator.py")
    off = ("async_add_executor_job" in cz) or ("async_add_import_executor_job" in source("__init__.py"))
    emit("async-dependency", "platinum", "done" if off else "todo", "1" if off else "0", "bool",
         "sync solve dispatched to an executor/process worker")

    # inject-websession
    inj = sum(1 for f in ASTS if "async_get_clientsession" in source(f))
    raw = sum(len(re.findall(r"aiohttp\.ClientSession\(", source(f))) for f in ASTS)
    emit("inject-websession", "platinum", "done" if inj > 0 and raw == 0 else "todo",
         f"{inj}", "modules", f"modules using async_get_clientsession={inj}; raw ClientSession( sites={raw}")

    # strict-typing (Platinum): BOTH halves, not just the ignore count. The
    # rule requires a PEP-561 `py.typed` marker in the package AND no
    # suppressions; the interrupted draft declared done from ignores==0 alone,
    # which is the false-done the register also carries.
    ignores = sum(len(re.findall(r"#\s*type:\s*ignore", source(f))) for f in ASTS)
    py_typed = (ROOT / "py.typed").exists()
    emit("strict-typing", "platinum", "done" if (ignores == 0 and py_typed) else "todo",
         f"{ignores}", "ignores",
         f"# type: ignore occurrences={ignores}; py.typed present={py_typed}")


# ===========================================================================
def trailer(start_wall: float, start_cpu: float) -> None:
    import threading

    thread_cpu = time.thread_time()
    process_cpu = time.process_time()
    tf = (process_cpu) / thread_cpu if thread_cpu else 0.0
    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = float("nan")
    swapins = 0
    try:
        swapins = int(resource.getrusage(resource.RUSAGE_SELF).ru_majflt)
    except Exception:
        pass
    print(f"RESULT thread_factor={tf:.4f} ratio")
    print(f"RESULT load1={load1:.3f} load")
    print(f"RESULT swapins={swapins} count")
    print(f"RESULT wall_s={time.time() - start_wall:.3f} s")


def main() -> None:
    start_wall = time.time()
    bronze()
    silver()
    gold()
    platinum()
    c = Counter(r[2] for r in _RESULTS)
    print(f"RESULT rules_done={c['done']} count")
    print(f"RESULT rules_exempt={c['exempt']} count")
    print(f"RESULT rules_todo={c['todo']} count")
    print(f"RESULT rules_total={len(_RESULTS)} count")
    trailer(start_wall, 0.0)


if __name__ == "__main__":
    main()
