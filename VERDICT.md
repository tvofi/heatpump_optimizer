Fix review: merge 98d33ce032e8958419accb7fa91fa9661b494521

bus-nonce: e28c83d19cc2c027a016dde52c84fca0

Review round 2. It judges the delta since round 1's `aac8c5e80`. Measured head: `98d33ce032e8958419accb7fa91fa9661b494521`. After it, mutation-autofix pushed `6f6aa4e48d6871cf5cb926c9ac53a521468ae58a` ("ci: pin killed mutants"), which is now the live head; I judged that commit as a delta (below). Evidence: `/Users/timmalmstrom/hpo-seats/r10s3/review-2379/evidence-r2`.

## Delta since aac8c5e80

- Production: `git diff aac8c5e80 98d33ce03 -- custom_components` is empty. The fixer's only change is a21ed7c29, which adds 49 lines to `tests/finite_boundary.py` (`_owner_pins`, nine rows, each driving the production symbol).
- Main merge: e7c743e27..98d33ce03 changes only 31 ledger `reason` lines from main's privacy scrub. It changes no file this PR authors and none of the PR's own pins. The three-dot diff against the merge base is 7 M, 24 A, 7 D: the 3 production files, 4 test or record files and the delivery row; the 23 round-1 pins and a21ed7c29's change; and the 7 stale pins. `git merge-tree --write-tree origin/main` at the live head exits 0, and its only stderr line is `LEDGER-MERGE: resolved tests/closures.json`. Goldens, claim files, VERSION, the manifest version and the notes heading are untouched.

## Each killing pin against its mutant (my runs of `tests/finite_boundary.py`, one worktree, each restored; clean run: `ALL 101 FINITE BOUNDARY CHECKS PASSED`, with all nine `(#2379)` rows `ok`)

- `climate.py:140 GUARD_OFF`, `if measured is not None:` -> `if False:`: KILLED, `climate current_temperature reads the measured upper floor first [got 19.0, want 20.5]`. The `if True:` form is KILLED too (TypeError).
- `entity.py:140 GUARD_OFF`, the numpy unwrap -> `if False:`: KILLED, `payload_number reads numpy.int64(7) as 7 [got None, want 7]`. Deleting the unwrap (my round-1 R1) is KILLED the same way. `if True:` is KILLED by the #1541 finite arms.
- `sensor.py:2808 CMP_BOUND`, `rate <= 0.0` -> `rate < 0.0`: KILLED, `_gap_energy_rate falls back to the contract price at a zero spot price [got 1.0, want 0.8]`.
- Advisory R2, `_payload_types` ignored: KILLED, `Compressor Starts refuses a float count [got 5.0, want None]`.
- Advisory R6, the upper/lower names swapped: KILLED, `zone_setpoint_attributes keeps upper and lower apart`.

I ran no `tests/entities.py` in this round. The round-1 entities runs (the clean run, R2 and R6) all end `ALL 2348 ENTITY CHECKS PASSED`, so another seat's `pkill` cannot have faked a kill in them.

## No new surviving site

- At 98d33ce03, `mutation` (117629788092) is red only on the same three `ADDED UNPINNED` sites. Its pin job reads `PIN KILLED: 3 pinned, 0 left unpinned`.
- Autofix delta 98d33ce03..6f6aa4e48: three files under `killed_by/` (climate `current_temperature GUARD_OFF d1cf25b6` killed by finite_boundary, `payload_number GUARD_OFF 6821a53f` killed by finite_boundary, `_gap_energy_rate CMP_BOUND 6c88eaac` killed by entities). They are kill-only, with no survivor_triage.
- At 6f6aa4e48 both `mutation` runs (117635958778, 117635972463) are success. They print no `ADDED UNPINNED` and no INCONCLUSIVE, and they read `4255 unpinned ... 4341 at the ratchet base c09d61dc9`; the null control survived every driver. All 72 check-runs at 6f6aa4e48 concluded success or skipped.

## Body

- Carry: names R10-ARCH-SHAPES via #2380, and the text is on origin/main.
- Class count: "35 sensor classes" under a stated rule (37 including the two private bases), which matches my probe's 35.
- Census: re-taken with the head's test at both ends, base 42 over 37 and head 0 over 50, which matches my round-1 run. The old 31/36 is withdrawn.
- Red checks: names and answers `mutation`.
- `closingIssuesReferences` is `[2242]`.
- **I could not re-derive "ALL 22 OWNER PINS PASSED"** (the fixer's own seat driver). The arm in the tree has nine rows, and my runs print nine `(#2379)` rows. It is not load-bearing.

## Carry

The head is now the bot's pin commit 6f6aa4e48, three `killed_by` files only, and every check is green. The orchestrator's carry predicate decides whether this verdict carries to that head.
