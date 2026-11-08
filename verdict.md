Fix review: blocked 2bf0e026397c99378c53d47a0a49c30927deefd9 class-open: replan dispatch_tier hotfix predicate needs production class for an R10-HOTFIX name, so 7 live hotfix groups rank below outside in the plan and above it in every other orderer

bus-nonce: bc4960e8b7501ae499bfc0d893978ea3

## Block

This is round 2, a later-round review. I reviewed head 2bf0e026397c99378c53d47a0a49c30927deefd9 against merge base 73365699a135fb813a43380096b6776d57f8ff4c, using the three-dot diff. Every Block and Finding item from round 1 (verdict/3304 at 429c7eaab) is closed at this head (see Evidence). One new item blocks.

The brief defines the order as "main, then hotfix (an R10-HOTFIX- name or kind bug), then outside, then today's order". The PR adds `roster_lib.is_hotfix`, which follows that definition: kind `bug`, or `HOTFIX` in the name. It also adds `dispatch_rank`, whose docstring calls it "the one order every queue reader applies". gate_priority and the tick's OWED order use it. open_driver gets the same result by name.

`tools/plan/replan.py` `dispatch_tier` does not use it. The diff moves its hotfix line ahead of the new outside arm but keeps the predicate `k == "bug" or "HOTFIX" in g and cls == "production"`. So an R10-HOTFIX-named group that is not production class is not a hotfix in the plan. It falls to the instrument tier (6), below outside (3) and below the critical path (4).

On the live roster (`handoff/audit-r10-roster` 6fb2599d), 8 HOTFIX-named groups are not done. 7 of them get replan tier 6 and dispatch_rank 0 (`ev/live-hotfix-tiers.txt`): GATE-BUSY-DEFER, CODEQL-HEADROOM, TRAIN-DEFER-WAIT, AUTHOR-EMAIL, NONREQUIRED-REDS, ROSTER-LINT-REFRESH and PREPR-SELFTEST-DARWIN.

A two-group fixture shows the effect (`ev/hotfix-predicate.txt`). With slots=1, R10-HOTFIX-X (kind instrument) and OUT (source outside):
- replan dispatches `['OUT', 'R10-HOTFIX-X']` (tiers 3 and 6);
- dispatch_rank gives `{'R10-HOTFIX-X': 0, 'OUT': 1}`;
- open_driver orders `['r10-hotfix-x', 'r10-out']`.

The plan therefore starts an outside group ahead of a group the owner named a hotfix. The opener, gate lease and OWED list put that hotfix first. That breaks the ruling's "unless i call the owner one a hotfix" in the one orderer that decides fixer starts. It also contradicts the PR's own claim of a single order.

The body's enumeration rule (`critical_path|critical_path_groups|CRITICAL_PRIORITY`) finds ordering sites, not hotfix predicates. So this seam is neither in its output nor dispositioned. The `production` condition was inherited from the base, where it decided only "urgent or not". This diff gives hotfix its own tier above outside, so the old predicate now decides an order the ruling settles.

To settle it, do one of these:
- make `dispatch_tier`'s hotfix arm `roster_lib.is_hotfix(group)`, with a fixture that has a non-production R10-HOTFIX group and an outside group, plus its mutant;
- or disposition in the body why a non-production hotfix should rank below outside in the plan only, with the owner's word for it.

Carry: R10-OUTSIDE-FIRST

## Findings

- Class-open: `tools/plan/replan.py` `dispatch_tier` keeps the base's `"HOTFIX" in g and cls == "production"` predicate while `roster_lib.is_hotfix`/`dispatch_rank` drop the class condition. 7 of 8 live non-done R10-HOTFIX groups get replan tier 6 below outside (3) and dispatch_rank 0 above it (`ev/live-hotfix-tiers.txt`, `ev/hotfix-predicate.txt`). Carry: R10-OUTSIDE-FIRST
- Defect (minor, same seam): `open_driver.default_class` treats a hotfix by name only (`r10-hotfix-` topic or `R10-HOTFIX-` group), never by kind `bug`, which the brief and `is_hotfix` both count. No live non-done group is kind `bug` without a HOTFIX name today, so nothing is misordered now. Passing `is_hotfix` through as the outside set is passed would close it. Carry: R10-OUTSIDE-FIRST
- Defect (doc): `tools/audit/seat/instruments/merge_train.py.md` is in the group's roster `files` list. It describes `Train.drain_order` and the `--front`/`--priority` tier, but not the new outside term between priority and the critical path. Carry: R10-OUTSIDE-FIRST
- Follow-up: `orchestrator_tick.owed_levels` and `gate_priority.derived_priority` map a PR to its group by `group_for_branch` only. A fork-head outside PR, whose branch no group claims, gets rank 3 / priority 0 there, while `merge_train._roster_group` falls back to `group_for_pr`. The brief requires that fallback only in merge_train. The tick has the PR number, so the same fallback would cost one call. Carry: R10-OUTSIDE-FIRST

## Evidence

