Fix review: blocked d65bcee9bdfb2cc11302d1c96d4bf00659ec24db class-open: Train.batch runs unwind after every batch, so a first TERM or HUP landing in a between-batch release is discarded by SIG_IGN and the train goes on to merge the next batch

bus-nonce: 206cf0ae7035dcafbdd6b18a4ab76231

## Block

Round 1. `stop_ignored` sets `SIG_IGN` for TERM and HUP, which **discards** a signal and does not defer it. `Train.unwind` is documented as running "once a stop is already unwinding it", and in `train()` that holds. `Train.batch` (merge_train.py:3205-3208 at the head) is different: it calls `self.unwind()` in the `finally` of **every** batch, including one that completed normally. A first, and only, operator TERM or HUP that lands while batch k releases its worktrees and hold is therefore thrown away. The loop then goes on to `queue_take` and `_batch(k+1)`, and that batch merges.

I measured this with my own probe, not the finder's or the fixer's. It is `ev/probe/batch_swallow.py` and `ev/probe/run.sh`: two batches, stubbed `run` with a 2 s `git worktree remove`, and one TERM sent 0.3 s into batch 1's unwind.
- At the head (`ev/probe-batch-swallow-head.txt`): `BATCH T` … DELETE, then **`BATCH T-b2`** … DELETE, then `RETURNED rc=0`. The stop was lost and the second batch ran.
- Null control, with the base's unwind and the same driver (`ev/probe-batch-swallow-null.txt`): `SYSTEMEXIT 143` after batch 1, so the stop is honoured. That run shows the original hold-DELETE skip, which is the bug the PR fixes.

The fix trades the hold-ref leak for a lost stop request on the path that merges pull requests. That is the worse failure. The brief asked for the unwind to ignore further signals "once it starts", meaning once a stop is unwinding, and not on every batch boundary. The self-test `_unwind_self_test` drives only `train()`, so this seam is untested.

The cure is the fixer's to choose. One sound shape: keep the signal but defer it. Inside the block, record the signal number in a handler that does not raise, or mask it with `signal.pthread_sigmask(SIG_BLOCK, …)`. Re-raise or unmask it after the hold DELETE, so a pending stop is delivered then. Add a batch-path arm: one TERM during batch 1's unwind, assert there is no `BATCH T-b2` and a non-zero exit, with this probe's mutant as the control.

## Findings

- `import contextlib` is now imported twice, at merge_train.py:277 and :280. The diff adds a duplicate of an existing import. Carry: R10-FLY-STAMP-FLUSH-HOLD
- The body's `Closes: triage batch 131 P402 (dev/programme/triage/s6-batch131.md)` path resolves neither at origin/main nor at the head. It exists only at `cd88cf6bd00d`, the triage ref named in the roster brief. Name that ref beside the path. Carry: R10-FLY-STAMP-FLUSH-HOLD
- `record_flush` gives back a dispatch whenever a hold appears after one (`count - 1`). This happens even when that beat already ran before the hold appeared. A hold that flaps can therefore re-dispatch more than `FLUSH_MAX_DISPATCHES` beats in total within the 7200 s deadline. The deadline bounds it, so I judge this acceptable, but the body should say so. Carry: R10-FLY-STAMP-FLUSH-HOLD

## Evidence

- RESULT head reviewed: d65bcee9bdfb2cc11302d1c96d4bf00659ec24db, from a detached worktree; merge base 0e9c508c1260220e49c049753b011e6e140f0e9c; `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- RESULT finder harness: the packet names none. The group brief's probe (stubbed gh, TERM twice during the unwind) is embedded as `_unwind_self_test`, and I re-ran it. The batch probe above is my own instrument.
- RESULT `python3 tools/audit/seat/merge_train.py --self-test`: "468 checks, 0 failed", rc=0 (`ev/train-selftest.txt`), which matches the body.
- RESULT `python3 tools/release/stamp.py --self-test`: `RESULT stamp_self_test=pass`, rc=0 (`ev/stamp-selftest.txt`), which matches the body.
- RESULT mutants (`ev/mutants.txt`), with the unmutated runs above as the null control. All were killed:
  - M1, `mut:stopign` with SIG_IGN replaced by the current handler: FAIL "a train TERMed again during its unwind still deletes the hold ref".
  - M2, `stop_ignored` replaced by nullcontext in `unwind`: the same arm FAILs.
  - M3, dispatch-site `not hold` removed: FAIL "planted live hold … spends no dispatch" and FAIL on the predicate-mutant arm.
  - M4, re-dispatch-site `not hold` removed: the same two FAIL.
  - M5, dispatch take-back removed: FAIL "a dispatch sent before the hold appeared is taken back …".
  - M6, stale-bound check removed: FAIL "hold: a young one is live …".
- RESULT bound: `hold_bound_s` reads `HOLD_MAX_AGE_S=3600` from nightly.yml:1064. There is no literal 3600 in `train_hold` or `hold_bound_s`. The staleness rule (age < 0 is stale, age >= bound is stale) matches nightly.yml:1081-1087. A failed read, or a missing bound, reads as no hold.
- RESULT `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. `node tools/policy/agreement.mjs | grep -c UNREGISTERED`: 0 (`ev/figures.txt`).
- RESULT `git merge-tree --write-tree origin/main d65bcee9…`: rc=0, tree 26211f9b0a4c, no conflict.
- RESULT VERSION, the manifest, RELEASE_NOTES.md, structure budgets and closures are untouched by the three-dot diff. The new tracked file is only the delivery row `dev/programme/delivery/3280.md`, which is in the diff.
- RESULT CI: `merge_train.py classify` gave `GREEN … pending: none red: none`, rc=0 (`ev/classify.txt`). The check-runs API across all pages lists 48 runs: 31 success, 17 skipped, 0 failure or cancelled. The body's `## Red checks: none` agrees.
- RESULT `## Head` names d65bcee…, which is current. The stray second line (`819d6528…` on be813ecd) is stale prose; it is not the head.
