import json,subprocess,sys
g=lambda r: json.loads(subprocess.check_output(["git","show",f"{r}:tests/closures.json"]))["closures"]
H,M,B=(g(x) for x in sys.argv[1:4])
bad=0
for s in sorted(set(H)|set(M)|set(B)):
    u=set(M.get(s,[]))|set(B.get(s,[])); h=set(H.get(s,[]))
    if u!=h: bad+=1; print("DIFF",s,"extra",sorted(h-u)[:5],"missing",sorted(u-h)[:5])
print("scripts",len(H),"non-union",bad)
c=H; prod={f for fs in c.values() for f in fs if f.startswith("custom_components/heatpump_optimizer/")}
a=set(c["tests/config_flow_steps.py"])&prod; b=set(c["tests/wood_advisor.py"])&prod
print("cfs/wood jaccard",len(a&b),len(a|b),round(len(a&b)/len(a|b),4), "cfs-only",sorted(a-b))
