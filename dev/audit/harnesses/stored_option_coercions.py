#!/usr/bin/env python3
"""Enumerate every unguarded float()/int() coercion of a value read off a mapping in the package.

WHY IT EXISTS. R11-LATE-P1-OPTIONS: a stored option of the wrong type raised in the readers that
coerced it with a bare ``float()``. The round-11 P1 sweep's ``opt-float`` rule
(``dev/audit/rounds/round11/sweep/P1/D14/sweep-P1/p1_seams.py``) keys on the receiver's NAME (a
fixed list of mapping names), so a reader whose mapping is called ``current``, ``answers`` or
``stored`` was outside it. This rule keys on the shape instead, over any receiver, and on two
spellings: the ``.get(...)`` inside the coerced expression (``direct``), and a local name assigned
from an expression holding a ``.get(...)`` earlier in the same function (``via-name``). A call
inside a ``try`` catching ``TypeError``, ``ValueError`` or ``Exception`` is guarded and not listed.

The rule's output is a superset of the stored-option readers: most seams read a store payload, a
computed dict or a feed. Which mapping a seam reads is a judgement the rule cannot make, so the
pull request that runs it dispositions every seam it prints. ``PRECONDITION`` drives the same walk
over a planted module carrying one seam of each spelling and one guarded call, and refuses unless
exactly the two seams are listed, so a walk that matches nothing cannot print a zero.

    python3 dev/audit/harnesses/stored_option_coercions.py <repo>
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

COERCIONS = ("float", "int")
CAUGHT = ("TypeError", "ValueError", "Exception")
PACKAGE = "custom_components/heatpump_optimizer"

PRECONDITION = '''
def direct(config):
    return float(config.get("a"))

def via_name(current):
    value = current.get("b")
    return int(value)

def guarded(config):
    try:
        return float(config.get("c"))
    except (TypeError, ValueError):
        return None
'''


def _has_get(node: ast.AST) -> bool:
    return any(
        isinstance(g, ast.Call) and isinstance(g.func, ast.Attribute) and g.func.attr == "get"
        for g in ast.walk(node)
    )


def _guarded(node: ast.AST, parents: dict[ast.AST, ast.AST]) -> bool:
    while node in parents:
        node = parents[node]
        if isinstance(node, ast.Try):
            for handler in node.handlers:
                if handler.type is None:
                    return True
                types = handler.type.elts if isinstance(handler.type, ast.Tuple) else [handler.type]
                if any(getattr(t, "id", "") in CAUGHT for t in types):
                    return True
    return False


def seams(source: str, label: str) -> list[str]:
    """``<coercion> <spelling> <label>:<line> <function>`` for each unguarded seam in ``source``."""
    tree = ast.parse(source)
    parents = {c: p for p in ast.walk(tree) for c in ast.iter_child_nodes(p)}
    found: set[tuple[int, int, str]] = set()
    out = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        from_get = {
            target.id
            for stmt in ast.walk(fn)
            if isinstance(stmt, (ast.Assign, ast.AnnAssign)) and stmt.value is not None
            and _has_get(stmt.value)
            for target in (stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target])
            if isinstance(target, ast.Name)
        }
        for call in ast.walk(fn):
            if not (isinstance(call, ast.Call) and getattr(call.func, "id", "") in COERCIONS
                    and call.args):
                continue
            arg = call.args[0]
            if _has_get(arg):
                spelling = "direct"
            elif any(isinstance(n, ast.Name) and n.id in from_get for n in ast.walk(arg)):
                spelling = "via-name"
            else:
                continue
            key = (call.lineno, call.col_offset, call.func.id)
            if key in found or _guarded(call, parents):
                continue
            found.add(key)
            out.append(f"{call.func.id} {spelling} {label}:{call.lineno} {fn.name}")
    return sorted(out, key=lambda s: (s.split()[2].split(":")[0], int(s.split()[2].split(":")[1]), s))


def main() -> int:
    planted = seams(PRECONDITION, "planted.py")
    if [s.split()[:2] for s in planted] != [["float", "direct"], ["int", "via-name"]]:
        print(f"REFUSED: the precondition module read {planted}, not one seam of each spelling")
        return 1
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".") / PACKAGE
    files = sorted(root.glob("*.py"))
    if not files:
        print(f"REFUSED: no module under {root}")
        return 1
    total = []
    for path in files:
        total += seams(path.read_text(), path.name)
    for seam in total:
        print(f"SEAM {seam}")
    for kind in COERCIONS:
        for spelling in ("direct", "via-name"):
            n = sum(1 for s in total if s.split()[:2] == [kind, spelling])
            print(f"RESULT {kind}_{spelling.replace('-', '_')}={n}")
    print(f"RESULT seams={len(total)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
