"""layering: package modules that reach a heavier layer than their own, and private names that cross a
module boundary (R10-ARCHSCORE-COVERAGE item 1; ARCH2-s4, round 10).

The layers, lowest first: a PURE module (it imports neither boundary), the SOLVER layer (it imports scipy),
the GLUE layer (it imports Home Assistant). A module's layer is the highest boundary it imports itself.
An import may go down or across, never up: glue may use the solver and pure code, the solver may use pure
code. Over the package's import graph -- a relative import at ANY scope is an edge, a function's
``from .optimizer import f`` included, because a lazy import is the same coupling paid later (counter
C17); an import the runtime never runs is no edge. That is the whole of a positive ``if TYPE_CHECKING:``
``body``, and no more: the section's ``else`` runs, ``not TYPE_CHECKING`` is true away from a type
checker, and a ``TYPE_CHECKING`` the module rebinds itself is not typing's --

  layer_violations   (module, layer) pairs where a module reaches, through other package modules, a layer
                     above its own: a pure module that cannot load without scipy (``quiet_windows`` and
                     ``silent_mode`` reached the optimizer for its private ``_utc_step_starts``) or without
                     Home Assistant, or a solver module that drags in Home Assistant. Per pair, so freeing a
                     pure module of the solver counts while it still reaches the glue. A decomposition does
                     not move it: a module extracted from the glue that imports Home Assistant is glue.
  private_cross_module   distinct private names (one leading underscore) of one package module named by
                     another: ``from .m import _x``, ``m._x`` through a module binding,
                     ``getattr(m, "_x")``, and ``_x`` read off a resolved ``import_module`` call (counter
                     C18: the attribute spellings are the same reach).
  unused_boundary_imports  (gate-only, counter C19) imports of a boundary whose names the module never reads:
                     a module would otherwise climb a layer, and leave its violation, by an import that does
                     nothing (attempt 23).

The reach is the reach whatever syntax spells it, so the graph follows every spelling of an import that
runs: ``from <pkg>.m import _x``, the absolute self-import, is the edge ``from .m import _x`` is (attempt
27); a constant-name ``import_module("...")``, relative and anchored on ``__package__`` too, is that
module's edge, and the private read off the call is that crossing (attempt 26). A name COMPUTED at runtime
is the one form no static read follows; the package's is ``__init__``'s platform loader.

LAYERS is a design choice, stated: Home Assistant is the integration's glue edge (model, optimizer and
learner modules take no ``homeassistant`` import, fixer.md step 17), and scipy is the solver's dependency.
numpy is used by nearly every module and is no boundary.
"""
from __future__ import annotations

import ast
import time
from pathlib import Path

from . import common as C

#: boundary -> layer rank; a module's rank is the highest it imports, 0 for a pure module.
LAYERS = {"scipy": 1, "homeassistant": 2}
#: the package's own absolute dotted prefix: an import naming it is a package edge, not an external root.
SELF = C.PKG_REL.replace("/", ".")
#: Counter C17: a function-scope import is an edge. ``vector.py`` switches it off.
ALL_SCOPES = True
#: Counter C18: a private name read through a module binding is a crossing. ``vector.py`` switches it off.
PRIVATE_ATTRS = True
#: Counter C19: an unread boundary import is a tripwire. ``vector.py`` switches it off.
UNUSED_IMPORTS = True


def _private(name: str) -> bool:
    return name.startswith("_") and not name.startswith("__")


def _self_module(dotted: str) -> str | None:
    """``dotted`` as a package-relative module name, ``""`` for the package itself, None when it names
    something this package does not own."""
    if dotted == SELF:
        return ""
    return dotted[len(SELF) + 1:] if dotted.startswith(SELF + ".") else None


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


def _targets(pkg: C.Pkg, mod: str, node: ast.ImportFrom) -> list[tuple[str, str]]:
    """(target module, imported name) for each name of a from-import; the name is ``""`` when the name
    is itself a module. An absolute import of this package resolves as the relative one does -- the
    prefix is stripped -- so ``from <pkg>.optimizer import _x`` reaches ``optimizer`` (attempt 27)."""
    if node.level:
        base = mod.split(".")[:-1]
        base = base[:len(base) - node.level + 1]
        src = ".".join(base + ([node.module] if node.module else []))
    else:
        src = _self_module(node.module) if node.module else None
        if src is None:
            return []
    out = []
    for a in node.names:
        full = f"{src}.{a.name}" if src else a.name
        if full in pkg.mods:
            out.append((full, ""))
        elif (src or "__init__") in pkg.mods:
            out.append((src or "__init__", a.name))
    return out


