import subprocess, sys, pathlib
WT = pathlib.Path("/private/tmp/rev-2883-r2/wt")
MT = WT/"tools/audit/merge_throughput.py"; RL = WT/"tools/audit/seat/roster_lib.py"
mo, ro = MT.read_text(), RL.read_text()
try:
    MT.write_text(mo.replace('"cat-file", "-e", f"{sha}:{path}"',
                             '"rev-parse", "--verify", "--quiet", f"{sha}:{path}"'))
    RL.write_text(ro.replace('"cat-file", "-e", f"{ref}:{CRITICAL_PATH_NAME}"',
                             '"rev-parse", "--verify", "--quiet", f"{ref}:{CRITICAL_PATH_NAME}"'))
    for label, cmd in (("flow-self-test", [sys.executable,"-I",str(MT),"--self-test"]),
                       ("roster_lib-self-test", [sys.executable,"-I",str(RL),"--self-test"])):
        r = subprocess.run(cmd, capture_output=True, text=True)
        tail = [l for l in r.stdout.splitlines() if l.startswith("FAIL") or l.startswith("ok:") or "self-test:" in l]
        print(f"RESULT {label} exit={r.returncode} :: {' | '.join(tail[-3:])}")
finally:
    MT.write_text(mo); RL.write_text(ro)
print("RESULT restored_clean =", subprocess.run(["git","-C",str(WT),"status","--porcelain"],capture_output=True,text=True).stdout.strip()=="")
