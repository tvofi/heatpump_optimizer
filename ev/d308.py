import json,sys
cl=json.loads(open(sys.argv[1]).read())["closures"]; txt=" ".join(open(sys.argv[2]).read().split())
P="custom_components/heatpump_optimizer/"
prod={f for fs in cl.values() for f in fs if f.startswith(P)}
n=sorted(cl);pairs=0;comp=0
for i in range(len(n)):
  for j in range(i+1,len(n)):
    a=set(cl[n[i]])&prod;b=set(cl[n[j]])&prod
    if a and b:
      comp+=1
      if len(a&b)/len(a|b)>=0.80: pairs+=1
tot=len(cl)*(len(cl)-1)//2
empty=sorted(s for s,fs in cl.items() if not set(fs)&prod)
m=[s for s in ("D3-08","#1218","selection cost",f"all {len(prod)} files",f"{pairs} of the {tot}",f"{comp} pairs") if s not in txt]+[e for e in empty if e not in txt]
print(f"prod={len(prod)} pairs={pairs}/{tot} comparable={comp} missing={m} -> {'PASS' if not m else 'FAIL'}")
