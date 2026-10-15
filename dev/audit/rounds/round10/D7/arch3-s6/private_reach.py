#!/usr/bin/env python3
"""ARCH3-s6 (round 10, D7): cross-module private reach and import closures, at every scope.

Metric 1: private_reach = number of (importer, source, name) triples where a module imports a name
          starting with one underscore from a sibling module, at ANY scope (module, function,
          TYPE_CHECKING) -- a function-scope reach is still a dependency on another module's
          private surface.
Metric 2: closure(M) = transitive module-level import closure of M (function-scope and
          TYPE_CHECKING imports excluded: they do not load at import time).
Command:  python3 dev/audit/rounds/round10/D7/arch3-s6/private_reach.py [PKG_DIR] [--closure M ...]
Perturbation: delete one private import line from a module -> private_reach falls by one; re-add a
          `from .optimizer import X` at module level of legionella -> closure(legionella) rises.
Null:     run twice on the same tree -> identical output (static; no timing).
"""
from __future__ import annotations

import ast
import os
import sys
import time
from pathlib import Path


def scan(pkg: Path):
    mods = {p.stem: p for p in sorted(pkg.glob("*.py"))}
    rows, graph = [], {}
    for m, p in mods.items():
        tree = ast.parse(p.read_text())
        lazy = set()
        for n in ast.walk(tree):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) or (
                isinstance(n, ast.If) and "TYPE_CHECKING" in ast.unparse(n.test)
            ):
                lazy.update(id(x) for x in ast.walk(n) if x is not n)
        out = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.ImportFrom) and n.level == 1:
                names = [n.module.split(".")[0]] if n.module else [a.name for a in n.names]
                if n.module:
                    for a in n.names:
                        if a.name.startswith("_") and not a.name.startswith("__"):
                            rows.append((m, n.module, a.name, n.lineno, "lazy" if id(n) in lazy else "top"))
                if id(n) not in lazy:
                    out.update(names)
        # `from . import sib` then `sib._name`: the same reach, spelled as an attribute
        sibs = {(a.asname or a.name) for n in ast.walk(tree)
                if isinstance(n, ast.ImportFrom) and n.level == 1 and not n.module
                for a in n.names if a.name in mods}
        for n in ast.walk(tree):
            if (isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
                    and n.value.id in sibs and n.attr.startswith("_")
                    and not n.attr.startswith("__")):
                rows.append((m, n.value.id, n.attr, n.lineno, "attr"))
        graph[m] = {o for o in out if o in mods and o != m}
    return rows, graph


def closure(g, m):
    seen, stack = set(), [m]
    while stack:
        for y in g.get(stack.pop(), ()):
            if y not in seen:
                seen.add(y)
                stack.append(y)
    seen.discard(m)
    return seen


def main(argv):
    t_cpu, t_thr = time.process_time(), time.thread_time()
    args = [a for a in argv[1:]]
    clos = []
    if "--closure" in args:
        i = args.index("--closure")
        clos = args[i + 1:]
        args = args[:i]
    pkg = Path(args[0] if args else "custom_components/heatpump_optimizer")
    rows, g = scan(pkg)
    for r in rows:
        print(f"ROW {r[0]:20s} <- {r[1]:18s} {r[2]:30s} L{r[3]:<5d} {r[4]}")
    print(f"RESULT private_reach={len(rows)} count")
    for m in clos:
        c = closure(g, m)
        print(f"RESULT closure_{m}={len(c)} modules optimizer={'IN' if 'optimizer' in c else 'out'}")
        # every direct edge of m that, alone, brings the solver in
        via = sorted(d for d in g.get(m, ()) if d == "optimizer" or "optimizer" in closure(g, d))
        print(f"INFO  solver_via_{m}={','.join(via) or '-'}")
    if "--all" in argv:
        sizes = {m: len(closure(g, m)) for m in g}
        print(f"RESULT closure_sum_all={sum(sizes.values())} module-edges")
        print(f"RESULT solver_reachers={sum(1 for m in g if 'optimizer' in closure(g, m))} modules")
    cpu, thr = time.process_time() - t_cpu, time.thread_time() - t_thr
    print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
