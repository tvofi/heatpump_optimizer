Fix review: blocked 519bb4db971b5d49736fcacdd57d57bff8f6c630 root-cause-unanswered: pr-contract went red at b419463b1 (117865632672, BAD-DEST R10-OPENPR-SILENT), unanswered; the body says no run on b419463b1 was red

bus-nonce: 79a91d7be0b23b3565970d8734d89203
Round: seventh review of #2404. Round 1 blocked 5cf5786b9 (item-ref over-fire). Rounds 2 and 3 blocked 354c84a96 and 312f31923 (mutation-vacuous). Round 4 blocked 03f1681a3 (root-cause-unanswered: wave-script and delivery-status). Round 5 blocked b419463b1 (carry-missing: R10-TICK-DRIVERS closed). Round 6 blocked b419463b1 (root-cause-unanswered: pr-contract 117865632672). This round judges the delta b419463b1..519bb4db9: a945bb62e, b2bbe0865, ab52c8457, f8acbc62a, 74201dd56 (main merges on the handoff line), e23fa9886 and 519bb4db9, plus the re-taken body.
Reviewed head: 519bb4db971b5d49736fcacdd57d57bff8f6c630 (ev/HEAD). Merge base 2d843030a. Role contract current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
Evidence: ev/ (this probe ref)

## Block

The code is sound and round 6's substance is fixed. R10-OPENPR-SILENT is now in main's roster (`git grep` at 2d843030a, which this head merges), and pr-contract at this head passes: `CARRY-AUDIT: 6 finding item(s): 6 routed, 0 unrouted, 0 bad destination(s)` (117902749693 and 117902576185). The block is step 11 and `defect-root-cause.md`'s Enforcement section, and the repair is a body edit only.

The trigger is "a check that went red on a commit in the branch". The commit check-runs API for b419463b18a2a7da70c77b23e912769e4af6afe8 (ev/check-runs-b419463b1.tsv, 51 runs) holds `117865632672 pr-contract completed failure 2026-10-19T02:48:20Z`. That run is round 6's block: carry_audit printed BAD-DEST because the destination was on the roster branch and not yet on main. This body's `## Red checks` opens with "No check run on the previous PR head `b419463b18a2a7da70c77b23e912769e4af6afe8` was red." That is false, and the section names 117865632672 nowhere. pr-contract does not refuse this itself, because its red list excludes pr-contract by name (`select(.name != "pr-contract")`, ev/pr-contract-117902749693.log). Its red-history line lists only `delivery-status, fast (3.14), wave-script`. So the gate passes and the check falls to the reviewer, as at 713182ca1, where the body did answer pr-contract's own red.

Repair: replace that sentence with a bullet that names pr-contract 117865632672 at b419463b1, its cause (the carry pointed at a group that was only on handoff/audit-r10-roster while the check reads the tree's roster), what cleared it (the roster entry landed on main, which 519bb4db9 merges in), and the cheaper-detector answer. A cheaper detector could be `carry_audit.py check --body` with `--roster-ref origin/main` run locally before the body edit. Its standing cost is about one second. Or the body can record that none exists. No code change is owed.

## Verified

RESULT drive sites=152 unmapped=0 mutants=190 survived=0 rc=0 (python3 dev/audit/harnesses/r10_carry_parser_mutants.py at head; 191 RESULT lines: M0 baseline, S-span-lo equivalent, every other mutant killed; worktree clean after; ev/drive.txt)
RESULT drive M15b=killed (1: "a segment ends at its line"); M16=killed (1: "a segment ends at the next `Carry:`"); M14=killed (3); M15=killed (3); M13=killed (4)
RESULT mutant_M10 (findings_gate call deleted from PreFlight.entry, my own edit) = killed: queue_pre_flight 41 checks, 4 failed, including "a body whose Friction finding names no destination PARKs on findings"; restored (ev/mutant-M10.txt)
RESULT carry_audit_selftest=144 failed=0; queue_pre_flight_selftest=41 failed=0; merge_train_selftest=189 failed=0 (ev/selftest.txt)
RESULT body_check (tree roster) = "6 routed, 0 unrouted, 0 bad" rc=0 (ev/body_check.txt)
RESULT rows39 rows_caught=33 of=33; last20 rows_caught=34 of=35, last20_hits=76 on_a_row=46 on_no_row=30
RESULT sweep --issues (origin/main roster) ISSUE-UNOWNED=4 (#2429, #2428, #2409, #2265), as the body says; roster-drift 64b1f82a3/b29cd8d23=6, same ref twice=0
RESULT codeowners_gap uncovered_files=0; policy_lint TOTAL 0 error(s) across 41 files; rules_sync ok; field_coverage ok; structure PASSED; closure select MODE: SCOPED -- 3 script(s) run; delivery_status OK, 0 overdue (ev/figures.txt)
RESULT resolution_delta: 519bb4db9, e23fa9886, f8acbc62a, ab52c8457 and b2bbe0865 each have exactly the tree `git merge-tree --write-tree` of their parents gives. Two merges were resolved by hand (ev/resolution.txt):
- a945bb62e: the three finding-propagation rule files. At head, policy_lint and rules_sync pass.
- 74201dd56: tools/audit/seat/queue_pre_flight.py. `git diff origin/main HEAD -- queue_pre_flight.py` contains additions only: the docstring line, the import, `findings_gate`, `issue_state`, the `dests` option and five self-test arms. Main's `raise_hold` step is kept intact (ev/qpf-vs-main.diff).
RESULT carry_audit.py and both r10_carry harnesses are byte-identical between b419463b1 and the head, and between 6f20f78a3 and the head.
RESULT merge_tree_vs_origin_main=clean (exit 0; origin/main 913ce1ff5)
RESULT version_manifest_notes=untouched; claim files untouched
RESULT check_runs_head=45 at 05:55 UTC: 31 success, 13 skipped, 0 failure, 1 in_progress (closures 117904612520); the block does not depend on it (ev/check-runs.tsv). The head was unchanged at 05:55 UTC

- Step 9: r10_carry_parser_mutants.py and r10_carry_sweep_rows.py are the fixer's own instruments, disclosed as such. The round-10 sweep still has no committed finder harness. M10 and the probes are mine.
- Step 10: the first Forward-carry item now routes to R10-OPENPR-SILENT, which main's roster holds. Round 6 opened the carry text on the roster branch (pass, precondition, control). The O10-policy-fixer-md items are out of tree and UNVERIFIED here, as the PR says.
- Note, not a block: `carry_audit.py --roster-ref origin/main check --body --comments` gives "11 items, 10 routed, 1 unrouted": round 3's M17 note (review 6253086887, item 7321e737, written before the marker existed). Round 6 named this, and the body still does not route it. The train's `--pre-flight` `findings` step will PARK this PR on it. It costs one body line: `Carry: dismissed: guard deleted in this diff (item 7321e737)`. Carry: dismissed: the fixer's body edit, named here and in round 6
