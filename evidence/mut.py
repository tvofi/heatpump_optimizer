import subprocess,sys,pathlib
W=pathlib.Path.home()/"wt"
M=[
("tools/audit/machinery_ratchet.py",'            bad.append("target")','            pass',"tools/audit/machinery_ratchet.py"),
("tools/audit/machinery_ratchet.py",'binds = cand is not None and cand["kind"] != "production"','binds = cand is not None',"tools/audit/machinery_ratchet.py"),
("tools/audit/machinery_ratchet.py",'return max(0, cap - tdoc["step"] * (n // tdoc["every_merges"])), n','return cap, n',"tools/audit/machinery_ratchet.py"),
("tools/audit/machinery_ratchet.py",'return max(0, cap - tdoc["step"] * (n // tdoc["every_merges"])), n','return cap - tdoc["step"] * (n // tdoc["every_merges"]), n',"tools/audit/machinery_ratchet.py"),
("tools/audit/machinery_ratchet.py",'if len(line.split()) == 3)','if len(line.split()) >= 2)',"tools/audit/machinery_ratchet.py"),
("tools/audit/machinery_ratchet.py",'past = m[c] > t + doc[c + BAND_SUFFIX]','past = m[c] > t',"tools/audit/machinery_ratchet.py"),
("tools/audit/machinery_ratchet.py",'t, n = scheduled_target(repo, base or head, doc[c], tdoc)','t, n = scheduled_target(repo, head, doc[c], tdoc)',"tools/audit/machinery_ratchet.py"),
("tools/audit/machinery_ratchet.py",'cand = rows[0] if base and rows and rows[0]["sha"] == head else None','cand = rows[0] if rows else None',"tools/audit/machinery_ratchet.py"),
("tools/audit/machinery_ratchet.py",'    if _git(repo, "merge-base", "--is-ancestor", a, tip, check=False).returncode != 0:\n        raise','    if False:\n        raise',"tools/audit/machinery_ratchet.py"),
("tools/audit/machinery_ratchet.py",'    if extra:\n        raise Refusal(f"{TARGET_BUDGETS}: {extra}','    if False:\n        raise Refusal(f"{TARGET_BUDGETS}: {extra}',"tools/audit/machinery_ratchet.py"),
("tools/audit/seat/pr_cap.py",'    if len(taken) < free:','    if len(taken) <= free:',"tools/audit/seat/pr_cap.py"),
("tools/audit/seat/pr_cap.py",'return text, m + u >= free','return text, m >= free',"tools/audit/seat/pr_cap.py"),
("tools/audit/seat/pr_cap.py",'if len(p.get("files") or []) >= GH_FILES_LIMIT','if len(p.get("files") or []) > GH_FILES_LIMIT',"tools/audit/seat/pr_cap.py"),
("tools/audit/seat/pr_cap.py",'    return v if isinstance(v, int) and v > PRODUCTION_SLOTS else None','    return v if isinstance(v, int) else None',"tools/audit/seat/pr_cap.py"),
("tools/audit/seat/pr_cap.py",'        if rc == 0 and slug is not None:','        if False:',"tools/audit/seat/pr_cap.py"),
("tools/policy/budget_raise_gate.py",'        (("step",), MIN),','        (("step",), MAX),',"tools/policy/budget_raise_gate.py"),
("tools/policy/budget_raise_gate.py",'        (("anchor",), FROZEN),','        (("anchor",), FREE),',"tools/policy/budget_raise_gate.py"),
("tools/policy/budget_raise_gate.py",'        (("every_merges",), MAX),','        (("every_merges",), MIN),',"tools/policy/budget_raise_gate.py"),
("tools/audit/seat/orchestrator_tick.py",'            self.line(S, *cap_mod.class_line(cap_mod.by_class(counted, files, rule), slots))','            pass',"tools/audit/seat/orchestrator_tick.py"),
]
for i,(f,a,b,t) in enumerate(M):
    p=W/f; s=p.read_text()
    if s.count(a)!=1: print(f"M{i} NOT-APPLIED count={s.count(a)} {f}: {a[:60]!r}"); continue
    p.write_text(s.replace(a,b))
    try:
        r=subprocess.run(["python3","-I",t,"--self-test"],cwd=W,capture_output=True,text=True,timeout=900)
        last=(r.stdout+r.stderr).strip().splitlines()[-1:] 
        print(f"M{i} {'KILLED' if r.returncode else 'SURVIVED'} rc={r.returncode} {f}: {a.strip()[:70]!r} -> {b.strip()[:40]!r} | {last}")
    finally: p.write_text(s)
