OLD, NEW = "if not trajectory:", "if False:"
MUT = mutant_method("_file_dhw_lead_predictions", OLD, NEW)
moved = 0
for name, traj in (("empty_list", []), ("none", None), ("one_step", [50.0]), ("solve_length_97", [50.0] * 97)):
    def run(fn):
        try:
            return counted(fn, traj, 0.25)
        except Exception as e:  # noqa: BLE001
            return f"raised {type(e).__name__}"
    b, m = run(CLS._file_dhw_lead_predictions), run(MUT)
    if traj is not None:  # None is not a value OptimizationResult carries (optimizer.py:3899: [] or tolist())
        moved += int(b != m)
    print(f"RESULT {name} baseline(leads,promise_calls,promises)={b} mutant={m}")
room_len, dhw_len = solved_lengths()
print(f"RESULT solved_trajectory_lengths room={room_len} dhw={dhw_len} count  (OptimizationResult.dhw_temp_trajectory is a list: [] or tolist())")
print(f"RESULT moved_reachable_inputs={moved} count")
tail()
