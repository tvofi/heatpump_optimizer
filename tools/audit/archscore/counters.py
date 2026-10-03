"""The counters: what keeps a score metric from being raised without improving the architecture.

The red team (``planted/redteam/``) raised the score with 13 of 16 moves that left the
architecture no better, from +0.5 to +160. A counter is a change to a metric's definition,
or a gate-only tripwire, so that the move reads as nothing or as inadmissible.

C1  an ``Any`` / ``object`` key is untyped              ``metrics/untyped_payload_keys.is_any``
C2  ``reflective_writes``, C2b ``computed_attr_access``  here; gate-only, weight 0. A write spelled
    reflectively is a write; the role engine does not yet read one as a write, so these
    only stop the count falling by re-spelling. They retire when it does.
C3  a statement dead by data flow does not split a clone  ``inert_statements``; applied to the shared
    clone window by ``vector.py``
C4  the coordinator is its whole package class hierarchy  ``flatten``
C5  a passthrough property is a reach                    ``passthrough_properties``; applied to the
    shared reach census by ``vector.py``
C6  ``family_orphan_overrides``                          here; gate-only
C7  ``unread_private_globals``                           here; gate-only
C11 literal keys read from a function's own ``**kw`` are parameters  ``metrics/footprint.params_over_10``
"""
from __future__ import annotations

import ast
import shutil
from pathlib import Path

from .metrics import common as C
from .metrics import family_splits as F

PKG = C.PKG_REL
BUILTIN_TYPES = {"list", "dict", "set", "object", "frozenset", "bytearray", "deque", "OrderedDict", "defaultdict"}
DUNDER_WRITES = {"__setattr__", "__delattr__", "__setitem__", "__delitem__"}
PURE = {"id", "len", "hash", "repr", "type", "str", "bool", "int", "float"}


def trees(root: Path) -> dict[str, ast.Module]:
    return {p.stem: ast.parse(p.read_text()) for p in sorted((Path(root) / PKG).glob("*.py"))}


# ---------------------------------------------------------------- C2
def _outside_dunders(t: ast.AST):
    """Nodes of t, skipping the bodies of dunder methods other than ``__init__`` (a descriptor's
    own ``__set__``, or a class's ``__setattr__`` implementing the protocol, writes nobody else's state)."""
    todo = [t]
    while todo:
        n = todo.pop()
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("__") \
                and n.name.endswith("__") and n.name != "__init__":
            continue
        yield n
        todo.extend(ast.iter_child_nodes(n))


def reflective_writes(ts: dict[str, ast.Module]) -> int:
    """Writes and mutations spelled reflectively: explicit ``__setattr__``-family calls,
    ``setattr``/``delattr`` (any name), ``type(x).m(...)``, unbound builtin mutators
    (``list.append(x, ..)``), ``vars(x)[k] =`` / ``x.__dict__[k] =``, ``getattr(o, n)(..)`` and
    ``operator.setitem``/``delitem``."""
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


def computed_attr_access(ts: dict[str, ast.Module]) -> int:
    """C2b: ``getattr``/``hasattr``/``setattr``/``delattr`` whose NAME is not a literal. A
    computed-name read is how a hub handle escapes the role engine without any reflective
    write (red-team attempt 13's ``_live(name)``)."""
    n = 0
    for t in ts.values():
        for x in _outside_dunders(t):
            if isinstance(x, ast.Call) and isinstance(x.func, ast.Name) \
                    and x.func.id in ("getattr", "hasattr", "setattr", "delattr") and len(x.args) >= 2 \
                    and not isinstance(x.args[1], ast.Constant):
                n += 1
    return n


# ---------------------------------------------------------------- C3
# An expression is effect-free when every node in it is one of these, every call calls a PURE builtin, a
# lambda, or a method of a value built from literals, and every name it binds is dead. A class by grammar,
# closed under composition, not a spelling list.
_PURE_NODES = (ast.Constant, ast.Name, ast.Load, ast.Store, ast.Attribute, ast.Tuple, ast.List, ast.Set,
               ast.Dict, ast.Starred, ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare, ast.IfExp, ast.Lambda,
               ast.arguments, ast.arg, ast.NamedExpr, ast.Call, ast.keyword, ast.JoinedStr, ast.FormattedValue,
               ast.operator, ast.unaryop, ast.boolop, ast.cmpop)


def _literal(e: ast.AST) -> bool:
    """Built from literals: names only PURE builtins, calls only of those or of a non-dunder method, no
    dunder attribute. Such a value is a fresh builtin the statement alone holds, so a method of it changes
    nothing outside it (``[].clear()``, ``"".join(())``); a dunder is refused because it reaches past the
    value's own type (``().__class__.__base__``)."""
    return all(
        isinstance(n, _PURE_NODES) and not isinstance(n, (ast.Lambda, ast.NamedExpr))
        and not (isinstance(n, ast.Name) and n.id not in PURE)
        and not (isinstance(n, ast.Attribute) and n.attr.startswith("__"))
        and not (isinstance(n, ast.Call) and not isinstance(n.func, (ast.Name, ast.Attribute)))
        for n in ast.walk(e))


