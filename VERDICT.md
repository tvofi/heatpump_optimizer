Fix review: merge 519bb4db971b5d49736fcacdd57d57bff8f6c630

bus-nonce: ad2455725e386f704487a3012b5f751b

Round 9 of #2404. Round 8 blocked this same head on the body only (carry-unsound: Forward-carry item 1 routed to R10-OPENPR-SILENT, which is done) and found nothing else at this head. This round judges round 8's repair, the body edit (PR updated 2026-10-19T06:14:45Z), and re-takes the head's figures.
Measured head: 519bb4db971b5d49736fcacdd57d57bff8f6c630 (ev/HEAD). It was still origin/fix/r10-carry-enforce when written. Merge base 2d843030a; origin/main abb397938. Role contract current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.

## Round 8's block is repaired

- Forward-carry item 1 now reads `Carry: dismissed: delivered by #2422 (7ab3030b); orchestrator_tick.carry_sweep goes live when this PR merges`. 7ab3030b is #2422's merge and is in origin/main. On origin/main, orchestrator_tick.py has `carry_sweep` (line 1775) over `tools/audit/carry_audit.py` (ev/carry_item1.txt). The dismissal is accurate.
- The round-6/7 note on M17 (item 7321e737) is now routed: `Carry: dismissed: guard deleted in this diff (item 7321e737)`.
- `carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body`: 7 routed, 0 unrouted, 0 bad, rc=0. `--roster-ref origin/main` and the tree's roster give the same (ev/carry_check.txt). With the verdict comments (`--comments`), both rosters give 13 routed, 0 unrouted, 0 bad, rc=0 (ev/carry_check_comments.txt). So the train's `findings` pre-flight will not PARK the PR.
- pr-contract 117917362115 started 06:14:51, after the body edit, and passed: `CARRY-AUDIT: 7 finding item(s): 7 routed, 0 unrouted, 0 bad destination(s)` and `FIGURES: 26 resolved, 0 not verified, 0 refused` (ev/pr-contract-117917362115.log).

## Verified

RESULT drive sites=152 unmapped=0 mutants=190 survived=0 rc=0 (dev/audit/harnesses/r10_carry_parser_mutants.py at head; ev/drive.txt; worktree clean after)
RESULT carry_audit_selftest=144 failed=0; queue_pre_flight_selftest=41 failed=0; merge_train_selftest=189 failed=0
RESULT rows39 rows_caught=33 of=33; last20 rows_caught=34 of=35, last20_hits=76 on_a_row=46 on_no_row=30
RESULT sweep --issues (origin/main roster) ISSUE-UNOWNED=4 (#2429, #2428, #2409, #2265); roster-drift 64b1f82a3/b29cd8d23=6; b29cd8d23 twice=0
RESULT codeowners_gap uncovered_files=0; field_coverage ok (dead=0 refused=0); agreement --only discovery divergent=0 unregistered=0 dead=0 refused=0; policy_lint TOTAL 0 error(s) across 41 policy file(s); rules_sync ok; structure PASSED; closure select MODE: SCOPED -- 3 script(s) run; delivery_status OK, 0 overdue (ev/figures.txt)
RESULT merge_tree_vs_origin_main=clean (exit 0, tree dfb7e449; origin/main abb397938)
RESULT version_manifest_notes_claims=untouched (empty three-dot diff)
RESULT check_runs_head=54: 39 success, 15 skipped, 0 failure, 0 in progress (ev/check-runs.tsv)
RESULT commits origin/main..head=35, as the body says

- Step 11: no run on this head is red. The range's reds (pr-contract at 7167a97d9/713182ca1/b419463b1, fast (3.14) at 713182ca1, wave-script and delivery-status at 03f1681a3) are each named and answered under `## Red checks`. pr-contract's red-history line reads `record` over 35 commits. I checked that each trigger was answered, not what the answer says.
- Step 12 / #1667: the code head is unchanged since rounds 7 and 8 (both merges are resolution-free, per round 7). I re-took the drive, the self-tests and the body's figures myself this round. They match the body.
- Step 9: r10_carry_parser_mutants.py and r10_carry_sweep_rows.py are the fixer's own instruments, disclosed as such. The round-10 sweep has no committed finder harness, as every earlier round recorded.
- Step 10: the remaining Forward-carry item and the Friction items route to O10-policy-fixer-md. That file is out of tree and UNVERIFIED here (carry_audit prints NOTE ... UNVERIFIED), as the PR says.
- Note, not a block: `## Red checks` says the head has `composed-proof` in progress. That run (117912628737) has since concluded success, so the sentence is stale, not false at the time it was written.
- Not mine to supply: this PR changes policy and code-owned paths, so tvofi's approving review at the head is still owed before merge, as the body's `## Approval` says.
