import subprocess, sys, pathlib, hashlib, os
WT = sys.argv[1]
F = pathlib.Path(WT) / "tools/audit/seat/roster_sync.py"
HEAD_SHA = "46725bebaf3ad55dd737471d5989bc12701f4318d1844c8566491334297f8889"

A_OLD = '''                    held = already_carried(g.get("carry") or [], text)
                    if held is not None:
                        refusals.append((pr.number, dest,
                                         "already carried (the same finding, "
                                         f"from #{pr.number}): {held[:60]!r}"))
                        continue
'''
B_OLD = '''        if want_rulings & rulings(c):
            return str(c)
'''
C_OLD = '''        if finding_words(c) == want:
            return str(c)
'''

def restore():
    subprocess.run(["git","-C",WT,"checkout","--","tools/audit/seat/roster_sync.py"],check=True)

def run(name, old, new):
    restore()
    src = F.read_text()
    assert old in src, f"{name}: pattern not found"
    F.write_text(src.replace(old, new, 1))
    r = subprocess.run([sys.executable, "tools/audit/seat/roster_sync.py", "--self-test"],
                       cwd=WT, capture_output=True, text=True)
    fails = [l for l in r.stdout.splitlines() if l.startswith("FAIL ")]
    tail = [l for l in r.stdout.splitlines() if l.startswith("roster_sync self-test:")]
    print(f"RESULT mutant_{name}_reddened: {len(fails)} rc={r.returncode} | {tail[-1] if tail else 'no summary'}")
    for l in fails:
        print("   ", l[:150])
    restore()
    sha = hashlib.sha256(F.read_bytes()).hexdigest()
    print(f"RESULT mutant_{name}_restored_identical: {sha == HEAD_SHA} ({sha[:12]})")

try:
    run("A_call_and_refusal_removed", A_OLD, "")
    run("B_ruling_arm_removed", B_OLD, "")
    run("C_text_arm_removed", C_OLD, "")
finally:
    restore()
    print("RESULT final_restore_identical:", hashlib.sha256(F.read_bytes()).hexdigest() == HEAD_SHA)
