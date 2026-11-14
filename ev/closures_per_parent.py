# reviewer-built: compare tools/ci/selftest_closures.json at head against each parent and main
import json, subprocess, sys
def load(r): return json.loads(subprocess.run(["git","show",f"{r}:tools/ci/selftest_closures.json"],capture_output=True,text=True,check=True).stdout)
H=sys.argv[1]; h=load(H)["steps"]
for p in sys.argv[2:]:
    t=load(p)["steps"]; lost=[]; flags=[]
    for sid,e in t.items():
        if sid not in h: lost.append((sid,"STEP")); continue
        for k,v in e.items():
            if isinstance(v,list):
                miss=sorted(set(v)-set(h[sid].get(k,[])))
                # a probe covered by a head file is not lost
                if k=="probes": miss=[x for x in miss if x not in set(h[sid].get("files",[]))]
                if miss: lost.append((sid,k,miss))
            elif isinstance(v,bool) and v and not h[sid].get(k): flags.append((sid,k))
    added=sorted(set(h)-set(t))
    print(f"vs {p[:10]}: steps base={len(t)} head={len(h)} added={added} lost-reads={len(lost)} lost-flags={flags}")
    for x in lost[:20]: print("   LOST",x)
