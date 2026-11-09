import sys,subprocess,os
H="699491f2368ddcd96c0fb14cf6040155f66f5c44"
CM="custom_components/heatpump_optimizer/"
M={
 "CTRL":None,
 "M1":(CM+"coordinator.py","        if measured:\n","        if True:\n"),
 "M4":(CM+"thermal_model.py",'    return const.ESTIMATE_ID_MARK in str(entity_id or "").lower()\n','    return False\n'),
 "M7":(CM+"thermal_model.py","            and (self.heat_sees_dhw or not dhw)\n",""),
 "G":(CM+"coordinator.py",'MeasuredCop.from_dict(stored.get("measured_cop") if _COP_BASELINE_KEY in stored else None)','MeasuredCop.from_dict(stored.get("measured_cop"))'),
 "RELEC":(CM+"thermal_model.py","            and self.cop_electric()\n            and not (self.heat_estimated","            and not (self.heat_estimated"),
}
name=sys.argv[1]; d=os.path.expanduser(f"~/mw/{name}")
subprocess.run(["git","-C","/home/user/heatpump_optimizer","worktree","add","-q","--detach",d,H],check=True)
if M[name]:
    f,a,b=M[name]; p=os.path.join(d,f); s=open(p).read(); assert s.count(a)==1,(name,s.count(a)); open(p,"w").write(s.replace(a,b))
print(subprocess.run(["git","-C",d,"diff","--stat"],capture_output=True,text=True).stdout)
env=dict(os.environ,PYTHONPATH="tests/hastub")
r=subprocess.run(["python3","tests/features.py"],cwd=d,env=env,capture_output=True,text=True)
out=r.stdout+r.stderr
fails=[l for l in out.splitlines() if "FAIL" in l]
print(f"RESULT mutant={name} rc={r.returncode}")
print("\n".join(fails[-30:])); print(out.splitlines()[-1] if out else "")
