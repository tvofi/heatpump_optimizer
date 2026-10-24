"""D14 class-sweep P4 enumerator: every seam where an iterative optimizer's
stop tolerance or seed set decides the returned plan, across the package.

Seam kinds (AST, every *.py under custom_components/heatpump_optimizer):
  STOP  a call to a scipy.optimize entry (minimize/linprog/least_squares/
        curve_fit/nnls/minimize_scalar) or to the package wrapper
        _scoped_minimize, keyed with its literal ftol/tol option ('-' if none);
  SEED  a list assignment/append/concat to a name `starts` (or a candidates
        rewrite inside a move_starts callback) in a function that calls
        _multi_start_minimize -- the seed set the multi-start brackets with.
Seam key: '<kind> <file>:<enclosing function> line <n> [ftol=..]'.

Run:  python3 dev/audit/rounds/round10/D14/sweep-P4/p4_seams.py [--null] [--perturb]
--null:    run on an in-memory clean fixture (closed-form code, no optimizer):
           expected 0 seams.
--perturb: re-introduce one line (`minimize(f, x0, options={"ftol": 1e-6})`
           appended to a copy of optimizer.py): STOP count must rise by 1.
Positive control (always run): asserts the seam list contains each R10
finding's site -- D0-s1-01 (SEED in _multi_start_minimize's space-only
caller) and D0-s2-01 (STOP ftol=1e-6 in _multi_start_minimize and
_lbfgsb_restart).  Static, contention-immune; tolerance 0.
"""
import ast, sys
from pathlib import Path

ROOT = Path.cwd()
PKG = ROOT / "custom_components" / "heatpump_optimizer"
OPT = {"minimize", "linprog", "least_squares", "curve_fit", "nnls",
       "minimize_scalar", "_scoped_minimize"}


def _name(n):
    if isinstance(n, ast.Name):
        return n.id
    if isinstance(n, ast.Attribute):
        return n.attr
    return None


def _ftol(call):
    for kw in call.keywords:
        if kw.arg in ("tol", "ftol"):
            return ast.unparse(kw.value)
        if kw.arg == "options" and isinstance(kw.value, ast.Dict):
            for k, v in zip(kw.value.keys, kw.value.values):
                if isinstance(k, ast.Constant) and k.value in ("ftol", "tol", "gtol"):
                    return ast.unparse(v)
    return "-"


def seams(fname, src):
    tree = ast.parse(src)
    out = []

    def visit(node, func, calls_ms):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                ms = any(isinstance(c, ast.Call) and _name(c.func) == "_multi_start_minimize"
                         for c in ast.walk(ch))
                inner = f"{func}.{ch.name}" if func else ch.name
                visit(ch, inner, ms or (calls_ms and ch.name == "move_starts"))
                continue
            if isinstance(ch, ast.Call) and _name(ch.func) in OPT:
                out.append(f"STOP {fname}:{func} line {ch.lineno} {_name(ch.func)} ftol={_ftol(ch)}")
            if calls_ms:
                tgt = None
                if isinstance(ch, ast.Assign):
                    tgt = [_name(t) for t in ch.targets]
                elif isinstance(ch, ast.AugAssign):
                    tgt = [_name(ch.target)]
                elif isinstance(ch, ast.Call) and _name(ch.func) == "append":
                    tgt = [_name(ch.func.value)]
                if tgt and "starts" in tgt:
                    out.append(f"SEED {fname}:{func} line {ch.lineno}")
            visit(ch, func, calls_ms)

    visit(tree, "", False)
    return out


def package(extra=None):
    res = []
    for f in sorted(PKG.glob("*.py")):
        src = f.read_text()
        if extra and f.name == "optimizer.py":
            src += extra
        res += seams(f.name, src)
    return res


CLEAN = '''
import numpy as np
def plan(prices, p_max):
    order = np.argsort(prices)
    out = np.zeros_like(prices)
    out[order[:4]] = p_max
    return out
'''

if __name__ == "__main__":
    if "--null" in sys.argv:
        s = seams("clean_fixture.py", CLEAN)
        print("\n".join(s)); print(f"RESULT null_seams={len(s)}")
        sys.exit(0 if not s else 1)
    base = package()
    for s in base:
        print(s)
    stop = [s for s in base if s.startswith("STOP")]
    seed = [s for s in base if s.startswith("SEED")]
    print(f"RESULT seams={len(base)} stop={len(stop)} seed={len(seed)}")
    pos = {
        "D0-s2-01 main": any("_multi_start_minimize line" in s and "ftol=1e-06" in s for s in stop),
        "D0-s2-01 restart": any("_lbfgsb_restart" in s and "ftol=1e-06" in s for s in stop),
        "D0-s1-01 seeds": len({s.split(" line")[0] for s in seed}) >= 2,
    }
    print(f"RESULT positive_control={pos}")
    if "--perturb" in sys.argv:
        p = package("\ndef _reintro(f, x0):\n    return minimize(f, x0, options={\"ftol\": 1e-6})\n")
        ps = [s for s in p if s.startswith("STOP")]
        print(f"RESULT perturbed_stop={len(ps)} (base {len(stop)}, delta {len(ps)-len(stop)})")
    sys.exit(0 if all(pos.values()) else 1)
