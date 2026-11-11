Fix review: merge d7347d0cbfeccbfdf4e9d7a19ecafcb59ba2cb34

bus-nonce: 091e3d4343ed64fd2f85057b48283289
pending-ci: gate

## Round

This is round 3 of this group (R10-ARBITER-OFF-RESTORE). It follows the round-2 verdict at `4a5abf4a`, which was blocked `class-open`. `review_carry.py 4a5abf4a d7347d0c` prints `FRESH-REVIEW` (`ev/review-carry.txt`). Under fix-review.md step 12 the round is reviewed as its delta: `git diff 4a5abf4a d7347d0c`, which is the production code in `ev/delta-production.diff`, plus the test, harness and ledger deltas. No main merge is in the delta: d7347d0c merges only e40e4594 into the branch. I measured at d7347d0c from a detached worktree.

## Evidence

- Head: the PR body's `## Head` names `d7347d0cbfeccbfdf4e9d7a19ecafcb59ba2cb34`, which is the head I measured (`ev/HEAD.txt`).
- Merge: `git merge-tree --write-tree origin/main d7347d0c` exits 0 against origin/main `ee64358be7` (`ev/merge-tree.txt`). Its stderr reads `LEDGER-MERGE: resolved tests/closures.json`, so the ledger driver resolved that file. No conflict.
- Prior block resolved. The round-2 block said `_arm_space` read the dropped record from `held.feedback.prev_c`, which `_feedback`'s run ends discard.
  - At the head, the fact lives on `ArbiterState.dropped`. `_note_sent` sets it. `_arm_space` reads it only while `written["space_setpoint"]` is absent.
  - Its lifetime is the one the block asked for. It is persisted beside `written` and loaded through `_writable`. It is cleared only by `_space_restored` (restore) and `_forget` (Off pass and release).
  - The run-scoped `prev_c` is untouched at the reset sites, so `_cut_of` and `_clamp_cut` keep their meaning.
- Class sweep: I re-ran the round-2 rule at the head (`git grep -n -E 'held.feedback = |rec = None|rec = held.feedback'`, `ev/class-sweep.txt`). It returns the same eight lines as the body: `:940`, `:943` (a read), `:945`, `:949`, `:952`, `:1062`, `:1065` and `:1904`.
  - The four run ends at `:940`, `:945`, `:949` and `:952` are each closed. The harness re-injects the defect at each site (`held.dropped.clear()`, M27 to M30), and each injection is KILLED.
  - `:1062` and `:1065` (`_clamp_cut`) are reached only through `hold` over present records. `:1904` is the restore. Both dispositions are unchanged from round 2.
  - The restart path (the run is never persisted) is closed by persistence (M31, M32, M38).
- Sibling rule: `git grep -n -E 'written\.pop\(|del held\.written'` returns `:1016`, `:1336` and `:1494`, matching the body's three sites.
  - Can a stale `dropped` value reach an unarmed `_arm_space`? A space write lands only after `_arm_space` arms: `_held_back` returns `not await _arm_space(...)`, so a failed arm holds the write.
  - `off_restore` disarms without the `restored` callback in two places: `_restore_baseline` with no writer (`off_restore.py:205-209`) and `async_restore` with no restorer or value (`:242-244`). Both leave the entity at the optimizer's value. A refusal of that value as a baseline is then correct, not stale.
  - Unload order: `async_unload_entry` calls `off_restore.async_restore` (`__init__.py:426`), whose callback `_space_restored` clears `dropped`, before `coordinator.async_shutdown()` (`:429`). `release` then saves with `_persist` (`pump_arbiter.py:1772-1786`). I did not trace `async_shutdown` to `release` line by line.
- Mutation proof, re-run by me at the head with `python3 dev/audit/harnesses/r10_arbiter_off_restore_mutants.py` on `git archive` copies (`ev/harness-mutants-head.txt`).
  - Both blocks print `SURVIVED NULL`.
  - 37 mutants are KILLED: M01 to M20 on the arbiter block, and M21 to M32 plus M34 to M38 on the feedback block. None survived. rc 0.
  - This instrument is the fixer's (fix-review.md step 9). The group has no finder harness: it is an owner-ruled build (#201 comment 6708225978), as the body states.
