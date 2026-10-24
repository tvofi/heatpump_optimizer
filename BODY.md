The gate-lease slot pool let two runs hold one slot, because a rival read an owner file while it was being written: `Owner.create` (O_EXCL, then write) and `Owner.write` (truncate, then write) both leave an empty file for a moment, and `_free_slot` unlinks any slot it cannot parse. CI showed this as `tests / fast` FAIL `concurrency control: two waiters released in one poll` (`overlaps=1`). RCA: `dev/audit/rca/R10-RCA-GATE-LEASE-FLAKE.md`, state (c).

Round 2 repairs the fix review's block. `mark_unleased` had the same torn write: it used `write_text`, and `_unleased` deletes a marker it cannot parse, so a `slots_status` that polled at the wrong moment deleted a live run's unleased witness. There is now one whole-file writer, `_write_whole` (a staged sibling file moved in with `os.replace`), and both `Owner.write` and `mark_unleased` call it. A new `pool_contents` case kills mutant M4. The RCA's wrong sentence saying `_enqueue` writes non-atomically is replaced by a table of every writer and its disposition.

## Head

`ee341cb0750ddf1d515bc1d473bc1557af103bac` merges origin/main `343fb2a2c` into `0567c2dcf875`, which holds the round-2 code on top of the previous head `ea459c0b5`. Everything below was measured at `ee341cb0750ddf1d515bc1d473bc1557af103bac`.

## Mutation proof

`PYTHONPATH=tests/hastub python3 tests/gate_lock.py --accept`. Each mutant is one edit to the fixed tree, restored after its run:

- `mark_unleased` back to `path.write_text`: `FAIL an unleased marker being rewritten is never lost to a polling slot-status` (polls missing it, three runs: 7697, 16448, 4959 during 1000 rewrites), 1 of 33 FAILED. At the previous head, before the fix, the same case read 23191 during 4000 rewrites (the failing test, written first).
- `Owner.create`'s `finally: tmp.unlink` removed (M4): `FAIL a take, a renewal and a marker leave no staging file in the pool` (`pool=['.create-…-slot-000', 'flock', 'slot-000', 'unleased-prepr-x']`), 1 of 33 FAILED.
- `_write_whole` back to `path.write_text`: `torn_write` and `torn_marker` both FAIL, 2 of 33 FAILED.
- Round 1's mutants still stand: `Owner.create` reverted to O_EXCL-then-write gives `torn_create` `winners=['rival', 'a']` (the reviewer re-ran it at `ea459c0b5`).

The missed-poll counts depend on thread timing, so only their order of magnitude reproduces.

## Null control

On the fixed tree, `ALL 33 gate lock acceptance checks PASSED` in three runs. `one_winner` and the cases from before this PR are unchanged and still pass.

## Figures

- 33 cases, all passing, three runs; the mutant totals above: `PYTHONPATH=tests/hastub python3 tests/gate_lock.py --accept`
- Class seams: every content writer in the module, from `grep -nE "write_text\(|os\.open\(|\.touch\(|\.write\(" tests/gate_lock.py` (test cases excluded). Dispositions: `Owner.create` closed (staged file, `os.link`); `Owner.write` closed (`_write_whole`); `mark_unleased` closed in this round (`_write_whole`); `_ticket_tmp`/`_enqueue` already atomic (private temp file, then `os.link`/`os.replace`); the `holding` marker is only checked with `.exists()`, so it is outside the class; the `flock` touch and its `os.open` write no content. No other file writes the lock directory: `git grep -nE "unleased-|slots/slot-|hpo-gate.lock/" -- ':!tests/gate_lock.py' ':!dev/audit/rca'` returns only prose and `prepr.sh`'s call of the CLI.
- Standing cost, about 2.2 s per `--accept` run: three timed runs each, 9.2–9.6 s with the four new cases and 7.0–7.2 s with their `cases` entries removed (wall clock, local)
- Scoped gate: `python3 tests/closure.py select` prints `MODE: SCOPED -- 1 script(s) run` (`tests/entities.py`). Here it prints `2 of 2429 ENTITY CHECKS FAILED` at the head and `2 of 2425` at origin/main, and the failing lines are the same two `hb:positive_control` lines on both trees (py-spy in this seat does not name the spin), so this diff adds no failure: `diff <(grep FAIL base.txt) <(grep FAIL head.txt)`. `tests/structure.py`: `STRUCTURE RATCHET PASSED`. `closure.py selftest`, `layout.py` and `harness_headers.py` pass
- `tools/pr/prepr.sh` at this head: every step passes except `closures`, which refuses because `tests/entities.py` exits 1 on `hb:positive_control`. The same check fails at origin/main in this seat: py-spy 0.4.2 runs against CPython 3.14.7 here but its dump lists no thread, so it never names the spin. This is the seat's environment, not this diff, and CI's `fast` job owns `tests/entities.py`
- RCA counts (3 reds in 2.4 days, job minutes) are unchanged from round 1; their commands are in the RCA, section 3

## Red checks

none. The round-1 reds at `ea459c0b5` (`pr-contract` waiting on code scanning, `gate` waiting on runs still being judged) came from workflows that had not finished at the time; neither names a defect in this diff.

## Forward-carry

none

## Friction

none
