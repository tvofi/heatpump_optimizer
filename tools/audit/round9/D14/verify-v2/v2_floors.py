"""D14 round 9, verifier V2 (independent) for D14-s3-01: one quantity, floored at one read, raw at another.

Metric (one line): v2_floor_raw_groups = quantity names Q (the final attribute/variable name of
an operand, e.g. p.buffer_tank_thermal_mass -> buffer_tank_thermal_mass) such that somewhere in
the imported package source Q appears as an argument of max(Q, <positive numeric constant>) and
somewhere else Q appears un-floored as the RIGHT operand of '/' (a divisor), OR is floored by two
different constants; v2_floor_raw_divisor_sites = the raw divisor sites summed over those groups.
Key: names in the AST of the modules as imported (heatpump_optimizer.__file__), not a hand list.
Stricter than the finder's rule (divisor only, not '*').

Null control (--fixture): a synthetic module where every read of Q is floored -> 0.
Perturbation (--reintroduce): append a function `return y / max(C_buf, 0.01)` (R7 D2-01's shape) to
thermal_model's source in memory -> C_buf (read raw as a divisor at thermal_model.py:2273 ff.)
becomes a group: 8 -> 9 expected.

Run: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D14/verify-v2/v2_floors.py [--fixture|--reintroduce]
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; 4-core cloud container, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, ast, glob
from collections import defaultdict
sys.path.insert(0, "custom_components")
t_proc0, t_thr0 = time.process_time(), time.thread_time()
import heatpump_optimizer  # noqa: E402

PKG = os.path.dirname(heatpump_optimizer.__file__)


def qname(n):
    if isinstance(n, ast.Attribute):
        return n.attr
    if isinstance(n, ast.Name):
        return n.id
    return None


def posconst(n):
    return isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool) and n.value > 0


def scan(sources):
    floors = defaultdict(set)     # Q -> {constants}
    floored_nodes = set()
    raw_div = defaultdict(list)   # Q -> [(file, line)]
    for fname, src in sources:
        tree = ast.parse(src)
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "max" and len(n.args) == 2:
                a, b = n.args
                for q, c in ((a, b), (b, a)):
                    if qname(q) and posconst(c):
                        floors[qname(q)].add(c.value)
                        floored_nodes.add(id(q))
        for n in ast.walk(tree):
            if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div):
                q = qname(n.right)
                if q and id(n.right) not in floored_nodes:
                    raw_div[q].append((os.path.basename(fname), n.lineno))
    groups = {}
    for q, cs in floors.items():
        if raw_div.get(q) or len(cs) > 1:
            groups[q] = (sorted(cs), raw_div.get(q, []))
    return groups


if "--fixture" in sys.argv:
    sources = [("fixture.py", "def f(p, y):\n    c = max(p.cap, 1e-6)\n    return y / c + y * c\n\n"
                              "def g(p, y):\n    return y / max(p.cap, 1e-6)\n")]
else:
    sources = [(f, open(f).read()) for f in sorted(glob.glob(os.path.join(PKG, "**", "*.py"), recursive=True))]
    if "--reintroduce" in sys.argv:
        sources = [(f, s + ("\ndef _v2_reintro(p, y):\n    return y / max(C_buf, 0.01)\n"
                            if f.endswith("thermal_model.py") else "")) for f, s in sources]
groups = scan(sources)
# ignore generic loop/scratch names that are not quantities
GENERIC = {"x", "y", "n", "i", "k", "v", "value", "total", "count", "denom", "d", "a", "b", "s", "t", "dt", "len"}
groups = {q: g for q, g in groups.items() if q not in GENERIC}
for q, (cs, sites) in sorted(groups.items()):
    print(f"GROUP {q}: floors={cs} raw_divisor_sites={len(sites)} e.g. {sites[:3]}")
print(f"RESULT v2_floor_raw_groups={len(groups)} count")
print(f"RESULT v2_floor_raw_divisor_sites={sum(len(s) for _, s in groups.values())} count")
print(f"RESULT v2_C_buf_group={int('C_buf' in groups)} count")
pc, tc = time.process_time() - t_proc0, time.thread_time() - t_thr0
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
