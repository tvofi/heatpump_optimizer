

def drive(n, count):
    c = coord()
    created = []
    with mock.patch.object(co, "SOLVE_FAILURE_ISSUE_COUNT", count), \
         mock.patch.object(co, "_create_issue", lambda *a, **k: created.append(c._solve_failures)):
        for _ in range(n):
            co._note_solve_failure(c, RuntimeError("probe"))
    return created


b, m = drive(8, 3), drive(8, 6)
print(f"RESULT issues_after_3_baseline={len(drive(3, 3))} count")
print(f"RESULT issues_after_3_mutant={len(drive(3, 6))} count")
print(f"RESULT first_issue_at_baseline={b[0] if b else None}")
print(f"RESULT first_issue_at_mutant={m[0] if m else None}")
print(f"RESULT null_delta={abs(len(drive(2, 3)) - len(drive(2, 6)))} count")
tail()
