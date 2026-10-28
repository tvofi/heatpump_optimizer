import json,subprocess as s
f="dev/programme/rosters/wave-r10-groups.json"
G=["R10-PREPR-CAP","R10-FLOW-MAIN-GATE","R10-FLY-OPENPR-ATOMIC","R10-TRAIN-OVERLAP-GRADE","R10-ORCH-REVIEW-PACKET","R10-FLOW-BOARD","R10-FLOW-ROSTER-FREEZE","R10-ORCH-ROSTER-SCHEMA","R10-ORCH-BEATD","R10-TRIAGE-S6"]
revs=s.check_output(["git","rev-list","--reverse","--first-parent","eab04d0eb..69b1ac245"]).decode().split()
revs=["08c0818cd"]+revs
prev={}
for r in revs:
    d={x["group"]:x for x in json.loads(s.check_output(["git","show",r+":"+f]))["groups"]}
    subj=s.check_output(["git","log","-1","--format=%h %s",r]).decode().strip()
    for k in G:
        st=((d.get(k) or {}).get("resume") or {}).get("stage"); n=len((d.get(k) or {}).get("carry") or [])
        if prev.get(k)!=(st,n): print(subj[:70],"|",k,st,"carries",n)
        prev[k]=(st,n)
