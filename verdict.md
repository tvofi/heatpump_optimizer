Fix review: blocked b419463b18a2a7da70c77b23e912769e4af6afe8 carry-missing: not carried to R10-TICK-DRIVERS (merged as #2390 at a96f4be4a, 2026-10-19 01:46 UTC, without the orchestrator_tick carry sweep; Forward-carry "none")

bus-nonce: 7f3a18f667a549abb5545615e803b29a
Round: fifth review of #2404. Round 1 blocked 5cf5786b9 (item-ref over-fire). Round 2 blocked 354c84a96 (paren form and segment scope each unpinned). Round 3 blocked 312f31923 (line-end cut and next-Carry: cut each unpinned). Round 4 blocked 03f1681a3 (root-cause-unanswered: wave-script and delivery-status, a body edit only). This round judges the delta 03f1681a3..b419463b18a2a7da70c77b23e912769e4af6afe8: the recarry bd68cf756 (origin/main b87e8f19 into 03f1681a3), 4696bac11 (bd68cf756 into the PR head) and b419463b1 (origin/main 06c6f3cf2), plus the re-taken body.
Reviewed head: b419463b18a2a7da70c77b23e912769e4af6afe8 (ev/HEAD; the PR head when written). Merge base 06c6f3cf2 = origin/main. Role contract current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
Evidence: ev/ (this probe ref)

## Block

Step 10. The body's first `## Forward-carry` item, the weekly and closure carry sweep in `tools/audit/seat/orchestrator_tick.py` (`carry_audit.py sweep --last N --issues` with both roster refs, a dispatch line on exit 1, a self-test arm with its null control), routes to `Carry: R10-TICK-DRIVERS` and says the fold text is out of tree because handoff/r10-tick-drivers holds the file. That destination closed during this round:

- #2390 (R10-TICK-DRIVERS) merged into main at a96f4be4a, 2026-10-19 01:46 UTC. That is the same main this head merges in through 06c6f3cf2.
- Its diff (13 files, ev/2390-merge.txt) does not touch `orchestrator_tick.py`. Its `## Forward-carry` reads "none" and never mentions this item.
- On origin/main nothing under `tools/` calls `carry_audit` (ev/main-carry_audit-callers.txt is empty). None of the "carry" lines in `orchestrator_tick.py` is the sweep (ev/main-tick-carry-lines.txt).
- The roster entry's `carry` list holds no such precondition. handoff/r10-tick-drivers is at fc145b97c, already in main, and it has no fold either.

So the finding now exists only in this PR's body. Repair, a body edit plus wherever the item is written: re-route it to a live destination that carries it as a precondition with its control, such as a new roster group (or a live one that owns `orchestrator_tick.py`), an issue, or an O-brief. Then give it that `Carry:`. No code change is owed.

The checker does not see this. `carry_audit.py check` on the live body prints `5 routed, 0 unrouted, 0 bad`, and with `--roster-ref origin/main` it prints the same (ev/body_check.txt). The roster still holds R10-TICK-DRIVERS at `resume.stage: not-started`, and dev/programme/delivery/2390.md still says **open**. The "holds as done" refusal therefore keys on a roster that lags the merge, and it fails open until the record absorbs #2390. This is a note on the instrument: the PR's grammar is correct as specified. A destination check that also reads the group's merged PR (the delivery row, or a `gh` read like the issue arm's) would have caught it. Carry: O10-policy-fixer-md

## Verified

RESULT drive sites=152 unmapped=0 mutants=190 survived=0 rc=0 (python3 dev/audit/harnesses/r10_carry_parser_mutants.py at head; ev/drive.txt; git status clean after)
RESULT carry_audit_selftest=144 failed=0; queue_pre_flight_selftest=37 failed=0; merge_train_selftest=180 failed=0 (ev/selftest.txt)
RESULT body_check="5 finding item(s): 5 routed, 0 unrouted, 0 bad destination(s)" (live body ev/body.md; 3 O10 notes UNVERIFIED)
RESULT resolution_delta: bd68cf756, 4696bac11 and b419463b1 each have exactly the tree `git merge-tree --write-tree` of their parents gives. b419463b1's only driver line is `LEDGER-MERGE: resolved tests/closures.json`, and the closures delta against 03f1681a3 is main's one `inert_reads` row (r10_tick_drivers.py). The authored files are byte-identical to 03f1681a3 apart from that row.
RESULT merge_tree_vs_origin_main=clean (exit 0; origin/main 06c6f3cf2 = merge base)
RESULT check_runs_head=41: 25 success, 13 skipped, 1 neutral (CodeQL), 0 failure; coverage 117853296362 and Analyze (python) 117853292583 in_progress when written (ev/check-runs.tsv)
RESULT version_manifest_notes=untouched (no path in the delta)

- Step 11: round 4's reds are now answered under `## Red checks` (wave-script, delivery-status and pr-contract at 03f1681a3), and none is red at this head. bd68cf756 and 4696bac11 have no check-runs of their own. I checked that the trigger was answered, not the answer's content.
- Step 12 and 1667: the code head is unchanged since round 4, whose code measurements stand. I re-took the drive and the self-tests above. I did not re-take policy_lint, field_coverage, agreement, structure or closure select. CI is green on them at this head, and I cite CI rather than re-running.
- Step 9: r10_carry_parser_mutants.py and r10_carry_sweep_rows.py are the fixer's own instruments, disclosed as such. The round-10 sweep has no committed finder harness, as rounds 1 to 4 recorded.
- Step 10, second item and the Friction items: these route to O10-policy-fixer-md, which is out of tree and UNVERIFIED here, as the PR says.
- Round count: this is the fifth round. Round 4's repair was a body edit, and this one is too. The block is no re-opened code defect: a destination closed under the PR.
