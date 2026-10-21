Fix review: merge 5ffbaaaeb827f184ed44abd9ead267ee8e626b08

PR #2569 (R10-ROSTER-PUSH-RACE), first review of this head. Measured at 5ffbaaaeb827f184ed44abd9ead267ee8e626b08; it was still the branch head when this verdict was written (ev/head_at_post.txt). Contract: dev/governance/roles/fix-review.md from main; `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so the contract is current.

RESULT selftest_head=76_checks_0_failed                       (ev/selftest_head.txt)
RESULT selftest_failing_first_e19bda54f=82_checks_7_failed     (ev/selftest_e19bda54f_failing_first.txt; matches the body)
RESULT mutants M1=7 M2=7 M3=2 M4=1 M5=4 failed                 (ev/mutants.txt; each matches the body exactly)
RESULT reviewer_mutants M6_push_by_branch_name=self-test crashes rc 1, M7_apply_op_only_on_attempt_1=5 failed, M8_non-race_refuse->print=1 failed
RESULT finder_repro base shared: A rc=0, reported sha NOT on origin, edit lost: 6/6 (diff/same group); head: 6/6 both edits land, reported sha on origin
RESULT finder_repro base separate: A rc=2 loud 6/6; head: both land 6/6
RESULT null_control solo base=6/6 ok head=6/6 ok, 1 commit each
RESULT three_seat_shared base: A silently lost; head: 3/3 land, 3 commits (ev/reviewer_race3.txt)
RESULT fixer_harness head shared=10/10 silent_losses=0 pushes=2; head separate=10/10 clean; solo=3/3 both trees
RESULT fixer_harness base shared silent_losses=1 in 9/10 (body says 6/10); false_reports=1 in 2/10 (body: 3/10)
RESULT merge_tree origin/main e7c664856 rc=0 tree 15e2fd455 (no conflict)
RESULT VERSION/manifest/notes/claims/golden/budgets untouched
RESULT ci at head: all check runs completed; only nightly-status is red (main's scheduled lane, not this PR's)

Steps:
1. Mutation proof: I re-applied M1-M5 exactly as the body names them. Every count matches. My own mutants M6-M8 also fail: pushing by branch name again, applying the op only once, and turning the non-race refusal into a print.
2/9. No finder harness is committed. The roster brief prescribes the reproduction ("two concurrent edits in a scratch bare repo"), and r10_roster_push_race.sh is the fixer's own. I therefore built and disclose my OWN harness, ev/reviewer_race.sh and ev/reviewer_race3.sh. It interleaves deterministically: a lint stub blocks run A after its commit and before its push until rival B has landed, which is the 2026-10-21 shape, with no timing luck involved. At the base it reproduces the field defect 6/6: A exits rc 0 and prints "pushed ... at <sha>" for a sha origin does not hold. At the head both edits land 6/6, with the sha reported on origin. I also ran the fixer's harness at both ends (ev/fixer_harness_summary.txt).
3. The null control holds: solo runs add one commit, the reported one, at both ends.
6. Class: I re-ran the body's enumeration rule myself (ev/class_rule.txt). Every production push site it returns is dispositioned in the body. The hits the body leaves unnamed are self-tests or harnesses: merge_train.py:2969 is the self-test stub, ref_privacy.py:661/712 are in self_test, budget_raise_gate.py:1311 is in _end_to_end, and r9_rc_bus_fetchhead.sh and a1_dispatch_arms.sh are harnesses. Also checked: other configurations (same-group carries, a three-seat race) and callers of roster_edit (r10_tick_which_roster.py reads the worktree HEAD, not the removed local branch; the governance.yml grep still matches).
7. The body names head 5ffbaaaeb, the head I measured.
8. Not re-derivable: the body's base-shared tallies (6/10 silent, 3/10 false reports) come from a sleep-timed harness and are stochastic. My 10 runs gave 9/10 and 2/10, the same direction. I could not reproduce the exact counts and do not confirm them. The head figures (10/10 clean) re-derive exactly. The tally fix (`passed` already counts failures) is confirmed by reading check().
10. Forward-carry `n/a: <reason>`: the seat-facing change is in INSTRUMENTS.md, inside this diff. Accepted.
11. pr-contract went red at 8b0a838d4 and aff55f82f. I read the job log: carry_audit UNROUTED on the Forward-carry line in both cases. The body names the check and answers it. Both pr-contract runs at this head are green and started after the body was last edited (14:08:06Z). nightly-status is red but answered, and the diff does not reach what it reads. Cancelled runs on the superseded heads are not reds.
13. merge-tree is clean against current origin/main.
14. tests/closures.json gains one INERT-reads entry, earned by the new harness file that harness_headers reads. No budget, claim or score moved.
15. apply_op removes the duplicated dispatch; the detached worktree plus push-by-sha is the sound mechanism. No breach found.

Not re-run by me (cited from CI per step 11): the gate, mutation, harness_headers (needs voluptuous, absent here) and entities. instrument-self-tests, closures, closure-scope and mutation are green at the head. I ran these cheap checks myself: layout rc 0, structure PASSED, ref_privacy 66/0, tmp_paths 0 refused.

bus-nonce: 277db9ac1c42a10b967e4edadf5a17d4
