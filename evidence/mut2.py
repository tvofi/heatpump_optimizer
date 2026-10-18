import subprocess, os, time
WT="/Users/timmalmstrom/hpo-seats/r10s3/review-2379/wt"; EV="/Users/timmalmstrom/hpo-seats/r10s3/review-2379/h/ev"
E="custom_components/heatpump_optimizer/entity.py"; S="custom_components/heatpump_optimizer/sensor.py"; C="custom_components/heatpump_optimizer/climate.py"
MUT=[
 ("S1f_climate140_GUARD_OFF_false",C,"        if measured is not None:\n            return float(measured)","        if False:\n            return float(measured)"),
 ("S2f_entity140_GUARD_OFF_false",E,"    if isinstance(value, np.generic):\n        value = value.item()\n    if isinstance(value, bool) or not","    if False:\n        value = value.item()\n    if isinstance(value, bool) or not"),
 ("S2t_entity140_GUARD_ON_true",E,"    if isinstance(value, np.generic):\n        value = value.item()\n    if isinstance(value, bool) or not","    if True:\n        value = value.item()\n    if isinstance(value, bool) or not"),
 ("S2d_R1_unwrap_deleted",E,"    if isinstance(value, np.generic):\n        value = value.item()\n    if isinstance(value, bool) or not","    if isinstance(value, bool) or not"),
]
env=dict(os.environ,PYTHONPATH="tests/hastub")
for mid,f,old,new in MUT:
    if f:
        p=os.path.join(WT,f); src=open(p).read(); n=src.count(old)
        if n!=1: print(mid,"NOT APPLIED",n,flush=True); continue
        open(p,"w").write(src.replace(old,new))
    try:
        t0=time.time(); r=subprocess.run(["python3","tests/finite_boundary.py"],cwd=WT,env=env,capture_output=True,text=True,timeout=2400)
        log=r.stdout+r.stderr; open(f"{EV}/r2_{mid}.log","w").write(log)
        fails=[l.strip()[:200] for l in log.splitlines() if l.strip().startswith("FAIL") or "Traceback" in l]
        print(mid,f"rc={r.returncode}",f"{int(time.time()-t0)}s","KILLED" if r.returncode else "SURVIVED",log.strip().splitlines()[-1][:80],flush=True)
        for l in fails[:3]: print("   ",l,flush=True)
    finally:
        if f: subprocess.run(["git","checkout","--",f],cwd=WT,check=True)
print("restored:",subprocess.run(["git","status","--short"],cwd=WT,capture_output=True,text=True).stdout or "clean")
