OLD, NEW = "return probe.value > 30.0", "return probe.value >= 30.0"
MUT = mutant_method("_external_heat_override", OLD, NEW)
moved = 0
for v in ("29.9", "30.0", "30.1", "400"):
    b, m = override(CLS._external_heat_override, FakeState(v, unit="°C"))[0], override(MUT, FakeState(v, unit="°C"))[0]
    moved += int(b != m)
    print(f"RESULT flue_{v}C baseline={b} mutant={m}")
print(f"RESULT moved_inputs={moved} count  (null: 29.9, 30.1 and 400 must not move)")
tail()
