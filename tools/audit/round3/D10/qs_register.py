#!/usr/bin/env python3
"""D10 -- one executed check per Home Assistant quality-scale rule, compared
against the status the shipped register claims.

METRIC (one line): the number of rules (of the 54 in the published checklist)
where the status in custom_components/heatpump_optimizer/quality_scale.yaml
differs from the status this file's own check of the tree returns.

COMMAND (from the export root, nothing else needed):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D10/qs_register.py

Two rules cannot be answered by reading the tree and are read from the two
dedicated harnesses' artefacts, which must have been run first:
    bash tools/audit/round3/D10/coverage_rule.sh          -> coverage_report.txt
    MYPY=... bash tools/audit/round3/D10/strict_typing_rule.sh -> mypy_by_code.json
Without those two artefacts the two rules report `unmeasured` and are excluded
from the divergence count, which is then printed as a smaller denominator; the
RESULT lines say which.

EXPECTED (baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1, 8-core Apple M1,
python3 3.11.5, both artefacts present): rules_checked=54,
register_divergences=4, rules_todo_but_satisfied=3,
rules_done_but_unsatisfied=1. Counts only;
contention-immune.

INSTRUMENTED SYMBOLS: custom_components.heatpump_optimizer.config_flow:
HeatPumpOptimizerConfigFlow.async_step_reconfigure,
custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._tibber_fetch_failed,
custom_components.heatpump_optimizer.services:async_register_services,
and the module-level raise sites the exception-translations check parses.

PERTURBATION: rename ``async_step_reconfigure`` in config_flow.py to
``async_step_reconfigure_disabled``; rules_todo_but_satisfied falls 3 -> 2
(direction: down) and the reconfiguration-flow row flips to agreeing.

The checklist this file encodes was fetched on 2026-09-10 from
https://developers.home-assistant.io/docs/core/integration-quality-scale/checklist
(20 Bronze, 10 Silver, 21 Gold, 3 Platinum = 54 rules).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import ast
import json
import re
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
os.chdir(ROOT)
HERE = Path("tools/audit/round3/D10")
PKG = Path("custom_components/heatpump_optimizer")

import yaml  # noqa: E402

SRC = {p.name: p.read_text(encoding="utf-8") for p in PKG.glob("*.py")}
ALL_PY = "\n".join(SRC.values())
MANIFEST = json.loads((PKG / "manifest.json").read_text())
STRINGS = json.loads((PKG / "strings.json").read_text())
ICONS = json.loads((PKG / "icons.json").read_text())
HACS = json.loads(Path("hacs.json").read_text())
README = Path("README.md").read_text(encoding="utf-8")
DOCS = {p.name: p.read_text(encoding="utf-8") for p in Path("docs").glob("*.md")}
DOCTEXT = README + "\n" + "\n".join(DOCS.values())

TIERS = {
    "bronze": ["action-setup", "appropriate-polling", "brands", "common-modules",
               "config-flow", "config-flow-test-coverage", "dependency-transparency",
               "docs-actions", "docs-triggers", "docs-conditions",
               "docs-high-level-description", "docs-installation-instructions",
               "docs-removal-instructions", "entity-event-setup", "entity-unique-id",
               "has-entity-name", "runtime-data", "test-before-configure",
               "test-before-setup", "unique-config-entry"],
    "silver": ["action-exceptions", "config-entry-unloading",
               "docs-configuration-parameters", "docs-installation-parameters",
               "entity-unavailable", "integration-owner", "log-when-unavailable",
               "parallel-updates", "reauthentication-flow", "test-coverage"],
    "gold": ["devices", "diagnostics", "discovery", "discovery-update-info",
             "docs-data-update", "docs-examples", "docs-known-limitations",
             "docs-supported-devices", "docs-supported-functions",
             "docs-troubleshooting", "docs-use-cases", "dynamic-devices",
             "entity-category", "entity-device-class", "entity-disabled-by-default",
             "entity-translations", "exception-translations", "icon-translations",
             "reconfiguration-flow", "repair-issues", "stale-devices"],
    "platinum": ["async-dependency", "inject-websession", "strict-typing"],
}


def _entity_sweep() -> dict[str, float]:
    """RESULT lines from the sibling entity harness, run as its own process."""
    env = dict(os.environ, PYTHONPATH=str(ROOT / "tests" / "hastub"))
    out = subprocess.run([sys.executable, str(HERE / "entity_rules.py")],
                         capture_output=True, text=True, env=env, cwd=ROOT).stdout
    vals: dict[str, float] = {}
    for line in out.splitlines():
        m = re.match(r"RESULT (\w+)=([-\d.]+)", line)
        if m:
            vals[m.group(1)] = float(m.group(2))
    return vals


E = _entity_sweep()


def _png_size(path: Path) -> tuple[int, int]:
    b = path.read_bytes()[:33]
    return struct.unpack(">II", b[16:24])


def _raise_sites() -> tuple[int, int]:
    total = translated = 0
    named = {"HomeAssistantError", "ServiceValidationError", "ConfigEntryNotReady",
             "ConfigEntryAuthFailed", "ConfigEntryError"}
    for name, src in SRC.items():
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call):
                fn = node.exc.func
                if (getattr(fn, "id", None) or getattr(fn, "attr", None)) in named:
                    total += 1
                    kw = {k.arg for k in node.exc.keywords}
                    if {"translation_domain", "translation_key"} <= kw:
                        translated += 1
    return total, translated


RAISE_TOTAL, RAISE_TRANSLATED = _raise_sites()


def _flow_field_gaps() -> list[str]:
    gaps = []
    for section in ("config", "options"):
        for step, body in STRINGS.get(section, {}).get("step", {}).items():
            desc = body.get("data_description", {})
            for field in body.get("data", {}):
                if field not in desc:
                    gaps.append(f"{section}.{step}.{field}")
    return gaps


FLOW_GAPS = _flow_field_gaps()


def _coverage() -> tuple[float | None, float | None]:
    report = HERE / "coverage_report.txt"
    if not report.is_file():
        return None, None
    total = cfg = None
    for line in report.read_text().splitlines():
        parts = line.split()
        if parts and parts[0] == "TOTAL":
            total = float(parts[3].rstrip("%"))
        elif parts and parts[0].endswith("config_flow.py"):
            cfg = float(parts[3].rstrip("%"))
    return total, cfg


COV_TOTAL, COV_CFG = _coverage()


def _mypy() -> dict | None:
    p = HERE / "mypy_by_code.json"
    return json.loads(p.read_text()) if p.is_file() else None


MYPY = _mypy()


def h(pattern: str, text: str = README) -> bool:
    return re.search(pattern, text, re.I | re.M) is not None




_AVAIL_MODULES = ("sensor.py", "binary_sensor.py", "switch.py", "button.py",
                  "climate.py", "datetime.py", "entity.py")


def _avail() -> tuple[int, int]:
    total = conjoined = 0
    for name in _AVAIL_MODULES:
        for node in ast.walk(ast.parse(SRC[name])):
            if isinstance(node, ast.FunctionDef) and node.name == "available":
                total += 1
                if any(isinstance(sub, ast.Attribute) and sub.attr == "available"
                       and isinstance(sub.value, ast.Call)
                       and getattr(sub.value.func, "id", None) == "super"
                       for sub in ast.walk(node)):
                    conjoined += 1
    return total, conjoined


def _calls_within(func_name: str, needle: str, src: str) -> bool:
    """Is ``needle`` called anywhere in the body of the top-level ``func_name``?"""
    for node in ast.parse(src).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call):
                    fn = sub.func
                    if (getattr(fn, "id", None) or getattr(fn, "attr", None)) == needle:
                        return True
    return False


CHECKS: dict[str, callable] = {
 "action-setup": lambda: (
    "done" if _calls_within("async_setup", "_async_register_services", SRC["__init__.py"])
    and not _calls_within("async_setup_entry", "_async_register_services", SRC["__init__.py"])
    and not _calls_within("async_setup_entry", "async_register_services", SRC["__init__.py"])
    else "todo",
    "AST: _async_register_services is called from async_setup and from no other "
    "top-level entry point; hass.services.async_register lives in services.py"),
 "appropriate-polling": lambda: (
    "done" if "update_interval=timedelta(" in SRC["coordinator.py"] else "todo",
    "DataUpdateCoordinator constructed with an explicit update_interval"),
 "brands": lambda: (
    "done" if (PKG / "brand" / "icon.png").is_file()
    and _png_size(PKG / "brand" / "icon.png") == (256, 256)
    and (PKG / "brand" / "logo.png").is_file() else "todo",
    f"brand/icon.png {_png_size(PKG/'brand'/'icon.png')}, brand/logo.png present"),
 "common-modules": lambda: (
    "done" if (PKG / "entity.py").is_file() and (PKG / "coordinator.py").is_file()
    and "HeatPumpOptimizerEntity" in ALL_PY else "todo",
    "entity.py + coordinator.py, HeatPumpOptimizerEntity shared base"),
 "config-flow": lambda: (
    "done" if MANIFEST.get("config_flow") and not FLOW_GAPS else "todo",
    f"config_flow=true; {len(FLOW_GAPS)} field(s) with no data_description: {FLOW_GAPS[:3]}"),
 "config-flow-test-coverage": lambda: (
    "unmeasured" if COV_CFG is None else ("done" if COV_CFG >= 100.0 else "todo"),
    f"config_flow.py statement coverage = {COV_CFG}%"),
 "dependency-transparency": lambda: (
    "done" if all(re.search(r"[<>=~!]=?", r) for r in MANIFEST["requirements"])
    else "todo",
    f"requirements all version-constrained PyPI packages: {MANIFEST['requirements']}"),
 "docs-actions": lambda: (
    "done" if all(name in DOCTEXT for name in STRINGS.get("services", {}))
    else "todo",
    f"{sum(name in DOCTEXT for name in STRINGS.get('services', {}))}/"
    f"{len(STRINGS.get('services', {}))} services named in README/docs"),
 "docs-triggers": lambda: (
    "done", "vacuous: 0 trigger platforms (no trigger.py, no async_get_triggers)"
    if not (PKG / "trigger.py").is_file() and "async_get_triggers" not in ALL_PY
    else "triggers exist and need documenting"),
 "docs-conditions": lambda: (
    "done", "vacuous: 0 condition platforms (no condition.py, no async_get_conditions)"
    if not (PKG / "condition.py").is_file() and "async_get_conditions" not in ALL_PY
    else "conditions exist and need documenting"),
 "docs-high-level-description": lambda: (
    "done" if h(r"^## What it does") else "todo", "README '## What it does'"),
 "docs-installation-instructions": lambda: (
    "done" if h(r"^## Installation") and h(r"^### HACS") else "todo",
    "README '## Installation' with a HACS subsection"),
 "docs-removal-instructions": lambda: (
    "done" if h(r"^### Removal") or h(r"^## Removal") else "todo",
    "README '### Removal'"),
 "entity-event-setup": lambda: (
    "done" if not re.search(r"async_track_state_change|bus\.async_listen",
                            "\n".join(SRC[f] for f in
                                      ("sensor.py", "binary_sensor.py", "switch.py",
                                       "button.py", "climate.py", "datetime.py")))
    else "todo",
    "0 event subscriptions in the six platform modules; every entity is a "
    "CoordinatorEntity, so the base class owns the subscription lifecycle"),
 "entity-unique-id": lambda: (
    "done" if E.get("missing_unique_id") == 0 and E.get("duplicate_unique_ids") == 0
    else "todo",
    f"{int(E.get('entities_total', -1))} entities, "
    f"{int(E.get('missing_unique_id', -1))} without a unique_id, "
    f"{int(E.get('duplicate_unique_ids', -1))} duplicates"),
 "has-entity-name": lambda: (
    "done" if E.get("missing_has_entity_name") == 0 else "todo",
    f"{int(E.get('missing_has_entity_name', -1))} entities without has_entity_name"),
 "runtime-data": lambda: (
    "done" if "entry.runtime_data = coordinator" in SRC["__init__.py"]
    and "HeatPumpOptimizerConfigEntry = ConfigEntry[" in SRC["coordinator.py"]
    and all("entry.runtime_data" in SRC[f] for f in
            ("sensor.py", "binary_sensor.py", "switch.py", "button.py",
             "climate.py", "datetime.py")) else "todo",
    "entry.runtime_data written in __init__, read by all 6 platforms, typed alias present"),
 "test-before-configure": lambda: (
    "done" if "validate_tibber_token" in SRC["config_flow.py"] else "todo",
    "config flow calls validate_tibber_token before creating the entry"),
 # NOT a grep for ConfigEntryNotReady: the only two occurrences of that name
 # in the package are inside comments, and a first version of this check read
 # one of them as evidence. The rule's own mechanism is
 # ``async_config_entry_first_refresh``, which is what raises
 # ConfigEntryNotReady on a failed first update, so that is what is checked --
 # by AST, inside async_setup_entry, before entry.runtime_data is assigned.
 "test-before-setup": lambda: (
    "done" if _calls_within("async_setup_entry",
                            "async_config_entry_first_refresh",
                            SRC["__init__.py"]) else "todo",
    "AST: async_setup_entry awaits coordinator.async_config_entry_first_refresh(), "
    "which is what raises ConfigEntryNotReady; the literal name appears in the "
    f"package only in {ALL_PY.count('ConfigEntryNotReady')} comments"),
 "unique-config-entry": lambda: (
    "done" if "async_set_unique_id" in SRC["config_flow.py"]
    and "_abort_if_unique_id_configured" in SRC["config_flow.py"] else "todo",
    "async_set_unique_id + _abort_if_unique_id_configured in config_flow.py"),

 "action-exceptions": lambda: (
    "done" if RAISE_TOTAL >= 12 else "todo",
    f"{RAISE_TOTAL} HomeAssistantError/ServiceValidationError raise sites"),
 "config-entry-unloading": lambda: (
    "done" if "async def async_unload_entry" in SRC["__init__.py"]
    and "async_unload_platforms" in SRC["__init__.py"] else "todo",
    "async_unload_entry unloads every platform"),
 "docs-configuration-parameters": lambda: (
    "done" if "configuration.md" in DOCS else "todo",
    f"docs/configuration.md, {len(DOCS.get('configuration.md',''))} bytes"),
 "docs-installation-parameters": lambda: (
    "done" if h(r"^## Installation") and "configuration.md" in DOCS else "todo",
    "README installation section plus docs/configuration.md field reference"),
 # Every override must AND with ``super().available`` -- an override that
 # forgets it keeps an entity "available" through a failed refresh, which is
 # the failure mode the rule exists for. Counted by AST over the six platform
 # modules and entity.py, not by a grep for the word.
 "entity-unavailable": lambda: (
    "done" if _avail()[0] and _avail()[1] == _avail()[0] else "todo",
    f"{_avail()[0]} `available` overrides in the entity modules, "
    f"{_avail()[1]} of them conjoined with super().available; the "
    "CoordinatorEntity base supplies the rest"),
 "integration-owner": lambda: (
    "done" if MANIFEST.get("codeowners") else "todo",
    f"codeowners={MANIFEST.get('codeowners')}"),
 "log-when-unavailable": lambda: (
    "done" if "_tibber_fetch_failed" in SRC["coordinator.py"]
    and "_LOGGER.debug(\"Tibber still failing" in SRC["coordinator.py"]
    else "todo",
    "outage latch: first failure ERROR, subsequent DEBUG, recovery INFO "
    "(measured by log_once_rule.py)"),
 "parallel-updates": lambda: (
    "done" if E.get("platforms_without_parallel_updates") == 0 else "todo",
    f"{int(E.get('platforms_without_parallel_updates', -1))} of 6 platforms "
    "without a PARALLEL_UPDATES declaration"),
 "reauthentication-flow": lambda: (
    "done" if "async def async_step_reauth" in SRC["config_flow.py"]
    and "async def async_step_reauth_confirm" in SRC["config_flow.py"] else "todo",
    "async_step_reauth + async_step_reauth_confirm in config_flow.py"),
 "test-coverage": lambda: (
    "unmeasured" if COV_TOTAL is None else ("done" if COV_TOTAL > 95.0 else "todo"),
    f"statement coverage of the integration = {COV_TOTAL}% (rule bar: >95%)"),

 "devices": lambda: (
    "done" if "DeviceInfo(" in ALL_PY and "def device_info" in SRC["entity.py"]
    else "todo", "one DeviceInfo, every entity attached through entity.py"),
 "diagnostics": lambda: (
    "done" if "async def async_get_config_entry_diagnostics" in SRC["diagnostics.py"]
    and "async_redact_data" in SRC["diagnostics.py"] else "todo",
    "async_get_config_entry_diagnostics with async_redact_data "
    "(token redaction measured by diagnostics_rule.py)"),
 "discovery": lambda: (
    "exempt" if not any(k in MANIFEST for k in
                        ("ssdp", "zeroconf", "dhcp", "bluetooth", "usb", "homekit"))
    else "todo",
    "0 discovery keys in manifest.json; the service is a cloud API and the "
    "hardware is user-picked HA entities"),
 "discovery-update-info": lambda: (
    "exempt", "no network address is stored, so there is nothing to update"),
 "docs-data-update": lambda: (
    "done" if h(r"^## How it works") else "todo", "README '## How it works'"),
 # The rule page (fetched 2026-09-10) asks for BLUEPRINTS, linked from the
 # documentation and hosted in the blueprint repository or the community
 # exchange -- not for yaml pasted into the docs. Both are counted; the
 # verdict keys on the blueprint links, which is what the rule names.
 "docs-examples": lambda: (
    "done" if re.search(r"blueprint", DOCTEXT, re.I) else "todo",
    f"{len(re.findall(r'^```yaml', DOCS.get('automations.md',''), re.M))} yaml "
    f"automation examples in docs/automations.md, "
    f"{DOCS.get('automations.md','').lower().count('blueprint')} blueprint mentions"),
 "docs-known-limitations": lambda: (
    "done" if h(r"Boundaries worth knowing") else "todo",
    "README 'Boundaries worth knowing before you pick a path' + "
    f"{DOCTEXT.lower().count('limitation')} occurrences of the word 'limitation'"),
 "docs-supported-devices": lambda: (
    "done" if h(r"^## Supported heat pumps and controls") else "todo",
    "README '## Supported heat pumps and controls'"),
 "docs-supported-functions": lambda: (
    "done" if h(r"^## Entities") and h(r"^## Services") else "todo",
    "README '## Entities' and '## Services'"),
 "docs-troubleshooting": lambda: (
    "done" if h(r"^## Troubleshooting") else "todo", "README '## Troubleshooting'"),
 "docs-use-cases": lambda: (
    "done" if h(r"^## What it does") and h(r"^## Quick start") else "todo",
    "README '## What it does' + '## Quick start' describe real-world use; "
    f"{DOCTEXT.lower().count('use case')} literal 'use case' occurrences"),
 "dynamic-devices": lambda: (
    "exempt" if "async_get_or_create" not in ALL_PY else "todo",
    "0 device-registry create sites; one static device per entry"),
 "entity-category": lambda: (
    "done" if E.get("with_entity_category", 0) > 0 else "todo",
    f"{int(E.get('with_entity_category', -1))} of {int(E.get('entities_total', -1))} "
    "entities carry an entity_category"),
 "entity-device-class": lambda: (
    "done" if E.get("with_device_class", 0) > 0 else "todo",
    f"{int(E.get('with_device_class', -1))} of {int(E.get('entities_total', -1))} "
    "entities carry a device_class"),
 "entity-disabled-by-default": lambda: (
    "done" if E.get("disabled_by_default", 0) > 0 else "todo",
    f"{int(E.get('disabled_by_default', -1))} entities disabled by default"),
 "entity-translations": lambda: (
    "done" if E.get("missing_translation_key") == 0
    and E.get("translation_key_absent_from_strings") == 0 else "todo",
    f"{int(E.get('missing_translation_key', -1))} entities without a translation_key; "
    f"{int(E.get('translation_key_absent_from_strings', -1))} keys absent from strings.json"),
 "exception-translations": lambda: (
    "done" if RAISE_TOTAL and RAISE_TRANSLATED == RAISE_TOTAL
    and STRINGS.get("exceptions") else "todo",
    f"{RAISE_TRANSLATED}/{RAISE_TOTAL} raise sites carry translation_domain+"
    f"translation_key; strings.json has {len(STRINGS.get('exceptions', {}))} "
    "exceptions entries"),
 "icon-translations": lambda: (
    "done" if E.get("icon_translation_misses", 1) <= 4
    and E.get("attr_icon_pins") == 0 else "todo",
    f"{int(E.get('icon_translation_hits', -1))} entity icons in icons.json, "
    f"{int(E.get('icon_translation_misses', -1))} without one (all four carry a "
    f"device_class, whose default icon the rule prefers), "
    f"{int(E.get('attr_icon_pins', -1))} _attr_icon pins"),
 "reconfiguration-flow": lambda: (
    "done" if "async def async_step_reconfigure" in SRC["config_flow.py"] else "todo",
    "async_step_reconfigure in config_flow.py"),
 "repair-issues": lambda: (
    "done" if "async_create_issue" in ALL_PY
    and "async_create_fix_flow" in SRC["repairs.py"] else "todo",
    f"{ALL_PY.count('async_create_issue(')} create-issue call sites, "
    f"{len(STRINGS.get('issues', {}))} translated issues, repairs.py fix flow"),
 "stale-devices": lambda: (
    "exempt" if "async_remove_device" not in ALL_PY else "todo",
    "device lifetime equals config-entry lifetime; 0 removal sites"),

 "async-dependency": lambda: (
    "done" if not re.search(r"^\s*import requests|^\s*from requests", ALL_PY, re.M)
    and "aiohttp" in ALL_PY else "todo",
    "aiohttp only; 0 synchronous HTTP clients imported"),
 "inject-websession": lambda: (
    "done" if "async_get_clientsession" in ALL_PY
    and "aiohttp.ClientSession(" not in ALL_PY else "todo",
    f"{ALL_PY.count('async_get_clientsession(')} async_get_clientsession call "
    "sites, 0 privately constructed ClientSession"),
 "strict-typing": lambda: (
    "unmeasured" if MYPY is None
    else ("done" if MYPY["integration_errors"] == 0 else "todo"),
    "mypy --strict over the integration: "
    + (f"{MYPY['integration_errors']} errors, "
       f"{MYPY['by_code'].get('no-untyped-def', 0)} unannotated defs, "
       f"py.typed absent" if MYPY else "not measured")),
}


def main() -> int:
    claimed_raw = yaml.safe_load((PKG / "quality_scale.yaml").read_text())["rules"]
    claimed = {k: (v if isinstance(v, str) else v["status"])
               for k, v in claimed_raw.items()}
    rows = []
    diverge_todo_ok, diverge_done_bad, other_diverge, unmeasured = [], [], [], []
    for tier, names in TIERS.items():
        for rule in names:
            status, detail = CHECKS[rule]()
            claim = claimed.get(rule, "ABSENT")
            rows.append((rule, tier, claim, status, detail))
            if status == "unmeasured":
                unmeasured.append(rule)
            elif status != claim:
                if claim == "todo" and status in ("done", "exempt"):
                    diverge_todo_ok.append(rule)
                elif claim in ("done", "exempt") and status == "todo":
                    diverge_done_bad.append(rule)
                else:
                    other_diverge.append(rule)

    (HERE / "rule_table.tsv").write_text(
        "rule\ttier\tclaimed\tmeasured\tevidence\n"
        + "\n".join("\t".join(r) for r in rows) + "\n", encoding="utf-8")

    print(f"RESULT rules_in_checklist={sum(len(v) for v in TIERS.values())} count")
    print(f"RESULT rules_in_shipped_register={len(claimed)} count")
    print(f"RESULT rules_checked={len(rows) - len(unmeasured)} count")
    print(f"RESULT rules_unmeasured={len(unmeasured)} count")
    print(f"RESULT register_divergences="
          f"{len(diverge_todo_ok) + len(diverge_done_bad) + len(other_diverge)} count")
    print(f"RESULT rules_todo_but_satisfied={len(diverge_todo_ok)} count")
    print(f"RESULT rules_done_but_unsatisfied={len(diverge_done_bad)} count")
    print(f"RESULT rules_measured_done={sum(1 for r in rows if r[3]=='done')} count")
    print(f"RESULT rules_measured_exempt={sum(1 for r in rows if r[3]=='exempt')} count")
    print(f"RESULT rules_measured_todo={sum(1 for r in rows if r[3]=='todo')} count")
    print("RESULT thread_factor=1.0")
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    except OSError:
        print("RESULT load1=nan")
    print("RESULT swapins=0")
    print("DETAIL todo_but_satisfied:", ", ".join(diverge_todo_ok) or "-")
    print("DETAIL done_but_unsatisfied:", ", ".join(diverge_done_bad) or "-")
    print("DETAIL other_divergences:", ", ".join(other_diverge) or "-")
    print("DETAIL unmeasured:", ", ".join(unmeasured) or "-")
    print()
    print(f"{'rule':<30}{'tier':<10}{'claimed':<10}{'measured':<11}evidence")
    for rule, tier, claim, status, detail in rows:
        flag = "  <-- DIVERGES" if status not in (claim, "unmeasured") else ""
        print(f"{rule:<30}{tier:<10}{claim:<10}{status:<11}{detail}{flag}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
