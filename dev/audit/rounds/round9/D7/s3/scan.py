import ast, sys, pathlib, collections, json
PKG = pathlib.Path("custom_components/heatpump_optimizer")
files = sorted(PKG.glob("*.py"))
src = {f.name[:-3]: f.read_text() for f in files}
trees = {m: ast.parse(s) for m, s in src.items()}
# hastub base names (overrides)
stub_names = set()
for p in pathlib.Path("tests/hastub").rglob("*.py"):
    for n in ast.walk(ast.parse(p.read_text())):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)): stub_names.add(n.name)
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name): stub_names.add(t.id)
        if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name): stub_names.add(n.target.id)
defs = []  # (module, qual, kind, lineno, node)
for m, t in trees.items():
    for n in t.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)): defs.append((m, n.name, "func", n.lineno))
        elif isinstance(n, ast.ClassDef):
            defs.append((m, n.name, "class", n.lineno))
            for b in n.body:
                if isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    defs.append((m, n.name + "." + b.name, "method", b.lineno))
        elif isinstance(n, ast.Assign):
            for tg in n.targets:
                if isinstance(tg, ast.Name): defs.append((m, tg.id, "const", n.lineno))
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
            defs.append((m, n.target.id, "const", n.lineno))
def refs(tree):
    c = collections.Counter()
    for n in ast.walk(tree):
        if isinstance(n, ast.Name): c[n.id] += 1
        elif isinstance(n, ast.Attribute): c[n.attr] += 1
        elif isinstance(n, ast.Constant) and isinstance(n.value, str): 
            for w in n.value.replace(".", " ").split(): c["str:" + w] += 1
    return c
prod = collections.Counter(); per_mod = {}
for m, t in trees.items():
    r = refs(t); per_mod[m] = r; prod.update(r)
test = collections.Counter()
for p in list(pathlib.Path("tests").glob("*.py")):
    try: test.update(refs(ast.parse(p.read_text())))
    except Exception: pass
out = []
for m, q, k, ln in defs:
    name = q.split(".")[-1]
    if name.startswith("__") and name.endswith("__"): continue
    if k == "method" and (name in stub_names or name.startswith("async_step_")): continue
    n = prod[name] + prod["str:" + name]
    if n == 0:
        out.append((m, q, k, ln, test[name] + test["str:" + name]))
for o in out: print("\t".join(map(str, o)))
print("TOTAL", len(out), file=sys.stderr)