def _pure_call(n: ast.Call) -> bool:
    f = n.func
    return isinstance(f, ast.Lambda) or (isinstance(f, ast.Name) and f.id in PURE) \
        or (isinstance(f, ast.Attribute) and _literal(n))


def _pure(e: ast.AST | None, dead: set[str]) -> bool:
    return e is None or all(
        isinstance(n, _PURE_NODES)
        and not (isinstance(n, ast.Call) and not _pure_call(n))
        and not (isinstance(n, ast.NamedExpr) and n.target.id not in dead)
        for n in ast.walk(e))


def _fold(e: ast.AST, dead: set[str]):
    """``(True, value)`` for an effect-free expression reading no name but a PURE builtin, else
    ``(False, None)``. No ``**``, ``<<`` or ``*``, so the value is no larger than the literals that spell
    it and evaluating it is bounded (``"x" * 10**10`` and ``[0] * 99999999999`` are refused, not run), and
    no attribute, so nothing reachable from a literal's type is evaluated."""
    if not _pure(e, dead) or any(isinstance(n, (ast.Pow, ast.LShift, ast.Mult, ast.MatMult, ast.NamedExpr, ast.Lambda,
                                                ast.Attribute))
                                 for n in ast.walk(e)) \
            or any(isinstance(n, ast.Name) and n.id not in PURE for n in ast.walk(e)):
        return False, None
    try:
        return True, eval(compile(ast.Expression(e), "<c3>", "eval"),  # noqa: S307 -- grammar above
                          {"__builtins__": {k: __builtins__[k] if isinstance(__builtins__, dict)
                                            else getattr(__builtins__, k) for k in PURE}})
    except Exception:  # noqa: BLE001 -- an expression that raises is not inert
        return False, None


def _inert(s: ast.stmt, dead: set[str]) -> bool:
    """A statement whose execution changes nothing the function can observe afterwards."""
    every = lambda body: all(_inert(x, dead) for x in body)  # noqa: E731
    if isinstance(s, ast.Pass):
        return True
    if isinstance(s, ast.Expr):
        return _pure(s.value, dead)
    if isinstance(s, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Delete)):
        targets = s.targets if isinstance(s, (ast.Assign, ast.Delete)) else [s.target]
        return all(isinstance(n, (ast.Name, ast.Tuple, ast.List, ast.Starred, ast.Store, ast.Del))
                   and not (isinstance(n, ast.Name) and n.id not in dead)
                   for x in targets for n in ast.walk(x)) and _pure(getattr(s, "value", None), dead)
    if isinstance(s, ast.Assert):
        ok, v = _fold(s.test, dead)
        return ok and bool(v)
    if isinstance(s, (ast.If, ast.While)):
        ok, v = _fold(s.test, dead)
        if isinstance(s, ast.While):
            return ok and not v and every(s.orelse)
        return every(s.body if v else s.orelse) if ok else _pure(s.test, dead) and every(s.body) and every(s.orelse)
    if isinstance(s, ast.For):
        ok, v = _fold(s.iter, dead)
        return ok and not list(v) and every(s.orelse) if ok and hasattr(v, "__iter__") else False
    if isinstance(s, ast.Try):
        return every(s.body) and every(s.orelse) and every(s.finalbody) and all(every(h.body) for h in s.handlers)
    return False


def _dead_names(fn: ast.AST) -> set[str]:
    """Names ``fn`` binds and nothing in it reads: not loaded anywhere in its body, nested scopes
    included, and not declared ``global`` or ``nonlocal``."""
    stored, live = set(), set()
    for n in ast.walk(fn):
        if isinstance(n, ast.Name):
            (live if isinstance(n.ctx, ast.Load) else stored).add(n.id)
        elif isinstance(n, (ast.Global, ast.Nonlocal)):
            live |= set(n.names)
    return stored - live


def inert_statements(trees, all_functions) -> set[int]:
    """``id()`` of every statement dead by data flow in the package's functions, dropped before a clone
    window is cut so junk interleaved in every window does not split the clone (attempt 04: 121 -> 7;
    04h to 04m are the spellings an enumeration missed). Dead: effect-free by ``_PURE_NODES`` and binding
    only names nothing reads; an ``assert``, ``if``, ``while`` or ``for`` whose test folds to a constant
    is judged on the branch that runs, and a ``try`` on its every part. Each function is judged with its
    own reads; an enclosing function reads a superset, so the union never drops a live statement.

    Out of the class, and so still open: junk with an effect (a call of anything not PURE), which is
    logic in the diff. A gap tolerance in the window would close that too, but it redefines the shared
    window (59 -> 72 copies on main at 16551007), so it is not here."""
    out: set[int] = set()
    for _path, tree in trees:
        for fn in all_functions(tree):
            dead = _dead_names(fn)
            out |= {id(s) for s in ast.walk(fn) if isinstance(s, ast.stmt) and s is not fn and _inert(s, dead)}
    return out


