#!/usr/bin/env python3
"""Prototype definitions for the proposed metric fixes, measured on a worktree.

private_reach        coord._x reads/writes (and getattr(coord, "_x")) from any code
                     outside the coordinator class body -- a name bound to the
                     coordinator is a parameter/variable named coord/coordinator
coord_footprint      logical statements (docstrings excluded) in the coordinator
                     class + in every function whose first parameter is coord/
                     coordinator, in any module
coord_writers_multi  coordinator attrs written (attr store, subscript/attr store
                     through it, or in-place method call on it) by >1 function,
                     counting writers inside AND outside the class
import_cycle_modules modules in a non-trivial SCC of the package import graph,
                     function-scope imports included
dup_pairs            function pairs, package-wide, sharing a window of DUP_W (default 2)
                     consecutive statements with identical ast.dump, string literals
                     blanked (>= DUP_NODES, default 30, AST nodes): formatting-blind and module-blind
params_over_10       functions with more than 10 parameters (self/cls excluded)
logical_max_fn       most logical statements in one function (docstrings excluded)
"""
import ast, hashlib, json, sys, pathlib
from collections import defaultdict

wt = pathlib.Path(sys.argv[1]); PKG = wt / "custom_components/heatpump_optimizer"
CLS = "HeatPumpOptimizerCoordinator"; CN = {"coord", "coordinator"}
trees = {p.stem: ast.parse(p.read_text()) for p in sorted(PKG.glob("*.py"))}
MUT = {"append", "extend", "update", "pop", "clear", "insert", "remove", "setdefault", "add", "discard"}

def is_doc(s):
    return isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and isinstance(s.value.value, str)

def stmts(node):
    return sum(1 for n in ast.walk(node) if isinstance(n, ast.stmt) and not is_doc(n)
               and not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)))

coord_cls = next(n for n in ast.walk(trees["coordinator"]) if isinstance(n, ast.ClassDef) and n.name == CLS)
in_cls = {id(n) for n in ast.walk(coord_cls)}

def root_attr(node):
    """For coord.X / coord.X[..] / coord.X.y, return X if rooted at a coordinator name."""
    while isinstance(node, (ast.Subscript, ast.Attribute)):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            return node.value.id, node.attr
        node = node.value
    return None, None

reach = 0; foot = stmts(coord_cls)
writers = defaultdict(set)
funcs = [(m, fn) for m, t in trees.items() for fn in ast.walk(t) if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef))]
for m, fn in funcs:
    inside = id(fn) in in_cls
    names = {"self"} if inside else CN
    if not inside:
        args = fn.args.posonlyargs + fn.args.args
        if args and args[0].arg in CN and fn in trees[m].body:
            foot += stmts(fn)
    for n in ast.walk(fn):
        if not inside and isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id in CN \
                and n.attr.startswith("_") and not n.attr.startswith("__"):
            reach += 1
        if not inside and isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "getattr" \
                and n.args and isinstance(n.args[0], ast.Name) and n.args[0].id in CN and len(n.args) > 1 \
                and isinstance(n.args[1], ast.Constant) and str(n.args[1].value).startswith("_"):
            reach += 1
        targets = []
        if isinstance(n, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            targets = n.targets if isinstance(n, ast.Assign) else [n.target]
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in MUT:
            targets = [n.func.value]
        for tg in targets:
            base, attr = root_attr(tg)
            if base in names and attr and not attr.startswith("__"):
                if inside or base in CN:
                    writers[attr].add((m, fn.name))
multi = sum(1 for w in writers.values() if len(w) > 1)

# import graph incl. function-scope imports
G = defaultdict(set)
for m, t in trees.items():
    for n in ast.walk(t):
        if isinstance(n, ast.ImportFrom) and n.level == 1:
            if n.module:
                G[m].add(n.module.split(".")[0])
            else:
                G[m] |= {a.name for a in n.names}
idx, low, st, on, comp_n, c = {}, {}, [], set(), [0], [0]
sys.setrecursionlimit(10000)
def sc(v):
    idx[v] = low[v] = c[0]; c[0] += 1; st.append(v); on.add(v)
    for w in G[v]:
        if w not in trees: continue
        if w not in idx: sc(w); low[v] = min(low[v], low[w])
        elif w in on: low[v] = min(low[v], idx[w])
    if low[v] == idx[v]:
        comp = []
        while True:
            w = st.pop(); on.discard(w); comp.append(w)
            if w == v: break
        if len(comp) > 1: comp_n[0] += len(comp)
for v in trees:
    if v not in idx: sc(v)

# formatting-blind, module-blind duplication
W = int(__import__("os").environ.get("DUP_W", "2"))
win = defaultdict(set)


def _norm(s):
    """ast.dump with string literals blanked: a log message is not a difference in logic."""
    s = ast.parse(ast.unparse(s)).body[0]
    for n in ast.walk(s):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            n.value = "S"
    return ast.dump(s)
def blocks(node):
    for f in ("body", "orelse", "finalbody"):
        b = getattr(node, f, None)
        if isinstance(b, list) and b and isinstance(b[0], ast.stmt):
            yield b
    for h in getattr(node, "handlers", []) or []:
        yield h.body
for m, fn in funcs:
    for node in ast.walk(fn):
        if node is not fn and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            continue
        for b in blocks(node):
            b = [s for s in b if not is_doc(s)]
            for i in range(len(b) - W + 1):
                w = b[i:i + W]
                if any(isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) for s in w): continue
                if sum(1 for s in w for _ in ast.walk(s)) < int(__import__("os").environ.get("DUP_NODES", "30")): continue
                key = hashlib.sha1("".join(_norm(s) for s in w).encode()).hexdigest()
                win[key].add((m, fn.name, fn.lineno))
pairs = set()
for owners in win.values():
    o = sorted(owners)
    for i in range(len(o)):
        for j in range(i + 1, len(o)):
            pairs.add((o[i], o[j]))
p10 = 0; lmax = 0
for m, fn in funcs:
    k = len([a for a in fn.args.posonlyargs + fn.args.args + fn.args.kwonlyargs if a.arg not in ("self", "cls")])
    p10 += k > 10
    lmax = max(lmax, stmts(fn))
print(json.dumps({"private_reach": reach, "coord_footprint": foot, "coord_writers_multi": multi,
                  "import_cycle_modules": comp_n[0], "dup_pairs": len(pairs), "params_over_10": p10,
                  "logical_max_fn": lmax}))
