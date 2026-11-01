Fix review: merge cddb99085a147ca6a9530514b7ed4b10bc2d59f5

bus-nonce: 281fd719b059d46f9ed2c0d014f5bea1

Round 1 (roster 10-14). Measured head cddb99085a147ca6a9530514b7ed4b10bc2d59f5 (authored code head df25f62e4; head adds only delivery/3061.md).

## Findings

- Policy: the diff edits dev/governance/roles/fix-review.md (policy; one sentence added to the packet, two clauses cut). It merges only on tvofi's approving review or the mandate in force; noted, not decided here. Carry: dismissed: owner approval gate (budget/policy review) already owed by the PR body's Approval section, nothing further to hand on
- Carry 13 owes a before/after count of mechanical block classes over the next 10 verdicts after merge; owed after merge, not measurable here. Carry: R10-ORCH-REVIEW-PACKET

## Evidence

- Harness (finder's, r10_seat_selftests_mutants.py arms review_packet-6..15) at head: RESULT survivors=0, all 10 KILLED; self-test 63 checks, 0 failed.
- Same arms (head's harness file) at base 2b6bef745: arms 6-9 KILLED against base self-test (51 checks); arms 10-15 NOT RUN, pattern absent at base (the code does not exist there). Base self-test 51 checks, 0 failed.
- Own mutant: carries_at(sha) < n -> <= n in unlanded_carries: self-test "carry-landed null: the same body once the carry lands passes" FAILs (63 checks, 1 failed), killed. Restored.
- Null controls present in the self-test (body citing no carry as landed passes; same carry once landed passes; arms 12-15 go red when the tests/arm are flipped).
- Packet at the head: Refusals none; carry_audit 14 routed, 0 unrouted; FIGURES 5 resolved, 0 not verified. CI: merge_train classify GREEN (pending none, red none). Mutation/gate not re-run (cite CI).
- Citations: #2870 (eb2063218) and #2939 (279578074) are merged on origin/main; carries 1-4,7-9 dismissals checked against those merges. Carry 9 (relay-format statement at fix-review.md line 7) present in the tree.
- Carry 6 (dispatch at the handoff ref) not built; body states why (re-keys topic record in open_pr.sh, adds a relay, edits standing-dispatch.md and fix-review step 7) and stops it for the orchestrator. Not blocked on.
- New refusal on other open heads: #3059 (ffec33d8d) draws `carry-landed: carry 4 cited as landed at edd149d14, whose roster entry holds 3` - rightly: the commit exists and its roster entry holds 3 carries, so the cite is premature. #3070 (584c317d5): no refusal. No reviewable head newly refused wrongly.
- git merge-tree --write-tree origin/main <head>: clean, rc 0, no conflicts.
- policy_lint --budgets rc 0 (fix-review brief 135 lines/cap 140); rules_sync --check ok; tests/structure.py PASSED; tests/golden, claim files, VERSION, RELEASE_NOTES: three-dot diff empty. Delivery row dev/programme/delivery/3061.md present in the three-dot diff. Scoped gate and entities.py are green in CI (gate, tests/closure-scope success).
- Red checks: none at the head.
