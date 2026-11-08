Outside work orders ahead of audit and owner work in every orderer, after main and hotfix. Repair of the round-1 blocked verdict at 3940fad2.

Owner ruling (tvofi 2026-11-07, triage batch 134 P420), verbatim: "all accepted outside issues or contributions should be prioritized higher than audit or owner submitted ones unless i call the owner one a hotfix."

## Head

ed1f1b1d196e2e2d78959696c4bc412a108c9b5d (merge of the handoff tip d21a15eb2fe0476875832f9d7695e9dea033083b into the branch)

## Answers to the verdict (one commit: d21a15eb2fe0476875832f9d7695e9dea033083b)

1. gate_priority `derived_priority`: now `roster_lib.dispatch_rank`; hotfix and outside groups return 2, critical path 1, else 0. The lease has three bands (`gate_lock.PRIORITY_MAX` is 2), so hotfix and outside share the top band and arrival orders them; splitting that band is the lease's seam and is carried, not silently dropped (see Forward-carry). Pinned by new gate_priority self-test checks and a null control.
2. orchestrator_tick `owed_levels`: sorts by `dispatch_rank` (hotfix, outside, critical, rest) then PR number. New check with a hotfix, an outside, a critical and a plain PR.
3. sweep_template 4d: restated (main, hotfix, outside, critical path, production, instruments).
4. plan_page: Tier tooltip, the note under the table and the self-test label at the tier check now state the six tiers.
5. instruments/open_driver.py.md: order restated.
6. mt-item-no-pr: new drain_order-level checks with a fork-head outside entry (#31, branch no group claims) through resume.pr, plus the no-outside null.
7. rl-group-for-pr-bool: roster_lib self-test fixture now has a group at resume.pr 1 and asserts group_for_pr(True) is None and (1) maps.
8. Figure corrected: merge_train self-test is 480 checks at this head (478 at 3940fad2).

Enumeration rule for ordering sites: grep -rn "critical_path\|critical_path_groups\|CRITICAL_PRIORITY" tools/ ; the sites it returns that order work are replan, open_driver, merge_train, gate_priority, orchestrator_tick (all wired); orchestrator_tick line ~1544 only marks CP on a design line and orders nothing.

## Mutation proof

Run by hand against each owner self-test (all KILLED): drain_order item drops pr (mt-item-no-pr, merge_train); group_for_pr bool guard deleted (rl-group-for-pr-bool, roster_lib); gate_priority `if rank <= 1` -> `if False` and the critical branch zeroed (gate_priority); owed_levels back to `0 if group in crit else 1` (orchestrator_tick); dispatch_rank hotfix arm disabled (orchestrator_tick). Earlier proofs for replan, open_driver and merge_train unchanged.

## Null control

No outside group and no hotfix: gate_priority fixture reads [1, 0, 0] as at base; owed_levels with the plain roster orders #100 then #99 as at base; earlier null controls for replan, open_driver and drain_order stand.

## Figures

Self-tests at head: gate_priority 15 checks, roster_lib 71, orchestrator_tick 285, merge_train 480, plan_page 67, all 0 failed. `python3 tests/structure.py`: RATCHET PASSED. `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh`: rc=0 (at d21a15eb); its diff-mutant step skipped (no file mutants reads in the diff), so survivor count 0 and no run time; the hand mutants above stand in. origin/main unmoved-or-conflict-free: `git merge-tree --write-tree origin/main HEAD` rc 0.

## Red checks

`governance / instrument-self-tests` (job 128661348216): red. Cause: `python3 -I tools/plan/replan.py --self-test` fails on the PR merge ref (refs/pull/3304/merge, 5259a4c4) with `FAIL dispatch follows the owner's order ... ['CPA','CPB','CPC','R10-HOTFIX-H','OUT',...]`, then `FAIL the unmutated copy's self-test exits 0`. The head alone passes (0 failed) and origin/main alone passes (0 failed); head merged with origin/main fails identically. Main's scheduler starts a ready critical-path group at once, over the slots cap (the overflow-exempt arm in build_plan), so with slots=1 the critical-path groups start at t0 with the hotfix and the outside group and sort ahead of them; this diff's new fixture assumes the old cap behavior. This diff's fixture is what fails, so this diff owns the red: it needs a fixer repair (order the fixture by tier among simultaneous starts, or carry the outside and hotfix tiers into the overflow pick), not a rerun. Cheaper detector: running the self-test on `git merge origin/main` of the head. It exists as this CI job; tools/pr/prepr.sh runs on the head unmerged and, by the owner ruling of 2026-11-07, is not rerun when main moves, so no pre-push detector covers a main-side scheduler change landing after the push. Standing cost of a merged-tree self-test pass in prepr: one replan.py run, seconds. Carry: dismissed: the merge train recarries and re-proves the head on current main under the owner ruling, so a prepr merge step would repeat that proof.

`pr-contract / pr-contract` (job 128661350034): red. Cause: `[pr-body] check governance / instrument-self-tests is red and ## Red checks does not name it`, the only error; the body said `none`. This diff did not cause it beyond the red above; it clears when this section names the check. Cheaper detector: `tools/pr/prepr.sh --body-check`, which exists and reads the red-history from the check-runs; it ran before the red existed, so it could not name it.

`gate` (job 128661143751): red at `Judge this head`, one line: `FAIL pr-contract / pr-contract: failure`. A consequence of the pr-contract red above; no separate cause and nothing to detect.

## Forward-carry

Splitting hotfix from outside inside the gate lease needs PRIORITY_MAX above 2 in tests/gate_lock.py (a different seam); not done here, hotfix and outside share band 2. Carry: dismissed: the lease has three bands and arrival orders within one, a hotfix waits behind an older outside run for one lease at most, and raising PRIORITY_MAX changes the aging rule for every waiter, so the split is not worth building without a measured wait

## Friction

none

## Unpinned sites

None added by the prepr mutant step (skipped); the hand mutants above are all killed.
