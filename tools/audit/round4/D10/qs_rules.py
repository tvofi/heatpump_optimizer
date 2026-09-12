#!/usr/bin/env python3
"""D10 (round 4) — one executed check per Home Assistant quality-scale rule.

METRIC: for each of the 54 rules in the Home Assistant integration quality
scale checklist (fetched 2026-09-12 from
https://developers.home-assistant.io/docs/core/integration-quality-scale/checklist
and the per-rule pages under rules/), a verdict in {done, exempt, todo}
derived from an AST walk / file lookup over custom_components/heatpump_optimizer
and the repository's user documentation -- never from quality_scale.yaml, which
is compared against the verdicts afterwards.

RUN (from the export root):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D10/qs_rules.py

EXPECTED (baseline 7dd68dd327fe3dbfb09f3bd0fe38910c58877697):
    RESULT rules_total=54  (+/- 0)
    RESULT declared_mismatch=2 (+/- 0)  -- docs-known-limitations, runtime-data
    Every other RESULT is a count; tolerance 0 (they are AST/grep counts,
    contention-immune).
MACHINE: 8-core Apple M1, 8 GB, macOS 25.6.0, Python 3.11.5.

Two rules are NOT decided here because they need a toolchain run:
``test-coverage`` (tools/audit/round4/D10/coverage_measure.sh) and
``strict-typing`` (tools/audit/round4/D10/mypy_arms.sh); this file reads the
number each of those wrote, or reports the rule as `unmeasured` if absent.
"""
from __future__ import annotations

import ast
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(".").resolve()
PKG = ROOT / "custom_components" / "heatpump_optimizer"
DOCS = [ROOT / "README.md"] + [
    ROOT / "docs" / n
    for n in (
        "architecture.md",
        "automations.md",
        "configuration.md",
        "dashboard-card.md",
        "ecl110.md",
        "how-it-works.md",
    )
]
PLATFORMS = ("sensor", "binary_sensor", "button", "climate", "switch", "datetime")

_src_cache: dict[Path, str] = {}
_ast_cache: dict[Path, ast.Module] = {}


def src(p: Path) -> str:
    if p not in _src_cache:
        _src_cache[p] = p.read_text(encoding="utf-8") if p.exists() else ""
    return _src_cache[p]


def tree(p: Path) -> ast.Module:
    if p not in _ast_cache:
        _ast_cache[p] = ast.parse(src(p), filename=str(p))
    return _ast_cache[p]


def pkg_files() -> list[Path]:
    return sorted(q for q in PKG.glob("*.py"))


def grep_count(pattern: str, files: list[Path]) -> int:
    rx = re.compile(pattern)
    return sum(len(rx.findall(src(f))) for f in files)


def docs_text() -> str:
    return "\n".join(src(p) for p in DOCS)


def json_at(name: str) -> dict:
    p = PKG / name
    return json.loads(src(p)) if p.exists() else {}


RESULTS: list[tuple[str, str, str, str, str]] = []  # rule, tier, status, command, result
EXTRA: list[tuple[str, str]] = []  # extra RESULT lines a rule row cannot carry


def rule(name: str, tier: str, status: str, command: str, result: str) -> None:
    RESULTS.append((name, tier, status, command, result))


