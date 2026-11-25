OLD = "run_power = min(min_run_power, p_dhw_max)"
NEW = "run_power = (min_run_power)"
MUT = mutated(dhw_planner, BASE_FN, OLD, NEW)
moved, total = sweep(MUT)
joint, per_slot = joint_cases()
print(f"RESULT production_shaped_moved={len(moved)} of {total} {moved[:3]}")
print(f"RESULT baseline_paths joint_shortcut={joint} per_slot={per_slot} count")
mv = tot = 0
for seed in range(12):
    for initial, ceiling, draw in ((50.0, 50.0, 1.8), (35.0, 55.0, 0.0), (45.0, 60.0, 3.0), (55.0, 55.0, 0.5)):
        for n, nw in ((24, 3), (96, 24), (48, 10)):
            plan, kw = fixture(n, nw, seed, initial, ceiling, draw)
            plan = np.where(plan > 0.55, 1.2, plan)
            tot += 1
            mv += not np.array_equal(run(plan, p_max=1.0, min_run=1.2, **kw), run(plan, MUT, p_max=1.0, min_run=1.2, **kw))
print(f"RESULT direct_min_run_above_pmax_moved={mv} of {tot}")
print(f"RESULT reach_caller_min_run_le_pmax={int('min_run_power = min(p_dhw_run, ' in SRC)} count")
footer()
