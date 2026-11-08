import ast, re, subprocess, sys, json
src = open("tests/features.py").read()
lines = src.splitlines(keepends=True)
tree = ast.parse(src)
start = next(i for i,l in enumerate(lines) if 'R.section("R10-HOTFIX-COP-UNMEASURED' in l) + 1
stmts = [n for n in tree.body if n.lineno < start]
def defines(n, name):
    if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)): return n.name==name
    if isinstance(n,(ast.Import,ast.ImportFrom)): return any((a.asname or a.name.split('.')[0])==name for a in n.names)
    if isinstance(n,(ast.Assign,ast.AnnAssign,ast.AugAssign)):
        tg = n.targets if isinstance(n,ast.Assign) else [n.target]
        return any(isinstance(x,ast.Name) and x.id==name for t in tg for x in ([t] if isinstance(t,ast.Name) else (t.elts if isinstance(t,(ast.Tuple,ast.List)) else [])))
    return False
chosen=[]
for _ in range(80):
    pre = []
    for n in sorted(chosen, key=lambda n:n.lineno):
        pre += ["--prelude", "".join(lines[n.lineno-1:n.end_lineno])]
    p = subprocess.run([sys.executable,"tools/audit/seat/features_block.py",*pre,'R.section("R10-HOTFIX-COP-UNMEASURED','R.section("early cut-off'],capture_output=True,text=True)
    m = re.search(r"NameError: name '(\w+)' is not defined", p.stderr)
    if not m:
        print(p.stdout[-600:], p.stderr[-1500:], "rc", p.returncode); break
    name = m.group(1)
    cand = [n for n in stmts if defines(n,name)]
    if not cand: print("no def for", name); break
    chosen.append(cand[-1]); print("add", name, cand[-1].lineno, file=sys.stderr)
json.dump(["".join(lines[n.lineno-1:n.end_lineno]) for n in sorted(chosen,key=lambda n:n.lineno)], open(sys.argv[1],"w"))
