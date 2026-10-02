"""Reviewer's own scan for provably-equivalent CMP_BOUND shapes:
(1) `A if A <op> B else B` (or mirrored) -- at A == B both arms are equal;
(2) `if A <op> B: A = B` / `x = A` arms equal at equality (max/min idiom);
(3) an ordering against a fractional constant where the other side is len()/int()/sum of bools."""
import ast, sys
sys.path.insert(0, "tests")
import mutation_table as mt
ORD = (ast.Lt, ast.LtE, ast.Gt, ast.GtE)
d = ast.dump
hits = []
for p in sorted(mt.PRODUCTION.rglob("*.py")):
    src = p.read_text(); rel = str(p.relative_to(mt.ROOT))
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.IfExp) and isinstance(n.test, ast.Compare) and len(n.test.ops) == 1 \
           and isinstance(n.test.ops[0], ORD) and n.test.lineno == n.test.end_lineno:
            a, b = {d(n.test.left), d(n.test.comparators[0])}, {d(n.body), d(n.orelse)}
            if a == b:
                hits.append(f"IFEXP-MAXMIN {rel}:{n.lineno}")
        if isinstance(n, ast.If) and isinstance(n.test, ast.Compare) and len(n.test.ops) == 1 \
           and isinstance(n.test.ops[0], ORD) and not n.orelse and len(n.body) == 1 \
           and isinstance(n.body[0], ast.Assign) and n.test.lineno == n.test.end_lineno:
            t = n.body[0]
            L, R = d(n.test.left), d(n.test.comparators[0])
            if len(t.targets) == 1 and {d(t.targets[0]), d(t.value)} == {L, R} \
               or len(t.targets) == 1 and d(t.value) in (L, R) and d(t.targets[0]).replace("Store", "Load") in (L, R):
                hits.append(f"IF-ASSIGN-MAXMIN {rel}:{n.lineno}")
        if isinstance(n, ast.Compare) and n.lineno == n.end_lineno:
            for x in [n.left] + n.comparators:
                pass
            sides = [n.left] + n.comparators
            for i, op in enumerate(n.ops):
                if not isinstance(op, ORD): continue
                l, r = sides[i], sides[i+1]
                for intside, c in ((l, r), (r, l)):
                    if isinstance(c, ast.Constant) and isinstance(c.value, float) and c.value != int(c.value) \
                       and isinstance(intside, ast.Call) and isinstance(intside.func, ast.Name) \
                       and intside.func.id in ("len", "int", "round", "sum"):
                        hits.append(f"INT-VS-FRACTION {rel}:{n.lineno}")
print(f"RESULT rv_equiv candidates={len(hits)}")
for h in hits: print(" ", h)
