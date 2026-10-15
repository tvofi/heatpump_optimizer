"""layering: package modules that reach a heavier layer than their own, and private names that cross a
module boundary (R10-ARCHSCORE-COVERAGE item 1; ARCH2-s4, round 10).

The layers, lowest first: a PURE module (it imports neither boundary), the SOLVER layer (it imports scipy),
the GLUE layer (it imports Home Assistant). A module's layer is the highest boundary it imports itself.
An import may go down or across, never up: glue may use the solver and pure code, the solver may use pure
code. Over the package's import graph -- a relative import at ANY scope is an edge, a function's
``from .optimizer import f`` included, because a lazy import is the same coupling paid later (counter
C17); an import under ``if TYPE_CHECKING:`` is no edge, nothing runs it --

  layer_violations   modules that reach, through other package modules, a layer above their own: a pure
                     module that cannot load without scipy (``quiet_windows`` and ``silent_mode`` reached
                     the optimizer for its private ``_utc_step_starts``) or without Home Assistant, or a
                     solver module that drags in Home Assistant. A decomposition does not move it: a module
                     extracted from the glue that imports Home Assistant is glue.
  private_cross_module   distinct private names (one leading underscore) of one package module named by
                     another: ``from .m import _x``, ``m._x`` through a module binding, and
                     ``getattr(m, "_x")`` (counter C18: the attribute spellings are the same reach).
  unused_boundary_imports  (gate-only, counter C19) imports of a boundary whose names the module never reads:
                     a module would otherwise climb a layer, and leave its violation, by an import that does
                     nothing (attempt 23).

LAYERS is a design choice, stated: Home Assistant is the integration's glue edge (model, optimizer and
learner modules take no ``homeassistant`` import, fixer.md step 17), and scipy is the solver's dependency.
numpy is used by nearly every module and is no boundary. A dynamic import (``importlib.import_module``
with a computed name) is invisible; the package's two are ``__init__``'s platform loader and the
optimizer's optional threadpool limiter.
"""
from __future__ import annotations

import ast
import re
import time
from pathlib import Path

from . import common as C

#: boundary -> layer rank; a module's rank is the highest it imports, 0 for a pure module.
LAYERS = {"scipy": 1, "homeassistant": 2}
#: Counter C17: a function-scope import is an edge. ``vector.py`` switches it off.
ALL_SCOPES = True
#: Counter C18: a private name read through a module binding is a crossing. ``vector.py`` switches it off.
PRIVATE_ATTRS = True
#: Counter C19: an unread boundary import is a tripwire. ``vector.py`` switches it off.
UNUSED_IMPORTS = True


def _private(name: str) -> bool:
    return name.startswith("_") and not name.startswith("__")


def _module_level(tree: ast.Module) -> set[int]:
    """ids of the import statements that run at import time: outside every function body."""
    out: set[int] = set()
    todo = list(tree.body)
    while todo:
        n = todo.pop()
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            continue
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            out.add(id(n))
        todo.extend(ast.iter_child_nodes(n))
    return out


def _relative_targets(pkg: C.Pkg, mod: str, node: ast.ImportFrom) -> list[tuple[str, str]]:
    """(target module, imported name) for each name of a relative import; the name is ``""`` when the
    name is itself a module."""
    base = mod.split(".")[:-1]
    base = base[:len(base) - node.level + 1]
    src = ".".join(base + ([node.module] if node.module else []))
    out = []
    for a in node.names:
        full = f"{src}.{a.name}" if src else a.name
        if full in pkg.mods:
            out.append((full, ""))
        elif (src or "__init__") in pkg.mods:
            out.append((src or "__init__", a.name))
    return out


