Outside work orders ahead of audit and owner work in every orderer, after main and hotfix. Repair of the red `governance / instrument-self-tests` on the merge ref: origin/main merged in, and replan's scheduler now gives the real slots in the tiered order before the critical-path overflow arm runs.

Owner ruling (tvofi 2026-11-07, triage batch 134 P420), verbatim: "all accepted outside issues or contributions should be prioritized higher than audit or owner submitted ones unless i call the owner one a hotfix."

## Head

4c4dd755dc73f1b18718e8ca55a4cbe2be9f9219 (origin/main 73365699a135fb813a43380096b6776d57f8ff4c merged at f6ffa979846da27a24bdc92d34edc9186855458f, then three commits)

## The repair (commits 413c9ec256b8, 51838e6d6a1a, 4c4dd755dc73)

Main's `build_plan` ran the critical-path overflow arm before the tiered pick. So a ready critical-path group took the free real slot first, and every later critical-path group took each freed slot ahead of a waiting hotfix or outside group. With slots=1 the hotfix waited behind the whole critical-path chain (the CI list: `['CPA','CPB','CPC','R10-HOTFIX-H','OUT',...]`). That breaks the owner's order, not only the fixture.

Chosen: carry the tiers into the slot pick. The pick over every ready group now fills the real slots first, in `dispatch_key` order. A critical-path group it leaves waiting still starts at once on an overflow slot and is flagged `exempt`. It takes a free slot only when the coordinator cap held the pick. Why this and not "order by tier among simultaneous starts": that would only re-sort the fixture's tie and leave the hotfix starved behind the chain in the plan. Why not make hotfix and outside exempt from the cap too: orchestrator.md section 5 grants the cap exemption to the critical path alone (it is policy, owner's call). The fix keeps that exemption unchanged: no critical-path group starts later than before. The only change is which tier holds the real slots.

The owner-order fixture now reads the order off the real slots (the non-exempt groups by start): hotfix, outside, production, then instruments by savings with unrecorded last. A second check states that the hotfix holds real slot 0 at t0 while CPA starts beside it at t0, exempt, and that CPA, CPB and CPC are all exempt.

Earlier answers to the round-1 verdict (commit d21a15eb2fe0476875832f9d7695e9dea033083b) stand as written there: gate_priority `derived_priority` via `roster_lib.dispatch_rank`, orchestrator_tick `owed_levels`, sweep_template 4d, plan_page tooltips, open_driver.py.md, the fork-head drain_order checks and the `group_for_pr` bool fixture.

Enumeration rule for ordering sites: grep -rn "critical_path\|critical_path_groups\|CRITICAL_PRIORITY" tools/ . The sites it returns that order work are replan, open_driver, merge_train, gate_priority and orchestrator_tick, and all are wired. orchestrator_tick's design-line CP mark orders nothing. The replan site had two arms ordering slots, and this repair puts both under the tiers.

## Mutation proof

Repair (replan): on the merged tree, restore main's arm order (the overflow arm moved back ahead of the capped pick) and run `python3 -I tools/plan/replan.py --self-test`. Result: KILLED. Two checks fail, `dispatch follows the owner's order ...` with `['CPA','CPB','CPC','R10-HOTFIX-H','OUT','PROD','HI','LO','NONE']` (the CI failure list exactly) and `the hotfix takes the free slot at t0 and the ready critical-path group starts beside it past the cap ...` (CPA on slot 0, not exempt). Then `the unmutated copy's self-test exits 0`. Restored: 0 failed.

New pins (51838e6d), each per-file mutant re-run at that head: roster_lib `if not gid:` GUARD_OFF and its RETURN_DEL are KILLED by the no-id hotfix row. The `isinstance(v, bool) or v is None` GUARD_OFF is KILLED by `R10-BOOL` (resume.pr True) ahead of the pr-1 row. open_driver.py:149 `cls[u] <= cls[t]` to `<` is KILLED by the equal-class omitted-topic check. Earlier hand mutants (drain_order, group_for_pr bool guard, gate_priority, owed_levels, dispatch_rank hotfix arm) stay as recorded at d21a15eb.

## Null control

The unmutated merged tree: replan self-test 0 failed. Its own null controls still hold: `overflow (null): the non-critical group past the cap waits and is not exempt`, and `null control: two groups in one tier keep the height tie-break`. With no hotfix or outside group in the fixture, the critical-path group still starts at t0 flagged exempt, so the overflow behaviour main added is untouched.

## Figures

