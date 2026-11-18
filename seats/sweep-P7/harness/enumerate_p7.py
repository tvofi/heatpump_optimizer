"""Class P7 seam enumerator, round 11 (D14 method step 3).

Generalises D2-s3-07's seam_rule (`def month_hours|monthrange` in ledger.py) to
the whole package: a span of true time derived from a CALENDAR count at a fixed
day length, which is wrong by an hour on a DST transition day/month.

Families (AST scan of custom_components/heatpump_optimizer/*.py):
  CAL      a call to calendar.monthrange / monthrange (days in a calendar month)
  DAYLEN   a product or quotient of a non-constant operand with a fixed day
           length: 24, 24.0, 1440, 86400, 96, HOURS_PER_DAY, QUARTERS_PER_DAY,
           or a constant sub-product equal to one of those (24 * 60, 24 * 3600)

Run:   python3 enumerate_p7.py [--root DIR] [--fixture clean|perturbed]
Prints one `SEAM <family> <file>:<line> <symbol> | <source>` line per seam, then
`RESULT seams=N CAL=a DAYLEN=b`.
--fixture clean      scans a synthetic module that uses true elapsed time only (null control)
--fixture perturbed  the same module plus one line `h = 24.0 * days`         (perturbation)
"""
import argparse, ast, os, sys, tempfile

DAY = {24, 1440, 86400, 96}
DAY_NAMES = {"HOURS_PER_DAY", "QUARTERS_PER_DAY", "MINUTES_PER_DAY", "SECONDS_PER_DAY"}

CLEAN = '''from datetime import datetime, timezone
def span_hours(a, b):
    return (b.astimezone(timezone.utc) - a.astimezone(timezone.utc)).total_seconds() / 3600.0
'''
PERTURB_LINE = "def month(days):\n    h = 24.0 * days\n    return h\n"


def const_val(n):
    if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool):
        return n.value
    if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mult):
        a, b = const_val(n.left), const_val(n.right)
        if a is not None and b is not None:
            return a * b
    return None


def is_day(n):
    v = const_val(n)
    if v is not None:
        return v in DAY
    return isinstance(n, ast.Name) and n.id in DAY_NAMES or (
        isinstance(n, ast.Attribute) and n.attr in DAY_NAMES)


def scan(path, rel):
    src = open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    lines = src.splitlines()
    out = []
    stack = []

    class V(ast.NodeVisitor):
        def _scope(self, node):
            stack.append(node.name)
            self.generic_visit(node)
            stack.pop()
        visit_FunctionDef = visit_AsyncFunctionDef = visit_ClassDef = _scope

        def visit_Call(self, node):
            f = node.func
            name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
            if name == "monthrange":
                out.append(("CAL", node.lineno))
            self.generic_visit(node)

        def visit_BinOp(self, node):
            if isinstance(node.op, (ast.Mult, ast.Div, ast.FloorDiv, ast.Mod)):
                l, r = node.left, node.right
                lc, rc = const_val(l) is not None, const_val(r) is not None
                if not (lc and rc):
                    if (is_day(r) and not lc) or (isinstance(node.op, ast.Mult) and is_day(l) and not rc):
                        out.append(("DAYLEN", node.lineno))
                        return  # one seam per outermost expression
            self.generic_visit(node)

    V().visit(tree)
    # symbol per line: innermost def containing it
    res = []
    defs = []
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defs.append((n.lineno, n.end_lineno, n.name, n))
    for fam, ln in out:
        cands = [d for d in defs if d[0] <= ln <= d[1]]
        cands.sort(key=lambda d: d[0])
        sym = ".".join(d[2] for d in cands) or "<module>"
        res.append((fam, rel, ln, sym, lines[ln - 1].strip()))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="custom_components/heatpump_optimizer")
    ap.add_argument("--fixture", choices=["clean", "perturbed"])
    a = ap.parse_args()
    root = a.root
    if a.fixture:
        root = tempfile.mkdtemp()
        with open(os.path.join(root, "fixture.py"), "w") as fh:
            fh.write(CLEAN + ("\n" + PERTURB_LINE if a.fixture == "perturbed" else ""))
    seen = set()
    seams = []
    for dp, _, fs in sorted(os.walk(root)):
        for f in sorted(fs):
            if f.endswith(".py"):
                p = os.path.join(dp, f)
                for s in scan(p, os.path.relpath(p, os.path.dirname(root.rstrip("/"))) if not a.fixture else f):
                    if (s[1], s[2]) not in seen:
                        seen.add((s[1], s[2]))
                        seams.append(s)
    for fam, rel, ln, sym, code in seams:
        print(f"SEAM {fam} {rel}:{ln} {sym} | {code}")
    c = {k: sum(1 for s in seams if s[0] == k) for k in ("CAL", "DAYLEN")}
    print(f"RESULT seams={len(seams)} CAL={c['CAL']} DAYLEN={c['DAYLEN']}")


if __name__ == "__main__":
    main()
