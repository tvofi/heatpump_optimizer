OLD = "if value <= centers[0]:"
NEW = "if value < centers[0]:"
MUT = mutated(defrost, defrost._interp_position, OLD, NEW)
print(f"RESULT at_first_centre baseline={defrost._interp_position(TC[0], TC)} mutant={MUT(TC[0], TC)}")
worst, pairs, tmoves = factor_delta(MUT)
print(f"RESULT interp_tuple_moves={tmoves} of {2 * len(probe_values())} count")
print(f"RESULT factor_max_abs_delta={worst} over {pairs} (t,h) pairs x 6 learners")
footer()
