# Reviewer's own mutation driver (round-4 re-review of #2558). Anchors B-E are the
# round-1 reviewer's (probe/rev-2558-e98d4b97); B2/C2/D2/D3 are added by this seat.
import subprocess,pathlib
PP="tools/audit/seat/plan_page.py"; RP="tools/plan/replan.py"
M=[("A-blobless-accepted",RP,"    if not want:\n        return (\"plan.json pins no roster blob","    if False:\n        return (\"plan.json pins no roster blob"),
("B-model-record-refusal",PP,'if "model" not in plan["generated"]:','if False:'),
("C-check_plan-dropped",PP,"bad = replan.check_plan(plan)","bad = []"),
("D-caption-drawn-count",PP,"f\"start, ETA and wave. {drawn} of","f\"start, ETA and wave. {max(0, len(chain) - 1) - drawn} of"),
("E-ref-override-ignored",RP,"    ref = ref or gen.get(\"roster_ref\") or \"\"","    ref = gen.get(\"roster_ref\") or ref or \"\""),
("D2-caption-constant-0",PP,"f\"start, ETA and wave. {drawn} of","f\"start, ETA and wave. {0} of"),
("D3-caption-constant-1",PP,"f\"start, ETA and wave. {drawn} of","f\"start, ETA and wave. {1} of"),
("C2-check_plan-truncated",PP,"bad = replan.check_plan(plan)","bad = replan.check_plan(plan)[:0]"),
]
def run():
    out=[]
    for c in (["python3","-I",PP,"--self-test"],["python3",RP,"--self-test"]):
        r=subprocess.run(c,capture_output=True,text=True)
        lines=(r.stdout+r.stderr).splitlines()
        fails=[l for l in lines if l.lstrip().startswith(("FAIL","not ok"))]
        tail=[l for l in lines if " failed" in l][-1:]
        out.append((c[-2].split("/")[-1],r.returncode,fails,tail))
    return out
def show(name,res,verdict):
    print("RESULT mutant=%s verdict=%s rc=%s"%(name,verdict,"/".join(str(r[1]) for r in res)))
    for f,rc,fails,tail in res:
        print("  %s rc=%d %s"%(f,rc,tail))
        for l in fails: print("    "+l)
r0=run(); show("M0",r0,"null" if all(r[1]==0 for r in r0) else "BASELINE-RED")
for n,f,old,new in M:
    p=pathlib.Path(f); s=p.read_text()
    if s.count(old)!=1: print("RESULT mutant=%s anchor-count=%d"%(n,s.count(old))); continue
    p.write_text(s.replace(old,new))
    try:
        res=run(); show(n,res,"killed" if any(r[1]!=0 for r in res) else "SURVIVED")
    finally: p.write_text(s)
