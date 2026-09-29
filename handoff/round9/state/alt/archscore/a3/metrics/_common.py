"""Shared static model of the package for the a3 architecture metrics.

Stdlib only (``ast``). Everything is derived from the source tree under
``<root>/custom_components/heatpump_optimizer``; nothing is imported or run.
The helpers follow ``tests/structure.py``'s style: small pure functions over
parsed trees, stable ordering, file:line evidence.

The one non-trivial piece is the ROLE engine (``propagate``), shared by
hub_solve_writes, shared_inplace_writes and private_reach. A role says what an
expression evaluates to, as far as the coordinator is concerned:

  ("coord",)              the coordinator instance (``self`` in its class,
                          ``getattr(self, "_ctx", self)``, ``self._ctx``,
                          ``entry.runtime_data``, a ``coord`` parameter ...)
  ("obj", path, cls)      an object reached FROM the coordinator along
                          ``path`` (attribute names, ``"[]"`` for an item),
                          ``cls`` its package class when the AST can type it
  ("self", cls)           a method's own ``self`` in a non-coordinator class

Roles flow into callees through arguments (context-insensitive: a parameter's
role set is the union over every analysed call site) and through local
aliases (flow-insensitive: ``x = self._a`` makes ``x`` an alias everywhere in
that function). That is the whole abstraction; its blind spots are listed in
new_metrics.md.
"""
from __future__ import annotations

import ast
from collections import defaultdict
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

PKG_REL = "custom_components/heatpump_optimizer"
COORD_CLASS = "HeatPumpOptimizerCoordinator"
COORD_MODULE = "coordinator"
HUBS = ("_opt_config", "_thermal_params", "_current_state")
CTX_ATTR = "_ctx"
MAX_PATH = 4

# Mutating container methods. Applied only when the receiver's class is
# unknown (a dict/list/set/deque) or is a package class that does not define
# the name itself (then it is a real method call and is resolved instead).
MUTATORS = frozenset({
    "append", "extend", "insert", "remove", "pop", "popitem", "clear",
    "update", "setdefault", "add", "discard", "sort", "reverse",
    "appendleft", "extendleft", "popleft", "difference_update",
    "intersection_update", "symmetric_difference_update", "__setitem__",
    "__delitem__",
})

# Names Home Assistant reaches by convention (tests/structure.py's lists).
HA_CONVENTION_NAMES = frozenset({
    "async_setup", "async_setup_entry", "async_unload_entry",
    "async_migrate_entry", "async_get_options_flow", "async_remove_entry",
    "async_remove_config_entry_device", "async_get_config_entry_diagnostics",
    "async_redact_data", "async_get_engine", "async_get_config_flow_dialect",
    "async_create_fix_flow", "CONFIG_SCHEMA", "PARALLEL_UPDATES", "PLATFORMS",
})
HA_CONVENTION_METHODS = frozenset({
    "_async_update_data", "async_press", "async_set_hvac_mode",
    "async_set_preset_mode", "async_set_temperature", "async_set_value",
    "async_turn_on", "async_turn_off", "is_on", "current_temperature",
    "hvac_action", "native_value", "extra_state_attributes",
    "async_get_options_flow",
})


def is_ha_method(name: str) -> bool:
    return name in HA_CONVENTION_METHODS or name.startswith("async_step_")


# ---------------------------------------------------------------------------
# the parsed package


@dataclass
class Mod:
    name: str
    path: Path
    rel: str
    tree: ast.Module
    lines: list[str]
    # local name -> ("mod", modname) | ("sym", modname, symbol) | ("ext", dotted)
    imports: dict[str, tuple] = field(default_factory=dict)
    tops: dict[str, ast.AST] = field(default_factory=dict)


@dataclass
class Cls:
    key: tuple[str, str]
    node: ast.ClassDef
    methods: dict[str, ast.AST]
    base_keys: list[tuple[str, str]]
    ext_bases: list[str]


@dataclass
class Fn:
    qual: str
    mod: str
    cls: tuple[str, str] | None
    node: ast.AST
    params: list[str]
    kind: str  # "function" | "method" | "staticmethod" | "classmethod"

    @property
    def name(self) -> str:
        return self.node.name

    @property
    def is_async(self) -> bool:
        return isinstance(self.node, ast.AsyncFunctionDef)


_WALK: dict[int, tuple[ast.AST, list]] = {}


