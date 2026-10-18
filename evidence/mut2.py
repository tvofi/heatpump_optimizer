import subprocess, sys, pathlib
exec(open("mut.py").read().split("try:")[0])
W = ('    if field not in WIRE_FIELDS:\n        raise Refuse(f"--field for wire-issue is one of "\n                     f"{\', \'.join(WIRE_FIELDS)}, not {field!r}")\n', '')
J = {"J1 both unwire guards (M7+M8)": [M["M7 main --field guard for wire ops deleted"], M["M8 op-level WIRE_FIELDS guard in unwire deleted"]],
     "J2 both wire guards (M7+op wire guard)": [M["M7 main --field guard for wire ops deleted"], W],
     "J3 op wire guard alone": [W]}
try:
  for name, reps in J.items():
    s = orig
    for a,b in reps:
      assert s.count(a)==1, name; s = s.replace(a,b)
    F.write_text(s)
    r = subprocess.run([sys.executable,str(F),"--self-test"],capture_output=True,text=True,cwd="wt")
    out=r.stdout+r.stderr
    print(f"RESULT mutant {name}: rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'} | {[l for l in out.splitlines() if 'self-test:' in l][-1]}")
    if r.returncode: print("   ", [l for l in out.splitlines() if "got:" in l or "FAIL" in l][:5])
finally:
  F.write_text(orig)
