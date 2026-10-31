import subprocess, sys, os, pathlib
REPO="/home/user/heatpump_optimizer"; HEAD="9fe3c4cf81465123f5dc6b360a30df7631f75974"
P="custom_components/heatpump_optimizer/"
M={
 "BASE": None,
 "Y1": (P+"pump_arbiter.py","i >= len(inp.plan.power_schedule or ())","i > len(inp.plan.power_schedule or ())"),
 "Y2": (P+"pump_arbiter.py","if not EntryConfig.from_mapping(inp.config).heat_pump_switch_entity:\n        return\n\n    async def _tick","if False:\n        return\n\n    async def _tick"),
 "M3": (P+"pump_arbiter.py","    if on != last:\n        await wiring.write(on)","    if True:\n        await wiring.write(on)"),
 "M4": (P+"coordinator.py","measured_power_kw=pump_arbiter.live_power_kw(self.hass, ctx._config),","measured_power_kw=self._measured_power,"),
 "R1": (P+"coordinator.py","early_cutoff.allow_on(early_cutoff.state_for(self), on), self._pump_signals)","on, self._pump_signals)"),
 "R3": (P+"coordinator.py","boost.held_for(self), self._write_supply)","boost.held_for(self), lambda on: pump_arbiter.switch_supply(self.hass, getattr(self, \"_ctx\", self)._config.heat_pump_switch_entity, on))"),
 "R2": (P+"thermal_model.py","dhw[i] if i < len(dhw) else 0.0)","0.0)"),
}
name=sys.argv[1]; wt=f"/home/user/mut/wt-{name}"
subprocess.run(["git","-C",REPO,"worktree","add","-q","--detach",wt,HEAD],check=True)
if M[name]:
    f,a,b=M[name]; p=pathlib.Path(wt,f); s=p.read_text(); assert s.count(a)==1,(name,s.count(a)); p.write_text(s.replace(a,b))
env=dict(os.environ,PYTHONPATH="tests/hastub")
r=subprocess.run([sys.executable,"tests/features.py"],cwd=wt,env=env,capture_output=True,text=True)
out=r.stdout+r.stderr
pathlib.Path(f"/home/user/mut/{name}.log").write_text(out)
fails=[l for l in out.splitlines() if "FAIL" in l]
summary=[l for l in out.splitlines() if "FEATURE CHECKS" in l]
pathlib.Path(f"/home/user/mut/{name}.res").write_text(f"RESULT {name} rc={r.returncode} {summary}\n"+"\n".join(fails[:20])+"\n")
subprocess.run(["git","-C",REPO,"worktree","remove","--force",wt])