def walk(node: ast.AST) -> list:
    """``ast.walk`` as a memoized list (the trees are never mutated)."""
    hit = _WALK.get(id(node))
    if hit is None or hit[0] is not node:
        out = [node]
        i = 0
        AST = ast.AST
        while i < len(out):
            n = out[i]
            i += 1
            for f in n._fields:
                v = getattr(n, f, None)
                if v.__class__ is list:
                    for x in v:
                        if isinstance(x, AST):
                            out.append(x)
                elif isinstance(v, AST):
                    out.append(v)
        hit = (node, out)
        _WALK[id(node)] = hit
    return hit[1]


def _decorator_names(node: ast.AST) -> set[str]:
    out = set()
    for d in getattr(node, "decorator_list", []):
        if isinstance(d, ast.Name):
            out.add(d.id)
        elif isinstance(d, ast.Attribute):
            out.add(d.attr)
        elif isinstance(d, ast.Call):
            f = d.func
            out.add(f.id if isinstance(f, ast.Name) else getattr(f, "attr", ""))
    return out


def is_property(node: ast.AST) -> bool:
    names = _decorator_names(node)
    return bool(names & {"property", "cached_property", "setter", "getter", "deleter"})


def _in_type_checking(tree: ast.Module) -> set[int]:
    """ids of Import nodes under ``if TYPE_CHECKING:``."""
    out: set[int] = set()
    for n in walk(tree):
        if isinstance(n, ast.If) and ast.unparse(n.test).endswith("TYPE_CHECKING"):
            for m in walk(n):
                if isinstance(m, (ast.Import, ast.ImportFrom)):
                    out.add(id(m))
    return out


