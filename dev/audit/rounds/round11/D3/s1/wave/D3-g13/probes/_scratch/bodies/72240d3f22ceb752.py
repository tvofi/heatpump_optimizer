OLD = "unchanged: np.ndarray = np.clip(plan, 0.0, p_dhw_max)"
NEW = "unchanged: np.ndarray = (plan)"
MUT = mutated(dhw_planner, BASE_FN, OLD, NEW)
moved, total = sweep(MUT)
joint, per_slot = joint_cases()
print(f"RESULT production_shaped_moved={len(moved)} of {total} {moved[:3]}")
print(f"RESULT baseline_paths joint_shortcut={joint} per_slot={per_slot} count")
# no-weak plans (the branch the line sits in): in range, above p_max, negative, nan
cases = {"in_range": {3: 2.0, 7: 0.0}, "above_pmax": {3: 3.5}, "negative": {6: -0.5}, "nan": {4: float("nan")}}
mv = []
for nm, slots in cases.items():
    p = np.zeros(24)
    for i, v in slots.items():
        p[i] = v
    b, m = run(p), run(p, MUT)
    print(f"RESULT no_weak_{nm} baseline={b[list(slots)].tolist()} mutant={m[list(slots)].tolist()}")
    if not np.array_equal(b, m, equal_nan=True):
        mv.append(nm)
print(f"RESULT direct_no_weak_moved={len(mv)} of {len(cases)} ({','.join(mv)})")
# Reach: the only caller (dhw_planner.py:1257) feeds _plan_dhw_cheapest_first's result, and every return of that
# method is np.clip(plan, 0.0, p_dhw_max) with the same p_dhw_run (dhw_planner.py:2191-2195, 2307).
import ast  # noqa: E402
_tree = ast.parse(SRC)
_fn = next(n for n in ast.walk(_tree) if isinstance(n, ast.FunctionDef) and n.name == "_plan_dhw_cheapest_first")
rets = [ast.get_source_segment(SRC, r.value) for r in ast.walk(_fn) if isinstance(r, ast.Return)
        and not any(isinstance(p, (ast.FunctionDef, ast.Lambda)) and p is not _fn and r in ast.walk(p)
                    for p in ast.walk(_fn))]
print(f"RESULT reach_cheapest_first_returns={rets}")
footer()
