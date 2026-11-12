import json, shutil, subprocess, sys, copy, re
from pathlib import Path
BASE=Path(sys.argv[1]); SC="/root/wt/tools/audit/seat/scorecard.py"
def rep(S):
    out=subprocess.run(["python3","-I",SC,"report","--dir",str(S/"scorecard"),"--train-log",str(S/"train.log"),"--sweep-record",str(S/"sweep.rec")],capture_output=True,text=True).stdout
    return {l[:7].strip():l for l in out.splitlines()}
b=rep(BASE)
def plant(name,fn,expect):
    S=Path(f"/root/h/p_{name}"); shutil.rmtree(S,ignore_errors=True); shutil.copytree(BASE,S)
    fn(S); a=rep(S)
    moved=[k for k in b if b[k]!=a.get(k)]
    print(f"PLANT {name}: moved={moved}  expect={expect}  {'OK' if moved==expect else 'MISMATCH'}")
    for k in moved: print("   before:",b[k]); print("   after: ",a[k])
d=lambda S:S/"scorecard"
J=lambda p:json.load(open(p)); W=lambda p,o:json.dump(o,open(p,"w"))
def window(S):
    runs=J(d(S)/"runs.json"); ok=[r for r in sorted(runs,key=lambda r:r["t"]) if r["c"] in("success","failure")][-20:]; return runs,ok
def a_gate(S):
    runs,ok=window(S)
    for r in ok:
        p=d(S)/"jobs"/f"jobs_{r['id']}.json"
        if r["c"]=="failure" and p.exists():
            j=J(p); g=[x for x in j["jobs"] if x["name"]=="gate"][0]; g["conclusion"]="failure" if g["conclusion"]=="success" else "success"; W(p,j); return
def a_run(S):
    runs,ok=window(S); ids={r["id"] for r in ok if r["c"]=="failure"}
    tgt=sorted(ids)[0]
    for r in runs:
        if r["id"]==tgt: r["c"]="success"
    W(d(S)/"runs.json",runs)
    # keep gate the same: run success counts gate green regardless; so A_gate also legitimately moves if that run was unread/red
def lastprs(S):
    V=J(d(S)/"verdicts.json")["verdicts"]; seen=set(); by={}
    for v in V:
        k=(v["pr"],v["head"],v["kind"],v["cls"])
        if k in seen: continue
        seen.add(k); by.setdefault(v["pr"],[]).append(v)
    return V,sorted(by.values(),key=lambda vs:vs[0]["t"])[-50:]
def y_rev(S):
    V,last=lastprs(S)
    vs=next(vs for vs in last if vs[0]["kind"]=="blocked" and vs[0]["cls"] in("wrong-number","unknown"))
    f=vs[0]
    for v in V:
        if v["pr"]==f["pr"] and v["head"]==f["head"] and v["kind"]==f["kind"] and v["cls"]==f["cls"]: v["kind"]="merge"; v["cls"]=""
    W(d(S)/"verdicts.json",{"verdicts":V})
def m_first(S):
    V,last=lastprs(S)
    f=next(vs for vs in last if vs[0]["kind"]=="blocked" and vs[0]["cls"]=="wrong-number")[0]
    for v in V:
        if v["pr"]==f["pr"] and v["head"]==f["head"] and v["kind"]==f["kind"] and v["cls"]==f["cls"]: v["cls"]="carry-missing"
    W(d(S)/"verdicts.json",{"verdicts":V})
def y_train(S):
    t=(S/"train.log").read_text().splitlines()
    clean=[re.search(r"#(\d+)",l)[1] for l in t if l.startswith("MERGED")]
    sk={re.search(r"#(\d+)",l)[1] for l in t if l.startswith(("SKIP","PARK"))}
    p=[x for x in clean if x not in sk][-1]
    (S/"train.log").write_text("\n".join(t+[f"SKIP #{p} planted"])+"\n")
def h(S):
    L=(S/"scorecard"/"merges.tsv").read_text().splitlines()
    for i in range(len(L)-1,0,-1):
        c=L[i].split("\t")
        if c[2] in("production","instrument") and "hotfix" not in c[3]: c[3]="hotfix"; L[i]="\t".join(c); break
    (S/"scorecard"/"merges.tsv").write_text("\n".join(L)+"\n")
def e(S):
    R=J(d(S)/"roster.json")
    g=next(g for g in R["groups"] if g.get("source")!="outside" and not ("HOTFIX" in g["group"] or g.get("kind") in("bug","hotfix")))
    g["source"]="outside"; g["resume"]={"stage":"fix"}; W(d(S)/"roster.json",R)
def c(S):
    runs=J(d(S)/"runs.json"); s=sorted(runs,key=lambda r:r["t"])[-50:]
    for r in s[10:20]: r["c"]="cancelled"
    W(d(S)/"runs.json",runs)
def k(S):
    (S/"sweep.rec").write_text((S/"sweep.rec").read_text()+"standing-dispatch recycle planted\n")
plant("A_gate",a_gate,["A_gate"])
plant("A_run",a_run,["A_gate","A_run"])
plant("Y_rev",y_rev,["Y_rev"])
plant("M_first",m_first,["M_first"])
plant("Y_train",y_train,["Y_train"])
plant("H",h,["H"])
plant("E",e,["E"])
plant("C",c,["A_gate","A_run","C, K"])
plant("K",k,["C, K"])
