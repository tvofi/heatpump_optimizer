d=$1; cd $d || exit 9
python3 - <<'PY' > tests/_blk.py
import ast,re
src=open("tests/features.py").read(); L=src.split("\n")
s=next(i for i,l in enumerate(L) if l.startswith('R.section("R10-GENERIC-HEAT-CURVE —'))
e=next(i for i,l in enumerate(L) if l.startswith('R.section("R5-D12-01'))
pro=next(i for i,l in enumerate(L) if l.startswith('R.section('))
imps=[]; defs={}
for n in ast.parse(src).body:
    if not (pro<=n.lineno-1<s): continue
    if isinstance(n,(ast.Import,ast.ImportFrom)): imps+=L[n.lineno-1:n.end_lineno]
    elif isinstance(n,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)):
        st=(n.decorator_list[0].lineno if n.decorator_list else n.lineno)-1
        defs[n.name]=(st,"\n".join(L[st:n.end_lineno]))
body="\n".join(L[s:e]); need=set(); text=body
while True:
    new={k for k in defs if k not in need and re.search(r"\b%s\b"%re.escape(k),text)}
    if not new: break
    need|=new; text="\n".join(defs[k][1] for k in need)
out=[defs[k][1] for k in sorted(need,key=lambda k:defs[k][0])]
print("\n".join(L[:pro]+imps+out+[body,'sys.exit(R.close("FEATURES BLOCK"))']))
PY
PYTHONPATH=tests/hastub:tests timeout 600 python3 tests/_blk.py; rc=$?; rm -f tests/_blk.py; exit $rc
