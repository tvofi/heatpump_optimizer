"""D5-s2 supplementary scan (D5.M4): qualified references in production
Python comments and docstrings -- ``module.name`` where module is a package
module, and ``Class.member`` where Class is a package class -- that do not
resolve to a definition in that module/class (AST).
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D5/s2/scan_qualified_refs.py
Expected: 19 printed rows, all false positives (entity ids such as
``sensor.hp_t4``, ``services.yaml``, ``datetime.weekday``); 0 real misses.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, box B2. Pure AST count, no timing.
"""
import io,tokenize,pathlib,ast,re,collections
root=pathlib.Path("custom_components/heatpump_optimizer")
mods={p.stem:p for p in root.glob("*.py")}
defs=collections.defaultdict(set)   # module -> top names ; class -> members
classes=collections.defaultdict(set)
for m,p in mods.items():
    t=ast.parse(p.read_text())
    for n in ast.walk(t):
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)): defs[m].add(n.name)
        if isinstance(n,ast.Assign):
            for tg in n.targets:
                for x in ast.walk(tg):
                    if isinstance(x,ast.Name): defs[m].add(x.id)
        if isinstance(n,ast.AnnAssign) and isinstance(n.target,ast.Name): defs[m].add(n.target.id)
        if isinstance(n,(ast.Import,ast.ImportFrom)):
            for a in n.names: defs[m].add(a.asname or a.name.split('.')[0])
        if isinstance(n,ast.ClassDef):
            for b in ast.walk(n):
                if isinstance(b,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)): classes[n.name].add(b.name)
                if isinstance(b,ast.AnnAssign) and isinstance(b.target,ast.Name): classes[n.name].add(b.target.id)
                if isinstance(b,ast.Assign):
                    for tg in b.targets:
                        for x in ast.walk(tg):
                            if isinstance(x,ast.Name): classes[n.name].add(x.id)
                            if isinstance(x,ast.Attribute): classes[n.name].add(x.attr)
                if isinstance(b,ast.Attribute) and isinstance(b.ctx,ast.Store): classes[n.name].add(b.attr)
def texts(p):
    src=p.read_text()
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type==tokenize.COMMENT: yield tok.start[0],tok.string
    for n in ast.walk(ast.parse(src)):
        if isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str):
            yield n.lineno, n.value.value
r=re.compile(r"\b([A-Za-z_]\w*)(?:\.py)?[.:]([A-Za-z_]\w*)\b")
bad=[]
for p in sorted(root.glob("*.py")):
    for ln,t in texts(p):
        for m in r.finditer(t):
            a,b=m.group(1),m.group(2)
            if a in mods and a!='const' or a=='const':
                if a in mods:
                    if b in ('py',) : continue
                    if b not in defs[a] and b not in classes: bad.append((p.name,ln,f"{a}.{b}","mod"))
            elif a in classes and a not in mods:
                if b not in classes[a] and not b.startswith('__'): bad.append((p.name,ln,f"{a}.{b}","cls"))
for x in bad: print(*x)
print(f"RESULT qualified_ref_rows={len(bad)} rows")
