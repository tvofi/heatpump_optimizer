import subprocess, sys, os, pathlib, concurrent.futures as cf
H="ddf75aaf8651c502794de257bbc76c044282f102"
REPO="/home/user/heatpump_optimizer"
F="custom_components/heatpump_optimizer/pump_arbiter.py"
M={
 "U1195-cmpbound": ("i >= len(inp.plan.power_schedule or ())", "i > len(inp.plan.power_schedule or ())"),
 "U1222-guardoff": ("    if not EntryConfig.from_mapping(inp.config).heat_pump_switch_entity:\n        return\n\n    async def _tick", "    if False:\n        return\n\n    async def _tick"),
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
with cf.ThreadPoolExecutor(2) as ex:
    for res in ex.map(run, M): print(res, flush=True)
