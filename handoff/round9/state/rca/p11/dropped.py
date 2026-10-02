"""Class search: parameters a hastub function accepts and never reads."""
import ast, pathlib, sys
root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "tests/hastub")
hits = []
for p in sorted(root.rglob("*.py")):
    tree = ast.parse(p.read_text())
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        a = fn.args
        params = [x.arg for x in a.posonlyargs + a.args + a.kwonlyargs]
        if a.vararg: params.append(a.vararg.arg)
        if a.kwarg: params.append(a.kwarg.arg)
        params = [x for x in params if x not in ("self", "cls")]
        body_is_stub = all(isinstance(s, (ast.Pass, ast.Expr, ast.Raise, ast.Return)) and not (isinstance(s, ast.Return) and s.value is not None and not isinstance(s.value, ast.Constant)) for s in fn.body)
        read = {n.id for s in fn.body for n in ast.walk(s) if isinstance(n, ast.Name)}
        for x in params:
            if x not in read:
                hits.append((str(p.relative_to(root)), fn.lineno, fn.name, x, body_is_stub))
for h in hits: print("DROPPED", *h)
print("dropped_params", len(hits), "in_nontrivial_bodies", sum(1 for h in hits if not h[4]))
