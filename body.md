Outside work orders ahead of audit and owner work in every orderer, after main and hotfix. Round 3 repairs the round-2 verdict (class-open at 2bf0e026): every orderer now reads the hotfix tier from one predicate, `roster_lib.is_hotfix`.

Owner ruling (tvofi 2026-11-07, triage batch 134 P420), verbatim: "all accepted outside issues or contributions should be prioritized higher than audit or owner submitted ones unless i call the owner one a hotfix."

## Head

`62f90fcb3bd8a45775642d290bf86b3274cb040d` merges main `2f6d699` into the previous head: an automatic merge by the orchestrator, no resolution. The reviewed code is unchanged.

`aff9f1393aec11bc0f5fc745d34a9161c09b695a` merges main `7bdc8aa` into the previous head: an automatic merge by the orchestrator, no resolution. The reviewed code is unchanged.

`cc0b58ff5be5b428a73d3b5b7e8caa184404d0ea` merges main `f365ce7` into the previous head: an automatic merge by the orchestrator, no resolution. The reviewed code is unchanged.

`0e307d59e495c56eb705ee9484f83311b38ce8d9` merges main `c782949` into the previous head: an automatic merge by the orchestrator, no resolution. The reviewed code is unchanged.

`43136fbca4b5ba2a6f7f137f60cf67951a305c94` is this PR's head, unchanged: its code was already in it and main merged cleanly, so the orchestrator's script set this body without a push.

`a0bad333ed4e0db2a7609c3b6a1df18625242011` merges origin/main `daf8b349fd30cc60786eeca333a426b693aa4c5f` into `f7161d2030a7cb6265eff2f22408e6457a3e00bc`. f7161d20 merged origin/main `51cd5ec8a42abde3c223f22e9f4a0d5f35f8844a` into the repair commit `2135d8b92f24f1020dd2016b46f99249ae7af57c`, which sits on the round-2 head `2bf0e026397c99378c53d47a0a49c30927deefd9`. Neither merge had a conflict. The figures below were taken at f7161d20 unless a line names another head. `git diff --name-only f7161d20 a0bad333` lists only `dev/programme/delivery/3346.md` and `tests/card_browser.mjs`, so the second merge reaches no file these figures read, and no self-test re-ran for it. prepr re-ran at a0bad333 (Figures). origin/main daf8b349 at 2026-11-08T21:13Z.

## Round-2 repair (commit 2135d8b92f24)

The verdict: `tools/plan/replan.py` `dispatch_tier` kept the base's hotfix predicate, `k == "bug" or "HOTFIX" in g and cls == "production"`. Under it an instrument-class R10-HOTFIX group fell to the instrument tier (6), below outside (3). Every other orderer ranked it above outside. Chosen fix: `dispatch_tier`'s hotfix arm is now `roster_lib.is_hotfix(group)`, the predicate `dispatch_rank` already applies. Rejected alternative: keep the class condition and get the owner's word that a non-production hotfix ranks below outside in the plan only. The ruling says "unless i call the owner one a hotfix", and a HOTFIX name is that call, so the plan has no reason to differ from the opener, the gate lease or the OWED list.

Enumeration rule for hotfix predicates, a different rule from the ordering-site grep in round 1: `grep -rnE '"HOTFIX"|R10-HOTFIX-|r10-hotfix-|is_hotfix|== "bug"' tools/ --include=*.py --include=*.mjs --include=*.sh`, with `_selftest.py` files and comment lines dropped. Each seam it returns, and its disposition:
- replan.py `dispatch_tier`: closed in this diff (`roster_lib.is_hotfix`).
- roster_lib.py `is_hotfix` / `dispatch_rank`: the owner of the predicate, unchanged. gate_priority `derived_priority` and orchestrator_tick `owed_levels` reach it through `dispatch_rank`, so they were already guarded.
- open_driver.py `default_class`: closed in this diff. It took a hotfix by topic or group name only. It now also takes the roster's `is_hotfix` set, passed through `order` and `run_pass` the same way the outside set is, so a `kind` "bug" group counts too. This is the verdict's minor finding.
- merge_train.py `drain_order`: closed in this diff. The rule returned it, and the verdict did not name it. Before this commit the drain read a hotfix only from the `--priority` flag, so a roster hotfix spooled without the flag drained behind outside entries. `Train._hotfix` (`roster_lib.is_hotfix` through the same `_roster_group` mapping, branch then `resume.pr`) now puts it in the `--priority` tier. `_outside` and `_hotfix` share one `_roster_is` reader.
- The other hits are comments, strings in fixtures or messages, or group names quoted as provenance: agreement.mjs:590, gh_comment.py:506, and merge_train.py at the R10-HOTFIX-TRAIN-DEFER-WAIT docstrings and comment. None of them decides an order.

