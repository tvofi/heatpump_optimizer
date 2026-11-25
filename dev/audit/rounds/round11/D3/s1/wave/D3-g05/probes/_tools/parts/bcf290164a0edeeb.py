OLD, NEW = "if probe.stale:", "if False:"
MUT = mutant_method("_external_heat_override", OLD, NEW)
STALE = lambda: FakeState("400", unit="°C", last_updated=NOW - timedelta(minutes=120))
b, m = override(CLS._external_heat_override, STALE(), cycles=4), override(MUT, STALE(), cycles=4)
print(f"RESULT stale_probe_4_cycles baseline_value={b[0]} baseline_warnings={b[1]} mutant_value={m[0]} mutant_warnings={m[1]}")
fb, fm = override(CLS._external_heat_override, FakeState("400", unit="°C"), cycles=4), override(MUT, FakeState("400", unit="°C"), cycles=4)
print(f"RESULT null_fresh_probe baseline={fb} mutant={fm}")
print(f"RESULT stale_warnings_moved={int(b[1] != m[1])} count")
tail()
