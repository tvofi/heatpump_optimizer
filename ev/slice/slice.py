"""Slice runner for tests/entities.py. usage: slice.py [entities_file]  (run from repo root,
PYTHONPATH=tests/hastub). Blocks located by source anchors, not line numbers."""
import ast, sys, os
src_path = sys.argv[1] if len(sys.argv) > 1 else "tests/entities.py"
src = open(src_path).read()
tree = ast.parse(src)
body = tree.body
L = src.split('\n')
def seg(n): return L[n.lineno-1]
def idx(pred, start=0):
    for i in range(start, len(body)):
        if pred(body[i]): return i
    raise SystemExit("anchor not found")
def starts(s): return lambda n: seg(n).startswith(s)
def label(n):
    if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) and seg(n).startswith("R.check(") and n.value.args \
       and isinstance(n.value.args[0], ast.Constant):
        return n.value.args[0].value
def lab(s): return lambda n: (label(n) or "").startswith(s)
sel = []
i_R = idx(starts('R = Results('))
sel += list(range(0, i_R + 1))
ROOT_I = idx(starts('ROOT = Path('), i_R); sel.append(ROOT_I)
for a in ("import subprocess as _subprocess", "import yaml as _yaml", "import closure as _closure", "import importlib.util as _cig_util"):
    sel.append(idx(starts(a)))
sel.append(idx(starts('_CIG_PATH')))
sel.append(idx(lambda n: seg(n)=='try:' and n.lineno>21096, idx(starts('import importlib.util as _cig_util'))))
# A: _ghx .. umbrella check (only umbrella label of R.checks)
a0 = idx(starts("def _ghx(")); a1 = idx(lab("the CI umbrella: DESIGN-P2's triggers"), a0)
A = list(range(a0, a1 + 1))
# B: _RC_DOCS .. "and the cancelling block" null control
b0 = idx(starts("_RC_DOCS = {")); b1 = idx(lab("and the cancelling block, a serialised one"), b0)
B = [b0, idx(starts('def _if_under('), b0)] + list(range(idx(starts('def _cc_value('), b0), b1 + 1))
# helper stmts needed from before B? (_RC_CONTEXTS precedes _RC_DOCS)
rc = idx(starts("_RC_CONTEXTS = ")); B = [rc] + B
print(f"# slice: preamble stmts 0..{i_R} + ROOT + 3 imports; A = stmts {a0}..{a1} (lines {body[a0].lineno}-{body[a1].end_lineno}, R.checks other than umbrella skipped); "
      f"B = _RC_CONTEXTS + _RC_DOCS + def _if_under + stmts from def _cc_value ..{b1} (lines {body[b0].lineno}-{body[b1].end_lineno}, all R.checks run)")
order = sorted(set(sel)) + A + B
g = {"__name__": "__main__", "__file__": os.path.abspath(src_path)}
sys.path.insert(0, os.path.join(os.getcwd(), "tests"))
skip_lab = lambda n, rng: rng is A and label(n) is not None and not label(n).startswith("the CI umbrella: DESIGN-P2's triggers")
import builtins
for i in order:
    n = body[i]
    if i in A and label(n) is not None and not label(n).startswith("the CI umbrella: DESIGN-P2's triggers"):
        continue
    code = compile(ast.Module([n], []), src_path, "exec")
    exec(code, g)
print("_CI_PLANT_MISSED =", g.get("_CI_PLANT_MISSED"))
print("_CI_DEFECTS =", g.get("_CI_DEFECTS"))
print("_CC_FOUND =", g.get("_CC_FOUND"))
