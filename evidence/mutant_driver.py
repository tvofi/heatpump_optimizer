import os, shutil, subprocess, sys, tempfile
SRC = "/home/user/rev"
PA = "custom_components/heatpump_optimizer/pump_arbiter.py"
CO = "custom_components/heatpump_optimizer/coordinator.py"
ST = "custom_components/heatpump_optimizer/store.py"
M = {
 "M1": (CO, "        pump_arbiter.note_supply(pump_arbiter.state_for(self), pump_arbiter.SupplyWiring(self.arbiter_inputs, boost.held_for(self), self._write_supply), on)\n", ""),
 "M2": (PA, "        await wiring.write(on)\n", "        pass\n"),
 "M3": (PA, "    if on != last:\n", "    if True:\n"),
 "M4": (CO, "measured_power_kw=pump_arbiter.live_power_kw(self.hass, ctx._config),", "measured_power_kw=self._measured_power,"),
 "M5": (ST, '        "written/silent/0": _FLAG,\n', ""),
 "M6": (PA, "    held.supply_unsub = async_track_time_interval(inp.hass, _tick, _TICK)\n", "    held.supply_unsub = (lambda: None)\n"),
 "X1-boost": (PA, "        return True\n    i = _step_index(inp.plan, now)", "        pass\n    i = _step_index(inp.plan, now)"),
 "X2-sysid": (PA, '    if (inp.action or {}).get("mode") == "system_identification":\n        return None\n    if boosts.active', "    if boosts.active"),
 "X3-stale": (PA, "    if inp.mode not in (MODE_AUTO, MODE_ECONOMY) or inp.plan_stale or inp.plan is None:", "    if inp.plan is None:"),
 "X4-released": (PA, "    if inp.entry_released:\n        return\n    on = step_supply", "    on = step_supply"),
 "X5-release": (PA, "    release_supply(held)\n", ""),
 "X6-gate": (PA, "    await supply_tick(held, wiring)\n", "    pass\n") ,
 "X7-cutoffhold": (CO, "            early_cutoff.allow_on(early_cutoff.state_for(self), on), self._pump_signals)", "            on, self._pump_signals)"),
 "X8-skipoff": (PA, "    if on or not ((signals.space_blocked and signals.dhw_blocked) or signals.mode.cooling):", "    if True:"),
 "X9-range": (PA, "    return None if i is None or i >= len(inp.plan.power_schedule or ()) else plan_step_runs(inp.plan, i)", "    return None if i is None else plan_step_runs(inp.plan, i)"),
}
M["NULL"] = (PA, "def supply_write(", "def supply_write(")
script = sys.argv[1]; which = sys.argv[2:] or list(M)
py = "/opt/hpo/venv-ci/bin/python"
for name in which:
    f, old, new = M[name]
    d = tempfile.mkdtemp(); os.rmdir(d)
    subprocess.run(["git", "-C", SRC, "worktree", "add", "-q", "--detach", d, "HEAD"], check=True)
    p = os.path.join(d, f); s = open(p).read()
    assert s.count(old) == 1, (name, s.count(old))
    open(p, "w").write(s.replace(old, new))
    env = dict(os.environ, PYTHONPATH="tests/hastub:tests:custom_components")
    r = subprocess.run([py] + script.split(), cwd=d, env=env, capture_output=True, text=True, timeout=2400)
    out = r.stdout + r.stderr
    fails = [l for l in out.splitlines() if l.startswith("  FAIL") or "CHECKS FAILED" in l or "CHECKS PASSED" in l or l.startswith("AGREE")]
    print(f"== {name} rc={r.returncode}"); print("\n".join(fails[-8:]) or out[-800:]); sys.stdout.flush()
    subprocess.run(["git", "-C", SRC, "worktree", "remove", "--force", d], check=True)
