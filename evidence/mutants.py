"""Reviewer's own hand mutants for PR #2465 (string replacements on a git-archive copy)."""
import sys, pathlib
P = "custom_components/heatpump_optimizer/"
M = {
 "M1": (P+"thermal_model.py", "return (inlet if gate is None or inlet > gate else gate) + FLOW_MIN_LIFT_K", "return inlet + FLOW_MIN_LIFT_K"),
 "M2": (P+"pump_arbiter.py", "modulation_floor_flow_c(_flow_inlet_c(inp), _gate_c(inp))", "modulation_floor_flow_c(_flow_inlet_c(inp))"),
 "M3": (P+"draw_range.py", "(d, a, cmd is None or cmd[0] >= cmd[1] - CEILING_TOLERANCE_K)", "(d, a, True)"),
 "M4": (P+"draw_range.py", "            if d > above\n", "            if True\n"),
 "M5": (P+"draw_range.py", "        draw.observe_idle(drawn_kw)", "        pass"),
 "M6": (P+"coordinator.py", "command=pump_arbiter.flow_command(self))", "command=None)"),
 "M7": (P+"pump_arbiter.py", "        or probe_install(inp.config).plan_writes_power()\n", ""),
 "M8": (P+"draw_range.py", "legacy = command is not None and not self.commands_known", "legacy = False"),
 "M9": (P+"inputs.py", "service[1]: int(sent) if sent.is_integer() else sent}", "service[1]: round(float(value), 1)}"),
 "M10": (P+"inputs.py", 'out = max(out, _on_step(temperature_from_c(lo_c, unit), step, "up"))', 'out = max(out, _on_step(temperature_from_c(lo_c, unit), step, "nearest"))'),
 "M11": (P+"inputs.py", 'out = min(out, _on_step(temperature_from_c(hi_c, unit), step, "down"))', 'out = min(out, _on_step(temperature_from_c(hi_c, unit), step, "nearest"))'),
 "M12": (P+"inputs.py", "    return step if step is not None and step > 0.0 else DEFAULT_SETPOINT_STEP", "    return DEFAULT_SETPOINT_STEP"),
 "M13": (P+"inputs.py", "    out = _on_step(temperature_from_c(value_c, unit), step, rounding)\n    if lo_c is not None:\n        out = max(out, _on_step(temperature_from_c(lo_c, unit), step, \"up\"))\n    if hi_c is not None:\n        out = min(out, _on_step(temperature_from_c(hi_c, unit), step, \"down\"))\n    converted = temperature_c(out, unit)\n    return out if converted is None else converted",
        "    out = _on_step(value_c, step, rounding)\n    if lo_c is not None:\n        out = max(out, _on_step(lo_c, step, \"up\"))\n    if hi_c is not None:\n        out = min(out, _on_step(hi_c, step, \"down\"))\n    return out"),
 "M14": (P+"draw_range.py", '            "samples": rows if self.commands_known else [r[:2] for r in rows],', '            "samples": [r[:2] for r in rows],'),
 "M15": (P+"pump_arbiter.py", "            lo=min(floor_c, heat_c),\n", ""),
}
k = sys.argv[1]; f, a, b = M[k]; p = pathlib.Path(f); s = p.read_text()
assert s.count(a) == 1, (k, s.count(a)); p.write_text(s.replace(a, b)); print(k, "applied", f)