Other verdict findings, closed in commit 2135d8b9:
- orchestrator_tick `owed_levels` maps a PR to its group by `group_for_branch`, else by `group_for_pr(roster, n)`, as `merge_train._roster_group` does, so a fork-head outside PR keeps its rank. gate_priority `derived_priority` gets no fallback: it runs before a pull request exists (prepr step 1b0) and receives a branch, not a PR number.
- `tools/audit/seat/instruments/merge_train.py.md` now states the drain order: `--priority`, roster hotfix or `--front`; then outside; then critical path; then arrival. It also states the branch-then-`group_for_pr` mapping.

## Mutation proof

Each mutant ran from a `git archive` of f7161d20 with the owner file's own `--self-test`. The script is `mut.sh` in the seat's scratch, a one-off, so it stays out of the tree. Lines are `name: mutation -> result, failing check`:
- replan-base-arm: `if roster_lib.is_hotfix(group):` restored to the base's `if k == "bug" or "HOTFIX" in g and cls == "production":` -> KILLED. It fails `an instrument-class R10-HOTFIX group is the hotfix tier and holds the one real slot at t0 ahead of an outside group ...` with `{'OUT': ('2026-01-05T00:00:00Z', 0, None, 3), 'R10-HOTFIX-X': ('2026-01-05T18:00:00Z', 0, None, 6)}`. That is the verdict's misordering: OUT holds the slot and the hotfix waits 18 h. The in-tree `tier-hotfix` mutant check also fails, because its anchor is the line this mutant removed.
- od-hotfix-set: `if group and roster_lib.norm_group(group) in hotfix:` -> `if False:` -> KILLED. It fails `run_pass: a kind-bug group with no HOTFIX name opens ahead of an outside group, cap 1`.
- od-hotfix-wiring: `run_pass` drops the `hotfix` argument to `order` -> KILLED by the same check.
- ot-fork-fallback: `or rl.group_for_pr(roster, n)` deleted -> KILLED. It fails `OWED buckets: a fork-head outside PR, mapped by resume.pr, prints before the critical path's; unrecorded, after it`.
- mt-drain-hotfix: `or self.hotfix(items[id(e)])` -> `or False` -> KILLED. It fails `P420 drain_order: a roster hotfix with no --priority flag (#8) drains ahead of an outside entry (#31)`.
- mt-hotfix-pred: `_hotfix` reads `is_outside` instead of `is_hotfix` -> KILLED by the same check.
Restored, each of these self-tests is 0 failed at f7161d20 (Figures). The earlier rounds' mutants stand as recorded at d21a15eb and 51838e6d, including the overflow-arm-order proof.

## Null control

Each new check has a null arm that would print the opposite result had the predicate been absent:
- replan: `null control: the same instrument without a HOTFIX name stays the instrument tier`.
- open_driver: `run_pass null: the same group with no kind waits behind the outside group` (it launches `r10-out`).
- orchestrator_tick: the same fork PR with `resume.pr` unrecorded prints after the critical path's (`[#100, #104]`).
- merge_train: `P420 drain_order null: the same group without a HOTFIX name drains behind the outside entry` (`[31, 7, 8]`).
The live-roster count below has its own null control: the pre-repair head 2bf0e026, run with the same script on the same roster, prints 7.

## Figures

