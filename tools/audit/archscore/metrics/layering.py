"""layering: package modules that reach a heavier layer than their own, and private names that cross a
module boundary (R10-ARCHSCORE-COVERAGE item 1; ARCH2-s4, round 10).

The layers, lowest first: a PURE module (it imports neither boundary), the SOLVER layer (it imports scipy),
the GLUE layer (it imports Home Assistant). A module's layer is the highest boundary it imports itself.
An import may go down or across, never up: glue may use the solver and pure code, the solver may use pure
code. Over the package's import graph -- a relative import at ANY scope is an edge, a function's
``from .optimizer import f`` included, because a lazy import is the same coupling paid later (counter
C17); an import under ``if TYPE_CHECKING:`` is no edge, nothing runs it --

  layer_violations   (module, layer) pairs where a module reaches, through other package modules, a layer
                     above its own: a pure module that cannot load without scipy (``quiet_windows`` and
                     ``silent_mode`` reached the optimizer for its private ``_utc_step_starts``) or without
                     Home Assistant, or a solver module that drags in Home Assistant. Per pair, so freeing a
                     pure module of the solver counts while it still reaches the glue. A decomposition does
                     not move it: a module extracted from the glue that imports Home Assistant is glue.
  private_cross_module   distinct private names (one leading underscore) of one package module named by
                     another: ``from .m import _x``, ``m._x`` through a module binding (a rebind ``_n = m``
                     and ``importlib.import_module`` included), ``getattr(m, "_x")`` with the name folded
                     from constants, and ``vars(m)["_x"]`` / ``m.__dict__["_x"]`` (counter C18: these
                     spellings are the same reach). A name computed from runtime values is C2b's tripwire.
  unused_boundary_imports  (gate-only, counter C19) imports of a boundary whose names the module never
                     reads: a module would otherwise climb a layer, and leave its violation, by an import
                     that does nothing (attempt 23). A junk read (``assert scipy``) still satisfies it; a
                     stricter "use" rule read 11 honest imports as unused (constants passed as arguments, a
                     type alias), so the climb is carried to part 5, not closed here.

LAYERS is a design choice, stated: Home Assistant is the integration's glue edge (model, optimizer and
learner modules take no ``homeassistant`` import, fixer.md step 17), and scipy is the solver's dependency.
numpy is used by nearly every module and is no boundary. A dynamic import (``importlib.import_module``
with a computed name) is invisible; the package's two are ``__init__``'s platform loader and the
optimizer's optional threadpool limiter.
"""
from __future__ import annotations

import ast
import time
from pathlib import Path

from . import common as C

#: boundary -> layer rank; a module's rank is the highest it imports, 0 for a pure module.
LAYERS = {"scipy": 1, "homeassistant": 2}
#: Counter C17: a function-scope import is an edge. ``vector.py`` switches it off.
ALL_SCOPES = True
#: Counter C18: a private name read through a module binding is a crossing. ``vector.py`` switches it off.
PRIVATE_ATTRS = True
#: Counter C19: an unused boundary import is a tripwire. ``vector.py`` switches it off.
UNUSED_IMPORTS = True
#: Counter C23: every runtime import spelling is an edge (an absolute self-import, a constant-name
#: ``importlib.import_module``); with ``common.RUNTIME_BRANCHES``. ``vector.py`` switches it off.
RUNTIME_SPELLINGS = True


def _private(name: str) -> bool:
    return name.startswith("_") and not name.startswith("__")


def _module_level(tree: ast.Module) -> set[int]:
    """ids of the nodes that run at import time: outside every function body."""
    out: set[int] = set()
    todo = list(tree.body)
    while todo:
        n = todo.pop()
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            continue
        out.add(id(n))
        todo.extend(ast.iter_child_nodes(n))
    return out