class Pkg:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.dir = self.root / PKG_REL
        self.mods: dict[str, Mod] = {}
        for path in sorted(self.dir.rglob("*.py")):
            rel = path.relative_to(self.root).as_posix()
            name = path.relative_to(self.dir).as_posix()[:-3].replace("/", ".")
            src = path.read_text()
            self.mods[name] = Mod(name, path, rel, ast.parse(src, filename=rel), src.splitlines())
        self.type_checking_imports: set[int] = set()
        for m in self.mods.values():
            self.type_checking_imports |= _in_type_checking(m.tree)
            self._index_module(m)
        self.classes: dict[tuple[str, str], Cls] = {}
        self.funcs: dict[str, Fn] = {}
        for m in self.mods.values():
            for node in m.tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    self._add_fn(m.name, None, node)
                elif isinstance(node, ast.ClassDef):
                    self._add_cls(m, node)
        for c in self.classes.values():
            for b in c.node.bases:
                r = self.resolve_expr_static(c.key[0], b)
                if r and r[0] == "class":
                    c.base_keys.append(r[1])
                else:
                    c.ext_bases.append(ast.unparse(b))
        # ``other_module.hook = local_function`` at import time (dependency
        # injection, e.g. ``setpoint_check.dhw_gated = dhw_gated``): a call of
        # ``hook`` inside other_module reaches local_function.
        self.injected: dict[tuple[str, str], str] = {}
        for m in self.mods.values():
            for node in m.tree.body:
                if isinstance(node, ast.Assign) and len(node.targets) == 1:
                    t = node.targets[0]
                    if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name):
                        imp = m.imports.get(t.value.id)
                        r = self.resolve_expr_static(m.name, node.value)
                        if imp and imp[0] == "mod" and r and r[0] == "func":
                            self.injected[(imp[1], t.attr)] = r[1]
        self._attr_types: dict[tuple[str, str], dict[str, tuple[str, str]]] = {}
        self._subs: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)
        for c in self.classes.values():
            for b in c.base_keys:
                self._subs[b].append(c.key)

    # -- indexing ----------------------------------------------------------
    def _index_module(self, m: Mod) -> None:
        pkg_parts = m.name.split(".")[:-1]
        for node in walk(m.tree):
            if isinstance(node, ast.ImportFrom):
                if node.level == 0:
                    for a in node.names:
                        m.imports.setdefault(a.asname or a.name, ("ext", f"{node.module}.{a.name}"))
                    continue
                base = pkg_parts[: len(pkg_parts) - node.level + 1]
                src = ".".join(base + [node.module] if node.module else base)
                for a in node.names:
                    bound = a.asname or a.name
                    target = f"{src}.{a.name}" if src else a.name
                    if target in self.mods:
                        m.imports[bound] = ("mod", target)
                    else:
                        m.imports[bound] = ("sym", src or "__init__", a.name)
            elif isinstance(node, ast.Import):
                for a in node.names:
                    m.imports.setdefault(a.asname or a.name.split(".")[0], ("ext", a.name))
        for node in m.tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                m.tops[node.name] = node
            else:
                for t in getattr(node, "targets", [getattr(node, "target", None)]):
                    if isinstance(t, ast.Name):
                        m.tops.setdefault(t.id, node)

    def _add_fn(self, mod: str, cls: tuple[str, str] | None, node: ast.AST) -> Fn:
        decos = _decorator_names(node)
        kind = "function"
        if cls is not None:
            kind = "staticmethod" if "staticmethod" in decos else "classmethod" if "classmethod" in decos else "method"
        a = node.args
        params = [p.arg for p in a.posonlyargs + a.args] + [p.arg for p in a.kwonlyargs]
        qual = f"{mod}:{cls[1]}.{node.name}" if cls else f"{mod}:{node.name}"
        if qual in self.funcs:  # property setter / overload: keep both under distinct quals
            qual = f"{qual}@{node.lineno}"
        fn = Fn(qual, mod, cls, node, params, kind)
        self.funcs[qual] = fn
        return fn

    def _add_cls(self, m: Mod, node: ast.ClassDef) -> None:
        key = (m.name, node.name)
        methods: dict[str, ast.AST] = {}
        for s in node.body:
            if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn = self._add_fn(m.name, key, s)
                methods.setdefault(s.name, fn.qual)
        self.classes[key] = Cls(key, node, methods, [], [])

    # -- resolution --------------------------------------------------------
    def resolve_name(self, mod: str, name: str, _seen: frozenset = frozenset()) -> tuple | None:
        """What a bare module-scope name refers to: ("func", qual) |
        ("class", key) | ("mod", modname) | ("var", (mod, name)) | None."""
        if (mod, name) in _seen or mod not in self.mods:
            return None
        m = self.mods[mod]
        node = m.tops.get(name)
        if node is not None:
            if isinstance(node, ast.ClassDef):
                return ("class", (mod, name))
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return ("func", f"{mod}:{name}")
            return ("var", (mod, name))
        imp = m.imports.get(name)
        if imp is None:
            return None
        if imp[0] == "mod":
            return ("mod", imp[1])
        if imp[0] == "sym":
            return self.resolve_name(imp[1], imp[2], _seen | {(mod, name)})
        return None

    def resolve_expr_static(self, mod: str, e: ast.AST) -> tuple | None:
        """Resolve ``Name`` / ``module.Name`` without any role information."""
        if isinstance(e, ast.Name):
            return self.resolve_name(mod, e.id)
        if isinstance(e, ast.Attribute):
            base = self.resolve_expr_static(mod, e.value)
            if base and base[0] == "mod":
                return self.resolve_name(base[1], e.attr)
            if base and base[0] == "class":
                q = self.member(base[1], e.attr)
                if q:
                    return ("func", q)
        return None

    def mro(self, key: tuple[str, str]) -> list[tuple[str, str]]:
        out, todo = [], [key]
        while todo:
            k = todo.pop(0)
            if k in out or k not in self.classes:
                continue
            out.append(k)
            todo.extend(self.classes[k].base_keys)
        return out

    def subclasses(self, key: tuple[str, str]) -> list[tuple[str, str]]:
        out, todo = [], list(self._subs.get(key, []))
        while todo:
            k = todo.pop()
            if k not in out:
                out.append(k)
                todo.extend(self._subs.get(k, []))
        return out

    def member(self, key: tuple[str, str], name: str) -> str | None:
        for k in self.mro(key):
            q = self.classes[k].methods.get(name)
            if q:
                return q
        return None

    def attr_types(self, key: tuple[str, str]) -> dict[str, tuple[str, str]]:
        """``self.A = K(...)`` / ``self.A: K`` anywhere in the class -> {A: K}."""
        if key in self._attr_types:
            return self._attr_types[key]
        out: dict[str, tuple[str, str]] = {}
        mod = key[0]
        for k in self.mro(key):
            for n in walk(self.classes[k].node):
                tgt = val = ann = None
                if isinstance(n, ast.Assign) and len(n.targets) == 1:
                    tgt, val = n.targets[0], n.value
                elif isinstance(n, ast.AnnAssign):
                    tgt, val, ann = n.target, n.value, n.annotation
                if not (isinstance(tgt, ast.Attribute) and isinstance(tgt.value, ast.Name) and tgt.value.id == "self"):
                    continue
                r = None
                if isinstance(val, ast.Call):
                    r = self.resolve_expr_static(mod, val.func)
                    if r and r[0] == "func":  # K.from_dict(...) classmethod constructor
                        fn = self.funcs[r[1]]
                        r = ("class", fn.cls) if fn.cls and fn.kind == "classmethod" else None
                if (r is None or r[0] != "class") and ann is not None:
                    r = self.resolve_expr_static(mod, ann)
                if r and r[0] == "class":
                    out.setdefault(tgt.attr, r[1])
        self._attr_types[key] = out
        return out

    @property
    def coord_key(self) -> tuple[str, str]:
        return (COORD_MODULE, COORD_CLASS)

    def fn_of_line(self, mod: str, lineno: int) -> Fn | None:
        best = None
        for fn in self.funcs.values():
            if fn.mod == mod and fn.node.lineno <= lineno <= fn.node.end_lineno:
                if best is None or fn.node.lineno > best.node.lineno:
                    best = fn
        return best


