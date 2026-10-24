"""Reviewer's own hand mutants for #2465; each applied to a copy, block run, restored."""
import pathlib, shutil, subprocess, sys
root = pathlib.Path(sys.argv[1]); P = "custom_components/heatpump_optimizer/"
M = {
 "R1 floor ignores gate": (P+"thermal_model.py", "return (inlet if gate is None or inlet > gate else gate) + FLOW_MIN_LIFT_K", "return inlet + FLOW_MIN_LIFT_K"),
 "R2 every sample full": (P+"draw_range.py", "cmd is None or cmd[0] >= cmd[1] - CEILING_TOLERANCE_K", "True"),
 "R3 idle not excluded": (P+"draw_range.py", "above = 0.0 if idle is None else IDLE_MARGIN * idle", "above = 0.0"),
 "R4 legacy kept": (P+"draw_range.py", "legacy = command is not None and not self.commands_known", "legacy = False"),
 "R5 service rounds tenths": (P+"inputs.py", 'sent = _on_step(float(value), setpoint_step(hass, entity_id), "nearest")', "sent = round(float(value), 1)"),
 "R6 step attr ignored": (P+"inputs.py", "return step if step is not None and step > 0.0 else DEFAULT_SETPOINT_STEP", "return DEFAULT_SETPOINT_STEP"),
 "R7 lo rounds nearest": (P+"inputs.py", 'out = max(out, _on_step(temperature_from_c(lo_c, unit), step, "up"))', 'out = max(out, _on_step(temperature_from_c(lo_c, unit), step, "nearest"))'),
 "R8 hi rounds nearest": (P+"inputs.py", 'out = min(out, _on_step(temperature_from_c(hi_c, unit), step, "down"))', 'out = min(out, _on_step(temperature_from_c(hi_c, unit), step, "nearest"))'),
 "R9 quantise in degC": (P+"inputs.py", "out = _on_step(temperature_from_c(value_c, unit), step, rounding)", "out = _on_step(value_c, step, rounding); unit = None"),
 "R10 freq install commanded": (P+"pump_arbiter.py", "        or probe_install(inp.config).plan_writes_power()\n", ""),
 "R11 coord passes no command": (P+"coordinator.py", "command=pump_arbiter.flow_command(self))", "command=None)"),
 "R12 idle not stored": (P+"draw_range.py", '"idle": [round(v, 3) for v in self.idle],', '"idle": [],'),
 "R13 valve rounds nearest": (P+"coordinator.py", 'write_setpoint_c(hass, entity_id, target, rounding="down")', "write_setpoint_c(hass, entity_id, target)"),
 "R14 any command is idle": (P+"draw_range.py", "command.written_c <= command.gate_c + GATE_TOLERANCE_K", "True"),
 "R15 gate rounds up": (P+"pump_arbiter.py", 'return _bounded(inp, "space_setpoint", FLOW_GATE_C, FLOW_GATE_C, rounding="down")', 'return _bounded(inp, "space_setpoint", FLOW_GATE_C, FLOW_GATE_C, rounding="up")'),
 "R16 floor lo dropped": (P+"pump_arbiter.py", "            lo=min(floor_c, heat_c),\n", ""),
 "R17 disagree ignores full": (P+"draw_range.py", "((full and a > DISAGREE_FACTOR * d) or d > DISAGREE_FACTOR * a)", "(a > DISAGREE_FACTOR * d or d > DISAGREE_FACTOR * a)"),
 "R18 dhw gate nearest": (P+"pump_arbiter.py", '_bounded(inp, "dhw_setpoint", DHW_GATE_C, rounding="down")', '_bounded(inp, "dhw_setpoint", DHW_GATE_C)'),
 "R19 commands_known always True on load": (P+"draw_range.py", "out.commands_known = not rows or all(", "out.commands_known = True or all("),
}
only = sys.argv[2:] 
for name, (f, old, new) in M.items():
    if only and name.split()[0] not in only: continue
    p = root / f; src = p.read_text()
    assert src.count(old) == 1, (name, src.count(old))
    p.write_text(src.replace(old, new))
    try:
        r = subprocess.run([str(pathlib.Path(__file__).with_name("blk.sh")), str(root)], capture_output=True, text=True)
        out = r.stdout.strip().splitlines()
        fails = [l for l in out if "FAIL" in l or "✗" in l]
        print(f"{name}: {'RED' if 'PASSED' not in (out[-1] if out else '') else 'GREEN (survived)'} | {out[-1] if out else ''} | {fails[:2]}", flush=True)
    finally:
        p.write_text(src)
