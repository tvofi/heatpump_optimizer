import subprocess, pathlib, shutil, re
HEAD="/root/w/head"; J="custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
M={"control":None,
   "card_basis_always_plans":('"whatif.basis_schedule"\n', None),
   "card_fallback_plan_money":("num(result.monthly_steady_cost_delta)","num(result.monthly_steady_cost_delta ?? result.monthly_cost_delta)"),
   "card_range_larger_end":("ends[0] === ends[1]","true || ends[0] === ends[1]")}
out=[]
for n,m in M.items():
    d=pathlib.Path(f"/root/cardmut/{n}"); shutil.rmtree(d, ignore_errors=True); d.mkdir(parents=True)
    subprocess.run(f"git -C {HEAD} archive HEAD | tar -x -C {d}", shell=True, check=True)
    if m:
        f=d/J; t=f.read_text()
        if n=="card_basis_always_plans":
            t2,k=re.subn(r'\?\s*"whatif\.basis_schedule"', '? "whatif.basis_plans"', t); assert k==1,k
        elif n=="card_range_larger_end":
            assert t.count(m[0])==1, t.count(m[0]); t2=t.replace("ends[0] === ends[1] ? ends[0]", "true ? ends[1]"); assert t2!=t
        else:
            assert t.count(m[0])==1, t.count(m[0]); t2=t.replace(m[0],m[1])
        f.write_text(t2)
    import os
    pv=subprocess.run(["python3","tests/plan_view.py"],cwd=d,capture_output=True,text=True,env=dict(os.environ,PYTHONPATH="tests/hastub:tests:custom_components"))
    r=subprocess.run(["node","tests/card.mjs"],cwd=d,capture_output=True,text=True)
    lines=[l for l in (r.stdout+r.stderr).splitlines() if l.strip() and not l.lstrip().startswith("ok")]
    out.append(f"== {n} rc={r.returncode}\n"+"\n".join(l[:220] for l in lines[-10:]))
    shutil.rmtree(d)
pathlib.Path("/root/ev/card_mutants.log").write_text("\n".join(out)); print("\n".join(out))
