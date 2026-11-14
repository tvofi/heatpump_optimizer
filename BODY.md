Closes the class behind R10-RCA-SELFTEST-SCOPE-DRIFT (part C; part A, main re-recording mechanically, is ruled to round 11). A re-record of `tools/ci/selftest_closures.json` taken at a stale base dropped reads main measures (#3409, #3419, #3506). `record` now unions over the committed entry, and `static` refuses a table diff that drops a read the base names unless the diff deletes the path.

## Re-cut

Fourth-round body replaced. Round history is dropped; every figure below is re-taken at the head named. Blocks answered: `root-cause-unrecorded` (`tests / fast (3.14)` red, answered under Red checks) and a content conflict in `dev/audit/config/bugclasses.json` with main, resolved by merge as a union (both `R10-RCA-SELFTEST-SCOPE-DRIFT` and `R10-RCA-FEATURES-WEEKEND-CLOCK` entries kept; the file parses as JSON and `git diff origin/main -- dev/audit/config/bugclasses.json` adds only this branch's entry).

## Head

Measured at `b3fd674e4d533e81aa1ef45d4ce0fec87078ad15` (merge of `origin/main` `9fdba3b8547f9762438dc19b98b310a63d34dcb1` into the PR head `df1512502349af541505b73a81a86beb4dd6f930`), 2026-11-14T15:46Z. `git merge-tree --write-tree origin/main HEAD` was run on the PR head before the merge and reported the one conflict above; the merge is the only change on the head.

## Mutation proof

`sh tools/ci/selftest_scope_mutants.sh` at this head: ends `SELFTEST-SCOPE MUTANTS: every mutant refused`, no `NOT REFUSED` or `MUTANT NOT APPLIED` line. It exports `GITHUB_BASE_REF=main SELFTEST_BASE=nonesuch` for the baseline and every mutant. Key mutants: "record replaces the committed entry again", the shrink-guard mutants, "the self-test leaks the caller's base selectors" (FAIL `static, ids and select over a fresh table`), "an undiffable base passes the shrink guard", "prune goes on over an unreadable table" (TypeError).

## Null control

- Unresolved base: `SELFTEST_BASE=origin/main python3 -I tools/ci/selftest_scope.py static` prints `0 problem(s)`, rc 0; with `SELFTEST_BASE=refs/heads/no-such-base` it prints `UNRESOLVED base refs/heads/no-such-base` and `1 problem(s)`.
- Self-test both environments: `python3 -I tools/ci/selftest_scope.py --self-test` unset and with `GITHUB_BASE_REF=main` exported, each `0 failed`.

## Figures

- `python3 -I tools/ci/selftest_scope.py --self-test`: `148 checks, 0 failed` at this head.
- `GITHUB_BASE_REF=main python3 -I tools/ci/selftest_scope.py static`: `114 gated step(s), 0 problem(s)`.
- `tools/pr/prepr.sh` run once at this head, result in the handoff message.

## Red checks

`tests / fast (3.14)` was red on #3551's head (job 132252007494). Cause: `tests/features.py` `_chg_seq` starts its default arm from the real clock, so the block is red on every Saturday and Sunday from 2026-11-14T00:00Z, on main and on every head; this diff does not touch `tests/features.py`. Fixed on main by #3578 (`R10-HOTFIX-FEATURES-WEEKEND-CLOCK`), merged into this head. The cheaper-detector answer is recorded with its cost test in `dev/audit/rca/R10-RCA-FEATURES-WEEKEND-CLOCK.md` (state (c): the nightly Kolkata step varies the zone, never the calendar day; countermeasure a nightly faketime step on the other day type, estimate 10-20 s a night; lint, frozen clock and per-PR double run refused by the cost test). Earlier: `governance / instrument-self-tests` red at `ef7e3373e7` (job 131898295736), outside the owed set; cause `GITHUB_BASE_REF=main` against a fixture with no `origin/main`; the mutants script now exports it.

## Forward-carry

dev/programme/rosters/wave-r10-groups.json, group R10-NUDGE-RETIRE: after this change a re-record keeps every read. So a group that retires or moves a file the table names (beatd and review-packet read it, in two different recordings) removes the read with \`python3 -I tools/ci/selftest_scope.py prune --step ID --drop files:PATH\` for each affected step, instead of re-recording twice. The shrink guard accepts the removal only for a path the same diff deletes. Re-measure each affected step's entry at its own merge base. Carry: R10-NUDGE-RETIRE (supersedes Carry 0, item cf5fef06)

## Friction

none
