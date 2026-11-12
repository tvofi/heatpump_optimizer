Fix review: merge 3d56953499ef23b0d51f2eee7d0cc782d05b572a

bus-nonce: af1debe34754400f68b15945c387b46a

## Round

Later round over the merge-verdicted head 701a18e26661a8c8ef416ae3bc1e9b7df2049d8a (verdict on probe/revt-r10-outside-supply-min-run-pause-a956bdf2). Earlier dispatches: 5dea8264f2c8 blocked (mutation-vacuous), 701a18e26661 merge, a936a11d461c head-moved (it measured nothing of this delta). Scope is the delta `git diff 701a18e26661 3d56953499ef` at the frozen handoff tip, per fix-review.md step 12. The one production change is 874cb0168230 (supply_hold.py, pump_arbiter.py, coordinator.py `_tail_freeze`). It replaces `interval_held` and `held_at` with `freeze_reason` and `held_until`. It widens the scope to nothing beyond those lines: `held_at`, `held_until` and `interval_held` have no other reader in custom_components/ (git grep at the head).

## Evidence

- Head reviewed: 3d56953499ef23b0d51f2eee7d0cc782d05b572a (ev/HEAD.txt), the handoff tip, frozen by the dispatch. The body's `## Head` names this SHA. No pull request exists yet, so there are no check runs to read and no CI to wait on. No review packet was dispatched.
- RESULT features_head: `PYTHONPATH=tests/hastub python3 tests/features.py` at the head printed `ALL 5416 FEATURE CHECKS PASSED`, rc 0 (ev/features_head.log).
- RESULT mutant m1 (`freeze_reason` `<` to `<=`): rc 1, `FAIL freeze_reason: null control: 60 minutes ago is not ['supply_held']` (ev/mutant_m1.diff, ev/features_m1.log).
- RESULT mutant m2 (`_freeze_span` two intervals to one): rc 1, 2 FAILs, `a write held 59 minutes ago on a 30-minute interval is frozen [None]` and `a config with no interval reads the default` (ev/features_m2.log).
- RESULT mutant m3 (`hold_supply` no longer sets `held_until`): rc 1, `FAIL an interval in which the gate held a write freezes the learners with the supply_held reason [None]`, then a TypeError in the freeze_reason block (ev/features_m3.log).
- RESULT mutant m4 (`_tail_freeze` drops `supply_hold.freeze_reason`): rc 1, the same integration check fails (ev/features_m4.log). Every predicate and assignment 874cb0168230 adds is killed. None survives.
- RESULT archscore: `tools/audit/archscore/score.py --diff 43e95474559c` at the head printed `Architecture score: dS +0.0000 NULL` (ev/archscore.log), matching the body. I did not re-derive the body's control (`dS -0.0006 WORSENS` at b2dd262882a8).
- RESULT structure: `tests/structure.py` printed `STRUCTURE RATCHET PASSED` with `class_excess_loc=17525`, the value 808f50df7f4c records (ev/structure.log). That budget change only lowers a cap. No `*_budgets.json` is raised in the delta.
- RESULT entities: `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` printed `ALL 2709 ENTITY CHECKS PASSED`, rc 0 (ev/entities.log).
- Versions and claims: `git diff 43e95474559c...HEAD` over VERSION, manifest.json, RELEASE_NOTES.md and both claim files is empty.
- Merge with main: `git merge-tree --write-tree origin/main 3d56953499ef` (origin/main d1def1ea6307) exit 0, `LEDGER-MERGE: resolved tests/closures.json`.
- Main-merge resolution 934f6d683e: per `--remerge-diff`, the tests/features.py conflict keeps both sides (the supply-switch sections and main's duty_switch block). The full features.py run above executed both. No custom_components/ path conflicted.
- Ledger delta: a936a11d4604 drops the five pins whose sites 874cb0168230 removed. 3d56953499ef pins the four new sites (freeze_reason BOOLOP, CMP_BOUND, RETURN_DEL; _freeze_span RETURN_DEL). My m1, m2 and m4 are in-place equivalents of CMP_BOUND, RETURN_DEL-span and the coordinator wiring, and are killed. I did not re-run `mutation_table.py --pin-killed` (a heavy run), so the body's `PIN KILLED: 4 pinned, 0 left unpinned` is quoted, not re-derived.
- Owed reds: `merge_train.py owed-reds` lists the required set. With no pull request, the head has no check runs, so no red is owed an answer at this head. The body's `## Red checks` answers the earlier reds (arch-score, mutation, pr-contract).
- Behaviour judged: the freeze span is now fixed when the write is held, from `inp.config` (a non-optional `Mapping` on `ArbiterInputs`). It is no longer recomputed at each learner query. An `optimization_interval` change applies from the next hold. Fail-closed side unchanged. Not a defect.

## Findings

- Carried from the 701a18e26661 verdict, still open: rule three (`supply_hold._ends_soon`) awaits the owner's ruling. The body still states its cost (0.82 kWh/day on LIGHT winter, a no-run HOT flat day) and the removal path. Carry: dismissed: surfaced in the PR body for the owner's code-owner review; no later stage changes
