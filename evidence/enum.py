import json,subprocess,collections
R="5e7f73ad5e6f3fc0bc16ca904dcf95748ea0a82c"
raw=subprocess.run(["git","-C","/home/user/heatpump_optimizer","ls-tree","-r","--name-only",R],capture_output=True,text=True).stdout.split()
rp=[p for p in raw if p.endswith("wave-r10-groups.json")][0]
ro=json.loads(subprocess.run(["git","-C","/home/user/heatpump_optimizer","show",f"{R}:{rp}"],capture_output=True,text=True).stdout)
gs=ro["groups"] if isinstance(ro,dict) else ro
B=json.load(open("ev/plan-wtbase.json"))["groups"];H=json.load(open("ev/plan-wt.json"))["groups"]
B=[dict(v,group=k) for k,v in B.items()];H=[dict(v,group=k) for k,v in H.items()]
bl={g["group"]:g["lane"] for g in B};hl={g["group"]:g["lane"] for g in H}
rg={g["group"]:g for g in gs}
print("roster",len(gs),"base",len(bl),"head",len(hl))
print("base",collections.Counter(bl.values()));print("head",collections.Counter(hl.values()))
def done(n): 
    return next((x.get("done") for x in H if x["group"]==n),None)
moved={n:(bl[n],hl[n]) for n in hl if bl.get(n)!=hl[n]}
print("moved",len(moved),collections.Counter(moved.values()))
print("moved not from Core model:",[n for n,(a,b) in moved.items() if a!="Core model"])
INST=("tools/","tests/",".github/",".claude/","dev/","docs/")
ROOT={"CLAUDE.md","AGENTS.md","README.md","RELEASE_NOTES.md"}
def own(g): return list(g.get("files") or [])+list(g.get("hot_files") or [])
def np_(f): return f.startswith(INST) or f in ROOT
wrong=[]
print("--moved groups with any custom_components/ or bare file:")
for n in moved:
    fs=own(rg[n]); 
    bad=[f for f in fs if not np_(f)]
    if bad: print(" ",n,bad,rg[n].get("kind"),rg[n].get("class"))
print("--Core model at head")
nofile=0;rows=[]
for n,l in hl.items():
    if l!="Core model":continue
    g=rg[n];fs=own(g)
    allnp= bool(fs) and all(np_(f) for f in fs)
    cc=any(f.startswith("custom_components/") for f in fs)
    rows.append((n,len(fs),cc,allnp,g.get("kind"),g.get("class"),done(n)))
    if allnp: print("  WRONG all-instrument still core:",n)
print("core at head",len(rows),"with custom_components",sum(r[2] for r in rows))
for r in rows:
    if not r[2]: print("  core without custom_components:",r)
print("--counts of moved open:",sum(1 for n in moved if not done(n)))
json.dump({"moved":moved},open("ev/moved.json","w"),indent=0)
