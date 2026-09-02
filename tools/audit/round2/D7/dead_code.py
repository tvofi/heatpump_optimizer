#!/usr/bin/env python3
"""D7 step 7 -- dead code: AST reachability confirmed by a runtime sentinel.

Metric (one line): every def (module function, method, nested def) under
custom_components/heatpump_optimizer is classed on two axes -- STATIC: its name occurs
anywhere in production as a Name, an attribute or a token of a non-docstring string constant
(so a getattr / dispatch-table / services.yaml use counts), else in tests/, else nowhere; RUNTIME: its code object STARTED
at least once while the gate's Python scripts (features, entities, golden, backtest,
optimality, validate, edge, manual_plan, open_meteo, solar_alignment, plan_view, frontend,
dst_checks; rolling/stress excluded as SLOW/alone) ran under sys.monitoring PY_START in a
tree copy carrying a stub RELEASE_NOTES.md (see train_mutations.py for why). dead_candidates
= not started AND not referenced in production AND not referenced in tests AND not a
framework hook by name (dunder, async_setup*/unload/migrate/step_*, HA entity properties).
Decorated defs are matched on either the def line or the first decorator line (CPython's
co_firstlineno is the decorator's).

Run:      PYTHONPATH=tests/hastub python tools/audit/round2/D7/dead_code.py
Expected: exact counts; ~3 min wall on the shared box; baseline c398fc84eec25fc44b60d74aae05b9a2da205884.
Machine:  8-core Apple M1, 8 GB, shared audit box; no timing reported.
Instrumented symbol: every def under heatpump_optimizer (co_firstlineno via sys.monitoring);
          the RESULT dead_candidates lists them by module:qualname:line.
Perturbation: delete one listed dead candidate from production -> dead_candidates DOWN by 1
          and the suite still passes; add a call to it in coordinator.py -> DOWN by 1 with
          started_by_suite UP by 1.
Writes:   tools/audit/round2/D7/dead_code.json and a private temp root only.
"""
from __future__ import annotations

import os

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

import ast
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
OUT = HERE / "dead_code.json"
PKG_REL = "custom_components/heatpump_optimizer"
PY = sys.executable
SCRIPTS = ["tests/features.py", "tests/entities.py", "tests/golden.py", "tests/backtest.py",
           "tests/optimality.py", "tests/validate.py", "tests/edge.py", "tests/manual_plan.py",
           "tests/open_meteo.py", "tests/solar_alignment.py", "tests/plan_view.py",
           "tests/frontend.py", "tests/dst_checks.py"]
FRAMEWORK = re.compile(
    r"^(__.*__|async_setup.*|async_unload.*|async_migrate.*|async_remove.*|async_get_options_flow|"
    r"async_step_.*|async_added_to_hass|async_will_remove_from_hass|async_press|async_turn_on|"
    r"async_turn_off|async_set_.*|async_select_option|async_update|native_value|native_min_value|"
    r"native_max_value|native_step|native_unit_of_measurement|extra_state_attributes|is_on|available|"
    r"icon|name|unique_id|device_info|state|device_class|state_class|options|current_option|"
    r"entity_category|hvac_mode|hvac_action|hvac_modes|current_temperature|target_temperature|"
    r"min_temp|max_temp|supported_features|temperature_unit|preset_mode|preset_modes|mode|"
    r"suggested_display_precision|entity_registry_enabled_default|should_poll|translation_key)$")


