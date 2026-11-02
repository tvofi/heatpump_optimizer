R10-OPENER-REUSE part 1 (issue #3123, instrument): `tools/audit/seat/open_driver.py`, the open arm of the session-local opener as a tracked instrument. It resolves part topics to their roster group (P363), orders by default class with a critical-path floor and prints STARVED (P350), and marks a (topic, sha) seen only on rc=0, retrying with backoff and printing OWED (the driver half of the seen-on-rc=0 carry). Repair round 2 answers the round-1 block: the `live` skip is pinned, and `World.launch` no longer builds shell text from a topic. The roster group holds 10 carries; this part builds indices 4 (driver half), 7, 8, 9 and names the rest below.

Refs #3123: the group stays open until its next part lands.

## Head

0321068b25ff8938cbbdad9f3800a8b611556e77, measured with `git rev-parse HEAD`. It merges forward from the previous handoff 03f6ebbe8 and the earlier merge of origin/main 8f286293b (commit 91e4f39ff); origin/main was still 8f286293b when `tools/pr/prepr.sh` last ran, so no second merge and no second prepr run was needed for main's movement, and `git merge-tree --write-tree origin/main HEAD` reports no conflict.

## Mutation proof

`python3 dev/audit/harnesses/r10_open_driver_mutants.py` applies one replacement per mutant to a copy of `tools/audit/seat/` and runs the copy's `open_driver.py --self-test`; M0 (nothing mutated) prints `failed=0` and all 16 mutants die:
- M-exact 10, M-body 3, M-landed 1, M-omitlast 1, M-crit 2, M-seen 4, M-starved 1, M-backoff 3 (round 1, unchanged).
- M-live (`elif topic in runs` -> `elif False`): fails `live run: one launch over two passes` and `live run: SKIP ... live logged` (2). At round 1 the same mutant left the self-test green.
- M-launch (the topic, state directory and opener pasted back into the `bash -c` text): fails 2 checks, the hostile-topic rows (the injected marker file and the slash topic's `.rc`).
- M-bo-base (300 -> 600), M-bo-max (7200 -> 14400): 1 check each, `backoff schedule: 5 min, doubling, 2 h cap`.
- M-head4, M-headall (`body_head` reads four lines / the whole body): 1 check each, `body_head: first three lines of BODY.md`.
- M-first (a later board line wins): `parse_board: one per topic, the first line wins`. M-triageB (drop the R10-TRIAGE-B fallback): `triage falls back to R10-TRIAGE-B<M>`.
The harness aborts on a pattern that does not occur exactly once. The round-1 reviewer's probes (`live_probe`, `launch_probe` in verdict/3164) were red at 709f438c0: two live passes launched twice, and `z$(touch${IFS}INJECTED)` created `INJECTED`.

## Null control

The clean tree passes every new row: `python3 -I tools/audit/seat/open_driver.py --self-test` prints `open_driver self-test: 66 checks, 0 failed`. Nulls: `null: triage with neither group` (no group opens), `null: body_head of a missing body is empty`, and `launch: no topic executed as shell code` (no `INJECTED` file anywhere under the scratch tree). The hostile-topic fixture drives `World.launch` with a dummy `open_pr.sh` in a scratch directory and a state directory containing a space, for the topics `r10-a;touch INJECTED`, `z$(touch${IFS}INJECTED)`, `a/b` and `r10-plain`: each must write its `.rc` with 0, deliver the topic as one argument and write its log. Earlier nulls (record topic, `r10-foo-2`, `r10-roster-ops-3`, namesake prefix, empty board, `handoff-update` line, STARVED at 1 h 50 min) are unchanged. The fixer's tree at origin/main has no `open_driver.py`, so every row fails there by absence.

## Figures

- `python3 -I tools/audit/seat/open_driver.py --self-test`: prints `open_driver self-test: N checks, 0 failed`.
- `python3 dev/audit/harnesses/r10_open_driver_mutants.py`: `RESULT mutants=16`, `RESULT survived=0`.
- `python3 tests/structure.py`: passes; no budget file touched.
- `python3 -I tools/audit/seat/selftest_wiring.py --check`: the self-test is a governance.yml step.
- Instrument scope: the self-test now drives the git layer (`World.tips`, `World.landed`, `World.body_head`) against a throwaway bare origin and `World.launch` against a scratch directory with a dummy opener. `roster_lib.show_roster` on the live roster and the real `open_pr.sh` are not driven.

## Red checks

none

## Forward-carry

The roster numbers its carries 1 to 10 (zero-based index plus one):
- Carry 5 (seen only on rc=0, backoff, OWED line): built in the driver; the tick printing the OWED lines is the next part. Carry: R10-OPENER-REUSE part 2.
- Carry 8 (P337 open driver, open arm), Carry 9 (P350), Carry 10 (P363): built here. Carry: R10-OPENER-REUSE part 2 (the opener session and tick adopt the driver).
- Carry 1, Carry 2 (card 4: hold lifted by the no-merge-queue ruling; body-only parts): not built. Carry: R10-OPENER-REUSE part 2.
- Carry 3, Carry 4 (prepr reuse in update_pr/open_pr with row_only_checks including tests/structure.py): not built, size. Carry: R10-OPENER-REUSE part 2.
- Carry 6 (opener checkout collected, one per-PR checkout in update_pr.sh): not built. Carry: R10-OPENER-REUSE part 2.
- Carry 7 (pr_args.sh records its absolute directory at source time, P362): not built. Carry: R10-OPENER-REUSE part 2.
Not wired in this part: the opener session's use of `open_driver.py` instead of its local copy, and the tick printing `OWED open-refused` lines. The round-1 findings (backoff schedule, `body_head`, parse_board first-wins, R10-TRIAGE-B fallback, instrument note, `## Head`) are all closed in this round, none carried.

## Friction

none
