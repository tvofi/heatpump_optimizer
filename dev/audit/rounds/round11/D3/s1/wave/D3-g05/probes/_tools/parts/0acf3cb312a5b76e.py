OLD, NEW = "if state is None:", "if False:"
MUT = mutant_method("_entity_state", OLD, NEW)
c = coord({"sensor.present": FakeState("on", attributes={"a": 1}), "sensor.bare": SimpleNamespace(state="x")})
inputs = ["sensor.absent", "sensor.present", "sensor.bare", "", None]
moved = 0
for eid in inputs:
    b = CLS._entity_state(c, eid)
    try:
        m = MUT(c, eid)
    except Exception as e:  # noqa: BLE001
        m = f"raised {type(e).__name__}"
    moved += int(b != m)
    print(f"RESULT entity_state[{eid!r}] baseline={b} mutant={m}")
print(f"RESULT moved_inputs={moved} count")
tail()
