import subprocess, sys, re, os
S=os.path.dirname(__file__)
R='/home/user/heatpump_optimizer'
M=[
 ("M1 carried ignored in hygiene","tests/env_drift.py","        if claim_file in carried:\n            inherited = None\n        elif kinds[claim_file]:","        if kinds[claim_file]:","py"),
 ("M2 untouched drop guard off","tests/env_drift.py","    if text == baseline_text:\n        return None\n    if inherited_claims_error(","    if inherited_claims_error(","py"),
 ("M3 judge_drift excuses every line","tests/env_drift.py","    excusing = authored_claims(\n        claims, _claimed_at(repo, fork_point(repo, ref), CLAIM_FILE))","    excusing = claims","py"),
 ("M4 apply baseline at ref tip","tests/env_drift.py","            shown = _show_at(repo, fork_point(repo, ref), rel)","            shown = _show_at(repo, ref, rel)","py"),
 ("M5 card excuses every line","tests/card_rig.mjs","excusing: authoredClaims(tree.claims, base.claims) }","excusing: tree.claims }","js"),
 ("M6 card untouched off","tests/card_rig.mjs",'  const untouched = (treeText || "") === (baseText || "");','  const untouched = false;',"js"),
]
for name,f,a,b,k in M:
    p=os.path.join(R,f); src=open(p).read()
    assert src.count(a)==1,name
    open(p,'w').write(src.replace(a,b))
    try:
        if k=="py":
            r=subprocess.run(["python3","tests/entities.py"],cwd=R,env={**os.environ,"PYTHONPATH":"tests/hastub"},capture_output=True,text=True)
        else:
            r=subprocess.run(["node","tests/card.mjs"],cwd=R,capture_output=True,text=True)
        out=r.stdout+r.stderr
        fails=[l.strip()[:150] for l in out.splitlines() if re.match(r'\s+FAIL',l) and not re.match(r'\s+FAIL a\d+:',l)]
        print(f"{name}: rc={r.returncode}"); [print("   ",x) for x in fails]; print("   ",out.strip().splitlines()[-1])
    finally:
        open(p,'w').write(src)
