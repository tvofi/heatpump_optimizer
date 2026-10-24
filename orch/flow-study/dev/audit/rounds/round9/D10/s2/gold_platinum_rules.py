#!/usr/bin/env python3
"""D10.M1/M2: one executed check per Gold and Platinum quality-scale rule.

Metric: per rule, one count printed as `RESULT <rule>.<check>=<n> count`,
where the count is the number of violating sites/entities (0 = holds) unless
the check name says otherwise. Entities are the ones the real
async_setup_entry of every platform in const.PLATFORMS adds for a coordinator
built by tests/golden.py:_capture_coordinator(coord_all_features).

Command (from the export root):
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D10/s2/gold_platinum_rules.py
Expected at baseline: see REPORT.md tier table (all counts exact).
Perturbation examples (all in memory): --perturb diag drops CONF_TIBBER_TOKEN
from diagnostics.TO_REDACT -> diagnostics.leaks goes up by 1;
--perturb icon removes the optimization_status sensor key from icons.json -> icon_translations.
entities_without_icon goes up by 1.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: 4-CPU Linux cloud container.
Instrumented symbols: heatpump_optimizer.<platform>:async_setup_entry,
heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator.device_info,
heatpump_optimizer.diagnostics:async_get_config_entry_diagnostics,
heatpump_optimizer.config_flow:HeatPumpOptimizerConfigFlow (flow steps).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, ast, asyncio, importlib, json, re, sys, tempfile, time
from pathlib import Path

os.environ.setdefault("HPO_PLANDATA", str(Path(tempfile.mkdtemp()) / "plandata.json"))
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
ap = argparse.ArgumentParser(); ap.add_argument("--perturb", default="", choices=("", "diag", "icon"))
args = ap.parse_args()

import yaml  # noqa: E402
import golden  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
import heatpump_optimizer.coordinator as cm  # noqa: E402
from heatpump_optimizer import const, diagnostics  # noqa: E402

P = Path("custom_components/heatpump_optimizer")
S = json.loads((P / "strings.json").read_text())
EN = json.loads((P / "translations/en.json").read_text())
SV = json.loads((P / "translations/sv.json").read_text())
ICONS = json.loads((P / "icons.json").read_text())
MAN = json.loads((P / "manifest.json").read_text())
SRC = {f.name: f.read_text() for f in sorted(P.glob("*.py"))}
TREES = {n: ast.parse(t) for n, t in SRC.items()}
README = Path("README.md").read_text()
DOCS = README + "\n".join(p.read_text(errors="ignore") for p in sorted(Path("docs").rglob("*.md")))

def R(name, value, note=""):
    print(f"RESULT {name}={value} count{('  (' + note + ')') if note else ''}")

if args.perturb == "diag":
    diagnostics.TO_REDACT = set(diagnostics.TO_REDACT) - {const.CONF_TIBBER_TOKEN}
if args.perturb == "icon":
    ICONS["entity"]["sensor"].pop("optimization_status")

# ---- build a coordinator and every entity through the real setup
made = []
_orig = cm.HeatPumpOptimizerCoordinator.__init__
def _init(self, *a, **k):
    _orig(self, *a, **k); made.append(self)
cm.HeatPumpOptimizerCoordinator.__init__ = _init
dt_util.freeze(golden.START)
golden._capture_coordinator(golden.coordinator_scenarios()["coord_all_features"])
coord = made[0]; entry = coord.entry; hass = coord.hass
entry.runtime_data = coord
ents = []
for plat in const.PLATFORMS:
    mod = importlib.import_module(f"heatpump_optimizer.{plat}")
    got = []
    asyncio.run(mod.async_setup_entry(hass, entry, lambda es, *a, **k: got.extend(es)))
    ents += [(plat, e) for e in got]
R("entities_built", len(ents), "denominator")
A = lambda e, n, d=None: getattr(e, "_attr_" + n, d)

# ---- devices
di = coord.device_info
ids = {frozenset(e.device_info["identifiers"]) for _, e in ents}
R("devices.distinct_devices", len(ids), "expect 1")
R("devices.missing_fields", sum(1 for k in ("identifiers", "name", "manufacturer", "model", "entry_type") if not di.get(k)))
R("devices.entry_type_not_service", int(str(di.get("entry_type")) not in ("service", "DeviceEntryType.SERVICE")))

# ---- diagnostics: drive with a secret token, a free-text name and a precise location
entry.data.update({"tibber_token": "SECRET-TOKEN-XYZ", "name": "Private Household Name",
                   "solar_location": {"latitude": 59.334591, "longitude": 18.063240, "radius": 0}})
dump = json.dumps(asyncio.run(diagnostics.async_get_config_entry_diagnostics(hass, entry)), default=str)
leaks = [s for s in ("SECRET-TOKEN-XYZ", "Private Household Name", "59.3345", "18.0632") if s in dump]
R("diagnostics.leaks", len(leaks), ",".join(leaks))
R("diagnostics.not_json_native", int(dump != json.dumps(json.loads(dump))))

# ---- discovery / discovery-update-info (exempt check)
disc_keys = [k for k in ("zeroconf", "ssdp", "dhcp", "usb", "bluetooth", "mqtt", "homekit") if k in MAN]
disc_steps = re.findall(r"async_step_(zeroconf|ssdp|dhcp|usb|bluetooth|mqtt|homekit)\b", SRC["config_flow.py"])
R("discovery.mechanisms", len(disc_keys) + len(disc_steps), f"iot_class={MAN.get('iot_class')}; exempt basis")

# ---- docs rules (documentation lookups over README.md + docs/)
heads = [h.strip("# ").lower() for h in re.findall(r"^#{2,4} .*$", README, re.M)]
for rule, needle in (("docs_known_limitations", "known limitations"), ("docs_supported_devices", "supported heat pumps"),
                     ("docs_troubleshooting", "troubleshooting"), ("docs_use_cases", "what it does")):
    R(f"{rule}.heading_missing", int(not any(needle in h for h in heads)))
R("docs_data_update.interval_mismatch", int(not (f"{const.DEFAULT_OPTIMIZATION_INTERVAL} minutes by default" in README)),
  f"DEFAULT_OPTIMIZATION_INTERVAL={const.DEFAULT_OPTIMIZATION_INTERVAL}")
low = DOCS.lower()
und = [v["name"] for d in EN["entity"].values() for v in d.values() if v.get("name") and v["name"].lower() not in low]
svcs = yaml.safe_load((P / "services.yaml").read_text())
R("docs_supported_functions.entities_undocumented", len(und))
R("docs_supported_functions.services_undocumented", len([s for s in svcs if s not in low]))
bps = sorted(Path("blueprints/automation").glob("*.yaml"))
roster = {getattr(e, "entity_id", None) for _, e in ents}
bad_bp = []
for b in bps:
    t = b.read_text()
    for s in re.findall(r"service: heatpump_optimizer\.(\w+)", t):
        if s not in svcs: bad_bp.append(f"{b.name}:{s}")
    for eid in re.findall(r"default: ((?:sensor|switch|binary_sensor)\.heat_pump_optimizer_\w+)", t):
        if eid not in roster: bad_bp.append(f"{b.name}:{eid}")
R("docs_examples.blueprints", len(bps), "in-tree count; exchange listing not reachable offline")
R("docs_examples.blueprint_dangling_refs", len(bad_bp), ",".join(bad_bp))
R("docs_examples.readme_links_blueprints", int("blueprints/automation" in README), "1 = linked")

# ---- dynamic-devices / stale-devices (exempt check)
R("dynamic_stale_devices.registry_create_or_remove_sites",
  sum(len(re.findall(r"async_get_or_create|async_remove_device|async_remove_config_entry_device|async_update_device", t)) for t in SRC.values()))

# ---- entity rules
cats = {}
for _, e in ents:
    c = str(A(e, "entity_category")); cats[c] = cats.get(c, 0) + 1
R("entity_category.uncategorised", cats.get("None", 0), f"census {cats}")
nodc = [type(e).__name__ for p, e in ents if p == "sensor" and A(e, "native_unit_of_measurement") and A(e, "device_class") is None]
R("entity_device_class.unit_without_device_class", len(nodc), ",".join(nodc))
R("entity_disabled_by_default.disabled", sum(1 for _, e in ents if A(e, "entity_registry_enabled_default", True) is False
                                             or getattr(type(e), "entity_registry_enabled_default", True) is False), "census, not a violation count")
def _own_name_none(e):
    # main-feature entity: a class of THIS integration sets _attr_name = None itself
    return any("_attr_name" in vars(c) and vars(c)["_attr_name"] is None
               for c in type(e).__mro__ if c.__module__.startswith("heatpump_optimizer"))
main_feature = [type(e).__name__ for _, e in ents if A(e, "translation_key") is None and _own_name_none(e)]
no_tk = [type(e).__name__ for _, e in ents if A(e, "translation_key") is None and not _own_name_none(e)]
no_str = [f"{p}.{A(e,'translation_key')}" for p, e in ents if A(e, "translation_key") and not all(
    A(e, "translation_key") in D["entity"].get(p, {}) for D in (S, EN, SV))]
R("entity_translations.no_translation_key", len(no_tk), f"main-feature (name None) excluded: {main_feature}")
R("entity_translations.key_missing_in_a_language", len(no_str), ",".join(no_str))
R("entity_translations.has_entity_name_false", sum(1 for _, e in ents if not A(e, "has_entity_name")))

# ---- exception-translations (AST census)
HAEXC = {"HomeAssistantError", "ServiceValidationError", "ConfigEntryNotReady", "ConfigEntryAuthFailed", "ConfigEntryError", "UpdateFailed"}
no_key, bad_key, ph_bad = [], [], []
for n_, t in TREES.items():
    for n in ast.walk(t):
        if isinstance(n, ast.Raise) and isinstance(n.exc, ast.Call):
            f = n.exc.func; name = getattr(f, "id", None) or getattr(f, "attr", None)
            if name not in HAEXC: continue
            kw = {k.arg: k.value for k in n.exc.keywords}
            tk = kw.get("translation_key")
            if tk is None: no_key.append(f"{n_}:{n.lineno}"); continue
            if isinstance(tk, ast.Constant):
                if not all(tk.value in D.get("exceptions", {}) for D in (S, EN, SV)): bad_key.append(f"{n_}:{n.lineno}")
                ph = kw.get("translation_placeholders")
                keys = {k.value for k in ph.keys} if isinstance(ph, ast.Dict) else set()
                for D in (S, EN, SV):
                    if set(re.findall(r"\{(\w+)\}", D["exceptions"].get(tk.value, {}).get("message", ""))) != keys:
                        ph_bad.append(f"{n_}:{n.lineno}")
for key in re.findall(r'_raise_update_failed\(\s*"(\w+)"', SRC["coordinator.py"]):
    if not all(key in D.get("exceptions", {}) for D in (S, EN, SV)): bad_key.append(f"_raise_update_failed:{key}")
R("exception_translations.raise_without_key", len(no_key), ",".join(no_key))
R("exception_translations.key_not_in_every_language", len(bad_key), ",".join(bad_key))
R("exception_translations.placeholder_mismatch", len(ph_bad), ",".join(sorted(set(ph_bad))))

# ---- icon-translations
noicon = [f"{p}.{A(e,'translation_key')}" for p, e in ents if A(e, "translation_key")
          and A(e, "translation_key") not in ICONS["entity"].get(p, {}) and A(e, "device_class") is None]
R("icon_translations.entities_without_icon", len(noicon), ",".join(noicon))
R("icon_translations.attr_icon_pins", sum(len(re.findall(r"_attr_icon\s*=", t)) for t in SRC.values()))
R("icon_translations.icons_keys_without_entity", sum(1 for p, d in ICONS["entity"].items() for k in d
                                                     if k not in {A(e, 'translation_key') for q, e in ents if q == p}))

# ---- reconfiguration-flow
from heatpump_optimizer import config_flow  # noqa: E402
flows = [c for c in vars(config_flow).values() if isinstance(c, type) and hasattr(c, "async_step_user")]
R("reconfiguration_flow.flow_without_reconfigure", sum(1 for c in flows if not hasattr(c, "async_step_reconfigure")))

# ---- repair-issues
bad_iss = []
for n_, t in TREES.items():
    for n in ast.walk(t):
        if isinstance(n, ast.Call) and (getattr(n.func, "id", None) or getattr(n.func, "attr", None)) in ("_create_issue", "create_issue", "async_create_issue"):
            tk = {k.arg: k.value for k in n.keywords}.get("translation_key")
            if isinstance(tk, ast.Constant) and not all(tk.value in D.get("issues", {}) for D in (S, EN, SV)):
                bad_iss.append(f"{n_}:{n.lineno}")
R("repair_issues.literal_key_not_in_every_language", len(bad_iss), ",".join(bad_iss))

# ---- platinum
sync_http = sum(len(re.findall(r"^\s*(import requests|from requests|import urllib\.request|from urllib\.request|import http\.client|import httpx)", t, re.M)) for t in SRC.values())
R("async_dependency.sync_http_imports", sync_http, f"requirements={MAN.get('requirements')}")
R("inject_websession.own_client_sessions", sum(len(re.findall(r"ClientSession\(|async_create_clientsession|create_async_httpx_client", t)) for t in SRC.values()))
R("inject_websession.shared_session_sites", sum(len(re.findall(r"async_get_clientsession\(", t)) for t in SRC.values()), "census")
R("strict_typing.py_typed_missing", int(not (P / "py.typed").exists()))
R("strict_typing.type_ignores", sum(len(re.findall(r"#\s*type:\s*ignore", t)) for t in SRC.values()))
bare = sum(len(re.findall(r"(?<![A-Za-z])ConfigEntry\b(?!\w)", ast.unparse(a)))
           for t in TREES.values() for n in ast.walk(t) if isinstance(n, ast.arg) and n.annotation is not None for a in [n.annotation])
R("strict_typing.bare_configentry_params", bare)

print(f"RESULT thread_factor={time.process_time()/max(time.thread_time(),1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print(f"RESULT swapins={[l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]}")
