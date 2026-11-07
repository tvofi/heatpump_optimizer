import sys,json,importlib.util
S=sys.argv[1]
spec=importlib.util.spec_from_file_location("rp",S+"/wt3/tools/plan/replan.py"); rp=importlib.util.module_from_spec(spec); spec.loader.exec_module(rp)
g={"group":"R10-COP-GATE","resume":{"stage":"in-progress","branch":"fix/r10-cop-gate"}}
for head in ["fix/r10-cop-gate","fix/r10-cop-gate-p6","fix/r10-cop-gate-vent-fix"]:
    print("topic_evidence open PR",head,"->",rp.topic_evidence(g,{"prs":[{"headRefName":head}],"refs":set()}))
G={"R10-COP-GATE":{"group":"R10-COP-GATE","lane":"Learners","kind":"defect","resume":{"stage":"done","branch":"fix/r10-cop-gate"}}}
code="+++ b/x\n+x = 1\n"
for head in ["fix/r10-cop-gate","fix/r10-cop-gate-p6"]:
    print("since-tag",head,"->",rp.production_groups_since([{"subject":f"Merge pull request #1 from tvofi/{head}","diff":code}],G))
