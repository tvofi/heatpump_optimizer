#!/usr/bin/env python3
"""Measure ONE historical tree with the CURRENT measurer (tests/structure.py at 7952d8f9).

Usage: python3 measure_one.py <tree-root>   -> prints one JSON object on stdout

* structure metrics: ``measure()`` of measurer/structure_7952d8f9.py, with REPO_ROOT /
  PACKAGE_DIR re-pointed at <tree-root>. The seam map is the CURRENT map
  (measurer/seam_map_7952d8f9.json) for every method it names, and the measurer's own
  seed rule ``regex_seam`` for any method it does not (historic names) -- a pure function
  of the method name, so the before and after sides of one commit use one assignment.
  The number of regex-fallback methods is reported as ``_seam_fallback``.
* enumerators m1 (hub writes), m2 (surface payload reads), m3 (coordinator private
  reach-through): the round-9 prototypes (handoff/audit-r9-alt evidence/), re-wrapped as
  functions that return counts and tolerate missing functions/files (reported as None).
"""
from __future__ import annotations

import ast
import collections
import importlib.util
import json
import re
import sys
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
MEASURER = HERE / "measurer" / "structure_7952d8f9.py"
SEAM_MAP = HERE / "measurer" / "seam_map_7952d8f9.json"


def load_measurer(root: Path):
    spec = importlib.util.spec_from_file_location("structure_cur", MEASURER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.REPO_ROOT = root
    mod.PACKAGE_DIR = root / "custom_components" / "heatpump_optimizer"
    mod.BUDGET_FILE = root / "tests" / "structure_budgets.json"
    mod.SEAM_MAP_FILE = SEAM_MAP
    current = json.loads(SEAM_MAP.read_text())["seams"]
    original = mod.seam_metrics
    fallback = []

    def hybrid_seam_metrics(coord_class, seams=None):
        methods = [m.name for m in coord_class.body
                   if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
        hybrid = {}
        for name in methods:
            if name in current:
                hybrid[name] = current[name]
            else:
                hybrid[name] = mod.regex_seam(name)
                fallback.append(name)
        return original(coord_class, hybrid)

    mod.seam_metrics = hybrid_seam_metrics
    return mod, fallback


def structure_metrics(root: Path) -> dict:
    out = {}
    try:
        mod, fallback = load_measurer(root)
        res = mod.measure()
        out.update(res["metrics"])
        out["_seam_fallback"] = len(fallback)
        out["_dynamic_problems"] = len(res["tables"]["dynamic_problems"])
        out["_top_is_coordinator"] = res["tables"]["top_is_coordinator"]
    except Exception as err:  # recorded, never hidden
        out["_structure_error"] = f"{type(err).__name__}: {err}"[:300]
        out["_structure_tb"] = traceback.format_exc()[-800:]
    return out


# ---------------------------------------------------------------- m1: hub writes
HUBS = ("_opt_config", "_thermal_params", "_current_state")


def _hub_writes(fn):
    alias = {}
    out = []
    for n in ast.walk(fn):
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) \
           and isinstance(n.value, ast.Attribute) and n.value.attr in HUBS:
            alias[n.targets[0].id] = n.value.attr
    for n in ast.walk(fn):
        tgts = []
        if isinstance(n, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            tgts = n.targets if isinstance(n, ast.Assign) else [n.target]
        for t in tgts:
            if isinstance(t, ast.Attribute):
                v = t.value
                if isinstance(v, ast.Attribute) and v.attr in HUBS:
                    out.append((v.attr, t.attr, t.lineno))
                elif isinstance(v, ast.Name) and v.id in alias:
                    out.append((alias[v.id], t.attr, t.lineno))
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "setattr" and n.args:
            a0 = n.args[0]
            hub = a0.attr if isinstance(a0, ast.Attribute) and a0.attr in HUBS else alias.get(getattr(a0, "id", None))
            if hub and len(n.args) > 1:
                f = n.args[1].value if isinstance(n.args[1], ast.Constant) else "<dynamic>"
                out.append((hub, f, n.lineno))
    return out


def m1(root: Path) -> dict:
    P = root / "custom_components" / "heatpump_optimizer"
    out = {}
    try:
        tree = ast.parse((P / "coordinator.py").read_text())
    except Exception as err:
        return {"_m1_error": str(err)[:200]}
    fns = {}
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fns.setdefault(n.name, n)
    writes = []
    present = 0
    for name in ("async_run_optimization", "_prepare_dhw_inputs"):
        if name in fns:
            present += 1
            writes += _hub_writes(fns[name])
    out["m1_solve_sites"] = len(writes) if present else None
    out["m1_solve_fields"] = len({(h, f) for h, f, _ in writes}) if present else None
    allw = _hub_writes(tree)
    out["m1_coord_sites"] = len(allw)
    out["m1_coord_fields"] = len({(h, f) for h, f, _ in allw})
    pkg = 0
    for p in sorted(P.rglob("*.py")):
        if p.name == "coordinator.py":
            continue
        try:
            pkg += len(_hub_writes(ast.parse(p.read_text())))
        except SyntaxError:
            pass
    out["m1_pkg_sites"] = len(allw) + pkg
    return out


# ---------------------------------------------------------------- m2: payload reads
TOP = {"self.coordinator.data", "self.coordinator.data or {}", "self._data()", "coordinator.data",
       "coordinator.data or {}"}
SURF = ["sensor.py", "binary_sensor.py", "climate.py", "switch.py", "entity.py", "button.py", "datetime.py"]


def m2(root: Path) -> dict:
    P = root / "custom_components" / "heatpump_optimizer"
    prod = set()
    goldens = sorted((root / "tests" / "golden").glob("coord_*.json"))
    for g in goldens:
        try:
            d = json.loads(g.read_text())
        except Exception:
            continue
        data = d.get("data", d) if isinstance(d, dict) else None
        prod |= set(data) if isinstance(data, dict) else set()
    reads = {}
    for f in SURF:
        if not (P / f).exists():
            continue
        t = ast.parse((P / f).read_text())
        for fn in [n for n in ast.walk(t) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            bound = {n.targets[0].id for n in ast.walk(fn) if isinstance(n, ast.Assign) and len(n.targets) == 1
                     and isinstance(n.targets[0], ast.Name) and ast.unparse(n.value) in TOP}

            def top(e):
                return ast.unparse(e) in TOP or (isinstance(e, ast.Name) and e.id in bound)
            for n in ast.walk(fn):
                k = None
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "get" and n.args \
                   and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str) and top(n.func.value):
                    k = n.args[0].value
                elif isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant) \
                        and isinstance(n.slice.value, str) and top(n.value):
                    k = n.slice.value
                if k:
                    reads.setdefault(k, []).append(f"{f}:{n.lineno}")
    return {
        "m2_keys_read": len(reads),
        "m2_read_sites": sum(map(len, reads.values())),
        "m2_unproduced": (len([k for k in reads if k not in prod]) if goldens else None),
    }


# ---------------------------------------------------------------- m3: reach-through
COORD_NAMES = {"coordinator", "coord", "self.coordinator", "self._coordinator", "self._coord"}


def m3(root: Path) -> dict:
    P = root / "custom_components" / "heatpump_optimizer"
    tot = collections.Counter()
    names = collections.Counter()
    writes = 0
    for p in sorted(P.glob("*.py")):
        if p.name == "coordinator.py":
            continue
        t = ast.parse(p.read_text())
        for n in ast.walk(t):
            hit = None
            if isinstance(n, ast.Attribute) and n.attr.startswith("_") and not n.attr.startswith("__") \
               and ast.unparse(n.value) in COORD_NAMES:
                hit = n.attr
                if isinstance(n.ctx, ast.Store):
                    writes += 1
            elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("getattr", "setattr", "hasattr") \
                    and len(n.args) >= 2 and ast.unparse(n.args[0]) in COORD_NAMES and isinstance(n.args[1], ast.Constant) \
                    and isinstance(n.args[1].value, str) and n.args[1].value.startswith("_") \
                    and not n.args[1].value.startswith("__"):
                hit = n.args[1].value
                if n.func.id == "setattr":
                    writes += 1
            if hit:
                tot[p.name] += 1
                names[hit] += 1
    return {"m3_reaches": sum(tot.values()), "m3_members": len(names), "m3_files": len(tot), "m3_writes": writes}


def main() -> int:
    root = Path(sys.argv[1]).resolve()
    out = structure_metrics(root)
    # null predictor: raw package size (a pure size proxy, not an architecture metric)
    pkg = root / "custom_components" / "heatpump_optimizer"
    out["null_pkg_loc"] = sum(len(p.read_text().splitlines()) for p in pkg.rglob("*.py"))
    for fn in (m1, m2, m3):
        try:
            out.update(fn(root))
        except Exception as err:
            out[f"_{fn.__name__}_error"] = f"{type(err).__name__}: {err}"[:200]
    print(json.dumps(out, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
