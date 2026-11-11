"""coord_footprint: logic statements in the coordinator class plus every function handed it.

A function is charged when a parameter of it carries the coordinator, found by ROLE (the
role engine follows call sites, so renaming ``coord`` to ``owner`` hides nothing: v0 read
-232 on that null). Plumbing is not logic and is not counted -- an alias
(``x = self.a.b``), a bare delegation (``self.f(a, b)`` as an expression, a return or a
single assignment whose arguments are names, attributes or constants) and a trivial
accessor (``return self._x``) -- so an Extract Method, a dedupe or a new accessor does
not read as growth.

``params_over_10`` is the guard against fragment chains (a pass-through chain inflates it)
and counts each literal key a function reads out of its own ``**kw`` as a parameter, so
turning keyword parameters into a ``**kw`` bag moves nothing (red-team attempt 11).
"""
from __future__ import annotations

import ast
from pathlib import Path

from . import common as C


def _is_doc(s: ast.AST) -> bool:
    return isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and isinstance(s.value.value, str)


def _simple(e: ast.AST) -> bool:
    return isinstance(e, (ast.Name, ast.Constant)) or (
        isinstance(e, ast.Attribute) and _simple(e.value)) or (
        isinstance(e, ast.Starred) and _simple(e.value))


def _delegation(call: ast.AST) -> bool:
    return isinstance(call, ast.Call) and isinstance(call.func, (ast.Attribute, ast.Name)) \
        and _simple(call.func if isinstance(call.func, ast.Name) else call.func.value) \
        and all(_simple(a) for a in call.args) and all(_simple(k.value) for k in call.keywords)


def _value(e: ast.AST) -> ast.AST:
    """What a statement's value computes: through an ``await``, and through a ``cast(T, x)``, which
    asserts a type and computes ``x`` (counter C12: a cast is not delegation, red-team attempt 15)."""
    e = e.value if isinstance(e, ast.Await) else e
    while isinstance(e, ast.Call) and isinstance(e.func, ast.Name) and e.func.id == "cast" and len(e.args) == 2:
        e = e.args[1]
    return e


def _plumbing(s: ast.AST) -> bool:
    if isinstance(s, ast.Expr):
        return _delegation(_value(s.value))
    if isinstance(s, ast.Return) and s.value is not None:
        v = _value(s.value)
        return _delegation(v) or (isinstance(v, ast.Attribute) and _simple(v))
    if isinstance(s, ast.Assign) and len(s.targets) == 1 and isinstance(s.targets[0], ast.Name):
        v = _value(s.value)
        return (isinstance(v, ast.Attribute) and _simple(v)) or _delegation(v)
    return False


def _arity(t: ast.AST) -> int:
    """Names a target binds: ``a, (b, c)`` is three, ``x.y`` and ``x[i]`` one each."""
    if isinstance(t, (ast.Tuple, ast.List)):
        return sum(_arity(e) for e in t.elts)
    return _arity(t.value) if isinstance(t, ast.Starred) else 1


def _display(e: ast.AST) -> bool:
    return isinstance(e, (ast.Tuple, ast.List))


def _bound(t: ast.AST, v: ast.AST) -> int:
    """The statements one target bound to one value spells. A tuple target against a tuple value of its
    length is its pairs, each judged alone and recursively (``a, (b, c) = e1, (e2, e3)`` is three, a pair of
    plumbing none); any other tuple target is the names it unpacks; a single target is one (or none, plumbing),
    a display bound to it being ONE value."""
    if _display(t):
        if _display(v) and not any(isinstance(e, ast.Starred) for e in t.elts + v.elts):
            if len(t.elts) == len(v.elts):
                return sum(_bound(a, b) for a, b in zip(t.elts, v.elts))
        if _display(v) and any(isinstance(e, ast.Starred) for e in t.elts):
            return _arity(t)  # ``a, *b = e1, e2, e3`` is a = e1; b = [e2, e3]: the star takes the rest
        return max(_arity(t), len(v.elts) if _display(v) else 0)
    return 0 if _plumbing(ast.Assign(targets=[t], value=v)) else 1


