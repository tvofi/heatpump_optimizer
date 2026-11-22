OLD = "weak = np.where((plan > 1e-6) & (plan < min_run_power))[0]"
NEW = "weak = np.where((plan > 1e-6) & (plan <= min_run_power))[0]"
MUT = mutated(dhw_planner, BASE_FN, OLD, NEW)
moved, total = sweep(MUT)
joint, per_slot = joint_cases()
print(f"RESULT production_shaped_moved={len(moved)} of {total} {moved[:3]}")
print(f"RESULT baseline_paths joint_shortcut={joint} per_slot={per_slot} count")
# A slot exactly at min_run_power (raised to the same value: no change), alone and beside a real weak slot.
p = np.zeros(24); p[5] = MIN_RUN; p[10] = 0.2
tie = 0
for kw in (dict(initial=35.0, ceiling=55.0), dict(initial=50.0, ceiling=50.0)):
    tie += not np.array_equal(run(p, **kw), run(p, MUT, **kw))
print(f"RESULT tie_at_min_run_moved={tie} of 2")
# Direct only: min_run_power above p_dhw_max (strong slots exactly at min_run=1.2, p_max=1.0) -- the caller forbids it.
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
