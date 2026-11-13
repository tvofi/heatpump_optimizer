import subprocess,sys,pathlib
root=pathlib.Path(sys.argv[1])
M=[("M1 zombie record dropped","tools/pr/cancel_superseded.py","zombies[rid] = now","pass"),
("M2 protected check dropped","tools/pr/cancel_superseded.py"," or pr in protected"," or False"),
("M3 priority check dropped (if prio)","tools/pr/cancel_superseded.py","    if prio:\n","    if True:\n"),
("M4 allow_cancel hold dropped","tools/pr/cancel_superseded.py","        if not allow_cancel:\n            return out\n",""),
("M5 pause CP guard dropped","tools/audit/seat/ci_pause.py","if not ci_priority.may_pause(t, setting):","if False:"),
("M6 pause dormancy switch dropped","tools/audit/seat/ci_pause.py","if not setting[\"priority_cancel\"]:","if False:"),
("M7 pause verdict guard dropped","tools/audit/seat/ci_pause.py","if self._verdicted(p[\"n\"]) is not False:","if False:"),
("M8 tier outside dropped","tools/audit/seat/ci_priority.py"," or rl.is_outside(g)",""),
("M9 sweep has_merge_verdict dropped","tools/pr/cancel_superseded.py","            if has_merge_verdict(api, a.repo, pr) is not False:\n                protected.add(pr)","            if False:\n                protected.add(pr)"),
]
for name,f,a,b in M:
    p=root/f; t=p.read_text()
    if t.count(a)!=1: print(name,"ANCHOR",t.count(a)); continue
    p.write_text(t.replace(a,b))
    try:
        r=subprocess.run([sys.executable,f,"--self-test"],cwd=root,capture_output=True,text=True,timeout=100)
        out=(r.stdout+r.stderr).strip().splitlines()
        fails=[l for l in out if "FAIL" in l][:3]
        print(f"{name}: rc={r.returncode} last={out[-1] if out else ''} fails={fails}")
    finally:
        p.write_text(t)
