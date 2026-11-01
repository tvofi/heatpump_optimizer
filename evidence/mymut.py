import subprocess, sys, pathlib
R = pathlib.Path(sys.argv[1])
P = {
 "M1-round1": ("tools/policy/budget_raise_gate.py", "want = (round(float(m.group(1)), 4), m.group(2))\n    got = [(round(float(a), 4), v)", "want = (round(float(m.group(1)), 1), m.group(2))\n    got = [(round(float(a), 1), v)"),
 "M2-rc-ignored": ("tools/policy/budget_raise_gate.py", "    if r.returncode != 0:\n        raise RuntimeError(f\"{ARCH_SCORER}", "    if False:\n        raise RuntimeError(f\"{ARCH_SCORER}"),
 "M3-expired-guarded": ("tools/policy/budget_raise_gate.py", "    return end is None or end > now", "    return True"),
 "M4-last-line": ("tools/policy/budget_raise_gate.py", "    return (r.stdout.splitlines() or [\"\"])[0]", "    return (r.stdout.splitlines() or [\"\"])[-1]"),
 "M5-no-owner": ("tools/policy/budget_raise_gate.py", "    if not (m and _is_owner(comment.get(\"user\"))\n", "    if not (m\n"),
}
for n,(t,o,new) in P.items():
    p = R/t; s = p.read_text()
    assert s.count(o)==1, n
    p.write_text(s.replace(o,new))
    try:
        fails=[]
        for tgt,flag in (("tools/pr/gh_comment.py","self-test"),("tools/policy/budget_raise_gate.py","--self-test")):
            r=subprocess.run([sys.executable,tgt,flag],cwd=R,capture_output=True,text=True)
            fails+=[l.strip() for l in r.stdout.splitlines() if l.strip().startswith("FAIL")]
    finally:
        p.write_text(s)
    print(f"RESULT mymutant={n} fails={len(fails)} {'KILLED' if fails else 'SURVIVED'}"); [print("   ",f[:150]) for f in fails[:3]]
