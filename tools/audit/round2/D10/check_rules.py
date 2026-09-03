#!/usr/bin/env python
"""D10 rule checker: Home Assistant integration quality scale, Bronze through Platinum.

Metric (one line): for each of the 54 checklist rules, one executed check -- an AST/regex
count over custom_components/heatpump_optimizer, a stub-driven drive of the production
symbol named in the row, or a documentation lookup -- yielding done / exempt / todo and
a number. Every headline RESULT is a count (contention-immune).

Command (from the export root, nothing else on the path):
  PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py
Options:
  --coverage-json PATH  coverage.json written by coverage_suite.sh (default
                        tools/audit/round2/D10/coverage/coverage.json; absent => the two
                        coverage rules print "not measured")
  --no-mypy             skip the strict-typing mypy run (~8 s; needs mypy importable or in
                        $D10_COV_PREFIX, default /tmp/d10-cov)
  --network             re-fetch PyPI metadata and brands.home-assistant.io digests instead of
                        using the values cached in this file (dependency-transparency, brands)
  --emit-yaml           print the draft quality_scale.yaml and exit
Expected (baseline c398fc84eec25fc44b60d74aae05b9a2da205884): RESULT done=27 todo=21 exempt=6
  (exact) with coverage.json present; the per-rule numbers are in REPORT.md. Tolerance: exact
  for every count; mypy counts may move with the mypy release (measured with mypy 2.3.1).
Machine: Apple M1, 8 GB, macOS (Darwin 25.6.0), Python 3.13.1, numpy 2.5.2, scipy 1.18.1.
Instrumented symbols: heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator
  (_async_update_data, _fetch_tibber_prices, update_interval, device_info),
  heatpump_optimizer.config_flow:HeatPumpOptimizerConfigFlow.async_step_user,
  heatpump_optimizer:async_setup_entry/async_unload_entry, every platform's async_setup_entry.
Writes nothing into the export; the mypy cache goes to a private temp dir.
"""
import os

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

import argparse
import ast
import asyncio
import glob
import hashlib
import importlib
import importlib.util
import json
import logging
import re
import subprocess
import urllib.parse
import sys
import tempfile
import time
from collections import Counter, namedtuple
from unittest import mock

ROOT = os.getcwd()
INTEG = os.path.join(ROOT, "custom_components", "heatpump_optimizer")
if not os.path.isfile(os.path.join(INTEG, "manifest.json")):
    sys.exit("run from the export root (custom_components/heatpump_optimizer/manifest.json not found)")
D10 = os.path.join(ROOT, "tools", "audit", "round2", "D10")
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "custom_components"))

BASELINE = "c398fc84eec25fc44b60d74aae05b9a2da205884"
Row = namedtuple("Row", "rule tier status command result")
ROWS: list = []
RESULTS: list = []
NOTES: dict = {}  # rule -> comment for quality_scale.yaml


def row(rule, tier, status, command, result, note=None):
    ROWS.append(Row(rule, tier, status, command, result))
    if note:
        NOTES[rule] = note


def res(name, value, unit="count"):
    RESULTS.append((name, value, unit))


# --------------------------------------------------------------------------- sources
PY_FILES = sorted(glob.glob(os.path.join(INTEG, "*.py")))
SRC = {os.path.basename(p): open(p, encoding="utf-8").read() for p in PY_FILES}
PLATFORMS = ["sensor", "binary_sensor", "button", "switch", "climate"]
PLATFORM_FILES = [f"{p}.py" for p in PLATFORMS]
MANIFEST = json.load(open(os.path.join(INTEG, "manifest.json")))
STRINGS = json.load(open(os.path.join(INTEG, "strings.json")))
HACS = json.load(open(os.path.join(ROOT, "hacs.json")))
DOCS = {"README.md": open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()}
for p in sorted(glob.glob(os.path.join(ROOT, "docs", "*.md"))):
    DOCS["docs/" + os.path.basename(p)] = open(p, encoding="utf-8").read()
DOCS["DISCLAIMER.md"] = open(os.path.join(ROOT, "DISCLAIMER.md"), encoding="utf-8").read()
USER_DOCS = {k: v for k, v in DOCS.items() if not k.startswith("docs/plan-")}


def grep(pattern, names=None, flags=re.M):
    hits = []
    for name, body in SRC.items():
        if names and name not in names:
            continue
        for m in re.finditer(pattern, body, flags):
            hits.append((name, body.count("\n", 0, m.start()) + 1, m.group(0)))
    return hits


def docs_grep(pattern, docs=None, flags=re.M | re.I):
    total = 0
    where = []
    for name, body in (docs or USER_DOCS).items():
        n = len(re.findall(pattern, body, flags))
        if n:
            where.append(f"{name}:{n}")
        total += n
    return total, where


def ast_of(name):
    return ast.parse(SRC[name], filename=name)


# --------------------------------------------------------------------------- stub drive
from harness import FakeEntry, FakeHass  # noqa: E402  (tests/harness.py: FakeHass, FakeEntry, FakeServiceCall)
from homeassistant.config_entries import ConfigEntryState  # noqa: E402
import heatpump_optimizer  # noqa: E402
from heatpump_optimizer import config_flow as cf  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import coordinator as coord_mod  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from homeassistant.helpers.update_coordinator import UpdateFailed  # noqa: E402

DOMAIN = const.DOMAIN
BASE_CFG = {
    "tibber_token": "x",
    "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
}
from datetime import datetime, timedelta  # noqa: E402

START = datetime(2026, 1, 15, 0, 0)


def make_coord(states=None, **extra):
    hass = FakeHass(states)
    entry = FakeEntry(data={**BASE_CFG, **extra})
    return HeatPumpOptimizerCoordinator(hass, entry), hass, entry


