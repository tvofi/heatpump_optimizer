"""literal_clones: one declaration spelled twice -- a selector, a schema, a record -- inside literals and calls
(R10-ARCHSCORE-COVERAGE item 3; ARCH2-s5, round 10).

The clone census (``duplication_copies``) joins functions that share a window of statements, so a spec that
is one expression -- ``_number(15, 28, 0.5, "°C", slider=True)`` as a dict value of a wizard page and again as
an argument of its options-registry row -- sits inside one statement and is invisible to it: the wizard's 44
selectors that rebuild their registry row's read NULL.

A SPEC is a call, dict, list, tuple or set expression of at least MIN_NODES nodes (expression contexts not
counted) that computes nothing at runtime: every name in it is bound at module level (a constant, an imported
module, a class, a function) or is a builtin, and it holds no lambda, comprehension, ``await``, walrus or star.
An annotation, an ``except`` type and the subscript of a generic (``dict[str, Any]``) are type expressions,
and a decorator configures the definition it decorates; none is a spec, and each is skipped. A clone class is the specs equal after normalisation; it counts its MAXIMAL
members, an occurrence whose enclosing spec is itself a clone being counted once, as the enclosing one.

Normalisation, so that re-spelling one value is not a fix (counter C20): a number is its float value (``15``
and ``15.0``), a positional argument of a call to an in-package function (no ``*args``) is the keyword it
binds, keyword arguments are in name order, and a dict's items in key order. A local bound once, in the same
function, to a spec-shaped value reads as that value, and so does a module constant bound once to a literal
(its own module's, or one imported by name from another package module) where the function does not bind the
name itself (counter C21), so hoisting a literal into a local or a constant does not hide its copy.

A module constant reads as its value whether it is read by name, imported by name (``from .m import X``), or
read through a module binding (``from . import m``; ``m.X``, resolved by ``common.resolve_expr_static``).

Not seen, and stated: a value computed at runtime, a constant bound twice, a constant read through an absolute
import of the package (``import custom_components.<pkg>.m``, which the package index records as external), a
callee outside the package (its signature is not read), and a call spelled through ``*args``/``**kwargs``.

Headline ``literal_clone_copies``: the members of every clone class.
"""
from __future__ import annotations

import ast
import builtins
import copy
import time
from collections import defaultdict
from pathlib import Path

from . import common as C

MIN_NODES = 6
_KINDS = (ast.Call, ast.Dict, ast.List, ast.Tuple, ast.Set)
_NOT_A_SPEC = (ast.Lambda, ast.comprehension, ast.NamedExpr, ast.Starred, ast.Await, ast.Yield, ast.YieldFrom)
_GENERICS = frozenset({"dict", "list", "tuple", "set", "frozenset", "type", "Callable", "Mapping", "Sequence",
                       "Iterable", "Iterator", "MutableMapping", "Optional", "Union", "Final", "ClassVar",
                       "Literal", "Annotated"})
_BUILTINS = frozenset(dir(builtins))
#: Counter C20: numbers, keywords and dict items normalised, and a positional argument of an in-package callee
#: read as the keyword it binds. ``vector.py`` switches it off.
NORMALISE = True
#: Counter C21: a local, or a module constant, bound once to a spec reads as it. ``vector.py`` switches it off.
INLINE_LOCALS = True


def _module_names(tree: ast.Module) -> set[str]:
    names = set()
    for s in tree.body:
        if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(s.name)
        elif isinstance(s, (ast.Import, ast.ImportFrom)):
            names |= {(a.asname or a.name).split(".")[0] for a in s.names}
        else:
            for t in getattr(s, "targets", [getattr(s, "target", None)]):
                if isinstance(t, ast.Name):
                    names.add(t.id)
    return names


def _module_constants(pkg) -> dict[str, dict[str, ast.AST]]:
    """C21 at module scope: per module, the names bound exactly once at its top level to a literal-only value
    (no name inside it) and never rebound (no ``global`` of it anywhere in the module)."""
    out: dict[str, dict[str, ast.AST]] = {}
    for m, mod in pkg.mods.items():
        bound: dict[str, list[ast.AST]] = defaultdict(list)
        for st in mod.tree.body:
            if isinstance(st, ast.Assign):
                for t in st.targets:
                    for y in ast.walk(t):
                        if isinstance(y, ast.Name):
                            bound[y.id].append(st.value if t is y else None)
            elif isinstance(st, (ast.AnnAssign, ast.AugAssign)) and isinstance(st.target, ast.Name):
                bound[st.target.id].append(st.value if isinstance(st, ast.AnnAssign) else None)
        rebound = {n for y in ast.walk(mod.tree) if isinstance(y, ast.Global) for n in y.names}
        out[m] = {k: v[0] for k, v in bound.items() if len(v) == 1 and v[0] is not None and k not in rebound
                  and not any(isinstance(y, ast.Name) for y in ast.walk(v[0]))}
    return out


