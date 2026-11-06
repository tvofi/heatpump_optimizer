Fix review: merge c94edc5614b94f042dbb9a1196aa594be294534f

bus-nonce: 5dbef69b2befe7299bbefb63c2cc5d88

Round 2. I measured head `c94edc5614b94f042dbb9a1196aa594be294534f` from a detached checkout. Its merge base is `30638cf0c8a7114019682f87051a4a282d2981ff`; origin/main is `4b7e1770ba81`. The roles diff from the merge base to origin/main is empty, so fix-review.md is current. Every round-1 finding is settled at this head, and the repair introduces no new finding that blocks.

## Evidence

- Round-1 block (instrument-broken): settled. `python3 -I tools/audit/seat/r10_roster_ops_mutants.py --self-test` prints `231 checks, 0 failed` at the head (ev/ops_selftest_head.txt). The L4 anchor `CARRY_CLOSED = CLOSED_STAGES` occurs once in roster_lib.py (ev/anchors.txt). The full plant run at the head ran all 75 plants, with none NOT RUN, and printed `plants: 75, without a FAIL line: ['C6']` (ev/ops_plants_head.txt). That matches round 1's base result (75 plants, C6 the only plant without a FAIL line), so this PR adds no survivor.
- Round-1 S09 anchor rot: settled. The S09/S09b anchor occurs once in handover_prompt.py at the head (ev/anchors.txt). `python3 -I dev/audit/harnesses/r10_seat_selftests_mutants.py S09 S09b` prints `S09 KILLED`, `S09b KILLED`, `RESULT survivors=0` (ev/seat_mutants_S09.txt).
- Round-1 surviving mutant (handover_prompt.in_flight reverted to DONE_STAGES): settled. That mutant is exactly S09b, and it is now killed by the new R9-D absorbed fixture row. handover_prompt's self-test is at `17 checks, 0 failed`.
- Round-1 body numbering: settled. The body's carries 1-9 map one to one onto the roster's 1-based `carry` list for R10-ROSTER-READ-SWEEP at handoff/audit-r10-roster `c516cf0f6620` (ev/roster_carries.txt). Carry 5 (RosterNotFound) is listed as landed, and the replan.py deviation from carry 1 is stated. The PR title still says "carries 1-4" while carries 1-5 land; that is cosmetic.
- Round-1 `## Red checks`: settled. The body answers the reds at the previous head a4a11b3f: instrument-self-tests, with its cause and a cheaper detector named, and the `gate` deferral. I read the check runs at this head live: total_count is 55 on one page of 100, and none concluded failure, cancelled or timed_out. `merge_train.py classify c94edc5614b94f042dbb9a1196aa594be294534f --pr 3250` returned `GREEN ... pending: none red: none`, rc 0 (ev/classify.out).
- Mutation proof from the body, re-run by me: reverting plan_page `if g in merged:` to `if g in done:` gives `67 checks, 8 failed`; unmutated, the head gives `67, 0 failed` and the base 30638cf0 gives `66, 0 failed`. All three match the body. My own extra mutant, dropping the swimlanes `and r["start"]` guard, is killed (`27 checks, 1 failed`, a FAIL line). See ev/selftests_and_planpage_mutant.txt and ev/planpage_swimlane_mutant.txt.
- Body figures re-derived at the head: plan_table 26, handover_prompt 17, resume_doc 15, roster_lib 64, orchestrator_tick 275 and carry_audit 365 checks, all 0 failed. I did not re-run replan, size_durations, merge_throughput, closure select, entities.py, structure.py or prepr. CI's gate, closures, closure-scope and the tests lanes are green at this head, and per fix-review.md 11 I cite them rather than re-run them.
- Merge: `git merge-tree --write-tree origin/main c94edc5614b94f042dbb9a1196aa594be294534f` exits 0 with no conflict (ev/merge_tree.txt).
- Untouched: the three-dot diff touches no VERSION, custom_components/, RELEASE_NOTES.md or `*budgets.json` file (ev/untouched.txt). The delivery row dev/programme/delivery/3250.md is in the three-dot diff. budget-raise-gate and arch-score are green.
- DONE_STAGES readers: the diff keeps DONE_STAGES meaning "merged". plan_page now separates `merged` (DONE_STAGES) from `done` (closed), which was the round-3 repair. My mutant above shows that conflating the two is caught.
- No finder harness is named. I used the instruments already in the tree (r10_roster_ops_mutants, r10_seat_selftests_mutants) and the roster carries' own controls, and built no instrument of my own.

## Findings

- Follow-up: the body says R10-FLOW-TOOLKIT-MODEL "no longer owes" replan's absorbed line, because this PR changes `replan.is_done` to `not roster_lib.is_open`. But that group's carry 3 (triage P254) at roster `c516cf0f6620` still lists arm (1) "is_done includes absorbed" as owed, and the body's `## Forward-carry` is `none`. Arm (2), the absorber name and the ADVISORY for an unknown absorber, is still unbuilt there. The destination's brief should mark arm (1) implemented by this PR so its fixer does not re-derive it. Harness: the roster text at c516cf0f6620, compared with `git show c94edc5614b94f042dbb9a1196aa594be294534f:tools/plan/replan.py | grep -n "def is_done" -A1`. Perturbation: not applicable, since this is a record finding. Carry: R10-FLOW-TOOLKIT-MODEL

## Closing self-audit

- `carry_audit.py check` over the PR body's carry, Head, Red checks and Forward-carry sections (copied from the live PR) and this verdict printed `CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)`, rc 0.