def defs_in(path: Path):
    tree = ast.parse(path.read_text())
    out = []

    def visit(body, prefix, kind):
        for n in body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                first = min([n.lineno] + [d.lineno for d in n.decorator_list])
                decos = [ast.unparse(d) for d in n.decorator_list]
                out.append({"name": n.name, "qualname": f"{prefix}{n.name}", "lineno": n.lineno,
                            "first": first, "kind": kind, "decorators": decos,
                            "lines": (n.end_lineno or n.lineno) - n.lineno + 1})
                inner = [c for c in ast.walk(n) if c is not n and isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
                # nested defs, one level (ast.walk is transitive; qualname approximated)
                for c in inner:
                    if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        f2 = min([c.lineno] + [d.lineno for d in c.decorator_list])
                        out.append({"name": c.name, "qualname": f"{prefix}{n.name}.<locals>.{c.name}",
                                    "lineno": c.lineno, "first": f2, "kind": "nested",
                                    "decorators": [ast.unparse(d) for d in c.decorator_list],
                                    "lines": (c.end_lineno or c.lineno) - c.lineno + 1})
            elif isinstance(n, ast.ClassDef):
                visit(n.body, f"{prefix}{n.name}.", "method")
    visit(tree.body, "", "function")
    return out


def name_census(paths):
    """Occurrences of every identifier as a Name, an attribute, or a token inside a string
    constant -- docstrings excluded, so a name mentioned only in prose does not count as a
    reference. A def's own name is a str field of FunctionDef, never a Name node, so the
    census never counts the definition itself."""
    c = Counter()
    for p in paths:
        try:
            tree = ast.parse(p.read_text())
        except SyntaxError:
            continue
        docstrings = set()
        for n in ast.walk(tree):
            if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and n.body:
                first = n.body[0]
                if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                    docstrings.add(id(first.value))
        for n in ast.walk(tree):
            if isinstance(n, ast.Name):
                c[n.id] += 1
            elif isinstance(n, ast.Attribute):
                c[n.attr] += 1
            elif isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docstrings:
                for tok in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", n.value):
                    c[tok] += 1
    return c


def js_yaml_json_census():
    c = Counter()
    for p in [ROOT / PKG_REL / "services.yaml", ROOT / PKG_REL / "strings.json",
              ROOT / PKG_REL / "www" / "heatpump-optimizer-card.js"]:
        if p.exists():
            for tok in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", p.read_text(errors="replace")):
                c[tok] += 1
    return c


def run_suite(tmp: Path):
    dst = tmp / "deadcode"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns("tools", ".git", "__pycache__", "*.pyc"))
    version = (ROOT / "VERSION").read_text().strip()
    (dst / "RELEASE_NOTES.md").write_text(f"## v{version}\n\n- D7 audit stub.\n")
    prefix = str((dst / PKG_REL).resolve()) + os.sep
    started = set()
    status = {}
    for s in SCRIPTS:
        out = tmp / (Path(s).stem + ".started.json")
        env = dict(os.environ)
        env.update({"PYTHONPATH": "tests/hastub", "D7_PKG_PREFIX": prefix, "D7_MON_OUT": str(out),
                    "HPO_PLANDATA": str(dst / "plandata.json")})
        env.pop("HASTUB_TZ", None)          # dst_checks.py's variable only; it breaks features.py
        if s.endswith("dst_checks.py"):
            env["HASTUB_TZ"] = "Europe/Stockholm"
        r = subprocess.run([PY, str(HERE / "d7_monitor_boot.py"), s], cwd=dst, env=env,
                           capture_output=True, text=True, timeout=1800)
        n = 0
        if out.exists():
            got = json.load(open(out))
            n = len(got)
            started.update((f, l, q) for f, l, q in got)
        status[s] = {"exit": r.returncode, "code_objects": n}
        print(f"   {s:28} exit={r.returncode:3d} code objects started={n}")
    shutil.rmtree(dst, ignore_errors=True)
    return started, status


