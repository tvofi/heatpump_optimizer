"""Legitimate movement of production calls across solver-touching merges (the barrier's false-fire rate).
For each first-parent merge M touching solver files: rows at M vs rows at M^1, per scenario:
same basin? calls ratio vs vouched; would calls_over (growth allowance g) fire?"""
import json, sys, os
sys.path[:0]=[]
W=os.path.dirname(os.path.abspath(__file__))
def load(rev):
    p=f"{W}/hist/{rev}.txt"
    if not os.path.exists(p): return None
    for l in open(p):
        if l.startswith("ROWS "): return json.loads(l[5:])
    return None
pairs=[l.split() for l in open(f"{W}/hist/pairs.txt") if len(l.split())==2]
G=[float(x) for x in (sys.argv[1:] or ["0.05"])]
fires={g:0 for g in G}; judged=0; merges_fired={g:set() for g in G}; worst=[]
for m,p in pairs:
    a,b=load(m),load(p)
    if not a or not b: print(m,p,"missing"); continue
    for lab in sorted(set(a)&set(b)):
        x,y=a[lab],b[lab]
        if not y["evals"] or not x["evals"]: continue
        rel=abs(x["objective"]-y["objective"])/max(abs(y["objective"]),1e-12)
        same=rel<=1e-6
        v=x["evals"]/y["evals"]
        if x["simulate"] and y["simulate"]: v=max(v,x["simulate"]/y["simulate"])
        r=x["calls"]/y["calls"]; excess=r/v
        tag="same" if same else "REPLANNED"
        print(f"{m} vs {p} {lab:18} {tag:9} calls {r:.4f}x vouched {v:.4f}x unvouched {excess:.4f}")
        if same:
            judged+=1; worst.append((excess,m,lab))
            for g in G:
                if excess>1+g: fires[g]+=1; merges_fired[g].add(m)
print("pairs",len(pairs),"judged scenario-pairs",judged)
for g in G: print(f"allowance {g}: fires {fires[g]} scenario-pairs in {len(merges_fired[g])} merges {sorted(merges_fired[g])}")
print("largest unvouched growth on unchanged plans:", sorted(worst,reverse=True)[:5])
