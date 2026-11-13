Closes the class behind R10-RCA-SELFTEST-SCOPE-DRIFT (part C; part A, main re-recording mechanically, is ruled to round 11). A re-record of `tools/ci/selftest_closures.json` taken at a stale base dropped reads main measures (#3409, #3419, #3506). `record` now unions over the committed entry, and `static` refuses a table diff that drops a read the base names unless the diff deletes the path.

## Head

Measured at `a3c9c90cee39d360f6e6718026c1075782bf8b8c` (code; first parent `428c7b8673127b136d5c34d3adfaa5f5f274a205`, the reviewed head, second parent `origin/main` `50373173d486faf394b24637c177ab38b691b394`), 2026-11-13T23:32Z. This head is the reviewed head plus one merge of `origin/main`; `git merge-tree --write-tree origin/main HEAD` exits 0 at it. The delta is `git diff 428c7b8673127b136d5c34d3adfaa5f5f274a205 HEAD -- tools/ci/selftest_scope.py tools/ci/selftest_scope_mutants.sh` on top of main's own changes (#3557's union of `check --write`, #3531):

- `tools/ci/selftest_scope_mutants.sh` (conflict): both sides appended `scope_mutant` lines after "static skips the settle check". Resolved by union: this branch's nine (record replaces, shrink-guard x4, prune x2, unresolved base x2), then main's four (check --write bare, union list entry, union flag, drift by the run's listed dir). Read back: `grep -c '^scope_mutant\|^workflow_mutant\|^wrapper_mutant'` holds every label from both parents.
- `tools/ci/selftest_scope.py` (auto-merged, then edited): the merge carried two unions of one concept, this branch's `union_entry` (`record`) and main's `union_entries` (`check --write`). `union_entries` now maps `union_entry` over the measured steps, so both writers union by one rule. `union_entry` reads a kind the measurement lacks as empty (`new.get(k, ())`), as main's did: with `new[k]` the self-test raised `KeyError: 'git'`. One behaviour moves for `check --write`: a probe that is also a listed file is dropped, which `write_table`'s compaction already does on write. Main's two union mutants retarget `union_entry`'s lines ("the union drops a committed list entry", "the union drops a committed flag") and are refused below.
- `tools/ci/selftest_closures.json` auto-merged with no conflict and no hand edit: main's re-recorded table (#3557) at this head, so it is not re-derived here. `python3 -I tools/ci/selftest_scope.py static` reads it (below).

The generated scope-line block is left out of this body as before.

## Review scope

Round 3 repairs the round-2 block (`ef7e3373e7`, introduced-red) and nothing else: `git diff ef7e3373e7 ac5ca58c09` (two files, `tools/ci/selftest_scope.py` and `tools/ci/selftest_scope_mutants.sh`, 48 insertions, 2 deletions).

- Cause: under a pull_request event `GITHUB_BASE_REF=main` is set, and the fresh-table fixture is a scratch repository with no `origin/main`; `table_base` now reports `UNRESOLVED base origin/main`, adding a line to `static`. Fix at the cause: `self_test` pops `GITHUB_BASE_REF` and `SELFTEST_BASE` from `os.environ` for the whole run (`_self_test` is the old body) and restores them after, so no fixture call, old or new, sees the caller's selectors. `main`'s `--self-test` branch maps a self-test that returned nothing to rc 1.
- Survivors of the diff mutation run (below) that were real holes got a check each: `D/**` slice in `shrink_drops`, an undiffable base in `shrink_gaps`, a missing table in `shrink_drops`, and the prune CLI over an unreadable table (rc 1, names UNREADABLE).

## Mutation proof

`sh tools/ci/selftest_scope_mutants.sh` at this merged head: 35 mutants (rule: the `== ` lines it prints; 31 at the reviewed head plus main's four), 35 refused, no `NOT REFUSED` or `MUTANT NOT APPLIED` line, ending `SELFTEST-SCOPE MUTANTS: every mutant refused`, rc 0. It first runs the baseline self-test with the caller's environment, then exports `GITHUB_BASE_REF=main SELFTEST_BASE=nonesuch` and runs the baseline again and every mutant under them. Added in round 3, with the check each fails:

- "the self-test leaks the caller's base selectors" (`held = {}`, the environment control removed): FAIL `static, ids and select over a fresh table`, 1 failed. This is the mutant the brief asked for.
- "the self-test wrapper returns nothing": rc 1 through `main`'s int guard.
- "a D/** item read as a slice off by one": FAIL `shrink_drops: a D/** item whose directory the diff emptied is exempt, one with a survivor is not`
- "an undiffable base passes the shrink guard": FAIL `shrink_gaps: a base the repository cannot diff against is refused, not passed`
- "the shrink guard judges a missing table": TypeError, refused.
- "prune goes on over an unreadable table": TypeError, refused.

`python3 tools/audit/seat/mutant_run.py --diff $(git merge-base origin/main HEAD)...HEAD --cmd 'python3 tools/ci/selftest_scope.py --self-test'` at the head: 43 survivors (47 before this round's checks). Triage:

- 37 are `STMT_DEL`/`CALL_DEL` of a `ck(...)` assertion or fixture-setup line inside the self-test body. Deleting an assertion cannot redden a suite that does not pin its own tally; equivalent by construction. Each assertion's rule has its own named mutant above or in the script.
- `816` `split("\t", 2)`: equivalent, a `--name-status` row of a path without a tab splits to the same two parts. `817`/`818` (untouched-table skip): equivalent, an untouched table compares equal to itself (round 2's `table-untouched-skip-removed`). `1623` and `1680`: constants in a fixture's entry and a fixture git wrapper's `check=`; no behaviour differs. `1800` rc 2 vs 1 on a self-test returning nothing: both nonzero, equivalent.
- CLI/`main()` branches: `record`, `prune` (unknown drop, unknown step, unreadable table, held drop), `check`, `select`, `static`, `ids`, unknown command (rc 2) and `--self-test` are each driven by a check; none of the 43 is on one.

## Both environments

At this merged head, unset: `selftest_scope self-test: 148 checks, 0 failed` (145 at the reviewed head plus main's checks). At the reviewed head `428c7b8673`: `python3 -I tools/ci/selftest_scope.py --self-test`, unset: `selftest_scope self-test: 145 checks, 0 failed`. With `GITHUB_BASE_REF=main` exported: `selftest_scope self-test: 145 checks, 0 failed`. With `GITHUB_BASE_REF=main SELFTEST_BASE=nonesuch`: the same (144 checks, 0 failed measured before the last check was added; 145 after). At `ef7e3373e7` the first of those printed 141 checks, 1 failed.

## Null control

- Shrink guard over history: the reviewer's driver `evidence/null.py` of af9e2248ef (sha1 0c95c32d4cfb257105e1d2b3258754cf617a13b9) with this head's `selftest_scope.py`, over the merges `git log --first-parent --merges --format=%H ba6fd7e8b^..3b9749dac5 -- tools/ci/selftest_closures.json` lists (16 listed, 16 printed). It refuses exactly #3409 (3 lines), #3419 (5) and #3506 (8) and passes the other 13, #3507 and #3535 among them. That matches round 1, because `shrink_gaps` is unchanged by this round. The exemption null (deletion exemption mutated out, so #3507 is refused with 2 lines) is the round-1 figure. The exemption code is untouched in this diff, and mutant "the shrink guard exempts nothing deleted" still kills it.
- The unresolved base, on this checkout: `SELFTEST_BASE=origin/main python3 -I tools/ci/selftest_scope.py static` prints `114 gated step(s), 0 problem(s)`, rc 0. With `SELFTEST_BASE=refs/heads/no-such-base` it prints `UNRESOLVED base refs/heads/no-such-base: ...` and `1 problem(s)`, rc 1. With neither variable set (first-parent fallback) it prints `0 problem(s)`, rc 0.

## Figures

- `python3 -I tools/ci/selftest_scope.py static` with `GITHUB_BASE_REF=main`: `114 gated step(s), 0 problem(s)`, rc 0.
- `PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh` once, last, at this merged head: `PRE-PR: a3c9c90cee39d360f6e6718026c1075782bf8b8c ... rc=0` (merged structure ratchet passed, ci predict no red, pr-body 0 errors, ancestry reds answered); `selftest_scope.py --self-test` 148 checks, 0 failed; `selftest_scope_mutants.sh` ends `every mutant refused`, rc 0; `GITHUB_BASE_REF=main selftest_scope.py static` 114 gated steps, 0 problems, rc 0.

## Brief carries

The group's five roster carries (by array position), each answered at this head:

- Carry 0 (beatd and review-packet are unions of two recordings, so a re-record must union): built in round 1. `record` unions over the committed entry (`union_record`), and after this merge `check --write` unions by the same `union_entry`. The R10-NUDGE-RETIRE instruction is under the forward-carry heading below.
- Carry 1 (`record` replaces rather than unions): built in round 1 (`union_entry`/`union_record`), pinned by mutant "record replaces the committed entry again".
- Carry 2 (re-record beatd and review-packet twice and union): superseded by the union `record` and the `prune` CLI. Routed to R10-NUDGE-RETIRE under the forward-carry heading below.
- Carry 3 (`git` entry `?` dropped from three steps): restored by the union. The shrink guard refuses any `git` item a diff drops, and no deletion exempts one (check "a git item or a flag is never exempt by deletion").
- Carry 4 (tests/entities.py not runnable on the reviewer's seat): an environment fault, with no finding on the head and nothing to build.

## Red checks

None owed: no check in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints was red on a commit of this branch at a read this seat made. Named anyway: `governance / instrument-self-tests` was red at `ef7e3373e7` (job 131898295736, `selftest_scope self-test: 141 checks, 1 failed`, mutants `BASELINE RED`), outside that set. Cause: `GITHUB_BASE_REF=main` under a pull_request event against a scratch fixture with no `origin/main`. Cheaper detector: `python3 -I tools/ci/selftest_scope.py --self-test` with `GITHUB_BASE_REF=main` exported, seconds locally; the mutants script now exports it itself, so its baseline covers the case.

The relay's prepr refusal `FIXTURE VACUOUS: window cache [--stats --window-cache did not take commit-to-PR map and per-PR reads from the file]` is not this branch's: the branch does not touch `tools/policy/policy_lint.mjs` (`git diff 50373173d486faf394b24637c177ab38b691b394 HEAD -- tools/policy/policy_lint.mjs` prints nothing), and on this seat `node tools/policy/policy_lint.mjs` (the default run, whose `assertAcceptance` holds that fixture) exits 0 with `FIXTURE ok: 93 error(s) hold 276 pins across 12 check classes` both at `origin/main` 50373173d4 and at this head. Neither end reproduces it, so it reads as the relay seat's environment (the fixture spawns `--stats --since <mainRef()>` children); not repairable from this diff. Carry: dismissed: not reproducible at main or at this head; policy_lint.mjs untouched by the branch

## Forward-carry

dev/programme/rosters/wave-r10-groups.json, group R10-NUDGE-RETIRE: after this change a re-record keeps every read. So a group that retires or moves a file the table names (beatd and review-packet read it, in two different recordings) removes the read with \`python3 -I tools/ci/selftest_scope.py prune --step ID --drop files:PATH\` for each affected step, instead of re-recording twice. The shrink guard accepts the removal only for a path the same diff deletes. Re-measure each affected step's entry at its own merge base. Carry: R10-NUDGE-RETIRE (supersedes Carry 0, item cf5fef06)

## Friction

none
