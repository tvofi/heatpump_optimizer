Fix review: blocked 3940fad2f1f49fcd466a22ad80934a76f26188c4 class-open: tools/pr/gate_priority.py derived_priority and orchestrator_tick.owed_levels order by critical path with no outside or hotfix term, neither in the diff nor dispositioned in the body

bus-nonce: 5b2e336e26a191112ee6414d3bd36ad5

## Block

Round 1 (first-round review). Reviewed at head 3940fad2f1f49fcd466a22ad80934a76f26188c4. Merge base 7c9c4c154cda514f938fd503cde2779716caf251. Three-dot diff.

The ruling is general: "all accepted outside issues or contributions should be prioritized higher than audit or owner submitted ones unless i call the owner one a hotfix". The body says outside work orders first "in the three orderers" but names no rule for how it enumerated them (fix-review.md step 6). I enumerated every site in the tree that orders work by critical path or hotfix. Three of those sites are neither in the diff nor dispositioned in the body:

1. `tools/pr/gate_priority.py:97` `derived_priority` returns 1 for a critical-path group's branch and 0 for everything else. An outside group's branch therefore waits behind a critical-path one for the gate lease and the heavy slot (`tools/pr/prepr.sh` step 1b0 exports it as `HPO_GATE_PRIORITY`; `tests/gate_lock.py` orders waiters by it). Hotfix gets no lift there either.
2. `tools/audit/seat/orchestrator_tick.py:851` `owed_levels` sorts the OWED review and fixer lines by `(0 if group in crit else 1, n)`. An outside PR that is owed a reviewer or fixer is listed after every critical-path one.
3. `tools/audit/seat/sweep_template.md:77` (4d) tells the sweep seat the queue priority "for the train, review, fixer and CI queues alike": "a push to main; then critical path and hotfix; then production ...". That now contradicts the train's own drain order at this head.

Each of these needs one of two things: the outside term (and the hotfix split where it applies) wired in, or a body disposition carrying it to the owning group. R10-CI-PRIORITY-PAUSE, which is after-edged on this group, owns the CI tier module and lists `orchestrator_tick.py`. I did not find it naming gate_priority or owed_levels.

Two integration defects in this diff's own scope go with this block, because they ship stale statements of the order the PR changes:

4. `tools/audit/seat/plan_page.py:1129`: the Tier column's tooltip on the rendered plan page still reads "1 main, 2 critical path and hotfixes, 3 production and instruments saving 12 h or more, 4 other instruments by savings". At this head the page renders tiers 1–6 (2 hotfix, 3 outside, 4 critical path, 5 production, 6 instrument). The PR updated the code comment at :248 but left the user-visible legend. The self-test label at :868 ("the critical path is tier 2") is stale the same way, though its value uses the constant.
5. `tools/audit/seat/instruments/open_driver.py.md:13-15` is a file in this group's own roster `files` list. It still states the old order: "a critical-path topic is never behind a non-critical one, an omitted topic slots by default class (critical, `R10-HOTFIX-*`, ...)".

6. A surviving mutant on the wiring the group brief requires ("an entry maps to its group by branch, else by group_for_pr"). In `merge_train.py`'s `drain_order`, I changed `return {"branch": b, "pr": e["pr"]}` to `return {"branch": b}`. All checks still pass: `merge_train.py --self-test` rc 0, mutant `mt-item-no-pr` SURVIVED. The fork-head arm is pinned only on `_outside` called directly, never through `drain_order`. A fork-head outside entry in a real drain could lose its outside rank and no test would fail. The body's survivor list does not include this line.

## Findings

