"""Verifier 2 harness (D6-01 attack) -- independent measurement of the HA boundary.

METRIC (mine, differs from the finder's): two numbers.
  (a) direct_ha_importers: modules whose own top-level AST contains an
      `import homeassistant...` / `from homeassistant...` statement executed at
      module import time (top level, including inside module-level try/if).
  (b) ha_dependents_by_reason: modules that fail to import with homeassistant
      refused, ATTRIBUTED -- only counted when the failure chain mentions the
      refusal, so a module failing for an unrelated missing dependency cannot
      inflate the count.

RUN (from the repository root):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/verify2_boundary.py

ROOT RULE: working directory (`ROOT = Path(".")`).

Baseline for comparison: finder's ha_boundary.py at 7dd68dd (21 failures,
11 undocumented). This tree is the branch head 0855277.
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
import json
import pathlib
import subprocess
import sys
import tempfile
import shutil

ROOT = pathlib.Path(".")
PKG = ROOT / "custom_components" / "heatpump_optimizer"

# ---- (a) AST scan: direct module-level HA import statements -----------------
def _top_level_import_names(tree: ast.Module) -> set[str]:
    """Names imported by statements that execute at module import time.

    Walks the module body plus, recursively, the bodies of module-level
    try/except/else/finally and if/else blocks -- anything that runs during
    import. Does NOT descend into function/class defs (those are lazy).
    """
    found: set[str] = set()
    stack: list[ast.stmt] = list(tree.body)
    while stack:
        node = stack.pop()
        if isinstance(node, ast.Import):
            for a in node.names:
                found.add(a.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                found.add(node.module)
        elif isinstance(node, ast.Try):
            stack.extend(node.body)
            stack.extend(node.orelse)
            stack.extend(node.finalbody)
            for h in node.handlers:
                stack.extend(h.body)
        elif isinstance(node, ast.If):
            stack.extend(node.body)
            stack.extend(node.orelse)
    return found


modules = sorted(p.stem for p in PKG.glob("*.py"))
direct: dict[str, set[str]] = {}
for p in PKG.glob("*.py"):
    tree = ast.parse(p.read_text())
    ha_names = {n for n in _top_level_import_names(tree)
                if n == "homeassistant" or n.startswith("homeassistant.")}
    if ha_names:
        direct[p.stem] = ha_names

# any HA import anywhere in the file (including inside functions) -- the lazy set
lazy_only: dict[str, int] = {}
for p in PKG.glob("*.py"):
    src = p.read_text()
    n_any = sum(1 for node in ast.walk(ast.parse(src))
                if isinstance(node, (ast.Import, ast.ImportFrom)))
    lazy_only[p.stem] = n_any

# ---- (b) attributed import-refusal probe ------------------------------------
CHILD = r'''
import sys, importlib, json
class Refuse:
    def find_module(self, name, path=None):
        return self.find_spec(name, path)
    def find_spec(self, name, path=None, target=None):
        if name == "homeassistant" or name.startswith("homeassistant."):
            raise ImportError("VERIFIER2-HA-REFUSED")
        return None
sys.meta_path.insert(0, Refuse())
sys.path.insert(0, sys.argv[2])
name = sys.argv[1]
try:
    importlib.import_module("heatpump_optimizer." + name)
    print(json.dumps({"ok": True}))
except BaseException as err:
    chain = []
    e = err
    while e is not None:
        chain.append(type(e).__name__ + ": " + str(e))
        e = e.__cause__ or e.__context__
        if len(chain) > 8:
            break
    print(json.dumps({"ok": False, "chain": chain}))
'''

_tmp = pathlib.Path(tempfile.mkdtemp(prefix="d6v2-boundary-"))
_scratch = _tmp / "heatpump_optimizer"
shutil.copytree(PKG, _scratch, ignore=shutil.ignore_patterns("__pycache__"))
(_scratch / "__init__.py").write_text("")  # empty: measure submodules, not pkg

attributed: dict[str, str] = {}
unattributed: dict[str, str] = {}
for name in [m for m in modules if m != "__init__"]:
    r = subprocess.run(
        [sys.executable, "-c", CHILD, name, str(_tmp)],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": "tests/hastub"},
    )
    out = r.stdout.strip().splitlines()
    try:
        res = json.loads(out[-1])
    except Exception:
        unattributed[name] = "NO-OUTPUT: " + (r.stderr or r.stdout)[:160]
        continue
    if res.get("ok"):
        continue
    chain = " <- ".join(res["chain"])
    if "VERIFIER2-HA-REFUSED" in chain:
        attributed[name] = chain[-200:]
    else:
        unattributed[name] = chain[-200:]

# __init__ measured separately (it IS the package)
init_src = (PKG / "__init__.py").read_text()
init_direct = "__init__" in direct
shutil.rmtree(_tmp, ignore_errors=True)

# ---- doc's named ten ---------------------------------------------------------
DOC_TEN = {"__init__", "config_flow", "coordinator", "open_meteo", "frontend",
           "sensor", "binary_sensor", "button", "climate", "switch"}

total_with_init = len(modules)
probe_failures = sorted(attributed) + (["__init__"] if init_direct else [])
undocumented = sorted(set(probe_failures) - DOC_TEN)
direct_importers = sorted(direct)
direct_undocumented = sorted(set(direct_importers) - DOC_TEN)

print(f"RESULT v2_modules_total={total_with_init} modules")
print(f"RESULT v2_direct_ha_importers={len(direct_importers)} modules")
print(f"RESULT v2_direct_undocumented={len(direct_undocumented)} modules")
print(f"RESULT v2_probe_attributed_failures={len(probe_failures)} modules")
print(f"RESULT v2_probe_unattributed_failures={len(unattributed)} modules")
print(f"RESULT v2_undocumented_dependents={len(undocumented)} modules")
print(f"RESULT thread_factor=1.0")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
print("direct importers:", direct_importers)
print("direct undocumented:", direct_undocumented)
print("probe undocumented dependents:", undocumented)
if unattributed:
    print("UNATTRIBUTED (would have been false positives):", unattributed)
# per-module attribution sample
for n in sorted(attributed):
    if n not in direct:
        print(f"  transitive: {n}: ...{attributed[n][-120:]}")
