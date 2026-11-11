import subprocess, sys, os, re
os.chdir(os.path.expanduser("~/wt"))
C="custom_components/heatpump_optimizer/"
A=C+"pump_arbiter.py"; S=C+"setpoint_check.py"; T=C+"thermal_model.py"
def ret_del(line):  # replace return statement with pass, same indent
    ind=line[:len(line)-len(line.lstrip())]; return ind+"pass"
M=[
 ("_dhw_write GUARD_OFF 90de19e4","guard_pins",A,"    if cycle is None:","    if False:"),
 ("_dhw_write RETURN_DEL e7e1a636","block_duty",A,'    return _bounded(inp, "dhw_setpoint", float(cycle), rounding="up")',"    pass"),
 ("dhw_gated RETURN_DEL 7523de18","block_duty",A,'    return not (reading is None or written is None or _differs("dhw_setpoint", reading, written[0]))',"    pass"),
 ("_dhw_floor CLAMP_DROP 645cbad5","block_duty",S,"    return floor if disinfection is None else max(floor, float(disinfection))","    return floor if disinfection is None else (floor)"),
 ("_dhw_floor RETURN_DEL 645cbad5","block_duty",S,"    return floor if disinfection is None else max(floor, float(disinfection))","    pass"),
 ("dhw_cycle_temp CLAMP_DROP 25788b20","guard_pins",T,"        return None if target is None else max(self.dhw_setpoint, target)","        return None if target is None else (self.dhw_setpoint)"),
 ("dhw_cycle_temp RETURN_DEL 25788b20","guard_pins",T,"        return None if target is None else max(self.dhw_setpoint, target)","        pass"),
 ("dhw_disinfection_temp RETURN_DEL aae31b25","guard_pins",T,"        return self.dhw_legionella_temp if self.legionella_cycle_active else None","        pass"),
 ("dhw_hard_max_temp CLAMP_DROP b26a9d8f","block_duty",T,"        return min(70.0, self.dhw_setpoint if top is None else top)","        return (70.0)"),
 ("dhw_hard_max_temp RETURN_DEL b26a9d8f","guard_pins",T,"        return min(70.0, self.dhw_setpoint if top is None else top)","        pass"),
 ("M11 arbiter revert (cycle<=everyday -> nearest)","block_duty",A,"    if cycle is None:\n","    if cycle is None or cycle <= everyday:\n"),
]
for name,test,f,old,new in M:
    src=open(f).read(); n=src.count(old)
    if n!=1: print(f"RESULT {name}: anchor count {n} -- not applied"); continue
    open(f,"w").write(src.replace(old,new))
    try:
        p=subprocess.run([sys.executable,f"tests/{test}.py"],capture_output=True,text=True,timeout=300,env=dict(os.environ,PYTHONPATH="tests/hastub:custom_components:tests"))
        out=p.stdout+p.stderr; m=re.findall(r"(\d+) of (\d+)|FAILED: (\d+)|(\d+) failed",out)
        tail=[l for l in out.strip().splitlines() if l.strip()][-1:]
        print(f"RESULT {name}: tests/{test}.py rc={p.returncode} {'KILLED' if p.returncode else 'SURVIVED'} | {tail}")
    finally:
        open(f,"w").write(src)
print("restored:", subprocess.run(["git","status","--porcelain"],capture_output=True,text=True).stdout or "clean")
