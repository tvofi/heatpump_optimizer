import json,subprocess,re
F="dev/programme/rosters/wave-r10-groups.json"
def load(ref): return {g["group"]:g for g in json.loads(subprocess.check_output(["git","show",f"{ref}:{F}"]))["groups"]}
d=json.load(open("/root/ev/roster_diff.json")); tgt={k:b for k,a,b,r in d["moves"] if b in("done","absorbed")}
revs=subprocess.check_output(["git","rev-list","--reverse","--first-parent","c3a279e32..174417fa3","--",F]).decode().split()
prev=load("c3a279e32"); origin={}
for r in revs:
    cur=load(r)
    for k in tgt:
        if k in cur and (prev.get(k,{}).get("resume") or {}).get("stage")!=(cur[k].get("resume") or {}).get("stage"): origin[k]=r
    prev=cur
head=load("174417fa3"); live={k for k,g in head.items() if (g.get("resume") or {}).get("stage") not in ("done","absorbed","refused","refuted","deferred")}
for k,b in sorted(tgt.items()):
    r=origin.get(k); body=subprocess.check_output(["git","log","-1","--format=%s%n%b",r]).decode() if r else ""
    lines=[l for l in body.splitlines() if k in l][:2]
    moved=sorted(set(re.findall(r"\[moved: (R10-[A-Z0-9-]+)\]"," ".join(head[k].get("carry") or []))))
    prs=re.findall(r"#(\d{3,5})"," ".join(lines))
    print(f"{b:8} {k:32} {r[:9] if r else '-':9} subj={body.splitlines()[0][:50] if body else ''!r} prs={prs} moved_to={moved} moved_live={[m for m in moved if m in live]} ncarry={len(head[k].get('carry') or [])} | {' / '.join(l.strip()[:140] for l in lines)}")
