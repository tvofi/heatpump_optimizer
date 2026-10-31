Fix review: merge d51d7c46caf7896426cb8e503f288e7c4c3db0b5

bus-nonce: a97c895d640dbdf46105755a11aac05c

## Summary

Round 1 of PR #3038 (R10-COP-GATE part 6, leads 20 and 21). I measured head d51d7c46caf7896426cb8e503f288e7c4c3db0b5 in a detached worktree. The merge base is be7584c4904e243ffb48c166be39221623d81415. The roles diff from the merge base to origin/main is empty, so the contract I followed is current. The fix is correct, every mutant is killed, the nulls hold, the class is closed or carried by id, and CI is GREEN. The architecture score is inadmissible (coord_footprint +2). I found only one admissible placement, and it is not sounder (see Findings), so the score does not block.

## Findings

- The body says "no existing statement there can absorb an early return that both the metered and the unmetered path need". That is not quite true. In `ev/alt_placement_A.diff` I put the predicate into the unmetered `return` as `None if ran_hot_water(...) else commanded_space`, and added it as a fourth term of the existing `measured is None or immersion or resistive` refusal. At the head that reads `Architecture score: dS +0.0000 NULL`, so it is admissible and behaves the same. I judge it not sounder. It writes the attribution call twice, once per branch, and the two copies can drift apart. The head's single guard states the rule once. That makes it the score-gaming shape (the same logic, fewer counted statements). The instrument property behind it: coord_footprint counts a guard statement but does not count the same predicate copied into existing conditions. This is by design for a statement count, and the arch-score gate already accepts an inadmissible rise with a stated reason, which this body gives. Carry: dismissed: statement-count metric by design (footprint.py docstring); no seat acted wrongly and the gate admits the stated reason
- Class, `_propagated_slab`'s `draw_range.space_draw_kw(..., coord._commanded_split(), space_served=...)` (coordinator.py:1010). It has the same plan-against-dwell shape on a point reading. It is a different rule, though, not an open seam of this class. The slab estimator cannot skip: it has to advance by some figure. Its existing rule books a live hot-water mode as a confident 0.0 kW, where `_interval_space_power` returns None. So for a switch-back interval the choice is between prorating and falling back to the plan, and that is a design decision, not this PR's predicate. The body names it, and it landed by id as carry 22 of R10-COP-GATE on origin/handoff/audit-r10-roster f85142a76, with MEASURE FIRST and the all-space null stated as its precondition (step 10 satisfied). Carry: R10-COP-GATE
- Structure payment (2c7f05d8a). The condensed v5.3.0 comment in `_interval_space_power` drops two pieces of the reason: the cooling-circuit destination, and the fact that the house heat-loss learner would replay a 0 kW sample as thermal behaviour. The core reason ("a confident claim the house got nothing") is kept. The -1/-1 re-record is earned by these real line removals and its reason is in commit 9c601202f's message. This is a nit and not a block. Carry: dismissed: the rule's reason survives in the comment and the docstring; a nit on comment wording

## Evidence

- Mutation proof (`ev/mut_*.log`). I ran each mutant as one exact replacement in its own detached worktree at the head, then `PYTHONPATH=tests/hastub python3 tests/features.py`:
  - RESULT head: `ALL 4642 FEATURE CHECKS PASSED` rc=0
  - RESULT site 1 (the `if ran_hot_water(...): return None` lines deleted): `2 of 4642 FEATURE CHECKS FAILED`, the two `_interval_space_power` checks (switch-back 2.2, hot water to the close 2.2; no power entity: switch-back 2.2).
  - RESULT site 2 (`and not ran_hot_water(...)` dropped from the `_record_accuracy` fold): `1 of 4642 FEATURE CHECKS FAILED`, the draw-fold check (`{'switch-back': 1, 'hot water to the close': 1, 'all-space': 1, 'no dwell': 1}`).
  - RESULT BOOLOP (`or`): rc=1, `FAIL without a power entity the commanded space figure is all there is`, then a TypeError at features.py:27506 (an existing check).
  - RESULT CMP_BOUND (`>=`): `3 of 4642 FEATURE CHECKS FAILED`; the all-space nulls refuse (None / 0) and the no-dwell arm keeps folding 1.
  - RESULT observed removed (`return a.dhw > 0.0`): rc=1, the same existing-check FAIL and TypeError as BOOLOP.
  - Every figure matches the body.