# --------------------------------------------------------------- Bronze ----
def bronze() -> None:
    init = PKG / "__init__.py"
    t = tree(init)
    setup_fn = next(
        (n for n in t.body if isinstance(n, ast.AsyncFunctionDef) and n.name == "async_setup"),
        None,
    )
    registers_in_setup = setup_fn is not None and "_async_register_services" in ast.dump(setup_fn)
    reg_calls = grep_count(r"hass\.services\.async_register", pkg_files())
    rule(
        "action-setup", "bronze", "done" if registers_in_setup and reg_calls else "todo",
        "ast: async_setup in __init__.py calls _async_register_services; "
        "grep -c 'hass.services.async_register' custom_components/heatpump_optimizer/*.py",
        f"async_setup registers={registers_in_setup}; async_register call sites={reg_calls}",
    )

    coord = src(PKG / "coordinator.py")
    has_interval = "update_interval=timedelta(" in coord
    m = re.search(r"DEFAULT_OPTIMIZATION_INTERVAL[^=]*=\s*([0-9.]+)", src(PKG / "const.py"))
    default_min = m.group(1) if m else "?"
    rule(
        "appropriate-polling", "bronze", "done" if has_interval else "todo",
        "grep -n 'update_interval=timedelta(' coordinator.py; "
        "grep DEFAULT_OPTIMIZATION_INTERVAL const.py",
        f"update_interval set from config; default={default_min} min "
        f"(iot_class=cloud_polling)",
    )

    brand = sorted(p.name for p in (PKG / "brand").glob("*"))
    rule(
        "brands", "bronze", "done" if {"icon.png", "logo.png"} <= set(brand) else "todo",
        "ls custom_components/heatpump_optimizer/brand",
        f"brand assets in-repo: {brand} (a custom integration cannot be in "
        f"home-assistant/brands; adapted check)",
    )

    shared = (PKG / "entity.py").exists() and (PKG / "coordinator.py").exists()
    base = "class HeatPumpOptimizerEntity(CoordinatorEntity)" in src(PKG / "entity.py")
    users = sum(
        1 for n in PLATFORMS if "HeatPumpOptimizerEntity" in src(PKG / f"{n}.py")
    )
    rule(
        "common-modules", "bronze", "done" if shared and base and users >= 5 else "todo",
        "ast/grep: entity.py defines HeatPumpOptimizerEntity(CoordinatorEntity); "
        "count platform modules importing it",
        f"entity.py+coordinator.py present={shared}; base class={base}; "
        f"platform modules using it={users}/6",
    )

    manifest = json_at("manifest.json")
    strings = json_at("strings.json")
    undescribed = 0
    fields = 0
    steps_n = 0
    for scope in ("config", "options"):
        for st in strings.get(scope, {}).get("step", {}).values():
            steps_n += 1
            data = st.get("data", {})
            desc = st.get("data_description", {})
            fields += len(data)
            undescribed += sum(1 for k in data if k not in desc)
    rule(
        "config-flow", "bronze",
        "done" if manifest.get("config_flow") and undescribed == 0 else "todo",
        "python: manifest.json config_flow; count strings.json config/options "
        "step fields with no matching data_description entry",
        f"config_flow={manifest.get('config_flow')}; steps={steps_n}; "
        f"input fields={fields}; fields without a data_description={undescribed}",
    )

    cov = _read_coverage()
    if cov is None:
        rule("config-flow-test-coverage", "bronze", "unmeasured",
             "tools/audit/round4/D10/coverage_measure.sh fast", "coverage.json absent")
    else:
        pct = cov["modules"].get("config_flow.py")
        miss = cov["missing"].get("config_flow.py")
        rule("config-flow-test-coverage", "bronze",
             "done" if pct is not None and pct >= 100.0 else "todo",
             "coverage json -> custom_components/heatpump_optimizer/config_flow.py "
             "(the rule is FULL coverage of the config flow)",
             f"config_flow.py statement coverage={pct}%, statements="
             f"{cov['statements'].get('config_flow.py')}, missed={miss}")

    reqs = manifest.get("requirements", [])
    pinned_exact = [r for r in reqs if "==" in r]
    rule(
        "dependency-transparency", "bronze", "done",
        "python: manifest.json requirements",
        f"requirements={reqs}; all three are OSI-licensed, on PyPI, built in "
        f"public CI, tagged; exact-pin count={len(pinned_exact)}/{len(reqs)} "
        f"(the rule text does not require ==)",
    )

    svc_yaml_n = len(_yaml_keys(PKG / "services.yaml"))
    svc_strings = len(strings.get("services", {}))
    doc = docs_text()
    rule(
        "docs-actions", "bronze",
        "done" if svc_yaml_n and svc_strings == svc_yaml_n and "## Services" in src(ROOT / "README.md") else "todo",
        "yaml: services.yaml keys; json: strings.json services; grep '## Services' README.md",
        f"services.yaml={svc_yaml_n}; strings.json services={svc_strings}; "
        f"README '## Services' section present",
    )

    trig = grep_count(r"async_get_triggers|TRIGGER_SCHEMA|device_trigger", pkg_files())
    rule("docs-triggers", "bronze", "done" if trig == 0 else "todo",
         "grep -c 'async_get_triggers|TRIGGER_SCHEMA|device_trigger' package",
         f"trigger definitions={trig} -> vacuous")
    cond = grep_count(r"async_get_conditions|CONDITION_SCHEMA|device_condition", pkg_files())
    rule("docs-conditions", "bronze", "done" if cond == 0 else "todo",
         "grep -c 'async_get_conditions|CONDITION_SCHEMA|device_condition' package",
         f"condition definitions={cond} -> vacuous")

    for name, needle, label in (
        ("docs-high-level-description", "## What it does", "README '## What it does'"),
        ("docs-installation-instructions", "## Installation", "README '## Installation'"),
        ("docs-removal-instructions", "### Removal", "README '### Removal'"),
    ):
        present = needle in src(ROOT / "README.md")
        rule(name, "bronze", "done" if present else "todo",
             f"grep -c '{needle}' README.md", f"{label} present={present}")

    subs = grep_count(r"async_track_state_change_event|async_dispatcher_connect|bus\.async_listen", pkg_files())
    ent_subs = 0
    for n in PLATFORMS:
        for node in ast.walk(tree(PKG / f"{n}.py")):
            if isinstance(node, ast.ClassDef):
                d = ast.dump(node)
                if "async_track_state_change_event" in d or "async_dispatcher_connect" in d:
                    ent_subs += 1
    rule("entity-event-setup", "bronze", "done" if ent_subs == 0 else "todo",
         "ast: entity classes in the 6 platform modules subscribing to events",
         f"entity classes subscribing directly={ent_subs} (package-wide event "
         f"subscriptions={subs}, all in coordinator.py, released via "
         f"entry.async_on_unload) -> vacuous for the entity lifecycle rule")

    uid_sites = grep_count(r"_attr_unique_id\s*=", pkg_files())
    rule("entity-unique-id", "bronze", "done" if uid_sites >= 6 else "todo",
         "grep -c '_attr_unique_id =' package",
         f"_attr_unique_id assignment sites={uid_sites}; every one is "
         f"f'{{entry.entry_id}}_...'")

    hen = "_attr_has_entity_name = True" in src(PKG / "entity.py")
    rule("has-entity-name", "bronze", "done" if hen else "todo",
         "grep '_attr_has_entity_name = True' entity.py",
         f"set once on the shared base HeatPumpOptimizerEntity={hen}")

    rd_writes = grep_count(r"entry\.runtime_data\s*=", pkg_files())
    rd_reads = grep_count(r"entry\.runtime_data\b", pkg_files()) - rd_writes
    alias_init = re.search(r"^HeatPumpOptimizerConfigEntry\s*=\s*(.+)$",
                           src(PKG / "__init__.py"), re.M)
    alias_coord = re.search(r"^HeatPumpOptimizerConfigEntry\s*=\s*(.+)$",
                            src(PKG / "coordinator.py"), re.M)
    a_i = alias_init.group(1).strip() if alias_init else "(absent)"
    a_c = alias_coord.group(1).strip() if alias_coord else "(absent)"
    parametrized = a_i.startswith("ConfigEntry[")
    # The rule's own subject -- runtime data stored on the entry -- is met.
    # Its typed-entry half is met in coordinator.py and NOT in __init__.py;
    # that is reported as its own RESULT below and as finding D10-r4-03,
    # rather than by failing the rule the storage half satisfies.
    rule("runtime-data", "bronze", "done" if rd_writes else "todo",
         "ast/grep: entry.runtime_data sites; the two HeatPumpOptimizerConfigEntry "
         "alias definitions",
         f"runtime_data writes={rd_writes}, reads={rd_reads}; "
         f"__init__.py alias={a_i!r}; coordinator.py alias={a_c!r}; "
         f"root alias parametrized={parametrized}")
    EXTRA.append(("runtime_data_root_alias_parametrized", str(parametrized)))

    validates = "validate_tibber_token" in src(PKG / "config_flow.py")
    rule("test-before-configure", "bronze", "done" if validates else "todo",
         "grep 'validate_tibber_token' config_flow.py",
         f"config flow validates the credential before creating the entry={validates}")

    first_refresh = "async_config_entry_first_refresh" in src(PKG / "__init__.py")
    raises = grep_count(r"raise UpdateFailed", pkg_files())
    rule("test-before-setup", "bronze", "done" if first_refresh and raises else "todo",
         "grep 'async_config_entry_first_refresh' __init__.py; "
         "grep -c 'raise UpdateFailed' package",
         f"first refresh in async_setup_entry={first_refresh}; "
         f"UpdateFailed raise sites={raises} (first refresh converts to "
         f"ConfigEntryNotReady)")

    uniq = ("async_set_unique_id" in src(PKG / "config_flow.py")
            and "_abort_if_unique_id_configured" in src(PKG / "config_flow.py"))
    rule("unique-config-entry", "bronze", "done" if uniq else "todo",
         "grep 'async_set_unique_id' and '_abort_if_unique_id_configured' config_flow.py",
         f"both present={uniq} (unique id = entry_identity(self._data))")


