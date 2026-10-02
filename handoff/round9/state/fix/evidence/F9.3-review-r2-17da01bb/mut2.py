import subprocess, sys, os, pathlib
S=os.environ["S"]; W=pathlib.Path(S+"/wt2g"); P="custom_components/heatpump_optimizer/coordinator.py"
M_ALL={
"N1_cost_floor_back":('floor = self._energy_totals[key] if key.endswith("_kwh") else -np.inf','floor = self._energy_totals[key]'),
"N2_kwh_floor_off":('floor = self._energy_totals[key] if key.endswith("_kwh") else -np.inf','floor = -np.inf'),
"N3_empty_day_as_streak":('if "day" in day else ()','if day.get("day") else ()'),
"N4_streak_dropped":('cleaned = {"day": str(day["day"]), **numbers} if keys else numbers','cleaned = {"day": str(day["day"]), **numbers} if keys else {"day": "", **numbers}'),
}
M={k:v for k,v in M_ALL.items() if k in os.environ.get("ONLY","").split(",")}
env=dict(os.environ, PYTHONPATH="tests/hastub", OPENBLAS_CORETYPE="Haswell", OPENBLAS_NUM_THREADS="1")
drivers=sys.argv[1:] or ["tests/finite_boundary.py"]
for name,(a,b) in M.items():
    p=W/P; src=p.read_text(); n=src.count(a)
    if n!=1: print(name,"SITE-COUNT",n,flush=True); continue
    p.write_text(src.replace(a,b))
    try:
        for d in drivers:
            r=subprocess.run([S+"/vci/bin/python",d],cwd=W,env=env,capture_output=True,text=True)
            fails=[l[:160] for l in (r.stdout+r.stderr).splitlines() if l.startswith("FAIL")][:2]
            print(name,d,"rc=%d"%r.returncode,"KILLED" if r.returncode else "SURVIVED",fails,flush=True)
    finally:
        p.write_text(src)