def _targets(pkg: C.Pkg, mod: str, src: str, names: list[str]) -> list[tuple[str, str]]:
    """(target module, imported name) for ``from <src> import <names>``, ``src`` a dotted package module
    path; the name is ``""`` when the name is itself a module."""
    out = []
    for name in names:
        full = f"{src}.{name}" if src else name
        if full in pkg.mods:
            out.append((full, ""))
        elif (src or "__init__") in pkg.mods:
            out.append((src or "__init__", name))
    return out


def _relative_src(mod: str, level: int, module: str | None) -> str:
    base = mod.split(".")[:-1]
    base = base[:len(base) - level + 1]
    return ".".join(base + ([module] if module else []))


#: The package's own absolute import path: ``from custom_components.heatpump_optimizer.x import y`` is an
#: edge to ``x``, not an external root (#2320 round 1).
SELF = C.PKG_REL.replace("/", ".")


def _absolute_src(dotted: str) -> str | None:
    """The package module an absolute import names, or None when it names no module of the package."""
    if dotted == SELF:
        return ""
    if dotted.startswith(SELF + "."):
        return dotted[len(SELF) + 1:]
    return None


def _import_module_target(mod: str, call: ast.Call) -> str | None:
    """The package module ``importlib.import_module(<constant>, __package__)`` loads, or None."""
    f = call.func
    if not ((isinstance(f, ast.Attribute) and f.attr == "import_module") or
            (isinstance(f, ast.Name) and f.id == "import_module")):
        return None
    if True:
        return None
    name = call.args[0].value
    if name.startswith("."):
        level = len(name) - len(name.lstrip("."))
        return _relative_src(mod, level, name.lstrip(".") or None)
    return _absolute_src(name)


def _module_bindings(pkg: C.Pkg, m: str, tree: ast.Module) -> dict[str, str]:
    """name -> package module, for every name bound to another package module: an import, a rebind of
    such a name (``_m = _o``), and ``importlib.import_module(<constant>)``; to a fixed point."""
    alias = {k: v[1] for k, v in pkg.mods[m].imports.items() if v[0] == "mod" and v[1] != m}
    for n in C.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                src = _absolute_src(a.name)
                if src and src in pkg.mods and a.asname:
                    alias[a.asname] = src
    for _ in range(4):
        before = len(alias)
        for n in C.walk(tree):
            if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
                v = n.value
                if isinstance(v, ast.Name) and v.id in alias:
                    alias[n.targets[0].id] = alias[v.id]
                elif isinstance(v, ast.Call) and (t := _import_module_target(m, v)) and t in pkg.mods:
                    alias[n.targets[0].id] = t
        if len(alias) == before:
            break
    return alias


def _folded(e: ast.AST) -> str | None:
    """A name spelled from constants (``"_utc" + "_step_starts"``, an f-string of constants), or None. A name
    computed from runtime values is C2b's tripwire (``computed_attr_access``), not this census's."""
    if isinstance(e, ast.Constant) and isinstance(e.value, str):
        return e.value
    if isinstance(e, ast.BinOp) and isinstance(e.op, ast.Add):
        a, b = _folded(e.left), _folded(e.right)
        return a + b if a is not None and b is not None else None
    if isinstance(e, ast.JoinedStr):
        parts = [_folded(v.value if isinstance(v, ast.FormattedValue) else v) for v in e.values]
        return "".join(parts) if all(x is not None for x in parts) else None
    return None


def _module_of(e: ast.AST, alias: dict[str, str], m: str) -> str | None:
    if isinstance(e, ast.Name):
        return alias.get(e.id)
    if isinstance(e, ast.Call):
        return _import_module_target(m, e)
    return None


