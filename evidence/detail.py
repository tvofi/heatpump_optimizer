import json,subprocess as s
f="dev/programme/rosters/wave-r10-groups.json"
g=lambda r:{x["group"]:x for x in json.loads(s.check_output(["git","show",r+":"+f]))["groups"]}
a,b=g("origin/main"),g("HEAD")
for k in b:
    A=a.get(k,{}); B=b[k]
    if A==B: continue
    print("=====",k)
    if A.get("resume")!=B.get("resume"): print(" resume main:",json.dumps(A.get("resume"))); print(" resume head:",json.dumps(B.get("resume")))
    ca=A.get("carry") or []; cb=B.get("carry") or []
    for c in cb:
        if c not in ca: print(" +carry:",json.dumps(c)[:900])
    for c in ca:
        if c not in cb: print(" -carry:",json.dumps(c)[:400])
    if k not in a: print(" NEW:",json.dumps({x:B[x] for x in B if x not in("carry",)})[:1500])
    if A.get("fixes")!=B.get("fixes"): print(" fixes",A.get("fixes"),"->",B.get("fixes"))
