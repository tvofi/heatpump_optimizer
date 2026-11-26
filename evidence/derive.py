import json,subprocess,sys,ast
sha=sys.argv[1]
d=json.loads(subprocess.check_output(["git","show",f"{sha}:tests/closures.json"]))["closures"]
P="custom_components/heatpump_optimizer/"
prod={f for fs in d.values() for f in fs if f.startswith(P)}
n=sorted(d); tot=len(n)*(len(n)-1)//2; hit=0; comp=0
for i in range(len(n)):
  for j in range(i+1,len(n)):
    a=set(d[n[i]])&prod; b=set(d[n[j]])&prod
    if not a or not b: continue
    comp+=1
    if len(a&b)/len(a|b)>=0.80: hit+=1
files=subprocess.check_output(["git","ls-tree","-r","--name-only",sha,P]).decode().split()
mods=[f for f in files if f.endswith(".py") and f.count("/")==2]
top=0
for f in mods:
  t=ast.parse(subprocess.check_output(["git","show",f"{sha}:{f}"]))
  if any((isinstance(s,ast.Import) and any(a.name.split('.')[0]=="homeassistant" for a in s.names)) or (isinstance(s,ast.ImportFrom) and (s.module or "").split('.')[0]=="homeassistant") for s in ast.walk(ast.Module(body=[x for x in t.body if not isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))],type_ignores=[]))): top+=1
print(f"{sha[:10]} scripts={len(n)} pairs>=0.80={hit} of {tot} comparable={comp} pkgfiles={len(files)} modules={len(mods)} ha_top_level={top} ha_free_incl_fn={len(mods)-top-1}")
