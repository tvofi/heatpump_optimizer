Fix review: merge 1617c879d075c732c62c31555eedc45bbed7f38c

bus-nonce: 5862665690362c9092f6f8ea456c63f3
pending-ci: gate

Round: second (delta over the reviewed head 680f34d3d275ec45143a7f30b8cf7953c73e6911, per the packet's `## Review scope: delta`). Measured head 1617c879d075c732c62c31555eedc45bbed7f38c, which is still the PR's head.sha at the time of writing (ev/head-recheck.txt). Merge base 946eb6d2551d9968de258bc47ee27efa10e7b3ea.

## Findings

- Body figure still misstated: at the head, `python3 -I tools/ci/selftest_scope.py --self-test` prints `selftest_scope self-test: 120 checks, 0 failed` (ev/selftest.txt). The body says `110 checks`, and adds that the first body said 110 too and the review read 120. The figure does not move the verdict: 0 failed either way, and the delta touches only the table. It may differ by environment, but I cannot re-derive 110 here. Carry: dismissed: a body-only figure with no later stage to carry it; the check passes at 0 failed

## Evidence

- Previous finding (class-open, 10 seat_gen misses) is resolved. The delta `git diff 680f34d3..1617c879` touches only tools/ci/selftest_closures.json: 18 insertions, 0 deletions. No code or other file is touched (ev/review-packet.md delta).
- Union check (ev/table-union.txt): I downloaded the selftest-closures artifact 14146974190 of main push run 43675609284 (946eb6d255). For each of 117 steps and each list field, the head table equals the previous head's table unioned with that artifact. Results: `not-union fields: 0 removed: 0`, no scalar (run_sha) changed. Additions land on exactly the 10 steps the block named: field-coverage, selftest-wiring, roster-queue-runner, outside-contract, beat-job-rows, hooks-setup, merge-train, open-pr, pr-args and update-pr. Each gains seat_gen.py and seat_gen_selftest.py, except merge-train and roster-queue-runner, which gain seat_gen.py only. The head table equals the artifact exactly (`head == artifact table: True`, ev/mutants.txt). The artifact is Linux CI output, not macOS traces.
- Against the merge base's table (ev/head-vs-mb.txt): removed 0, changed scalars 0, and `seat-gen head==mb: True`. This matches the body's "nothing removed or changed" and "content identical".
- Drift replay with the head worktree's `selftest_scope.drift` and `workflow_steps`, against artifact 14146974190 (ev/drift-replay.txt). Merge-base table: 14 refusals, being the earlier 4 (policy-lint-mutants, dependency-graph-census, temp-or-machine-path, prepr) plus the 10 seat_gen lines. Previous head 680f34d3: 10. Head: 0 refusals, 0 notes. This matches the body's null control and figures.
- RESULT mutants: 18/18 killed (ev/mutants.txt). Removing each added entry from the head table brings back its own UNDER-SCOPED line.
- Newer main: main moved to 13cbe48de4 (ev/main-since-mb.txt). The commits since the merge base add 45 files, none in a new directory (ev/main-added-paths.txt). Push run 43679574156 at ef7e953e4d failed instrument-self-tests on the same step. Its artifact 14148941667, replayed (ev/drift-replay-ef7e953.txt), refuses main's table with the same 14 lines and the head's table with 0. The head table equals that artifact too. So newer merges up to ef7e953e4d add no misses. Run 43678528951 at 2d0b1c7594 was cancelled and left no artifact. Run 43680834184 at 13cbe48de4 (the v10.0.0 stamp) was still in progress, with no artifact, when this was written. It is unmeasured here.
- `selftest_scope static` at the head: `117 gated step(s), 0 problem(s)`, matching the body (ev/selftest.txt).
- Merge: `git merge-tree --write-tree origin/main 1617c879d0` at origin/main 13cbe48de4 gives rc=0 (ev/merge-tree.txt). Main's table is byte-for-byte the merge base's (`mb==main table: True`).
- VERSION, manifest and notes heading: not in the diff.
- CI: `merge_train.py classify 1617c879d0 --pr 3606` printed `WAIT 1617c879d075c732c62c31555eedc45bbed7f38c pending: gate red: none` on each of 32 runs, 05:28 to 06:02 UTC, 65 s apart (ev/classify-log.txt, ev/classify-*.txt). Hence the pending-ci line. The live head check runs (ev/head-recheck.txt) show `governance / instrument-self-tests` concluded success at the head, so the step this PR repairs is green on the PR. `tests / fast (3.14)` was still running. An early `gate` run concluded failure, which classify reads as pending with no red. `governance / delivery-status` failed and is outside `merge_train.py owed-reds` (ev/owed-reds.txt), so no answer is owed. The body's `## Red checks` names the instrument-self-tests red and answers it, which is unchanged from the reviewed round.
- No finder's harness is committed for this class (packet: none named). The replays are my own script calling the builder's `selftest_scope.drift`, so they are the builder's instrument, not the finder's.
- Forward-carry: unchanged from the reviewed head. The packet's carry_audit routes R11-INTAKE-R10-RESIDUE (1 routed, 0 unrouted).
- Scope: delta only. The delta touches no custom_components/ code, so the review was not widened.
