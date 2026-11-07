import subprocess,sys,pathlib
M=[
("M3 gh-list-rc-ignored","tools/audit/seat/beat_jobs.py",'    if rc != 0:\n        return write_job(ctx, "gantt", [f"gantt: UNREADABLE gh pr list rc={rc}"])\n','    pass\n'),
("M4 roster-show-rc-ignored","tools/audit/seat/beat_jobs.py",'    if rc != 0 or not path:\n        return write_job(ctx, "gantt", [f"gantt: UNREADABLE roster','    if not path:\n        return write_job(ctx, "gantt", [f"gantt: UNREADABLE roster'),
("M5 va-fired-flag-wrong","tools/audit/seat/beat_jobs.py",'(("fire_ledger", "--fired"),','(("fire_ledger", "--fired-ledger"),'),
("M5b va-flags-dropped","tools/audit/seat/beat_jobs.py",'            args += [flag, str(ctx.overlay[key])]','            pass'),
("M7 mark-ne-op-dropped","tools/audit/seat/beat_jobs.py",'        if mark != op or not any(','        if not any('),
("M7b refused-cascade-any","tools/audit/seat/beat_jobs.py",'        if mark == f"#refused {op}" and any(','        if any('),
("M10 rows-no-gantt","tools/audit/seat/beat_jobs.py",'"plan-beat", "gantt", "verdict-audit", "pulse",','"plan-beat", "verdict-audit", "pulse",'),
("M11 no-handoff-wip-fetch","tools/audit/seat/beat_jobs.py",', "+refs/heads/handoff-wip/*:refs/gantt/handoff-wip/*"]',']'),
("M12 fired-ledger-empty","tools/audit/seat/beat_jobs.py",'read(Path(str(ledger))) if ledger else ""','""'),
("M13 gantt-err-tail","tools/audit/seat/beat_jobs.py",'[f"gantt: UNREADABLE sweep_gantt rc={rc}: {(err.strip().splitlines() or [\'\'])[-1]}"]','[]'),
("M14 plan-sha-empty-page","tools/audit/seat/beat_jobs.py",'if page else ""','if True else ""'),
("M15 cascade-line-dropped","tools/audit/seat/beat_jobs.py",'    if cascade:\n        lines.append(','    if False:\n        lines.append('),
]
root=pathlib.Path("/home/user/mut")
sel=sys.argv[1:]
for name,f,a,b in M:
    if sel and name.split()[0] not in sel: continue
    p=root/f; src=p.read_text()
    if src.count(a)!=1: print(name,"ANCHOR",src.count(a)); continue
    p.write_text(src.replace(a,b))
    r=subprocess.run(["python3","-I","tools/audit/seat/beat_jobs.py","--self-test"],cwd=root,capture_output=True,text=True,timeout=900)
    p.write_text(src)
    fails=[l for l in (r.stdout+r.stderr).splitlines() if "FAIL" in l][:3]
    last=(r.stdout+r.stderr).strip().splitlines()[-1:] 
    print(name,"rc",r.returncode,last,fails,flush=True)
