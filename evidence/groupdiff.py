import json,subprocess as s,sys
f="dev/programme/rosters/wave-r10-groups.json"
g=lambda r:{x["group"]:x for x in json.loads(s.check_output(["git","show",r+":"+f]))["groups"]}
a,b=g("origin/main"),g("HEAD")
print(len(a),len(b))
for k in b:
    if k not in a: print("ADDED",k,json.dumps(b[k],indent=1)); continue
    if a[k]!=b[k]:
        keys=[x for x in set(a[k])|set(b[k]) if a[k].get(x)!=b[k].get(x)]
        print("CHANGED",k,"stage",a[k].get("stage"),"->",b[k].get("stage"),"fields",keys)
