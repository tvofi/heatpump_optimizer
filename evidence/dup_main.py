import json,subprocess as s,collections
f="dev/programme/rosters/wave-r10-groups.json"
d=json.loads(s.check_output(["git","show","origin/main:"+f]))["groups"]
live=lambda x:((x.get("resume") or {}).get("stage") not in ("done","absorbed"))
m=collections.defaultdict(list)
for x in d:
    for i in (x.get("issues") or [])+(x.get("fixes") or []):
        m[i].append((x["group"],(x.get("resume") or {}).get("stage"),"fixes" if i in (x.get("fixes") or []) else "issues"))
for i in (2895,2907,2508,2733,2855,2875,2499,2429,2436,2437,2438): print(i,m.get(i))
print("--- issues on >1 live group:")
for i,v in sorted(m.items()):
    L=[g for g in v if g[1] not in ("done","absorbed")]
    if len({g[0] for g in L})>1: print(i,L)
