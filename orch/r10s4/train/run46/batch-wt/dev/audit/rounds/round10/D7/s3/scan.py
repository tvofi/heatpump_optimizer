import ast, sys, re
from pathlib import Path
from collections import Counter
PKG=Path("custom_components/heatpump_optimizer")
def idents(paths):
    c=Counter()
    for p in paths:
        try: t=ast.parse(p.read_text())
        except Exception: continue
        for n in ast.walk(t):
            if isinstance(n,ast.Name): c[n.id]+=1
            elif isinstance(n,ast.Attribute): c[n.attr]+=1
            elif isinstance(n,ast.alias): c[(n.asname or n.name).split('.')[-1]]+=1; c[n.name.split('.')[-1]]+=1
            elif isinstance(n,ast.Constant) and isinstance(n.value,str):
                for w in re.findall(r"[A-Za-z_]\w*",n.value): c[w]+=1
    return c
prod=sorted(PKG.glob("*.py")); tests=sorted(Path("tests").rglob("*.py"))
P=idents(prod); T=idents(tests)
for p in prod:
    t=ast.parse(p.read_text())
    for n in ast.walk(t):
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
            nm=n.name
            if nm.startswith("__") or nm.startswith("async_") or nm.startswith("_async_") : continue
            if P[nm]==0: print(f"{'TESTONLY' if T[nm] else 'DEAD'} {p.name}:{n.lineno} {nm}")