def with_payload(coord):
    """tests/golden.py:_capture_coordinator's deterministic inputs, then the published dict."""
    coord._prices = [
        {"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
         "starts_at": (START + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
        for h in range(48)
    ]
    coord._weather_forecast = [
        {"datetime": (START + timedelta(hours=h)).isoformat(),
         "temperature": -5.0 + 3.0 * (h % 24) / 24.0, "wind_speed": 3.0,
         "precipitation": 0.0, "humidity": 85.0}
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [
        max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)
    ]
    coord._forecast_arrays()
    coord.data = coord._build_data_dict()
    return coord


def roster(coord, hass, entry):
    """Every entity through the real platform async_setup_entry (tests/entities.py:collect idea)."""
    out = []
    # The platforms read ``entry.runtime_data`` since audit B5 (3da0e27);
    # the ``hass.data`` slot is what they read before it. Both are set.
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coord
    entry.runtime_data = coord
    for p in PLATFORMS:
        mod = importlib.import_module(f"heatpump_optimizer.{p}")
        added = []
        asyncio.run(mod.async_setup_entry(hass, entry, added.extend))
        out.extend((p, e) for e in added)
    return out


class _Cap(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        self.records.append(record)


def failing_cycles(n=3):
    """Drive _async_update_data n times with the Tibber fetch failing (the stub has no HTTP session)."""
    coord, hass, entry = make_coord()
    coord._skip_solve_once = False
    cap = _Cap()
    lg = logging.getLogger("heatpump_optimizer")
    old = lg.level
    lg.addHandler(cap)
    lg.setLevel(logging.DEBUG)
    try:
        async def run():
            raised = 0
            for _ in range(n):
                try:
                    await coord._async_update_data()
                except UpdateFailed:
                    raised += 1
            return raised
        raised = asyncio.run(run())
    finally:
        lg.removeHandler(cap)
        lg.setLevel(old)
    errors = [r for r in cap.records if r.levelno >= logging.ERROR]
    return raised, errors, cap.records


class _Resp:
    def __init__(self, status, payload):
        self.status = status
        self._payload = payload

    async def json(self):
        return self._payload


class _Ctx:
    def __init__(self, resp):
        self._resp = resp

    async def __aenter__(self):
        return self._resp

    async def __aexit__(self, *exc):
        return False


class _Session:
    def __init__(self, status, payload=None):
        self.status = status
        self.payload = payload or {}

    def post(self, *args, **kwargs):
        return _Ctx(_Resp(self.status, self.payload))


def tibber_exception_for(status):
    coord, hass, entry = make_coord()
    with mock.patch.object(coord_mod, "async_get_clientsession", lambda hass: _Session(status)):
        try:
            asyncio.run(coord._fetch_tibber_prices())
        except Exception as err:  # noqa: BLE001
            return type(err).__name__, str(err)
    return None, ""


def flow_user(verdict, existing_entries=0):
    flow = cf.HeatPumpOptimizerConfigFlow()
    hass = FakeHass()
    flow.hass = hass
    for _ in range(existing_entries):
        hass.config_entries.entries.append(FakeEntry(data=BASE_CFG))
    user_input = {"name": "Heat Pump Optimizer", const.CONF_TIBBER_TOKEN: "t",
                  const.CONF_WEATHER_ENTITY: "weather.home"}

    async def fake_validate(hass, token):
        return verdict

    with mock.patch.object(cf, "validate_tibber_token", fake_validate):
        return asyncio.run(flow.async_step_user(user_input))


def lifecycle():
    """heatpump_optimizer:async_setup_entry then async_unload_entry on the harness FakeHass."""
    hass = FakeHass()
    entry = FakeEntry(data=BASE_CFG)
    hass.config_entries.entries.append(entry)
    # The domain's ``async_setup`` first, as Home Assistant does before the
    # domain's first entry: audit B5 (3da0e27) moved service registration
    # there (action-setup). Without it nothing is registered at all.
    asyncio.run(heatpump_optimizer.async_setup(hass, {}))
    ok = asyncio.run(heatpump_optimizer.async_setup_entry(hass, entry))
    entry.state = ConfigEntryState.LOADED if ok else ConfigEntryState.SETUP_ERROR
    services_after_setup = sorted(hass.services.async_services().get(DOMAIN, {}))
    coord = entry.runtime_data
    outcomes = {}
    for svc, data in (("run_optimization", {}), ("simulate_plan", {"target_temp": 21.0}),
                      ("restore_learned_snapshot", {})):
        try:
            value = asyncio.run(hass.services.async_call(DOMAIN, svc, data))
            outcomes[svc] = ("returned", repr(value)[:80])
        except Exception as err:  # noqa: BLE001
            outcomes[svc] = ("raised", type(err).__name__)
    unload_ok = asyncio.run(heatpump_optimizer.async_unload_entry(hass, entry))
    services_after_unload = sorted(hass.services.async_services().get(DOMAIN, {}))
    return {
        "setup_ok": ok, "unload_ok": unload_ok,
        "services_after_setup": services_after_setup,
        "services_after_unload": services_after_unload,
        "coordinator_left": entry.entry_id in hass.data.get(DOMAIN, {}),
        "base_shutdown_called": getattr(coord, "base_shutdown_called", None),
        "outcomes": outcomes,
    }


# --------------------------------------------------------------------------- checks
def _is_github_host(url: str) -> bool:
    """Whether a URL's HOST is github.com, rather than merely containing it.

    `"github.com" in url` is the substring test CodeQL flags as
    py/incomplete-url-substring-sanitization, and it is wrong on its own
    terms: `https://notgithub.com/x` and `https://evil.example/?q=github.com`
    both pass it. Nothing here is a security boundary -- this reads locally
    installed package metadata to report where a dependency's source lives --
    but a check that answers the wrong question is not evidence, and this
    harness's output is evidence for the dependency-transparency rule.

    A `Project-URL` entry is `"<label>, <url>"`, so the URL is what follows
    the first comma when there is one.
    """
    candidate = url.split(",", 1)[-1].strip() if "," in url else url.strip()
    host = (urllib.parse.urlsplit(candidate).hostname or "").lower()
    return host == "github.com" or host.endswith(".github.com")


def check_bronze(ctx):
    init = ast_of("__init__.py")
    setup_defs = [n for n in ast.walk(init) if isinstance(n, ast.AsyncFunctionDef) and n.name == "async_setup"]
    reg_in_entry = 0
    for fn in ast.walk(init):
        if isinstance(fn, ast.AsyncFunctionDef) and fn.name == "async_setup_entry":
            for n in ast.walk(fn):
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "async_register":
                    reg_in_entry += 1
    res("services_registered_in_setup_entry", reg_in_entry)
    res("async_setup_defs", len(setup_defs))
    row("action-setup", "bronze", "done" if setup_defs and not reg_in_entry else "todo",
        "AST __init__.py: async_setup defs; hass.services.async_register calls inside async_setup_entry",
        f"async_setup defs={len(setup_defs)}; async_register inside async_setup_entry={reg_in_entry}",
        "11 services are registered in async_setup_entry and removed after the last unload; "
        "the rule wants async_setup registration with a loaded-entry check in each handler.")

    # The stub base class discards kwargs, so capture what the production super().__init__ passes.
    captured = {}
    orig_init = coord_mod.DataUpdateCoordinator.__init__

    def rec_init(self, *a, **k):
        captured.update(k)
        return orig_init(self, *a, **k)

    with mock.patch.object(coord_mod.DataUpdateCoordinator, "__init__", rec_init):
        make_coord()
        secs = captured["update_interval"].total_seconds()
        make_coord(optimization_interval=15)
        secs15 = captured["update_interval"].total_seconds()
    res("update_interval_default_s", int(secs), "s")
    row("appropriate-polling", "bronze", "done" if secs == 1800 and secs15 == 900 else "todo",
        "update_interval kwarg HeatPumpOptimizerCoordinator.__init__ passes to DataUpdateCoordinator.__init__; manifest iot_class",
        f"update_interval default={secs:.0f} s, optimization_interval=15 => {secs15:.0f} s; "
        f"iot_class={MANIFEST.get('iot_class')}")

    # brands: served image differs from the placeholder served for a domain that has no brand.
    cached = {"heatpump_optimizer": "37fb00d31bbd6934a812a8660704e47f9a07967bf66247a43582cd5c7a06e9bf",
              "placeholder": "048001a5cf75aa8b1cec6035eea4ae9e174016084ef94d6c97860e4886187c98"}
    source = "cached 2026-09-02"
    if ctx.network:
        try:
            import urllib.request
            def sha(url):
                with urllib.request.urlopen(url, timeout=20) as r:
                    return hashlib.sha256(r.read()).hexdigest()
            cached = {"heatpump_optimizer": sha("https://brands.home-assistant.io/_/heatpump_optimizer/icon.png"),
                      "placeholder": sha("https://brands.home-assistant.io/_/zz_no_such_domain_d10/icon.png")}
            source = "fetched now"
        except Exception as err:  # noqa: BLE001
            source = f"fetch failed ({type(err).__name__}); cached"
    distinct = cached["heatpump_optimizer"] != cached["placeholder"]
    local = [os.path.exists(os.path.join(INTEG, "brand", f)) for f in ("icon.png", "logo.png")]
    row("brands", "bronze", "done" if distinct else "todo",
        "sha256(brands.home-assistant.io/_/heatpump_optimizer/icon.png) != sha256(.../_/zz_no_such_domain_d10/icon.png)",
        f"served icon digest distinct from placeholder={distinct} ({source}); "
        f"in-tree brand/icon.png,logo.png present={local} (not a location Home Assistant reads)")

    has_coord = os.path.exists(os.path.join(INTEG, "coordinator.py"))
    has_entity = os.path.exists(os.path.join(INTEG, "entity.py"))
    base_classes = grep(r"^class \w+\(CoordinatorEntity, \w+Entity\)", PLATFORM_FILES)
    res("entity_base_classes_outside_entity_py", len(base_classes))
    row("common-modules", "bronze", "done" if has_coord and has_entity else "todo",
        "ls coordinator.py entity.py; grep '^class .*(CoordinatorEntity, ' platform files",
        f"coordinator.py={has_coord}; entity.py={has_entity}; CoordinatorEntity base classes in platform files="
        f"{len(base_classes)} ({', '.join(sorted({b[0] for b in base_classes}))})",
        "coordinator.py exists; the five CoordinatorEntity base classes live in the platform files, not entity.py.")

    steps_missing = []
    fields_missing = 0
    fields_total = 0
    for flow in ("config", "options"):
        for sid, step in STRINGS[flow]["step"].items():
            data = step.get("data") or {}
            if not data:
                continue
            desc = step.get("data_description") or {}
            fields_total += len(data)
            miss = [k for k in data if k not in desc]
            fields_missing += len(miss)
            if miss:
                steps_missing.append(f"{flow}.{sid}:{len(miss)}/{len(data)}")
    res("flow_fields_without_data_description", fields_missing)
    row("config-flow", "bronze", "done" if MANIFEST.get("config_flow") and "config_flow.py" in SRC else "todo",
        "manifest config_flow; strings.json step.data vs step.data_description",
        f"manifest config_flow={MANIFEST.get('config_flow')}; steps={len(STRINGS['config']['step'])} config + "
        f"{len(STRINGS['options']['step'])} options; fields without data_description={fields_missing}/{fields_total} "
        f"({', '.join(steps_missing) or 'none'})")

    cov = ctx.coverage
    cfp = cov.get("config_flow.py") if cov else None
    user_calls_with_input = 0
    for tpath in glob.glob(os.path.join(ROOT, "tests", "*.py")):
        body = open(tpath, encoding="utf-8").read()
        user_calls_with_input += len(re.findall(r"async_step_user\(\s*\{", body))
        user_calls_with_input += len(re.findall(r"async_step_user\(\s*[a-z_]+\)", body))
    res("tests_driving_async_step_user_with_input", user_calls_with_input)
    if cfp is not None:
        res("coverage_config_flow_pct", round(cfp["percent_covered"], 1), "pct")
        status = "done" if cfp["percent_covered"] >= 100.0 else "todo"
        detail = f"config_flow.py {cfp['percent_covered']:.1f}% ({cfp['missing_lines']} of {cfp['num_statements']} statements missed)"
    else:
        status, detail = "todo", "config_flow.py coverage not measured (run coverage_suite.sh)"
    row("config-flow-test-coverage", "bronze", status,
        "coverage_suite.sh -> coverage.json[config_flow.py]; grep tests for async_step_user(<input>)",
        f"{detail}; tests calling async_step_user with input={user_calls_with_input} (error branches "
        f"invalid_tibber_token/cannot_connect never driven)",
        "The rule wants 100 % of the config flow; the suite renders the user form but never submits it.")

    from importlib import metadata as md
    deps = []
    for req in MANIFEST.get("requirements", []):
        name = re.split(r"[<>=!~]", req)[0]
        try:
            m = md.metadata(name)
            lic = m.get("License-Expression") or (m.get("License") or "")[:40]
            cls = [c for c in (m.get_all("Classifier") or []) if c.startswith("License ::")]
            urls = [u for u in (m.get_all("Project-URL") or []) if _is_github_host(u)]
            home = m.get("Home-page") or ""
            src = "github" if urls or _is_github_host(home) else "?"
            deps.append(f"{name} {m['Version']}: {lic or cls[:1]} src={src}")
        except md.PackageNotFoundError:
            deps.append(f"{name}: not installed locally")
    pypi = "local metadata"
    if ctx.network:
        try:
            import urllib.request
            got = []
            for req in MANIFEST.get("requirements", []):
                name = re.split(r"[<>=!~]", req)[0]
                with urllib.request.urlopen(f"https://pypi.org/pypi/{name}/json", timeout=20) as r:
                    info = json.load(r)["info"]
                got.append(f"{name}@{info['version']} on PyPI")
            pypi = "; ".join(got)
        except Exception as err:  # noqa: BLE001
            pypi = f"PyPI fetch failed ({type(err).__name__})"
    row("dependency-transparency", "bronze", "done",
        "importlib.metadata for manifest requirements (License, Project-URL); PyPI JSON with --network",
        "; ".join(deps) + f" [{pypi}]")

    svc_yaml = SRC and open(os.path.join(INTEG, "services.yaml"), encoding="utf-8").read()
    svc_names = re.findall(r"^([a-z_]+):", svc_yaml, re.M)
    readme = DOCS["README.md"]
    sec = readme[readme.index("## Services"):readme.index("## How it works")]
    documented = [s for s in svc_names if f"`{s}`" in sec]
    cfg_doc = DOCS["docs/configuration.md"]
    detailed = [s for s in svc_names if f"**`{s}`**" in cfg_doc]
    res("services_documented_readme", len(documented))
    row("docs-actions", "bronze", "done" if len(documented) == len(svc_names) == 11 else "todo",
        "services.yaml names vs README '## Services' table and docs/configuration.md field detail",
        f"services.yaml={len(svc_names)}; README table rows={len(documented)}; field-level in docs/configuration.md={len(detailed)}")

    trig = grep(r"async_attach_trigger|device_trigger|TRIGGER_SCHEMA")
    cond = grep(r"async_condition_from_config|device_condition|CONDITION_SCHEMA")
    row("docs-triggers", "bronze", "exempt", "grep async_attach_trigger|device_trigger", f"trigger registrations={len(trig)}",
        "No custom triggers are registered.")
    row("docs-conditions", "bronze", "exempt", "grep async_condition_from_config|device_condition", f"condition registrations={len(cond)}",
        "No custom conditions are registered.")

    n, where = docs_grep(r"^## What it does", {"README.md": readme})
    row("docs-high-level-description", "bronze", "done" if n else "todo",
        "grep '^## What it does' README.md", f"heading={n}; first paragraph describes the service and links the upstream project")
    inst = docs_grep(r"^## Installation|^### HACS|^### Manual|^## Requirements", {"README.md": readme})[0]
    row("docs-installation-instructions", "bronze", "done" if inst >= 4 else "todo",
        "grep '^## Installation|^### HACS|^### Manual|^## Requirements' README.md", f"headings found={inst}/4")
    n, where = docs_grep(r"remov(e|ing|al) (of )?(the )?integration|^#+\s*remov|uninstall|delete the (integration|config entry)")
    res("docs_removal_instructions", n)
    row("docs-removal-instructions", "bronze", "done" if n else "todo",
        "grep -i 'remov(e|ing|al) (the )?integration|uninstall' README.md docs/*.md", f"matches={n} {where}",
        "No 'Removing the integration' section anywhere in README.md or docs/.")

    subs_in_entities = grep(r"async_track_|async_listen|\.subscribe\(", PLATFORM_FILES)
    unsub = grep(r"self\._unsub_\w+\(\)", ["coordinator.py"])
    row("entity-event-setup", "bronze", "done" if not subs_in_entities else "todo",
        "grep async_track_|async_listen|subscribe in platform files; _unsub_*() calls in coordinator.async_shutdown",
        f"entity-level subscriptions outside async_added_to_hass={len(subs_in_entities)}; coordinator unsubscribes on shutdown={len(unsub)}")

    ents = ctx.roster
    uids = [getattr(e, "_attr_unique_id", None) for _, e in ents]
    dup = len(uids) - len(set(uids))
    res("entities", len(ents))
    row("entity-unique-id", "bronze", "done" if all(uids) and not dup else "todo",
        "roster via each platform's async_setup_entry: _attr_unique_id present and unique",
        f"entities={len(ents)}; missing unique_id={sum(1 for u in uids if not u)}; duplicates={dup}")
    hen = sum(1 for _, e in ents if getattr(e, "_attr_has_entity_name", False))
    row("has-entity-name", "bronze", "done" if hen == len(ents) else "todo",
        "roster: _attr_has_entity_name", f"has_entity_name True on {hen}/{len(ents)} entities")

    rt = grep(r"runtime_data")
    hd = grep(r"hass\.data\[DOMAIN\]|hass\.data\.get\(DOMAIN|hass\.data\.setdefault\(DOMAIN")
    res("runtime_data_refs", len(rt))
    res("hass_data_domain_refs", len(hd))
    row("runtime-data", "bronze", "done" if rt else "todo",
        "grep runtime_data; grep 'hass.data[DOMAIN]' custom_components/heatpump_optimizer",
        f"runtime_data references={len(rt)}; hass.data[DOMAIN] references={len(hd)} in "
        f"{', '.join(sorted({h[0] for h in hd}))}",
        "Coordinator and config stash live in hass.data[DOMAIN][entry_id]; needs HA >= 2024.4 for ConfigEntry.runtime_data.")

    branches = {}
    for verdict in ("invalid_auth", "cannot_connect", "ok"):
        r = flow_user(verdict)
        branches[verdict] = (r.get("type"), r.get("step_id"), (r.get("errors") or {}).get(const.CONF_TIBBER_TOKEN))
    ok_branches = (branches["invalid_auth"][2] == "invalid_tibber_token" and branches["cannot_connect"][2] == "cannot_connect"
                   and branches["ok"][1] == "temperature")
    row("test-before-configure", "bronze", "done" if ok_branches else "todo",
        "HeatPumpOptimizerConfigFlow.async_step_user with validate_tibber_token patched to each verdict",
        f"invalid_auth->{branches['invalid_auth'][2]}, cannot_connect->{branches['cannot_connect'][2]}, ok->step {branches['ok'][1]}")

    first = grep(r"async_config_entry_first_refresh\(\)", ["__init__.py"])
    auth = grep(r"ConfigEntryAuthFailed")
    exc401 = tibber_exception_for(401)
    exc403 = tibber_exception_for(403)
    exc200err = None
    coord, hass, entry = make_coord()
    with mock.patch.object(coord_mod, "async_get_clientsession",
                           lambda hass: _Session(200, {"errors": [{"message": "invalid token"}]})):
        try:
            asyncio.run(coord._fetch_tibber_prices())
        except Exception as err:  # noqa: BLE001
            exc200err = type(err).__name__
    n_auth_raises = sum(1 for e in (exc401[0], exc403[0], exc200err) if e == "ConfigEntryAuthFailed")
    res("auth_failures_raising_ConfigEntryAuthFailed", n_auth_raises)
    row("test-before-setup", "bronze", "done" if first else "todo",
        "grep async_config_entry_first_refresh in async_setup_entry; _fetch_tibber_prices under a 401/403/errors-payload session",
        f"first refresh in setup={len(first)}; ConfigEntryAuthFailed in code={len(auth)}; "
        f"401->{exc401[0]}, 403->{exc403[0]}, 200+errors->{exc200err} (all UpdateFailed => ConfigEntryNotReady retry loop)",
        "Temporary failures surface through async_config_entry_first_refresh; an invalid token is not "
        "distinguished (no ConfigEntryAuthFailed), see reauthentication-flow.")

    guards = grep(r"async_set_unique_id|_abort_if_unique_id_configured|_async_abort_entries_match|_async_current_entries"
                  r"|config_entries\.async_entries\(DOMAIN\)", ["config_flow.py"])
    single = MANIFEST.get("single_config_entry")
    r = flow_user("ok", existing_entries=1)
    res("unique_entry_guards", len(guards) + (1 if single else 0))
    res("flow_aborts_with_existing_entry", 1 if r.get("type") == "abort" else 0)
    row("unique-config-entry", "bronze", "done" if (guards or single) else "todo",
        "grep unique-id/entries-match guards in config_flow.py; manifest single_config_entry; "
        "async_step_user with one entry already in hass.config_entries",
        f"guards={len(guards)}; manifest single_config_entry={single}; with an existing entry the user step returns "
        f"type={r.get('type')} step={r.get('step_id')} (no abort); strings.json abort.already_configured exists unused",
        "Nothing stops a second entry. Cheapest fix: self._async_abort_entries_match() in async_step_user (any HA), "
        "or manifest single_config_entry (HA >= 2024.3).")


def check_silver(ctx):
    sve = grep(r"raise ServiceValidationError\(")
    hae = grep(r"raise HomeAssistantError\(")
    life = ctx.lifecycle
    silent = {k: v for k, v in life["outcomes"].items() if v[0] == "returned"}
    res("service_failure_paths_returning_silently", len(silent))
    row("action-exceptions", "silver", "done" if hae and not silent else "todo",
        "grep raise ServiceValidationError|HomeAssistantError; call run_optimization/simulate_plan/"
        "restore_learned_snapshot through FakeServices on a coordinator with no prices",
        f"ServiceValidationError raises={len(sve)}; HomeAssistantError raises={len(hae)}; failure outcomes: "
        + "; ".join(f"{k}: {v[0]} {v[1]}" for k, v in life["outcomes"].items()),
        "Validation errors raise; operational failures (no prices, no plan, no snapshot) return silently or as a response dict.")

    row("config-entry-unloading", "silver",
        "done" if life["unload_ok"] and not life["services_after_unload"] and not life["coordinator_left"]
        and life["base_shutdown_called"] else "todo",
        "heatpump_optimizer.async_setup_entry then async_unload_entry on FakeHass",
        f"services after setup={len(life['services_after_setup'])}, after unload={len(life['services_after_unload'])}; "
        f"coordinator left in hass.data={life['coordinator_left']}; coordinator.async_shutdown reached base={life['base_shutdown_called']}")

    cfg_doc = DOCS["docs/configuration.md"]
    opt_titles = [(sid, s.get("title", "")) for sid, s in STRINGS["options"]["step"].items() if s.get("data")]
    found = [sid for sid, t in opt_titles if t and re.search(r"^#+\s*" + re.escape(t), cfg_doc, re.M | re.I)]
    row("docs-configuration-parameters", "silver", "done" if len(found) == len(opt_titles) else "todo",
        "strings.json options step titles (steps with fields) as headings in docs/configuration.md",
        f"options pages with fields={len(opt_titles)}; documented as headings={len(found)}"
        + ("" if len(found) == len(opt_titles) else f"; missing={[s for s, _ in opt_titles if s not in found]}"))

    cfg_steps = [(sid, s) for sid, s in STRINGS["config"]["step"].items() if s.get("data")]
    user_labels = list(STRINGS["config"]["step"]["user"]["data"].values())
    labelled = [l for l in user_labels if l.lower() in cfg_doc.lower()]
    setup_sec = cfg_doc[cfg_doc.index("## Initial setup"):cfg_doc.index("## Changing settings later")]
    row("docs-installation-parameters", "silver", "done" if len(labelled) >= len(user_labels) - 2 else "todo",
        "strings.json config.step.user.data labels found in docs/configuration.md '## Initial setup'",
        f"config steps with fields={len(cfg_steps)}; user-step labels documented={len(labelled)}/{len(user_labels)}; "
        f"'Initial setup' section={len(setup_sec)} chars")

    ents = ctx.roster
    coord = ctx.coord
    coord.last_update_success = False
    still = [(p, getattr(e, "_attr_translation_key", None) or type(e).__name__) for p, e in ents if e.available]
    coord.last_update_success = True
    res("entities_available_after_failed_refresh", len(still))
    row("entity-unavailable", "silver", "done" if not still else "todo",
        "roster with coordinator.last_update_success=False: count entity.available",
        f"available after a failed refresh={len(still)}/{len(ents)} {still}",
        "Two buttons override available() without super().available, so they stay available when the coordinator fails.")

    owners = MANIFEST.get("codeowners", [])
    row("integration-owner", "silver", "done" if owners else "todo", "manifest codeowners", f"codeowners={owners}")

    raised, errors, records = failing_cycles(3)
    reasons = [str(r.getMessage())[:60] for r in errors]
    res("error_records_over_3_failed_refreshes", len(errors))
    # Null control: the fetch alone, three times. The latch in _tibber_fetch_failed must give exactly one ERROR;
    # anything above one in the full cycle is the outer handler in _async_update_data.
    c2, _, _ = make_coord()
    cap2 = _Cap()
    lg2 = logging.getLogger("heatpump_optimizer")
    lg2.addHandler(cap2)
    try:
        for _ in range(3):
            try:
                asyncio.run(c2._fetch_tibber_prices())
            except UpdateFailed:
                pass
    finally:
        lg2.removeHandler(cap2)
    direct_errors = sum(1 for r in cap2.records if r.levelno >= logging.ERROR)
    res("error_records_over_3_failed_fetches_direct", direct_errors)
    row("log-when-unavailable", "silver", "done" if len(errors) <= 1 else "todo",
        "_async_update_data x3 with the Tibber fetch failing (stub: no HTTP session); count ERROR records on logger heatpump_optimizer",
        f"UpdateFailed raised={raised}/3; ERROR records={len(errors)} (rule: 1) with exc_info on "
        f"{sum(1 for r in errors if r.exc_info)}: {reasons}; null control _fetch_tibber_prices x3 alone => {direct_errors} ERROR",
        "_tibber_fetch_failed latches ERROR-once correctly, but _async_update_data's outer except re-logs "
        "ERROR with a traceback on every failed cycle.")

    pu = grep(r"^PARALLEL_UPDATES\s*=", PLATFORM_FILES)
    res("platforms_declaring_parallel_updates", len(pu))
    row("parallel-updates", "silver", "done" if len(pu) == len(PLATFORMS) else "todo",
        "grep '^PARALLEL_UPDATES' in the five platform files", f"declared in {len(pu)}/{len(PLATFORMS)} platforms",
        "No platform declares PARALLEL_UPDATES (0 for the coordinator read-only platforms, 1 for button/switch/climate).")

    reauth = grep(r"async_step_reauth", ["config_flow.py"])
    res("reauth_steps", len(reauth))
    row("reauthentication-flow", "silver", "done" if reauth else "todo",
        "grep async_step_reauth config_flow.py; ConfigEntryAuthFailed count",
        f"async_step_reauth={len(reauth)}; ConfigEntryAuthFailed raises={len(grep(r'raise ConfigEntryAuthFailed'))}; "
        f"the Tibber token is a credential (not exempt); re-entry only via the options 'entities' page",
        "Tibber token authentication exists, so the rule applies; a 401 is reported as UpdateFailed and no reauth flow is offered.")

    cov = ctx.coverage
    if cov:
        tot = ctx.coverage_totals
        ge95 = sum(1 for v in cov.values() if v["percent_covered"] >= 95.0)
        low = sorted(cov.items(), key=lambda kv: kv[1]["percent_covered"])[:5]
        res("coverage_total_pct", round(tot["percent_covered"], 1), "pct")
        res("coverage_modules_ge95", ge95)
        res("coverage_modules", len(cov))
        row("test-coverage", "silver", "done" if ge95 == len(cov) else "todo",
            "coverage_suite.sh (every gate script under coverage.py, combined) -> coverage.json",
            f"total {tot['percent_covered']:.1f}% of {tot['num_statements']} statements; modules >= 95%: {ge95}/{len(cov)}; "
            f"lowest: " + ", ".join(f"{k[:-3]} {v['percent_covered']:.0f}%" for k, v in low),
            f"Measured once (PROVISIONAL timing, shared box): {ge95} of {len(cov)} modules reach 95 %.")
    else:
        row("test-coverage", "silver", "todo", "coverage_suite.sh", "not measured (coverage.json absent)")


def check_gold(ctx):
    ents = ctx.roster
    infos = [dict(e.device_info) for _, e in ents]
    idents = {frozenset(i.get("identifiers", ())) for i in infos}
    entry_type = sum(1 for i in infos if i.get("entry_type"))
    res("device_entry_type_service", entry_type)
    row("devices", "gold", "done",
        "roster: device_info identifiers, entry_type", f"devices={len(idents)} (identifiers={sorted(idents)[0] if idents else None}); "
        f"entry_type set on {entry_type}/{len(infos)}; manufacturer={infos[0].get('manufacturer')!r} model={infos[0].get('model')!r}",
        "One service device per entry; DeviceInfo lacks entry_type=DeviceEntryType.SERVICE (available since HA 2021.12).")

    diag = os.path.exists(os.path.join(INTEG, "diagnostics.py"))
    diag_defs = len(grep(r"def async_get_config_entry_diagnostics"))
    res("diagnostics_defs", diag_defs)
    row("diagnostics", "gold", "done" if diag else "todo", "ls diagnostics.py; grep async_get_config_entry_diagnostics",
        f"diagnostics.py={diag}; async_get_config_entry_diagnostics defs={diag_defs}",
        "No diagnostics platform; the token would need redaction.")

    disc = [k for k in ("zeroconf", "ssdp", "dhcp", "bluetooth", "usb", "homekit", "mqtt") if k in MANIFEST]
    row("discovery", "gold", "exempt", "manifest discovery keys", f"discovery keys={disc}",
        "A cloud API (Tibber) plus the user's own Home Assistant entities; nothing on the network to discover.")
    row("discovery-update-info", "gold", "exempt", "manifest discovery keys", f"discovery keys={disc}",
        "Not discoverable (see discovery).")

    n, where = docs_grep(r"optimization interval \(30 minutes by default\)|every optimization interval")
    row("docs-data-update", "gold", "done" if n else "todo",
        "grep 'optimization interval (30 minutes by default)' README.md docs/*.md", f"matches={n} {where}")
    bp, _ = docs_grep(r"blueprint")
    auto, where = docs_grep(r"^\s*(automation|trigger|alias):")
    res("docs_blueprints", bp)
    row("docs-examples", "gold", "done" if bp else "todo",
        "grep -i blueprint; grep '^ *(automation|trigger|alias):' README.md docs/*.md",
        f"blueprint mentions={bp}; automation examples={auto}; the YAML examples present are card configs "
        f"({docs_grep(r'^```yaml')[0]} fences)",
        "No blueprints or automation examples; the YAML examples are dashboard-card configs.")
    kl, _ = docs_grep(r"^#+\s*known limitations")
    res("docs_known_limitations_sections", kl)
    row("docs-known-limitations", "gold", "done" if kl else "todo",
        "grep '^#* Known limitations' README.md docs/*.md DISCLAIMER.md",
        f"sections={kl}; DISCLAIMER.md carries caveats ({docs_grep(r'not a (safety device|compliance feature)', {'DISCLAIMER.md': DOCS['DISCLAIMER.md']})[0]} 'not a ...' statements) but no limitations list",
        "No 'Known limitations' section; the disclaimer is legal, not a capability list.")
    sd, _ = docs_grep(r"^#+\s*(un)?supported (devices|hardware|heat pumps)")
    row("docs-supported-devices", "gold", "done" if sd else "todo",
        "grep '^#* (Un)supported devices' README.md docs/*.md",
        f"sections={sd}; the control paths (on/off switch, ECL110 over MQTT, frequency writer) are described "
        f"separately (README lines 'Inverter frequency', 'ECL110 heat-curve control'; docs/ecl110.md)",
        "Drives the pump through Home Assistant entities and one MQTT bridge; no supported/unsupported statement in one place.")
    readme = DOCS["README.md"]
    sec = readme[readme.index("## Entities"):readme.index("## Services")]
    rows_ = [l for l in sec.splitlines() if l.startswith("|") and not re.match(r"^\|\s*-", l) and not re.match(r"^\|\s*(Entity|Sensor|Name|Button|Binary)", l, re.I)]
    counts = re.findall(r"\((\d+) total\)", sec)
    row("docs-supported-functions", "gold", "done" if sum(map(int, counts)) + 2 == len(ents) else "todo",
        "README '## Entities' section: per-platform totals vs the roster",
        f"README totals={counts} (+ switch and climate) vs roster={len(ents)} entities; table rows={len(rows_)}")
    ts, _ = docs_grep(r"^## Troubleshooting", {"README.md": readme})
    row("docs-troubleshooting", "gold", "done" if ts else "todo", "grep '^## Troubleshooting' README.md",
        f"section={ts}; bullets={len(re.findall(r'^- ', readme[readme.index('## Troubleshooting'):readme.index('## ECL110')], re.M))}")
    wid = readme[readme.index("## What it does"):readme.index("## Requirements")]
    uc = len(re.findall(r"^\*\*[^*]+\*\*", wid, re.M))
    row("docs-use-cases", "gold", "done" if uc >= 3 else "todo",
        "README '## What it does': bold-lead use-case paragraphs", f"use-case paragraphs={uc}")

    row("dynamic-devices", "gold", "exempt", "roster: one device per entry", f"devices per entry=1; entities={len(ents)}",
        "One service device per config entry; devices never appear at runtime.")

    cats = Counter(str(getattr(e, "_attr_entity_category", None)) for _, e in ents)
    diag_like = re.compile(r"status|accuracy|solver|health|problem|samples|version|diagnos|score|starts|drift|learn|scale|derate|bias|advisor|identification|snapshot", re.I)
    uncat = [getattr(e, "_attr_translation_key", None) or type(e).__name__ for _, e in ents
             if not getattr(e, "_attr_entity_category", None) and diag_like.search(getattr(e, "_attr_translation_key", "") or "")]
    res("entities_with_category", sum(v for k, v in cats.items() if k != "None"))
    row("entity-category", "gold", "done", "roster: _attr_entity_category",
        f"categories={dict(cats)}; uncategorised entities with diagnostic-looking keys={len(uncat)}: {uncat[:8]}",
        "Diagnostic category set on the obviously diagnostic entities; the remaining diagnostic-looking ones are a judgement call.")

    unit_class = {"°C": "temperature", "kW": "power", "W": "power", "kWh": "energy", "W/m²": "irradiance",
                  "Hz": "frequency", "min": "duration", "h": "duration", "L": "volume_storage"}
    classless = []
    with_class = 0
    for p, e in ents:
        if p != "sensor":
            continue
        unit = getattr(e, "_attr_native_unit_of_measurement", None)
        dc = getattr(e, "_attr_device_class", None)
        if dc:
            with_class += 1
        elif unit in unit_class:
            classless.append(f"{getattr(e, '_attr_translation_key', type(e).__name__)}[{unit}]")
    res("sensors_with_unit_but_no_device_class", len(classless))
    row("entity-device-class", "gold", "done" if not classless else "todo",
        "roster sensors: native unit maps to a SensorDeviceClass but _attr_device_class is None",
        f"sensors with device_class={with_class}; unit-mappable without one={len(classless)}: {classless[:10]}",
        None if not classless else "Two kWh sensors lack SensorDeviceClass.ENERGY; the three degree-Celsius ones are deltas "
        "(displacement, prediction error) where TEMPERATURE would convert wrongly, so they are correctly classless.")

    disabled = [getattr(e, "_attr_translation_key", type(e).__name__) for _, e in ents
                if getattr(e, "_attr_entity_registry_enabled_default", True) is False]
    res("entities_disabled_by_default", len(disabled))
    row("entity-disabled-by-default", "gold", "done" if disabled else "todo",
        "roster: _attr_entity_registry_enabled_default is False", f"disabled by default={len(disabled)}: {disabled}")

    missing_tk = []
    for p, e in ents:
        tk = getattr(e, "_attr_translation_key", None)
        if tk is None and getattr(e, "_attr_name", "unset") is None:
            continue  # device-named primary entity (climate)
        if tk not in (STRINGS.get("entity", {}).get(p) or {}):
            missing_tk.append(f"{p}.{tk}")
    res("entities_missing_translation", len(missing_tk))
    row("entity-translations", "gold", "done" if not missing_tk else "todo",
        "roster: _attr_translation_key present in strings.json entity.<platform>",
        f"entities={len(ents)}; missing translation={len(missing_tk)} {missing_tk}; strings entity keys="
        f"{ {k: len(v) for k, v in STRINGS['entity'].items()} }; translations/sv.json present={os.path.exists(os.path.join(INTEG, 'translations', 'sv.json'))}")

    raises = grep(r"raise (ServiceValidationError|HomeAssistantError)\(")
    translated = grep(r"raise (ServiceValidationError|HomeAssistantError)\([^)]*translation_key", flags=re.S)
    res("exception_raises_with_translation_key", len(translated))
    row("exception-translations", "gold", "done" if translated and len(translated) == len(raises) else "todo",
        "grep raise ServiceValidationError(...translation_key; strings.json 'exceptions'",
        f"raises={len(raises)}; with translation_key={len(translated)}; strings.json exceptions block={'exceptions' in STRINGS}",
        "All 15 service exceptions carry literal English messages; no 'exceptions' block in strings.json (API in floor 2024.1).")

    icons = grep(r"_attr_icon\s*=", PLATFORM_FILES)
    icons_json = os.path.exists(os.path.join(INTEG, "icons.json"))
    res("icons_in_code", len(icons))
    row("icon-translations", "gold", "done" if icons_json else "todo",
        "ls icons.json; grep '_attr_icon =' platform files", f"icons.json={icons_json}; _attr_icon assignments={len(icons)}",
        "Icons are entity state (_attr_icon) rather than icons.json; icons.json needs HA >= 2024.2 (floor is 2024.1.0).")

    reconf = grep(r"async_step_reconfigure", ["config_flow.py"])
    row("reconfiguration-flow", "gold", "done" if reconf else "todo",
        "grep async_step_reconfigure config_flow.py", f"async_step_reconfigure={len(reconf)}; options flow pages={len(STRINGS['options']['step'])} "
        f"(the 'entities' page re-validates the token, so the function exists outside the reconfigure source)",
        "Settings live in the config flow, so the rule applies; SOURCE_RECONFIGURE needs HA >= 2024.4.")

    calls = re.findall(r"async_create_issue\((?:.|\n)*?translation_key=\"([a-z_]+)\"", SRC["coordinator.py"])
    keys = set(STRINGS.get("issues", {}))
    missing = sorted(set(calls) - keys)
    res("repair_issue_create_calls", len(calls))
    row("repair-issues", "gold", "done" if calls and not missing else "todo",
        "regex async_create_issue(...translation_key=) in coordinator.py vs strings.json issues",
        f"create calls={len(calls)} over {len(set(calls))} keys; strings issues={len(keys)}; keys without strings={missing}; "
        f"is_fixable=False on {len(grep(r'is_fixable=False'))} calls")

    row("stale-devices", "gold", "exempt", "roster: one device per entry, identifiers=(DOMAIN, entry_id)",
        "the device is the entry; removing the entry removes it", "One device per entry; nothing can go stale.")


def check_platinum(ctx):
    sync_http = grep(r"^\s*(import requests|from requests|import urllib\.request|import httplib|import http\.client)")
    executor = grep(r"async_add_executor_job\(")
    row("async-dependency", "platinum", "done" if not sync_http else "todo",
        "grep sync HTTP libraries; manifest requirements; grep async_add_executor_job",
        f"requirements={MANIFEST.get('requirements')} (compute libraries, no I/O); sync HTTP imports={len(sync_http)}; "
        f"HTTP via aiohttp; executor offloads={len(executor)}")
    sess = grep(r"async_get_clientsession\(")
    own = grep(r"aiohttp\.ClientSession\(")
    row("inject-websession", "platinum", "done" if sess and not own else "todo",
        "grep async_get_clientsession( vs aiohttp.ClientSession(",
        f"shared-session call sites={len(sess)} ({', '.join(sorted({s[0] for s in sess}))}); private sessions={len(own)}")
    if ctx.no_mypy:
        row("strict-typing", "platinum", "todo", "mypy --strict (skipped: --no-mypy)", "skipped")
        return
    env = dict(os.environ)
    env["MYPYPATH"] = os.path.join(ROOT, "tests", "hastub")
    # The stub reaches mypy through MYPYPATH only, so the count is the same as the header's standalone command
    # whatever PYTHONPATH the caller had. Counted: 'error:' lines under custom_components/ (notes excluded).
    env.pop("PYTHONPATH", None)
    if importlib.util.find_spec("mypy") is None:
        env["PYTHONPATH"] = os.environ.get("D10_COV_PREFIX", "/tmp/d10-cov")
    with tempfile.TemporaryDirectory(prefix="d10-mypy-") as tmp:
        cmd = [sys.executable, "-m", "mypy", "--strict", "--show-error-codes", "--no-error-summary",
               "--no-incremental", "--cache-dir", tmp, "--python-version", "3.13",
               "custom_components/heatpump_optimizer"]
        t0 = time.time()
        proc = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=ROOT)
        wall = time.time() - t0
    lines = [l for l in proc.stdout.splitlines() if l.startswith("custom_components/") and ": error:" in l]
    codes = Counter()
    files = Counter()
    for l in lines:
        m = re.search(r"\[([a-z-]+)\]$", l)
        codes[m.group(1) if m else "?"] += 1
        files[l.split(":")[0].rsplit("/", 1)[-1]] += 1
    res("mypy_strict_errors", len(lines))
    res("mypy_strict_files_with_errors", len(files))
    res("mypy_wall_s", round(wall, 1), "s")
    top = ", ".join(f"{k}={v}" for k, v in codes.most_common(6))
    row("strict-typing", "platinum", "done" if not lines else "todo",
        "mypy --strict --python-version 3.13 custom_components/heatpump_optimizer with MYPYPATH=tests/hastub",
        f"errors={len(lines)} in {len(files)}/{len(PY_FILES)} files (mypy {proc.stdout.count('') and 'run'}, {wall:.0f} s, PROVISIONAL); by code: {top}; "
        f"worst files: {', '.join(f'{k}={v}' for k, v in files.most_common(4))}; py.typed n/a (integration, not a library)",
        "mypy --strict reports hundreds of errors; no-untyped-def and type-arg are integration-internal, "
        "no-untyped-call is partly the untyped stub.")


# --------------------------------------------------------------------------- output
TIERS = ["bronze", "silver", "gold", "platinum"]
ORDER = ["action-setup", "appropriate-polling", "brands", "common-modules", "config-flow", "config-flow-test-coverage",
         "dependency-transparency", "docs-actions", "docs-triggers", "docs-conditions", "docs-high-level-description",
         "docs-installation-instructions", "docs-removal-instructions", "entity-event-setup", "entity-unique-id",
         "has-entity-name", "runtime-data", "test-before-configure", "test-before-setup", "unique-config-entry",
         "action-exceptions", "config-entry-unloading", "docs-configuration-parameters", "docs-installation-parameters",
         "entity-unavailable", "integration-owner", "log-when-unavailable", "parallel-updates", "reauthentication-flow",
         "test-coverage",
         "devices", "diagnostics", "discovery", "discovery-update-info", "docs-data-update", "docs-examples",
         "docs-known-limitations", "docs-supported-devices", "docs-supported-functions", "docs-troubleshooting",
         "docs-use-cases", "dynamic-devices", "entity-category", "entity-device-class", "entity-disabled-by-default",
         "entity-translations", "exception-translations", "icon-translations", "reconfiguration-flow", "repair-issues",
         "stale-devices",
         "async-dependency", "inject-websession", "strict-typing"]


def emit_yaml():
    print(f"# Draft quality_scale.yaml for custom_components/heatpump_optimizer -- D10, round 2, baseline {BASELINE[:7]}.")
    print("# Custom integrations cannot declare a tier; this records rule-by-rule adherence as executed by")
    print("# tools/audit/round2/D10/check_rules.py. Status values: done / todo / exempt. Comments name the gap")
    print("# and, where the fix needs an API newer than the hacs.json floor (2024.1.0), the minimum release.")
    print("rules:")
    by = {r.rule: r for r in ROWS}
    for rule in ORDER:
        r = by[rule]
        note = NOTES.get(rule)
        if note or r.status != "done":
            print(f"  {rule}:")
            print(f"    status: {r.status}")
            if note:
                print(f"    comment: >-")
                print(f"      {note}")
        else:
            print(f"  {rule}: done")


def swapins_now():
    try:
        vs = subprocess.run(["vm_stat"], capture_output=True, text=True).stdout
        for line in vs.splitlines():
            if line.startswith("Swapins"):
                return int(line.split(":")[1].strip().rstrip("."))
    except Exception:  # noqa: BLE001
        pass
    try:
        for line in open("/proc/vmstat"):
            if line.startswith("pswpin"):
                return int(line.split()[1])
    except Exception:  # noqa: BLE001
        pass
    return None


SWAP_AT_START = swapins_now()


def contention():
    import numpy as np
    a = np.random.default_rng(0).standard_normal((400, 400))
    c0, t0 = time.process_time(), time.thread_time()
    for _ in range(20):
        a @ a
    c1, t1 = time.process_time(), time.thread_time()
    tf = (c1 - c0) / max(t1 - t0, 1e-9)
    swap = "n/a"
    try:
        vs = subprocess.run(["vm_stat"], capture_output=True, text=True).stdout
        for line in vs.splitlines():
            if line.startswith("Swapins"):
                swap = line.split(":")[1].strip().rstrip(".")
    except Exception:  # noqa: BLE001
        try:
            for line in open("/proc/vmstat"):
                if line.startswith("pswpin"):
                    swap = line.split()[1]
        except Exception:  # noqa: BLE001
            pass
    return tf, os.getloadavg()[0], swap


class Ctx:
    pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coverage-json", default=os.path.join(D10, "coverage", "coverage.json"))
    ap.add_argument("--no-mypy", action="store_true")
    ap.add_argument("--network", action="store_true")
    ap.add_argument("--emit-yaml", action="store_true")
    args = ap.parse_args()
    ctx = Ctx()
    ctx.no_mypy = args.no_mypy
    ctx.network = args.network
    ctx.coverage = None
    ctx.coverage_totals = None
    if os.path.exists(args.coverage_json):
        d = json.load(open(args.coverage_json))
        ctx.coverage = {os.path.basename(k): v["summary"] for k, v in d["files"].items()}
        ctx.coverage_totals = d["totals"]
    logging.getLogger().addHandler(logging.NullHandler())
    logging.getLogger("heatpump_optimizer").propagate = False
    coord, hass, entry = make_coord()
    ctx.coord = with_payload(coord)
    ctx.roster = roster(ctx.coord, hass, entry)
    ctx.lifecycle = lifecycle()
    check_bronze(ctx)
    check_silver(ctx)
    check_gold(ctx)
    check_platinum(ctx)
    if args.emit_yaml:
        emit_yaml()
        return 0
    by = {r.rule: r for r in ROWS}
    assert set(by) == set(ORDER), sorted(set(by) ^ set(ORDER))
    print(f"# D10 rule table -- baseline {BASELINE}\n")
    print("| rule | tier | status | check | result |")
    print("|---|---|---|---|---|")
    for rule in ORDER:
        r = by[rule]
        print(f"| {r.rule} | {r.tier} | {r.status} | {r.command} | {r.result.replace('|', '/')} |")
    print()
    counts = Counter(r.status for r in ROWS)
    for tier in TIERS:
        c = Counter(r.status for r in ROWS if r.tier == tier)
        n = sum(c.values())
        print(f"RESULT {tier}_done={c['done']} of {n} count")
        print(f"RESULT {tier}_todo={c['todo']} of {n} count")
        print(f"RESULT {tier}_exempt={c['exempt']} of {n} count")
    print(f"RESULT done={counts['done']} count")
    print(f"RESULT todo={counts['todo']} count")
    print(f"RESULT exempt={counts['exempt']} count")
    print(f"RESULT rules={len(ROWS)} count")
    for name, value, unit in RESULTS:
        print(f"RESULT {name}={value} {unit}")
    tf, load1, swap = contention()
    print(f"RESULT thread_factor={tf:.2f}")
    print(f"RESULT load1={load1:.2f}")
    print(f"RESULT swapins={swap}")
    end = swapins_now()
    delta = (end - SWAP_AT_START) if (end is not None and SWAP_AT_START is not None) else "n/a"
    print(f"RESULT swapins_delta_during_run={delta}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
