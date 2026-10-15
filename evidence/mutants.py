import subprocess, sys, pathlib
I = "custom_components/heatpump_optimizer/inputs.py"
C = "custom_components/heatpump_optimizer/coordinator.py"
P = "custom_components/heatpump_optimizer/pump_arbiter.py"
M = [
 ("M1 setpoint_unit climate predicate off", I, 'if entity_id.split(".", 1)[0] == "climate":\n        return _instance_unit(hass)', 'if False:\n        return _instance_unit(hass)'),
 ("M2 write_setpoint_c writes value_c unconverted", I, "temperature_from_c(value_c, unit))", "value_c)"),
 ("M3 valve via raw write_setpoint", C, "if not await write_setpoint_c(self.hass, entity_id, target):", "if not await __import__('custom_components.heatpump_optimizer.inputs', fromlist=['x']).write_setpoint(self.hass, entity_id, target):"),
 ("M4 _RANGE_KEYS emptied", I, '_RANGE_KEYS = {"climate": ("min_temp", "max_temp")}', '_RANGE_KEYS = {}'),
 ("M5 setpoint_and_unit not-entity guard off", I, "    if not entity_id:\n        return None\n    state = hass.states.get(entity_id)\n    raw", "    if False:\n        return None\n    state = hass.states.get(entity_id)\n    raw"),
 ("R1 setpoint_range_c in state unit", I, "    unit = setpoint_unit(hass, entity_id, state)\n    return temperature_c(attrs.get(low_key)", "    unit = state_unit(state)\n    return temperature_c(attrs.get(low_key)"),
 ("R2 _bounded drops the high clamp", P, "value = min(value, high) if high is not None else value", "value = value"),
 ("R3 _bounded drops the low clamp", P, "value = max(value, floor, low if low is not None else floor)", "value = max(value, floor)"),
 ("R4 write_setpoint_c ignores the reading unit", I, "reading[1] if reading is not None\n        else", "None if reading is not None\n        else"),
 ("R5 arbiter _write raw write_setpoint", P, "await write_setpoint_c(coord.hass, entity, value)", "from .inputs import write_setpoint as _w; await _w(coord.hass, entity, value)"),
]
sel = sys.argv[1:] or [m[0].split()[0] for m in M]
for name, f, old, new in M:
    if name.split()[0] not in sel: continue
    p = pathlib.Path(f); src = p.read_text()
    assert src.count(old) == 1, (name, src.count(old))
    p.write_text(src.replace(old, new))
    try:
        r = subprocess.run([sys.executable, "tools/audit/seat/features_block.py", "°F set-points: one unit rule"], capture_output=True, text=True)
        out = r.stdout + r.stderr
        fails = [l.strip() for l in out.splitlines() if l.strip().startswith(("FAIL", "!!", "x ")) or "FAIL" in l[:8]]
        summ = [l for l in out.splitlines() if "FEATURES BLOCK" in l]
        print(f"RESULT {name}: rc={r.returncode} {summ[-1] if summ else out[-300:]}")
        for l in fails: print("    ", l[:200])
    finally:
        subprocess.run(["git", "checkout", "--", f])
print("clean:", subprocess.run(["git","status","--porcelain","--untracked-files=no"],capture_output=True,text=True).stdout or "yes")
