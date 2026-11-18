"""Verifier D1#2 V2 for D1-s3-07 (static half) and seam checks. Metric: handlers catching
Exception/BaseException/bare in custom_components/heatpump_optimizer whose body contains no
Raise and no Call whose dotted name contains 'log'/'LOGGER'/'warn'/'_failed'/'note' (helpers
that record). Lists the 7 named by the finding and whether each is in the set."""
import ast, pathlib, sys
root=pathlib.Path(sys.argv[1])
def dn(n):
    if isinstance(n,ast.Attribute): return dn(n.value)+"."+n.attr
    if isinstance(n,ast.Name): return n.id
    return ""
hits=[]
for p in sorted(root.glob("*.py")):
    t=ast.parse(p.read_text())
    for node in ast.walk(t):
        if isinstance(node,ast.ExceptHandler):
            ty=node.type
            names=[dn(x) for x in (ty.elts if isinstance(ty,ast.Tuple) else [ty])] if ty else ["<bare>"]
            if not any(n in ("Exception","BaseException","<bare>") for n in names): continue
            body=ast.Module(body=node.body,type_ignores=[])
            rec=any(isinstance(x,ast.Raise) for x in ast.walk(body)) or any(isinstance(x,ast.Call) and any(k in dn(x.func).lower() for k in ("log","warn","_failed","note","debug","error","exception")) for x in ast.walk(body))
            if not rec: hits.append(f"{p.name}:{node.lineno}")
print("V2 07 silent_broad_static=",len(hits))
named=["coordinator.py:10082","coordinator.py:10642","coordinator.py:10647","coordinator.py:2692","diagnostics.py:339","diagnostics.py:367","optimizer.py:1866"]
print("V2 07 named_in_set=",sum(n in hits for n in named),"/7")
print(" ".join(hits))
