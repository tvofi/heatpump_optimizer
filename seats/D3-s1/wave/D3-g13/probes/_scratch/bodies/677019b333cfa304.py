OLD = "if value < centers[i + 1]:"
NEW = "if value <= centers[i + 1]:"
MUT = mutated(defrost, defrost._interp_position, OLD, NEW)
print(f"RESULT at_interior_centre baseline={defrost._interp_position(TC[2], TC)} mutant={MUT(TC[2], TC)}")
worst, pairs, tmoves = factor_delta(MUT)
print(f"RESULT interp_tuple_moves={tmoves} of {2 * len(probe_values())} count")
print(f"RESULT factor_max_abs_delta={worst} over {pairs} (t,h) pairs x 6 learners")
footer()