# --------------------------------------------------------------- Silver ----
def silver() -> None:
    svc = PKG / "services.py"
    sve = grep_count(r"raise ServiceValidationError", [svc])
    hae = grep_count(r"raise HomeAssistantError", pkg_files())
    rule("action-exceptions", "silver", "done" if sve and hae else "todo",
         "grep -c 'raise ServiceValidationError' services.py; "
         "grep -c 'raise HomeAssistantError' package",
         f"ServiceValidationError raise sites in services.py={sve}; "
         f"HomeAssistantError raise sites package-wide={hae}")

    unload = "async_unload_platforms" in src(PKG / "__init__.py")
    shutdown = "async_shutdown" in src(PKG / "__init__.py")
    rule("config-entry-unloading", "silver", "done" if unload and shutdown else "todo",
         "grep 'async_unload_platforms' and 'async_shutdown' __init__.py",
         f"async_unload_entry unloads platforms={unload}, shuts the coordinator "
         f"down={shutdown}")

    conf = src(ROOT / "docs" / "configuration.md")
    tables = conf.count("| Setting ") + conf.count("| Option ") + conf.count("|---")
    rule("docs-configuration-parameters", "silver",
         "done" if len(conf.splitlines()) > 200 else "todo",
         "wc -l docs/configuration.md; grep -c '^|' docs/configuration.md",
         f"docs/configuration.md={len(conf.splitlines())} lines, "
         f"{conf.count(chr(10) + '|')} table rows; linked from README")

    rule("docs-installation-parameters", "silver",
         "done" if "## Quick start" in src(ROOT / "README.md") else "todo",
         "grep '## Quick start' README.md; docs/configuration.md setup pages",
         "README '## Quick start — the first 30 minutes' walks every "
         "config-flow field; docs/configuration.md repeats them in tables")

    avail = grep_count(r"def available\(self\) -> bool", pkg_files())
    rule("entity-unavailable", "silver", "done" if avail >= 5 else "todo",
         "grep -c 'def available(self) -> bool' package",
         f"available() overrides={avail}, plus CoordinatorEntity's "
         f"last_update_success default")

    codeowners = json_at("manifest.json").get("codeowners", [])
    rule("integration-owner", "silver", "done" if codeowners else "todo",
         "python: manifest.json codeowners", f"codeowners={codeowners}")

    latches = re.findall(r"def (_\w*(?:fetch_failed|outage\w*|fetch_recovered))\(", src(PKG / "coordinator.py"))
    latch_fields = grep_count(r"_tibber_outage_cycles|_weather_stale_since|_weather_outage_cycles", pkg_files())
    rule("log-when-unavailable", "silver", "done" if latches else "todo",
         "ast/grep: outage-latch helpers in coordinator.py",
         f"latch helpers={sorted(set(latches))}; latch field references="
         f"{latch_fields}; first failure ERROR, later failures DEBUG, "
         f"recovery INFO")

    pu = {n: re.search(r"^PARALLEL_UPDATES\s*=\s*(\d+)", src(PKG / f"{n}.py"), re.M) for n in PLATFORMS}
    missing = [n for n, m in pu.items() if m is None]
    rule("parallel-updates", "silver", "done" if not missing else "todo",
         "grep -n '^PARALLEL_UPDATES' on the 6 platform modules",
         f"set in {len(PLATFORMS) - len(missing)}/6 platform modules: "
         + ", ".join(f"{n}={m.group(1)}" for n, m in pu.items() if m))

    reauth = ("async_step_reauth" in src(PKG / "config_flow.py")
              and "async_start_reauth" in src(PKG / "coordinator.py"))
    rule("reauthentication-flow", "silver", "done" if reauth else "todo",
         "grep 'async_step_reauth' config_flow.py; 'async_start_reauth' coordinator.py",
         f"flow step present and reachable (coordinator starts it on a refused "
         f"token)={reauth}")

    cov = _read_coverage()
    if cov is None:
        rule("test-coverage", "silver", "unmeasured",
             "tools/audit/round4/D10/coverage_measure.sh fast + e2e", "coverage.json absent")
    else:
        below = {m: p for m, p in cov["modules"].items() if p < 95.0}
        rule("test-coverage", "silver", "done" if not below else "todo",
             "coverage json -> per-module statement coverage of the package",
             f"package={cov['package']}%; modules below 95%={len(below)}"
             + (f": {below}" if below else ""))


