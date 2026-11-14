import json,subprocess,sys
def load(rev,f):
    return json.loads(subprocess.check_output(["git","show",f"{rev}:custom_components/heatpump_optimizer/{f}"]))
def flat(d,p=""):
    o={}
    if isinstance(d,dict):
        for k,v in d.items(): o.update(flat(v,p+"/"+k))
    else: o[p]=d
    return o
B=sys.argv[1]; M=sys.argv[2]; BR=sys.argv[3]; H=sys.argv[4]
for f in ["strings.json","translations/en.json","translations/de.json","translations/sv.json"]:
    b,m,br,h=(flat(load(r,f)) for r in (B,M,BR,H))
    bad=0
    for k in set(b)|set(m)|set(br)|set(h):
        mc = m.get(k)!=b.get(k); brc = br.get(k)!=b.get(k)
        if mc and brc and m.get(k)!=br.get(k):
            print(f,"BOTH",k,"| head==main",h.get(k)==m.get(k),"head==br",h.get(k)==br.get(k)); 
            print("  main:",m.get(k)); print("  br:  ",br.get(k)); print("  head:",h.get(k)); bad+=1
        elif mc and h.get(k)!=m.get(k): print(f,"MAIN-LOST",k,m.get(k),"|",h.get(k)); bad+=1
        elif brc and not mc and h.get(k)!=br.get(k): print(f,"BR-LOST",k,br.get(k),"|",h.get(k)); bad+=1
    print(f,"issues",bad, "main-changed",sum(m.get(k)!=b.get(k) for k in set(b)|set(m)))
