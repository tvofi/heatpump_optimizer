mut = mutate(SID, "_size_step_power", "                while hi - lo > 0.01:", "                while hi - lo >= 0.01:")
# the tie: hi - lo reaches exactly 0.01 only when q_max = 0.01 * 2**k (exact halving), cop a power of two
tie_args = [(0.01 * 2 ** k / c, float(c), 21.0, o) for k in range(6, 12) for c in (1, 2, 4) for o in (2.0, -5.0, 8.0)]
moved_tie, n_tie = scan(mut, args=tie_args)
bis = sum(1 for h in HOUSES.values() for a in tie_args if call(SID._size_step_power, *a, h) not in (None, a[0]))
print(f"RESULT tie_inputs_that_bisect={bis}/{n_tie} count  (returned neither the full power nor None)")
print(f"RESULT tie_inputs_moved={moved_tie}/{n_tie} count")
gen_args = [(p, c, b, o) for p in (1.5, 3.0, 4.5, 6.0, 9.0) for c in (2.0, 3.0, 3.7) for b in (20.0, 21.0) for o in (-5.0, 2.0, 8.0)]
moved_gen, n_gen = scan(mut, args=gen_args)
print(f"RESULT generic_inputs_moved={moved_gen}/{n_gen} count")
tail()
