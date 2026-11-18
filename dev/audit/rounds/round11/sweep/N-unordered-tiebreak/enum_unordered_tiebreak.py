#!/usr/bin/env python3
"""Enumerator for class N-unordered-tiebreak (round 11, D14 steps 3-4).

Lists every place the package picks ONE element (or an order) out of an
unordered collection where equal candidates can tie, so the pick follows set
iteration order (PYTHONHASHSEED for str/bytes/object elements):
  - max/min/sorted(<set-like>, key=...)       (a key makes ties possible)
  - next(iter(<set-like>)), <set-like>.pop(), list/tuple(<set-like>)[i]
  - for x in <set-like>: ... with a running best (if ... > / < ...: best = x)
<set-like>: set()/frozenset() call, a list/generator comprehension over one, set literal or comprehension, a set
operation on those, or a local/attr name assigned one in the same module.
Usage: enum_unordered_tiebreak.py [PKG_DIR]
"""
from __future__ import annotations
import ast, sys
from pathlib import Path


def _setlike(n, names):
    if isinstance(n, (ast.Set, ast.SetComp)):
        return True
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("set", "frozenset"):
        return True
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in (
            "union", "intersection", "difference", "symmetric_difference") and _setlike(n.func.value, names):
        return True
    if isinstance(n, ast.BinOp) and isinstance(n.op, (ast.BitOr, ast.BitAnd, ast.Sub, ast.BitXor)):
        return _setlike(n.left, names) or _setlike(n.right, names)
    if isinstance(n, (ast.ListComp, ast.GeneratorExp)) and any(_setlike(g.iter, names) for g in n.generators):
        return True
    if isinstance(n, ast.Name) and n.id in names:
        return True
    if isinstance(n, ast.Attribute) and ("self." + n.attr) in names:
        return True
    return False


def _set_names(tree):
    names = set()
    for f in ast.walk(tree):  # parameters annotated as a set
        if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for a in f.args.args + f.args.kwonlyargs:
                if a.annotation is not None and any(w in ast.unparse(a.annotation).lower() for w in ("set[", "frozenset", "abstractset")):
                    names.add(a.arg)
    changed = True
    while changed:
        changed = False
        for a in ast.walk(tree):
            tgt, val = None, None
            if isinstance(a, ast.Assign) and len(a.targets) == 1:
                tgt, val = a.targets[0], a.value
            elif isinstance(a, ast.AnnAssign) and a.value is not None:
                tgt, val = a.target, a.value
                if "set" in ast.unparse(a.annotation).lower().split("[")[0]:
                    pass
            if tgt is None:
                continue
            key = tgt.id if isinstance(tgt, ast.Name) else ("self." + tgt.attr if isinstance(tgt, ast.Attribute) else None)
            if key and key not in names and _setlike(val, names):
                names.add(key); changed = True
    return names


def scan(pkg: Path):
    out = []
    for p in sorted(pkg.rglob("*.py")):
        t = ast.parse(p.read_text())
        names = _set_names(t)
        funcs = {}
        for f in ast.walk(t):
            if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                for c in ast.walk(f):
                    funcs[id(c)] = f.name
        for n in ast.walk(t):
            kind = None
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
                fn = n.func.id
                if fn in ("max", "min", "sorted") and n.args and _setlike(n.args[0], names) and any(k.arg == "key" for k in n.keywords):
                    kind = f"{fn}(set,key)"
                elif fn == "next" and n.args and isinstance(n.args[0], ast.Call) and getattr(n.args[0].func, "id", None) == "iter" \
                        and n.args[0].args and _setlike(n.args[0].args[0], names):
                    kind = "next(iter(set))"
            elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "pop" and not n.args \
                    and _setlike(n.func.value, names):
                kind = "set.pop()"
            elif isinstance(n, ast.Subscript) and isinstance(n.value, ast.Call) and getattr(n.value.func, "id", None) in ("list", "tuple") \
                    and n.value.args and _setlike(n.value.args[0], names):
                kind = "list(set)[i]"
            elif isinstance(n, ast.For) and _setlike(n.iter, names):
                body = ast.unparse(ast.Module(body=n.body, type_ignores=[]))
                tv = ast.unparse(n.target)
                if any(isinstance(s, ast.If) and isinstance(s.test, ast.Compare) and any(isinstance(o, (ast.Gt, ast.Lt, ast.GtE, ast.LtE)) for o in s.test.ops)
                       and any(isinstance(b, ast.Assign) and tv in ast.unparse(b.value) for b in s.body) for s in ast.walk(n)) \
                        or "break" in body or "return " + tv in body:
                    kind = "for-in-set running pick"
            if kind:
                out.append((p.name, n.lineno, funcs.get(id(n), "<module>"), kind, ast.get_source_segment(p.read_text(), n).splitlines()[0][:110]))
    return out


if __name__ == "__main__":
    pkg = Path(sys.argv[1] if len(sys.argv) > 1 else "custom_components/heatpump_optimizer")
    rows = scan(pkg)
    for r in rows:
        print("SEAM %s:%d %s [%s] %s" % r)
    print(f"seams={len(rows)}")
