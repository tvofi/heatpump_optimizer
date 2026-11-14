# reviewer-built mutant driver (not the finder's; this PR names no finder harness)
import os, subprocess, sys, shutil
src="tools/ci/selftest_scope.py"; orig=open(src).read()
M=[("pop-only-GITHUB_BASE_REF",'("GITHUB_BASE_REF", "SELFTEST_BASE")','("GITHUB_BASE_REF",)'),
   ("pop-only-SELFTEST_BASE",'("GITHUB_BASE_REF", "SELFTEST_BASE")','("SELFTEST_BASE",)'),
   ("int-guard-passes-None",'return rc if isinstance(rc, int) else 1','return rc if isinstance(rc, int) else 0'),
   ("union_entries-keeps-unmeasured-steps",'return {sid: union_entry(old.get(sid), m) for sid, m in measured.items()}','return {**old, **{sid: union_entry(old.get(sid), m) for sid, m in measured.items()}}'),
   ("drift-probe-own-dirs-removed",'a in dirs or a in set(m["dirs"])','a in dirs')]
env=dict(os.environ, GITHUB_BASE_REF="main", SELFTEST_BASE="nonesuch")
try:
  for name,a,b in M:
    assert orig.count(a)==1,(name,orig.count(a))
    open(src,"w").write(orig.replace(a,b))
    r=subprocess.run([sys.executable,"-I",src,"--self-test"],capture_output=True,text=True,env=env)
    tail=(r.stdout.strip().splitlines() or [r.stderr.strip()[-200:]])[-1]
    print(("KILLED" if r.returncode else "SURVIVED"),name,"::",tail,"rc",r.returncode)
finally:
  open(src,"w").write(orig)
