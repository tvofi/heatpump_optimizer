"""Apply each named mutant, run each given test script, report rc and FAIL lines."""
import pathlib, subprocess, sys, os
ns={}; exec(open('/tmp/rvtools/xmut_defs.py').read(), ns); M=ns['M']
names=sys.argv[1].split(','); scripts=sys.argv[2].split(',')
env=dict(os.environ, PYTHONPATH="tests/hastub")
def run(s):
    cmd=["node",s] if s.endswith(".mjs") else [sys.executable,s]
    return subprocess.run(cmd,capture_output=True,text=True,env=env,timeout=3000)
if os.environ.get("BASE"):
  for s in scripts:
    r=run(s); print(f"BASE {s}: rc {r.returncode}", flush=True)
for name,(f,a,b) in M.items():
    if name.split()[0] not in names: continue
    p=pathlib.Path(f); orig=p.read_text(); assert orig.count(a)==1, name
    p.write_text(orig.replace(a,b))
    try:
        for s in scripts:
            r=run(s); fl=[l.strip()[:140] for l in (r.stdout+r.stderr).splitlines() if l.strip().startswith(("FAIL","Traceback"))]
            print(f"{name} | {s}: rc {r.returncode}, {len(fl)} FAIL", flush=True)
            for l in fl[:4]: print("    ",l, flush=True)
    finally: p.write_text(orig)
