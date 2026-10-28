import subprocess,sys,pathlib
root=pathlib.Path(sys.argv[1])
M=[("G1 judge never waits","tools/ci/gate.py","if ok or why != [deferral(waiting)] or now()","if True or ok or why != [deferral(waiting)] or now()"),
("G2 unbounded wait","tools/ci/gate.py"," or now() - t0 + POLL_S > GATE_WAIT_MAX_S:",":"),
("G3 waits on decided red","tools/ci/gate.py","if ok or why != [deferral(waiting)] or","if ok or not waiting or"),
("G4 deferral publishes PASS","tools/ci/gate.py","        return False, [deferral(waiting)]","        return True, []"),
("G5 gate busy ignores judging (waits on judging gates)","tools/ci/gate.py",'"action_required") and not judging(r))','"action_required"))'),
("P1 waits_on id order only (pre-M1)","tools/ci/prelude.py",'(run["id"] < run_id or t is None or t[0] == "code")','run["id"] < run_id'),
("P2 prelude waits until finished","tools/ci/prelude.py","                if not judging(run):","                if True:"),
("P3 prelude never waits","tools/ci/prelude.py","        if not busy:\n            return \"\"","        if True:\n            return \"\""),
("P4 prelude unbounded","tools/ci/prelude.py","        if now() - t0 + POLL_S > WAIT_MAX_S:","        if False:"),
]
def run(cmd):
    p=subprocess.run(cmd,cwd=root,capture_output=True,text=True,timeout=300)
    return p.returncode,p.stdout+p.stderr
for name,f,a,b in M:
    path=root/f; src=path.read_text(); assert src.count(a)==1,(name,src.count(a))
    path.write_text(src.replace(a,b))
    try:
        res=[]
        for t in ("gate","prelude"):
            rc,o=run(["python3","-I",f"tools/ci/{t}.py","--self-test"])
            fails=[l for l in o.splitlines() if l.startswith("FAIL") or "failed" in l]
            res.append(f"{t}: rc={rc} "+" | ".join(fails)[:900])
        try:
            rc,o=run(["python3","dev/audit/harnesses/r10_gate_defer_race.py"])
            res.append("harness: "+" ; ".join(l for l in o.splitlines() if ":" in l and "verdicts" in l or "Error" in l))
        except subprocess.TimeoutExpired: res.append("harness: TIMEOUT")
        print("==",name); print("\n".join(res))
    finally:
        path.write_text(src)
print(subprocess.run(["git","status","--short"],cwd=root,capture_output=True,text=True).stdout or "clean")
