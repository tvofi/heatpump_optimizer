"""import_cycles: strongly-connected components of the package's intra-package
import graph, plus Martin's instability / abstractness / main-sequence view.

Graph. Node = package module. Edge m -> n when m imports n by any
intra-package form (``from . import n``, ``from .n import x``, ``from .n.x
import y``, ``from . import n as a``), at module level OR inside a function
(a function-local import is a runtime dependency, and is the usual way a
cycle is hidden from the import-time check). Imports under ``if
TYPE_CHECKING:`` are excluded: they never execute. ``from .n import x``
where ``x`` is itself a submodule adds the edge to ``n.x`` too.

Headline: number of modules that sit in a non-trivial SCC (size > 1, or a
self-import), by Tarjan's algorithm. Details: the SCCs; the same on the
module-level-only graph (the import-time cycles Python would actually hit);
per-module Ca (afferent: modules importing it), Ce (efferent: modules it
imports), I = Ce / (Ca + Ce); A = abstract classes (Protocol / ABC /
abstractmethod-bearing) / all classes; D = |A + I - 1|; the mean D and the
modules in the "zone of pain" (I < 0.3 and A < 0.3 with Ca >= 5: heavily
depended-on and concrete).
"""
from __future__ import annotations

import ast
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C  # noqa: E402


def edges(pkg: C.Pkg, module_level_only: bool = False) -> dict[str, set[str]]:
    g: dict[str, set[str]] = {m: set() for m in pkg.mods}
    for m in pkg.mods.values():
        parts = m.name.split(".")[:-1]
        nodes = m.tree.body if module_level_only else C.walk(m.tree)
        if module_level_only:  # module level includes try/if blocks at top
            nodes = [n for top in m.tree.body if not isinstance(top, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                     for n in C.walk(top)]
        for n in nodes:
            if id(n) in pkg.type_checking_imports:
                continue
            if isinstance(n, ast.ImportFrom) and n.level > 0:
                base = parts[: len(parts) - n.level + 1]
                src = ".".join(base + [n.module] if n.module else base)
                if src in pkg.mods:
                    g[m.name].add(src)
                for a in n.names:
                    sub = f"{src}.{a.name}" if src else a.name
                    if sub in pkg.mods:
                        g[m.name].add(sub)
            elif isinstance(n, ast.Call) and not module_level_only:
                # importlib.import_module(".x", __package__) and the package's
                # lazy wrappers around it: a runtime edge the AST can name
                f = n.func
                fname = f.id if isinstance(f, ast.Name) else getattr(f, "attr", "")
                if fname in ("import_module", "_lazy", "_async_lazy"):
                    for a in n.args:
                        if isinstance(a, ast.Constant) and isinstance(a.value, str) and a.value.lstrip(".") in pkg.mods:
                            g[m.name].add(a.value.lstrip("."))
            elif isinstance(n, ast.Import):
                for a in n.names:
                    if a.name.startswith("custom_components.heatpump_optimizer."):
                        t = a.name.split("custom_components.heatpump_optimizer.", 1)[1]
                        if t in pkg.mods:
                            g[m.name].add(t)
    return g


def tarjan(g: dict[str, set[str]]) -> list[list[str]]:
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    stack: list[str] = []
    on: set[str] = set()
    out: list[list[str]] = []
    counter = [0]
    sys.setrecursionlimit(max(10000, sys.getrecursionlimit()))

    def strong(v):
        index[v] = low[v] = counter[0]
        counter[0] += 1
        stack.append(v)
        on.add(v)
        for w in sorted(g[v]):
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

    for v in sorted(g):
        if v not in index:
            strong(v)
    return [c for c in out if len(c) > 1 or c[0] in g[c[0]]]


def abstractness(pkg: C.Pkg, mod: str) -> tuple[int, int]:
    total = abstract = 0
    for key, c in pkg.classes.items():
        if key[0] != mod:
            continue
        total += 1
        bases = " ".join(c.ext_bases)
        has_abs = any("abstractmethod" in C._decorator_names(s) for s in c.node.body
                      if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef)))
        if "Protocol" in bases or "ABC" in bases or has_abs:
            abstract += 1
    return abstract, total


def measure(root: Path) -> dict:
    t0 = time.perf_counter()
    pkg = C.load(str(root))
    g = edges(pkg)
    g_top = edges(pkg, module_level_only=True)
    sccs = tarjan(g)
    sccs_top = tarjan(g_top)
    ca = {m: 0 for m in g}
    for m, outs in g.items():
        for n in outs:
            if n != m:
                ca[n] += 1
    rows = {}
    for m in sorted(g):
        ce = len(g[m] - {m})
        inst = ce / (ca[m] + ce) if (ca[m] + ce) else 0.0
        a, tot = abstractness(pkg, m)
        abst = a / tot if tot else 0.0
        rows[m] = {"Ca": ca[m], "Ce": ce, "I": round(inst, 3), "A": round(abst, 3), "D": round(abs(abst + inst - 1), 3)}
    mean_d = round(sum(r["D"] for r in rows.values()) / len(rows), 3) if rows else 0.0
    pain = sorted(m for m, r in rows.items() if r["I"] < 0.3 and r["A"] < 0.3 and r["Ca"] >= 5)
    return {
        "metric": "import_cycles",
        "value": sum(len(c) for c in sccs),
        "details": {
            "sccs": sccs,
            "import_time_sccs_module_level_only": sccs_top,
            "modules_in_import_time_cycles": sum(len(c) for c in sccs_top),
            "edges": sum(len(v - {k}) for k, v in g.items()),
            "mean_distance_from_main_sequence": mean_d,
            "zone_of_pain": pain,
            "per_module": rows,
        },
        "runtime_s": round(time.perf_counter() - t0, 3),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(measure(Path(sys.argv[1] if len(sys.argv) > 1 else ".")), indent=1))