- Live roster, command `python3 -I tiers.py <tree> wave-r10-groups.json`. The script is a one-off in the seat's scratch. Rule: for every roster group where `roster_lib.is_hotfix` and `roster_lib.is_open` hold, count those whose `replan.dispatch_tier(g, False, g.get("savings"))` is not `TIER_HOTFIX`. Roster `handoff/audit-r10-roster` 93fd3041c1f1 at 2026-11-08T20:51:39Z. At f7161d20 it prints `open is_hotfix groups 9; not TIER_HOTFIX in replan 0`. At 2bf0e026 it prints `... 9; ... 7`, the same seven groups the verdict lists: GATE-BUSY-DEFER, CODEQL-HEADROOM, TRAIN-DEFER-WAIT, AUTHOR-EMAIL, NONREQUIRED-REDS, ROSTER-LINT-REFRESH and PREPR-SELFTEST-DARWIN. The verdict counted 8 open at roster 6fb2599d. The roster has moved since, so the open count is the roster's, not this diff's.
- Two-group fixture with slots=1, R10-HOTFIX-X (kind instrument) and OUT (source outside), read with `build_plan`. At 2bf0e026: OUT is on slot 0 at t0 and the hotfix starts at t0+18 h, tiers 3 and 6. At f7161d20: R10-HOTFIX-X is on real slot 0 at t0, tier 2. OUT is the taller group, so it is the critical path, and it starts beside the hotfix at t0 flagged exempt.
- Self-tests at f7161d20, each printed by its own `--self-test`, all 0 failed: replan `self-test: 0 failed`; gate_priority 15 checks; roster_lib 71; orchestrator_tick 286 (285 plus the fork-head check); merge_train 574 (main's checks plus this diff's two drain checks); plan_page 67; open_driver 86 (84 plus the two run_pass checks).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. `tools/audit/archscore/score.py --diff 2bf0e026` at 2135d8b9: `Architecture score: dS +0.0000 NULL`.
- Scope: `tests/closure.py select --diff 51cd5ec8` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, and `scope.run` names `tests/entities.py`, which needs the real Home Assistant package (see the round-2 evidence) and is left to CI.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body.md>`, body check included: rc=0 at f7161d20. Main then moved to daf8b349, so origin/main was merged and prepr was re-run at a0bad333 (next line).
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body.md>` at a0bad333, body check included: `PRE-PR: a0bad333ed4e... rc=0` at 2026-11-08T21:14:57Z, and origin/main was still daf8b349 when the run ended.
- The three-dot diff against 51cd5ec8 touches no `VERSION`, manifest, `RELEASE_NOTES.md`, `tests/golden/` file or `*budgets.json`.

## Red checks

At the round-2 head 2bf0e026, every check run concluded success, skipped or neutral (verdict evidence, 55 runs). The three reds below come from earlier heads and are answered as they were.

`governance / instrument-self-tests` (job 128661348216): red. Cause: `python3 -I tools/plan/replan.py --self-test` failed on the PR merge ref (refs/pull/3304/merge, 5259a4c4) with `FAIL dispatch follows the owner's order ... ['CPA','CPB','CPC','R10-HOTFIX-H','OUT',...]`, then `FAIL the unmutated copy's self-test exits 0`. The head alone passed and origin/main alone passed; the merge failed. Main's build_plan ran its critical-path overflow arm before the tiered pick, so critical-path groups took the real slot ahead of the hotfix and outside groups this diff ranks above them. This diff owned the red. Repaired above: origin/main merged in, the tiered pick runs first, replan self-test 0 failed at 4c4dd755. Cheaper detector: running the self-test on `git merge origin/main` of the head. It exists as this CI job; tools/pr/prepr.sh runs on the head unmerged. By the owner ruling of 2026-11-07 it is not rerun when main moves, so no pre-push detector covers a main-side scheduler change landing after the push. Standing cost of a merged-tree self-test pass in prepr: one replan.py run, about 85 s. Carry: dismissed: the merge train recarries and re-proves the head on current main under the owner ruling, so a prepr merge step would repeat that proof.

`pr-contract / pr-contract` (job 128661350034): red. Cause: `[pr-body] check governance / instrument-self-tests is red and ## Red checks does not name it`, the only error; the body said `none`. This diff did not cause it beyond the red above; this section names the check. Cheaper detector: `tools/pr/prepr.sh --body-check`, which exists and reads the red-history from the check-runs. It ran before the red existed, so it could not name it.

