stamp.py `record_flush` waited for a record merge while a live `refs/heads/train-hold` made every beat it dispatched exit `skip-train-hold`. Its three dispatches were spent under the hold, and the timeout named no hold. It now reads the hold itself and spends no dispatch under one. A second change, in `merge_train.py`, makes the train's unwind ignore a second TERM or HUP, so the hold DELETE is always issued.

Alternatives: no `train.sh` trap change (`pr_exit_trap` already TERMs `merge_train.py` first). The unwind is one `Train.unwind` method used by both `train` and `batch`, instead of the guard being duplicated at each `finally`. The hold is an injected collaborator `held`, defaulting to `train_hold` (zero REST: `git ls-remote`, fetched committer date, message pid), with the bound read from `nightly.yml`'s `HOLD_MAX_AGE_S=` by source read, never a second literal. A hold never refuses the flush; an unreadable hold or bound reads as no hold. The hold pid is read with `partition`, not a second `pid=(\d+)` grammar, which `agreement.mjs` reported as UNREGISTERED against `beatd.py`'s lock-file reader (a different concept).

Closes: triage batch 131 P402 (dev/programme/triage/s6-batch131.md).

## Head

819d6528ad0a6408fbfb33048c114a185eb5fdde, on origin/main be813ecd4924 (unmoved at the last `prepr.sh`; no second run owed).

## Mutation proof

- `mut:stopign` (the `signal.SIG_IGN` line in `stop_ignored`, replaced by `contextlib.nullcontext`): `merge_train.py --self-test` arm "a train TERMed again during its unwind still deletes the hold ref" is paired with the arm "mutant mut:stopign ... the second TERM skips the DELETE", which runs the unfixed unwind for real and reads no DELETE.
- Predicate mutant of `record_flush` (`if not hold and` removed at the dispatch site and the re-dispatch site, run inside the stamp self-test): it dispatches under the planted live hold and exhausts at `FLUSH_MAX_DISPATCHES`; arm "flush: a mutant dispatching under a live hold exhausts FLUSH_MAX_DISPATCHES, and is caught".

## Null control

- Probe at the base (`merge_train.py` at be813ecd, stubbed gh, `Train._train` replaced by a sleep, worktree release stubbed to take 2 s, `held=True`): one TERM issues `gh api --method DELETE repos/o/r/git/refs/heads/train-hold`; a second TERM 0.5 s later issues no DELETE (it ends at `git worktree remove`). Not a non-finding, so the fix is made. The same probe is the self-test's driver.
- The `merge_train.py` arm "null control: one TERM deletes the hold ref" passes on both trees.
- Stamp arm "an absent hold changes nothing (null control)": `FLUSH_MAX_DISPATCHES` dispatches and no hold named, as before.
- Stale and future-dated holds read as no hold (arm "hold: a young one is live ...").

## Figures

- `python3 tools/audit/seat/merge_train.py --self-test` → "468 checks, 0 failed" (the 3 new arms included).
- `python3 tools/release/stamp.py --self-test` → `RESULT stamp_self_test=pass`.
- `node tools/policy/agreement.mjs | grep -c UNREGISTERED` → 0.
- `bash tools/pr/prepr.sh` at the head → `rc=0`, scoped gate: `tests/doc_claims.py` and `tests/entities.py` ran green.
- `python3 tests/structure.py` → RATCHET PASSED.

## Red checks

none. One local `prepr.sh` red, `agreement lane` (UNREGISTERED `pid=(\d+)` shared with `beatd.py`), was repaired before the handoff; the cheaper detector is `prepr.sh`'s own agreement lane, which already caught it.

## Forward-carry

none

## Friction

none
