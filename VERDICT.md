Fix review: blocked bb730c1eeeb63880bc42336f347f6587564a57b1 ci-red: gate failed on codeql / Analyze (python) cancelled; code review otherwise clean

bus-nonce: 6eef92437863e90da5a029d4fc524abc

## Round
Second fix-review round of #3181 (R10-CI-RUNNER-FIXES). This is a delta review at head bb730c1eeeb63880bc42336f347f6587564a57b1 against the previously reviewed head 3339aa92b6a60e6492263da1a6b6dd5efaa39b64 (verdict/3181, blocked class-open). I worked from a detached worktree with the finder's harness (verdict/3181 evidence/failed_script_regex.txt, run_sh_pin_mutants.txt and pin_replica.py). The role files under dev/governance/roles/ match between the merge base and origin/main (the three-dot diff is empty).

## Block
The required `gate` check is red at this head. Both gate runs (code 126572565490 and edit 126573967845) fail on one line only: `FAIL codeql / Analyze (python): cancelled`. Job 126550446352 started at about 11:41 and was terminated mid-analysis at 12:26:40. Its log ends with "Terminate orphan process: pid (3240) (codeql)", and the check-run output is empty. `merge_train.py classify bb730c1eeeb63880bc42336f347f6587564a57b1 --pr 3181` exited 1 with `RED ... pending: none red: gate` (ev/ci_classify.txt).
Every other check on the head concluded success or skipped (ev/check_runs.tsv, 55 check runs across all pages), including tests / fast (3.14), governance / instrument-self-tests (which runs `merge_train.py --self-test`), tests / closures, tests / coverage, tests / lane-proofs, tests / arch-instrument and both pr-contract runs. The exception is tests / nightly-status, which is inherited and answered in the body.
A cancelled analysis job is an infrastructure outcome. It is not caused by this diff, and nothing in the body needs to change. The repair is to re-run the CodeQL python job, or the whole codeql workflow, on this head and let the gate re-grade. Under the protocol a red CI cannot carry a merge verdict, so this verdict blocks on the CI state alone. The code findings below are a merge as they stand: a re-review after a green re-run needs only to confirm that classify prints GREEN at an unmoved head.

## Findings
- Follow-up: the outer `if [ "$rc" -ne 0 ]` guard at the lane report (tests/run.sh:809) is pinned by no check. `_failed_marker_self_test` lifts only from `if ended_before_summary ...` to the inner `fi`, and it sets rc=1 itself. Inverting the guard to `-eq` (mutant M8), or replacing it with `true` (mutant M9), leaves `merge_train self-test: 442 checks, 0 failed` and the entities pin replica ok (ev/mutants_head.txt). Under M8, every passing script in a lane run would print a FAILED/ENDED marker, and `culprit()` would then name passing scripts. This is not a regression: the pre-PR one-liner `[ "$rc" -ne 0 ] && echo ">>> FAILED: $label"` was equally unpinned. The cheapest repair is to widen the lifted block in `_failed_marker_self_test` to include the outer `if [ "$rc" -ne 0 ]; then ... fi`, and drive it at rc=0 as a null case that must print nothing. Carry: R10-CI-RUNNER-FIXES
- Residual: the group's first carry (the owner's "Build it now" item, plan-regain card 9: an edit run exits without holding a runner, and the code run's gate re-dispatches the body units) is still not built at this head. The body says so. It stays verbatim at carry[0] of group R10-CI-RUNNER-FIXES in dev/programme/rosters/wave-r10-groups.json on origin/main 8e90d8144, which I re-read. The orchestrator must not close the group when this PR merges. Carry: R10-CI-RUNNER-FIXES

## Evidence
- RESULT reader, finder's harness at both ends (ev/regex_harness.py, which applies the tree's own FAILED_SCRIPT literal): at 3339aa92b the ENDED line gives `[]` (ev/failed_script_regex_3339aa92.txt). At bb730c1ee it gives `['tests/entities.py']`, both bare and with a `python3 ` label prefix, and the plain FAILED line is unchanged (ev/failed_script_regex_head.txt). The one live call site is merge_train.py:2687, `scripts |= set(FAILED_SCRIPT.findall(log))` inside culprit().
- RESULT null control: the unmutated head prints `merge_train self-test: 442 checks, 0 failed`, matching the body's figure.
- RESULT mutants (ev/mutants_head.txt; each restored from a byte copy, and `git status` was clean after):
  - M1 reader reverted to `>>> FAILED: `: 1 failed (FAILED_SCRIPT names the script...). This matches the body.
  - M3 run.sh if/else reverted to the exact pre-PR one-liner (clean rerun, ev/m3_clean.diff, `bash -n` ok): 439 checks, 1 failed (the lift check). This matches the body.
  - M4 negation dropped: 2 failed. This matches the body. The entities pin replica gives FAIL [1, 0].
  - M5 FAILED dropped from SUMMARY_LINE: 1 failed. The replica gives FAIL [0, 0].
  - M6 failed-check branch prints the ENDED wording: 1 failed.
  - M7 ENDED line renamed to `>>> CRASHED:`: 2 failed.
  - M8 and M9 (outer rc guard): survive, see Findings.
  The previous verdict's Follow-up (the call site was unpinned) is settled for the if/else itself.
- RESULT class: I re-ran the body's rule, `grep -rIn ">>> FAILED\|>>> ENDED\|ENDED BEFORE"` at the head (ev/class_enum_head.txt). It returns exactly the body's list: run.sh x3, merge_train.py (the reader plus fixtures), orchestrator_tick.py (a fixture), quiet.sh:61, recorded round logs and fixtures, and two roster prose lines. A broader grep for `>>> ` prefix readers (`^>>>`, startswith) adds nothing. quiet.sh:58 runs `GATE_JOBS=1`, and run.sh:126-130 makes that serial, so the lane report never runs there, as the body says. No undispositioned reader remains.
- Delta: the three-dot diff at bb730c1ee differs from the one at 3339aa92b only in tools/audit/seat/merge_train.py, which is commit 3173cce2d (ev/delta_three_dot.diff). The two origin/main merges changed none of the PR's files.
- Pin is exercised in CI: governance.yml:943 runs `merge_train.py --self-test` in instrument-self-tests with no path filter, so a future run.sh edit meets the fixture. That job concluded success on this head.
- Not re-derived: the body's `ALL 2603 ENTITY CHECKS PASSED` and `STRUCTURE RATCHET PASSED`. CI's tests / fast (3.14) concluded success on this head and is cited as the authority. Carry: dismissed: evidence, not a finding
- Merge: `git merge-tree --write-tree origin/main bb730c1ee` exits 0, giving tree 39b7069d8 with origin/main at 8e90d8144 (ev/merge_tree.txt).
- VERSION, the manifest and RELEASE_NOTES.md are untouched. No golden fixture or claim file is in the diff (ev/three_dot_files.txt).
- Red checks besides the block: tests / nightly-status is red and inherited (it grades main's nightly). The body names it, and the diff reaches nothing it reads. The body's root-cause answer for the round-1 red (tests / fast at 241f47e62) stands unchanged from the previous verdict.
- Head: the body names bb730c1eeeb63880bc42336f347f6587564a57b1, and it is the branch tip and refs/pull/3181/head by ls-remote both at the start of the review and after CI concluded (ev/HEAD.txt).
- Instruments disclosed: ev/regex_harness.py is mine and wraps the finder's regex check. ev/pin_replica.py is the previous reviewer's, reused unchanged.