`gate` (job 128661143751): red at `Judge this head`, one line: `FAIL pr-contract / pr-contract: failure`. A consequence of the pr-contract red above; no separate cause and nothing to detect.

`tests / fast (3.14)` (check-run 129330845342, job 129330845342, head `62f90fcb3bd8`): red, and it is main's red inherited at 2f6d699e, not this diff's. Cause: `tests/entities.py` (3 of 2707 checks) and `tests/harness_headers.py` (3 of 112) failed; the log shows `FAIL de.json has exactly strings.json's keys` for `options.step.entities.sections.indoor.data.flow_heat_c`, `flow_min_lift_k` (data and data_description) and `selector.space_setpoint_unit.options.return`, the two flow-field label/description checks in de.json, and D6 claim C112 false (`claims_true` 122 against 123), which fails the byte-identical harness output check. Main's own tests/fast run at 2f6d699e (job 129291622423) prints the same de.json and D6 lines. The skew is between #3372/#3360 and #3331: keys missing from de.json and from the card's German dictionary. The fix is hotfix #3378. This branch inherited it through a recarry onto red main and touches none of de.json, strings.json, the card or D6. Process state (d): the process was sound and main's state changed underneath the recarry. Cheaper detector: none on this branch, since the branch does not touch those files; the detector for the skew is the tests/fast run that caught it on main. Carry: dismissed: the fix is #3378 on main and the train recarry re-proves this head on the repaired main.

## Forward-carry

Splitting hotfix from outside inside the gate lease needs PRIORITY_MAX above 2 in tests/gate_lock.py (a different seam); not done here, hotfix and outside share band 2. Carry: dismissed: the lease has three bands and arrival orders within one, a hotfix waits behind an older outside run for one lease at most, and raising PRIORITY_MAX changes the aging rule for every waiter, so the split is not worth building without a measured wait

## Friction

fixer-step-push: contradiction: refs/heads/handoff-wip/r10-outside-first still holds a prior seat's BLOCKED commit 4a66cde5, which is not an ancestor of this head. A fast-forward step push is impossible, so none was made and nothing was forced. This seat hands off directly. Carry: dismissed: the brief deletes the step ref after the handoff, which clears it for the next seat
mutant-cmd-scope: cost: one MUTANT_CMD runs one self-test over the mutants of every changed file, so on a multi-file diff the prepr count reports the command's reach, not the pins. This round's proof is per file (above). Carry: dismissed: per-file runs by `--path` already exist in mutant_run.py, and a seat that reads its survivors per file finds the gap in one listing

## Unpinned sites

Every remaining survivor from the per-file runs, by disposition:
- Self-test lines (a mutant there weakens a fixture or deletes one check; no production behaviour moves). These are value checks in the instrument's own self-test, and `mutation-autofix` mutates `custom_components/` only. gate_priority.py:231 (`>` to `>=` in the check). roster_lib.py:894 and :914 (fixture constants in the is_outside and group_for_pr checks). replan.py:755, :761, :762 and :766 (tier-check bounds and constants). replan.py:792 is tightened from `slot < 1` to `slot == 0` at 4c4dd755 and not re-run by the instrument. All 9 open_driver_selftest.py sites (:114, :118, :119 x2, :120 x2, :122, :124, :126), a test-only file. All 15 merge_train.py sites (:4010 x2, :5572, :5574, :5585, :5588, :5591, :5592, :5597, :5605 x2, :5607, :5615, :6961 x2), all inside `_self_test` (lines 3836 to 8396): the fixture default `outside=lambda it: False` and fork-head fixture constants.
- Equivalent: roster_lib.py:657 RETURN_DEL. `continue` becomes `pass` as the last statement of the loop body, so the next iteration follows either way. orchestrator_tick.py:897 CONST_SWAP. The no-roster default rank `3` becomes `4` only on the arm where every item gets the same constant, so the sort by PR number is unchanged.
- Round 3 (2135d8b9): every production line this commit adds is pinned by a killed mutant above: replan's hotfix arm, open_driver's hotfix set and its wiring, the tick's fork-head fallback, and merge_train's drain term and `_hotfix` predicate. `_roster_is` is the body `_outside` already had, and the P420 `_outside` checks pin it. The new lines in the test files and the instrument doc are fixtures and prose.