- Class-open: `tools/pr/gate_priority.py` `derived_priority` (gate lease and heavy slot via `tests/gate_lock.py`) has no outside or hotfix term. Carry: R10-OUTSIDE-FIRST
- Class-open: `tools/audit/seat/orchestrator_tick.py` `owed_levels` orders OWED review and fixer lines critical path first, with no outside term. Carry: R10-OUTSIDE-FIRST
- Class-open: `tools/audit/seat/sweep_template.md` (4d) states the superseded queue order for the train, review, fixer and CI queues. Carry: R10-OUTSIDE-FIRST
- Defect: the `plan_page.py:1129` Tier tooltip and the `:868` check label still describe the four-tier order. Carry: R10-OUTSIDE-FIRST
- Defect: `instruments/open_driver.py.md:13-15` (in the group's own files list) states the superseded opener order. Carry: R10-OUTSIDE-FIRST
- Surviving mutant `mt-item-no-pr`: `drain_order` dropping `pr` from the item survives. It needs a drain-level check with a fork-head outside entry. Carry: R10-OUTSIDE-FIRST
- Surviving mutant `rl-group-for-pr-bool`: deleting `group_for_pr`'s `isinstance(pr, bool)` guard survives, because the fixture has no group with `resume.pr` 1, so `True` maps to None anyway. A fixture group at pr 1 would pin it. Carry: R10-OUTSIDE-FIRST
- Figure: the body quotes `merge_train.py --self-test` as 477 checks. It is 478 at both da8a36ec and the head (base 472; the last pin commit added one). Carry: R10-OUTSIDE-FIRST

## Evidence

- Head: the PR API shows the head is 3940fad2f1f49fcd466a22ad80934a76f26188c4 at verdict time. The body names the same head. `ev/HEAD.txt`.
- Role files: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- Merge: `git merge-tree --write-tree origin/main <head>` rc 0, no conflict (origin/main 17e115792). `ev/merge-tree.txt`.
- CI: `merge_train.py classify 3940fad2 --pr 3304` exits 0: "GREEN 3940fad2f1f49fcd466a22ad80934a76f26188c4 pending: none red: none" (`ev/classify.txt`). Across all check-run pages at the head nothing concluded other than success or skipped (`ev/checks.txt`). No red check, so no root-cause answer is owed, and the body's "Red checks: none" holds.
- Self-tests at head: replan 0 failed; open_driver 83 checks, 0 failed; merge_train 478 checks, 0 failed; roster_lib 69 checks, 0 failed (`ev/head-*.log`). At base: 472 / 76 / 0 failed / 67. `tests/structure.py` at head: STRUCTURE RATCHET PASSED, rc 0.
- Harness: none was named by the finder. I built my own (`ev/reviewer_harness.py.txt`) and disclose it as mine. It drives each orderer at base and head; RESULT lines are in `ev/harness.txt`:
  - replan with outside: head `['R10-HOTFIX-H', 'OUT', 'CPA', 'CPB', 'PROD']`, base `['CPA', 'CPB', 'R10-HOTFIX-H', 'PROD', 'OUT']`.
  - open_driver default order: head `['r10-hotfix-x', 'r10-out', 'r10-cp', 'triage-x', 'r10-inst']`.
  - drain_order: head `[5, 3, 2, 1, 4]` (priority, outside, critical, arrival) both injected and through the roster read; base `[5, 2, 1, 3, 4]`.
  - Each orderer puts outside between hotfix and critical path.
- Null control: random rosters and topic sets with no `source` field and no hotfix give the same sha256 at base and head. replan `8fac3ead7e92fd63` at both ends; open_driver `bef9dfd41011a633` at both ends; drain null `[5, 2, 1, 3, 4]` at both ends.
- Hotfix split: with a hotfix present and no outside group, the order differs from base, as the body says (replan null `['R10-HOTFIX-H', 'CPA', ...]`). It is pinned: replan's "dispatch follows the owner's order" seq and the `replan-hotfix-below-cp` mutant (KILLED), and open_driver's "the fence beats the file" check. A consequence the body does not name: in open_driver, an omitted record topic now slots ahead of listed rest-class topics when the only listed higher-class topic was a hotfix, because the hotfix is now fenced.
- Fence starvation: 10 listed outside topics plus 1 omitted hotfix leaves the hotfix at position 0 of 11. The fence cannot starve hotfix.
- Live roster (`handoff/audit-r10-roster`): 4 groups with `source: outside` (R10-COMBI-TANK, R10-GENERIC-HEAT-CURVE, R10-GENERIC-HEAT-CURVE-PERSISTENT, R10-INPUT-REAPPEAR), tier 3 at head. Tier histogram base `[(2,5),(3,14),(4,49)]`, head `[(2,1),(3,4),(4,4),(5,10),(6,49)]`.
- Callers of dispatch_tier and its constants: plan_page only. `plan_page.py --self-test` 67 checks, 0 failed. No committed plan or ordering golden carries tier values, so there is nothing to claim. `VERSION`, the manifest and the release notes are untouched (no such path in the diff).
- Mutants, mine (`ev/mutants.txt`, `ev/reviewer_mutants.py.txt`), 16 KILLED and 2 SURVIVED:
  - KILLED: replan-tier-outside, replan-hotfix-below-cp, replan-outside-eq-urgent, od-class-outside, od-fence-1, od-fence-0, od-sortkey-unfenced, od-runpass-outside-empty, od-swap-hotfix-outside, mt-drain-outside, mt-drain-swap, mt-no-pr-fallback, mt-outside-any-group, rl-is-outside-truthy, rl-is-outside-absent-true, rl-group-for-pr-none.
  - SURVIVED: mt-item-no-pr, rl-group-for-pr-bool.
  - The body's named mutation proofs reproduce.
- Not re-derived: the body's `tests/entities.py` figure ("3 of 2655 ENTITY CHECKS FAILED" at head and at base 8a1358e8). In this container entities.py stops at import (`ModuleNotFoundError: homeassistant`) at both the head and the merge base (`ev/head-entities.txt`, `ev/base-entities.txt`). Also not re-derived: the prepr mutant figures (25 survivors, 23m41s), whose log is on the fixer's machine.
- Forward-carry: the body says none, and the roster group has no carries. The block above is this group's own to settle.
