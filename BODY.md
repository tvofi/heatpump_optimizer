Hotfix: main is red on governance / instrument-self-tests (run 43337393276, job 131599549208). The drift step's `selftest_scope.py check` printed `114 gated step(s), 20 refusal(s)` where the step requires zero, because 16 entries of tools/ci/selftest_closures.json missed files, probes or dirs the run read. This re-records those 16 entries on Linux with strace and changes nothing else.

## Head

4a013ff156a4e499ec806b1ac99f2776c506e982, cut from origin/main 4869f1656b892a1aee8afc7db4dbd9feff06ad1c.

## Mutation proof

n/a: the change is a measured data file with no production line to delete. The check that goes red without it is the drift step itself (20 refusals at the cited run).

## Null control

98 of 114 entries are byte-identical to origin/main: a script comparing each entry of the old and new table prints `True` for "the entries that differ are exactly the 16 re-recorded", and `tools/pr/prepr.sh` reports claim files byte-identical and 0 failures. Method: a full `record` over all 114 steps, then only the entries whose measurement was not a subset of the committed one were replaced.

The 16: beatd, ci-predictor, cloud-dispatcher, dependency-graph-census, field-coverage, hooks-setup, open-pr, policy-lint-mutants, pr-args, prepr, review-packet, selftest-wiring, temp-or-machine-path, throwaway-git-helper, update-pr, verdict-bus. I count 16 where the cited run named fifteen plus "three more"; the sixteenth by my measure is cloud-dispatcher or temp-or-machine-path, which the log excerpt did not list.

Non-determinism, stated: a second recording of those 16 (record --step, fresh traces) was a subset of the new table for 14 steps. Two differed from the first recording: beatd (the second also opened the git index and stat'ed `.claude/**` paths) and review-packet (the first also read dev/programme/rosters/wave-r10-groups.json). Each of those two entries holds the union of both recordings, which is safe over-approximation. verdict-bus failed once under strace in the full record (its self-test passed untraced and on a rerun), so its entry is from the passing rerun. I did not reach a zero-refusal `check` over a single fresh full trace set: the CI push run on main is that measurement. If it still names beatd or review-packet, the cause is the non-determinism above.

## Figures

none

## Red checks

instrument-self-tests (drift step, run 43337393276). Which merges added the unrecorded reads: the unrecorded paths include tools/audit/seat/scorecard.py, added by the mach-scorecard group (merge 74fd1a9a49) and read by field-coverage and others, and the duty-switch design directory under docs/design, plus reads added to review-packet and the prepr family by later merges; I read the measured diff, not each merge's changed files one by one. Whether the pull-request lane could have refused them: the scoped lane runs every step only when a diff ADDS a file under tools/, and these merges changed or read files rather than adding tool files, so no step was selected whose recorded closure missed them; only main's forced FULL re-measure sees it. Cheaper detector: none that stays cheap. Selecting every step on every diff is the cost that R10-CI-SELFTEST-SCOPE removed; a per-PR strace of all 114 steps took about 30 minutes here. Recorded as a standing cost of the design, not a gap to build around.

## Forward-carry

none

## Friction

none
