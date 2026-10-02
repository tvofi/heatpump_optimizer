"""Prototype P3 rule: one floor per quantity, and no raw divisor beside it.

Every `max(E, c)` / `max(c, E)` with c a positive constant (literal or SCREAMING_CASE name) is a
FLOOR of E, whatever role it then plays. Every right operand of `/` or `//` that is not itself a
floor is a RAW DIVISOR. E is resolved through single-assignment locals (recursively, depth 4),
`float()`/`int()` are transparent, and attribute chains are cut to their leaf, so `p_range` in
one method and `p_max - p_min` in another key alike when both come from the same attributes. A key
still naming an unresolved local is scoped to its function.

A GROUP is a key that is: floored in more than one function ("dup"); floored with two constants
("mixed"); or floored anywhere and divided raw anywhere ("raw").
"""
import ast, sys
from collections import defaultdict
from pathlib import Path


def const(n):
    if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool):
        return float(n.value)
    if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
        v = const(n.operand)
        return -v if isinstance(v, float) else None
    if isinstance(n, ast.Name) and n.id.isupper():
        return n.id
    return None


class Resolver(ast.NodeTransformer):
    def __init__(self, alias, depth=0):
        self.alias, self.depth = alias, depth

    def visit_Attribute(self, n):
        return ast.Name(id=n.attr, ctx=ast.Load())

    def visit_Name(self, n):
        if n.id in self.alias and self.depth < 4:
            return Resolver(self.alias, self.depth + 1).visit(_copy(self.alias[n.id]))
        return n

    def visit_Call(self, n):
        if isinstance(n.func, ast.Name) and n.func.id in ("float", "int") and len(n.args) == 1 and not n.keywords:
            return self.visit(n.args[0])
        return self.generic_visit(n)


def _copy(node):
    return ast.parse(ast.unparse(node), mode="eval").body


def floor_of(node):
    """(E, c) when node is max(E, c>0) or max(c>0, E), else None."""
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "max" \
            and len(node.args) == 2 and not node.keywords:
        a, b = node.args
        for q, c in ((a, b), (b, a)):
            cv = const(c)
            if cv is not None and (isinstance(cv, str) or cv > 0) and const(q) is None:
                return q, cv
    return None


def scan(sources):
    floored, raw = defaultdict(list), defaultdict(list)
    for mod, src in sources.items():
        for fn in ast.walk(ast.parse(src)):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            assigns = defaultdict(list)
            for n in ast.walk(fn):
                if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
                    assigns[n.targets[0].id].append(n.value)
                elif isinstance(n, (ast.AugAssign, ast.AnnAssign, ast.For, ast.NamedExpr)):
                    t = getattr(n, "target", None)
                    if isinstance(t, ast.Name):
                        assigns[t.id].append(None)
            alias = {k: v[0] for k, v in assigns.items() if len(v) == 1 and v[0] is not None and const(v[0]) is None
                     and k not in {x.id for x in ast.walk(v[0]) if isinstance(x, ast.Name)}}
            params = {a.arg for a in fn.args.args + fn.args.kwonlyargs + fn.args.posonlyargs}
            local = (set(assigns) - set(alias)) | params
            tag = f"{mod}:{fn.name}"

            def key(e):
                r = Resolver(alias).visit(_copy(e))
                names = {x.id for x in ast.walk(r) if isinstance(x, ast.Name)}
                txt = ast.unparse(r)
                return f"{tag}::{txt}" if names & local else txt

            for n in ast.walk(fn):
                f = floor_of(n)
                if f:
                    floored[key(f[0])].append((str(f[1]), f"{mod}:{n.lineno}", tag))
                if isinstance(n, ast.BinOp) and isinstance(n.op, (ast.Div, ast.FloorDiv)):
                    d = n.right
                    if floor_of(d) or const(d) is not None:
                        continue
                    if floor_of(Resolver(alias).visit(_copy(d))):
                        continue  # a local that IS a floor (c = max(Q, k); x / c)
                    raw[key(d)].append((f"{mod}:{n.lineno}", tag))
    groups = {}
    for k, fl in floored.items():
        kinds = []
        if len({c for c, _, _ in fl}) > 1:
            kinds.append("mixed")
        if len({f for _, _, f in fl}) > 1:
            kinds.append("dup")
        if raw.get(k):
            kinds.append("raw")
        if kinds:
            groups[k] = (kinds, fl, raw.get(k, []))
    return groups


def params_fields(sources):
    """Every field and property of ThermalParameters: the quantities the class is about."""
    out = set()
    for node in ast.walk(ast.parse(sources["thermal_model"])):
        if isinstance(node, ast.ClassDef) and node.name == "ThermalParameters":
            for b in node.body:
                if isinstance(b, ast.AnnAssign) and isinstance(b.target, ast.Name):
                    out.add(b.target.id)
                elif isinstance(b, ast.FunctionDef) and any(
                        isinstance(d, ast.Name) and d.id == "property" for d in b.decorator_list):
                    out.add(b.name)
    return out


def physical(groups, fields):
    """Groups whose key reads a ThermalParameters quantity and no unresolved local."""
    keep = {}
    for k, v in groups.items():
        if "::" in k:
            continue
        names = {x.id for x in ast.walk(ast.parse(k, mode="eval").body) if isinstance(x, ast.Name)}
        if names & fields and all(n in fields or n.isupper() for n in names):
            keep[k] = v
    return keep


def load(root):
    return {p.stem: p.read_text() for p in sorted(Path(root).glob("*.py"))}


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "custom_components/heatpump_optimizer"
    src = load(root)
    g = scan(src)
    if "--all" not in sys.argv:
        g = physical(g, params_fields(src))
    for k, (kinds, fl, rw) in sorted(g.items()):
        print(f"GROUP {','.join(kinds):14s} {k}  floored={[(c, s) for c, s, _ in fl]} raw={[s for s, _ in rw][:5]}{'...' if len(rw) > 5 else ''}")
    print(f"RESULT p3_groups={len(g)} dup={sum('dup' in v[0] for v in g.values())} "
          f"mixed={sum('mixed' in v[0] for v in g.values())} raw={sum('raw' in v[0] for v in g.values())}")
