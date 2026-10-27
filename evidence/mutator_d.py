import subprocess, sys, pathlib, hashlib
WT=sys.argv[1]; F=pathlib.Path(WT)/"tools/audit/seat/roster_sync.py"
HEAD="46725bebaf3ad55dd737471d5989bc12701f4318d1844c8566491334297f8889"
OLD='                    held = already_carried(g.get("carry") or [], text)\n'
NEW=('                    held = next((str(c) for c in (g.get("carry") or [])\n'
     '                                   if f"#{pr.number}" in str(c)), None)\n')
def run(name, old, new):
    subprocess.run(["git","-C",WT,"checkout","--","tools/audit/seat/roster_sync.py"],check=True)
    src=F.read_text(); assert old in src
    F.write_text(src.replace(old,new,1))
    r=subprocess.run([sys.executable,"tools/audit/seat/roster_sync.py","--self-test"],cwd=WT,capture_output=True,text=True)
    fails=[l for l in r.stdout.splitlines() if l.startswith("FAIL ")]
    tail=[l for l in r.stdout.splitlines() if l.startswith("roster_sync self-test:")]
    print(f"RESULT mutant_{name}: {len(fails)} red rc={r.returncode} | {tail[-1] if tail else 'no summary'}")
    for l in fails: print("   ",l[:170])
    subprocess.run(["git","-C",WT,"checkout","--","tools/audit/seat/roster_sync.py"],check=True)
    print("RESULT restored_identical:", hashlib.sha256(F.read_bytes()).hexdigest()==HEAD)
try:
    run("D_reintroduce_pr_number_key", OLD, NEW)
finally:
    subprocess.run(["git","-C",WT,"checkout","--","tools/audit/seat/roster_sync.py"],check=True)
