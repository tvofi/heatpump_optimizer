"""Reviewer's own runtime solver census (not the fixer's tool): for each module of
custom_components/heatpump_optimizer (not __init__) in TREE, import it in a fresh
interpreter with TREE/tests/hastub and TREE/custom_components on the path; record whether
heatpump_optimizer.optimizer and scipy are in sys.modules afterwards."""
import subprocess,sys,os
from pathlib import Path
tree=Path(sys.argv[1]).resolve()
pkg=tree/"custom_components"/"heatpump_optimizer"
env={**os.environ,"PYTHONPATH":f"{tree/'tests'/'hastub'}{os.pathsep}{tree/'custom_components'}"}
mods=sorted(p.stem for p in pkg.glob("*.py") if p.stem!="__init__")
inn=[];fail=[];sci=[]
for m in mods:
    r=subprocess.run([sys.executable,"-c",f"import sys,heatpump_optimizer.{m} as _m; assert _m.__file__.startswith({str(pkg)!r}), _m.__file__; print(int('heatpump_optimizer.optimizer' in sys.modules), int('scipy' in sys.modules))"],capture_output=True,text=True,env=env,cwd="/")
    if r.returncode: fail.append(m); print(m,"FAIL",r.stderr.strip().splitlines()[-1][:150]); continue
    o,s=r.stdout.split()
    if o=="1": inn.append(m)
    if s=="1": sci.append(m)
print("IN:"," ".join(inn))
print(f"RESULT modules={len(mods)} solver_in={len(inn)} scipy_in={len(sci)} import_failures={len(fail)}")
