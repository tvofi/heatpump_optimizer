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
# Builtins that neither iterate nor mutate an argument (``list``, ``sum``, ``sorted`` iterate, and iterating
# an iterator consumes it), so a call of one is no effect outside its own result.
PURE = {"id", "len", "hash", "repr", "type", "str", "bool", "int", "float", "isinstance", "issubclass", "callable",
        "abs", "round", "divmod", "ord", "chr", "hex", "oct", "bin", "ascii", "complex"}


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
# lambda, or a method of a value built from literals, every subscript and comprehension reads a value built
# from literals, and every name it binds is dead. A class by grammar, closed under composition, not a
# spelling list.
_PURE_NODES = (ast.Constant, ast.Name, ast.Load, ast.Store, ast.Attribute, ast.Tuple, ast.List, ast.Set,
               ast.Dict, ast.Starred, ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare, ast.IfExp, ast.Lambda,
               ast.arguments, ast.arg, ast.NamedExpr, ast.Call, ast.keyword, ast.JoinedStr, ast.FormattedValue,
               ast.operator, ast.unaryop, ast.boolop, ast.cmpop, ast.Subscript, ast.Slice, ast.ListComp,
               ast.SetComp, ast.DictComp, ast.GeneratorExp, ast.comprehension)


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
    """Effect-free. A subscript or a comprehension's iterable must be built from literals: indexing or
    iterating anything else can run code that changes it (a defaultdict, an iterator)."""
    return e is None or all(
        isinstance(n, _PURE_NODES)
        and not (isinstance(n, ast.Call) and not _pure_call(n))
        and not (isinstance(n, ast.NamedExpr) and n.target.id not in dead)
        and not (isinstance(n, ast.Subscript) and not _literal(n))
        and not (isinstance(n, ast.comprehension) and (not _literal(n.iter) or n.is_async))
        for n in ast.walk(e))


def _fold(e: ast.AST, dead: set[str]):
    """``(True, value)`` for an effect-free expression reading no name but a PURE builtin, else
    ``(False, None)``. No ``**``, ``<<`` or ``*``, so the value is no larger than the literals that spell
    it and evaluating it is bounded (``"x" * 10**10`` and ``[0] * 99999999999`` are refused, not run), no
    attribute, so nothing reachable from a literal's type is evaluated, and no comprehension or subscript."""
    if not _pure(e, dead) or any(isinstance(n, (ast.Pow, ast.LShift, ast.Mult, ast.MatMult, ast.NamedExpr, ast.Lambda,
                                                ast.Attribute, ast.Subscript, ast.comprehension))
                                 for n in ast.walk(e)) \
            or any(isinstance(n, ast.Name) and n.id not in PURE for n in ast.walk(e)):
        return False, None
    try:
        return True, eval(compile(ast.Expression(e), "<c3>", "eval"),  # noqa: S307 -- grammar above
                          {"__builtins__": {k: __builtins__[k] if isinstance(__builtins__, dict)
                                            else getattr(__builtins__, k) for k in PURE}})
    except Exception:  # noqa: BLE001 -- an expression that raises is not inert
        return False, None


class _Scope:
    """What C3 knows about one function: the names it binds that nothing reads (``dead``), the names
    bound in it other than by a self-assignment (``bound``: the parameters and every other store), every
    name it mentions (``named``), and the modules its file imports at top level (``imported``)."""

    def __init__(self, fn: ast.AST, imported: set[str]):
        self.imported = imported
        stored, live, self.named, self.bound = set(), set(), set(), set()
        for n in ast.walk(fn):
            if isinstance(n, ast.Name):
                self.named.add(n.id)
                (live if isinstance(n.ctx, ast.Load) else stored).add(n.id)
            elif isinstance(n, ast.arg):
                self.bound.add(n.arg)
            elif isinstance(n, (ast.Global, ast.Nonlocal)):
                live |= set(n.names)
            elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n is not fn:
                stored.add(n.name)
                if isinstance(n, ast.ClassDef):  # a class body's binding is an attribute, read from outside it
                    live |= {t.id for b in n.body for t in ast.walk(b)
                             if isinstance(t, ast.Name) and isinstance(t.ctx, ast.Store)
                             and not isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}
            elif isinstance(n, (ast.Import, ast.ImportFrom)):
                stored |= {(a.asname or a.name).split(".")[0] for a in n.names}
        self.dead = stored - live
        # a store that binds a value: not one inside a self-assignment, and not an annotation alone
        skip = {id(n) for x in ast.walk(fn) if _self_assign(x) or (isinstance(x, ast.AnnAssign) and x.value is None)
                for n in ast.walk(x)}
        self.bound |= {n.id for n in ast.walk(fn)
                       if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store) and id(n) not in skip}


