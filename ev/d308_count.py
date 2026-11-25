import json,sys,subprocess
def count(rev):
    c=json.loads(subprocess.check_output(["git","show",f"{rev}:tests/closures.json"]))["closures"]
    prod={f for fs in c.values() for f in fs if f.startswith("custom_components/heatpump_optimizer/")}
    n=sorted(c);pairs=[];cfs=[]
    for i in range(len(n)):
        for j in range(i+1,len(n)):
            a=set(c[n[i]])&prod;b=set(c[n[j]])&prod
            if a and b:
                jac=len(a&b)/len(a|b)
                if jac>=0.8: pairs.append((n[i],n[j]))
                if "config_flow_steps" in n[i]+n[j] and 0.78<jac<0.82: cfs.append((round(jac,3),n[i],n[j]))
    print(rev,"prod",len(prod),"pairs",len(pairs),"of",len(n)*(len(n)-1)//2, "cfs_near", cfs)
for r in sys.argv[1:]: count(r)
