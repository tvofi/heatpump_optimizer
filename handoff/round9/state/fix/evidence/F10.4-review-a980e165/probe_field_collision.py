"""Reviewer's own probe: re-run tests/structure.py dead_members() with every
other class's fields (class-body annotated/plain assigns and self.<n> stores)
added as phantom same-name members, so an untyped x.<n> load is ambiguous as
it really is. Prints real members that move from measured-live to name-kept."""
import ast, copy, sys
sys.path.insert(0, "tests")
import structure as S
pkg = S.Package(S.module_trees())
dead0, kept0 = S.dead_members(pkg)
k0 = {(r, c, n) for r, c, n in kept0}; d0 = {(r, c, n) for r, c, n, _ in dead0}
real = set()
for (mod, cname), cls in pkg.classes.items():
    fns = {it.name for it in cls.body if isinstance(it, (ast.FunctionDef, ast.AsyncFunctionDef))}
    real |= {(pkg.mods[mod][0], cname, f) for f in fns}
    fields = set()
    for it in cls.body:
        if isinstance(it, ast.AnnAssign) and isinstance(it.target, ast.Name): fields.add(it.target.id)
        if isinstance(it, ast.Assign): fields |= {t.id for t in it.targets if isinstance(t, ast.Name)}
    for n in ast.walk(cls):
        if isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Store) and isinstance(n.value, ast.Name) and n.value.id == "self":
            fields.add(n.attr)
    for f in sorted(fields - fns):
        stub = ast.parse(f"def {f}(self): pass").body[0]
        stub.lineno = 0
        cls.body.append(stub)   # phantom: data attribute of this class
dead1, kept1 = S.dead_members(pkg)
k1 = {(r, c, n) for r, c, n in kept1}; d1 = {(r, c, n) for r, c, n, _ in dead1}
moved = sorted(k for k in (k1 | d1) & real if k not in k0 and k not in d0)
for k in moved: print("UNPRINTED", *k, "->", "dead" if k in d1 else "name-kept")
print(f"RESULT field_collision_unprinted={len(moved)} count")
print(f"RESULT name_kept_reported={len(k0)} count")
