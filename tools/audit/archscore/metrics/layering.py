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
runs, and every read that reaches a module through one: ``from <pkg>.m import _x``, the absolute
self-import, is the edge ``from .m import _x`` is (attempt 27); so is the plain dotted ``import <pkg>.m``,
whose statement binds the whole path with an ``as`` and only its root without one, and ``from <pkg>
import m as _o``, whose module binding a private read off ``_o`` crosses through like any other
(attempts 28-30); a constant-name ``import_module``, relative and anchored on ``__package__`` too, is
that module's edge whether the name is passed positionally, as the ``name`` keyword, or held by a
module-level string constant, and the private read off the call is that crossing (attempts 26, 31, 37).
The name's relation to this package is one predicate at a dot boundary: a DESCENDANT of it
(``<pkg>.m``) loads a module of ours, and a strict PREFIX of it -- ``custom_components``, the namespace
the package is nested in -- reaches one where the read dots back down into it, so ``import
custom_components as _cc`` with ``_cc.<pkg>.optimizer._x`` is the edge and the crossing the relative
spelling is (attempts 32-35); a read through an attribute chain, and through ``getattr``, names the
same module (attempt 36). The EDGE belongs to the module a read resolves to, whether the name read off it
is public or private -- the edge is the layer coupling, and C18 prices only the private names -- and it is
added once, on the node a dotted chain ENDS on, because every step of a chain before it names the same
module and would take the edge a second time (attempts 38, 39). A name COMPUTED at runtime is the one form no static read follows; the package's is
``__init__``'s platform loader.

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


def _relative(path: str) -> str | None:
    """``path`` as a package-relative module name: ``""`` for the package itself, the tail for a module
    below it, None for anything else. A strict PREFIX of the package -- ``custom_components``, the
    namespace the package is nested in -- names no module of ours on its own (attempt 32)."""
    if path == SELF:
        return ""
    return path[len(SELF) + 1:] if path.startswith(SELF + ".") else None


def _namespaced(path: str) -> bool:
    """Is ``path`` in this package's namespace: the package, a module below it, or a strict PREFIX of it.
    Ancestor and descendant are one predicate, derived from SELF at a dot boundary, because an import
    naming either can reach this package: the descendant loads a module of ours, the ancestor reaches
    one where a read dots down into it (attempts 28, 32-35)."""
    return path == SELF or path.startswith(SELF + ".") or SELF.startswith(path + ".")


def _pkg_module(pkg: C.Pkg, path: str) -> str | None:
    """The module of this package an absolute dotted path names -- ``__init__`` for the package itself,
    None for a path this package has no module at."""
    rel = _relative(path)
    if rel is None:
        return None
    key = rel or "__init__"
    return key if key in pkg.mods else None


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


def _from_names(pkg: C.Pkg, mod: str, node: ast.ImportFrom) -> list[tuple[str, str, str]]:
    """(bound name, absolute dotted path, imported name) for each name of a from-import; the imported
    name is ``""`` when the name is itself a module of this package. A relative import resolves to the
    path the absolute one names, and a source anywhere in this package's namespace -- the package, one
    of its modules, or the namespace it is nested in -- resolves the same way, so ``from <pkg>.optimizer
    import _x``, ``from <pkg> import optimizer as _o`` and ``from <ns> import <pkg>`` all reach what the
    relative spelling reaches (attempts 27, 30, 33, 34)."""
    if node.level:
        base = mod.split(".")[:-1]
        base = base[:len(base) - node.level + 1]
        src = ".".join(base + ([node.module] if node.module else []))
        path = f"{SELF}.{src}" if src else SELF
    elif node.module and _namespaced(node.module):
        path = node.module
    else:
        return []
    out = []
    for a in node.names:
        if _pkg_module(pkg, f"{path}.{a.name}") is not None:
            out.append((a.asname or a.name, f"{path}.{a.name}", ""))
        elif _pkg_module(pkg, path) is not None:
            out.append((a.asname or a.name, path, a.name))
    return out


def _roots(node: ast.Import | ast.ImportFrom) -> set[str]:
    """The external root packages an import names: a name of this package is no external root, however
    it is spelled (attempt 27)."""
    if isinstance(node, ast.Import):
        return {a.name.split(".")[0] for a in node.names if _relative(a.name) is None}
    if node.level or not node.module or _relative(node.module) is not None:
        return set()
    return {node.module.split(".")[0]}


