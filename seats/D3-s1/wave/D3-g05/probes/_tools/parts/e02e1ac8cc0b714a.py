OLD, NEW = "if not trajectory:", "if False:"  # unique in _file_lead_predictions (line 10223)
MUT = mutant_method("_file_lead_predictions", OLD, NEW)
moved_kept = 0
for name, traj in (("empty_room", []), ("one_point", [21.0]), ("solved_97", [21.0] * 97)):
    b = counted(CLS._file_lead_predictions, traj, None, room=True)
    m = counted(MUT, traj, None, room=True)
    moved_kept += int(b[0] != m[0] or b[2] != m[2])
    print(f"RESULT {name} baseline(leads,promise_calls,promises_kept)={b} mutant={m}")
print(f"RESULT moved_kept_records={moved_kept} count  (note_promise calls may differ; kept promises and leads are the output)")
tail()