def _roots(node: ast.Import | ast.ImportFrom) -> set[str]:
    """The external root packages an import names: a name of this package is no external root, however
    it is spelled (attempt 27)."""
    if isinstance(node, ast.Import):
        return {a.name.split(".")[0] for a in node.names if _self_module(a.name) is None}
    if node.level or not node.module or _self_module(node.module) is not None:
        return set()
    return {node.module.split(".")[0]}


def _package_of(mod: str) -> str:
    """``__package__`` for a package module: the module's parent, the package itself at the top."""
    parent = mod.rpartition(".")[0]
    return f"{SELF}.{parent}" if parent else SELF


def _dynamic_name(mod: C.Mod, node: ast.Call) -> str | None:
    """The absolute dotted module a constant-name ``import_module``/``__import__`` call imports, or
    None where the call is not one of those, takes its name from a computation, or is relative with no
    static anchor -- ``import_module`` requires that argument, and without it the call loads nothing
    (attempt 26)."""
    f = node.func
    if isinstance(f, ast.Name):
        imp = mod.imports.get(f.id)
        named = f.id == "__import__" or bool(
            imp and imp[0] == "ext" and imp[1] in ("importlib.import_module", "__import__"))
    elif isinstance(f, ast.Attribute) and f.attr in ("import_module", "__import__") \
            and isinstance(f.value, ast.Name):
        imp = mod.imports.get(f.value.id)
        named = f.value.id == "importlib" or bool(imp and imp[0] == "ext" and imp[1] == "importlib")
    else:
        named = False
    if not named or not node.args:
        return None
    first = node.args[0]
    if not (isinstance(first, ast.Constant) and isinstance(first.value, str)):
        return None
    name = first.value
    if not name.startswith("."):
        return name
    anchor = node.args[1] if len(node.args) > 1 else \
        next((k.value for k in node.keywords if k.arg == "package"), None)
    if isinstance(anchor, ast.Constant) and isinstance(anchor.value, str):
        base = anchor.value
    elif isinstance(anchor, ast.Name) and anchor.id == "__package__":
        base = _package_of(mod.name)
    else:
        return None
    rest = name.lstrip(".")
    parts = base.split(".")
    parts = parts[:len(parts) - (len(name) - len(rest)) + 1]
    return ".".join(parts + ([rest] if rest else []))


def _dynamic_target(pkg: C.Pkg, name: str) -> str | None:
    """The package module a resolved dynamic import reaches, or None for a name outside the package."""
    rel = _self_module(name)
    if rel is None:
        return None
    target = rel or "__init__"
    return target if target in pkg.mods else None


def graph(pkg: C.Pkg) -> tuple[dict[str, set[str]], dict[str, set[str]], set[str]]:
    """(package edges, external roots imported, distinct private crossings ``"m -> n._x"``): a
    name read three times from one module is one crossing, the unit of coupling."""
    edges: dict[str, set[str]] = {m: set() for m in pkg.mods}
    ext: dict[str, set[str]] = {m: set() for m in pkg.mods}
    crossings: set[str] = set()

    def cross(m: str, target: str, name: str) -> None:
        if target == m:
            return
        edges[m].add(target)
        if _private(name or target.rsplit(".", 1)[-1]):
            crossings.add(f"{m} -> {target}.{name}" if name else f"{m} -> {target}")

    for m, mod in pkg.mods.items():
        live = None if ALL_SCOPES else _module_level(mod.tree)
        modalias = {k: v[1] for k, v in mod.imports.items() if v[0] == "mod" and v[1] != m}
        # id of each constant-name dynamic import's call -> the module it names. The walk reaches a call
        # before the attribute read off it, so the private arm resolves from this table, not from order.
        dynamic = {}
        for n in C.walk(mod.tree):
            if isinstance(n, ast.Call) and (name := _dynamic_name(mod, n)) is not None:
                dynamic[id(n)] = name
        for n in C.walk(mod.tree):
            if isinstance(n, (ast.Import, ast.ImportFrom)):
                if id(n) in pkg.type_checking_imports or (live is not None and id(n) not in live):
                    continue
                if isinstance(n, ast.ImportFrom):
                    for target, name in _targets(pkg, m, n):
                        cross(m, target, name)
                ext[m] |= _roots(n)
            elif isinstance(n, ast.Call) and id(n) in dynamic:
                target = _dynamic_target(pkg, dynamic[id(n)])
                if target is not None:
                    cross(m, target, "")
                else:
                    ext[m].add(dynamic[id(n)].split(".")[0])
            elif PRIVATE_ATTRS and isinstance(n, ast.Attribute) and _private(n.attr) \
                    and isinstance(n.value, ast.Call) and id(n.value) in dynamic \
                    and (t := _dynamic_target(pkg, dynamic[id(n.value)])) is not None:
                cross(m, t, n.attr)
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
