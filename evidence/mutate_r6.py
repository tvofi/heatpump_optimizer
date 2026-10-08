import sys, pathlib
W = pathlib.Path("/Users/timmalmstrom/hpo-seats/review-2025-r6/wt/custom_components/heatpump_optimizer")
C, EC, SM = W / "coordinator.py", W / "entry_config.py", W / "silent_mode.py"
M = {
 "M1_5051_GUARD_OFF": (C, 5051, "if not ctx._config.lower_floor_temp_entity:", "if False:"),
 "M2_5462_BOOLOP": (C, 5462, "self._vent_cusum.tripped and ctx", "self._vent_cusum.tripped or ctx"),
 "M3_6840_GUARD_OFF": (C, 6840, "if ctx._config.precip_type_enabled and np.any(snow_array > 0.0):", "if False:"),
 "M4_6840_BOOLOP": (C, 6840, "precip_type_enabled and np.any", "precip_type_enabled or np.any"),
 "M5_8901_GUARD_OFF": (C, 8901, "if not ctx._config.capacity_curve_enabled:", "if False:"),
 "M6_8934_GUARD_OFF": (C, 8934, "if not ctx._config.capacity_curve_enabled:", "if False:"),
 "M7_10776_GUARD_OFF": (C, 10776, 'if not getattr(self, "_ctx", self)._config.comfort_learning_enabled:', "if False:"),
 "M8_ec256_GUARD_OFF": (EC, 256, "if isinstance(merged, EntryConfig):", "if False:"),
 "M9_sm104_GUARD_OFF": (SM, 104, "if fraction is None:", "if False:"),
 "M10_ec_empty_guard_restored": None,
}
k = sys.argv[1]
if k == "M10_ec_empty_guard_restored":
    s = EC.read_text()
    a = "    result = _refused_number(value, math.nan)\n    return default if result is None else result\n"
    assert s.count(a) == 1
    EC.write_text(s.replace(a, '    if value == "":\n        return 7.0\n' + a))
    sys.exit(0)
p, n, a, b = M[k]
lines = p.read_text().split("\n")
assert a in lines[n - 1], (k, lines[n - 1])
lines[n - 1] = lines[n - 1].replace(a, b, 1)
p.write_text("\n".join(lines))
print(k, "->", lines[n - 1].strip())
