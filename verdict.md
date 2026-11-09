Fix review: merge 6517b1f443af372887dbadd49919a2ab605b66fe

bus-nonce: cec948f62af12e30cdd3c5c1a8f02655

## Evidence
- Head measured: 6517b1f443af372887dbadd49919a2ab605b66fe (ev/HEAD.txt); merge base 51cd5ec8a42abde3c223f22e9f4a0d5f35f8844a. This is the first round I have seen of this PR, not a count of the fixer's rounds.
- CI: `merge_train.py classify` exits 0 (GREEN, pending none, red none) at this head. The packet's gate digest is green, and the body's earlier reds (arch-score, arch-instrument, mutation, codeql cancel, gate deferral) are each named and answered in `## Red checks`.
- Merge: `git merge-tree --write-tree origin/main <head>` exits 0 with no conflict. Roles dir moved on main (proposal-triage.md only), not fix-review.
- Mutation proof re-run by me at the head (ev/mutants.txt): baseline `tests/wood_advisor.py` passes 25 checks. M2 (`_plan_partload` guard forced), M3 (`_derated` drops the factor) and M6 (hot-water draw dropped) each fail 3 wood_advisor checks. M1 (`partload_at=partload_factor` deleted in coordinator.py) fails the features wood block (1 of 31). No vacuous mutant. The tree was restored after each.
- Harness `r10_partload_residue.py refill` (the finder's `r10_partload_pricing` solves, the PR's own wood arm, disclosed as the fixer's) run at the head and at the merge base (ev/refill_head.txt, ev/refill_base.txt): the production advisor against the derated arm reads count residual 0 and night picks off 0 on all four rows at the head. At the base it reads 19/67 (spread) and 58/560 (flat), the body's figures. At d=0 every wood figure is 0 at both ends. `null rows not zero 0`, `positive (d>0) price days with a zero maximum 0`, `failures 0`, rc=0 at both. The wood price-error, shortfall and picks-changed figures are digit-identical to the body.
- Class: the only production callers of `build_wood_fuel_view` and `_attach_night_advice` are in `wood_fuel.py` (via `wood_fuel_from_parts`), and the only caller of `wood_fuel_from_parts` is coordinator.py:8304, which passes `partload_at`. No seam is left undiffed.
- Metrics: `score.py --diff <base> <head>` prints `dS +0.0000 NULL`. The two ledger pins are for the two new sites. The budget moves are only -1 on `class_excess_loc` and `max_class_loc`, from the joined `int()` line, which is real (no raise).
- VERSION, manifest, RELEASE_NOTES and tests/golden are untouched (three-dot diff stat empty).
- Carry audit at the head, from the packet: 5 routed, 0 unrouted. The forward-carry to R10-SAV-COMFORT is named with its control (zero-derate null) and figures.
- Not re-derived: the Pi-class factor 6.8x (Geekbench ratio, cited externally), the carry 1 and 3 CPU timings (I did not re-run `relaxed` or `buffer`; the body's refusals hold under any factor below 306x and are not what this fix changes), and the roster-branch carry text (not opened from `handoff/audit-r10-roster`).
