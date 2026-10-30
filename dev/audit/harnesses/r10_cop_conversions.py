"""R10-COP-PARTLOAD: every conversion between heat and electrical power
through a COP in the production package, by AST.

    python3 dev/audit/harnesses/r10_cop_conversions.py [ROOT]

ROOT defaults to ``custom_components/heatpump_optimizer``. A hit is a
division whose divisor is COP-shaped (heat to power) or a product with a
COP-shaped factor (power to heat), as a ``BinOp`` or an augmented
assignment. COP-shaped: a name, attribute, call or subscript whose
identifier contains ``cop`` (any case), but not ``copy`` or ``scope`` and not
one of the conversion helpers themselves; a product of such terms
(``cop * dt``); or a ``max``/``min``/``float``/``abs`` wrapping one
(``max(dt * cop_j, 1e-6)``). Only the outermost hit of a nested pair is
printed, so ``take / (cop * dt)`` is one hit, not two. Each line is
``file:line:function:DIV|MUL:ROUTED|PLAIN: expression``; the function
anchors the hit when a line shifts. ``ROUTED`` marks a hit that goes through
a helper: an argument of one, or a product with one's result
(``cop * heat_per_cop_kw(...)``). The last lines are ``RESULT hits=<n>`` and
``RESULT plain=<n>``.

The rule is lexical by design: it over-fires on COP-named constants that are
not a coefficient of performance (``COP_HEALTH_THRESHOLD``), which a
disposition answers, and it cannot see a COP that was renamed before the
conversion (a ``heat_per_kwh`` variable), which is why the heat-per-COP
helpers in ``thermal_model.py`` are the only sanctioned conversion route.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

_COP = re.compile(r"cop", re.I)
_NOT_COP = re.compile(r"copy|scope", re.I)
HELPERS = {"heat_per_cop_kw", "power_for_heat_per_cop_kw", "delivered_heat_kw"}
_WRAPPERS = {"max", "min", "float", "abs", "maximum", "minimum"}


def _ident(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, (ast.Call, ast.Subscript)):
        return _ident(node.func if isinstance(node, ast.Call) else node.value)
    return None


def _copish(node: ast.AST) -> bool:
    name = _ident(node)
    if isinstance(node, ast.Call) and name in _WRAPPERS:
        return any(_copish(arg) for arg in node.args)
    if name and _COP.search(name) and not _NOT_COP.search(name) and name not in HELPERS:
        return True
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
        return _copish(node.left) or _copish(node.right)
    return False


def _hit(op: ast.operator, left: ast.AST, right: ast.AST) -> str | None:
    if isinstance(op, ast.Div) and _copish(right):
        return "DIV"
    if isinstance(op, ast.Mult) and (_copish(left) or _copish(right)):
        return "MUL"
    return None


def _helper_call(node: ast.AST) -> bool:
    return isinstance(node, ast.Call) and _ident(node) in HELPERS


def scan(root: Path) -> list[str]:
    out: list[tuple[str, int, str]] = []
    for path in sorted(root.rglob("*.py")):
        tree = ast.parse(path.read_text(), filename=str(path))
        rel = path.relative_to(root)

        def walk(node: ast.AST, func: str, inside: bool, routed: bool) -> None:
            kind = None
            if isinstance(node, ast.BinOp):
                kind = _hit(node.op, node.left, node.right)
                pair = (node.left, node.right)
            elif isinstance(node, ast.AugAssign):
                kind = _hit(node.op, node.target, node.value)
                pair = (node.target, node.value)
            if kind and not inside:
                route = "ROUTED" if routed or any(map(_helper_call, pair)) else "PLAIN"
                out.append((str(rel), node.lineno, f"{rel}:{node.lineno}:{func}:"
                            f"{kind}:{route}: {ast.unparse(node)}"))
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func = node.name
            for child in ast.iter_child_nodes(node):
                arg = _helper_call(node) and child in node.args
                walk(child, func, inside or bool(kind), routed or arg)

        walk(tree, "<module>", False, False)
    return [line for _, _, line in sorted(out)]


def main(argv: list[str]) -> int:
    root = Path(argv[1] if len(argv) > 1 else "custom_components/heatpump_optimizer")
    hits = scan(root)
    for line in hits:
        print(line)
    print(f"RESULT hits={len(hits)}")
    print(f"RESULT plain={sum(':PLAIN: ' in line for line in hits)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
