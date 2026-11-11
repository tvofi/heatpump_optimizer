import subprocess, pathlib, shutil, os, sys
HEAD="/root/w/head"; F="custom_components/heatpump_optimizer/services.py"
SCRIPTS=["entities.py","manual_plan.py","doc_claims.py","deployment_shape.py","config_flow_steps.py","finite_boundary.py"]
out=[]
for n in ("control","f_service_no_steady"):
    d=pathlib.Path(f"/root/mutf/{n}"); shutil.rmtree(d, ignore_errors=True); d.mkdir(parents=True)
    subprocess.run(f"git -C {HEAD} archive HEAD | tar -x -C {d}", shell=True, check=True)
    if n!="control":
        f=d/F; t=f.read_text(); a="coord.async_simulate(overrides, steady=True)"; assert t.count(a)==1; f.write_text(t.replace(a,"coord.async_simulate(overrides)"))
    for s in SCRIPTS:
        r=subprocess.run([sys.executable,"tests/"+s],cwd=d,capture_output=True,text=True,env=dict(os.environ,PYTHONPATH="tests/hastub:tests:custom_components"))
        last=[l for l in r.stdout.splitlines() if l.strip()][-1:] 
        fails=[l.strip()[:200] for l in r.stdout.splitlines() if "FAIL" in l and "CHECKS" not in l][:6]
        out.append(f"{n} {s} rc={r.returncode} {last} {fails}")
        pathlib.Path("/root/ev/mutant_f_other_scripts.log").write_text("\n".join(out))
    shutil.rmtree(d)
print("\n".join(out))
