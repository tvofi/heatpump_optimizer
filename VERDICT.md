Fix review: merge 7236c8a2c1dbd17b145598032e996a637e3fc752

bus-nonce: 70f18a8fbba02f3b6ebe65eacadd5d13
pending-ci: gate (merge_train.py classify prints WAIT 7236c8a2c1dbd17b145598032e996a637e3fc752 pending: gate red: none, after more than 30 min of polling, ev/classify_final.txt)

## Evidence

- Round 4, a delta review over the reviewed head 6ab7d15ef7dfb69eb55ede687f044297306572de (resume verdict/3444@45a53b2c). Range 6ab7d15e..7236c8a2: 2329627cd (mutation-autofix pins, 22 ledger files), 11547bbe3 (the churn-floor check in tests/features.py, 49 lines, and the pins), b6e31891a (a merge of both onto 2329627cd), 9b5c699a (merges origin/main 6d16af36), and 7236c8a2 (merges 9b5c699a).
- Production patch unchanged: `git diff ee64358be 6ab7d15e -- custom_components/` is byte-identical to `git diff 6d16af36 7236c8a2 -- custom_components/`. The main merge left the reviewed production code as it was, so the review does not widen.
- Previous verdict's one finding (Residual: the fix is inert at 10/15 min) was dismissed there, and the production patch has not changed, so it stands as dismissed. Nothing new to carry.
- Mutation proof, my own runs of `PYTHONPATH=tests/hastub python3 tests/features.py` in worktrees at this head (ev/features_M{0,1,2}.txt, ev/mutant_M{1,2}.diff):
  - M0, unmutated (the control): `ALL 5243 FEATURE CHECKS PASSED`, rc=0. The new check reads ok, and the combi_type_branch census is green now that main is merged.
  - M1, dhw_learning.py:516 `energy_kwh >= 1e-4`: rc=1, `1 of 5243 FEATURE CHECKS FAILED`, only "the draw fold saves a tick only strictly above its 1e-4 kWh floor, folded or taken back", reading `{'fold': (1, 1), 'take': (0, 1)}`.
  - M2, `taken_kwh >= 1e-4`: rc=1, the same single check, reading `{'fold': (0, 1), 'take': (1, 1)}`.
  - Each mutant fails only its own arm, and in every run the one-ulp-above control saves once. So the check is not vacuous, and each arm detects its own site.
- `python3 tests/mutation_table.py --list CMP_BOUND` (rc 0) prints both dhw_learning.py:516 CMP_BOUND sites as `pinned`, which matches the body. The ledger entry DhwProfileLearner.async_fold_draw_stats.CMP_BOUND.b95e18b7.json names tests/features.py as the killer.
- The new check is test-only: it drives `async_fold_draw_stats` at exactly 1e-4 and at nextafter(1e-4, 1), and the fold arm searches for a drop whose booked energy is exactly the floor. No production behaviour moves.
- `git merge-tree --write-tree origin/main 7236c8a2` exits 0 (`LEDGER-MERGE: resolved tests/closures.json`, set merge). origin/main is at 2cfa3d7d, and the head merges main 6d16af36 (ev/merge-tree.txt).
- Claim files: `git diff 6d16af36...7236c8a2` (three-dot) is empty for both claim files, so the branch claims nothing. The two-dot change in the range is main's.
- VERSION, manifest.json and RELEASE_NOTES.md show no change from merge base 6d16af36.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED (ev/structure.txt). The budget file's change against the merge base is class_excess_loc 17534 -> 17532 (down) plus recorded_at; nothing was raised.
- PR body: `## Head` names 7236c8a2c1dbd17b145598032e996a637e3fc752, which is the head measured here. `## Red checks` answers tests / mutation, tests / mutation-autofix, tests / typing, tests / fast (3.14), governance / instrument-self-tests, gate, pr-contract, arch-score and tests / nightly-status, each with a named cheaper detector or a finding that none exists. tests / nightly-status is outside `merge_train.py owed-reds` (ev/owed-reds.txt), so it owes nothing. The pr-contract run at this head has not run yet, so its check of red-history is CI's, behind the gate.
- Not re-run: the gate, the mutation table, and the round-3 harness figures, whose production patch is unchanged since they were measured; those are CI's or the prior round's. figure_lint's 43 `unverified` lines are the round-3 harness rows already re-derived in the previous verdict; I did not re-derive them at this delta.
- Harness provenance: the worktree mutants are mine, not in the tree, and their diffs are in ev/.
- Closing self-audit: `carry_audit.py check` over this verdict printed `CARRY-AUDIT: 0 finding item(s)` with rc 0. I ran it against a stub body holding only the PR body's `## Forward-carry: none` and `## Friction: none`. The review packet's own run of carry_audit at the head, over the live body, printed the same 0 items.
