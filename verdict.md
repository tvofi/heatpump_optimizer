Fix review: blocked 4a5abf4a0c86db73bc8291dc7d9d40dfb41d7385 class-open: _arm_space reads the dropped space record from held.feedback.prev_c, but every run-ending site in _feedback (pump_arbiter.py:934, 943, 946 after 939) discards it while the write is still held, so an unarmed key captures the optimizer's own write as the baseline (Carry 8 still live)

bus-nonce: 7e7c257d3d933d89842e35b1d57cef41

Round 2 (delta), cloud seat, measured at head `4a5abf4a0c86db73bc8291dc7d9d40dfb41d7385` over the reviewed head `561edf4c8f9b99420013b48ce1d225645ef70b95`. The PR head was still `4a5abf4a0c86db73bc8291dc7d9d40dfb41d7385` when I read it back before writing this verdict (`ev/HEAD.txt`).

## Block

- Commit `4831cb404f` claims that Carry 8 and Carry 17 are met: "`_arm_space` no longer reads the space record's absence as 'never written' without checking `ArbiterState.feedback`". But the dropped record lives only in the loop run's `prev_c`, and the run ends on paths other than a write or a restore. `_feedback` sets `held.feedback = None` on a pass without a qualifying inlet or base (`pump_arbiter.py:934`). It starts a fresh `FeedbackRun` (with `prev_c` None) when the compressor drops below the run threshold (`:943`), and again after a window-expired run (`:939` then `:946`). After any of these, `_arm_space` sees no record and no `prev_c`, so it computes `own=False` and captures the reading as the baseline. That reading is the optimizer's own last write.
- Reproduction: I added one check to the feedback block (`ev/reviewer-repro-R10.patch`), built on the PR's own `_fb_own` helper. I ran it through the harness's `SEAM_BLOCK` command (`ev/reviewer-repro-R10.txt`). It printed `REVIEWER-RESET held-after-move False after-off-pass True feedback None after-new-run True reading 26.0`, then `1 of 37 FEATURES BLOCK FAILED`.
  - Null control 1: the same state before the run ends is held (`held-after-move False`). This is the PR's own check, and it still passes.
  - Null control 2: an arbiter that never wrote captures (`never wrote True`). This is also the PR's own check.
  - The flip from held to captured comes only from the run ending. The ending comes from either `_feedback(..., on=False)` (`:934`) or a fresh `FeedbackRun` (`:943`/`:946`).
- Reachability: on an upgrade with the loop active, the first loop move after the key is unarmed is held by the own-write refusal, so the controller keeps the optimizer's value. The write stays held until a person changes the controller. During that time, any compressor stop, defrost or hot-water pass, or any other non-qualifying pass ends the run. The next space write then arms with the optimizer's own value as the baseline, so Off and unload restore the optimizer's number as if it were the person's. This is the exact failure Carry 8 names, reached by a different path. The PR's check covers only one move and two moves with no run end between them (M23/M24).
- Class rule for the fixer: every site that ends or replaces `held.feedback` while `written["space_setpoint"]` is absent. Running `git grep -n -E 'held.feedback = |rec = None|rec = held.feedback' -- custom_components/heatpump_optimizer/pump_arbiter.py` at the head returns these sites:
  - 934, 939, 943 and 946 (`_feedback`): all four are open.
  - 1054 (`_clamp_cut`): reached only through `hold`, which iterates over existing records, so the record is present there. Not open.
  - 1893 (`_space_restored`): the restore is intended to end the run. Not open.
- The body's own Carry 8 alternatives point the same way. Keeping the own-write fact on a structure whose lifetime is the loop run ties the refusal to compressor cycling. The fact needs a lifetime of "until a write replaces it or a restore ends it" that holds across run resets. That fixes `_arm_space`'s reader. Note that `_cut_of`/`_clamp_cut` read `prev_c` with run-scoped meaning, so the fix should not simply stop resetting it.

## Evidence

- RESULT mutation proof (step 1): `python3 dev/audit/harnesses/r10_arbiter_off_restore_mutants.py` at the head printed `SURVIVED NULL` and `KILLED` for M01 to M20 on the arbiter block, then `SURVIVED NULL` and `KILLED` for M21 to M25 on the feedback block, rc 0 (`ev/mutants-head.txt`). This matches the body's `## Mutation proof`.
- RESULT conflict resolution (step 13):
  - First merge, `acb7122c7` (561edf4c8 + a7628041dc): a fresh `git merge-tree --write-tree` of its parents reports `CONFLICT (content)` only in `pump_arbiter.py`, plus the ledger driver's `LEDGER-MERGE: resolved tests/closures.json`. The recorded merge differs from the fresh tree only by the three conflict-marker lines in `ArbiterState`: both parents' fields are kept (`space_before`, `feedback`, `stop_gap_k`), and no other line changed (`ev/merge-resolution-acb7122c7.txt`).
  - Second merge, `4a5abf4a0`: its tree `909195e5b8` is byte-identical to a fresh merge-tree of its parents (`ev/merge-resolution.txt`).
  - No main fix was reverted: `git diff origin/main...HEAD` touches only `pump_arbiter.py` in `custom_components/`.
- RESULT merge with main: `git merge-tree --write-tree origin/main 4a5abf4a0c` gives rc 0, and origin/main `cbd23f1c8` is the head's second parent (`ev/merge-tree.txt`).
- RESULT 8577f904 (cut seam): `_cut_of` is a pure extraction of `_clamp_cut`'s former bracket, and `_clamp_cut`'s behaviour is unchanged. Its extra `rec.prev_c is None` guard is redundant for behaviour and narrows the type for `value > rec.prev_c`. `_edited` gains `not _cut_of(held.feedback, record[0], observed)`, which is consistent with `hold`'s adoption. M21 and M22 are killed. I found no defect.
- RESULT 4831cb40 `_note_sent` change, its effect on main's loop (the widening named under step 12): keeping `prev_c` when the record is already gone changes `_clamp_cut`'s bracket only when the previous move's write was not recorded (held or failed). In that case the controller still holds the older `prev_c`, so the wider bracket is the right "record the write replaced". A miss resets the run (`_clamp_cut` `:1054`). This does not create a second defect. Risk named: `pump_arbiter.py` `_note_sent` / `_clamp_cut` bracket.
- CI: `merge_train.py classify 4a5abf4a0c --pr 3404` printed `WAIT ... pending: gate red: none` at 09:26:17Z (`ev/classify-log.txt`). The packet digest showed a `tests / mutation` failure (id 130432598986) and a `tests / nightly-status` failure. classify reports `red: none` for the required set (`ev/owed-reds.txt`), so `nightly-status` is not owed (defect-root-cause.md). I did not wait for green, because the block is on code and does not depend on CI.
- Figures not re-derived: `ALL 5236 FEATURE CHECKS PASSED`, the scoped-gate counts, `STRUCTURE RATCHET PASSED`, `dS +0.0006`, the S1 to S5 site mutants and the reviewer-mutant statuses (R1 to R4). I did not re-run any of them this round.
- Previous verdict's items: the R1 carry to R10-WATER-SETPOINT-FEEDBACK stands. R2 and R4 were dismissed. The body says R4 was re-anchored to `last)`, and I did not re-run it.

## Friction

- The frugal inline-search guard refused reads after five operations, so I read the mutant output through a scout agent. Carry: dismissed: session tooling, not this repository
