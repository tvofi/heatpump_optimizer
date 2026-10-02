#!/usr/bin/env python3
"""Prototype counter-metrics for the red-team games (redteam.md section 3).

    python3 counters.py ROOT   -> JSON on stdout

untyped_payload_keys_v2   a3's metric, but a TypedDict key annotated Any / object (or NotRequired[Any])
                          is NOT a contract (C1).
reflective_writes         package-wide count of writes / mutations spelled reflectively:
                          object.__setattr__ / x.__setattr__ / __setitem__ / __delitem__ / __delattr__
                          called explicitly, setattr/delattr (any name), type(x).m(...), unbound builtin
                          mutators (list.append(x, ..)), vars(x)[k] = / x.__dict__[k] = , getattr(o, n)(..)
                          dynamic invocation, operator.setitem/delitem (C2). Bodies of dunder methods
                          other than __init__ (a descriptor's own __get__/__set__) are exempt.
                          Gate-only: must not rise.
computed_attr_access      getattr/hasattr/setattr/delattr with a non-literal name, outside dunder bodies
                          (C2b). Gate-only: must not rise.
dup_pairs_v2              dup_pairs_v1 with effect-free expression statements (constants, names,
                          attributes, calls of id/len/hash/repr/type/str) dropped before windowing (C3).
private_reach_v2          a3's private_reach where a coordinator property whose body is just
                          ``return self._x`` is read as ``_x`` (C5).
family_orphan_overrides   ENTITY_FAMILY_OVERRIDES entries whose target family has < 2 members, or whose
                          target is the key itself: a declaration that removes a member from its
                          family without homing it anywhere (C6).
unread_private_globals    module-level private bindings (``_X = ...``) that nothing in the package
                          loads (C7) -- a keep-alive registry is one.
params_over_10_v2         a1's params_over_10, counting each literal key a function reads out of its
                          own ``**kw`` as a parameter (C11).
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCR = HERE.parents[1]
sys.path.insert(0, str(SCR / "a3" / "metrics"))
sys.path.insert(0, str(SCR / "b"))
import _common as C  # noqa: E402

PKG = "custom_components/heatpump_optimizer"
BUILTIN_TYPES = {"list", "dict", "set", "object", "frozenset", "bytearray", "deque", "OrderedDict", "defaultdict"}
DUNDER_WRITES = {"__setattr__", "__delattr__", "__setitem__", "__delitem__"}
PURE = {"id", "len", "hash", "repr", "type", "str", "bool", "int", "float"}


def trees(root: Path):
    return {p.stem: ast.parse(p.read_text()) for p in sorted((root / PKG).glob("*.py"))}


# ---------------------------------------------------------------- C1
def untyped_v2(root: Path) -> int:
    import untyped_payload_keys as U
    orig = U.typed_dicts

    def typed_no_any(pkg):
        out = orig(pkg)
        for key, keys in list(out.items()):
            c = pkg.classes.get(key)
            if c is None:
                continue
            anyk = set()
            for s in c.node.body:
                if isinstance(s, ast.AnnAssign) and isinstance(s.target, ast.Name):
                    a = ast.unparse(s.annotation)
                    for w in ("NotRequired[", "Required[", "ReadOnly["):
                        a = a.replace(w, "").rstrip("]") if a.startswith(w) else a
                    if a.split(".")[-1] in ("Any", "object"):
                        anyk.add(s.target.id)
            out[key] = keys - anyk
        return out
    U.typed_dicts = typed_no_any
    try:
        return U.measure(root)["value"]
    finally:
        U.typed_dicts = orig


# ---------------------------------------------------------------- C2
def _outside_dunders(t):
    """Nodes of t, skipping the bodies of dunder methods (a descriptor's __set__ / a class's own
    __setattr__ implementing the protocol is not a reflective write into someone else)."""
    todo = [t]
    while todo:
        n = todo.pop()
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("__") \
                and n.name.endswith("__") and n.name != "__init__":
            continue
        yield n
        todo.extend(ast.iter_child_nodes(n))


def reflective_writes(ts) -> int:
    n = 0
    for t in ts.values():
        for x in _outside_dunders(t):
            if isinstance(x, ast.Call):
                f = x.func
                if isinstance(f, ast.Attribute) and f.attr in DUNDER_WRITES:
                    n += 1
                elif isinstance(f, ast.Name) and f.id in ("setattr", "delattr"):
                    n += 1
                elif isinstance(f, ast.Attribute) and isinstance(f.value, ast.Call) \
                        and isinstance(f.value.func, ast.Name) and f.value.func.id == "type":
                    n += 1
                elif isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) \
                        and f.value.id in BUILTIN_TYPES and f.attr in C.MUTATORS and x.args:
                    n += 1
                elif isinstance(f, ast.Call) and isinstance(f.func, ast.Name) and f.func.id == "getattr":
                    n += 1
                elif isinstance(f, ast.Attribute) and f.attr in ("setitem", "delitem") \
                        and isinstance(f.value, ast.Name) and f.value.id == "operator":
                    n += 1
            tg = []
            if isinstance(x, (ast.Assign, ast.Delete)):
                tg = x.targets
            elif isinstance(x, (ast.AugAssign, ast.AnnAssign)):
                tg = [x.target]
            for s in tg:
                if isinstance(s, ast.Subscript):
                    v = s.value
                    if (isinstance(v, ast.Call) and isinstance(v.func, ast.Name) and v.func.id == "vars") or \
                            (isinstance(v, ast.Attribute) and v.attr == "__dict__"):
                        n += 1
    return n


def computed_attr_access(ts) -> int:
    """C2b: getattr/hasattr/setattr/delattr whose NAME is not a literal (outside dunder bodies).
    A computed-name read is how a hub handle escapes the role engine without any reflective write
    (attempt 13's ``_live(name)``)."""
    n = 0
    for t in ts.values():
        for x in _outside_dunders(t):
            if isinstance(x, ast.Call) and isinstance(x.func, ast.Name) \
                    and x.func.id in ("getattr", "hasattr", "setattr", "delattr") and len(x.args) >= 2 \
                    and not isinstance(x.args[1], ast.Constant):
                n += 1
    return n


# ---------------------------------------------------------------- C3
def _noop(s) -> bool:
    if not isinstance(s, ast.Expr):
        return False
    v = s.value
    if isinstance(v, (ast.Constant, ast.Name, ast.Attribute)):
        return True
    return isinstance(v, ast.Call) and isinstance(v.func, ast.Name) and v.func.id in PURE \
        and all(isinstance(a, (ast.Constant, ast.Name)) for a in v.args)


def dup_v2(pkg) -> int:
    import metrics_v1 as V
    orig = V._is_doc
    V._is_doc = lambda s: orig(s) or _noop(s)
    try:
        return V.dup_pairs_v1(pkg)
    finally:
        V._is_doc = orig


# ---------------------------------------------------------------- C5
def private_reach_v2(root: Path, ts) -> int:
    import private_reach as PR
    cls = next(n for n in ts["coordinator"].body if isinstance(n, ast.ClassDef) and n.name == C.COORD_CLASS)
    passthrough = set()
    for f in cls.body:
        if isinstance(f, ast.FunctionDef) and C.is_property(f):
            body = [s for s in f.body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
            if len(body) == 1 and isinstance(body[0], ast.Return) and isinstance(body[0].value, ast.Attribute) \
                    and isinstance(body[0].value.value, ast.Name) and body[0].value.value.id == "self" \
                    and body[0].value.attr.startswith("_"):
                passthrough.add(f.name)
    orig = PR._private
    PR._private = lambda name: orig(name) or name in passthrough
    try:
        return PR.measure(root)["value"]
    finally:
        PR._private = orig


# ---------------------------------------------------------------- C6
def family_orphans(root: Path) -> int:
    import family_splits as F
    rows = F.load_rows(root)
    F.OV.clear()
    F.OV.update(F.overrides(root))
    fams: dict = {}
    for _p, key, *_ in rows:
        fams.setdefault(F.OV.get(key, key.split("_")[0]), set()).add(key)
    return sum(1 for k, v in F.OV.items() if v == k or len(fams.get(v, ())) < 2)


# ---------------------------------------------------------------- C7
def unread_private_globals(ts) -> int:
    loaded = set()
    for t in ts.values():
        for x in ast.walk(t):
            if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Load):
                loaded.add(x.id)
            elif isinstance(x, ast.Attribute):
                loaded.add(x.attr)
            elif isinstance(x, ast.ImportFrom):
                loaded |= {a.name for a in x.names}
    n = 0
    for t in ts.values():
        for s in t.body:
            tg = s.targets if isinstance(s, ast.Assign) else [s.target] if isinstance(s, ast.AnnAssign) else []
            for x in tg:
                if isinstance(x, ast.Name) and x.id.startswith("_") and not x.id.startswith("__") \
                        and x.id not in loaded:
                    n += 1
    return n


# ---------------------------------------------------------------- C11
def params_v2(ts) -> int:
    n = 0
    for t in ts.values():
        for fn in ast.walk(t):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            a = fn.args
            k = len([x for x in a.posonlyargs + a.args + a.kwonlyargs if x.arg not in ("self", "cls")])
            if a.kwarg:
                kw = a.kwarg.arg
                keys = set()
                for x in ast.walk(fn):
                    if isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute) and x.func.attr in ("get", "pop") \
                            and isinstance(x.func.value, ast.Name) and x.func.value.id == kw and x.args \
                            and isinstance(x.args[0], ast.Constant):
                        keys.add(x.args[0].value)
                    elif isinstance(x, ast.Subscript) and isinstance(x.value, ast.Name) and x.value.id == kw \
                            and isinstance(x.slice, ast.Constant):
                        keys.add(x.slice.value)
                k += len(keys)
            n += k > 10
    return n


def measure(root: Path) -> dict:
    root = Path(root).resolve()
    ts = trees(root)
    pkg = C.load(str(root))
    fns = {"untyped_payload_keys_v2": lambda: untyped_v2(root), "reflective_writes": lambda: reflective_writes(ts),
           "computed_attr_access": lambda: computed_attr_access(ts),
           "dup_pairs_v2": lambda: dup_v2(pkg), "private_reach_v2": lambda: private_reach_v2(root, ts),
           "family_orphan_overrides": lambda: family_orphans(root),
           "unread_private_globals": lambda: unread_private_globals(ts), "params_over_10_v2": lambda: params_v2(ts)}
    out = {}
    for k, f in fns.items():
        try:
            out[k] = f()
        except Exception as err:  # recorded, never hidden
            out[k] = None
            out[f"_{k}_error"] = f"{type(err).__name__}: {err}"[:200]
    return out


if __name__ == "__main__":
    print(json.dumps(measure(Path(sys.argv[1])), sort_keys=True))
