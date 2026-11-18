"""Class P1 sweep (round 10, D14 steps 3-4): time-keyed feed rows whose
timestamp is missing or unparseable.

Seam = a function in custom_components/heatpump_optimizer that reads a
timestamp key (starts_at/startsAt/start/datetime/time/t/end...) off a row dict.
Flags per seam (AST, no import):
  ADMIT      the timestamp read has a literal "" / None fallback that is stored
             into an output row (row kept with no usable stamp)
  POSITIONAL the function holds a branch that, when no row parsed, places the
             raw rows by list position (iterates/indexes the source list in the
             else/`if not` arm after a timestamp parse).
Command: python3 dev/audit/rounds/round10/D14/sweep-P1/p1_ts_seams.py [--null] [--perturb]
  --null    scans a clean fixture (drop-on-unparseable, no fallback): RESULT seams_flagged=0
  --perturb the same fixture with one line re-introduced (`or ""` admit):     seams_flagged=1
"""
import ast, sys, pathlib

TS_KEYS = {"starts_at", "startsAt", "start", "datetime", "time", "t", "timestamp",
           "end", "ends_at", "start_time", "end_time"}
PKG = pathlib.Path("custom_components/heatpump_optimizer")

CLEAN = '''
def parse(rows):
    out = []
    for r in rows:
        s = r.get("startsAt")
        if not s:
            continue
        out.append({"starts_at": s, "total": r.get("total")})
    return out
'''
PERTURBED = CLEAN.replace('s = r.get("startsAt")', 's = r.get("startsAt") or ""')

def ts_get(node):
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == "get" and node.args
            and isinstance(node.args[0], ast.Constant) and node.args[0].value in TS_KEYS)

def admits(fn):
    for n in ast.walk(fn):
        if isinstance(n, ast.BoolOp) and isinstance(n.op, ast.Or) and any(ts_get(v) for v in n.values):
            last = n.values[-1]
            if isinstance(last, ast.Constant) and last.value in ("", None):
                return True
    return False

def positional(fn):
    for n in ast.walk(fn):
        if isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant) and n.slice.value == 0:
            v = ast.unparse(n.value)
            if v.endswith("_prices") or v.endswith("forecast"):
                return True
    # an else / `if not entries` arm that walks the raw source rows by position
    for n in ast.walk(fn):
        if isinstance(n, ast.If):
            arms = n.orelse if n.orelse else []
            test = ast.unparse(n.test)
            body = n.body if test.startswith("not ") else arms
            for b in body:
                t = ast.unparse(b)
                if ("for " in t and ("range(4)" in t or "* 4" in t)) or "[0]" in t and ("forecast" in t or "_prices" in t):
                    return True
    return False

def scan(sources):
    seams = []
    for name, text in sources:
        tree = ast.parse(text)
        for fn in ast.walk(tree):
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if any(ts_get(n) for n in ast.walk(fn)):
                    # innermost only: skip if a nested def holds all reads
                    seams.append((name, fn.name, admits(fn), positional(fn)))
    # dedupe nested
    return sorted(set(seams))

if "--null" in sys.argv or "--perturb" in sys.argv:
    srcs = [("fixture.py", PERTURBED if "--perturb" in sys.argv else CLEAN)]
else:
    srcs = [(str(p), p.read_text()) for p in sorted(PKG.rglob("*.py"))]
seams = scan(srcs)
flagged = 0
for f, sym, a, p in seams:
    tag = ("ADMIT " if a else "") + ("POSITIONAL" if p else "")
    flagged += bool(a or p)
    print(f"SEAM {f}::{sym} {tag or '-'}")
print(f"RESULT seams_total={len(seams)} count")
print(f"RESULT seams_flagged={flagged} count")