def _name_bindings(pkg: C.Pkg, mod: C.Mod, live: set[int] | None) -> dict[str, str]:
    """Local name -> the absolute dotted path of the module it binds, for every import this module runs
    that names something in this package's namespace: the relative ``from . import m``, the absolute
    ``from <pkg> import m as x`` -- which ``Pkg.imports`` files as an external name, so no ``modalias``
    held it (attempt 30) -- the plain dotted ``import <pkg>.m``, whose statement binds the whole path
    with an ``as`` and only its root without one (attempts 28, 29), and the same spelt from the
    namespace the package is nested in, ``import custom_components as _cc`` (attempts 32, 35)."""
    out: dict[str, str] = {}
    for n in C.walk(mod.tree):
        if not isinstance(n, (ast.Import, ast.ImportFrom)):
            continue
        if id(n) in pkg.type_checking_imports or (live is not None and id(n) not in live):
            continue
        if isinstance(n, ast.Import):
            for a in n.names:
                if _namespaced(a.name):
                    # ``import a.b.c`` binds only ``a``; ``import a.b.c as x`` binds the whole path.
                    out[a.asname or a.name.split(".")[0]] = a.name if a.asname else a.name.split(".")[0]
        else:
            for bound, path, name in _from_names(pkg, mod.name, n):
                if not name:
                    out[bound] = path
    return out


def _dotted_path(modbind: dict[str, str], node: ast.AST) -> str | None:
    """The dotted path an expression spells when every step of it is statically readable: a name an
    import of this module bound, an attribute of one, and a ``getattr``/``hasattr``/``setattr`` whose
    name is a constant string. None where a step is computed (attempt 36)."""
    if isinstance(node, ast.Name):
        return modbind.get(node.id)
    if isinstance(node, ast.Attribute):
        base = _dotted_path(modbind, node.value)
        return f"{base}.{node.attr}" if base is not None else None
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
            and node.func.id in ("getattr", "hasattr", "setattr") and len(node.args) >= 2 \
            and isinstance(node.args[1], ast.Constant) and isinstance(node.args[1].value, str):
        base = _dotted_path(modbind, node.args[0])
        return f"{base}.{node.args[1].value}" if base is not None else None
    return None


def _ends_chain(parent: dict[int, ast.AST], node: ast.AST) -> bool:
    """Is this the node a dotted chain ENDS on? An attribute that is another attribute's ``value`` is a
    step of that chain, not a read of its own: a read anywhere in it takes the edge for the module the
    WHOLE chain names, so the edge is added once, on the outermost node (round-4 review)."""
    p = parent.get(id(node))
    return not (isinstance(p, ast.Attribute) and p.value is node)


def _reached(pkg: C.Pkg, modbind: dict[str, str], m: str, node: ast.AST) -> tuple[str, str] | None:
    """(module, the name read off it) for the OUTERMOST point of an expression's dotted chain whose
    receiver resolves to a module of this package, searching outside in: ``a.b.c.d`` where ``a.b`` is a
    module takes the edge for ``a.b`` with ``c`` the name read off it, so a chain that walks on PAST the
    module -- ``_cc.<pkg>.optimizer._utc_step_starts.__call__`` -- still takes it (round-5 review).
    None where no receiver in the chain resolves to a module of ours, and never ``m`` itself."""
    e: ast.AST = node
    while True:
        if isinstance(e, ast.Attribute):
            path = _dotted_path(modbind, e.value)
            target = _pkg_module(pkg, path) if path is not None else None
            if target is not None and target != m:
                return target, e.attr
            e = e.value
        elif isinstance(e, ast.Call) and isinstance(e.func, ast.Name) \
                and e.func.id in ("getattr", "hasattr", "setattr") and len(e.args) >= 2 \
                and isinstance(e.args[1], ast.Constant) and isinstance(e.args[1].value, str):
            path = _dotted_path(modbind, e.args[0])
            target = _pkg_module(pkg, path) if path is not None else None
            if target is not None and target != m:
                return target, e.args[1].value
            e = e.args[0]
        else:
            return None


def _package_of(mod: str) -> str:
    """``__package__`` for a package module: the module's parent, the package itself at the top."""
    parent = mod.rpartition(".")[0]
    return f"{SELF}.{parent}" if parent else SELF


