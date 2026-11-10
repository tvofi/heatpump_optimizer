Fix review: blocked 34a9cf1251fa6046f3182a21aea60a84b477609f class-open: Dests.check issue token: a Carry to #N whose only owner is a carries-open group is accepted (Dests.__init__ owned via is_open)

bus-nonce: d8ae8ad539cffae2a80157f65d44575e

Round 1 (no earlier verdict on this PR). Measured head 34a9cf1251fa6046f3182a21aea60a84b477609f, merge base 9ecbd4f6371de662ad7fa731d22b06dc38806903; head re-read at verdict time, unchanged.

## Block

The owner-approved rule is "a carry goes to the live group owning the seam; if none exists, the producing group owns the fix". The PR routes all group-token destinations through `roster_lib.carry_receivable`, but the issue-token path of the same destination check is untouched. `Dests.check` accepts `Carry: #N` when `owns(n)`, and `Dests.__init__` (carry_audit.py:374-376) fills `owned` from every `roster_lib.is_open` group, carries-open and refuted ones included. The body lists `Dests.__init__ (is_open)` under "Not destination readers" as "issue ownership". Measurement refutes that: it is the destination test for `#N`.

Measured at the head, with `--roster-ref origin/handoff/audit-r10-roster` (5076c9e6caad07d561929555bba5078a14fde713) and live issue state (ev/issue_bypass_head.txt):
- `Carry: R10-REVIEW-ENUMERATE`: BAD-DEST, refused by the barrier (rc 1).
- `Carry: #3313`: routed (rc 0). #3313 is open and its only owner is R10-REVIEW-ENUMERATE, which is carries-open.
- `Carry: R10-CLOSEOUT-CLEANUP`: refused (rc 1). `Carry: #2728`: routed (rc 0). #2728 is open and its only owner is that carries-open group.

My census (ev/issue_bypass_census.txt, `$HOME/rev3417/issue_bypass.py`, my own instrument, not the finder's) finds 5 issues whose owner in `owned` fails `carry_receivable`. 4 of them are open: #2505, #2728, #3313, #3314. A seat refused on the group token can re-spell the same parking as the group's issue and pass.

To repair it, `check` should refuse an issue token whose owner is a roster group that fails `carry_receivable`, unless a carry file or an O-brief owns it. `owned`/`owns` should stay as they are for `sweep --issues`. Add a failing-then-passing self-test arm and a null control (an issue owned by a live group still routes).

## Findings

- ci_predict.py's self-test is broken by this PR, and the body misfiles the seam. tools/pr/ci_predict.py:1382-1383 picks the first `roster_lib.is_open` group as "a group of the roster" that must be predicted green. Through the in-tree roster (read at origin/main) that group is R10-PREPR-CAP, at stage carries-open, which the barrier now refuses. Result: `FAIL a carry to a group of the roster is predicted green`, `ci_predict self-test: 1 failed` at the head, and `0 failed` at both the merge base 9ecbd4f63 and origin/main f0bfadeb8 (ev/ci_predict_selftest_3revs.txt). CI shows the same failure in `governance / instrument-self-tests` (job 129763664492, ev/ci_instrument_self_tests_ci_predict_tail.txt). The body lists `ci_predict.py:1383` as "planner and merge openness", but it picks a carry destination. It should pick with `carry_receivable`. This is not the basis of the block, because `governance / instrument-self-tests` is not in `merge_train.py owed-reds` (owner ruling 2026-11-09). It will turn that lane red on main once merged. Carry: R10-CARRY-SINK-BARRIER

## Evidence

- CI: `merge_train.py classify 34a9cf125... --pr 3417` printed `GREEN 34a9cf1251fa6046f3182a21aea60a84b477609f pending: none red: none` (rc 0, first run). `governance / instrument-self-tests` concluded failure. It is not in the owed-reds set (ev/owed_reds.txt), so this PR owes no `## Red checks` answer for it. The body's `## Red checks: none` is consistent with the owed set.
- Mutation proof: I ran 8 targeted mutants of my own at the head, each against the file's `--self-test` and then restored. All 8 were killed (ev/mutants.txt). The mutants were: CARRY_DEST_CLOSED = CARRY_CLOSED (roster_lib 1 failed; carry_audit 4 FAIL); sink clause dropped (carry_audit 1 failed); refuted dropped from CARRY_DEST_CLOSED (roster_lib 1 failed); `Dests.live` back to CARRY_CLOSED (carry_audit 4 FAIL); `carry_plan` back to `is_open` (roster_sync 2 failed, the two the body names); sink ignoring issues (1 failed); sink keyed on a missing `files` key (1 failed).
- I did not re-run the body's r10_roster_ops_mutants full run (K10/W6/W12/L7/L8, Y6 retired). My L7/L8-equivalent mutants (M1, M2) were killed. The Y6 equivalence argument reads sound against the write path's `appends, _`, but I did not re-derive it.
- Finder's harness: none named. The body's `dev/audit/harnesses/r10_carry_sink_barrier.py` is the fixer's own instrument, as the body says. At the body's roster ref 43495fb6 it re-derives the body's figures exactly. Base 699f4d9ef: carries-open 10 of 10, refuted 1 of 1, pending_on_accepted_closed=47. Fix 22f3ba79a: 0 of 10, 0 of 1, 0. in-progress 14 of 14 and not-started 22 of 22 at both ends (ev/harness_body_roster.txt).
- At today's roster 5076c9e6: base and merge base read carries-open 4 of 4, pending 5. Head reads 0 of 4, pending 0. The null control is flat at both ends (ev/harness_both_ends.txt).
- The brief's 116 is the count of all carries on the 10 groups. I did not re-derive it; the body says it is not the harness's figure.
- Null control: self-test arms for R10-WORK / R10-NEXT / R10-PR pass at the head. carry_audit 409 checks, roster_lib 88, roster_sync 96, all 0 failed (ev/selftests_head.txt).
- Policy scope: the edit replaces one line of finding-propagation.md ("not `carry_receivable` is none: the seam's live owner is, else the producer (tvofi 2026-11-10)") and changes "done" to "unreceivable". That is the owner-approved rule and does not widen it. The sink test (no PR, issue or fix, `files: []`) is narrower than the brief's "no PR and no live brief work". The stage set adds only carries-open and refuted to the existing CARRY_CLOSED (absorbed, done stages, refused, deferred). `rules_sync.mjs --check`: RULES-SYNC ok. `policy_lint.mjs`: fixtures ok. The owner approval is still owed at merge, as the body states.
- `git merge-tree --write-tree origin/main <head>`: rc 0, clean (ev/merge_tree.txt).
- VERSION, manifest, RELEASE_NOTES, both claim files and every `*_budgets.json` are untouched in the three-dot diff (ev/untouched.txt).
- The body's head line names 34a9cf1251fa6046f3182a21aea60a84b477609f, the head I measured.
- Archscore dS +0.0000, `STRUCTURE RATCHET PASSED`, and `ALL 2707 ENTITY CHECKS PASSED` are taken from CI's green `arch-score`, `gate` and `tests` lanes. I did not re-run them.
