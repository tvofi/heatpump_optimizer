# Walk every roster-touching commit c3a279e..174417fa3 (first-parent: main's roster unchanged in range),
# attribute each carry/fix text removed per group to the commit's op; then reconcile against main->head.
import json, subprocess, collections, sys
F="dev/programme/rosters/wave-r10-groups.json"
def load(ref):
    return {g["group"]: g for g in json.loads(subprocess.check_output(["git","show",f"{ref}:{F}"]))["groups"]}
def items(g,k):
    v=g.get(k) or []
    return [json.dumps(x,sort_keys=True) if not isinstance(x,str) else x for x in v]
revs=subprocess.check_output(["git","rev-list","--reverse","--first-parent","c3a279e3252a8b57bb00b5a677318cd4fe20387f..174417fa378846e2e876156984c3f39333ebd3ba","--",F]).decode().split()
prev=load("c3a279e3252a8b57bb00b5a677318cd4fe20387f"); removals=collections.defaultdict(list)
for r in revs:
    cur=load(r); subj=subprocess.check_output(["git","log","-1","--format=%s",r]).decode().strip()
    for k,g in prev.items():
        h=cur.get(k,{})
        for fld in ("carry","carries","fixes"):
            new=set(items(h,fld))
            for t in items(g,fld):
                if t not in new: removals[(k,fld,t)].append((r[:9],subj))
    prev=cur
main=load("origin/main"); head=load("82f1d76ffef5e2fa920e50c0b004621daf5130ef")
silent=[]; byop=collections.Counter(); total=0
for k,g in main.items():
    for fld in ("carry","carries","fixes"):
        new=set(items(head.get(k,{}),fld))
        for t in items(g,fld):
            if t in new: continue
            total+=1
            ops=removals.get((k,fld,t),[])
            op=ops[-1][1].split()[1] if ops and ops[-1][1].startswith("roster_edit") else (ops[-1][1] if ops else "NONE")
            # text edited in place? (successor starting with old text, e.g. a '[moved: X]' suffix)
            succ=[n for n in new if n.startswith(t) or n.startswith(t.rstrip("."))]
            byop[(fld,op, "edited" if succ else "gone")]+=1
            if op!="drop-carry" and not succ: silent.append((k,fld,ops[-1] if ops else None,t[:200]))
print("LOST_FROM_MAIN",total); [print(" ",k,v) for k,v in sorted(byop.items())]
print("SILENT",len(silent))
for s in silent: print(" ",s)
