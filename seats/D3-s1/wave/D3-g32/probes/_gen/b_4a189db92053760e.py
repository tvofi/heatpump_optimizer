mut = mutate(SID, "_slab_outcome", "        if refusal is not None:", "        if False:")
moved = 0
for ua, c, g in GRID:
    if c <= 0:
        continue  # log of a negative capacity: the solver works in log space and cannot produce it
    b, m = outcome(SID._slab_outcome, ua, c, g), outcome(mut, ua, c, g)
    if b != m:
        moved += 1
        print(f"RESULT moved_ua{ua}_c{c}_g{g}: baseline={b} mutant={m}")
print(f"RESULT inputs_moved={moved}/{sum(1 for x in GRID if x[1] > 0)} count  (refused fit -> completed=True)")
print(f"RESULT null_in_band_delta={int(outcome(SID._slab_outcome, 0.2, 4.0, 0.4) != outcome(mut, 0.2, 4.0, 0.4))} count")
tail()
