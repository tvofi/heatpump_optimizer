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


def _plumbing(s: ast.AST) -> bool:
    if isinstance(s, ast.Expr):
        v = s.value.value if isinstance(s.value, ast.Await) else s.value
        return _delegation(v)
    if isinstance(s, ast.Return) and s.value is not None:
        v = s.value.value if isinstance(s.value, ast.Await) else s.value
        return _delegation(v) or (isinstance(v, ast.Attribute) and _simple(v))
    if isinstance(s, ast.Assign) and len(s.targets) == 1 and isinstance(s.targets[0], ast.Name):
        v = s.value.value if isinstance(s.value, ast.Await) else s.value
        return (isinstance(v, ast.Attribute) and _simple(v)) or _delegation(v)
    return False


def logic_stmts(node: ast.AST) -> int:
    return sum(1 for n in ast.walk(node) if isinstance(n, ast.stmt) and not _is_doc(n)
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


def params_over_10(trees: dict[str, ast.Module]) -> int:
    n = 0
    for t in trees.values():
        for fn in ast.walk(t):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
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
            n += k > 10
    return n


def measure(root: Path, pkg: C.Pkg | None = None) -> dict:
    pkg = pkg or C.load(str(root))
    eng = C.engine(pkg)
    fp, charged = coord_footprint(pkg, eng)
    trees = {m.name: m.tree for m in pkg.mods.values() if "." not in m.name}
    return {"coord_footprint": fp, "params_over_10": params_over_10(trees), "charged": charged}
