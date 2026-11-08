import subprocess,sys,pathlib
wt=pathlib.Path(sys.argv[1])
M=[
("G1 fresh: me-lag guard removed","tools/ci/gate.py",'        if r is me and any((r["jobs"].get(f"{unit} / {n}") or ("",))[0] != "completed" for n in names):\n            return "~", r["id"]\n',''),
("G2 fresh: min instead of max start","tools/ci/gate.py",'return max(((r.get("starts")','return min(((r.get("starts")'),
("G3 fresh: id before start","tools/ci/gate.py",'for n in names), default=""), r["id"]','for n in names), default="") and r["id"]'),
("G4 sort ascending","tools/ci/gate.py",'key=lambda r: fresh(r, names), reverse=True','key=lambda r: fresh(r, names), reverse=False'),
("G5 me starts dropped","tools/ci/gate.py",'"jobs": api["jobs"], "starts": api.get("starts") or {}}','"jobs": api["jobs"]}'),
("G6 read_api: own starts not passed","tools/ci/gate.py",'jobs = run_jobs(get, repo, ctx["run_id"], starts)','jobs = run_jobs(get, repo, ctx["run_id"])'),
("G7 read_api: others starts not passed","tools/ci/gate.py",'else run_jobs(get, repo, r["id"], st)})','else run_jobs(get, repo, r["id"])})'),
("G8 fresh: me-lag guard any->all","tools/ci/gate.py",'if r is me and any((r["jobs"]','if r is me and all((r["jobs"]'),
("P1 run_jobs: starts not filled","tools/ci/prelude.py",'        starts.update((j["name"], j.get("started_at")) for j in rows)\n','        pass\n'),
("S1 judge: stale branch removed","tools/ci/sweep.py",'        if pin:\n            self.fresh(run, gate, runs, pin)\n            return\n','        pass\n'),
("S2 stale_pin: events check removed","tools/ci/sweep.py",'        if run.get("event") not in PINNED_EVENTS:\n            return None\n','        pass\n'),
("S3 stale_pin: py filter dropped","tools/ci/sweep.py",' and f["filename"].endswith(".py")',''),
("S4 stale_pin: prefix dropped","tools/ci/sweep.py",'f["filename"].startswith(PINNED_PROGRAMS) and ',''),
("S5 stale_pin: cap 300->301","tools/ci/sweep.py",'len(files) >= 300','len(files) >= 301'),
("S6 stale_pin: fork guard off","tools/ci/sweep.py",'[] if head_repo != self.repo else ',''),
("S7 stale_pin: cache never set","tools/ci/sweep.py",'        if self.pin == ():','        if True:'),
("S8 fresh: later only dispatch event dropped","tools/ci/sweep.py",'r.get("event") == "workflow_dispatch"\n                 and ','True and '),
("S9 fresh: >= -> >","tools/ci/sweep.py",'r.get("created_at", "") >= (gate','r.get("created_at", "") > (gate'),
("S10 fresh: no-completed default ~ -> ''","tools/ci/sweep.py",'(gate.get("completed_at") or "~")','(gate.get("completed_at") or "")'),
("S11 fresh: once-per-sweep off","tools/ci/sweep.py",'        if self.dispatches:\n','        if False:\n'),
("S12 fresh: dispatches not counted","tools/ci/sweep.py",'        self.dispatches += 1\n','        pass\n'),
("S13 fresh: inputs base wrong","tools/ci/sweep.py",'"inputs": {"pr": str(self.pull_number), "base": base}','"inputs": {"pr": str(self.pull_number), "base": ref}'),
("S14 judge: runs not passed (run)","tools/ci/sweep.py",'self.judge(r, g, "completed red", runs)','self.judge(r, g, "completed red")'),
("S15 judge: runs not passed (settle)","tools/ci/sweep.py",'judged before run(s) {late} finished", runs)','judged before run(s) {late} finished")'),
("S16 judge: runs not passed (poll)","tools/ci/sweep.py",'"polled, completed red", list(listing.values()))','"polled, completed red")'),
("S17 stale_pin: compare range reversed","tools/ci/sweep.py",'compare/{base[\'sha\']}...{base[\'ref\']}','compare/{base[\'ref\']}...{base[\'sha\']}'),
]
def run():
    out=[]
    for c in (["python3","-I","-B","tools/ci/gate.py","--self-test"],["python3","-I","-B","tools/ci/sweep.py","--self-test"],["python3","-I","-B","tools/ci/prelude.py","--self-test"],["python3","-B","dev/audit/harnesses/r10_rca_gate_busy_defer_2.py","replay","--ci","tools/ci"]):
        p=subprocess.run(c,cwd=wt,capture_output=True,text=True)
        last=[l for l in (p.stdout+p.stderr).splitlines() if 'checks' in l or 'RESULT' in l]
        out.append((c[3] if c[1]=='-I' else 'replay',p.returncode,last[-1] if last else (p.stdout+p.stderr).strip().splitlines()[-1][:120]))
    return out
surv=0
for name,f,a,b in M:
    p=wt/f;s=p.read_text()
    if s.count(a)!=1: print(f"{name}: ANCHOR {s.count(a)}");continue
    p.write_text(s.replace(a,b,1))
    try: r=run()
    finally: p.write_text(s)
    killed=any(rc!=0 for _,rc,_ in r)
    surv+= not killed
    print(f"{name}: {'KILLED' if killed else 'SURVIVED'} | "+"; ".join(f"{t} rc={rc} {l}" for t,rc,l in r))
print(f"RESULT reviewer-mutants={len(M)} survivors={surv}")
