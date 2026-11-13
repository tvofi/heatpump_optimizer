import json, subprocess, ast, io, tokenize, re, sys
MB='154dbb4c61652135381ce66646d23f7109d1c142'
d=json.load(open(sys.argv[1]))
cache={}
def src(p):
    if p not in cache:
        try: cache[p]=subprocess.run(['git','show',f'{MB}:{p}'],capture_output=True,text=True,check=True).stdout
        except Exception: cache[p]=None
    return cache[p]
codecache={}
def codelines(p):
    if p in codecache: return codecache[p]
    s=src(p); doc=set(); code=set()
    t=ast.parse(s)
    for n in ast.walk(t):
        if isinstance(n,(ast.Module,ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) and n.body and isinstance(n.body[0],ast.Expr) and isinstance(getattr(n.body[0],'value',None),ast.Constant) and isinstance(n.body[0].value.value,str):
            e=n.body[0]; doc.update(range(e.lineno,e.end_lineno+1))
    for tok in tokenize.generate_tokens(io.StringIO(s).readline):
        if tok.type in (tokenize.COMMENT,tokenize.NL,tokenize.NEWLINE,tokenize.INDENT,tokenize.DEDENT,tokenize.ENDMARKER): continue
        for l in range(tok.start[0],tok.end[0]+1):
            if l not in doc: code.add(l)
    codecache[p]=code; return code
out=[]
for r in d['rows']:
    kinds=[]
    for ev in r.get('evidence',[]):
        m=re.match(r'([^:\s]+):(\d+)(?:-(\d+))?',ev)
        if not m: kinds.append(('noref',ev)); continue
        p,a,b=m.group(1),int(m.group(2)),int(m.group(3) or m.group(2))
        if src(p) is None: kinds.append(('missing',ev)); continue
        if p.endswith('.py'):
            k='code' if any(l in codelines(p) for l in range(a,b+1)) else 'COMMENT'
        else: k='nonpy:'+p.rsplit('.',1)[-1]
        kinds.append((k,ev))
    hascode=any(k=='code' for k,_ in kinds)
    out.append((r['verdict'],hascode,r['key'],kinds))
from collections import Counter
print(Counter((v,h) for v,h,_,_ in out))
for v,h,k,kinds in out:
    if not h and v in ('true','false','stale','unverifiable'):
        print(v,k,kinds)