def _imported_constants(pkg, consts: dict[str, dict[str, ast.AST]], m: str) -> dict[str, ast.AST]:
    """Module ``m``'s own constants plus the package constants it imports by name (``from .const import X``)."""
    own = dict(consts.get(m, {}))
    for local, imp in pkg.mods[m].imports.items():
        if imp[0] == "sym" and local not in own:
            r = pkg.resolve_name(imp[1], imp[2])
            if r and r[0] == "var" and r[1][1] in consts.get(r[1][0], {}):
                own[local] = consts[r[1][0]][r[1][1]]
    return own


def _attr_constant(pkg, consts: dict[str, dict[str, ast.AST]], m: str, n: ast.Attribute,
                   shadowed: frozenset | set) -> ast.AST | None:
    """C21 through a module binding: ``_c.X`` (``from . import const as _c``), or a dotted chain of them, whose
    receiver resolves to a package module and whose name is one of that module's constants. A root name the
    function binds itself is its own, not the module."""
    root = n
    while isinstance(root, ast.Attribute):
        root = root.value
    if not isinstance(root, ast.Name) or root.id in shadowed:
        return None
    r = pkg.resolve_expr_static(m, n)
    if r and r[0] == "var" and r[1][1] in consts.get(r[1][0], {}):
        return consts[r[1][0]][r[1][1]]
    return None


def _signatures(pkg, m: str) -> dict[str, list[str]]:
    """C20's positional binding: names callable in ``m`` that resolve to an in-package function taking no
    ``*args``, with their positional parameter names in order."""
    out: dict[str, list[str]] = {}
    for name in {*pkg.mods[m].tops, *pkg.mods[m].imports}:
        r = pkg.resolve_name(m, name)
        fn = pkg.funcs.get(r[1]) if r and r[0] == "func" else None
        if fn is not None and fn.cls is None and fn.node.args.vararg is None:
            out[name] = [a.arg for a in (*fn.node.args.posonlyargs, *fn.node.args.args)]
    return out


def _type_nodes(tree: ast.Module) -> set[int]:
    """ids of every node inside an annotation, an ``except`` type, a generic's subscript or a decorator (a
    decorator configures the one definition it decorates: two classes each ``@dataclass(frozen=True)`` share an
    idiom, not a declaration)."""
    roots: list[ast.AST] = []
    for n in ast.walk(tree):
        roots += getattr(n, "decorator_list", [])
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            a = n.args
            roots += [n.returns] + [x.annotation for x in [*a.posonlyargs, *a.args, *a.kwonlyargs, a.vararg, a.kwarg]
                                    if x is not None]
        elif isinstance(n, ast.AnnAssign):
            roots.append(n.annotation)
        elif isinstance(n, ast.ExceptHandler):
            roots.append(n.type)
        elif isinstance(n, ast.Subscript) and ast.unparse(n.value).split(".")[-1] in _GENERICS:
            roots.append(n.slice)
    # expression contexts are shared singletons (one ``Load`` for the whole tree), so they are never marked
    return {id(y) for r in roots if r is not None for y in ast.walk(r) if not isinstance(y, ast.expr_context)}


class _Normalise(ast.NodeTransformer):
    def __init__(self, sigs: dict[str, list[str]] | None = None):
        self.sigs = sigs or {}

    def visit_Constant(self, n):
        if NORMALISE and isinstance(n.value, (int, float)) and not isinstance(n.value, bool):
            return ast.Constant(value=float(n.value))
        return n

    def visit_Call(self, n):
        self.generic_visit(n)
        if NORMALISE:
            params = self.sigs.get(n.func.id) if isinstance(n.func, ast.Name) else None
            if params is not None and len(n.args) <= len(params) \
                    and not any(isinstance(a, ast.Starred) for a in n.args):
                n.keywords = [ast.keyword(arg=p, value=a) for p, a in zip(params, n.args)] + n.keywords
                n.args = []
            n.keywords = sorted(n.keywords, key=lambda k: k.arg or "")
        return n

    def visit_Dict(self, n):
        self.generic_visit(n)
        if NORMALISE and all(k is not None for k in n.keys):
            pairs = sorted(zip(n.keys, n.values), key=lambda kv: ast.dump(kv[0]))
            n.keys, n.values = [k for k, _ in pairs], [v for _, v in pairs]
        return n