def _flat(e: ast.AST):
    """The elements of a display statement, nested displays flattened: ``(f(), (g(), h()))`` is three."""
    if _display(e):
        for x in e.elts:
            yield from _flat(x)
    elif isinstance(e, ast.Set):
        for x in e.elts:
            yield from _flat(x)
    elif isinstance(e, ast.Dict):
        for x in [k for k in e.keys if k is not None] + e.values:
            yield from _flat(x)
    else:
        yield e


def _chain(e: ast.AST) -> int:
    """Branches of the conditional-expression tree ``a if p else b if q else c`` (three), 0 for a lone one. An
    ``IfExp`` is followed through its body arm as well as its orelse: ``(a if q else b) if p else c`` is three
    branches, as its nested if/else spells (red-team attempt 54)."""
    def leaves(x: ast.AST) -> int:
        return leaves(x.body) + leaves(x.orelse) if isinstance(x, ast.IfExp) else 1
    k = leaves(e)
    return k if k > 2 else 0


def _own_exprs(s: ast.AST):
    """Every expression node of a statement's own header and value, not those of the statements it contains."""
    stack = [c for c in ast.iter_child_nodes(s) if not isinstance(c, (ast.stmt, ast.excepthandler, ast.match_case))]
    while stack:
        e = stack.pop()
        yield e
        stack.extend(c for c in ast.iter_child_nodes(e) if not isinstance(c, (ast.stmt, ast.excepthandler, ast.match_case)))


def _extras(s: ast.AST) -> int:
    """Statements a statement's own expressions pack: each walrus (``h(a := f(), b := g())`` is three) beyond
    one that is itself the statement or an element of a bare display, and the branches a conditional-expression
    chain spells (an if/elif/else of ``k`` branches is ``2k - 1`` statements, the chain's assign being one; a
    lone ``a if p else b`` is the idiom and reads one)."""
    carried = {id(s.value)} if isinstance(s, ast.Expr) else set()
    if isinstance(s, ast.Expr) and isinstance(s.value, (ast.Tuple, ast.List, ast.Set, ast.Dict)):
        carried = {id(e) for e in _flat(s.value)}
    nodes = list(_own_exprs(s))
    inner = {id(a) for n in nodes if isinstance(n, ast.IfExp) for a in (n.body, n.orelse) if isinstance(a, ast.IfExp)}
    return sum(1 for n in nodes if isinstance(n, ast.NamedExpr) and id(n) not in carried) \
        + sum(2 * _chain(n) - 2 for n in nodes if isinstance(n, ast.IfExp) and id(n) not in inner and _chain(n))


def _units(s: ast.AST) -> int:
    """The statements a statement packs (counter C25). One AST statement can hold several: a
    tuple-unpack ``a, b, c = (f(x) for x in xs)``, a tuple on the right ``a, b = f(), g()``, a chain
    ``a = b = f()``, a bare tuple, set or dict ``f(), g()``, a loop over a literal ``for a, b in [(f(), g())]``,
    ``with p as a, q as b``, ``import a, b``, a walrus, a conditional-expression chain. Each reads as the
    plain statements it spells, so packing them lowers no count. A single-target, single-value
    statement is one, a display bound to one target included."""
    return _own(s) + _extras(s)


