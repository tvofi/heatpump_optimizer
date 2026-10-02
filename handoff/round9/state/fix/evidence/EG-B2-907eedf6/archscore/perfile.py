import sys, json
sys.path.insert(0,"a3/metrics"); sys.path.insert(0,"b"); sys.path.insert(0,"redteam/counters")
import ast, private_reach as PR, counters as CN, _common as C
S=sys.argv[1]
def run(root, v2):
    if v2:
        ts = CN.trees(__import__("pathlib").Path(root))
        cls = next(n for n in ts["coordinator"].body if isinstance(n, ast.ClassDef) and n.name == C.COORD_CLASS)
        pt=set()
        for f in cls.body:
            if isinstance(f, ast.FunctionDef) and C.is_property(f):
                body=[s for s in f.body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
                if len(body)==1 and isinstance(body[0],ast.Return) and isinstance(body[0].value,ast.Attribute) and isinstance(body[0].value.value,ast.Name) and body[0].value.value.id=="self" and body[0].value.attr.startswith("_"): pt.add(f.name)
        o=PR._private; PR._private=lambda n:o(n) or n in pt
    r=PR.measure(__import__("pathlib").Path(root))
    return r["value"], r["details"]["per_file_weighted"]
out={}
for v2 in (0,1):
  for n,p in (("base",S+"/base"),("head",S+"/wt")):
    out[f"{n}_v{2 if v2 else 1}"]=run(p,v2)
    if v2: PR._private=PR._private if False else PR._private
import importlib; 
json.dump(out,open(sys.argv[2],"w"),indent=1)
