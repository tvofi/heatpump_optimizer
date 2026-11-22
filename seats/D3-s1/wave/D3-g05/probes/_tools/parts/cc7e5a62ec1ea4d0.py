OLD, NEW = "if not reading.ok or reading.text is None:", "if False:"
MUT = mutant_method("_external_heat_override", OLD, NEW)
# The line is reached only after read() classed the state not_numeric, i.e. a present, valued word.
cases = {
    "word_on": FakeState("on"), "word_off": FakeState("off"), "word_garbage": FakeState("burning?"),
    "empty_string": FakeState(""), "whitespace": FakeState("  "),
    "word_on_old_stamp": FakeState("on", last_updated=NOW - timedelta(days=14)),
    "word_on_future_stamp": FakeState("on", last_updated=NOW + timedelta(hours=2)),
    "numeric_with_bad_unit": FakeState("400", unit="K?"),
    "unavailable": FakeState("unavailable"), "not_configured": None,
}
moved = 0
for name, st in cases.items():
    try:
        b = override(CLS._external_heat_override, st)[0]
    except Exception as e:  # noqa: BLE001
        b = f"raised {type(e).__name__}"
    try:
        m = override(MUT, st)[0]
    except Exception as e:  # noqa: BLE001
        m = f"raised {type(e).__name__}"
    moved += int(b != m)
    print(f"RESULT {name} baseline={b} mutant={m}")
print(f"RESULT moved_inputs={moved} of {len(cases)} count")
tail()
