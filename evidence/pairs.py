import json,sys,subprocess
def pairs(ref):
    c=json.loads(subprocess.check_output(["git","show",f"{ref}:tests/closures.json"]))["closures"]
    prod={f for fs in c.values() for f in fs if f.startswith("custom_components/heatpump_optimizer/")}
    n=sorted(c); out=set()
    for i in range(len(n)):
        for j in range(i+1,len(n)):
            a=set(c[n[i]])&prod; b=set(c[n[j]])&prod
            if a and b and len(a&b)/len(a|b)>=0.80: out.add((n[i],n[j]))
    return len(n),out
res={}
for r in sys.argv[1:]:
    k,p=pairs(r); res[r]=p; print(r,"scripts",k,"total",k*(k-1)//2,"pairs",len(p))
r=sys.argv[1:]
if len(r)>=3:
    h,m,b=(res[x] for x in r[:3])
    print("head-main",sorted(h-m)); print("main-head",sorted(m-h)); print("head-prev",sorted(h-b)); print("prev-head",sorted(b-h))
