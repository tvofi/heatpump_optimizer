import subprocess,sys,pathlib
M=[("A-blobless-accepted","tools/plan/replan.py","    if not want:\n        return (\"plan.json pins no roster blob","    if False:\n        return (\"plan.json pins no roster blob"),
("B-model-record-refusal","tools/audit/seat/plan_page.py",'if "model" not in plan["generated"]:','if False:'),
("C-check_plan-dropped","tools/audit/seat/plan_page.py","bad = replan.check_plan(plan)","bad = []"),
("D-caption-drawn-count","tools/audit/seat/plan_page.py","f\"start, ETA and wave. {drawn} of","f\"start, ETA and wave. {max(0, len(chain) - 1) - drawn} of"),
("E-ref-override-ignored","tools/plan/replan.py","    ref = ref or gen.get(\"roster_ref\") or \"\"","    ref = gen.get(\"roster_ref\") or ref or \"\""),
]
def run():
    out=[]
    for c in (["python3","-I","tools/audit/seat/plan_page.py","--self-test"],["python3","tools/plan/replan.py","--self-test"]):
        r=subprocess.run(c,capture_output=True,text=True); out.append((r.returncode,[l for l in (r.stdout+r.stderr).splitlines() if l.startswith(("FAIL","  FAIL","not ok","FAILED"))or " failed" in l][-4:]))
    return out
print("RESULT mutant=M0", run())
for n,f,old,new in M:
    p=pathlib.Path(f); s=p.read_text()
    if s.count(old)!=1: print("RESULT mutant=%s anchor-count=%d"%(n,s.count(old))); continue
    p.write_text(s.replace(old,new))
    try:
        res=run(); k=any(rc!=0 for rc,_ in res)
        print("RESULT mutant=%s verdict=%s"%(n,"killed" if k else "SURVIVED"),res)
    finally: p.write_text(s)