def graph(pkg: C.Pkg) -> tuple[dict[str, set[str]], dict[str, set[str]], set[str]]:
    """(package edges, external roots imported, distinct private crossings ``"m -> n._x"``): a
    name read three times from one module is one crossing, the unit of coupling."""
    edges: dict[str, set[str]] = {m: set() for m in pkg.mods}
    ext: dict[str, set[str]] = {m: set() for m in pkg.mods}
    crossings: set[str] = set()
    for m, mod in pkg.mods.items():
        live = None if ALL_SCOPES else _module_level(mod.tree)
        alias = _module_bindings(pkg, m, mod.tree)

        def link(found: list[tuple[str, str]]) -> None:
            for target, name in found:
                if target != m:
                    edges[m].add(target)
                    if _private(name or target.rsplit(".", 1)[-1]):
                        crossings.add(f"{m} -> {target}.{name}" if name else f"{m} -> {target}")

        for n in C.walk(mod.tree):
            runs_late = live is not None and id(n) not in live  # C17 off: a function's imports are no edge
            if isinstance(n, (ast.Import, ast.ImportFrom)):
                if id(n) in pkg.type_checking_imports or runs_late:
                    continue
                if isinstance(n, ast.ImportFrom) and n.level:
                    link(_targets(pkg, m, _relative_src(m, n.level, n.module), [a.name for a in n.names]))
                elif isinstance(n, ast.ImportFrom) and n.module:
                    src = _absolute_src(n.module) if RUNTIME_SPELLINGS else None
                    if src is not None:
                        link(_targets(pkg, m, src, [a.name for a in n.names]))
                    else:
                        ext[m].add(n.module.split(".")[0])
                elif isinstance(n, ast.Import):
                    for a in n.names:
                        src = _absolute_src(a.name) if RUNTIME_SPELLINGS else None
                        if src:
                            link([(src, "")] if src in pkg.mods else [])
                        else:
                            ext[m].add(a.name.split(".")[0])
            elif isinstance(n, ast.Call) and RUNTIME_SPELLINGS and not runs_late \
                    and (t := _import_module_target(m, n)) is not None:
                link([(t, "")] if t in pkg.mods else [])
            if not PRIVATE_ATTRS:
                continue
            if isinstance(n, ast.Attribute) and _private(n.attr) and (t := _module_of(n.value, alias, m)):
                crossings.add(f"{m} -> {t}.{n.attr}")
            elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) \
                    and n.func.id in ("getattr", "hasattr", "setattr", "delattr") and len(n.args) >= 2 \
                    and (t := _module_of(n.args[0], alias, m)):
                key = _folded(n.args[1])
                if isinstance(key, str) and _private(key):
                    crossings.add(f"{m} -> {t}.{key}")
            elif isinstance(n, ast.Subscript) and isinstance(key := _folded(n.slice), str) and _private(key):
                v = n.value  # vars(m)["_x"], m.__dict__["_x"]
                t = _module_of(v.args[0], alias, m) if isinstance(v, ast.Call) and isinstance(v.func, ast.Name) \
                    and v.func.id == "vars" and v.args else \
                    _module_of(v.value, alias, m) if isinstance(v, ast.Attribute) and v.attr == "__dict__" else None
                if t:
                    crossings.add(f"{m} -> {t}.{key}")
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
    or a name a string annotation's expression spells)."""
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
        for n in C.walk(mod.tree):  # a string annotation reads the names its expression spells
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and len(n.value) < 200:
                try:
                    read |= {x.id for x in ast.walk(ast.parse(n.value, mode="eval")) if isinstance(x, ast.Name)}
                except SyntaxError:
                    pass
        out += [f"{m}: {name}" for name in sorted(bound) if name not in read]
    return out


def measure(root: Path) -> dict:
    t0 = time.perf_counter()
    pkg = C.load(str(root))
    edges, ext, crossings = graph(pkg)
    rank = {m: max([LAYERS[x] for x in ext[m] if x in LAYERS], default=0) for m in pkg.mods}
    violations = sorted(f"{m} ({rank[m]} -> {r})" for m in pkg.mods
                        for r in {rank[n] for n in closure(edges, m)} if r > rank[m])
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
