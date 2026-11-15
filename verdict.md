Design review: approve a63a2ca6cde761f9647573b5cfeab2b02f37655a

Round 3, the amendment only: `git diff 0c692c86d2 a63a2ca6` (one file, `design.md`), judged against the build d73ec97da13b4df42e7b7eef36731707b963fce7 and the blocked fix verdict 04e5bcfca3dd0b44e682185df4ccaaa7cc98b428. Ruled: departures 1 and 3, nothing else. The approved note outside the delta was not re-read. Ruling c1 is not decided here.

## Rulings

- **Departure 1, the second unpriced descent in `_relaxed_plans`: adopt, as built.** `custom_components/heatpump_optimizer/optimizer.py:248` at d73ec97da1 guards it on `cycling_cost > 0` and `_priced_stops` not none, and `_commit_runs` (`optimizer.py:699`) takes the minimum over the relaxed plans, so one more plan cannot raise a stage call's score. The approved shape's test 5 premise is false by measurement (first row below); neither single-descent shape is better.
- **Departure 3, `runs.commit` is not the identity on a realizable input: adopt, with test 3's clause as the amendment replaces it.** `runs.py:147` pays each on step its price and `_advance` each edge the start price, so identity holds only where nothing can be bought; `optimizer.py:696` returns the same array only where no start has a price and the projection returns the plan, which is the narrowed invariant the note now states. An identity guard in the leaf would withhold from the true objective every changed plan measured below, all of which score strictly lower.

Seam (step 1): both departures stay inside `optimizer.py`'s candidate stage and `runs.py`; no new write path, no second owner. Shape (step 2): the second descent is no finding's behaviour and the note says why it moves (test 5's premise). Hot files (step 5): `optimizer.py` and `runs.py` are unchanged between the build's merge base d7004eaa775d and `origin/main` a72ae19952; the delta adds no file to the approved note's set, so sibling designs were not re-read. Cost (step 6): no build change is asked for.

## Measurement, re-run by this seat

One box (x86_64, 4 cores), detached worktree at d73ec97da1, `PYTHONPATH=tests/hastub:custom_components:tests`, the four jobs sharing the cores (so no timing is reported).

- `dev/audit/harnesses/r11_honest_starts_runs.py descents`: output byte-identical to `ev/harness_descents_head.txt` (16 lines), exit 0, null cells that moved or descended twice 0. Tabulated from it, published objective over the 12 cells, above / equal / below and sums: operand alone against unpriced alone 5 / 2 / 5, 574.59 against 577.19; both against operand alone 1 / 6 / 5, 574.19 against 574.59; both against unpriced alone 0 / 8 / 4. Equal to the note's table.
- Per stage call (my own spy on `_commit_runs`, re-running it with the first relaxed plan alone and scoring both results in their shipped scopes, in no tree): 20 calls with two plans on the 12 cells, below 6, equal 14, above 0. The spy left all 12 published objectives equal to the harness's. The cell above the operand alone (modulating clamped, phase 30, -4 degC, 38.1123 against 38.0075) made 2 calls, 1 below and 1 equal. Equal to the note. The note's 64 calls on the reviewer's 140 cells were not re-run.
- `ev/reviewer_leaf_props.py 1`: identity fails on 2180 of 3000, the only failing property; seed 0 gives 2215. Equal to the note.
- `ev/reviewer_solve_props.py 1 140`: the 140 cell lines and the RESULT lines are byte-identical to `ev/solve_props_head.txt`; 149 engaged stage calls, 13 `realizable_changed`.
- Realizable first relaxed plans (the same script with one added print: the plan clipped to the shipped scope's box, scored in the shipped scope): 18 of 149; 13 ship changed, each strictly below (gains 0.000001 to 15.4278), edges falling in 5, level in 7, rising in 1; 5 unchanged, all with a start priced; of the 13, 11 price a start and 2 do not, those 2 lying 1.374 and 0.600 kW outside the stage box. Equal to the note.
- Leaf arms (my own script on the reviewer's generator, seed 0, band 2, lengths (1, 1), cap p_max), masks differing from the input's own of 3000: as generated 2223; start price zero 1848; flat price and start price zero 1425; price zero and start price zero 0; that arm with `_TIE_BREAK` 0, 2035. Equal to the note. The control moves under its perturbation, so the replaced clause of test 3 can fail.

Stated by the note, not verified here: the CPU figure 25.0 against 22.6 seconds (my runs were contended), the 64-call reading, `env_drift.py --all`, `tests/stress.py`, the mutants, and the c1 table.

## Notes for the fixer (carried, no revise point)

- Two of the 11 priced changed plans (gains 15.3964 and 15.4278) had the relaxed plan 3.062 and 2.359 kW outside the shipped scope's box, so their gain is measured against a clipped plan; the note attributes clipping only to the 2 unpriced ones. Print the clip distance beside the gain when note a2 lands the reading in the harness. Carry: R11-OUTSIDE-HONEST-STARTS-RUNS (item r1)
- Test 5's "no higher than the first alone" holds by construction of the minimum; what can fail is "strictly lower in at least one call" and the named cell. Name the cell in the test: duty-cycle, phase 30, 2 degC ships 26.1997 with both and 26.2715 with the second descent removed. Carry: R11-OUTSIDE-HONEST-STARTS-RUNS (item r2)
- The second descent's cost is one run on one box in the note; measure it with `tests/stress.py` against `tests/stress_budgets.json` at the merge base and at the head that opens the pull request, on a priced-switch config, and state both in the body (D9, Raspberry-Pi-class). Carry: R11-OUTSIDE-HONEST-STARTS-RUNS (item r3)
- Why the one cell ends dearer across two space solves is not established (note a1); it stays stated in the body with both figures and is not chased in this pull request. Carry: R11-OUTSIDE-HONEST-STARTS-RUNS (item a1)

## Routed

- decision: owner. Ruling c1 (arm 1, arm 2 as one predicate, or arm 2 with the swing term kept). Not read for a verdict here.
- The fix verdict's blocks 2 (note n6) and 3 (the body's c1 paragraph) are the fixer's; this verdict clears block 1 only, at d73ec97da1.

Seat token count: the harness reports none.
