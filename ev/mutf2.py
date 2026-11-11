import subprocess, pathlib, os, sys, time
out=[]
F="custom_components/heatpump_optimizer/services.py"
subprocess.run("git -C /home/user/heatpump_optimizer worktree add --detach /root/w/mutf 7c7f06081827bbf9c52da7b2345b3a5a81048649", shell=True, capture_output=True)
f=pathlib.Path("/root/w/mutf")/F; t=f.read_text(); a="coord.async_simulate(overrides, steady=True)"
if a in t: f.write_text(t.replace(a,"coord.async_simulate(overrides)"))
for s in ("entities.py","deployment_shape.py","doc_claims.py","debug_collect.py","dst_checks.py"):
    for n,d in (("head","/root/w/head"),("f_service_no_steady","/root/w/mutf")):
        r=subprocess.run([sys.executable,"tests/"+s],cwd=d,capture_output=True,text=True,env=dict(os.environ,PYTHONPATH="tests/hastub:tests:custom_components"))
        lines=[l for l in r.stdout.splitlines() if l.strip()]
        fails=[l.strip()[:260] for l in lines if l.lstrip().startswith("FAIL")]
        out.append(f"{n} {s} rc={r.returncode} fails={len(fails)} last={lines[-1][:120] if lines else ''}\n   " + "\n   ".join(fails[:8]))
        pathlib.Path("/root/ev/mutant_f_worktree.log").write_text("mutant: services.py handle_simulate_plan calls async_simulate(overrides) without steady=True, in a git worktree at 7c7f06081827bbf9c52da7b2345b3a5a81048649\n"+"\n".join(out))
print("\n".join(out))
