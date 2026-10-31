"""N-no-expiry enumerator: every "entry covering now" lookup over a timestamped series.

Seam: a call `bisect_right(<stamps>, <t>) - 1` in a function of the package.
Flag `unbounded`: the function has no comparison that bounds the found entry in
time (a Compare naming `end`, a `timedelta`, or a difference `<t> - <stamps>[i]`).
An unbounded seam treats the last entry as covering [start, inf).
Command: python3 dev/audit/rounds/round10/D14/sweep_n_no_expiry.py [root ...]
  --null      run on the clean fixture (expected: 0 unbounded)
  --perturb   run on a copy of _known_prices_for with its end check removed
              (one line; expected: unbounded 0 -> 1)
"""
import ast, pathlib, sys

PKG = pathlib.Path(__file__).resolve().parents[5] / "custom_components/heatpump_optimizer"

CLEAN = '''
from bisect import bisect_right
from datetime import timedelta
def lookup(starts, values, now):
    i = bisect_right(starts, now) - 1
    end = starts[i + 1] if i + 1 < len(starts) else starts[i] + timedelta(hours=1)
    if i < 0 or now >= end:
        return None
    return values[i]
'''


def _is_bisect_minus_one(node):
    return (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Sub)
            and isinstance(node.left, ast.Call)
            and (getattr(node.left.func, "id", None) == "bisect_right"
                 or getattr(node.left.func, "attr", None) == "bisect_right")
            and isinstance(node.right, ast.Constant) and node.right.value == 1)


def _time_bounded(fn):
    for c in ast.walk(fn):
        if not isinstance(c, ast.Compare):
            continue
        for n in ast.walk(c):
            if isinstance(n, ast.Name) and n.id == "end":
                return True
            if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "timedelta":
                return True
    return False


def scan_source(src, name):
    out = []
    tree = ast.parse(src)
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        inner = {id(n) for f in ast.walk(fn) if f is not fn and isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in ast.walk(f)}
        for n in ast.walk(fn):
            if id(n) not in inner and _is_bisect_minus_one(n):
                out.append((name, n.lineno, fn.name, not _time_bounded(fn)))
    return out


def main(argv):
    if "--null" in argv:
        seams = scan_source(CLEAN, "<clean>")
    elif "--perturb" in argv:
        src = (PKG / "coordinator.py").read_text()
        tree = ast.parse(src)
        fn = next(f for f in ast.walk(tree) if isinstance(f, ast.FunctionDef) and f.name == "_known_prices_for")
        body = ast.get_source_segment(src, fn)
        cut = body.replace("            if step_start >= end:\n                break\n", "", 1)
        assert cut != body, "perturbation anchor missing"
        import textwrap
        seams = scan_source(textwrap.dedent(cut), "coordinator.py:_known_prices_for(perturbed)")
    else:
        seams = []
        for p in sorted(PKG.rglob("*.py")):
            seams += scan_source(p.read_text(), str(p.relative_to(PKG.parents[1])))
    for f, ln, sym, unb in seams:
        print(f"SEAM {f}:{ln} {sym} {'UNBOUNDED' if unb else 'bounded'}")
    print(f"RESULT seams={len(seams)} count")
    print(f"RESULT unbounded={sum(s[3] for s in seams)} count")


main(sys.argv[1:])
