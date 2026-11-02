R10-OPENER-REUSE part 1 (issue #3123, instrument): `tools/audit/seat/open_driver.py`, the open arm of the session-local opener as a tracked instrument. It resolves part topics to their roster group (P363), orders by default class with a critical-path floor and prints STARVED (P350), and marks a (topic, sha) seen only on rc=0, retrying with backoff and printing OWED (the driver half of the seen-on-rc=0 carry). The roster group holds 10 carries; this part builds indices 4 (driver half), 7, 8, 9 and names the rest below.

Refs #3123: the group stays open until its next part lands.

## Head

03f6ebbe86a165bdbbd18a03e71801da2aa91c35, measured with `git rev-parse HEAD`. origin/main was ea6ae27736631e9987fe20a9b4f86ad5e8b79acb at the last prepr run; no merge was needed (`git merge-tree --write-tree origin/main HEAD` reports no conflict).

Main moved after the last prepr run (`git rev-parse origin/main` at push time differs from the base above); `git merge-tree --write-tree origin/main HEAD` reports no conflict, so per the brief it was not merged.

## Mutation proof

`python3 dev/audit/harnesses/r10_open_driver_mutants.py` applies one replacement per mutant to a copy of `tools/audit/seat/` and runs the copy's `open_driver.py --self-test`; all eight die, M0 is clean:
- M-exact (drop exact-first, P363 (i)): fails `exact wins: roster-ops-2`, `exact wins: ci-layout-p1` and others (10 checks).
- M-body (drop the body-names-group check): fails the three null rows `null: foo-2 body silent`, `null: roster-ops-3 names only itself`, `null: body names a longer name only`.
- M-landed (drop the ledger.py landed check): fails `on-main skipped`.
- M-omitlast (omitted topics sort last): fails `omitted higher classes slot before a listed instrument`.
- M-crit (no critical floor): fails 2 order rows.
- M-seen (seen on any rc): fails 4 rows including `failed open not marked seen`.
- M-starved, M-backoff: killed (1 and 3 checks).
The harness aborts on a pattern that does not occur exactly once.

## Null control

The self-test carries the nulls the carries name: `r10-record-s9-owed` logs NEEDS-TITLE; `r10-foo-2` with a body naming a different group does; `r10-roster-ops-3` whose body names only R10-ROSTER-OPS-3 does; a topic for a group absent from the roster never opens against a namesake prefix; an empty board and a `handoff-update` line start nothing; STARVED is absent at 1 h 50 min and present at 2 h 10 min; the omitted non-critical topic sorts after listed topics of higher default class. M0 of the harness (nothing mutated) prints `failed=0`. Failing test first: the self-test was written against the resolver and order contract before the mutants; the tree at origin/main has no `open_driver.py`, so every row fails there by absence.

## Figures

- `python3 -I tools/audit/seat/open_driver.py --self-test`: prints `open_driver self-test: N checks, 0 failed`.
- `python3 dev/audit/harnesses/r10_open_driver_mutants.py`: `RESULT mutants=8`, `RESULT survived=0`.
- `python3 -I tools/audit/seat/selftest_wiring.py --check`: 0 unwired, 0 index gaps (the self-test is a governance.yml step).
- `python3 tests/structure.py`: passes; no budget file touched.
- Suffix-strip rows (P363), in the self-test: r10-sav-comfort-p2 to R10-SAV-COMFORT, r10-roster-ops-2-p1 to R10-ROSTER-OPS-2, r10-prepr-cap-2 to R10-PREPR-CAP, r10-fly-train-defaults-p2 to R10-FLY-TRAIN-DEFAULTS, r10-ux-health-p3 to R10-UX-HEALTH; exact: r10-roster-ops-2 stays R10-ROSTER-OPS-2, r10-ci-layout-p1 stays R10-CI-LAYOUT-P1.
- Instrument scope: the git layer (`World.tips`, `World.landed`) is driven once against a throwaway bare origin; launching `open_pr.sh` and `roster_lib.show_roster` on the live roster are not driven by the self-test.

## Red checks

none

## Forward-carry

The roster numbers its carries 1 to 10 (zero-based index plus one):
- Carry 5 (seen only on rc=0, backoff, OWED line): built in the driver; the tick printing the OWED lines is the next part. Carry: R10-OPENER-REUSE part 2.
- Carry 8 (P337 open driver, open arm), Carry 9 (P350), Carry 10 (P363): built here. Design choices: a stripped match uses the generated title `<GROUP> (part <N>): <topic words>`; `triage-s<N>-batch<M>` resolves to R10-TRIAGE-S<N>, else R10-TRIAGE-B<M>, checked against the roster; an omitted topic slots after the last listed topic of equal or higher default class within its critical or non-critical part; STARVED age is now minus the handoff commit's ct. Carry: R10-OPENER-REUSE part 2 (the opener session and tick adopt the driver).
- Carry 1, Carry 2 (card 4: hold lifted by the no-merge-queue ruling; body-only parts): not built. Carry: R10-OPENER-REUSE part 2.
- Carry 3, Carry 4 (prepr reuse in update_pr/open_pr with row_only_checks including tests/structure.py): not built, size. Carry: R10-OPENER-REUSE part 2.
- Carry 6 (opener checkout collected, one per-PR checkout in update_pr.sh): not built. Carry: R10-OPENER-REUSE part 2.
- Carry 7 (pr_args.sh records its absolute directory at source time, P362): not built. Carry: R10-OPENER-REUSE part 2.
Not wired in this part: the opener session's use of `open_driver.py` instead of its local copy, and the tick printing `OWED open-refused` lines.

## Friction

none
