"""B3c (BAD): the pass-through chain taken as far as it goes on the five
worst-CC functions (optimize, identify, _update_current_state,
get_current_action, simulate_trajectory_batch): repeatedly tail-split the
fragment with the highest CC at its middle legal top-level cut, until no
fragment over CC 15 has a legal cut left. Each fragment takes every live local
as a parameter and tail-calls the next. Nothing is named, nothing is
encapsulated; only the metric's unit of account changes.
"""
import ast, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import COORD, COORD_CLASS, PKG, read, write, find_method, tail_cut_ok, tail_extract, seam_set

def cc(fn):
    c = 1
    for n in ast.walk(fn):
        if isinstance(n, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.IfExp, ast.ExceptHandler, ast.Assert)): c += 1
        elif isinstance(n, ast.BoolOp): c += len(n.values) - 1
        elif isinstance(n, ast.comprehension): c += 1 + len(n.ifs)
        elif isinstance(n, ast.match_case): c += 1
    return c

TARGETS = [(f"{PKG}/optimizer.py", "HeatPumpOptimizer", "optimize"),
           (f"{PKG}/sysid.py", "SystemIdentification", "identify"),
           (COORD, COORD_CLASS, "_update_current_state"),
           (f"{PKG}/optimizer.py", "HeatPumpOptimizer", "get_current_action"),
           (f"{PKG}/thermal_model.py", "ThermalModel", "simulate_trajectory_batch")]
made = []
for rel, cls, root in TARGETS:
    s = read(rel)
    frags = [root]
    n = 0
    while True:
        cands = []
        for name in frags:
            fn = find_method(s, cls, name)
            if cc(fn) <= 15:
                continue
            # a cut must leave decision points on BOTH sides, or it makes no progress
            def dp(stmts):
                return cc(ast.Module(body=stmts, type_ignores=[])) - 1
            legal = [k for k in range(1, len(fn.body))
                     if dp(fn.body[:k]) > 0 and dp(fn.body[k:]) > 0 and tail_cut_ok(fn, k)[0]]
            if legal:
                cands.append((cc(fn), name, legal[len(legal) // 2]))
        if not cands or n >= 40:
            break
        _, name, k = max(cands)
        n += 1
        new = f"_{root.lstrip('_')}_frag{n}"
        s, _ = tail_extract(s, cls, name, k, new)
        frags.append(new)
        if rel == COORD:
            seam_set(new, "core")
    write(rel, s)
    made.append((root, n))
print(made)
