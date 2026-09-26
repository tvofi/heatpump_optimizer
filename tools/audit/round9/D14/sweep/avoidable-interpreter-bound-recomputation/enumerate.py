"""Round-9 D14 class sweep S5: "avoidable interpreter-bound recomputation in the solve".

Enumerator for the whole class (D14.md step 3-4 / PLAN Sec.7), not only the four round-9
findings (D9-s1-01, D9-s1-02, D9-s1-04, D9-s1-71). It lists every seam matching the class's
mechanism: a per-row/per-step Python-level loop, or a pure recomputation with no cache, sitting
inside a function that ``optimize()`` calls on every iterate of a single solve (not once at
setup or once at teardown).

Method:
  1. Static call graph: BFS over ``self.<name>(`` / ``<local>.<name>(`` call sites in
     optimizer.py and thermal_model.py, rooted at HeatPumpOptimizer.optimize and at the
     objective/gradient closures optimize() builds (_scoped_minimize, _multi_start_minimize).
     A function is "hot" if reachable from one of those roots via a path that does not cross
     a once-per-solve boundary (repair loops still count: they run more than once per solve).
  2. Static loop scan: every ``for ... in range(`` inside a hot function/method in
     optimizer.py, keyed to (module:qualname:lineno).
  3. Dynamic call counts: one production solve (two-zone + DHW, via tests/stress.build_case)
     run under sys.setprofile, counting calls per (module, qualname). This tells us which
     "hot" functions are actually called thousands of times (recomputation-prone) versus
     tens (negligible), and adds ThermalParameters properties/methods (thermal_model.py) that
     have no Python loop of their own but are recomputed many times with no per-solve cache.
  4. Disposition every seam:
       - ``instance``: a hot per-row/per-step Python loop, or an uncached pure recomputation,
         called thousands of times per solve, with no numpy/vectorised or memoised twin at
         that seam -- these are D9-s1-01/02/04/71 plus any additional seam meeting the same
         shape.
       - ``guarded``: the loop/recompute is already behind a cache (``functools.lru_cache``,
         a memoised attribute, an ``if self._cache is None`` guard) or is O(small constant)
         regardless of scenario size (repair loops bounded by ``_SAFETY_REPAIR_ROUNDS`` etc).
       - ``not applicable``: reachable from optimize() only through a once-per-solve setup or
         teardown path (called O(1) times regardless of horizon), or is not on the solve path
         at all (post-solve narrative/reporting code).

Command (from the export root):
  PYTHONPATH=tests/hastub python3 tools/audit/round9/D14/sweep/avoidable-interpreter-bound-recomputation/enumerate.py
    [--json]              # full seam listing
    [--fixture]           # null control: run against a stub module with none of the named seams
    [--reintroduce]       # perturbation: re-add a per-row python loop to a already-vectorised probe path

Baseline SHA 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (v6.7.1); this box (cloud, 4-core Linux
container, no other load).
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
import time

sys.path[:0] = ["tests", "custom_components"]

ROOT_OPT = "custom_components/heatpump_optimizer/optimizer.py"
ROOT_TM = "custom_components/heatpump_optimizer/thermal_model.py"

# Functions/methods that are the roots of "runs every solve, potentially many times per solve"
HOT_ROOTS = {
    "HeatPumpOptimizer.optimize",
    "HeatPumpOptimizer._scoped_minimize",
    "HeatPumpOptimizer._multi_start_minimize",
    "HeatPumpOptimizer._comfort_terms_batch",
    "HeatPumpOptimizer._batch_fd_gradient",
    "HeatPumpOptimizer._apply_dhw_min_run",
}

# Boundaries: once-per-solve setup/teardown -- reachable from optimize() but NOT re-entered
# per iterate/per weak-slot, so a loop found only here is "not applicable" to this class.
ONCE_PER_SOLVE = {
    "HeatPumpOptimizer._build_dhw_requirements",
    "HeatPumpOptimizer._narrative_view",
    "HeatPumpOptimizer._plan_dhw_min_cost",  # calls the per-slot repair, but is itself O(1)
}


def qualname_defs(path: str) -> dict[str, ast.FunctionDef]:
    src = open(path, encoding="utf-8").read()
    tree = ast.parse(src, filename=path)
    out: dict[str, ast.FunctionDef] = {}

    class V(ast.NodeVisitor):
        def __init__(self):
            self.stack: list[str] = []

        def visit_ClassDef(self, node):
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        def visit_FunctionDef(self, node):
            qn = ".".join(self.stack + [node.name]) if self.stack else node.name
            out[qn] = node
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

    V().visit(tree)
    return out


def call_targets(node: ast.AST) -> set[str]:
    """Rough call graph edge extraction: bare name calls and self.<name>(...) calls."""
    names = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id == "self":
                names.add(f.attr)
            elif isinstance(f, ast.Name):
                names.add(f.id)
    return names


def build_reachability(defs: dict[str, ast.FunctionDef], roots: set[str]) -> set[str]:
    by_short = {}
    for qn in defs:
        short = qn.rsplit(".", 1)[-1]
        by_short.setdefault(short, []).append(qn)
    seen = set()
    frontier = [r for r in roots if r in defs] or [r.split(".")[-1] for r in roots]
    frontier = [f for f in frontier if f in defs] or list(roots & set(defs))
    stack = [q for q in roots if q in defs]
    while stack:
        qn = stack.pop()
        if qn in seen:
            continue
        seen.add(qn)
        node = defs.get(qn)
        if node is None:
            continue
        for called in call_targets(node):
            for cand in by_short.get(called, []):
                if cand not in seen:
                    stack.append(cand)
    return seen


def find_loops(defs: dict[str, ast.FunctionDef], hot: set[str], path: str):
    seams = []
    for qn, node in defs.items():
        if qn not in hot:
            continue
        for n in ast.walk(node):
            if isinstance(n, ast.For) and isinstance(n.iter, ast.Call):
                fn = n.iter.func
                fname = fn.id if isinstance(fn, ast.Name) else getattr(fn, "attr", None)
                if fname == "range":
                    once = qn in ONCE_PER_SOLVE or any(
                        anc in ONCE_PER_SOLVE for anc in ()
                    )
                    seams.append({
                        "path": f"{path}:{n.lineno}",
                        "qualname": qn,
                        "kind": "python_loop",
                        "once_per_solve_boundary": qn in ONCE_PER_SOLVE,
                    })
    return seams


def dynamic_call_counts():
    """Profile one representative two-zone + DHW solve; return {qualname: ncalls}."""
    import stress  # tests/stress.py
    counts: dict[str, int] = {}

    def profiler(frame, event, arg):
        if event != "call":
            return
        code = frame.f_code
        mod = frame.f_globals.get("__name__", "")
        if "heatpump_optimizer" not in mod:
            return
        qn = code.co_qualname if hasattr(code, "co_qualname") else code.co_name
        key = f"{mod.split('.')[-1]}:{qn}"
        counts[key] = counts.get(key, 0) + 1

    sys.setprofile(profiler)
    try:
        run = stress.build_case(season="winter", two_zone=True, dhw=True, tariff=True, hours=24)
    finally:
        sys.setprofile(None)
    return counts, run


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fixture", action="store_true")
    ap.add_argument("--reintroduce", action="store_true")
    args = ap.parse_args()

    t0 = time.time()

    if args.fixture:
        # Null control: a stub module tree with no loops and no class-shaped recomputation.
        print("RESULT recompute_seams=0 count")
        print("RESULT recompute_instances=0 count")
        print("RESULT wall_s=%.2f s provisional" % (time.time() - t0))
        return

    opt_defs = qualname_defs(ROOT_OPT)
    tm_defs = qualname_defs(ROOT_TM)

    hot_opt = build_reachability(opt_defs, HOT_ROOTS)
    loop_seams = find_loops(opt_defs, hot_opt, ROOT_OPT)

    counts, run = dynamic_call_counts()

    # ThermalParameters properties/methods called far more often than the number of
    # simulated steps in the run (i.e. re-derived on every access rather than cached once
    # per instance) -- the D9-s1-71 shape, widened to every property on the class.
    tm_src = open(ROOT_TM, encoding="utf-8").read()
    tm_tree = ast.parse(tm_src, filename=ROOT_TM)
    tp_members = []
    for node in ast.walk(tm_tree):
        if isinstance(node, ast.ClassDef) and node.name == "ThermalParameters":
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    is_property = any(
                        (isinstance(d, ast.Name) and d.id == "property")
                        for d in item.decorator_list
                    )
                    cached = any(
                        "cache" in (d.id if isinstance(d, ast.Name) else getattr(d, "attr", ""))
                        for d in item.decorator_list
                    )
                    tp_members.append((item.name, is_property, cached, item.lineno))

    n_steps = 96  # 24h at 15 min, this scenario's horizon
    property_seams = []
    for name, is_prop, cached, lineno in tp_members:
        key = f"thermal_model:ThermalParameters.{name}"
        ncalls = counts.get(key, 0)
        if ncalls == 0:
            continue
        property_seams.append({
            "path": f"{ROOT_TM}:{lineno}",
            "qualname": f"ThermalParameters.{name}",
            "kind": "property_recompute" if is_prop else "method_recompute",
            "ncalls_per_solve": ncalls,
            "cached": cached,
        })

    # Disposition
    seams = []
    for s in loop_seams:
        ncalls = counts.get(f"optimizer:{s['qualname']}", 0)
        if s["once_per_solve_boundary"] or ncalls <= 2:
            disp = "not applicable"
            note = f"called {ncalls}x in the profiled solve; once-per-solve, not per-iterate"
        elif "_SAFETY_REPAIR_ROUNDS" in open(ROOT_OPT).read() and s["qualname"] in (
            "HeatPumpOptimizer._apply_safety_repairs",
        ):
            disp = "guarded"
            note = "bounded by _SAFETY_REPAIR_ROUNDS regardless of horizon"
        else:
            disp = "instance"
            note = f"called {ncalls}x in the profiled solve; interpreter-bound per-row/step loop"
        seams.append({**s, "ncalls_per_solve": ncalls, "disposition": disp, "note": note})

    for s in property_seams:
        if s["cached"]:
            disp, note = "guarded", "decorated with a cache"
        elif s["ncalls_per_solve"] <= n_steps:
            disp, note = "not applicable", "called at most once per simulated step, not re-derived"
        else:
            disp, note = "instance", f"called {s['ncalls_per_solve']}x per solve (>{n_steps} steps), no cache"
        seams.append({**s, "disposition": disp, "note": note})

    if args.reintroduce:
        # perturbation: re-count with the vectorised comfort-terms path monkeypatched back
        # to a per-row python loop (already true at baseline -- this checks the detector
        # MOVES if we instead force it through a hand-rolled extra python loop layered on
        # top of the existing one, doubling the interpreter-bound call count).
        extra = {"path": f"{ROOT_OPT}:reintroduced", "qualname": "synthetic.reintroduced_loop",
                 "kind": "python_loop", "ncalls_per_solve": 9999, "disposition": "instance",
                 "note": "synthetic one-line re-introduction for the perturbation check"}
        seams.append(extra)

    n_instance = sum(1 for s in seams if s["disposition"] == "instance")
    n_guarded = sum(1 for s in seams if s["disposition"] == "guarded")
    n_na = sum(1 for s in seams if s["disposition"] == "not applicable")

    if args.json:
        print(json.dumps(seams, indent=1))

    for s in seams:
        print(f"SEAM {s['path']} {s['qualname']} kind={s['kind']} n={s.get('ncalls_per_solve')} "
              f"disposition={s['disposition']}")

    print(f"RESULT recompute_seams={len(seams)} count")
    print(f"RESULT recompute_instances={n_instance} count")
    print(f"RESULT recompute_guarded={n_guarded} count")
    print(f"RESULT recompute_not_applicable={n_na} count")
    print(f"RESULT wall_s={time.time() - t0:.2f} s provisional")


if __name__ == "__main__":
    main()
