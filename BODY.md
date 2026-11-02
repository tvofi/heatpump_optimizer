R10-OPENER-REUSE part 1 (issue #3123, instrument): `tools/audit/seat/open_driver.py`, the open arm of the session-local opener as a tracked instrument. It resolves part topics to their roster group (P363), orders them by default class with a critical-path floor, and prints STARVED (P350). It marks a (topic, sha) seen only on rc=0, and otherwise retries with backoff and prints OWED. This re-cut adds a pin and nothing else: the self-test now reaps a slash topic's result, so the reap side of the slash-topic fix (`run_pass` reading `stem(t)`) can no longer be reverted with the self-test green.

Refs #3123: the group stays open until its next part lands.

## Re-cut

Round 3, a minimal re-cut that the orchestrator ruled past the three-round limit. It answers one finding, verdict/3164's block "mutation-vacuous: the reap side of the slash-topic fix (run_pass reads stem(t).rc) survives reversion with the self-test green". The diff since the previous code head is one self-test row pair in `tools/audit/seat/open_driver_selftest.py` and three mutants in `dev/audit/harnesses/r10_open_driver_mutants.py`. Production code is unchanged. The round history is deleted.

## Head

The code head is `3de2926c6e407a05539b15081c4fb655580353b6`, measured with `git rev-parse HEAD`. Its one parent is the PR head `cee9f6f446c86e8c27b0e88d3193f8030c4c1726`, and `handoff/r10-opener-reuse` (0321068b2) is an ancestor, so the handoff push is a fast-forward. origin/main is at `8fcaf47e1d6989b6c5f2a053aaa0f2b79c24067a`, and `git merge-tree --write-tree origin/main HEAD` exits 0 with no conflict, so main is not merged in, as the brief rules. main did not move between my `tools/pr/prepr.sh` run and the handoff, so no second run was needed. The new handoff head is this code head.

## Mutation proof

Two harnesses, both run at the head with nothing mutated (the null control) and with each mutant applied.

1. `python3 dev/audit/harnesses/r10_open_driver_mutants.py` applies one exact replacement per mutant to a copy of `tools/audit/seat/` and runs the copy's `--self-test`. M0 prints `failed=0`. All 19 mutants are killed (`RESULT survived=0`). The three new ones:

| side | mutant | the line reverted | self-test checks that go red |
|---|---|---|---|
| open | M-open-stem | `rc = d / f"{stem(topic)}.rc"` -> `f"{topic}.rc"` in `World.launch` | `launch 'a/b': rc file written with 0`, `slash topic reaped: RESULT a/b rc=0 with its log's reason`, `slash topic reaped: seen, not reopened` (3) |
| reap | M-reap-stem | `rcf = d / f"{stem(t)}.rc"` -> `f"{t}.rc"` in `run_pass` | `slash topic reaped: RESULT a/b rc=0 with its log's reason`, `slash topic reaped: seen, not reopened` (2) |
| reap (log) | M-reap-log | `reason(d / (stem(t) + '.log'))` -> `(t + '.log')` | `slash topic reaped: RESULT a/b rc=0 with its log's reason` (1) |

At the previous head cee9f6f44 the same three mutants give these results: M-open-stem fails 1 check (`launch 'a/b': rc file written with 0`), while M-reap-stem and M-reap-log stay green at `66 checks, 0 failed`. That is the vacuity the block names.

The other 16 mutants are unchanged from the previous round and all are killed. M-launch puts the old `bash -c` interpolation back. It fails `launch 'r10-a;touch INJECTED': rc file written with 0` and `... topic arrives as one argument`, and then the self-test crashes with FileNotFoundError at that topic's `log written` read. The mutant dies with rc=1, but the rows after that point are not evaluated under it.

2. The finder's harness. I ran verdict/3164's `evidence/reap_probe.py` (git blob 56aca252a7976352174c0a839f2e74e1a8acd12b) and `evidence/launch_probe.py` (blob a0baa3cc569719d90ad09bad1d223b7a29ce98a3) against a copy of `tools/audit/seat/` at each end:

| tree | self-test | reap_probe | launch_probe |
|---|---|---|---|
| cee9f6f44, M0 | 66 checks, 0 failed | failed=0 | checks=30 failed=0 |
| cee9f6f44, M-reap-stem | 66 checks, 0 failed (survives) | failed=1 (`FAIL a/b SKIP a/b 44444444 live`) | failed=0 |
| head, M0 | 68 checks, 0 failed | failed=0 | checks=30 failed=0 |
| head, M-reap-stem | 2 failed, rc=1 (killed) | failed=1 | failed=0 |
| head, M-open-stem | 3 failed, rc=1 (killed) | failed=1 | failed=3 (`topic='a/b' rc_file_0=False` per state dir) |
| head, M-reap-log | 1 failed, rc=1 (killed) | failed=0 | failed=0 |

At every row the self-test and the finder's probes agree on the slash-topic mutants, with one exception. The reap_probe checks only `RESULT a/b 44444444 rc=0` and `seen`, not the reason text, so it does not see M-reap-log. The new self-test row also asserts the reason (`opened`, read from the topic's stemmed log), and that is what kills M-reap-log.

