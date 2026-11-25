from custom_components.heatpump_optimizer import defrost  # noqa: E402

OLD = "if self.duty_counts[t][h] > 0:"
NEW = "if self.duty_counts[t][h] >= 0:"
MUT = mutated(defrost, defrost.DefrostDerate.summary, OLD, NEW)


def rows_with_duty(learner, fn=None):
    rows = (fn or defrost.DefrostDerate.summary)(learner)
    return sum(1 for r in rows if "duty" in r), len(rows), rows


# Case: one INFERRED observation (no defrost flag: the pre-v5.3.0 estimator), zero measured duty samples.
d = defrost.DefrostDerate()
d.observe(3.0, 85.0, 0.8)
b_duty, b_rows, b = rows_with_duty(d)
m_duty, m_rows, m = rows_with_duty(d, MUT)
print(f"RESULT rows_total_baseline={b_rows} count")
print(f"RESULT rows_with_duty_baseline={b_duty} count")
print(f"RESULT rows_with_duty_mutant={m_duty} count")
print(f"RESULT mutant_row_fields={sorted(set(m[0]) - set(b[0]))}")
print(f"RESULT mutant_row_duty={m[0].get('duty')} events={m[0].get('events')} duty_samples={m[0].get('duty_samples')}")
# Null control: a bucket with a counted duty reports its duty in both arms.
n = defrost.DefrostDerate()
n.observe_duty(3.0, 85.0, 0.1, events=1)
nb, _, _ = rows_with_duty(n)
nm, _, _ = rows_with_duty(n, MUT)
print(f"RESULT null_delta_rows={nm - nb} count")
# Empty learner: no rows in either arm (source None skips the row before line 642).
e = defrost.DefrostDerate()
print(f"RESULT empty_rows_baseline={len(e.summary())} mutant={len(MUT(e))} count")
footer()
