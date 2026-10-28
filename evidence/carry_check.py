import json,subprocess,sys
f="dev/programme/rosters/wave-r10-groups.json"
def load(ref):
    return {g["group"]:g for g in json.loads(subprocess.check_output(["git","show",ref+":"+f]))["groups"]}
head=load("HEAD"); main=load("origin/main")
def carries(g): 
    c=g.get("carries") or g.get("carry") or []
    return c
for src,dst,pid in [("R10-ORCH-REVIEW-PACKET","R10-REVIEW-CARRY","P200"),("R10-ORCH-ROSTER-SCHEMA","R10-FLOW-TOOLKIT-MODEL","P203")]:
    s=[c for c in carries(head[src]) if f"#{pid}" in json.dumps(c)]
    d=[c for c in carries(head[dst]) if f"#{pid}" in json.dumps(c)]
    print(pid,"src",src,"stage",head[src].get("resume",{}).get("stage"),"n_src",len(s),"| dst",dst,"stage",head[dst].get("resume",{}).get("stage"),"n_dst",len(d),"dst carries main->head",len(carries(main[dst])),len(carries(head[dst])))
    for x in d: print("  dst len",len(x) if isinstance(x,str) else len(json.dumps(x)))
    for x in s: print("  src len",len(x) if isinstance(x,str) else len(json.dumps(x)))
    print("  verbatim:", any(x==y for x in s for y in d))
    if d: print("  TEXT:", (d[0] if isinstance(d[0],str) else json.dumps(d[0]))[:2500])
    print("  files dst:", head[dst].get("files"))
import difflib
print("---- diffs src vs dst")
for src,dst,pid in [("R10-ORCH-REVIEW-PACKET","R10-REVIEW-CARRY","P200"),("R10-ORCH-ROSTER-SCHEMA","R10-FLOW-TOOLKIT-MODEL","P203")]:
    s=[c for c in carries(head[src]) if f"#{pid}" in json.dumps(c)][0]
    d=[c for c in carries(head[dst]) if f"#{pid}" in json.dumps(c)][0]
    sm=difflib.SequenceMatcher(None,s,d)
    for op in sm.get_opcodes():
        if op[0]!="equal": print(pid,op[0],repr(s[op[1]:op[2]]),"->",repr(d[op[3]:op[4]]))
    print(pid,"strip-marker equal:", s.rsplit("Carry:",1)[0]==d.rsplit("Carry:",1)[0])
