import json,sys,os
WT=os.path.expanduser("~/hpo-seats/r10s6/review-2889b/wt-head")
sys.path.insert(0,WT+"/tools/audit/seat"); sys.path.insert(0,WT+"/tools/audit")
import roster_sync as R
d=json.load(open("/tmp/r10roster.json"))
gs=[g for g in d["groups"] if isinstance(g,dict) and g.get("group")]
text_hits=[]; ruling_hits=[]
for g in gs:
    cs=[str(x) for x in (g.get("carry") or [])]
    for i,c in enumerate(cs):
        got=R.already_carried(cs[:i]+cs[i+1:],c)
        if got is None: continue
        (text_hits if R.finding_words(got)==R.finding_words(c) else ruling_hits).append((g["group"],c[:60],got[:60]))
print("RESULT live_text_arm_duplicate_pairs:",len(text_hits))
print("RESULT live_ruling_arm_duplicate_pairs:",len(ruling_hits))
for x in ruling_hits: print("   RULING:",x)