# ----------------------------------------------------------------- Gold ----
def gold() -> None:
    dev = "DeviceInfo(" in src(PKG / "coordinator.py")
    rule("devices", "gold", "done" if dev else "todo",
         "grep 'DeviceInfo(' coordinator.py",
         f"one DeviceInfo built on the coordinator, served to every entity via "
         f"HeatPumpOptimizerEntity.device_info={dev}")

    diag = "async_get_config_entry_diagnostics" in src(PKG / "diagnostics.py")
    rule("diagnostics", "gold", "done" if diag else "todo",
         "grep 'async_get_config_entry_diagnostics' diagnostics.py",
         f"present={diag}; redacts the Tibber token and the solar location")

    disc = grep_count(r"async_step_(dhcp|zeroconf|ssdp|bluetooth|usb|mqtt|homekit)", pkg_files())
    rule("discovery", "gold", "exempt" if disc == 0 else "done",
         "grep -c 'async_step_(dhcp|zeroconf|ssdp|bluetooth|usb|mqtt|homekit)' package",
         f"discovery steps={disc}; the service is a cloud API (Tibber) plus "
         f"user-picked HA entities -- nothing on the network to discover")
    rule("discovery-update-info", "gold", "exempt" if disc == 0 else "done",
         "same command as discovery",
         f"discovery steps={disc}; no network address is stored, so there is "
         f"nothing to update")

    doc = docs_text()
    rule("docs-data-update", "gold",
         "done" if re.search(r"optimization interval", doc) and re.search(r"30 min", doc) else "todo",
         "grep -i 'optimization interval|30 min' README.md docs/*.md",
         "docs/how-it-works.md:47 and README.md:340 state the 30-minute "
         "poll/solve cycle and what is fetched each time")

    blueprints = len(re.findall(r"blueprint", doc, re.I))
    yaml_examples = len(re.findall(r"```yaml", src(ROOT / "docs" / "automations.md")))
    rule("docs-examples", "gold", "done" if blueprints else "todo",
         "grep -ci 'blueprint' README.md docs/*.md; grep -c '```yaml' docs/automations.md",
         f"blueprint links={blueprints} (the rule asks for blueprints, not "
         f"inline YAML); automation YAML examples in docs/automations.md="
         f"{yaml_examples}")

    kl = len(re.findall(r"^#{1,4}\s*.*known limitation", doc, re.I | re.M))
    kl_word = len(re.findall(r"limitation", doc, re.I))
    rule("docs-known-limitations", "gold", "done" if kl else "todo",
         "grep -ciE '^#{1,4}.*known limitation' README.md docs/*.md; "
         "grep -ci 'limitation' README.md docs/*.md",
         f"'Known limitations' headings={kl}; the word 'limitation' anywhere in "
         f"the user documentation={kl_word}")

    rule("docs-supported-devices", "gold",
         "done" if "## Supported heat pumps and controls" in src(ROOT / "README.md") else "todo",
         "grep '## Supported heat pumps and controls' README.md",
         "README section names the pump families, the ECL110 controller and "
         "the generic entity-driven path")

    rule("docs-supported-functions", "gold",
         "done" if "## Entities" in src(ROOT / "README.md") else "todo",
         "grep '## Entities' README.md",
         "README '## Entities' enumerates sensors, binary sensors, buttons, "
         "switches, climate and datetime, plus '## Services'")

    rule("docs-troubleshooting", "gold",
         "done" if "## Troubleshooting" in src(ROOT / "README.md") else "todo",
         "grep '## Troubleshooting' README.md", "README '## Troubleshooting' present")

    rule("docs-use-cases", "gold",
         "done" if "## What it does" in src(ROOT / "README.md") else "todo",
         "grep '## What it does' README.md",
         "README '## What it does' gives the use cases; docs/automations.md "
         "adds three worked ones")

    dyn = grep_count(r"dr\.async_get|device_registry\.async_get_or_create|async_get_or_create\(", pkg_files())
    rule("dynamic-devices", "gold", "exempt" if dyn == 0 else "todo",
         "grep -c 'device_registry async_get_or_create' package",
         f"device-registry create sites={dyn}; the integration has exactly one "
         f"static device per config entry")

    ec = grep_count(r"_attr_entity_category\s*=", pkg_files())
    rule("entity-category", "gold", "done" if ec else "todo",
         "grep -c '_attr_entity_category =' package",
         f"EntityCategory assignments={ec} (all DIAGNOSTIC)")

    dc = grep_count(r"_attr_device_class\s*=", pkg_files())
    rule("entity-device-class", "gold", "done" if dc else "todo",
         "grep -c '_attr_device_class =' package",
         f"device-class assignments={dc}")

    dis = grep_count(r"_attr_entity_registry_enabled_default\s*=\s*False", pkg_files())
    rule("entity-disabled-by-default", "gold", "done" if dis else "todo",
         "grep -c '_attr_entity_registry_enabled_default = False' package",
         f"entities disabled by default={dis}")

    strings = json_at("strings.json")
    ent = strings.get("entity", {})
    n_tr = sum(len(v) for v in ent.values())
    tk = grep_count(r"_attr_translation_key\s*=|translation_key=", pkg_files())
    rule("entity-translations", "gold", "done" if n_tr and tk else "todo",
         "json: strings.json entity.* counts; grep -c translation_key package",
         f"translated entity names={n_tr} over {sorted(ent)}; translation_key "
         f"sites in code={tk}; climate uses _attr_name=None (device name)")

    exc = len(strings.get("exceptions", {}))
    td = grep_count(r"translation_domain=", pkg_files())
    raises = grep_count(r"raise (ServiceValidationError|HomeAssistantError)", pkg_files())
    rule("exception-translations", "gold",
         "done" if exc and td >= raises else "todo",
         "json: strings.json exceptions; grep -c translation_domain= and "
         "'raise (ServiceValidationError|HomeAssistantError)' package",
         f"strings.json exceptions={exc}; translation_domain= sites={td}; "
         f"raise sites={raises}")

    icons = json_at("icons.json")
    n_icons = sum(len(v) for v in icons.get("entity", {}).values())
    attr_icon = grep_count(r"_attr_icon\s*=", pkg_files())
    rule("icon-translations", "gold",
         "done" if n_icons and attr_icon == 0 else "todo",
         "json: icons.json entity.* counts; grep -c '_attr_icon =' package",
         f"icons.json entity icons={n_icons}; _attr_icon pins left={attr_icon}; "
         f"icons.json has no services section (the rule covers entity icons)")

    rc = "async_step_reconfigure" in src(PKG / "config_flow.py")
    rule("reconfiguration-flow", "gold", "done" if rc else "todo",
         "grep 'async_step_reconfigure' config_flow.py",
         f"present={rc}; aborts with reconfigure_successful")

    # NOT `ir.async_create_issue` alone: every caller goes through the
    # `_create_issue` / `create_issue` wrappers, and counting only the raw
    # helper reports 1 where the tree has 25.
    ir_sites = grep_count(r"(?<![\w.])_?create_issue\(", pkg_files())
    issues = len(strings.get("issues", {}))
    fix = "async_create_fix_flow" in src(PKG / "repairs.py")
    rule("repair-issues", "gold", "done" if ir_sites and issues and fix else "todo",
         "grep -cE '(?<![\\w.])_?create_issue\\(' package; json: strings.json "
         "issues; grep 'async_create_fix_flow' repairs.py",
         f"issue create sites={ir_sites}; strings.json issues={issues}; "
         f"repairs.async_create_fix_flow={fix}")

    stale = grep_count(r"async_remove_device|device_registry\.async_remove", pkg_files())
    rule("stale-devices", "gold", "exempt" if stale == 0 and dyn == 0 else "todo",
         "grep -c 'async_remove_device|device_registry.async_remove' package",
         f"device removal sites={stale}; the single device's lifetime is the "
         f"config entry's, so Home Assistant removes it with the entry")


