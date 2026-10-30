import subprocess, sys, os, pathlib
H = "f41e5a5f4a674977970d63400b38cac3f6f321cf"
REPO = "/home/user/heatpump_optimizer"
C = "custom_components/heatpump_optimizer/coordinator.py"
P = "custom_components/heatpump_optimizer/pump_arbiter.py"
MUT = {
 "S1243": (P, "    if held.supply is None or held.supply[0] == step:\n        return\n    inp = wiring.inputs()", "    if False:\n        return\n    inp = wiring.inputs()"),
 "NULL": None,
 "R3": (C, "pump_arbiter.SupplyWiring(self.arbiter_inputs, boost.held_for(self), self._write_supply), on)",
        "pump_arbiter.SupplyWiring(self.arbiter_inputs, boost.held_for(self), lambda on: pump_arbiter.switch_supply(self.hass, getattr(self, \"_ctx\", self)._config.heat_pump_switch_entity, on)), on)"),
 "R1": (C, "early_cutoff.allow_on(early_cutoff.state_for(self), on), self._pump_signals)", "on, self._pump_signals)"),
 "R4": (P, "    if on or not ((signals.space_blocked and signals.dhw_blocked) or signals.mode.cooling):\n        return on", "    if True:\n        return on"),
}
name = sys.argv[1]
wt = f"/tmp/claude-0/rv/wt_{name}"
subprocess.run(["git", "-C", REPO, "worktree", "add", "-f", "--detach", wt, H], check=True, capture_output=True)
m = MUT[name]
if m:
    f, old, new = m
    p = pathlib.Path(wt, f); s = p.read_text()
    assert s.count(old) == 1, (name, s.count(old))
    p.write_text(s.replace(old, new))
script = sys.argv[2] if len(sys.argv)>2 else "tests/features.py"
r = subprocess.run([sys.executable, script], cwd=wt, env={**os.environ, "PYTHONPATH": "tests/hastub"}, capture_output=True, text=True)
out = r.stdout + r.stderr
pathlib.Path(f"/tmp/claude-0/rv/features_{name}_{os.path.basename(script)}.log").write_text(out)
fails = [l for l in out.splitlines() if "FAIL" in l]
summary = [l for l in out.splitlines() if "FEATURE CHECKS" in l]
pathlib.Path(f"/tmp/claude-0/rv/mutant_{name}_{os.path.basename(script)}.res").write_text(f"RESULT {name} rc={r.returncode} {summary}\n" + "\n".join(fails[:40]) + "\n")
subprocess.run(["git", "-C", REPO, "worktree", "remove", "--force", wt])
