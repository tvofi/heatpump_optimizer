# V2: count in-place attribute/subscript/mutating-call writes on objects reached via self.<hub>
# (directly or via a local alias bound from self.<hub> in the same function), per package.
import ast,sys,pathlib
HUBS=set(sys.argv[2].split(','))
root=pathlib.Path(sys.argv[1])/'custom_components/heatpump_optimizer'
MUT={'append','clear','extend','update','pop','insert','remove','add'}
tot=0;sites=[]
def base(n):
    while isinstance(n,(ast.Attribute,ast.Subscript)):
        if isinstance(n,ast.Attribute) and n.attr in HUBS: return n.attr
        n=n.value
    return n.id if isinstance(n,ast.Name) else None
for p in sorted(root.rglob('*.py')):
    t=ast.parse(p.read_text())
    for f in ast.walk(t):
        if not isinstance(f,(ast.FunctionDef,ast.AsyncFunctionDef)): continue
        alias={}
        for n in ast.walk(f):
            if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name):
                b=base(n.value) if isinstance(n.value,ast.Attribute) else None
                if b in HUBS and isinstance(n.value,ast.Attribute) and n.value.attr in HUBS: alias[n.targets[0].id]=b
        def hub(tgt):
            if not isinstance(tgt,(ast.Attribute,ast.Subscript)): return None
            if isinstance(tgt,ast.Attribute) and isinstance(tgt.value,ast.Name) and tgt.value.id=='self': return None
            b=base(tgt); return b if b in HUBS else alias.get(b)
        for n in ast.walk(f):
            tg=[]
            if isinstance(n,ast.Assign): tg=n.targets
            elif isinstance(n,(ast.AugAssign,ast.AnnAssign)): tg=[n.target]
            elif isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in MUT: tg=[n.func.value] if hub(n.func.value) or (isinstance(n.func.value,ast.Attribute) and base(n.func.value) in HUBS) else []
            for x in tg:
                h=hub(x) or (base(x) if base(x) in HUBS else None)
                if h: tot+=1; sites.append(f"{p.name}:{n.lineno}:{f.name}:{h}")
print("TOTAL",tot)
for s in sites: print(s)
