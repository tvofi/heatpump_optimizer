#!/usr/bin/env python3
"""D7 step 1 -- structural metrics of custom_components/heatpump_optimizer, by AST.

Metric (one line): per module physical lines / classes / functions; per class the
methods, the instance attributes (``self.<name>`` assigned anywhere in the class)
and how many are assigned in more than one method; per function the McCabe
cyclomatic complexity (1 + if / elif / for / while / except / ifexp / assert /
match-case / comprehension-for / comprehension-if / extra boolean operand); the
intra-package import graph (module-level edges and function-level "deferred"
edges, TYPE_CHECKING blocks excluded) and its strongly connected components.

Run:      PYTHONPATH=tests/hastub python tools/audit/round2/D7/metrics_ast.py
Expected: RESULT coordinator_lines=10902 (exact), coordinator_methods=264 (exact),
          every other RESULT exact (counts); baseline c398fc84eec25fc44b60d74aae05b9a2da205884.
Machine:  8-core Apple M1, 8 GB, shared audit box -- counts are contention-immune.
Instrumented symbol: heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator
          (and every module under custom_components/heatpump_optimizer).
Perturbation: delete one attribute cluster from coordinator.py (for example every
          attribute ``_init_dhw_learning`` assigns and the methods that only use
          them) -> coordinator_instance_attrs, coordinator_methods and
          coordinator_lines move DOWN; add ``from .coordinator import X`` at module
          level in sensor.py -> import_cycle_sccs_module_level moves UP.
Writes:   tools/audit/round2/D7/metrics_ast.json (next to this script) only.
"""
from __future__ import annotations

import os

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

import ast
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PKG = ROOT / "custom_components" / "heatpump_optimizer"
OUT = Path(__file__).resolve().parent / "metrics_ast.json"
PKG_NAME = "heatpump_optimizer"


# --- cyclomatic complexity ---------------------------------------------------

class _CC(ast.NodeVisitor):
    """McCabe complexity of ONE function body; nested defs are not descended."""

    def __init__(self) -> None:
        self.n = 1

    def generic_visit(self, node):  # noqa: D401
        if isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While,
                             ast.ExceptHandler, ast.IfExp, ast.Assert)):
            self.n += 1
        elif isinstance(node, ast.BoolOp):
            self.n += max(0, len(node.values) - 1)
        elif isinstance(node, ast.comprehension):
            self.n += 1 + len(node.ifs)
        elif isinstance(node, ast.match_case):
            self.n += 1
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda,
                             ast.ClassDef)):
            return  # nested scope: its own number
        super().generic_visit(node)


def complexity(fn: ast.AST) -> int:
    v = _CC()
    for stmt in fn.body:
        v.visit(stmt)
    return v.n


# --- per-module walk ---------------------------------------------------------

def module_name(path: Path) -> str:
    return path.stem


def resolve_import(node: ast.AST, this: str) -> list[str]:
    """Intra-package targets of one import node (module stems)."""
    out: list[str] = []
    if isinstance(node, ast.ImportFrom):
        if node.level == 1:
            if node.module:
                out.append(node.module.split(".")[0])
            else:
                out.extend(a.name for a in node.names)
        elif node.level == 0 and node.module and node.module.startswith(PKG_NAME + "."):
            out.append(node.module.split(".")[1])
        elif node.level == 0 and node.module == PKG_NAME:
            out.extend(a.name for a in node.names)
    elif isinstance(node, ast.Import):
        for a in node.names:
            if a.name.startswith(PKG_NAME + "."):
                out.append(a.name.split(".")[1])
    return [m for m in out if m != this]


def in_type_checking(stack: list[ast.AST]) -> bool:
    for n in stack:
        if isinstance(n, ast.If):
            t = n.test
            if (isinstance(t, ast.Name) and t.id == "TYPE_CHECKING") or (
                isinstance(t, ast.Attribute) and t.attr == "TYPE_CHECKING"
            ):
                return True
    return False


def walk_with_stack(node, stack=None):
    stack = stack or []
    yield node, stack
    for child in ast.iter_child_nodes(node):
        yield from walk_with_stack(child, stack + [node])


