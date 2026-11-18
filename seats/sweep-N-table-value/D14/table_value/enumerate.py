"""D14 sweep, class N-table-value: list every production numeric data table.

A seam is a module-level name in custom_components/heatpump_optimizer/**/*.py
whose assigned value is a dict/tuple/list/set literal (or a call wrapping one,
e.g. MappingProxyType({...}) / frozenset(...)) and whose evaluated runtime
value holds >= 3 numeric leaves (int/float, bool excluded).  The runtime value
is read by importing the module under tests/hastub, so names and arithmetic
resolve the way production computes with them.
Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/table_value/enumerate.py [--json] [--root DIR]
"""
import ast
import importlib
import json
import math
import os
import sys

ROOT = "custom_components"
PKG = "heatpump_optimizer"
args = sys.argv[1:]
if "--root" in args:
    ROOT = args[args.index("--root") + 1]
sys.path.insert(0, "tests")
sys.path.insert(0, ROOT)

LIT = (ast.Dict, ast.Tuple, ast.List, ast.Set, ast.DictComp, ast.ListComp)


def literal(node):
    if isinstance(node, LIT):
        return True
    if isinstance(node, ast.Call) and node.args and isinstance(node.args[0], LIT):
        return True
    return False


def leaves(v, seen=None):
    seen = seen if seen is not None else set()
    if id(v) in seen:
        return 0
    if isinstance(v, bool):
        return 0
    if isinstance(v, (int, float)):
        return 1
    if isinstance(v, dict) or hasattr(v, "items") and not isinstance(v, (str, bytes)):
        seen.add(id(v))
        try:
            return sum(leaves(x, seen) for x in v.values())
        except Exception:
            return 0
    if isinstance(v, (tuple, list, set, frozenset)):
        seen.add(id(v))
        return sum(leaves(x, seen) for x in v)
    if hasattr(v, "__dataclass_fields__"):
        seen.add(id(v))
        return sum(leaves(getattr(v, f), seen) for f in v.__dataclass_fields__)
    return 0


def seams():
    base = os.path.join(ROOT, PKG)
    out = []
    for dp, dn, fn in os.walk(base):
        dn[:] = sorted(d for d in dn if d not in ("www", "translations", "__pycache__"))
        for f in sorted(fn):
            if not f.endswith(".py"):
                continue
            path = os.path.join(dp, f)
            rel = os.path.relpath(path, ROOT)
            mod = rel[:-3].replace(os.sep, ".")
            if mod.endswith(".__init__"):
                mod = mod[: -len(".__init__")]
            tree = ast.parse(open(path, encoding="utf-8").read())
            cands = []
            for node in tree.body:
                tgt = None
                if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                    tgt, val = node.targets[0].id, node.value
                elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value is not None:
                    tgt, val = node.target.id, node.value
                if tgt and literal(val):
                    cands.append((tgt, node.lineno))
            if not cands:
                continue
            try:
                m = importlib.import_module(mod)
            except Exception as e:  # noqa: BLE001
                for tgt, ln in cands:
                    out.append({"file": os.path.join(ROOT, path[len(ROOT) + 1:]) if False else path, "symbol": tgt, "line": ln, "leaves": None, "error": repr(e)[:80]})
                continue
            for tgt, ln in cands:
                v = getattr(m, tgt, None)
                n = leaves(v)
                if n >= 3:
                    out.append({"file": path, "symbol": tgt, "line": ln, "leaves": n, "module": mod})
    return out


if __name__ == "__main__":
    s = seams()
    if "--json" in args:
        print(json.dumps(s, indent=1))
    else:
        for x in s:
            print(f"{x['file']}:{x['line']}  {x['symbol']}  leaves={x['leaves']}{'  ERROR ' + x['error'] if x.get('error') else ''}")
        print(f"RESULT seams={len(s)} count")
