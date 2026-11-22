OLD = "weak = np.where((plan > 1e-6) & (plan < min_run_power))[0]"
NEW = "weak = np.where((plan >= 1e-6) & (plan < min_run_power))[0]"
MUT = mutated(dhw_planner, BASE_FN, OLD, NEW)
moved, total = sweep(MUT)
joint, per_slot = joint_cases()
print(f"RESULT production_shaped_moved={len(moved)} of {total} {moved[:3]}")
print(f"RESULT baseline_paths joint_shortcut={joint} per_slot={per_slot} count")
res = {}
for nm, kw in (("tank_room", dict(initial=35.0, ceiling=55.0)), ("tank_full", dict(initial=50.0, ceiling=50.0))):
    for v in (1e-6, np.nextafter(1e-6, 0.0), np.nextafter(1e-6, 1.0)):
        p = np.zeros(24); p[5] = v
        res[(nm, float(v))] = (float(run(p, **kw)[5]), float(run(p, MUT, **kw)[5]))
for (nm, v), (b, m) in res.items():
    print(f"RESULT slot_at_{v!r}_{nm} baseline={b!r} mutant={m!r}")
b, m = res[("tank_room", 1e-6)]
print(f"RESULT slot_kw_at_1e-6_baseline={b!r}")
print(f"RESULT slot_kw_at_1e-6_mutant={m!r}")
print(f"RESULT boundary_inputs_moved={sum(b != m for b, m in res.values())} of {len(res)}")
footer()
