import subprocess, sys, pathlib
exec(open("mut.py").read().split("try:")[0])
J={"M11 wire default field -> fixes": [('op_wire_issue(roster, a.group, value, a.field or "issues")','op_wire_issue(roster, a.group, value, a.field or "fixes")')],
   "M12 unwire dedupe-all -> remove first only": [('    g[field] = [i for i in held if i != n]\n','    held.remove(n); g[field] = held\n')]}
try:
  for name, reps in J.items():
    s = orig
    for a,b in reps:
      assert s.count(a)==1, name; s = s.replace(a,b)
    F.write_text(s)
    r = subprocess.run([sys.executable,str(F),"--self-test"],capture_output=True,text=True,cwd="wt")
    out=r.stdout+r.stderr
    print(f"RESULT mutant {name}: rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'} | {[l for l in out.splitlines() if 'self-test:' in l][-1]}")
finally:
  F.write_text(orig)
