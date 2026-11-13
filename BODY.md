Closes the class behind R10-RCA-SELFTEST-SCOPE-DRIFT (part C; part A, main re-recording mechanically, is ruled to round 11). A re-record of `tools/ci/selftest_closures.json` taken at a stale base dropped reads main measures (#3409, #3419, #3506). `record` now unions over the committed entry, and `static` refuses a table diff that drops a read the base names unless the diff deletes the path.

## Head

Measured at `6a1966196c0e605653bccce7ccfdbfdffd9fda37` (code; parent `552638f8dc3a1c7f270448163d44df992c62dac2`), `origin/main` 5288db5dad at 2026-11-13T12:28:26Z. `git merge-tree --write-tree origin/main HEAD`: rc 0, no conflict, so no main merge.

## Review scope

Round 2 repairs the round-1 block (`af9e2248ef`, mutation-vacuous) and nothing else: `git diff 552638f8dc3a1c7f270448163d44df992c62dac2 6a1966196c0e605653bccce7ccfdbfdffd9fda37` (two files, `tools/ci/selftest_scope.py` and `tools/ci/selftest_scope_mutants.sh`).

- Survivors (a) and (b): the self-test now drives `main(["prune", ...])` on a fixture table in the throwaway repo. A held drop writes the table less exactly that read (`files:f2`, `objects:`; `index`, `dirs` and step `b` unchanged). A call with one held and one unknown drop, and a call on an unknown step, both return rc 1 and name the drop, and the file stays byte-identical. The mixed call is deliberate: with `if False:`, the held drop gets written whatever format the file was in.
- Survivor (c): `shrink_drops` gets a fixture where a base probe `t/q` is kept by a head that lists the directory `t`. Its null is the same head listing `u`, which is refused once.
- Fail-open: `table_base` now returns `(revision, problem)`. A named base (`SELFTEST_BASE`, or `origin/$GITHUB_BASE_REF`) that does not resolve returns the problem `UNRESOLVED base <name>: ...`, and `static` prints it as a problem line (rc 1) instead of running `shrink_gaps(root, None)`, which passes. With no base named, the first-parent fallback is unchanged. Alternative considered and not taken: raising from `table_base`. That would put an exception path into `static`'s problem-list idiom for one case. A tuple keeps every refusal as a printed line.

## Mutation proof

`sh tools/ci/selftest_scope_mutants.sh` at the head: 25 mutants (rule: the `== ` lines it prints), each `self-test rc 1`, ending `SELFTEST-SCOPE MUTANTS: every mutant refused`, rc 0. The baseline (unmutated) self-test it runs first passes. Added this round, with the check each one fails:

- "the shrink guard keeps no probe by its listed directory" (`or any(a in dirs for a in _ancestors(x))` deleted): FAIL `shrink_drops: a probe whose directory the head lists is kept, ...`
- "prune writes nothing" (`write_table(root / TABLE, entries, root)` deleted): FAIL `prune: a held drop writes the table, less exactly that read`
- "prune accepts an unknown drop" (`if unknown:` -> `if False:`): FAIL `prune: an unknown drop or step is refused (rc 1), naming it, the table byte-identical`
- "an unresolvable named base resolves to no problem" (the problem string becomes `""`): FAIL `table_base: a named base that does not resolve is a problem, not a base` and `static: a base that does not resolve adds one problem line ...`
- "static drops the unresolved-base problem" (`[unresolved] if unresolved` -> `[] if unresolved`): FAIL on the same `static` check.

"static never runs the shrink guard" is re-anchored to the new `static` line and is still refused. A self-correction, disclosed: my first spelling of the unresolved-base mutant (`"" or (...)`) was vacuous, because it still evaluated to the problem string, and the script printed `NOT REFUSED`. It now reads `"" and (...)` and is refused.

The reviewer's own driver (`evidence/run.sh` of af9e2248ef, sha1 a2c6dee7c6e5f340d7aa72c862910185249aaa44), run at this head with the three survivors' mutations: `KILLED prune-cli-no-write`, `KILLED prune-cli-ignores-unknown` and `KILLED probe-dir-ancestor-removed`, each `141 checks, 1 failed`. Null for that driver (an identity substitution) prints `SURVIVED null-unmutated :: 141 checks, 0 failed`.

## Null control

- Shrink guard over history: the reviewer's driver `evidence/null.py` of af9e2248ef (sha1 0c95c32d4cfb257105e1d2b3258754cf617a13b9) with this head's `selftest_scope.py`, over the merges `git log --first-parent --merges --format=%H ba6fd7e8b^..3b9749dac5 -- tools/ci/selftest_closures.json` lists (16 listed, 16 printed). It refuses exactly #3409 (3 lines), #3419 (5) and #3506 (8) and passes the other 13, #3507 and #3535 among them. That matches round 1, because `shrink_gaps` is unchanged by this round. The exemption null (deletion exemption mutated out, so #3507 is refused with 2 lines) is the round-1 figure. The exemption code is untouched in this diff, and mutant "the shrink guard exempts nothing deleted" still kills it.
- The unresolved base, on this checkout: `SELFTEST_BASE=origin/main python3 -I tools/ci/selftest_scope.py static` prints `114 gated step(s), 0 problem(s)`, rc 0. With `SELFTEST_BASE=refs/heads/no-such-base` it prints `UNRESOLVED base refs/heads/no-such-base: ...` and `1 problem(s)`, rc 1. With neither variable set (first-parent fallback) it prints `0 problem(s)`, rc 0.

## Figures

- `python3 -I tools/ci/selftest_scope.py --self-test`: 141 checks, 0 failed (rule: its closing line).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, no budget touched.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: FULL` (reason: `tools/ci/selftest_closures.json` changes the gate itself, inherited from round 1's table diff). That is left to CI, not reproduced here.

## Brief carries

The group's five roster carries (by array position), each answered at this head:

- Carry 0 (beatd and review-packet are unions of two recordings, so a re-record must union): built in round 1. `record` unions over the committed entry (`union_record`). The R10-NUDGE-RETIRE instruction is under `## Forward-carry`.
- Carry 1 (`record` replaces rather than unions): built in round 1 (`union_entry`/`union_record`), pinned by mutant "record replaces the committed entry again".
- Carry 2 (re-record beatd and review-packet twice and union): superseded by the union `record` and the `prune` CLI, which this round pins. Routed to R10-NUDGE-RETIRE under `## Forward-carry`.
- Carry 3 (`git` entry `?` dropped from three steps): restored by the union. The shrink guard now refuses any `git` item a diff drops, and no deletion exempts one (check "a git item or a flag is never exempt by deletion").
- Carry 4 (tests/entities.py not runnable on the reviewer's seat): an environment fault, with no finding on the head and nothing to build.

## Red checks

none. Round 1's review classified the PR head as WAIT with "gate red: none" at every poll (`af9e2248ef` `evidence/classify.log`). No check of this branch's history was red at a read this seat made. This round made no per-commit API read, because the API quota is tight.

## Forward-carry

dev/programme/rosters/wave-r10-groups.json, group R10-NUDGE-RETIRE: after this change a re-record keeps every read. So a group that retires or moves a file the table names (beatd and review-packet read it, in two different recordings) removes the read with \`python3 -I tools/ci/selftest_scope.py prune --step ID --drop files:PATH\` for each affected step, instead of re-recording twice. The shrink guard accepts the removal only for a path the same diff deletes. Re-measure each affected step's entry at its own merge base. Carry: R10-NUDGE-RETIRE (supersedes Carry 0, item cf5fef06)

## Friction

none
