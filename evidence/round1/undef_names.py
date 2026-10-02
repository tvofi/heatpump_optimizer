"""Reviewer's own instrument: names loaded in a method but bound nowhere in it,
its enclosing scopes, the module, or builtins. Catches a deleted local still read."""
import ast, builtins, sys
src = open(sys.argv[1]).read(); tree = ast.parse(src)
mod_names = set(dir(builtins))
for n in tree.body:
    if isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)): mod_names.add(n.name)
    elif isinstance(n, (ast.Import, ast.ImportFrom)):
        for a in n.names: mod_names.add((a.asname or a.name).split('.')[0])
    else:
        for t in ast.walk(n):
            if isinstance(t, ast.Name) and isinstance(t.ctx, ast.Store): mod_names.add(t.id)
def bound(fn):
    b = set()
    for t in ast.walk(fn):
        if isinstance(t, ast.Name) and isinstance(t.ctx, (ast.Store, ast.Del)): b.add(t.id)
        elif isinstance(t, ast.arg): b.add(t.arg)
        elif isinstance(t, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)): b.add(t.name)
        elif isinstance(t, (ast.Import, ast.ImportFrom)):
            for a in t.names: b.add((a.asname or a.name).split('.')[0])
        elif isinstance(t, ast.ExceptHandler) and t.name: b.add(t.name)
    return b
total = 0
for cls in [n for n in tree.body if isinstance(n, ast.ClassDef)]:
    for fn in cls.body:
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)): continue
        if sys.argv[2:] and fn.name not in sys.argv[2:]: continue
        b = bound(fn)
        bad = sorted({t.id for t in ast.walk(fn) if isinstance(t, ast.Name) and isinstance(t.ctx, ast.Load) and t.id not in b and t.id not in mod_names})
        print(f"RESULT undef {cls.name}.{fn.name}: {bad}"); total += len(bad)
print(f"RESULT undef-total {total}")
