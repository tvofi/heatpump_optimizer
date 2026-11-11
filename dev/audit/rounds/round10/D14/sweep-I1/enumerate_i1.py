"""Class I1 sweep (D14 method 3): enumerate every defensive-guard seam of the
class -- a guard conjunct that protects a read or an emission and whose
falsifying branch the gate may never exercise.

Families (from the round-10 findings' seam_rules, generalised to the AST):
  LEN   an `and`/conditional whose operand is `<idx> < len(<seq>)` (D3-s1-02)
  DROP  `if <name>:` whose body logs a 'Quarantined' / malformed WARNING (D3-s2-01)
  KEEP  `if <x> and not self._<attr>:` whose body assigns a fallback to
        self._<attr> (keep-prior-else-fabricate; D3-s1-01)
Command:
  python dev/audit/rounds/round10/D14/sweep-I1/enumerate_i1.py [ROOT]
    ROOT defaults to custom_components/heatpump_optimizer
  --fixture : run the null control (clean synthetic module -> 0 seams) and the
              perturbation (that module plus ONE re-introduced guard line -> 1)
Output: one 'SEAM <family> <file>:<line> <symbol>' per seam, then
'RESULT seams=N LEN=a DROP=b KEEP=c' (count, exact). Static, no timing.
"""
import ast, os, sys, tempfile


def _is_len_cmp(n):
    return (isinstance(n, ast.Compare) and len(n.ops) == 1
            and isinstance(n.ops[0], ast.Lt) and isinstance(n.comparators[0], ast.Call)
            and getattr(n.comparators[0].func, "id", None) == "len")


def _logs_quarantine(body):
    for st in body:
        for n in ast.walk(st):
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and (
                    "Quarantined" in n.value or "malformed" in n.value.lower()):
                return True
    return False


def scan_source(src, rel):
    tree = ast.parse(src)
    out = []
    stack = []

    def sym():
        return ".".join(stack) or "<module>"

    class V(ast.NodeVisitor):
        def _scope(self, node):
            stack.append(node.name)
            self.generic_visit(node)
            stack.pop()
        visit_FunctionDef = visit_AsyncFunctionDef = visit_ClassDef = _scope

        def visit_BoolOp(self, node):
            if isinstance(node.op, ast.And) and any(_is_len_cmp(v) for v in node.values):
                out.append(("LEN", rel, node.lineno, sym()))
            self.generic_visit(node)

        def visit_If(self, node):
            t = node.test
            if isinstance(t, ast.Name) and _logs_quarantine(node.body):
                out.append(("DROP", rel, node.lineno, sym()))
            if (isinstance(t, ast.BoolOp) and isinstance(t.op, ast.And) and len(t.values) == 2
                    and isinstance(t.values[1], ast.UnaryOp) and isinstance(t.values[1].op, ast.Not)
                    and isinstance(t.values[1].operand, ast.Attribute)
                    and getattr(t.values[1].operand.value, "id", None) == "self"):
                attr = t.values[1].operand.attr
                if any(isinstance(n, ast.Assign) and any(
                        isinstance(tg, ast.Attribute) and tg.attr == attr for tg in n.targets)
                        for st in node.body for n in ast.walk(st)):
                    out.append(("KEEP", rel, node.lineno, sym()))
            self.generic_visit(node)

    V().visit(tree)
    return out


def scan(root):
    seams = []
    for dp, _, fs in os.walk(root):
        for f in sorted(fs):
            if f.endswith(".py"):
                p = os.path.join(dp, f)
                seams += scan_source(open(p).read(), p)
    return sorted(seams, key=lambda s: (s[1], s[2]))


def report(seams):
    for fam, f, l, s in seams:
        print(f"SEAM {fam} {f}:{l} {s}")
    c = {k: sum(1 for x in seams if x[0] == k) for k in ("LEN", "DROP", "KEEP")}
    print(f"RESULT seams={len(seams)} LEN={c['LEN']} DROP={c['DROP']} KEEP={c['KEEP']}")


CLEAN = '''
def f(xs, i, log):
    if xs:
        return xs[i]
    if i < 3:
        log.warning("ok")
    return None
'''
REINTRO = "    y = xs and i < len(xs)\n"

if __name__ == "__main__":
    if "--fixture" in sys.argv:
        d = tempfile.mkdtemp()
        p = os.path.join(d, "clean.py")
        open(p, "w").write(CLEAN)
        print("NULL:"); report(scan(d))
        open(p, "w").write(CLEAN.replace("    if xs:\n", REINTRO + "    if xs:\n", 1))
        print("PERTURBED (one line):"); report(scan(d))
    else:
        args = [a for a in sys.argv[1:] if not a.startswith("--")]
        report(scan(args[0] if args else "custom_components/heatpump_optimizer"))
