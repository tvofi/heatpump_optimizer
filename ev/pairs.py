import json, subprocess, sys
def load(rev):
    return json.loads(subprocess.check_output(["git","show",f"{rev}:tests/closures.json"]))["closures"]
def pairs(c):
    prod={f for fs in c.values() for f in fs if f.startswith("custom_components/heatpump_optimizer/")}
    n=sorted(c); out=set()
    for i in range(len(n)):
        for j in range(i+1,len(n)):
            a=set(c[n[i]])&prod; b=set(c[n[j]])&prod
            if a and b and len(a&b)/len(a|b)>=0.80: out.add((n[i],n[j]))
    comp=sum(1 for i in range(len(n)) for j in range(i+1,len(n)) if set(c[n[i]])&prod and set(c[n[j]])&prod)
    return out,len(n)*(len(n)-1)//2,comp,len(prod)
res={}
for rev in sys.argv[1:]:
    p,t,comp,np_=pairs(load(rev)); res[rev]=p
    print(f"{rev}: {len(p)} of the {t}; comparable {comp}; prod files {np_}")
r=sys.argv[1:]
if len(r)>=2:
    print("added vs first:",sorted(res[r[-1]]-res[r[0]])); print("removed:",sorted(res[r[0]]-res[r[-1]]))