def _self_assign(s: ast.stmt) -> bool:
    """``x = x`` or ``a, b = a, b``: every target the same plain name as the value in its place."""
    def same(t, v):
        if isinstance(t, ast.Name) and isinstance(v, ast.Name):
            return t.id == v.id
        return isinstance(t, (ast.Tuple, ast.List)) and isinstance(v, (ast.Tuple, ast.List)) \
            and len(t.elts) == len(v.elts) and all(same(a, b) for a, b in zip(t.elts, v.elts))
    return isinstance(s, ast.Assign) and all(same(t, s.value) for t in s.targets)


def _inert_def(s: ast.stmt, sc: _Scope) -> bool:
    """A nested ``def`` or ``class`` nothing names: no decorator, defaults and annotations effect-free, and
    for a class no base, no keyword and a body of inert statements (a base's ``__init_subclass__`` or a
    metaclass would run code)."""
    if s.decorator_list or s.name not in sc.dead:
        return False
    if isinstance(s, ast.ClassDef):
        return not s.bases and not s.keywords and all(_inert(x, sc) for x in s.body)
    a = s.args
    notes = [x.annotation for x in (*a.posonlyargs, *a.args, *a.kwonlyargs, a.vararg, a.kwarg) if x is not None]
    return all(_pure(x, sc.dead) for x in (*a.defaults, *[d for d in a.kw_defaults if d is not None],
                                            *notes, s.returns))


def _inert_import(s: ast.stmt, sc: _Scope) -> bool:
    """An import whose names nothing reads, of a module the file already imports at top level: the import
    is a lookup in ``sys.modules``, its module code ran when the file loaded. A relative or a star import
    is never inert."""
    if isinstance(s, ast.ImportFrom) and (s.level or s.module is None or any(a.name == "*" for a in s.names)):
        return False
    mods = [s.module] if isinstance(s, ast.ImportFrom) else [a.name for a in s.names]
    return all(m in sc.imported for m in mods) \
        and all((a.asname or a.name).split(".")[0] in sc.dead for a in s.names)


def _inert_match(s: ast.stmt, sc: _Scope) -> bool:
    """A ``match`` on an effect-free subject, whose patterns capture only dead names and compare only
    effect-free values (no class pattern, which calls ``isinstance`` and ``__match_args__``), whose guards
    are effect-free and whose every case body is inert."""
    ok = (ast.MatchValue, ast.MatchSingleton, ast.MatchSequence, ast.MatchAs, ast.MatchOr, ast.MatchStar)
    return _pure(s.subject, sc.dead) and all(
        all(isinstance(p, ok) or not isinstance(p, ast.pattern) for p in ast.walk(c.pattern))
        and all(getattr(p, "name", None) in (None, *sc.dead) for p in ast.walk(c.pattern)
                if isinstance(p, (ast.MatchAs, ast.MatchStar)))
        and all(_pure(p.value, sc.dead) for p in ast.walk(c.pattern) if isinstance(p, ast.MatchValue))
        and _pure(c.guard, sc.dead) and all(_inert(x, sc) for x in c.body)
        for c in s.cases)