def _local_specs(fn: ast.AST, is_spec) -> dict[str, ast.AST]:
    """C21: locals of ``fn`` bound exactly once, to a spec-shaped value."""
    bound: dict[str, list[ast.AST]] = defaultdict(list)
    for n in ast.walk(fn):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    bound[t.id].append(n.value)
        elif isinstance(n, (ast.AnnAssign, ast.AugAssign, ast.NamedExpr)) and isinstance(n.target, ast.Name):
            bound[n.target.id].append(n.value if not isinstance(n, ast.AugAssign) else None)
        elif isinstance(n, (ast.For, ast.AsyncFor, ast.With, ast.AsyncWith)):
            for t in ast.walk(n.target if isinstance(n, (ast.For, ast.AsyncFor)) else ast.Tuple(
                    elts=[i.optional_vars for i in n.items if i.optional_vars is not None])):
                if isinstance(t, ast.Name):
                    bound[t.id].append(None)
    return {k: v[0] for k, v in bound.items() if len(v) == 1 and v[0] is not None and is_spec(v[0], {})}


def specs(root: Path) -> dict[str, list[tuple[str, int]]]:
    """normalised spec -> its maximal occurrences (``module``, line), for every spec seen twice or more."""
    pkg = C.load(str(root))
    occ: dict[str, list[tuple[str, int, int]]] = defaultdict(list)
    parent: dict[int, str] = {}
    consts = _module_constants(pkg) if INLINE_LOCALS else {}
    for m, mod in pkg.mods.items():
        known = _module_names(mod.tree) | _BUILTINS
        skip = _type_nodes(mod.tree)
        mod_consts = _imported_constants(pkg, consts, m) if INLINE_LOCALS else {}
        sigs = _signatures(pkg, m) if NORMALISE else {}

        def is_spec(e: ast.AST, locals_: dict[str, ast.AST]) -> bool:
            for y in ast.walk(e):
                if isinstance(y, _NOT_A_SPEC) or id(y) in skip:
                    return False
                if isinstance(y, ast.Name) and y.id not in known and y.id not in locals_:
                    return False
            return True

        scopes = [(n, _local_specs(n, is_spec) if INLINE_LOCALS else {}) for n in ast.walk(mod.tree)
                  if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        local_of: dict[int, dict[str, ast.AST]] = {}
        for fn, loc in scopes:
            # a module constant reads as its value unless this function binds the name itself
            a = fn.args
            stored = {y.id for y in ast.walk(fn) if isinstance(y, ast.Name) and isinstance(y.ctx, ast.Store)} \
                | {x.arg for x in (*a.posonlyargs, *a.args, *a.kwonlyargs, a.vararg, a.kwarg) if x is not None}
            scope = {**{k: v for k, v in mod_consts.items() if k not in stored}, **loc}
            for y in ast.walk(fn):
                local_of[id(y)] = (scope, stored)  # innermost wins: functions nested later overwrite
        for x in ast.walk(mod.tree):
            if not isinstance(x, _KINDS) or id(x) in skip:
                continue
            loc, shadowed = local_of.get(id(x), (mod_consts, frozenset()))
            if not is_spec(x, loc) or sum(1 for y in ast.walk(x) if not isinstance(y, ast.expr_context)) < MIN_NODES:
                continue
            form = copy.deepcopy(x)
            if INLINE_LOCALS:
                form = _Inline(loc, lambda a, m=m, sh=shadowed: _attr_constant(pkg, consts, m, a, sh)).visit(form)
            key = ast.dump(_Normalise(sigs).visit(form))
            occ[key].append((m, x.lineno, id(x)))
            for y in ast.iter_child_nodes(x):
                parent[id(y)] = key
    dup = {k for k, v in occ.items() if len(v) > 1}
    out: dict[str, list[tuple[str, int]]] = {}
    for k in dup:
        members = [(m, line) for m, line, i in occ[k] if parent.get(i) not in dup]
        if len(members) > 1:
            out[k] = sorted(members)
    return out


class _Inline(ast.NodeTransformer):
    def __init__(self, loc: dict[str, ast.AST], attr=None):
        self.loc, self.attr = loc, attr

    def visit_Name(self, n):
        return copy.deepcopy(self.loc[n.id]) if n.id in self.loc else n

    def visit_Attribute(self, n):
        v = self.attr(n) if self.attr is not None else None
        return copy.deepcopy(v) if v is not None else self.generic_visit(n)


def measure(root: Path) -> dict:
    t0 = time.perf_counter()
    found = specs(root)
    per_module: dict[str, int] = defaultdict(int)
    for members in found.values():
        for m, _line in members:
            per_module[m] += 1
    return {
        "metric": "literal_clones",
        "value": sum(len(v) for v in found.values()),
        "details": {"classes": len(found), "per_module": dict(sorted(per_module.items(), key=lambda kv: -kv[1])),
                    "largest": sorted(([f"{m}:{line}" for m, line in v] for v in found.values()), key=len)[-5:]},
        "runtime_s": round(time.perf_counter() - t0, 3),
    }
