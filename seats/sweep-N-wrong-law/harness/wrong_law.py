#!/usr/bin/env python3
"""Enumerate N-wrong-law seams: a physical law coded as an affine correction
`c ± term` that is then clamped (min/max/clip/clamp), the shape in which a
wrong operator or sign is silently pinned to a bound so the effect never acts.

A seam is every min()/max()/clip()/clamp*()/np.clip call (nested pairs counted
once, at the outer call) one of whose arguments is a BinOp Add/Sub with a
numeric-constant or constant-name operand (c ± term or term ± c), plus every
call whose argument is such a clamp. Each seam is printed with its bounds and
`pinned` when the bound equals the affine constant on the side the operator
pushes towards (e.g. min(1.0, ... 1.0 + t ...)): for a nonnegative term that
seam can never leave the bound, which is the D2-s2-02 signature.
Usage: wrong_law.py [ROOT] [--json]
"""
import ast, json, sys
from pathlib import Path

CLAMPS = {"min", "max", "clip", "clamp", "_clamp", "clamp01", "_clip"}


def cname(f):
    return f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)


def is_const(n, consts):
    if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool):
        return True
    if isinstance(n, ast.UnaryOp) and isinstance(n.operand, ast.Constant):
        return True
    nm = n.id if isinstance(n, ast.Name) else (n.attr if isinstance(n, ast.Attribute) else None)
    return bool(nm and nm.isupper())


def law_const(n):
    """The affine constant of a law: a float literal or a named constant, not an
    integer offset (index arithmetic such as i + 1 or len(x) - 1)."""
    if isinstance(n, ast.Constant):
        return isinstance(n.value, float)
    if isinstance(n, ast.UnaryOp):
        return isinstance(getattr(n.operand, "value", None), float)
    return True


def val(n, consts):
    try:
        return float(ast.literal_eval(n))
    except Exception:
        nm = n.id if isinstance(n, ast.Name) else (n.attr if isinstance(n, ast.Attribute) else None)
        return consts.get(nm)


def affine(n, consts):
    """Yield (const_value_or_name, op, term_src) for c ± term inside n (top-level only)."""
    if isinstance(n, ast.BinOp) and isinstance(n.op, (ast.Add, ast.Sub)):
        for c, t, side in ((n.left, n.right, "L"), (n.right, n.left, "R")):
            if is_const(c, consts) and not is_const(t, consts) and law_const(c):
                op = "+" if isinstance(n.op, ast.Add) else ("-" if side == "L" else "+rev")
                return (val(c, consts), ast.unparse(c), op, ast.unparse(t))
    return None


def scan(root):
    out = []
    for f in sorted(Path(root).rglob("*.py")):
        try:
            tree = ast.parse(f.read_text())
        except SyntaxError:
            continue
        consts = {}
        for n in tree.body:
            if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
                try:
                    consts[n.targets[0].id] = float(ast.literal_eval(n.value))
                except Exception:
                    pass
        inner = set()
        owner = {}
        for fn in ast.walk(tree):
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for n in ast.walk(fn):
                    owner[id(n)] = fn.name
        for call in ast.walk(tree):
            if not (isinstance(call, ast.Call) and cname(call.func) in CLAMPS) or id(call) in inner:
                continue
            bounds, hits = [], []
            stack = [(call, cname(call.func))]
            while stack:
                c, kind = stack.pop()
                for i, a in enumerate(c.args):
                    if kind in ("clip", "clamp", "_clamp", "_clip") and i in (1, 2) and is_const(a, consts):
                        bounds.append(("max" if i == 1 else "min", val(a, consts)))
                        continue
                    if isinstance(a, ast.Call) and cname(a.func) in CLAMPS:
                        inner.add(id(a)); stack.append((a, cname(a.func)))
                    elif is_const(a, consts):
                        bounds.append((kind, val(a, consts)))
                    else:
                        aff = affine(a, consts)
                        if aff:
                            hits.append(aff)
            if not hits:
                continue
            for cv, csrc, op, term in hits:
                ups = [b for k, b in bounds if k == "min" and b is not None]
                los = [b for k, b in bounds if k == "max" and b is not None]
                pinned = (cv is not None and ((op == "+" and ups and min(ups) <= cv)
                                              or (op == "-" and los and max(los) >= cv)))
                out.append({"file": str(f), "line": call.lineno, "symbol": owner.get(id(call), "<module>"),
                            "expr": ast.unparse(call)[:140], "const": csrc, "op": op, "term": term[:60],
                            "upper": min(ups) if ups else None, "lower": max(los) if los else None,
                            "pinned": bool(pinned)})
    return out


args = [a for a in sys.argv[1:] if not a.startswith("--")]
seams = scan(args[0] if args else "custom_components/heatpump_optimizer")
if "--json" in sys.argv:
    print(json.dumps(seams, indent=1))
else:
    for s in seams:
        print(f"{'PINNED ' if s['pinned'] else ''}{s['file']}:{s['line']} {s['symbol']} :: {s['expr']}")
    print(f"seams={len(seams)} pinned={sum(s['pinned'] for s in seams)}")
