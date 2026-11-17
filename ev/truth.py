import json,subprocess,collections,sys
g=lambda r,f: json.loads(subprocess.check_output(["git","show",f"{r}:{f}"]))["steps"]
a=g("e352724335","tools/ci/selftest_closures.json"); b=g("142926ec66","tools/ci/selftest_closures.json")
T=set()
for s,e in b.items():
  for k in ("files","dirs","probes"):
    for p in set(e.get(k,[]))-set(a.get(s,{}).get(k,[])): T.add((s,k,p))
c=collections.Counter(k for _,k,_ in T); print(len(T),dict(c),"steps",len({s for s,_,_ in T}))
rem=set()
for s,e in a.items():
  for k in ("files","dirs","probes"):
    for p in set(e.get(k,[]))-set(b.get(s,{}).get(k,[])): rem.add((s,k,p))
print("removed",len(rem))
json.dump(sorted(T),open(sys.argv[1],"w"))
