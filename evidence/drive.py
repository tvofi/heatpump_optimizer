import subprocess, sys, os, pathlib, concurrent.futures as cf
H="ddf75aaf8651c502794de257bbc76c044282f102"
REPO="/home/user/heatpump_optimizer"
F="custom_components/heatpump_optimizer/pump_arbiter.py"
M={
 "X0-null": None,
 "X1-boost": ("    if boosts.active(boost.CHANNEL_SPACE, now) or boosts.active(boost.CHANNEL_DHW, now):\n        return True\n", ""),
 "X2-sysid": ("    if (inp.action or {}).get(\"mode\") == \"system_identification\":\n        return None\n    if boosts.active", "    if boosts.active"),
 "X3a-mode": ("    if inp.mode not in (MODE_AUTO, MODE_ECONOMY) or inp.plan_stale or inp.plan is None:", "    if inp.plan_stale or inp.plan is None:"),
 "X3b-stale": ("    if inp.mode not in (MODE_AUTO, MODE_ECONOMY) or inp.plan_stale or inp.plan is None:", "    if inp.mode not in (MODE_AUTO, MODE_ECONOMY) or inp.plan is None:"),
 "X4-released": ("    inp = wiring.inputs()\n    if inp.entry_released:\n        return\n    on = step_supply", "    inp = wiring.inputs()\n    on = step_supply"),
 "X5-release": ("    release_supply(held)\n    inp = coord.arbiter_inputs()", "    inp = coord.arbiter_inputs()"),
 "X6-armonce": ("    if held.supply_unsub is not None:\n        return\n    inp = wiring.inputs()", "    inp = wiring.inputs()"),
}
def run(name):
    wt=f"/tmp/claude-0/sav/wt-{name}"
    subprocess.run(["git","-C",REPO,"worktree","add","-q","--detach",wt,H],check=True)
    p=pathlib.Path(wt,F); s=p.read_text()
    if M[name]:
        old,new=M[name]; assert s.count(old)==1,(name,s.count(old)); p.write_text(s.replace(old,new,1))
    env=dict(os.environ,PYTHONPATH="tests/hastub")
    r=subprocess.run(["python3","tests/features.py"],cwd=wt,env=env,capture_output=True,text=True)
    out=r.stdout+r.stderr
    fails=[l for l in out.splitlines() if "FAIL" in l]
    tail=[l for l in out.splitlines() if "FEATURE CHECKS" in l]
    pathlib.Path(f"/tmp/claude-0/sav/{name}.log").write_text(out)
    subprocess.run(["git","-C",REPO,"worktree","remove","--force",wt])
    return f"RESULT {name} rc={r.returncode} {tail} FAILS={fails[:12]}"
with cf.ThreadPoolExecutor(4) as ex:
    for res in ex.map(run, M): print(res, flush=True)
