"""D5-s2 supplementary scan (D5.M4): a comment that names a module-level
numeric constant and puts a number right after it (``NAME (100 L)``,
``NAME = 0.5``) -- compared with the constant's literal value.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D5/s2/scan_const_numbers.py
Expected: RESULT const_adjacent_checked=2, const_adjacent_mismatch=0.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, box B2. Pure AST count, no timing.
"""
import io,tokenize,pathlib,ast,re,sys
sys.path.insert(0,'tests/hastub'); sys.path.insert(0,'.')
import importlib
CHECKED=[]; BAD=[]
root=pathlib.Path("custom_components/heatpump_optimizer")
# gather all module-level numeric constants across package
vals={}
for p in sorted(root.glob("*.py")):
    for n in ast.parse(p.read_text()).body:
        tgt=None
        if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name): tgt=n.targets[0].id
        if isinstance(n,ast.AnnAssign) and isinstance(n.target,ast.Name): tgt=n.target.id
        if tgt and n.value is not None:
            try: v=ast.literal_eval(n.value)
            except Exception: continue
            if isinstance(v,(int,float)) and not isinstance(v,bool): vals.setdefault(tgt,[]).append((p.name,v))
def texts(p):
    src=p.read_text()
    lines=src.splitlines()
    # merge contiguous comment lines
    buf=[];start=None;prev=-9
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type==tokenize.COMMENT:
            if tok.start[0]==prev+1: buf.append(tok.string.lstrip('#:'))
            else:
                if buf: yield start," ".join(buf)
                buf=[tok.string.lstrip('#:')]; start=tok.start[0]
            prev=tok.start[0]
    if buf: yield start," ".join(buf)
    for n in ast.walk(ast.parse(src)):
        if isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str):
            yield n.lineno, n.value.value
r=re.compile(r"`{0,2}([A-Z][A-Z0-9_]{3,})`{0,2}\s*(?:\(|=|,|is|of|at)?\s*~?(-?\d+(?:\.\d+)?)")
for p in sorted(root.glob("*.py")):
    for ln,t in texts(p):
        t=re.sub(r"\s+"," ",t)
        for m in r.finditer(t):
            name,num=m.group(1),m.group(2)
            if name not in vals: continue
            vs={v for _,v in vals[name]}
            CHECKED.append(name)
            if any(abs(float(num)-v)<1e-9 for v in vs):
                print("OK",p.name,ln,name,num); continue
            BAD.append(name)
            print(f"{p.name}:{ln} {name} cited {num} actual {vs} :: ...{t[max(0,m.start()-60):m.end()+60]}")
print(f"RESULT const_adjacent_checked={len(CHECKED)} rows")
print(f"RESULT const_adjacent_mismatch={len(BAD)} rows")