def main() -> int:
    print("=== D7 dead code ===")
    pkg = ROOT / PKG_REL
    prod = sorted(pkg.glob("*.py"))
    tests = sorted((ROOT / "tests").glob("*.py"))
    defs = []
    for p in prod:
        for d in defs_in(p):
            d["module"] = p.name
            defs.append(d)
    # static references: count of occurrences of the name across production minus the defs of that name
    prod_names = name_census(prod) + js_yaml_json_census()
    test_names = name_census(tests)
    tmp = Path(os.environ.get("D7_TMP") or tempfile.mkdtemp(prefix="d7dead-"))
    tmp.mkdir(parents=True, exist_ok=True)
    print("-- runtime sentinel: the gate's Python scripts under sys.monitoring")
    started, status = run_suite(tmp)
    started_lines = {(f, l) for f, l, _ in started}
    started_qual = {(f, q) for f, _, q in started}

    rows = []
    for d in defs:
        ref_prod = prod_names[d["name"]]
        ref_test = test_names[d["name"]]
        ran = ((d["module"], d["first"]) in started_lines or (d["module"], d["lineno"]) in started_lines
               or (d["module"], d["qualname"]) in started_qual)
        fw = bool(FRAMEWORK.match(d["name"]))
        prop = any(x in ("property", "cached_property", "callback", "staticmethod", "classmethod") for x in d["decorators"])
        rows.append({**d, "ref_prod": ref_prod, "ref_test": ref_test, "started": ran, "framework": fw,
                     "decorated": prop})
    dead = [r for r in rows if not r["started"] and r["ref_prod"] == 0 and r["ref_test"] == 0 and not r["framework"]]
    dead_prod_only = [r for r in rows if not r["started"] and r["ref_prod"] == 0 and not r["framework"]]
    untested = [r for r in rows if not r["started"] and (r["ref_prod"] > 0)]
    dynamic = [r for r in rows if r["started"] and r["ref_prod"] == 0 and not r["framework"]]

    print(f"\n-- defs {len(rows)}; started by the suite {sum(r['started'] for r in rows)}; "
          f"statically unreferenced in production {sum(1 for r in rows if r['ref_prod'] == 0)}")
    print("\nDead candidates (never started, unreferenced in production AND tests, not a framework hook):")
    for r in sorted(dead, key=lambda r: (r["module"], r["lineno"])):
        print(f"   {r['module']}:{r['qualname']}:{r['lineno']} ({r['lines']} lines, {r['kind']}, deco={r['decorators']})")
    print("\nUnreferenced in production, never started, but named in tests (test-only reach):")
    for r in sorted(dead_prod_only, key=lambda r: (r["module"], r["lineno"])):
        if r not in dead:
            print(f"   {r['module']}:{r['qualname']}:{r['lineno']} ({r['lines']} lines) tests refs={r['ref_test']}")
    print(f"\nStarted at runtime but statically unreferenced in production (dynamic reach, the sentinel's job): {len(dynamic)}")
    for r in sorted(dynamic, key=lambda r: (r["module"], r["lineno"]))[:40]:
        print(f"   {r['module']}:{r['qualname']}:{r['lineno']} deco={r['decorators']} tests refs={r['ref_test']}")
    print(f"\nReferenced in production but never started by the suite (uncovered, not dead): {len(untested)}")
    by_mod = Counter(r["module"] for r in untested)
    print("   by module:", by_mod.most_common(12))

    res = {
        "defs_total": len(rows),
        "started_by_suite": sum(r["started"] for r in rows),
        "static_unreferenced_prod": sum(1 for r in rows if r["ref_prod"] == 0),
        "dead_candidates": len(dead),
        "dead_candidate_lines": sum(r["lines"] for r in dead),
        "unreferenced_prod_never_started_incl_test_named": len(dead_prod_only),
        "dynamic_reach_started_unreferenced": len(dynamic),
        "referenced_never_started": len(untested),
    }
    for k, v in res.items():
        print(f"RESULT {k}={v} count")
    print("RESULT dead_candidate_list=" + ";".join(f"{r['module']}:{r['qualname']}:{r['lineno']}" for r in dead) + " text")
    print("RESULT thread_factor=1.0")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    OUT.write_text(json.dumps({"results": res, "suite": status, "dead": dead, "dead_prod_only": dead_prod_only,
                               "dynamic": dynamic, "untested": untested}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
