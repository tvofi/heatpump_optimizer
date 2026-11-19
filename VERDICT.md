Fix review: merge 9809bc79c2498f2b25867a5cc88dacd68c62a01a
bus-nonce: c797b3be109992538e0094608c491546

Note: mutation-red: tests / mutation (job 135435076683, run 44484978564) is red at this head: MUTATION TABLE REFUSED on the six added unpinned sites the body's `## Red checks` already names (coordinator.py 6148 BOOLOP, 11199 GUARD_OFF; solve_gate.py 76, 78, 90, 129; ev/ci_mutation_table_9809bc79.txt), with tests / mutation-pins (1)/(2) in progress at review time to pin them (ci-autofix.md). The same six were refused at 28977f9e; not introduced by the delta under review. bus.sh post refuses merge while it is red (C8). Carry: dismissed: answered in the body's Red checks; mutation-autofix pins them
Note: stale-figure: the body's `## Architecture score` quotes `score.py --diff 8ab5dc566f`, an earlier merge base than this head's 99436a082c; the PR's own diff is unchanged across the merge (below), so the figure's substance holds; owed: re-take at the current base. Carry: dismissed: paperwork on a body figure, not code

Round 3, delta only (tvofi 2026-11-09): reviewed head 28977f9e820ee1813eccd5952484e0365e72f91a (verdict on review/3738, b1b28784d7) -> 9809bc79c2498f2b25867a5cc88dacd68c62a01a. review_carry.py printed FRESH-REVIEW (71c7ef06 is not the automatic merge of its parents), so the delta was read by hand.

## Delta
- The PR's own diff, merge-base-relative at each head (8751943e...28977f9e vs 99436a08...9809bc79), differs in exactly three files: tests/features.py (one added blank line where main's appended block meets the PR's), tests/structure_budgets.json (only main's base `recorded_at` moved; the PR's own budget moves are byte-identical: class_excess_loc 17382->17380, coordinator_attrs 136->135, coordinator_multiassigned_attrs 104->102, max_class_loc 7875->7873), and the deletion of tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.RETURN_DEL.1457a93f.json (ev/own_diff_interdiff.txt). No custom_components/ line of the PR's own diff changed, so nothing widens the review.
- Stale pin deletion: the 1457a93f pin's `old` is `        return payload` (8 spaces) in async_simulate; at this head async_simulate holds no such line, the return now sits at coordinator.py:11289 (12 spaces, under the solve gate's user slot), anchored fd0988d6 and already pinned by c06d2fb954 (killed_by tests/features.py). Targeted mutant at the head (tools/audit/seat/mutant_run.py --root <worktree> --spec, ev/mutant_spec.json; command features_block.py over "# #240: the what-if's parameters must share" .. "# -- The held start, on the optimizer" with its emitted prelude): `SURVIVED NULL`, `KILLED async_simulate_RETURN_DEL_fd0988d6` (ev/mutant_fd0988d6.log). The deletion removes a dead anchor and leaves the live site pinned.
- tests/features.py conflict union: both appended blocks survive in order, the PR's `# -- R11-SEAM-cycle-solve: when a solve runs (solve_gate)` (line 97386) then main's `# -- The plan peak under the lift: accepted, never clipped` (line 97837), before the single closing `sys.exit(R.close(...))`. Each run alone through tools/audit/seat/features_block.py with its emitted prelude: `ALL 13 FEATURES BLOCK PASSED` rc 0 (ev/block_cycle_solve.log) and `ALL 2 FEATURES BLOCK PASSED` rc 0 (ev/block_room_lift_peak.log). The full tests/features.py was started at the head but had not finished on this host (load average ~147) at publication; CI's tests lanes at this head are the authority.
- tests/structure.py at the head: STRUCTURE RATCHET PASSED, rc 0 (ev/structure.log).

## Prior findings
- Note mutation-red (stale 1457a93f pin on the merge ref): RESOLVED by the pin's deletion; the refusal text at this head names only the six added sites, not 1457a93f (ev/ci_mutation_table_9809bc79.txt).
- Note stale-figure (architecture score base): still stale at a newer base; carried above as a Note.
- Round 2's block resolution (D1-s1-03 trailing refresh): the code it verified is unchanged in the own diff (no custom_components/ interdiff), so it stays resolved.

## Evidence
- git merge-tree --write-tree origin/main 9809bc79: rc 0 (ev/merge_tree.txt).
- Three-dot from 99436a082c: VERSION, manifest.json, RELEASE_NOTES.md and both claim files untouched.
- The body's `## Head` names 9809bc79c2498f2b25867a5cc88dacd68c62a01a; refs/pull/3738/head read back at 9809bc79c2498f2b25867a5cc88dacd68c62a01a before posting.
- Live checks at publication: tests / mutation failure (above), gate failure (downstream of it), arch-instrument, closures, coverage, fast (3.14), replay and mutation-pins (1)/(2) in progress.