def _inert(s: ast.stmt, sc: _Scope) -> bool:
    """A statement whose execution changes nothing the function can observe afterwards."""
    dead = sc.dead
    every = lambda body: all(_inert(x, sc) for x in body)  # noqa: E731
    if isinstance(s, ast.Pass):
        return True
    if isinstance(s, ast.Expr):
        return _pure(s.value, dead)
    if isinstance(s, (ast.Global, ast.Nonlocal)):
        # a declaration changes only where later uses of its names resolve; with no use there is none
        return not set(s.names) & sc.named
    if _self_assign(s):
        # rebinding a name to its own value; the name must be bound already, by a parameter or another store
        return all(n.id in sc.bound for t in s.targets for n in ast.walk(t) if isinstance(n, ast.Name))
    if isinstance(s, ast.AnnAssign) and s.value is None:
        # a local annotation is never evaluated and binds nothing; it only makes the name local
        return isinstance(s.target, ast.Name) and (s.target.id in sc.bound or s.target.id in dead)
    if isinstance(s, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Delete)):
        targets = s.targets if isinstance(s, (ast.Assign, ast.Delete)) else [s.target]
        return all(isinstance(n, (ast.Name, ast.Tuple, ast.List, ast.Starred, ast.Store, ast.Del))
                   and not (isinstance(n, ast.Name) and n.id not in dead)
                   for x in targets for n in ast.walk(x)) and _pure(getattr(s, "value", None), dead)
    if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return _inert_def(s, sc)
    if isinstance(s, (ast.Import, ast.ImportFrom)):
        return _inert_import(s, sc)
    if isinstance(s, ast.Match):
        return _inert_match(s, sc)
    if type(s).__name__ == "TypeAlias":  # 3.12+: the value is evaluated lazily, so only the binding counts
        return isinstance(s.name, ast.Name) and s.name.id in dead
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
    if isinstance(s, (ast.Try, getattr(ast, "TryStar", ast.Try))):
        return every(s.body) and every(s.orelse) and every(s.finalbody) and all(every(h.body) for h in s.handlers)
    return False


def _top_imports(tree: ast.AST) -> set[str]:
    """Modules a file imports at top level (unconditionally): already in ``sys.modules`` once it loaded."""
    out: set[str] = set()
    for s in getattr(tree, "body", []):
        if isinstance(s, ast.Import):
            for a in s.names:
                parts = a.name.split(".")
                out |= {".".join(parts[:i + 1]) for i in range(len(parts))}
        elif isinstance(s, ast.ImportFrom) and not s.level and s.module:
            out.add(s.module)
    return out | {"sys", "builtins"}


def inert_statements(trees, all_functions) -> set[int]:
    """``id()`` of every statement dead by data flow in the package's functions, dropped before a clone
    window is cut so junk interleaved in every window does not split the clone (attempt 04: 121 -> 7;
    04h to 04v are the spellings an enumeration missed). Dead (``_inert``): an effect-free expression; a
    store, delete or annotation binding only names nothing reads; a self-assignment of a bound name; a
    ``global`` or ``nonlocal`` of names the function never uses; a nested ``def`` or ``class`` nothing
    names; an import already done at top level, binding a dead name; a ``match``, ``assert``, ``if``,
    ``while`` or ``for`` judged on what can run; a ``try`` on its every part. Each function is judged with
    its own reads; an enclosing function reads a superset, so the union never drops a live statement.

    Out of the class, and so still open: a statement with an effect the grammar cannot rule out (a call
    of anything else, a write through an attribute or a subscript, an ``assert`` that can fail, a ``with``),
    which is logic in the diff. A gap tolerance in the window would close that too, but it redefines the
    window tests/structure.py shares, so it is not here (ABOUT.md, "Interleaved junk")."""
    out: set[int] = set()
    for _path, tree in trees:
        imported = _top_imports(tree)
        for fn in all_functions(tree):
            sc = _Scope(fn, imported)
            out |= {id(s) for s in ast.walk(fn) if isinstance(s, ast.stmt) and s is not fn and _inert(s, sc)}
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