@lru_cache(maxsize=4)
def load(root: str) -> Pkg:
    return Pkg(Path(root))


# ---------------------------------------------------------------------------
# the role engine

COORD = ("coord",)
# By the package's naming convention a name ``coord`` / ``coordinator`` holds
# the coordinator (the m3 enumerator's rule); a binding the engine can see
# takes precedence.
COORD_NAMES = frozenset({"coord", "coordinator"})
EMPTY: frozenset = frozenset()


def is_coord_annotation(ann: ast.AST | None) -> bool:
    if ann is None:
        return False
    s = ast.unparse(ann)
    return "Coordinator" in s or s.strip("'\"").endswith("Coord")


_ENGINES: dict[tuple, "Engine"] = {}


def engine(pkg: Pkg, seed_params: bool = True) -> "Engine":
    """One Engine per (package, seeding) -- run_all shares it across metrics."""
    key = (id(pkg), seed_params)
    if key not in _ENGINES or _ENGINES[key].pkg is not pkg:
        _ENGINES[key] = Engine(pkg, seed_params=seed_params)
    return _ENGINES[key]


class Engine:
    """Role propagation over the package (see the module docstring)."""

    def __init__(self, pkg: Pkg, *, seed_params: bool = True):
        self.pkg = pkg
        self.seed_params = seed_params
        self.coord_attr_types = pkg.attr_types(pkg.coord_key) if pkg.coord_key in pkg.classes else {}
        self.alias: dict = {}
        self.slots: dict = {}
        self.alias = self._derive_aliases()
        self.slots = self._derive_coord_slots()

    # -- derived tables ----------------------------------------------------
    def _derive_aliases(self) -> dict[tuple[str, str], tuple[str, ...]]:
        """(coordinator attr A, field F) -> canonical path, when the
        coordinator constructs ``self.A = K(..., <coord path>, ...)`` and
        ``K.__init__`` stores that parameter as ``self.F`` (so
        ``self._thermal_model.params`` IS ``_thermal_params``)."""
        pkg = self.pkg
        out: dict[tuple[str, str], tuple[str, ...]] = {}
        if pkg.coord_key not in pkg.classes:
            return out
        cnode = pkg.classes[pkg.coord_key].node
        for fnode in [n for n in cnode.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            env = self._local_env(fnode, {"self": frozenset({COORD})}, pkg.coord_key, COORD_MODULE, bare=True)
            for n in walk(fnode):
                if not (isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.value, ast.Call)):
                    continue
                t = n.targets[0]
                if not (isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id == "self"):
                    continue
                r = pkg.resolve_expr_static(COORD_MODULE, n.value.func)
                if not r or r[0] != "class":
                    continue
                init = pkg.member(r[1], "__init__")
                if not init:
                    continue
                params = pkg.funcs[init].params[1:]
                bound = {}
                for i, a in enumerate(n.value.args):
                    if i < len(params):
                        bound[params[i]] = a
                for kw in n.value.keywords:
                    if kw.arg:
                        bound[kw.arg] = kw.value
                stores = {}
                for s in walk(pkg.funcs[init].node):
                    if isinstance(s, ast.Assign) and len(s.targets) == 1 and isinstance(s.value, ast.Name):
                        st = s.targets[0]
                        if isinstance(st, ast.Attribute) and isinstance(st.value, ast.Name) and st.value.id == "self":
                            stores[s.value.id] = st.attr
                for p, argexpr in bound.items():
                    if p not in stores:
                        continue
                    for role in self.ev(argexpr, env, COORD_MODULE, pkg.coord_key, bare=True):
                        if role[0] == "obj":
                            out.setdefault((t.attr, stores[p]), role[1])
        return out

    def _derive_coord_slots(self) -> dict[tuple[str, str], set[str]]:
        """Per non-coordinator class: the ``self.X`` attributes that hold the
        coordinator. ``coordinator`` for CoordinatorEntity subclasses (HA sets
        it in the base __init__), plus ``self.X = <coord param>`` stores."""
        pkg = self.pkg
        out: dict[tuple[str, str], set[str]] = {}
        for key, c in pkg.classes.items():
            if key == pkg.coord_key:
                continue
            slots = set()
            for k in pkg.mro(key):
                if any("CoordinatorEntity" in b for b in pkg.classes[k].ext_bases):
                    slots.add("coordinator")
                for n in walk(pkg.classes[k].node):
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        a = n.args
                        cps = {p.arg for p in a.args + a.kwonlyargs
                               if p.arg in ("coord", "coordinator") or is_coord_annotation(p.annotation)}
                        for s in walk(n):
                            if isinstance(s, (ast.Assign, ast.AnnAssign)):
                                tg = s.targets[0] if isinstance(s, ast.Assign) else s.target
                                if (isinstance(tg, ast.Attribute) and isinstance(tg.value, ast.Name)
                                        and tg.value.id == "self" and isinstance(s.value, ast.Name)
                                        and s.value.id in cps):
                                    slots.add(tg.attr)
            if slots:
                out[key] = slots
        return out

    # -- evaluation ----------------------------------------------------------
    def canon(self, path: tuple[str, ...]) -> tuple[str, ...]:
        for _ in range(4):
            if len(path) >= 2 and (path[0], path[1]) in self.alias:
                path = self.alias[(path[0], path[1])] + path[2:]
            else:
                break
        return path

    def step(self, role: tuple, attr: str) -> tuple | None:
        pkg = self.pkg
        if role == COORD:
            if attr == CTX_ATTR:
                return COORD
            return ("obj", (attr,), self.coord_attr_types.get(attr))
        if role[0] == "obj":
            path, cls = role[1], role[2]
            if len(path) >= MAX_PATH:
                return None
            newpath = self.canon(path + (attr,))
            if newpath != path + (attr,):
                cls2 = self.coord_attr_types.get(newpath[0]) if len(newpath) == 1 else None
            else:
                cls2 = pkg.attr_types(cls).get(attr) if cls else None
            return ("obj", newpath, cls2)
        if role[0] == "self":
            if attr in self.slots.get(role[1], ()):
                return COORD
            return None
        return None

    def ev(self, e: ast.AST, env: dict, mod: str, cls, bare: bool = False) -> frozenset:
        if isinstance(e, ast.Name):
            r = env.get(e.id, EMPTY)
            if not r and self.seed_params and e.id in COORD_NAMES:
                return frozenset({COORD})
            return r
        if isinstance(e, ast.Attribute):
            if e.attr == "runtime_data":
                return frozenset({COORD})
            out = set()
            for r in self.ev(e.value, env, mod, cls, bare):
                s = self.step(r, e.attr)
                if s:
                    out.add(s)
            return frozenset(out)
        if isinstance(e, ast.Call):
            f = e.func
            if isinstance(f, ast.Name) and f.id == "getattr" and len(e.args) >= 2 \
                    and isinstance(e.args[1], ast.Constant) and isinstance(e.args[1].value, str):
                name = e.args[1].value
                if name == "runtime_data":
                    return frozenset({COORD})
                base = self.ev(e.args[0], env, mod, cls, bare)
                if name == CTX_ATTR:
                    return base
                return frozenset(s for r in base if (s := self.step(r, name)))
            if isinstance(f, ast.Name) and f.id == "cast" and len(e.args) == 2:
                return self.ev(e.args[1], env, mod, cls, bare)
            r = self.pkg.resolve_expr_static(mod, f)
            if r and r[0] == "class" and r[1] == self.pkg.coord_key:
                return frozenset({COORD})
            return EMPTY
        if isinstance(e, ast.Subscript):
            out = set()
            for r in self.ev(e.value, env, mod, cls, bare):
                if r[0] == "obj" and len(r[1]) < MAX_PATH:
                    out.add(("obj", r[1] + ("[]",), None))
            return frozenset(out)
        if isinstance(e, ast.NamedExpr):
            return self.ev(e.value, env, mod, cls, bare)
        if isinstance(e, ast.IfExp):
            return self.ev(e.body, env, mod, cls, bare) | self.ev(e.orelse, env, mod, cls, bare)
        if isinstance(e, ast.BoolOp):
            out = EMPTY
            for v in e.values:
                out = out | self.ev(v, env, mod, cls, bare)
            return out
        if isinstance(e, ast.Await):
            return EMPTY
        return EMPTY

    def _bind(self, target: ast.AST, value: ast.AST | None, roles: frozenset | None, env: dict,
              mod: str, cls, bare: bool) -> bool:
        changed = False
        if isinstance(target, ast.Name):
            r = roles if roles is not None else self.ev(value, env, mod, cls, bare)
            if r and not r <= env.get(target.id, EMPTY):
                env[target.id] = env.get(target.id, EMPTY) | r
                changed = True
        elif isinstance(target, (ast.Tuple, ast.List)) and isinstance(value, (ast.Tuple, ast.List)) \
                and len(target.elts) == len(value.elts):
            for t, v in zip(target.elts, value.elts):
                changed |= self._bind(t, v, None, env, mod, cls, bare)
        return changed

    def _local_env(self, fnode: ast.AST, params: dict, cls, mod: str, bare: bool = False) -> dict:
        env = {k: frozenset(v) for k, v in params.items()}
        assigns = []
        for n in walk(fnode):
            if isinstance(n, ast.Assign):
                for t in n.targets:
                    assigns.append((t, n.value))
            elif isinstance(n, ast.AnnAssign) and n.value is not None:
                assigns.append((n.target, n.value))
            elif isinstance(n, ast.NamedExpr):
                assigns.append((n.target, n.value))
            elif isinstance(n, (ast.For, ast.AsyncFor)) and isinstance(n.iter, (ast.Tuple, ast.List)):
                for elt in n.iter.elts:
                    assigns.append((n.target, elt))
            elif isinstance(n, (ast.With, ast.AsyncWith)):
                for item in n.items:
                    if item.optional_vars is not None:
                        assigns.append((item.optional_vars, item.context_expr))
        for _ in range(4):
            changed = False
            for t, v in assigns:
                changed |= self._bind(t, v, None, env, mod, cls, bare)
            if not changed:
                break
        return env

    def seed_env(self, fn: Fn) -> dict:
        """Roles a function has on its own, before any call site."""
        env: dict[str, frozenset] = {}
        a = fn.node.args
        if fn.cls == self.pkg.coord_key and fn.kind == "method":
            env[fn.params[0]] = frozenset({COORD})
        elif fn.cls is not None and fn.kind == "method" and fn.params:
            env[fn.params[0]] = frozenset({("self", fn.cls)})
        if self.seed_params:
            for p in a.posonlyargs + a.args + a.kwonlyargs:
                if p.arg in ("coord", "coordinator") or is_coord_annotation(p.annotation):
                    env[p.arg] = env.get(p.arg, EMPTY) | {COORD}
        return env

    # -- call resolution -----------------------------------------------------
    def callees(self, fn: Fn, call: ast.Call, env: dict) -> list[tuple[str, frozenset | None, int]]:
        """[(qual, self_roles or None, arg offset)] for a call expression."""
        pkg, f, out = self.pkg, call.func, []
        if isinstance(f, ast.Name):
            r = pkg.resolve_name(fn.mod, f.id)
            if r and r[0] == "var" and r[1] in pkg.injected:
                r = ("func", pkg.injected[r[1]])
            if r and r[0] == "func":
                out.append((r[1], None, 0))
            elif r and r[0] == "class":
                init = pkg.member(r[1], "__init__")
                if init:
                    out.append((init, frozenset({("self", r[1])}), 1))
        elif isinstance(f, ast.Attribute):
            m = f.attr
            v = f.value
            st = pkg.resolve_expr_static(fn.mod, v)
            if st and st[0] == "mod":
                r = pkg.resolve_name(st[1], m)
                if r and r[0] == "func":
                    out.append((r[1], None, 0))
                elif r and r[0] == "class":
                    init = pkg.member(r[1], "__init__")
                    if init:
                        out.append((init, frozenset({("self", r[1])}), 1))
                return out
            if st and st[0] == "class":
                q = pkg.member(st[1], m)
                if q:
                    k = pkg.funcs[q].kind
                    out.append((q, None, 1 if k == "classmethod" else 0))
                return out
            if isinstance(v, ast.Call) and isinstance(v.func, ast.Name) and v.func.id == "super" and fn.cls:
                for b in pkg.classes[fn.cls].base_keys:
                    q = pkg.member(b, m)
                    if q:
                        out.append((q, env.get(fn.params[0], EMPTY) if fn.params else EMPTY, 1))
                        break
                return out
            roles = self.ev(v, env, fn.mod, fn.cls)
            for r in roles:
                key = None
                if r == COORD:
                    key = pkg.coord_key
                elif r[0] == "obj" and r[2]:
                    key = r[2]
                elif r[0] == "self":
                    key = r[1]
                if key and key in pkg.classes:
                    q = pkg.member(key, m)
                    if q:
                        k = pkg.funcs[q].kind
                        out.append((q, frozenset({r}) if k == "method" else None, 1 if k in ("method", "classmethod") else 0))
        return out

    def references(self, fn: Fn, node: ast.AST, env: dict) -> list[tuple[str, frozenset | None]]:
        """A method or function referenced without being called (a callback)."""
        pkg = self.pkg
        if isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Load):
            out = []
            for r in self.ev(node.value, env, fn.mod, fn.cls):
                key = pkg.coord_key if r == COORD else r[2] if r[0] == "obj" else r[1] if r[0] == "self" else None
                if key and key in pkg.classes:
                    q = pkg.member(key, node.attr)
                    if q:
                        out.append((q, frozenset({r})))
            st = pkg.resolve_expr_static(fn.mod, node)
            if st and st[0] == "func":
                out.append((st[1], None))
            return out
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            r = pkg.resolve_name(fn.mod, node.id)
            if r and r[0] == "func":
                return [(r[1], None)]
        return []

    # -- propagation -----------------------------------------------------------
    def propagate(self, roots: dict[str, dict] | None = None) -> tuple[dict[str, dict], set[str]]:
        """Worklist to a fixpoint. ``roots`` maps qual -> initial param roles;
        None means every function, each with its ``seed_env``. Returns
        (param env per reached function, reached set)."""
        ck = None if roots is not None else "ALL"
        if ck and getattr(self, "_prop_all", None) is not None:
            return self._prop_all
        res = self._propagate(roots)
        if ck:
            self._prop_all = res
        return res

    def _propagate(self, roots):
        pkg = self.pkg
        penv: dict[str, dict] = {}
        if roots is None:
            roots = {q: self.seed_env(fn) for q, fn in pkg.funcs.items()}
        else:
            roots = {q: {**self.seed_env(pkg.funcs[q]), **{k: frozenset(v) for k, v in e.items()}}
                     for q, e in roots.items()}
        work = list(roots)
        for q, e in roots.items():
            penv[q] = dict(e)
        guard = 0
        while work and guard < 200000:
            guard += 1
            q = work.pop()
            fn = pkg.funcs[q]
            env = self._local_env(fn.node, penv[q], fn.cls, fn.mod)
            called_funcs = set()
            for n in walk(fn.node):
                targets: list[tuple[str, frozenset | None, list, list]] = []
                if isinstance(n, ast.Call):
                    called_funcs.add(id(n.func))
                    for cq, selfroles, off in self.callees(fn, n, env):
                        targets.append((cq, selfroles, n.args, n.keywords, off))
                elif id(n) not in called_funcs and isinstance(n, (ast.Attribute, ast.Name)):
                    for cq, selfroles in self.references(fn, n, env):
                        targets.append((cq, selfroles, [], [], 1 if selfroles is not None else 0))
                for cq, selfroles, args, kws, off in targets:
                    callee = pkg.funcs[cq]
                    new = penv.get(cq)
                    changed = new is None
                    if new is None:
                        new = self.seed_env(callee)
                    params = callee.params
                    upd: dict[str, frozenset] = {}
                    if selfroles and params and callee.kind == "method":
                        upd[params[0]] = selfroles
                    for i, a in enumerate(args):
                        if isinstance(a, ast.Starred):
                            break
                        j = i + off
                        if j < len(params):
                            r = self.ev(a, env, fn.mod, fn.cls)
                            if r:
                                upd[params[j]] = upd.get(params[j], EMPTY) | r
                    for kw in kws:
                        if kw.arg and kw.arg in params:
                            r = self.ev(kw.value, env, fn.mod, fn.cls)
                            if r:
                                upd[kw.arg] = upd.get(kw.arg, EMPTY) | r
                    for p, r in upd.items():
                        if not r <= new.get(p, EMPTY):
                            new[p] = new.get(p, EMPTY) | r
                            changed = True
                    if changed:
                        penv[cq] = new
                        work.append(cq)
        return penv, set(penv)

    # -- write sites -------------------------------------------------------------
    def write_sites(self, fn: Fn, env: dict) -> list[dict]:
        """Every write this function performs through a role-carrying base.

        kind: "rebind"  coord.A = v            (a store ON the coordinator)
              "attr"    <obj>.F = v / del / setattr / augassign
              "item"    <obj>[k] = v / del / augassign
              "mutate"  <obj>.append(...) etc. on an untyped container
        """
        pkg, out = self.pkg, []
        full = self._local_env(fn.node, env, fn.cls, fn.mod)

        def base_roles(e):
            return self.ev(e, full, fn.mod, fn.cls)

        own_self = fn.params[0] if (fn.kind == "method" and fn.params and fn.cls != pkg.coord_key) else None

        def root_name(e):
            while isinstance(e, (ast.Attribute, ast.Subscript)):
                e = e.value
            return e.id if isinstance(e, ast.Name) else None

        # locals that alias the method's own object or a part of it
        # (``state = self.state``): writes through them are the object
        # mutating itself, not a reach into someone else's state.
        own_names = {own_self} if own_self else set()
        if own_self:
            for _ in range(3):
                for n in walk(fn.node):
                    if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
                        if root_name(n.value) in own_names and isinstance(n.value, (ast.Attribute, ast.Subscript, ast.Name)):
                            own_names.add(n.targets[0].id)

        def emit(kind, roles, field_, node, via, base=None):
            own = base is not None and root_name(base) in own_names
            for r in roles:
                if r == COORD and kind == "attr":
                    out.append(dict(kind="rebind", path=(field_,), field=field_, line=node.lineno, via=via, own=own))
                elif r[0] == "obj":
                    out.append(dict(kind=kind, path=r[1], field=field_, line=node.lineno, via=via, own=own))

        def store_target(t, node, via):
            if isinstance(t, (ast.Tuple, ast.List)):
                for e in t.elts:
                    store_target(e.value if isinstance(e, ast.Starred) else e, node, via)
            elif isinstance(t, ast.Attribute):
                emit("attr", base_roles(t.value), t.attr, node, via, t.value)
            elif isinstance(t, ast.Subscript):
                emit("item", base_roles(t.value), "[]", node, via, t.value)

        for n in walk(fn.node):
            if isinstance(n, ast.Assign):
                for t in n.targets:
                    store_target(t, n, "assign")
            elif isinstance(n, (ast.AugAssign, ast.AnnAssign)):
                if isinstance(n, ast.AnnAssign) and n.value is None:
                    continue
                store_target(n.target, n, "augassign" if isinstance(n, ast.AugAssign) else "assign")
            elif isinstance(n, ast.Delete):
                for t in n.targets:
                    store_target(t, n, "del")
            elif isinstance(n, ast.Call):
                f = n.func
                if isinstance(f, ast.Name) and f.id in ("setattr", "delattr") and len(n.args) >= 2:
                    name = n.args[1].value if isinstance(n.args[1], ast.Constant) else "<dynamic>"
                    emit("attr", base_roles(n.args[0]), name, n, f.id, n.args[0])
                elif isinstance(f, ast.Attribute) and f.attr in MUTATORS:
                    roles = base_roles(f.value)
                    keep = set()
                    for r in roles:
                        if r[0] == "obj" and (r[2] is None or not pkg.member(r[2], f.attr)):
                            keep.add(r)
                    emit("mutate", frozenset(keep), f.attr, n, f.attr, f.value)
        return out


def site_key(fn: Fn, pkg: Pkg, s: dict) -> str:
    return f"{pkg.mods[fn.mod].rel.split('/')[-1]}:{s['line']}"
