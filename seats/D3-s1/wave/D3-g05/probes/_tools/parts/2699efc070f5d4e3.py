OLD, NEW = 'if probe.problem != "not_numeric":', "if False:"
MUT = mutant_method("_external_heat_override", OLD, NEW)
cases = {
    "not_configured": None,
    "unavailable": FakeState("unavailable"),
    "unknown": FakeState("unknown"),
    "implausible_minus127C": FakeState("-127", unit="°C"),   # DS18B20 lost-bus code, outside FLUE_RANGE_C
    "implausible_1500C": FakeState("1500", unit="°C"),
    "word_on": FakeState("on"),                              # null: not_numeric, both arms read the flag
    "fresh_20C": FakeState("20", unit="°C"),                 # null: numeric, returns before the line
}
moved = 0
for name, st in cases.items():
    b, m = override(CLS._external_heat_override, st)[0], override(MUT, st)[0]
    moved += int(b != m)
    print(f"RESULT {name} baseline={b} mutant={m}")
# missing entity: configured, absent from the state machine
c = coord({}, external_heat_entity=ENT)
r = lambda: InputReader(c.hass, c._config, enabled=True, scale=1.0, now=lambda: NOW)
b, m = CLS._external_heat_override(c, r()), MUT(c, r())
moved += int(b != m)
print(f"RESULT missing_entity baseline={b} mutant={m}")
print(f"RESULT moved_inputs={moved} count")
tail()