# ---------------------------------------------------------------- C5
def passthrough_properties(coord: ast.ClassDef) -> dict[str, str]:
    """name -> private attribute, for each coordinator property whose body is just
    ``return self._x``: a public face on a private, so reading it is reading the private."""
    out = {}
    for f in coord.body:
        if isinstance(f, ast.FunctionDef) and C.is_property(f):
            body = [s for s in f.body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
            if len(body) == 1 and isinstance(body[0], ast.Return) and isinstance(body[0].value, ast.Attribute) \
                    and isinstance(body[0].value.value, ast.Name) and body[0].value.value.id == "self" \
                    and body[0].value.attr.startswith("_"):
                out[f.name] = body[0].value.attr
    return out


# ---------------------------------------------------------------- C6
def family_orphan_overrides(root: Path) -> int:
    """``ENTITY_FAMILY_OVERRIDES`` entries whose target family has fewer than two members, or whose
    target is the key itself: a declaration that removes a member from its family and homes it
    nowhere (attempt 07 'cured' family_splits 3 -> 0 with one-member families)."""
    rows = F.load_rows(root)
    ov = F.overrides(root)
    fams: dict[str, set] = {}
    for _p, key, *_ in rows:
        fams.setdefault(ov.get(key, key.split("_")[0]), set()).add(key)
    return sum(1 for k, v in ov.items() if v == k or len(fams.get(v, ())) < 2)


# ---------------------------------------------------------------- C7
def unread_private_globals(ts: dict[str, ast.Module]) -> int:
    """Module-level private bindings (``_X = ...``) nothing in the package loads. A keep-alive
    registry that touches every dead member is one (attempt 08)."""
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


# ---------------------------------------------------------------- C4
def flatten(src: Path, dst: Path, inline: bool = True) -> int:
    """Copy ``src``'s package to ``dst`` with the coordinator's package-local base classes inlined.

    The coordinator is its MRO, not one class node. Every member a local base (defined in
    ``coordinator.py``, recursively) defines and the coordinator does not is moved into the
    coordinator's body -- the coordinator's own win, as the MRO would have it -- and the
    coordinator's bases become the bases' external bases. Every metric keyed on the coordinator
    class is then measured on the class the runtime builds. Identity on a tree whose coordinator
    has no local base. Returns the number of inlined bases (attempts 05c and 05d moved the whole
    class behind a rename, +101).
    """
    src, dst = Path(src), Path(dst)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src / PKG, dst / PKG, ignore=shutil.ignore_patterns("__pycache__"))
    p = dst / PKG / "coordinator.py"
    text = p.read_text()
    tree = ast.parse(text)
    classes = {n.name: n for n in tree.body if isinstance(n, ast.ClassDef)}
    coord = classes[C.COORD_CLASS]
    lines = text.splitlines(keepends=True)

    def names(body_stmts: list[ast.stmt]) -> set[str]:
        out = set()
        for s in body_stmts:
            if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                out.add(s.name)
            elif isinstance(s, ast.Assign):
                out |= {t.id for t in s.targets if isinstance(t, ast.Name)}
            elif isinstance(s, ast.AnnAssign) and isinstance(s.target, ast.Name):
                out.add(s.target.id)
        return out

    def start(s: ast.AST) -> int:
        return min([s.lineno] + [d.lineno for d in getattr(s, "decorator_list", [])])

    have = names(coord.body)
    extra, ext_bases, drop = [], [], []
    todo = [ast.unparse(b) for b in coord.bases]
    while todo:
        b = todo.pop(0)
        if b in classes and b != coord.name:
            base = classes[b]
            drop.append(base)
            for s in base.body:
                if isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant):
                    continue
                nm = names([s])
                if nm and nm <= have:
                    continue
                have |= nm
                extra.append("".join(lines[start(s) - 1:s.end_lineno]))
            todo += [ast.unparse(x) for x in base.bases]
        elif b not in ext_bases:
            ext_bases.append(b)
    if drop and inline:
        header = f"class {C.COORD_CLASS}({', '.join(ext_bases)}):\n"
        new = header + "".join(lines[coord.body[0].lineno - 1:coord.end_lineno]) + "\n" + "".join(extra)
        cut = {(start(c), c.end_lineno) for c in drop}
        out, i = [], 1
        for a, b in sorted(cut | {(start(coord), coord.end_lineno)}):
            out.append("".join(lines[i - 1:a - 1]))
            if (a, b) not in cut:
                out.append(new)
            i = b + 1
        out.append("".join(lines[i - 1:]))
        p.write_text("".join(out))
    return len(drop)