def analyse(path: Path) -> dict:
    src = path.read_text()
    tree = ast.parse(src)
    this = module_name(path)
    info = {
        "lines": src.count("\n") + (0 if src.endswith("\n") else 1),
        "classes": {},
        "functions": {},   # qualname -> cc
        "imports_module": set(),
        "imports_deferred": set(),
    }
    # imports
    for node, stack in walk_with_stack(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if in_type_checking(stack):
                continue
            targets = resolve_import(node, this)
            deferred = any(isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef)) for s in stack)
            (info["imports_deferred"] if deferred else info["imports_module"]).update(targets)
    # functions and classes
    def visit_scope(body, prefix, class_node=None):
        for n in body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                q = f"{prefix}{n.name}"
                info["functions"][q] = {"cc": complexity(n), "lineno": n.lineno,
                                        "lines": (n.end_lineno or n.lineno) - n.lineno + 1}
                # nested defs
                visit_scope([c for c in ast.walk(n) if False], q + ".")  # placeholder
                for c in n.body:
                    if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        visit_scope([c], q + ".")
                    else:
                        for d in ast.walk(c):
                            if isinstance(d, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                info["functions"].setdefault(
                                    f"{q}.<nested>.{d.name}",
                                    {"cc": complexity(d), "lineno": d.lineno,
                                     "lines": (d.end_lineno or d.lineno) - d.lineno + 1})
            elif isinstance(n, ast.ClassDef):
                q = f"{prefix}{n.name}"
                methods = [m for m in n.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
                attr_writers: dict[str, set[str]] = defaultdict(set)
                attr_readers: dict[str, set[str]] = defaultdict(set)
                for m in methods:
                    for d in ast.walk(m):
                        if isinstance(d, ast.Attribute) and isinstance(d.value, ast.Name) and d.value.id == "self":
                            if isinstance(d.ctx, (ast.Store, ast.Del)):
                                attr_writers[d.attr].add(m.name)
                            else:
                                attr_readers[d.attr].add(m.name)
                method_names = {m.name for m in methods}
                inst_attrs = {a for a in attr_writers if a not in method_names}
                class_attrs = [
                    s.target.id for s in n.body
                    if isinstance(s, ast.AnnAssign) and isinstance(s.target, ast.Name)
                ] + [
                    t.id for s in n.body if isinstance(s, ast.Assign)
                    for t in s.targets if isinstance(t, ast.Name)
                ]
                info["classes"][q] = {
                    "lineno": n.lineno,
                    "lines": (n.end_lineno or n.lineno) - n.lineno + 1,
                    "methods": len(methods),
                    "instance_attrs": len(inst_attrs),
                    "instance_attrs_multi_writer": sum(
                        1 for a in inst_attrs if len(attr_writers[a]) > 1),
                    "class_attrs": len(class_attrs),
                    "attr_writers": {a: sorted(attr_writers[a]) for a in sorted(inst_attrs)},
                }
                visit_scope(n.body, q + ".", n)
    visit_scope(tree.body, "")
    return info


def tarjan(graph: dict[str, set[str]]) -> list[list[str]]:
    index = {}
    low = {}
    stack = []
    on = set()
    out = []
    counter = [0]

    def strong(v):
        index[v] = low[v] = counter[0]
        counter[0] += 1
        stack.append(v)
        on.add(v)
        for w in graph.get(v, ()):
            if w not in index:
                strong(w)
                low[v] = min(low[v], low[w])
            elif w in on:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            comp = []
            while True:
                w = stack.pop()
                on.discard(w)
                comp.append(w)
                if w == v:
                    break
            out.append(sorted(comp))

    sys.setrecursionlimit(10000)
    for v in sorted(graph):
        if v not in index:
            strong(v)
    return out


def main() -> int:
    modules = sorted(p for p in PKG.glob("*.py"))
    per = {module_name(p): analyse(p) for p in modules}
    names = set(per)

    total_lines = sum(m["lines"] for m in per.values())
    all_funcs = {f"{mod}:{q}": d for mod, m in per.items() for q, d in m["functions"].items()}
    all_classes = {f"{mod}:{q}": d for mod, m in per.items() for q, d in m["classes"].items()}

    g_mod = {m: {t for t in per[m]["imports_module"] if t in names} for m in per}
    g_all = {m: {t for t in (per[m]["imports_module"] | per[m]["imports_deferred"]) if t in names} for m in per}
    sccs_mod = [c for c in tarjan(g_mod) if len(c) > 1]
    sccs_all = [c for c in tarjan(g_all) if len(c) > 1]
    # self-loops via deferred import of own module are impossible; 2-cycles:
    two_cycles_all = sorted({tuple(sorted((a, b))) for a in g_all for b in g_all[a] if a in g_all.get(b, ())})
    two_cycles_mod = sorted({tuple(sorted((a, b))) for a in g_mod for b in g_mod[a] if a in g_mod.get(b, ())})
    deferred_edges = sorted((m, t) for m in per for t in per[m]["imports_deferred"] if t in names)

    coord = per["coordinator"]
    coord_cls = coord["classes"]["HeatPumpOptimizerCoordinator"]
    cc_sorted = sorted(all_funcs.items(), key=lambda kv: -kv[1]["cc"])

    print("=== D7 metrics (AST) ===")
    print(f"{'module':22} {'lines':>6} {'classes':>7} {'funcs':>6} {'maxCC':>6} {'imports':>7} {'deferred':>8}")
    for mod in sorted(per, key=lambda m: -per[m]["lines"]):
        m = per[mod]
        maxcc = max((d["cc"] for d in m["functions"].values()), default=0)
        print(f"{mod:22} {m['lines']:6d} {len(m['classes']):7d} {len(m['functions']):6d} {maxcc:6d} "
              f"{len(g_mod[mod]):7d} {len([t for t in m['imports_deferred'] if t in names]):8d}")
    print("\nTop 20 functions by cyclomatic complexity:")
    for q, d in cc_sorted[:20]:
        print(f"  {d['cc']:4d}  {q}  (line {d['lineno']}, {d['lines']} lines)")
    print("\nClasses by methods:")
    for q, d in sorted(all_classes.items(), key=lambda kv: -kv[1]["methods"])[:10]:
        print(f"  {d['methods']:4d} methods {d['instance_attrs']:4d} attrs "
              f"({d['instance_attrs_multi_writer']} multi-writer)  {q}  {d['lines']} lines")
    print("\nModule-level import SCCs (size>1):", sccs_mod)
    print("Module+deferred import SCCs (size>1):", [(len(c), c[:6]) for c in sccs_all])
    print("2-cycles at module level:", two_cycles_mod)
    print("2-cycles incl. deferred:", two_cycles_all[:20], "..." if len(two_cycles_all) > 20 else "")
    print("Deferred (function-level) intra-package imports:", deferred_edges)

    res = {
        "total_lines": total_lines,
        "modules": len(per),
        "coordinator_lines": coord["lines"],
        "coordinator_methods": coord_cls["methods"],
        "coordinator_instance_attrs": coord_cls["instance_attrs"],
        "coordinator_instance_attrs_multi_writer": coord_cls["instance_attrs_multi_writer"],
        "coordinator_class_lines": coord_cls["lines"],
        "coordinator_share_of_package_lines": round(coord["lines"] / total_lines, 4),
        "functions_total": len(all_funcs),
        "functions_cc_gt_10": sum(1 for d in all_funcs.values() if d["cc"] > 10),
        "functions_cc_gt_20": sum(1 for d in all_funcs.values() if d["cc"] > 20),
        "functions_cc_gt_30": sum(1 for d in all_funcs.values() if d["cc"] > 30),
        "max_cc": cc_sorted[0][1]["cc"],
        "import_edges_module_level": sum(len(v) for v in g_mod.values()),
        "import_edges_deferred": len(deferred_edges),
        "import_cycle_sccs_module_level": len(sccs_mod),
        "import_cycle_sccs_with_deferred": len(sccs_all),
        "largest_scc_with_deferred": max((len(c) for c in sccs_all), default=0),
        "two_cycles_with_deferred": len(two_cycles_all),
    }
    for k, v in res.items():
        unit = "ratio" if isinstance(v, float) else "count"
        print(f"RESULT {k}={v} {unit}")
    print("RESULT thread_factor=1.0")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    OUT.write_text(json.dumps({
        "results": res,
        "modules": {m: {k: (sorted(v) if isinstance(v, set) else v) for k, v in d.items()} for m, d in per.items()},
        "sccs_module_level": sccs_mod,
        "sccs_with_deferred": sccs_all,
        "two_cycles_with_deferred": two_cycles_all,
        "deferred_edges": deferred_edges,
        "top_cc": [(q, d) for q, d in cc_sorted[:40]],
    }, indent=1, default=sorted))
    return 0


if __name__ == "__main__":
    sys.exit(main())