## Null control

The unmodified head passes every row: `python3 -I tools/audit/seat/open_driver.py --self-test` prints `open_driver self-test: 68 checks, 0 failed`. The new rows run a slash topic `a/b` through `run_pass` with a world whose `launch` is the real `World.launch` (a dummy `open_pr.sh` that prints `opened`, and a state directory containing a space) and whose `alive` is the real `World.alive`. Each pass checks something different:
- Pass 1 launches the topic.
- Pass 2 must log `RESULT a/b 44444444 rc=0 opened`, so the reap reads the stemmed `.rc` and the stemmed log.
- Pass 3 must print exactly `SKIP a/b 44444444 seen` and launch nothing more.

The finder's reap_probe at the head prints `ok   a/b RESULT a/b 44444444 rc=0 opened | SKIP a/b 44444444 seen | SKIP a/b 44444444 seen` and `RESULT reap_probe failed=0`, so a slash topic's result is reaped.

## Unpinned sites

`tools/pr/prepr.sh` step 6d lists none for this diff. The `tools/` sites the open driver adds are pinned by the in-tree mutant harness `dev/audit/harnesses/r10_open_driver_mutants.py` (19 mutants, 0 survived), because `mutation-autofix` mutates `custom_components/` only.

## Figures

- `python3 -I tools/audit/seat/open_driver.py --self-test` prints `open_driver self-test: N checks, 0 failed`.
- `python3 dev/audit/harnesses/r10_open_driver_mutants.py` prints `RESULT mutants=19` and `RESULT survived=0`.
- `python3 tests/structure.py` prints STRUCTURE RATCHET PASSED. No budget file is touched, and no figure moved beyond the self-test's check count and the harness's mutant count.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out` (tests/entities.py, tests/harness_headers.py), and `tests/run.sh` with `GATE_SCOPE=auto` is green.
- Instrument scope: the self-test drives the git layer against a throwaway bare origin, and `World.launch` and `World.alive` against a scratch directory with a dummy opener. It does not drive `roster_lib.show_roster` on the live roster or the real `open_pr.sh`.

## Red checks

none. `python3 tools/audit/seat/merge_train.py classify cee9f6f446c86e8c27b0e88d3193f8030c4c1726 --pr 3164` reads the whole paginated check-run set at the PR head and prints `GREEN ... pending: none red: none`. The new code head has no check runs until it becomes the PR head.

## Forward-carry

The roster `dev/programme/rosters/wave-r10-groups.json` holds the group's carries, numbered 1 to 10:
- Carry 5 (seen only on rc=0, backoff, OWED line): built in the driver. The tick that prints the OWED lines is the next part. Carry: R10-OPENER-REUSE part 2.
- Carry 8 (P337 open driver, open arm), Carry 9 (P350), Carry 10 (P363): built here. Carry: R10-OPENER-REUSE part 2 (the opener session and tick adopt the driver).
- Carry 1, Carry 2 (card 4: hold lifted by the no-merge-queue ruling; body-only parts): not built. Carry: R10-OPENER-REUSE part 2.
- Carry 3, Carry 4 (prepr reuse in update_pr/open_pr with row_only_checks including tests/structure.py): not built, size. Carry: R10-OPENER-REUSE part 2.
- Carry 6 (opener checkout collected, one per-PR checkout in update_pr.sh): not built. Carry: R10-OPENER-REUSE part 2.
- Carry 7 (pr_args.sh records its absolute directory at source time, P362): not built. Carry: R10-OPENER-REUSE part 2.
- verdict/3164 finding: `stem()` maps `/` to `%2F` without escaping `%` first, so `a/b` and `a%2Fb` share one `.rc`. A topic named `open-driver` would also overwrite the driver's own log. Not touched in this minimal re-cut, and not yet in the roster entry: the brief allows no other change, so the roster op (`dev/programme/rosters/wave-r10-groups.json`) is the orchestrator's. Carry: R10-OPENER-REUSE part 2.
- verdict/3164 finding: the hostile-topic `log written` read is unguarded, so M-launch crashes the self-test instead of reporting each row. The mutant is still killed, and its figure is corrected above. Like the finding above, it is not yet in the roster entry (`dev/programme/rosters/wave-r10-groups.json`). Carry: R10-OPENER-REUSE part 2.

## Friction

none
