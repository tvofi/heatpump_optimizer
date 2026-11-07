stamp.py `record_flush` waited for a record merge while a live `refs/heads/train-hold` made every beat it dispatched exit `skip-train-hold`. Its three dispatches were spent under the hold, and the timeout named no hold. It now reads the hold itself and spends no dispatch under one. A second change, in `merge_train.py`, keeps the hold DELETE from being skipped by a second TERM or HUP during the unwind, and (repair round 2) delivers a first stop that lands in a batch's closing release instead of discarding it.

Repair round 2 (verdict/3280, blocked d65bcee9bdfb): `Train.batch` calls `unwind()` in the `finally` of every batch, and the round-1 `stop_ignored` set `SIG_IGN`, which discards a signal. A first TERM in batch k's release was lost and batch k+1 merged. `stop_ignored` now records the signal in a handler that does not raise, restores the handlers, and delivers the first recorded signal through the restored handler after the hold DELETE. Entered with a stop already unwinding (a `SystemExit` in flight), further signals are dropped, as the brief requires. The duplicate `import contextlib` is removed.

Alternatives: masking with `signal.pthread_sigmask` was not taken (it leaves the signal pending to the kernel, with no hook to say when the stop is already unwinding). No `train.sh` trap change. One `Train.unwind` method serves `train` and `batch`. The hold is an injected collaborator `held`, defaulting to `train_hold` (zero REST), the bound read from `nightly.yml`'s `HOLD_MAX_AGE_S=`, never a second literal. A hold never refuses the flush; an unreadable hold or bound reads as no hold.

`record_flush` gives a dispatch back (`count - 1`) whenever a hold appears after one, even if that beat had already run. A hold that flaps can therefore re-dispatch more than `FLUSH_MAX_DISPATCHES` beats in total; the 7200 s deadline bounds it, which is accepted.

Shared file: `tools/release/stamp.py` is also changed by the hotfix R10-FLY-STAMP-FLUSH-COST (topic r10-fly-stamp-flush-cost). This round changes no line of stamp.py; its stamp.py change is round 1's `record_flush`/hold reading. Whichever lands second merges `origin/main` and reruns `stamp.py --self-test`; no ordering is required by this PR.

Closes: triage batch 131 P402 (`dev/programme/triage/s6-batch131.md`, which exists only at triage ref `cd88cf6bd00d`, not at origin/main or this head).

## Head

10fa087733460ce6f8f5d4164d3e7fa1d4050ead, on origin/main 28d46c491 (merged in; `prepr.sh` run at this head, 2026-11-07T13:45Z).

## Mutation proof

Mutants are the source with one marked line replaced, run for real by the self-test driver:
- `mut:stopign` (`handler = defer` replaced by `handler = signal.SIG_IGN`, the round-1 behaviour): killed by the check "mutant (old SIG_IGN): the first TERM is discarded and batch 2 runs" reading `BATCH T-b2` and `RETURNED rc=0`; the real run of "a first TERM in batch 1's closing release stops the train: no second batch, exit 143" is the paired kill.
- `mut:deferdeliver` (the delivery line replaced by `pass`, a defer that never re-raises): killed by "mutant (defer never re-raises): the stop is lost as well and batch 2 runs".
- Record_flush predicate mutants (round 1, unchanged): `not hold` removed at the dispatch and re-dispatch sites, caught by "flush: a mutant dispatching under a live hold exhausts FLUSH_MAX_DISPATCHES, and is caught".

Failing test first: the batch arm was added before the fix and failed at the round-1 head (`FAIL a first TERM in batch 1's closing release stops the train: no second batch, exit 143`), then passed after.

## Null control

- With no signal, two batches both merge and the train returns 0: "null control: with no signal both batches merge and the train returns 0".
- One TERM on the train path deletes the hold ref; a second TERM during a stop's unwind is still ignored and the DELETE is still issued ("a train TERMed again during its unwind still deletes the hold ref").
- The first-TERM batch arm also asserts the hold DELETE went out before the stop was delivered.
- Stamp arms from round 1 (absent hold changes nothing; stale and future-dated holds read as no hold) are unchanged.

## Figures

- `python3 tools/audit/seat/merge_train.py --self-test` → "472 checks, 0 failed" (round 1: 468; the 4 new arms are the batch-path checks).
- `python3 tools/release/stamp.py --self-test` → `RESULT stamp_self_test=pass`.
- `python3 tests/structure.py` → STRUCTURE RATCHET PASSED.
- `bash tools/pr/prepr.sh` at the head → `rc=0` (origin/main unmoved since: no second run owed).
- Class seams: the rule is `grep -n "stop_ignored\|\.unwind()" tools/audit/seat/merge_train.py`; callers are `Train.unwind` (used by `train` and `batch`) alone, both covered by the arms above. The reviewer's two-batch probe (from verdict/3280, not in the tree) is ported as the batch driver of `_unwind_self_test` in merge_train.py.

## Red checks

none. The check-runs API for d65bcee9bdfb (68 runs on one page of 100): 0 failure or cancelled. Local `prepr.sh` repaired one red in round 1 (agreement lane).

## Forward-carry

none

## Friction

none