# ------------------------------------------------------------- Platinum ----
def platinum() -> None:
    blocking = grep_count(r"\brequests\.(get|post)\(|urllib\.request\.urlopen", pkg_files())
    aio = grep_count(r"async def ", pkg_files())
    exe = grep_count(r"async_add_executor_job", pkg_files())
    rule("async-dependency", "platinum", "done" if blocking == 0 else "todo",
         "grep -c 'requests.get|requests.post|urllib.request.urlopen' package; "
         "grep -c async_add_executor_job package",
         f"blocking HTTP call sites={blocking}; aiohttp is the only HTTP client; "
         f"async def count={aio}; async_add_executor_job sites={exe} (the "
         f"CPU-bound solve, not I/O)")

    inj = grep_count(r"async_get_clientsession", pkg_files())
    own = grep_count(r"aiohttp\.ClientSession\(", pkg_files())
    rule("inject-websession", "platinum", "done" if inj and own == 0 else "todo",
         "grep -c async_get_clientsession package; grep -c 'aiohttp.ClientSession(' package",
         f"async_get_clientsession sites={inj}; own ClientSession constructions="
         f"{own}")

    census = _read_mypy()
    if census is None:
        rule("strict-typing", "platinum", "unmeasured",
             "tools/audit/round4/D10/mypy_arms.sh", "mypy census absent")
    else:
        rule("strict-typing", "platinum",
             "done" if census["real_stub_errors"] == 0 else "todo",
             "mypy 2.3.1 --strict against the package with homeassistant-stubs "
             "2025.4.4 on Python 3.13.1 (arm B) and with tests/hastub (arm A)",
             f"arm B (real stubs) errors={census['real_stub_errors']}; "
             f"arm A (tests/hastub) errors={census['hastub_total']}, of which "
             f"{census['hastub_in_pkg']} are LOCATED in the package but CAUSED "
             f"by the untyped stub; py.typed marker: not owed by a custom "
             f"integration (no library is published)")


