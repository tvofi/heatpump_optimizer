OLD = "if bool(np.all(joint_temps <= joint_limit + 1e-9)):"
NEW = "if bool(np.all(joint_temps < joint_limit + 1e-9)):"
MUT = mutated(dhw_planner, BASE_FN, OLD, NEW)
moved, total = sweep(MUT)
joint, per_slot = joint_cases()
print(f"RESULT production_shaped_moved={len(moved)} of {total} {moved[:3]}")
print(f"RESULT baseline_paths joint_shortcut={joint} per_slot={per_slot} count")
# Bound: the mutant only skips the shortcut on an exact float tie; skipping it ALWAYS (mutant 111763243ac44278's edit)
# moves no plan, so skipping it on a tie cannot either.
OFF = mutated(dhw_planner, BASE_FN, OLD, "if False:")
moved_off, _ = sweep(OFF)
print(f"RESULT shortcut_always_off_moved={len(moved_off)} of {total}")
footer()
