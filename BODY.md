Closes the class behind R10-RCA-SELFTEST-SCOPE-DRIFT (part C; part A, main re-recording mechanically, is ruled to round 11). A re-record of `tools/ci/selftest_closures.json` taken at a stale base dropped reads main measures (#3409, #3419, #3506). `record` now unions over the committed entry, and `static` refuses a table diff that drops a read the base names unless the diff deletes the path.

## Head

Measured at `82f3cf9759a1184753dd414e0499ce17b331c24d` (code), `origin/main` 0723540391 at 2026-11-13T09:02:10Z.

## Mutation proof

`sh tools/ci/selftest_scope_mutants.sh` prints `SELFTEST-SCOPE MUTANTS: every mutant refused`, now including four new mutants, each with self-test rc 1: "record replaces the committed entry again" (`entries[sid] = m`, restoring replace semantics); "the shrink guard exempts nothing deleted" (`or True`, the deletion exemption removed); "the shrink guard exempts every drop" (`gone(x)`, the exemption inverted); "static never runs the shrink guard". The failing tests first: `union_record`/`prune_entries`/`shrink_drops`/`shrink_gaps` checks, plus `static` over a fixture repo refusing a dropping commit.

## Null control

Guard over every first-parent merge that touched the table, base = the merge's first parent, head = the merge (driver: a scratch script calling `selftest_scope.shrink_gaps` in a detached checkout of each merge). In the window ba6fd7e8b0^..f47250150a it refuses exactly #3409 (3 lines: beatd), #3419 (5: open-pr, pr-args, prepr, update-pr) and #3506 (8) and passes the other 12 of 15, including #3507, whose deleted `dev/programme/carries/carry-1774.json` makes it exempt. Null control for the exemption: with the deletion exemption mutated out, the same run refuses #3507 as well (2 lines) and still the three. Later merges up to the base: #3535 (the RERECORD merge) passes, no later merge touched the table. The run did not skip: 16 merges listed by `git log --first-parent --format=%h ba6fd7e8b^..origin/main -- tools/ci/selftest_closures.json`, 16 printed.

#3514 (live conflict in the table alone): not measured here, its branch was not read. The guard would not have prevented a textual merge conflict; it prevents the silent half of the class, a resolution that keeps the wrong side and drops reads. The union record shrinks the conflict surface only for re-records.

## Figures

- `python3 -I tools/ci/selftest_scope.py --self-test`: 0 failed.
- `python3 -I tools/ci/selftest_scope.py static` with `SELFTEST_BASE=origin/main`: 0 problem(s) (the re-record of selftest-scope and selftest-scope-mutants by `record --step` on Linux with strace, unioned; its diff only re-collapses entries into `D/**`).
- `python3 tools/audit/fold_ledger.py check`: 0 violation(s) with the new class and its RCA indexed.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, no budget touched.

## Red checks

none

## Forward-carry

dev/programme/rosters/wave-r10-groups.json, group R10-NUDGE-RETIRE: after this change a re-record keeps every read, so a group that retires or moves a file the table names (beatd and review-packet read it, two differing recordings) removes the read with \`python3 -I tools/ci/selftest_scope.py prune --step ID --drop files:PATH\` for each affected step, not by re-recording twice; the shrink guard accepts the removal only for a path the same diff deletes. Re-measure each affected step's entry at its own merge base. Carry: R10-NUDGE-RETIRE (supersedes Carry 0, item cf5fef06)

## Friction

none