- Own mutants, built by me and not in the fixer's set, run on the harness's `SEAM_BLOCK` through `tools/audit/seat/mutant_run.py` (`ev/own-spec-X.json`, `ev/own-mutants-X.txt`). Each is SURVIVED NULL then KILLED, rc 0:
  - X1 `_arm_space` reads `None` in place of `held.dropped`.
  - X2 `_note_sent` sets `prev_c` but not `dropped`.
  - X3 `_load` discards the stored `dropped`.
- The body's unpinned-site kills, re-run by me (`ev/own-spec-U.json`, `ev/own-mutants-U.txt`). On `SEAM_BLOCK`: SURVIVED NULL, `KILLED U1_note_sent_guard_off` (`:1013`), `KILLED U2_release_guard_off` (`:1586`), rc 0. This agrees with the body.
- Null control: SURVIVED NULL in every driver run above. The body's per-row control (`prev_c` None after every run end at both ends) is in the check the mutants kill. I did not separately re-run the base-side `1 of 37 FEATURES BLOCK FAILED` failing-first figure. M37 (round 2's reader) and my X1 put the base's reader back and both are KILLED, which is the same failure observed from the head side.
- Cheap checks at the head (`ev/cheap-checks.txt`):
  - `tests/finite_boundary.py`: `ALL 110 FINITE BOUNDARY CHECKS PASSED`. The new `dropped/space_setpoint` is declared in `store.DOMAINS`.
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
  - `archscore --diff cbd23f1c8b`: `Architecture score: dS +0.0000 NULL`, as the body quotes.
- Step 4 and step 5 checks:
  - `VERSION`, `manifest.json`, `RELEASE_NOTES.md`, both claim files and every `*_budgets.json` are untouched three-dot against the merge base `cbd23f1c8b`.
  - No golden fixture moves in the diff, so there is no claim to compare.
- Metric movement (step 14): one ledger pin is deleted, `_arbitrate GUARD_OFF 87a4cba9`, a stale pin on the Off-pass guard line this diff edits. It is replaced in CI by `mutation-autofix`. The new line's mutant is shown KILLED by U2 above, so the deletion is earned by the line edit and is not a dropped disposition.
- Figures I did not re-derive:
  - The body's scoped-gate count (`MODE: SCOPED -- 23 script(s) run, 10 scoped out`).
  - The full `tests/features.py` `1 of 5253` figure.
  - The `ci_predict.py` output.
  - These are CI's heavy runs, cited and not re-run.
- Red checks (fix-review.md step 11; owed set in `ev/owed-reds.txt`):
  - `tests / mutation`, job 130533725880, is red at this head: `MUTATION TABLE REFUSED -- 2632 unpinned site(s) against 2626 ... 7 of them added by this diff`. The sites are `:1013` GUARD_OFF, `:1038` GUARD_OFF, `:1041` CMP_BOUND*2, `:1041` RETURN_DEL, `:1063` GUARD_OFF and `:1586` GUARD_OFF.
  - This is the body's six `## Unpinned sites` entries, CMP_BOUND*2 counting as two. The body's `## Red checks` names `mutation`, with `ci_predict.py` as the cheaper detector. These are killed unpinned sites that `mutation-autofix` repairs (ci-autofix.md), and the body shows each killed. I re-ran U1 and U2 above. The trigger is answered.
  - `gate` is red as the aggregator of that red.
  - `tests / nightly-status` is red but is not in the owed set, so it blocks nothing.
- CI wait: from 13:05 to 13:35Z, `merge_train.py classify d7347d0c --pr 3404` printed `WAIT ... pending: gate red: none` (rc 3) on 30 runs at least 60 s apart (`ev/classify-log.txt`). I stopped waiting under the brief's 30-minute rule, so the relay posts this verdict only once CI is green at this head. `tests / fast (3.14)` was still running at my last read. The body answers its predicted inherited census red in `## Red checks` (main-vendor-census), and the brief rules it inherited from main.

## Findings

none
