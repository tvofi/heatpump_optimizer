"""shapes: one rule implemented by N functions (R10-ARCHSCORE-COVERAGE item 6; ARCH-s2 and ARCH2-s3, round 10).

The clone census (``duplication_copies``) joins functions sharing a window of two statements carrying at least
30 nodes, so a rule that is a whole small function -- an availability gate, a payload-number guard, an evidence
log -- written again under another name sits below the window and is invisible to it. ARCH-s2 drove such shapes
by hand (``shape_payload_guard.py``: 35 implementations of one payload guard), each with a seam rule of its own.

The SHAPE of a function is its body with its own names erased (counter C23): the docstring dropped, the
function's parameters and the names it binds numbered by first use, every number one ``N`` and every string one
``S`` (as the clone window reads strings), and a nested function its own shape (it is also its own unit), so a
decorator's wrapper is not every wrapper. Names it does not bind -- builtins, module globals, attributes -- stay:
a getter of ``_x`` is not a getter of ``_y``. A function under MIN_NODES nodes is not a rule
(``return self._x``).

  shape_copies   members of every shape class of two or more functions (as ``duplication_copies`` counts)

GATE ONLY (weight 0), by calibration, as item 6 requires. Weighted, it would be gamed: one statement re-spelled
(``raw < 0`` as ``0 > raw``) leaves the class while the rule is still written twice -- the planted
``a3_shape_copies_respelled_control`` is that BAD edit and reads NULL -- and on the corpus its one fall is a BAD
commit (``ca711b56``), so a weight would credit a defect. As a tripwire it costs nothing: on the 45 labelled
corpus commits it rises on five BAD and two NEUTRAL commits and one GOOD (``0323c5b8``), every one already
inadmissible, so it moves no recorded verdict; and it closes attempt 45, a ``duplication_copies`` class collapsed
below the window, which read IMPROVES without it. ``ABOUT.md`` carries the measurement.
"""
from __future__ import annotations

import ast
import copy
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

if __package__ in (None, ""):  # run as a script
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from archscore.metrics import common as C  # noqa: E402
else:
    from . import common as C

#: Nodes (expression contexts not counted) a shape needs to be a rule rather than an accessor.
MIN_NODES = 12
#: a string constant is one ``S``, as ``duplication_copies``' window reads it
STRINGS = True
#: Counter C23: own names numbered, numbers and strings abstracted. ``vector.py`` switches it off.
ERASE = True
_FN = (ast.FunctionDef, ast.AsyncFunctionDef)


def _bound(fn: ast.AST) -> set[str]:
    """The names ``fn`` binds itself: its parameters and every name stored in its own body."""
    a = fn.args
    out = {x.arg for x in (*a.posonlyargs, *a.args, *a.kwonlyargs, a.vararg, a.kwarg) if x is not None}
    stack = list(fn.body)
    while stack:
        n = stack.pop()
        if isinstance(n, (*_FN, ast.ClassDef, ast.Lambda)):
            if not isinstance(n, ast.Lambda):
                out.add(n.name)
            continue
        if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)):
            out.add(n.id)
        elif isinstance(n, ast.ExceptHandler) and n.name:
            out.add(n.name)
        elif isinstance(n, ast.alias):
            out.add((n.asname or n.name).split(".")[0])
        stack.extend(ast.iter_child_nodes(n))
    return out


class _Erase(ast.NodeTransformer):
    def __init__(self, own: set[str], root: ast.AST):
        self.own, self.num, self.root = own, {}, root

    def _v(self, name: str) -> str:
        return f"v{self.num.setdefault(name, len(self.num))}"

    def visit_FunctionDef(self, n):
        if n is not self.root:  # its own unit; it stands here as its own shape, so a wrapper is not every wrapper
            return ast.Expr(value=ast.Constant(value=f"F:{shape(n, floor=0)}"))
        self.generic_visit(n)
        return n

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, n):
        return ast.Expr(value=ast.Constant(value="C"))

    def visit_arg(self, n):
        n.arg = self._v(n.arg) if ERASE else n.arg
        n.annotation = None
        return n

    def visit_Name(self, n):
        if n.id in self.own:
            n.id = self._v(n.id)
        return n

    def visit_Constant(self, n):
        if not ERASE:
            return n
        if isinstance(n.value, (int, float, complex)) and not isinstance(n.value, bool):
            return ast.Constant(value="N")
        if STRINGS and isinstance(n.value, str):
            return ast.Constant(value="S")
        return n


def shape(fn: ast.AST, floor: int | None = None) -> str | None:
    """The shape key of one function, or None below ``floor`` nodes (default MIN_NODES)."""
    floor = MIN_NODES if floor is None else floor
    f = copy.deepcopy(fn)
    body = f.body
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
            and isinstance(body[0].value.value, str):
        body = body[1:] or [ast.Pass()]
    f.body, f.decorator_list, f.returns, f.name = body, [], None, "f"
    if sum(1 for y in ast.walk(ast.Module(body=body, type_ignores=[])) if not isinstance(y, ast.expr_context)) \
            < floor:
        return None
    e = _Erase(_bound(fn) if ERASE else set(), f)
    f.args = e.visit(f.args)
    f.body = [e.visit(s) for s in f.body]
    return ast.dump(ast.Module(body=f.body, type_ignores=[]))


def classes(root: Path) -> list[list[str]]:
    """Shape classes of two or more functions, each as sorted ``module:qualname`` members."""
    pkg = C.load(str(root))
    by: dict[str, list[str]] = defaultdict(list)
    for m, mod in pkg.mods.items():
        def walk(node, prefix):
            for c in ast.iter_child_nodes(node):
                if isinstance(c, _FN):
                    k = shape(c)
                    if k is not None:
                        by[k].append(f"{m}:{prefix}{c.name}")
                    walk(c, f"{prefix}{c.name}.")
                elif isinstance(c, ast.ClassDef):
                    walk(c, f"{prefix}{c.name}.")
                else:
                    walk(c, prefix)
        walk(mod.tree, "")
    return sorted((sorted(v) for v in by.values() if len(v) > 1), key=lambda g: (-len(g), g))


def measure(root: Path) -> dict:
    t0 = time.perf_counter()
    found = classes(root)
    return {"metric": "shapes", "shape_copies": sum(len(g) for g in found),
            "details": {"classes": len(found), "largest": found[:8]},
            "runtime_s": round(time.perf_counter() - t0, 3)}


if __name__ == "__main__":
    print(json.dumps(measure(Path(sys.argv[1] if len(sys.argv) > 1 else ".")), indent=1))