- Head: `git ls-remote` shows refs/heads/fix/r10-outside-first at 2bf0e026397c99378c53d47a0a49c30927deefd9 when I measured and again before writing. The PR API head is the same, and the body's `## Head` names it (merging authored head 4c4dd755). `ev/HEAD.txt`.
- Role files: `git diff <merge-base>...origin/main -- dev/governance/roles/` touches orchestrator.md and standing-dispatch.md only. fix-review.md is unchanged, so I followed the main copy.
- Merge: `git merge-tree --write-tree origin/main <head>` rc 0, no conflict, tree a239317f (origin/main 17e621f08). `ev/merge-tree.txt`.
- CI: `merge_train.py classify 2bf0e026… --pr 3304` exits 0, `GREEN … pending: none red: none`, on two reads (`ev/classify.txt`). I read all 55 check runs at the head (paginated): every one concluded success, skipped or neutral (`ev/checks.txt`). The body's `## Red checks` names the three reds of earlier heads (instrument-self-tests on the merge ref, pr-contract, gate), each with cause and detector, and the pr-contract run at this head is green.
- Round-1 items, all closed at this head:
  - gate_priority `derived_priority` now goes through `dispatch_rank`: hotfix and outside give 2, critical gives 1. Mutants gp-outside-band-off and gp-outside-as-critical are KILLED.
  - `owed_levels` ranks by `dispatch_rank`. Mutants ot-owed-rank-const and ot-owed-old-crit-only are KILLED.
  - sweep_template 4d is restated.
  - The plan_page tooltip, the note and the :875 label are restated.
  - The open_driver.py.md order is restated.
  - mt-item-no-pr is KILLED (the drain-level fork-head check).
  - rl-group-for-pr-bool is KILLED (the `R10-ONE` pr-1 fixture).
  - The merge_train check count is quoted as 514 and is 514.
- Self-tests at the head, all rc 0 and 0 failed (`ev/head-*.log`): replan; gate_priority 15; roster_lib 71; orchestrator_tick 285; merge_train 514; plan_page 67; open_driver 84. These match every count in the body's Figures. At the base: 12 / 67 / 283 / 506 / 67 / 76, and replan 0 failed (`ev/base-*.log`).
- `tests/structure.py` at the head: STRUCTURE RATCHET PASSED, rc 0. The diff touches no `*_budgets.json`, `VERSION`, manifest, `RELEASE_NOTES.md`, claim file or `tests/closures.json`. The one new tracked file, `dev/programme/delivery/3304.md`, is the delivery row (`**open**`, R10-OUTSIDE-FIRST), and CI's closure checks are green on it.
- `tests/entities.py` (run plainly, BASH_ENV unset per the owner note) did not run clean. It stops at import with `ModuleNotFoundError: No module named 'homeassistant'` from tests/harness.py:25 (`ev/head-entities.txt`). The body quotes no entities figure at this head.
- Harness: the finder named none. I used the round-1 reviewer's harness (`ev/reviewer_harness.py.txt`), which is a reviewer's instrument, not the finder's or the fixer's, and ran it at both ends (`ev/harness-base.txt`, `ev/harness-head.txt`).
  - Head: replan with outside starts CPA (exempt) and then `R10-HOTFIX-H`, `OUT`, `PROD` on the real slot. open_driver orders `['r10-hotfix-x','r10-out','r10-cp','triage-x','r10-inst']`. drain_order gives `[5,3,2,1,4]`, both injected and through the roster read.
  - Base: drain_order gives `[5,2,1,3,4]`.
- Null control at both ends:
  - replan random-null digest is 8fac3ead7e92fd63 at the base and at the head;
  - open_driver random-null digest is bef9dfd41011a633 at both ends;
  - drain null is `[5,2,1,3,4]` at both ends.
- Live roster tier histogram: base `[(2,4),(3,12),(4,50)]`, head `[(2,1),(3,3),(4,3),(5,9),(6,50)]`.
- Mutation proof (`ev/mutants.txt`, script `ev/reviewer_mutants.py.txt`): 26 mutants, 26 KILLED, 0 SURVIVED. The list is the round-1 eighteen plus replan-arm-order-main, gp-outside-band-off, gp-outside-as-critical, rl-rank-hotfix-arm, rl-rank-outside-arm, rl-is-hotfix-no-bug, ot-owed-rank-const and ot-owed-old-crit-only.
  - The repair's own proof reproduces. Moving the overflow arm back ahead of the tiered pick fails `dispatch follows the owner's order …` with `['CPA','CPB','CPC','R10-HOTF…`, and fails `the hotfix takes the free slot at t0 …`.
  - The replan "unmutated copy's self-test exits 0" failure under a mutant is that check copying the mutated tree. It is expected and is not a false kill.
- Enumeration rule: I re-ran the body's grep (`ev/enum-rule.txt`). Beyond the five sites the body wires, it returns merge_throughput, ci_critpath, gantt_drift, plan_table, probe_bridge, sweep_gantt, budget_raise_gate and stamp. I read each hit: they measure, display or budget the critical path and order no work, so the body's claim holds for its own rule. The blocking seam above is outside that rule's reach.
- Not re-derived: the prepr figures (40 of 40 survivors under MUTANT_CMD at 413c9ec2) and the per-file instrument survivor counts (133 mutants, 38 then 34 survivors) and wall times. Their logs are on the fixer's machine. My own mutants are a different, hand-written set.
- Forward-carry: the body's one carry (splitting the lease band) and both Friction items are dismissed with a reason, and the packet's carry_audit routes all three. The roster group has no `carry` entries.
