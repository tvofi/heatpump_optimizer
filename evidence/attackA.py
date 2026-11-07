import sys,json,subprocess,importlib.util
S=sys.argv[1]
spec=importlib.util.spec_from_file_location("rp",S+"/wt3/tools/plan/replan.py"); rp=importlib.util.module_from_spec(spec); spec.loader.exec_module(rp)
G=rp.groups_of(json.load(open(S+"/roster.json")))
print("roster groups",len(G),"production",sum(1 for n in G if rp.roster_lane(G[n]) in rp.PRODUCTION))
repo="/home/user/heatpump_optimizer"
def commits(a,b):
    log=subprocess.run(["git","-C",repo,"log","--first-parent","--format=%H%x1f%s",f"{a}..{b}"],capture_output=True,text=True).stdout
    out=[]
    for l in log.splitlines():
        sha,_,s=l.partition("\x1f")
        d=subprocess.run(["git","-C",repo,"diff","-U0",f"{sha}^1",sha,"--","custom_components"],capture_output=True,text=True).stdout
        out.append({"subject":s,"diff":d})
    return out
by_topic={t:n for n in G for t in rp.topics_of(G[n])}
for a,b in [("v7.1.0","v7.1.1"),("v7.1.1","v7.1.2"),("v7.1.2","v7.1.3"),("v7.1.3","v7.1.4"),("v7.1.4","origin/main")]:
    cs=commits(a,b)
    code=[c for c in cs if rp.substantive(c["diff"])]
    tops=[rp.merge_topic(c["subject"]) for c in code]
    inr=[t for t in tops if t in by_topic]
    cred=rp.production_groups_since(cs,G)
    print(f"{a}..{b}: commits {len(cs)}, code-changing {len(code)}, topics parsed {sum(1 for t in tops if t)}, topic on roster {len(inr)}, credited {cred}")
    print("   code topics:",tops[:20])
print("--- perturbation: a part branch <topic>-<suffix> names its longest roster topic")
def pgs(commits):
    out={}
    for c in commits:
        t=rp.merge_topic(c["subject"]); n=None
        if t:
            cands=[k for k in by_topic if t==k or t.startswith(k+"-")]
            n=by_topic[max(cands,key=len)] if cands else None
        if n and rp.roster_lane(G[n]) in rp.PRODUCTION and rp.substantive(c.get("diff") or ""): out[n]=True
    return list(out)
for a,b in [("v7.1.0","v7.1.1"),("v7.1.1","v7.1.2"),("v7.1.2","v7.1.3"),("v7.1.3","v7.1.4"),("v7.1.4","origin/main")]:
    cs=commits(a,b); h=rp.production_groups_since(cs,G); p=pgs(cs)
    print(f"{a}..{b}: head {len(h)}, perturbed {len(p)}, added {sorted(set(p)-set(h))}, lost {sorted(set(h)-set(p))}")