Self-tests at 4c4dd755 (merged tree), each printed by its own `--self-test`, all 0 failed: replan `self-test: 0 failed` (model self-test 0 failed, run 84 s); gate_priority 15 checks; roster_lib 71 checks; orchestrator_tick 285 checks; merge_train 514 checks (main's own checks added since 480); plan_page 67 checks; open_driver 84 checks.
`python3 tests/structure.py`: STRUCTURE RATCHET PASSED. Claim files byte-identical to origin/main (prepr `claim files`).
`PREPR_SKIP_CLOSURES=1 MUTANT_CMD="python3 -I tools/plan/replan.py --self-test" bash tools/pr/prepr.sh`: rc=0 at 413c9ec2. Its diff-mutant step ran 40 mutants (`--max-mutants 40`) across all 11 changed files against replan's self-test alone and reported 40 survivors (report only). The command could reach replan's mutants only, so that count measures the command and not the pins.
Per-file diff-mutant runs, the instrument re-run with each file's own self-test: `python3 -I tools/audit/seat/mutant_run.py --diff 73365699a135...HEAD --path <file> --cmd "python3 -I <file's owner> --self-test" --report-only`, at 413c9ec2, 133 mutants listed (`--list`), run in parallel. Survivors and wall time per file: gate_priority 13 mutants, 1 survivor, 18 s. open_driver 13, 1, 24 s. open_driver_selftest 15, 9, 32 s. orchestrator_tick 8, 1, 21 s. roster_lib 28, 6, 25 s. replan 19, 5, 1682 s. merge_train 37, 15, 2692 s. That is 38 survivors at 413c9ec2. Re-run at 51838e6d after the pins: roster_lib 3 survivors, open_driver 0. The null control is the same command printing a survivor at 413c9ec2. That leaves 34 survivors, each dispositioned under `## Unpinned sites`.
origin/main 73365699a135 at 2026-11-08T10:09:47Z; `git merge-tree --write-tree origin/main HEAD` rc 0.

## Red checks

`governance / instrument-self-tests` (job 128661348216): red. Cause: `python3 -I tools/plan/replan.py --self-test` failed on the PR merge ref (refs/pull/3304/merge, 5259a4c4) with `FAIL dispatch follows the owner's order ... ['CPA','CPB','CPC','R10-HOTFIX-H','OUT',...]`, then `FAIL the unmutated copy's self-test exits 0`. The head alone passed and origin/main alone passed; the merge failed. Main's build_plan ran its critical-path overflow arm before the tiered pick, so critical-path groups took the real slot ahead of the hotfix and outside groups this diff ranks above them. This diff owned the red. Repaired above: origin/main merged in, the tiered pick runs first, replan self-test 0 failed at 4c4dd755. Cheaper detector: running the self-test on `git merge origin/main` of the head. It exists as this CI job; tools/pr/prepr.sh runs on the head unmerged. By the owner ruling of 2026-11-07 it is not rerun when main moves, so no pre-push detector covers a main-side scheduler change landing after the push. Standing cost of a merged-tree self-test pass in prepr: one replan.py run, about 85 s. Carry: dismissed: the merge train recarries and re-proves the head on current main under the owner ruling, so a prepr merge step would repeat that proof.

`pr-contract / pr-contract` (job 128661350034): red. Cause: `[pr-body] check governance / instrument-self-tests is red and ## Red checks does not name it`, the only error; the body said `none`. This diff did not cause it beyond the red above; this section names the check. Cheaper detector: `tools/pr/prepr.sh --body-check`, which exists and reads the red-history from the check-runs. It ran before the red existed, so it could not name it.

`gate` (job 128661143751): red at `Judge this head`, one line: `FAIL pr-contract / pr-contract: failure`. A consequence of the pr-contract red above; no separate cause and nothing to detect.

## Forward-carry

Splitting hotfix from outside inside the gate lease needs PRIORITY_MAX above 2 in tests/gate_lock.py (a different seam); not done here, hotfix and outside share band 2. Carry: dismissed: the lease has three bands and arrival orders within one, a hotfix waits behind an older outside run for one lease at most, and raising PRIORITY_MAX changes the aging rule for every waiter, so the split is not worth building without a measured wait

## Friction

fixer-step-push: contradiction: refs/heads/handoff-wip/r10-outside-first held a prior seat's BLOCKED commit 2a5cd948 that is not an ancestor of the PR head, so a fast-forward step push of this repair was refused and was not forced; this seat pushed no step ref and hands off directly. Carry: dismissed: the brief deletes the step ref after the handoff, which clears it for the next seat
mutant-cmd-scope: cost: one MUTANT_CMD runs one self-test over the mutants of every changed file, so on a multi-file diff the prepr count reports the command's reach (40 of 40 survived) instead of the pins; the per-file runs above were the measurement. Carry: dismissed: per-file runs by `--path` already exist in mutant_run.py, and a seat that reads its survivors per file finds the gap in one listing

## Unpinned sites

Every remaining survivor from the per-file runs, by disposition:
- Self-test lines (a mutant there weakens a fixture or deletes one check; no production behaviour moves). These are value checks in the instrument's own self-test, and `mutation-autofix` mutates `custom_components/` only. gate_priority.py:231 (`>` to `>=` in the check). roster_lib.py:894 and :914 (fixture constants in the is_outside and group_for_pr checks). replan.py:755, :761, :762 and :766 (tier-check bounds and constants). replan.py:792 is tightened from `slot < 1` to `slot == 0` at 4c4dd755 and not re-run by the instrument. All 9 open_driver_selftest.py sites (:114, :118, :119 x2, :120 x2, :122, :124, :126), a test-only file. All 15 merge_train.py sites (:4010 x2, :5572, :5574, :5585, :5588, :5591, :5592, :5597, :5605 x2, :5607, :5615, :6961 x2), all inside `_self_test` (lines 3836 to 8396): the fixture default `outside=lambda it: False` and fork-head fixture constants.
- Equivalent: roster_lib.py:657 RETURN_DEL. `continue` becomes `pass` as the last statement of the loop body, so the next iteration follows either way. orchestrator_tick.py:897 CONST_SWAP. The no-roster default rank `3` becomes `4` only on the arm where every item gets the same constant, so the sort by PR number is unchanged.