def _module_const(mod: C.Mod, node: ast.AST) -> ast.Constant | None:
    """The string constant a module-level name holds, or None: ``_MOD = ".optimizer"`` is statically
    readable, so an ``import_module`` naming it is the constant-name call it spells, in either
    module-level spelling: ``_MOD = "..."`` or ``_MOD: str = "..."`` (attempts 37, 40). A name rebound,
    a name that is not a module-level assignment, and one holding anything but a string are all None."""
    name = node.id if isinstance(node, ast.Name) else None
    assign = mod.tops.get(name) if name is not None else None
    if not isinstance(assign, (ast.Assign, ast.AnnAssign)):
        return None
    targets = assign.targets if isinstance(assign, ast.Assign) else [assign.target]
    if len(targets) != 1 or not isinstance(targets[0], ast.Name):
        return None
    if isinstance(assign.value, ast.Constant) and isinstance(assign.value.value, str):
        return assign.value
    return None


def _dynamic_name(mod: C.Mod, node: ast.Call) -> str | None:
    """The absolute dotted module a constant-name ``import_module``/``__import__`` call imports, or
    None where the call is not one of those, takes its name from a computation, or is relative with no
    static anchor -- ``import_module`` requires that argument, and without it the call loads nothing
    (attempt 26). ``import_module``'s first parameter is named ``name`` and its relative anchor
    ``package``, so each is read as a keyword as well as positionally (attempt 31), and a name held by
    a module-level string constant is the constant it holds (attempt 37)."""
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
    if not named:
        return None
    first = node.args[0] if node.args else \
        next((k.value for k in node.keywords if k.arg == "name"), None)
    if isinstance(first, ast.Name) and (const := _module_const(mod, first)) is not None:
        first = const
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


def graph(pkg: C.Pkg) -> tuple[dict[str, set[str]], dict[str, set[str]], set[str]]:
    """(package edges, external roots imported, distinct private crossings ``"m -> n._x"``): a
    name read three times from one module is one crossing, the unit of coupling."""
    edges: dict[str, set[str]] = {m: set() for m in pkg.mods}
    ext: dict[str, set[str]] = {m: set() for m in pkg.mods}
    crossings: set[str] = set()

    def cross(m: str, target: str, name: str, private: bool = True) -> None:
        """The edge, and -- when the name it is read by is private and C18 is on -- the crossing. The
        two are separate on purpose: the edge is the LAYER coupling, which a public name takes as much
        as a private one, and C18 prices only the private names (round-4 review)."""
        if target == m:
            return
        edges[m].add(target)
        if private and _private(name or target.rsplit(".", 1)[-1]):
            crossings.add(f"{m} -> {target}.{name}" if name else f"{m} -> {target}")

    for m, mod in pkg.mods.items():
        live = None if ALL_SCOPES else _module_level(mod.tree)
        modalias = _name_bindings(pkg, mod, live)
        # id of each node -> its parent: a dotted chain's intermediate nodes are steps, not reads, and
        # only the node the chain ENDS on takes the edge (round-4 review).
        parent = {id(c): n for n in C.walk(mod.tree) for c in ast.iter_child_nodes(n)}
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
                    for _bound, path, name in _from_names(pkg, m, n):
                        if (target := _pkg_module(pkg, path)) is not None:
                            cross(m, target, name)
                else:
                    for a in n.names:
                        if (target := _pkg_module(pkg, a.name)) is not None:
                            cross(m, target, "")
                ext[m] |= _roots(n)
            elif isinstance(n, ast.Call) and id(n) in dynamic:
                target = _pkg_module(pkg, dynamic[id(n)])
                if target is not None:
                    cross(m, target, "")
                else:
                    ext[m].add(dynamic[id(n)].split(".")[0])
            elif _ends_chain(parent, n) and isinstance(n, ast.Attribute) \
                    and isinstance(n.value, ast.Call) and id(n.value) in dynamic \
                    and (t := _pkg_module(pkg, dynamic[id(n.value)])) is not None:
                cross(m, t, n.attr, private=PRIVATE_ATTRS)
            elif _ends_chain(parent, n) and isinstance(n, ast.Attribute) \
                    and (hit := _reached(pkg, modalias, m, n)) is not None:
                cross(m, hit[0], hit[1], private=PRIVATE_ATTRS)
            elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) \
                    and n.func.id in ("getattr", "hasattr", "setattr") and len(n.args) >= 2 \
                    and isinstance(n.args[1], ast.Constant) and isinstance(n.args[1].value, str) \
                    and (hit := _reached(pkg, modalias, m, n)) is not None:
                cross(m, hit[0], hit[1], private=PRIVATE_ATTRS)
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
