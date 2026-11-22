from custom_components.heatpump_optimizer import defrost  # noqa: E402

OLD = "duty = min(max(float(duty), 0.0), DEFROST_DUTY_MAX)"
NEW = "duty = min((float(duty)), DEFROST_DUTY_MAX)"
MUT = mutated(defrost, defrost.derate_from_duty, OLD, NEW)
inputs = [-1e9, -1.0, -0.3, -1e-12, -0.0, 0.0, 1e-12, 0.1, 0.3, 0.31, 1.0, 5.0,
          float("inf"), float("-inf"), float("nan")]
moved = []
for v in inputs:
    b, m = defrost.derate_from_duty(v), MUT(v)
    print(f"RESULT derate({v!r}) baseline={b!r} mutant={m!r}")
    if not (b == m or (b != b and m != m)) or str(b) != str(m):
        moved.append(repr(v))
print(f"RESULT inputs_moved={len(moved)} of {len(inputs)} ({','.join(moved)})")
print(f"RESULT DERATE_MAX={defrost.DERATE_MAX}")
# Positive control on the harness: if DERATE_MAX were above 1 the dropped floor would show (the M4 condition).
with mock.patch.object(defrost, "DERATE_MAX", 1.05):
    b = defrost.derate_from_duty(-0.3)
    m = mutated(defrost, defrost.derate_from_duty, OLD, NEW)(-0.3)
print(f"RESULT posctl_derate_max_1_05 baseline={b} mutant={m}")
footer()
