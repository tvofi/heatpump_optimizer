import subprocess,sys,pathlib
M=[
 ("beat-refusal-silent","tools/audit/seat/beat_jobs.py","    if rc != 0 and not held:\n        held = [f\"toolchain-promote","    if False:\n        held = [f\"toolchain-promote","tools/audit/seat/beat_jobs.py"),
 ("beat-no-statefile","tools/audit/seat/beat_jobs.py","        atomic(ctx.state / \"beatd\" / \"toolchain.txt\", out)","        pass","tools/audit/seat/beat_jobs.py"),
 ("beat-held-prefix","tools/audit/seat/beat_jobs.py","if ln.startswith(\"PROMOTE-HELD \")]","if ln.startswith(\"PROMOTE\")]","tools/audit/seat/beat_jobs.py"),
 ("scan-unbounded","tools/audit/seat/toolchain.py","if r.get(\"status\") == \"completed\"][:SCAN_RUNS]:","if r.get(\"status\") == \"completed\"]:","tools/audit/seat/toolchain.py"),
 ("walk-no-movable","tools/audit/seat/toolchain.py","            movable(run.get(\"head_sha\") or \"\", f\"run","            (lambda *a: None)(run.get(\"head_sha\") or \"\", f\"run","tools/audit/seat/toolchain.py"),
 ("init-twice","tools/audit/seat/toolchain.py","    if old and create:\n","    if False:\n","tools/audit/seat/toolchain.py"),
 ("held-runs-2","tools/audit/seat/toolchain.py","HELD_RUNS = 3 ","HELD_RUNS = 2 ","tools/audit/seat/toolchain.py"),
 ("sha-nonsha-head","tools/audit/seat/toolchain.py","and r.get(\"head_sha\") == sha]","]","tools/audit/seat/toolchain.py"),
 ("status-cancelled-green","tools/ci/gate.py","all(j is not None and j[1] == \"success\" for j in ran)","all(j is not None and j[1] in (\"success\",\"cancelled\") for j in ran)","tools/ci/gate.py"),
 ("prune-prefix-loose","tools/audit/seat/prune_refs.py","name.startswith(TOOLCHAIN_PREFIX)","\"toolchain\" in name","tools/audit/seat/prune_refs.py"),
]
for name,f,a,b,t in M:
    p=pathlib.Path(f); s=p.read_text()
    if s.count(a)!=1: print(f"RESULT mutant={name} verdict=NOT-APPLIED count={s.count(a)}"); continue
    p.write_text(s.replace(a,b))
    try:
        r=subprocess.run([sys.executable,"-I",t,"--self-test"],capture_output=True,text=True,timeout=200)
        last=(r.stdout+r.stderr).strip().splitlines()[-1:] 
        print(f"RESULT mutant={name} rc={r.returncode} verdict={'killed' if r.returncode else 'SURVIVED'} :: {last}",flush=True)
    finally:
        p.write_text(s)
