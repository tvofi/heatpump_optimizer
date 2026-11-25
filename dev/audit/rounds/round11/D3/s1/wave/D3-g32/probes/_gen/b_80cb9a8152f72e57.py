mut = mutate(SID, "_slab_outcome", "        gains_kw = float(np.clip(gains_kw, 0.0, 2.0))", "        gains_kw = float((gains_kw))")
moved = 0
for g in (-0.5, -0.3, -0.1, -1e-6, 0.0, 0.4, 1.99, 2.0):
    b, m = outcome(SID._slab_outcome, 0.2, 4.0, g), outcome(mut, 0.2, 4.0, g)
    moved += b != m
    print(f"RESULT gains_fit{g}: baseline={b} mutant={m}")
print(f"RESULT inputs_moved={moved}/8 count  (fitted gains in [-0.5, 0): published internal_gains_kw)")
tail()