def _own(s: ast.AST) -> int:
    if isinstance(s, ast.Assign):
        if len(s.targets) == 1:
            return _bound(s.targets[0], s.value)
        if len(s.targets) > 1 and all(isinstance(t, ast.Name) for t in s.targets) \
                and _plumbing(ast.Assign(targets=s.targets[:1], value=s.value)):
            return 0  # ``a = b = x.y`` is two aliases
        return max(1, sum(_arity(t) for t in s.targets))
    if isinstance(s, ast.Expr) and isinstance(s.value, (ast.Tuple, ast.List, ast.Set, ast.Dict)):
        return sum(1 for e in _flat(s.value) if not isinstance(e, ast.Constant) and not _plumbing(ast.Expr(value=e)))
    if isinstance(s, (ast.For, ast.AsyncFor)) and isinstance(s.iter, (ast.Tuple, ast.List, ast.Set)):
        # ``for a, b, c in [(e1, e2, e3)]`` binds three values once; a loop over a literal with one target is one
        return max(1, sum(_bound(s.target, e) for e in s.iter.elts if _display(s.target) and _display(e)))
    if isinstance(s, (ast.With, ast.AsyncWith)):
        return len(s.items)
    if isinstance(s, (ast.Import, ast.ImportFrom)):
        return len(s.names)
    if isinstance(s, ast.Delete):
        return sum(_arity(t) for t in s.targets)
    return 1


PACKING_UNITS = True  # False: one per statement, for ``vector.ablated`` (counter C25 off)


def logic_stmts(node: ast.AST) -> int:
    return sum(_units(n) if PACKING_UNITS else 1 for n in ast.walk(node) if isinstance(n, ast.stmt) and not _is_doc(n)
               and not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
               and not _plumbing(n))


def coord_footprint(pkg: C.Pkg, eng: C.Engine) -> tuple[int, list[str]]:
    cls = pkg.classes[pkg.coord_key].node
    total = logic_stmts(cls)
    penv, _ = eng.propagate(None)
    charged = []
    for q, fn in sorted(pkg.funcs.items()):
        if fn.cls is not None or fn.node not in pkg.mods[fn.mod].tree.body:
            continue
        env = penv.get(q, {})
        if any(C.COORD in env.get(p, frozenset()) for p in fn.params):
            n = logic_stmts(fn.node)
            total += n
            charged.append(f"{fn.mod}.{fn.name}:{n}")
    return total, charged


READ_KW_KEYS = True  # False: the plain count, for ``vector.ablated`` (counter C11 off)


def _param_count(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """The definition's parameter count, C11's literal ``**kw`` keys included.

    The one definition of the guard; ``params_over_10`` and the head census
    (#1776) both read it, so the count and the named sites cannot drift
    apart.
    """
    a = fn.args
    k = len([x for x in a.posonlyargs + a.args + a.kwonlyargs if x.arg not in ("self", "cls")])
    if a.kwarg and READ_KW_KEYS:
        kw = a.kwarg.arg
        keys = set()
        for x in ast.walk(fn):
            if isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute) \
                    and x.func.attr in ("get", "pop") \
                    and isinstance(x.func.value, ast.Name) and x.func.value.id == kw and x.args \
                    and isinstance(x.args[0], ast.Constant):
                keys.add(x.args[0].value)
            elif isinstance(x, ast.Subscript) and isinstance(x.value, ast.Name) and x.value.id == kw \
                    and isinstance(x.slice, ast.Constant):
                keys.add(x.slice.value)
        k += len(keys)
    return k


def params_over_10_sites(trees: dict[str, ast.Module]) -> list[str]:
    """``module.qualname`` for every function the guard counts, parents included."""
    sites: list[str] = []
    for mod, t in trees.items():
        def visit(node: ast.AST, prefix: str) -> None:
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if _param_count(child) > 10:
                        sites.append(f"{mod}.{prefix}{child.name}")
                    visit(child, f"{prefix}{child.name}.")
                elif isinstance(child, ast.ClassDef):
                    visit(child, f"{prefix}{child.name}.")
                else:
                    visit(child, prefix)
        visit(t, "")
    return sites


def params_over_10(trees: dict[str, ast.Module]) -> int:
    return len(params_over_10_sites(trees))


def measure(root: Path, pkg: C.Pkg | None = None) -> dict:
    pkg = pkg or C.load(str(root))
    eng = C.engine(pkg)
    fp, charged = coord_footprint(pkg, eng)
    trees = {m.name: m.tree for m in pkg.mods.values() if "." not in m.name}
    return {"coord_footprint": fp, "params_over_10": params_over_10(trees), "charged": charged}
