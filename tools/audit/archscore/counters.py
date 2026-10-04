"""The counters: what keeps a score metric from being raised without improving the architecture.

The red team (``planted/redteam/``) raised the score with 13 of 16 moves that left the
architecture no better, from +0.5 to +160. A counter is a change to a metric's definition,
or a gate-only tripwire, so that the move reads as nothing or as inadmissible.

C1  an ``Any`` / ``object`` key is untyped              ``metrics/untyped_payload_keys.is_any``
C2  ``reflective_writes``, C2b ``computed_attr_access``  here; gate-only, weight 0. A write spelled
    reflectively is a write; the role engine does not yet read one as a write, so these
    only stop the count falling by re-spelling. They retire when it does.
C3  a clone window is any two statements of a block in order  ``gapped_clones``; replaces the shared
    census in the score's copy only (``vector.py``), so nothing interleaved splits a clone
C4  the coordinator is its whole package class hierarchy  ``flatten``
C5  a passthrough property is a reach                    ``passthrough_properties``; applied to the
    shared reach census by ``vector.py``
C6  ``family_orphan_overrides``                          here; gate-only
C7  ``unread_private_globals``                           here; gate-only
C11 literal keys read from a function's own ``**kw`` are parameters  ``metrics/footprint.params_over_10``
"""
from __future__ import annotations

import ast
import hashlib
import re
import shutil
from collections import defaultdict
from pathlib import Path

from .metrics import common as C
from .metrics import family_splits as F

PKG = C.PKG_REL
BUILTIN_TYPES = {"list", "dict", "set", "object", "frozenset", "bytearray", "deque", "OrderedDict", "defaultdict"}
DUNDER_WRITES = {"__setattr__", "__delattr__", "__setitem__", "__delitem__"}


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
_LOCAL = re.compile("\u27e6([^\u27e7]*)\u27e7")


def _statement_form(S, s: ast.stmt, local: set[str], modalias: set[str]) -> str:
    """``S.normalized_window``'s form of one statement with the function's own names left marked, so a
    window of any two statements renumbers them by first use exactly as ``normalized_window`` does
    (``ast.dump`` prints in the order ``NodeTransformer`` visits)."""
    class Normalize(ast.NodeTransformer):
        def visit_Attribute(self, n):
            self.generic_visit(n)
            if isinstance(n.value, ast.Name) and n.value.id in modalias and n.value.id not in local:
                return ast.copy_location(ast.Name(id=n.attr, ctx=n.ctx), n)
            return n

        def visit_Name(self, n):
            if n.id in local:
                n.id = "\u27e6" + n.id + "\u27e7"
            return n

        def visit_Constant(self, n):
            if isinstance(n.value, str):
                n.value = "S"
            return n
    return ast.dump(Normalize().visit(ast.parse(ast.unparse(s)).body[0]))


def gapped_clones(S, trees, gap: int | None = None) -> list[list[tuple[str, str, int]]]:
    """``S.duplicate_clones`` with a window of ANY two statements of a block, in order, instead of two
    adjacent ones. A copy keeps every statement of its original in order, so whatever is interleaved
    into it -- any spelling, any count, an effect or none -- leaves the original's pairs intact and the
    clone joined: the interleaving game (attempt 04 and every variant) fails by construction rather than
    by an enumeration of junk. Its adjacent pairs are the shared census's windows (the same copies at gap
    0, pinned by ``tests/arch_score.py``), so the score's count is a superset of the ratchet's. Nested
    definitions sit outside every window, as in the census. ``gap`` bounds the statements a window skips;
    ``0`` is the shared census, which ``tests/arch_score_head.py`` holds it to."""
    windows: dict[str, set] = defaultdict(set)
    for path, tree in trees:
        rel, modalias = str(path.relative_to(S.REPO_ROOT)), S._module_aliases(tree)
        for fn in S.all_functions(tree):
            local, owner, stack = S._local_names(fn), (rel, fn.name, fn.lineno), [fn]
            while stack:
                node = stack.pop()
                stack += [c for c in ast.iter_child_nodes(node)
                          if not isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef))]
                blocks = [getattr(node, f) for f in ("body", "orelse", "finalbody")
                          if isinstance(getattr(node, f, None), list) and getattr(node, f)
                          and isinstance(getattr(node, f)[0], ast.stmt)]
                for block in blocks + [h.body for h in getattr(node, "handlers", []) or []]:
                    block = [s for s in block if not S._is_docstring(s)
                             and not isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
                    size = [sum(1 for _ in ast.walk(s)) for s in block]
                    form: dict[int, str] = {}
                    for i in range(len(block)):
                        for j in range(i + 1, len(block) if gap is None else min(len(block), i + 2 + gap)):
                            if size[i] + size[j] < S.DUP_MIN_NODES:
                                continue
                            for k in (i, j):
                                if k not in form:
                                    form[k] = _statement_form(S, block[k], local, modalias)
                            names: dict[str, str] = {}
                            key = _LOCAL.sub(lambda m: names.setdefault(m.group(1), f"v{len(names)}"),
                                             form[i] + form[j])
                            windows[hashlib.sha1(key.encode()).hexdigest()].add(owner)
    parent: dict = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for owners in windows.values():
        first, *rest = sorted(owners)
        for other in rest:
            parent[find(other)] = find(first)
    groups: dict = defaultdict(list)
    for member in parent:
        groups[find(member)].append(member)
    return sorted(sorted(g) for g in groups.values() if len(g) > 1)


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
