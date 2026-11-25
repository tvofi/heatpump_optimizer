"""D10-s2 gold rule exception-translations: every Home Assistant exception the
integration constructs carries translation_domain=DOMAIN and a translation_key
that every shipped catalogue (strings.json, en, sv, de) defines, with exactly
the placeholders the raise site passes.

Metric: bad = (site, catalogue) pairs where a HomeAssistantError-family
construction (direct, or through a helper that forwards its caller's key)
lacks a key, names a key the catalogue lacks, or passes placeholders that
differ from the catalogue message's fields.
Key: the raise site's own keyword arguments as written in the shipped source
against the shipped catalogue's message text (what HA formats at raise time).
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D10/s2/exc_translations.py [--perturb]
Expected at baseline 92d38ecb: RESULT bad=2 (button.py and services.py raise
run_optimization_no_prices with {entry_ids}; de.json's message reads
{entry_id}), +-0. --perturb deletes the en catalogue's entry for the first
literal key met (in memory): bad rises.
Instrumented symbol: heatpump_optimizer.button:ForceOptimizationButton.async_press,
heatpump_optimizer.services (run_optimization handler), and the catalogues
custom_components/heatpump_optimizer/translations/*.json.
Machine: local macOS box B2, Python 3.14 venv-ci.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import ast
import json
import resource
import string
import sys
import time
from pathlib import Path

PKG = Path("custom_components/heatpump_optimizer")
HA_EXC = {"HomeAssistantError", "ServiceValidationError", "ConfigEntryNotReady",
          "ConfigEntryError", "ConfigEntryAuthFailed", "UpdateFailed",
          "IntegrationError", "Unauthorized", "ServiceNotFound"}
PERTURB = "--perturb" in sys.argv
CATS = {n: json.loads((PKG / f).read_text()).get("exceptions", {}) for n, f in (
    ("strings", "strings.json"), ("en", "translations/en.json"),
    ("sv", "translations/sv.json"), ("de", "translations/de.json"))}
TREES = {p: ast.parse(p.read_text()) for p in sorted(PKG.glob("*.py"))}


def fields(msg):
    return {f for _, f, _, _ in string.Formatter().parse(msg) if f}


def is_exc_call(node):
    return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in HA_EXC


# Helpers that construct the exception with a key their caller passes:
# name -> (key param index, key param name, placeholder spec), the spec a set
# of literal names, or "**" when the helper forwards its own **kwargs.
HELPERS = {}
for tree in TREES.values():
    for fn in ast.walk(tree):
        if not isinstance(fn, ast.FunctionDef):
            continue
        params = [a.arg for a in fn.args.args]
        for node in ast.walk(fn):
            if not is_exc_call(node):
                continue
            kw = {k.arg: k.value for k in node.keywords if k.arg}
            key = kw.get("translation_key")
            if isinstance(key, ast.Name) and key.id in params:
                ph = kw.get("translation_placeholders")
                if isinstance(ph, ast.Name) and fn.args.kwarg and ph.id == fn.args.kwarg.arg:
                    spec = "**"
                elif isinstance(ph, ast.Dict):
                    spec = {k.value for k in ph.keys if isinstance(k, ast.Constant)}
                else:
                    spec = set()
                HELPERS[fn.name] = (params.index(key.id), key.id, spec)

state = {"perturbed": False}
sites = 0
bad = []


def judge(where, key_node, passed):
    if not isinstance(key_node, ast.Constant):
        bad.append(f"{where} non-literal key")
        return
    key = key_node.value
    if PERTURB and not state["perturbed"] and key in CATS["en"]:
        del CATS["en"][key]
        state["perturbed"] = True
    for name, cat in CATS.items():
        msg = (cat.get(key) or {}).get("message")
        if not msg:
            bad.append(f"{where} key {key} missing in {name}")
        elif fields(msg) != passed:
            bad.append(f"{where} key {key} placeholders {sorted(passed)} vs {name} {sorted(fields(msg))}")


for path, tree in TREES.items():
    helper_bodies = {id(n) for fn in ast.walk(tree) if isinstance(fn, ast.FunctionDef)
                     and fn.name in HELPERS for n in ast.walk(fn)}
    for node in ast.walk(tree):
        if isinstance(node, ast.Raise) and isinstance(node.exc, ast.Name) and node.exc.id in HA_EXC:
            sites += 1
            bad.append(f"{path.name}:{node.lineno} bare raise {node.exc.id}")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in HELPERS:
            idx, kname, spec = HELPERS[node.func.id]
            kw = {k.arg: k.value for k in node.keywords if k.arg}
            key = node.args[idx] if len(node.args) > idx else kw.get(kname)
            passed = ({k.arg for k in node.keywords if k.arg and k.arg != kname}
                      if spec == "**" else spec)
            sites += 1
            judge(f"{path.name}:{node.lineno} via {node.func.id}", key, passed)
        elif is_exc_call(node) and id(node) not in helper_bodies:
            sites += 1
            kw = {k.arg: k.value for k in node.keywords if k.arg}
            where = f"{path.name}:{node.lineno} {node.func.id}"
            if "translation_key" not in kw or "translation_domain" not in kw:
                bad.append(f"{where} no translation_key/domain")
                continue
            ph = kw.get("translation_placeholders")
            passed = {k.value for k in ph.keys if isinstance(k, ast.Constant)} if isinstance(ph, ast.Dict) else set()
            judge(where, kw["translation_key"], passed)

for line in bad:
    print("BAD", line)
print(f"RESULT helpers={len(HELPERS)} count")
print(f"RESULT sites={sites} count")
print(f"RESULT bad={len(bad)} count")
print(f"RESULT thread_factor={time.process_time() / (time.thread_time() or 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}")
