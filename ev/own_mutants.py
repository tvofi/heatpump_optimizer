import subprocess, sys, os
W="/tmp/rv-mut"; A="custom_components/heatpump_optimizer/pump_arbiter.py"; T="custom_components/heatpump_optimizer/thermal_model.py"
MUT=[("R0-null",A,"",""),
 ("R1-le-to-lt",A,"if cycle is None or cycle <= everyday:","if cycle is None or cycle < everyday:"),
 ("R2-hardmax-ignores-cycle",T,"return min(70.0, self.dhw_setpoint if top is None else top)","return min(70.0, self.dhw_setpoint)"),
 ("R3-booked-space-row-cycle",A,'return PumpCommand(both, _bounded(inp, "dhw_setpoint", DHW_GATE_C, rounding="down"), space, silent)','return PumpCommand(both, dhw, space, silent)'),
 ("R4-cycle-uses-disinfection-not-cycle",A,"cycle = inp.params.dhw_cycle_temp if","cycle = inp.params.dhw_disinfection_temp if"),
 ("R5-round-down",A,'float(cycle), rounding="up")','float(cycle), rounding="down")'),
]
env=dict(os.environ, PYTHONPATH="tests/hastub")
for n,f,o,new in MUT:
    p=os.path.join(W,f); s=open(p).read()
    if o: assert s.count(o)==1,(n,s.count(o)); open(p,"w").write(s.replace(o,new))
    try:
        out=[]
        for t in ["tests/block_duty.py"]+(["tests/features.py","tests/rolling.py"] if f==T or n=="R0-null" else []):
            r=subprocess.run([sys.executable,t],cwd=W,env=env,capture_output=True,text=True)
            fails=[l.strip() for l in (r.stdout+r.stderr).splitlines() if "FAIL" in l][:3]
            out.append(f"{t} rc={r.returncode} {fails}")
        print(n, "|", " ; ".join(out), flush=True)
    finally:
        open(p,"w").write(s)
