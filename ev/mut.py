import subprocess, sys, pathlib, shutil
M = [
 ("M1","tools/ci/prelude.py",'        if not judging({"title": r.get("display_title") or "", "jobs": run_jobs(get, ctx["repo"], r["id"])}):','        if False and not judging({"title": r.get("display_title") or "", "jobs": run_jobs(get, ctx["repo"], r["id"])}):'),
 ("M2","tools/ci/prelude.py",'        if not judging({"title": r.get("display_title") or "", "jobs": run_jobs(get, ctx["repo"], r["id"])}):','        if True:'),
 ("M3","tools/ci/prelude.py",'    if not why and kind in BODY_KINDS and pr:','    if not why and kind == "edit" and pr:'),
 ("M4","tools/ci/prelude.py",'    return all(jobs.get(u) == ("completed", "skipped")','    return any(jobs.get(u) == ("completed", "skipped")'),
 ("M5","tools/ci/gate.py",'        st, _, _ = post(f"repos/{ctx[\'repo\']}/actions/runs/{r[\'id\']}/rerun")','        st = 201'),
 ("M6","tools/ci/gate.py",'        return False, [SELF_DEFERRED]       #','        pass  #'),
 ("M7","tools/ci/gate.py",'r.get("status") != "action_required" and deferring(r))','r.get("status") != "action_required" and False)'),
 ("M8","tools/ci/gate.py",'    if kind != "code" or not pr or post is None:','    if not pr or post is None:'),
 ("R1-waiting_on-drops-pending","tools/ci/gate.py",'    return sorted(set(busy(ctx, others)) | set(pending(ctx, others)))','    return sorted(set(busy(ctx, others)))'),
 ("R2-redispatch-ignores-completed","tools/ci/gate.py",' or r.get("status") != "completed":',':'),
 ("R3-pending-takes-earliest","tools/ci/gate.py",'r["id"] > latest.get(t[0], {"id": -1})["id"]','r["id"] < latest.get(t[0], {"id": 10**12})["id"]'),
]
out=[]
for name,f,old,new in M:
    p=pathlib.Path(f); src=p.read_text()
    n=src.count(old)
    if n!=1: out.append(f"{name}: SKIP pattern count {n}"); continue
    p.write_text(src.replace(old,new))
    for d in pathlib.Path("tools/ci").rglob("__pycache__"): shutil.rmtree(d)
    res=[]
    for t in ("prelude","gate"):
        r=subprocess.run([sys.executable,"-I",f"tools/ci/{t}.py","--self-test"],capture_output=True,text=True)
        tail=(r.stdout+r.stderr).strip().splitlines()
        summ=[l for l in tail if "self-test:" in l]
        res.append(f"{t} rc={r.returncode} {summ[-1] if summ else tail[-1:]}")
    p.write_text(src)
    out.append(f"{name}: "+" | ".join(res))
print("\n".join(out))
