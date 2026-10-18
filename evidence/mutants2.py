import subprocess, os
S="/Users/timmalmstrom/hpo-seats/r10s3/review-n-log-flood"; W=S+"/wt"
PY="/Users/timmalmstrom/heatpump_optimizer/tools/audit/seat/shims/seat-python"
C="custom_components/heatpump_optimizer/"
M=[("survivor_valve_GUARD_OFF", C+"coordinator.py",
    '        if log_held(self, "valve_write", why is not None, "Valve write entity %s %s", entity_id, why):',
    '        if False:', ["tests/features.py","dev/audit/rounds/round10/D14/log_flood/probe.py"]),
   ("survivor_space_CMP_BOUND", C+"pump_arbiter.py",
    '    misdeclared = room is not None and low is not None and low > room + SETPOINT_TOLERANCE',
    '    misdeclared = room is not None and low is not None and low >= room + SETPOINT_TOLERANCE', ["tests/features.py","dev/audit/rounds/round10/D14/log_flood/probe.py"]),
   ("own_flowunit_clear_DEL", C+"pump_arbiter.py",
    '        log_held(inp.hass, f"space_target_flow_declared:{entity}", False)',
    '        pass', ["tests/features.py","dev/audit/rounds/round10/D14/log_flood/probe.py"]),
   ("own_future_stamp_noclear", C+"inputs.py",
    '            self.enabled and limit is not None and future,',
    '            True if self.hass in __import__("custom_components.heatpump_optimizer.log_latch", fromlist=["x"])._HELD_CONDITIONS and any(k.startswith(f"future_stamp:{reading.key}:") for k in __import__("custom_components.heatpump_optimizer.log_latch", fromlist=["x"])._HELD_CONDITIONS[self.hass]) and False else (self.enabled and limit is not None and future) or None,', []),
   ("own_forget_held_DEL", C+"coordinator.py",
    '        forget_held(self.hass)  # the reader\'s and arbiter\'s latches re-warn after a reload',
    '        pass', ["tests/features.py","dev/audit/rounds/round10/D14/log_flood/probe.py"]),
]
env=dict(os.environ, PYTHONPATH="tests/hastub")
for name,f,old,new,scripts in M:
    if not scripts: continue
    p=W+"/"+f; orig=open(p).read(); lines=orig.split("\n")
    idx=[i for i,l in enumerate(lines) if l==old]; assert len(idx)==1,(name,idx)
    lines[idx[0]]=new; open(p,"w").write("\n".join(lines))
    try:
        for sc in scripts:
            r=subprocess.run([PY,sc],cwd=W,env=env,capture_output=True,text=True)
            out=r.stdout+r.stderr; tag=sc.split("/")[-1]
            open(f"{S}/evidence/r2.{name}.{tag}.txt","w").write(out)
            fails=[l.strip()[:160] for l in out.splitlines() if l.lstrip().startswith("FAIL") or "PROBE FAILED" in l or ("recur=0" in l) or ("floods=" in l and "floods=0" not in l)][:3]
            print(f"RESULT {name} {tag} rc={r.returncode} killed={r.returncode!=0}", fails, flush=True)
    finally:
        open(p,"w").write(orig)
print("restored:", subprocess.run(["git","-C",W,"status","--porcelain"],capture_output=True,text=True).stdout or "clean")
