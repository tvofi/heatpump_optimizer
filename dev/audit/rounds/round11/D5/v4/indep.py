import tokenize,io,ast,re,sys
def units(path):
    src=open(path).read(); out=[]; cur=[]; last=-9
    for t in tokenize.generate_tokens(io.StringIO(src).readline):
        if t.type==tokenize.COMMENT:
            if t.start[0]==last+1 and cur: cur.append(t.string.lstrip('# ')) 
            else:
                if cur: out.append(' '.join(cur))
                cur=[t.string.lstrip('# ')]
            last=t.start[0]
    if cur: out.append(' '.join(cur))
    tree=ast.parse(src)
    for n in ast.walk(tree):
        if isinstance(n,(ast.Module,ast.FunctionDef,ast.ClassDef,ast.AsyncFunctionDef)):
            d=ast.get_docstring(n)
            if d: out.append(d)
    return out
def over(u):
    c=0
    for s in re.split(r'(?<=[.!?])\s+|\n\s*\n',u):
        if len(s.split())>40: c+=1
    return c
for f in sys.argv[1:]:
    us=units(f); print(f,len(us),'units with >40w sentence:',sum(1 for u in us if over(u)),'sentences',sum(over(u) for u in us))