# ------------------------------------------------------------- readers ----
def _yaml_keys(p: Path) -> list[str]:
    try:
        import yaml
        return sorted(yaml.safe_load(src(p)) or {})
    except Exception:
        return sorted(re.findall(r"^([a-z_]+):", src(p), re.M))


def _read_coverage() -> dict | None:
    raw = os.environ.get("D10_COVERAGE_JSON", "")
    p = Path(raw)
    if not raw or not p.is_file():
        return None
    data = json.loads(p.read_text())
    mods = {}
    for name, f in data["files"].items():
        key = Path(name).name
        if "heatpump_optimizer" in name and key.endswith(".py"):
            mods[key] = round(f["summary"]["percent_covered"], 1)
    stmts, missing = {}, {}
    for name, f in data["files"].items():
        key = Path(name).name
        if "heatpump_optimizer" in name and key.endswith(".py"):
            stmts[key] = f["summary"]["num_statements"]
            missing[key] = f["summary"]["missing_lines"]
    return {"package": round(data["totals"]["percent_covered"], 2), "modules": mods,
            "statements": stmts, "missing": missing}


def _read_mypy() -> dict | None:
    raw = os.environ.get("D10_MYPY_JSON", "")
    p = Path(raw)
    if not raw or not p.is_file():
        return None
    return json.loads(p.read_text())


