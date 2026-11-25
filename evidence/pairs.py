import json, subprocess, sys
def load(rev):
    return json.loads(subprocess.check_output(["git","show",f"{rev}:tests/closures.json"]))["closures"]
def pairs(c):
    prod={f for fs in c.values() for f in fs if f.startswith("custom_components/heatpump_optimizer/")}
    n=sorted(c); out={}
    for i in range(len(n)):
        for j in range(i+1,len(n)):
            a=set(c[n[i]])&prod; b=set(c[n[j]])&prod
            if a and b: out[(n[i],n[j])]=len(a&b)/len(a|b)
    return out, len(n), prod
for rev in sys.argv[1:]:
    p,n,prod=pairs(load(rev)); print(rev, "scripts",n,"prod",len(prod),"comparable",len(p),">=0.80",sum(v>=0.80 for v in p.values()))
pb,_,_=pairs(load(sys.argv[1])); ph,_,_=pairs(load(sys.argv[2]))
for k in sorted(set(pb)|set(ph)):
    b=pb.get(k); h=ph.get(k)
    if (b is not None and b>=0.8)!=(h is not None and h>=0.8): print("moved", k, b, h)