- Nulls. In the site 1 and site 2 mutants, which put back the base behaviour, the all-space dwell and the no-dwell interval read 2.2 / 2.2 / fold 1 / fold 1. At the head they read the same. So the nulls keep the plan rule at both ends.
- Predicate attack (1):
  - A combination mode, cooling, an unrecognised mode or a stale last-good read gives `observed_duty` None. `ModeDwell.shares` then returns None, so the interval is unobserved and the plan rule stands, consistent with the module doctrine (#2753).
  - A dwell that is observed with dhw==0 while the mode is hot water at the close needs a change exactly at the read instant (a zero-length segment). On the space-power path the existing live-mode refusal `mode_observed and not space_heat` still catches it. On the fold path it is an edge of zero measure.
  - `meter.cycle` is (the previous read, this read), set in `_observe_heat_energy` before both readers in the same cycle. `_pending_prediction` and `_last_house_sample` are re-set every cycle, so the attribution window is the interval each site governs.
  - Refusing rather than prorating matches `space_heat_kw`'s point-reading rule on the metered path. On the unmetered path the ask could be prorated, but that would assume the pump delivered the ask during its space hours. The refusal selects on mode, not on the measured value, so it is the unbiased choice.
- Class enumeration (3). I re-ran the body's two greps at the head and they return the sites the body lists. `_interval_space_power` has one caller (`_close_fabric_interval`, :5388).
- Architecture score (4): RESULT `python3 tools/audit/archscore/score.py --diff be7584c4904e243ffb48c166be39221623d81415` at the head gives `Architecture score: dS -0.0012 WORSENS (inadmissible: coord_footprint 2380->2382)` (`ev/archscore.txt`). Alternative A reads NULL; it is judged above. The other placements I considered:
  - Moving the refusal into `heat_energy` or the meter: the call site still needs one statement in the coordinator to act on the answer, so no saving.
  - Folding it into the live-mode refusal: that covers only the metered path.
- Structure (5): RESULT `tests/structure.py` at the head gives `STRUCTURE RATCHET PASSED`, `class_excess_loc 17655 <= 17655` and `max_class_loc 8060 <= 8060`, rc=0 (`ev/structure.txt`). Commit 9c601202f's message records the reason.
- Mutation ledger (6): RESULT `tests/mutation_table.py --list` shows `pinned` for coordinator.py:4718 GUARD_OFF, coordinator.py:9751 GUARD_OFF, and heat_energy.py:252 BOOLOP, CMP_BOUND and RETURN_DEL (`ev/mutation_list.txt`). No file under tests/ names `b36c07ff` at the head.
- Finder's harness. I read `dev/audit/rounds/round10/study-ident/owner_rows.py` and did not run it (it reads a private bundle). It recomputes gates from stored accuracy rows, calls `draw_range` directly, and never calls `_interval_space_power` or `_record_accuracy`. Its rows carry no mode dwell. So it is flat for this diff by construction, as the body says.
- Companion harness: RESULT `dev/audit/harnesses/r10_cop_gate.py` (sha1 d03dd93508936796fba5ec07ce387d393c9d8b60). At be7584c49 and at the head both print `RESULT synthetic.selfset.folded=0/12 refusal=draw_off_ask observability=not_measurable` and `RESULT synthetic.follows.folded=12/12 refusal=None observability=draw_follows_plan`, so it is flat (`ev/companion.txt`).
- CI (7). RESULT `merge_train.py classify d51d7c46caf7896426cb8e503f288e7c4c3db0b5` gives `GREEN ... pending: none red: none` rc=0, at the start and again before the verdict (`ev/classify.txt`, `ev/classify2.txt`). The review packet's check digest shows no red check-run. The body's `## Red checks: none` is consistent with that. I cite CI's heavy runs and did not re-run them.
- Merge. RESULT `git merge-tree --write-tree origin/main d51d7c46c` against origin/main 3759d49a5aa032f2edd66f6406e5aabf5072b1fc exited rc=0 (`ev/merge_tree.txt`).
- `VERSION`, the manifest, `RELEASE_NOTES.md` and both claim files are untouched in the three-dot diff. No golden fixture is in the diff.
- Head. The PR head at verdict time is d51d7c46caf7896426cb8e503f288e7c4c3db0b5 (ls-remote refs/pull/3038/head), which is the head I measured and the head the body names.
- Figures I did not re-derive myself:
  - the body's `MODE: SCOPED -- 22 script(s) run`;
  - its prepr.sh output;
  - its `4642` count at 9c601202f. My own count is 4642 at the head.
- Instrument note: the mutation driver is my own scratch script (`mut.py`, one exact replacement asserted once), not in the tree.
