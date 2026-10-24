import json,re,os,sys
sys.path.insert(0,os.path.dirname(__file__))
from dec import D,I,N,O
C=os.path.dirname(__file__); R="/Users/timmalmstrom/hpo-orch/r10s6"
items=json.load(open(C+"/items.json"))
CAR=R+"/routing-carries-1"
def clean(t):
    t=re.sub(r"\s*Carry:.*$","",t).strip()
    return t.lstrip("- ").strip()
# carries to append to existing live groups: dest -> list of (ids, file)
MERGE={"1f866f06":"3b97e1aa","e6bf0f70":"9728f4d0","98904e32":"6fb50ac5"}
NOOP_HELD={"d17bc0c8","325975e1","1e40d527","771d38c3","84be4901","85501172","d4f06227"}
NEWG={"R10-ADVISOR-RESIDUE","R10-RESTORE-RACE-PROBE","R10-BRIEFS-FOLD-D0"}
app={}; newcarry={}
for iid,(v,dest,ev) in D.items():
    if v!=N or iid in NOOP_HELD: continue
    key=MERGE.get(iid,iid)
    rows=items[iid]; r=rows[0]
    old=",".join(sorted({b.split(':')[0] for x in rows for b in x["bad"]})) or "no destination (unrouted)"
    why=(f"its destination {old} is done and did not implement it" if r['bad'] else "it carried no Carry: marker and is not implemented")
    txt=f"From #{r['pr']} ({r['where']}, item {iid}), routed by routing audit 1 (2026-10-24): {why} ({ev}). {clean(r['text'])}"
    if dest in NEWG: newcarry.setdefault(dest,[]).append(txt); continue
    app.setdefault((dest,key),[]).append(txt)
ops=[]
for (dest,key),txts in sorted(app.items()):
    f=f"{CAR}/{dest}--{key}.txt"; open(f,"w").write("\n".join(txts)+"\n")
    ops.append(f"python3 tools/audit/seat/roster_edit.py append-carry {dest} @{f}")
json.dump(newcarry,open(C+"/newcarry.json","w"),indent=1)
open(C+"/carry_ops.txt","w").write("\n".join(ops)+"\n")
# decisions rows
rows=[]
for iid,lst in items.items():
    for r in lst:
        v,dest,ev=D[iid]
        kind="BAD-DEST "+",".join(sorted({b.split(':')[0] for b in r['bad']})) if r['status']=="bad" else "UNROUTED"
        rows.append((int(r['pr']),r['where'],iid,kind,v,dest,ev))
rows.sort(key=lambda x:(-x[0],x[1],x[2]))
json.dump(rows,open(C+"/rows.json","w"))
from collections import Counter
print(Counter((x[3].split()[0],x[4]) for x in rows)); print(len(rows), len(ops)); print(Counter(x[5] for x in rows if x[4]==N))