def graph(pkg: C.Pkg) -> tuple[dict[str, set[str]], dict[str, set[str]], set[str]]:
    """(package edges, external roots imported, distinct private crossings ``"m -> n._x"``): a
    name read three times from one module is one crossing, the unit of coupling."""
    edges: dict[str, set[str]] = {m: set() for m in pkg.mods}
    ext: dict[str, set[str]] = {m: set() for m in pkg.mods}
    crossings: set[str] = set()
    for m, mod in pkg.mods.items():
        live = None if ALL_SCOPES else _module_level(mod.tree)
        modalias = {k: v[1] for k, v in mod.imports.items() if v[0] == "mod" and v[1] != m}
        for n in C.walk(mod.tree):
            if isinstance(n, (ast.Import, ast.ImportFrom)):
                if id(n) in pkg.type_checking_imports or (live is not None and id(n) not in live):
                    continue
                if isinstance(n, ast.ImportFrom) and n.level:
                    for target, name in _relative_targets(pkg, m, n):
                        if target != m:
                            edges[m].add(target)
                            if _private(name or target.rsplit(".", 1)[-1]):
                                crossings.add(f"{m} -> {target}.{name}" if name else f"{m} -> {target}")
                elif isinstance(n, ast.ImportFrom) and n.module:
                    ext[m].add(n.module.split(".")[0])
                elif isinstance(n, ast.Import):
                    ext[m] |= {a.name.split(".")[0] for a in n.names}
            elif PRIVATE_ATTRS and isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) \
                    and n.value.id in modalias and _private(n.attr):
                crossings.add(f"{m} -> {modalias[n.value.id]}.{n.attr}")
            elif PRIVATE_ATTRS and isinstance(n, ast.Call) and isinstance(n.func, ast.Name) \
                    and n.func.id in ("getattr", "hasattr", "setattr") and len(n.args) >= 2 \
                    and isinstance(n.args[0], ast.Name) and n.args[0].id in modalias \
                    and isinstance(n.args[1], ast.Constant) and isinstance(n.args[1].value, str) \
                    and _private(n.args[1].value):
                crossings.add(f"{m} -> {modalias[n.args[0].id]}.{n.args[1].value}")
    return edges, ext, crossings


def closure(edges: dict[str, set[str]], m: str) -> set[str]:
    seen, todo = set(), [m]
    while todo:
        for y in edges[todo.pop()]:
            if y not in seen:
                seen.add(y)
                todo.append(y)
    seen.discard(m)
    return seen


def unused_boundary_imports(pkg: C.Pkg) -> list[str]:
    """``module: name`` for each name a boundary import binds that the module never reads (a loaded name,
    or a word of a string annotation)."""
    out = []
    for m, mod in pkg.mods.items():
        bound: dict[str, str] = {}
        for n in C.walk(mod.tree):
            if isinstance(n, ast.Import):
                for a in n.names:
                    if a.name.split(".")[0] in LAYERS:
                        bound[a.asname or a.name.split(".")[0]] = a.name
            elif isinstance(n, ast.ImportFrom) and not n.level and n.module and n.module.split(".")[0] in LAYERS:
                for a in n.names:
                    bound[a.asname or a.name] = f"{n.module}.{a.name}"
        if not bound:
            continue
        read = {n.id for n in C.walk(mod.tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
        for n in C.walk(mod.tree):
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and len(n.value) < 200:
                read |= set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", n.value))
        out += [f"{m}: {name}" for name in sorted(bound) if name not in read]
    return out


def measure(root: Path) -> dict:
    t0 = time.perf_counter()
    pkg = C.load(str(root))
    edges, ext, crossings = graph(pkg)
    rank = {m: max([LAYERS[x] for x in ext[m] if x in LAYERS], default=0) for m in pkg.mods}
    violations = sorted(f"{m} ({rank[m]} -> {max(rank[n] for n in closure(edges, m))})" for m in pkg.mods
                        if closure(edges, m) and max(rank[n] for n in closure(edges, m)) > rank[m])
    unused = unused_boundary_imports(pkg) if UNUSED_IMPORTS else []
    return {
        "metric": "layering",
        "layer_violations": len(violations),
        "private_cross_module": len(crossings),
        "unused_boundary_imports": len(unused) if UNUSED_IMPORTS else None,
        "details": {
            "layers": {r: sorted(m for m in pkg.mods if rank[m] == r) for r in (0, *sorted(LAYERS.values()))},
            "violations": violations,
            "crossings": sorted(crossings),
            "unused_boundary_imports": unused,
        },
        "runtime_s": round(time.perf_counter() - t0, 3),
    }