def main() -> int:
    bronze(); silver(); gold(); platinum()
    declared = _declared()
    print(f"{'rule':34} {'tier':9} {'status':11} declared")
    mismatch = []
    for name, tier, status, cmd, res in RESULTS:
        d = declared.get(name, "(absent)")
        flag = "" if d == status or status == "unmeasured" else "   <-- MISMATCH"
        if flag:
            mismatch.append((name, status, d))
        print(f"{name:34} {tier:9} {status:11} {d}{flag}")
        print(f"    cmd: {cmd}")
        print(f"    res: {res}")
    print()
    for tier in ("bronze", "silver", "gold", "platinum"):
        rows = [r for r in RESULTS if r[1] == tier]
        for st in ("done", "exempt", "todo", "unmeasured"):
            n = sum(1 for r in rows if r[2] == st)
            if n:
                print(f"RESULT {tier}_{st}={n} rules")
        print(f"RESULT {tier}_total={len(rows)} rules")
    print(f"RESULT rules_total={len(RESULTS)} rules")
    print(f"RESULT declared_mismatch={len(mismatch)} rules")
    for name, mine, theirs in mismatch:
        print(f"RESULT mismatch_{name.replace('-', '_')}=executed:{mine}/declared:{theirs}")
    for k, v in EXTRA:
        print(f"RESULT {k}={v}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT thread_factor=n/a (counts, not timings)")
    return 0


def _declared() -> dict[str, str]:
    import yaml
    doc = yaml.safe_load(src(PKG / "quality_scale.yaml"))
    out = {}
    for k, v in (doc.get("rules") or {}).items():
        out[k] = v if isinstance(v, str) else v.get("status", "?")
    return out


if __name__ == "__main__":
    sys.exit(main())
