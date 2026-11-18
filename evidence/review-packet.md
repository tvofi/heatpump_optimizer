# Review packet #3717
head: bdc3a77df7fea249cecf09581813d3726ea3d070
base: 83b9012d61eb9dba11c265cf987dd1d5960c8c96

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=134652489401 success
arch-score / arch-score id=134662504117 success
arm id=134652092720 skipped
budget-raise-gate / budget-raise-gate id=134662532637 success
cancel-superseded id=134662502817 success
codeql id=134662503987 skipped
codeql / Analyze (actions) id=134652406857 success
codeql / Analyze (javascript-typescript) id=134652406917 success
codeql / Analyze (python) id=134652406888 success
gate id=134662502447 success
governance id=134662574506 skipped
governance / env-matrix id=134652406957 success
governance / instrument-self-tests id=134652406943 success
governance / policy-docs id=134652406946 success
governance / record id=134652408542 skipped
governance / wave-script id=134652406934 success
hassfest id=134662545690 skipped
hassfest / hassfest id=134652407154 success
kernel-points id=134662555533 skipped
pr-contract id=134662504307 skipped
pr-contract / pr-contract id=134661415909 success
prelude id=134662561428 success
refresh id=134662569011 success
sweep-self id=134662996627 skipped
tests id=134662504585 skipped
tests / arch-instrument id=134652744860 success
tests / briefs id=134652406826 success
tests / browser id=134652744751 success
tests / ci-ratchet id=134654647342 skipped
tests / claims-autofix id=134654647606 skipped
tests / closure-scope id=134652407059 success
tests / closures id=134652744907 success
tests / closures-autofix id=134654403187 skipped
tests / coverage id=134652744727 success
tests / coverage-ratchet id=134653442845 success
tests / fast (3.14) id=134652744697 success
tests / graders-head-copy id=134653442861 success
tests / lane-proofs id=134654852633 success
tests / mutation id=134652407064 success
tests / mutation-autofix id=134652811470 skipped
tests / mutation-pins id=134652811631 skipped
tests / nightly-ha id=134652747374 skipped
tests / nightly-status id=134652406999 failure
tests / replay id=134652746919 skipped
tests / typing id=134652744743 success
validate id=134662524092 skipped
validate / validate-hacs id=134652406921 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: SCOPED -- 0 script(s) run, 33 scoped out.
             no segment of this names a program this check knows
  unverified git diff --stat 7c2f4c30ca 345d32d62de2677080b66c8035540c09e5d7d3d9
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 0 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/programme/delivery/3717.md b/dev/programme/delivery/3717.md
new file mode 100644
index 0000000000..8ecf60c16a
--- /dev/null
+++ b/dev/programme/delivery/3717.md
@@ -0,0 +1 @@
+- [#3717](https://github.com/tvofi/heatpump_optimizer/pull/3717) — **open**, R11-OUTSIDE-HONEST-STARTS-RUNS-P3: #3529 rebased onto main (R11-OUTSIDE-HONEST-STARTS-RUNS-P3)
diff --git a/docs/design/2026-11-12-honest-starts-and-runs/design.md b/docs/design/2026-11-12-honest-starts-and-runs/design.md
index 721abadec9..535a9a32fd 100644
--- a/docs/design/2026-11-12-honest-starts-and-runs/design.md
+++ b/docs/design/2026-11-12-honest-starts-and-runs/design.md
@@ -130,7 +130,7 @@ Base `870238eb21` (v7.1.12, with #3461 merged). Where the build differs from the
 - **P2, commit.** The relaxed multi-start runs with the start term off (`_start_term_off`). The count is bilinear in neighbouring steps, and a descent priced with it stayed where its start lay: a trickle it did not leave, or one run it did not break. `_commit_runs` then builds the candidates (`_run_plans`): the per-step projection, raised and rounded; each band's `runs.commit` mask (`BANDS`, widening to the whole horizon; a balance outside its band is penalised by `OUT_OF_BAND`, never refused); the relaxed plan where it already runs. It scores all of them in one `objective_batch` call on the true objective with the start term, re-solves the levels of the best two inside their runs, polishes the better one (`_pinned_runs`) and ships the lowest score. So no plan ships worse than the projection, and a failure anywhere in the stage ships the projection. A committed space step runs at the floor or above on its own, also beside a hot-water charge: the plan stays one the pump can run when the combi exchange moves the charge afterwards. On an install that can duty-cycle, a step capped under the floor still cycles; on one that cannot, it stays off.
 - **P3, the floor.** The floor store admits only asks at or under the configured floor × (1 + `AGREE_TOLERANCE`), and each sample lapses on its own age, so an engaged plan cannot ratchet the floor: it lapses back to the configured figure and is learned again. Persisted as `draw/floor`.
 - **P4, hot water.** `runs.commit_store` is a program on the planner's linear store (`runs.Store`, 0.25 K grid). A charge runs whole steps at the run power and may end inside its last step where the store is full: the pump runs at its level and stops, so that step is no level under the floor (a tail). A charge that starts in the step it ends in is a whole run and must last `MIN_ON`. On an install that cannot duty-cycle a tail stays at the floor or above, the level contract `clamp_planned_levels` has today. A step without a charge is not bound by the charge ceiling, because a combi store's space side heats it past, and stops at the store's rating, as `thermal_model.store_step` does. Without those two rules the program had no feasible path in most exchange rounds on the reporter's install and the planners' trickle plan shipped. What a charge pays besides its energy follows the compressor (`_charge_costs`): a start where it is off, the learned share of one for each duty change where the space plan runs. The hot-water plan that ships is the cheaper, in energy at the planning prices plus starts, of the committed plan and the planners' own plan with every step under the floor run at the floor (`_commit_charges`); so an engaged plan holds no charge step under the floor but a tail. Limit: the program charges at the run power only, so a modulating pump's long part-load charge comes from the second candidate.
-- **Combi store.** The space plan is not re-solved after the flux exchange. Charges move the store in whole steps, the space side's flux moves with the store, and the rounds need not settle: `_held_round` keeps the round whose store, walked by the model, falls least under the requirement, and of those the cheapest. `_settled` then settles the space plan against that hot-water plan. The space plan was solved around the first hot-water plan; the exchange's charges hold the store afterwards; the space runs still carry heat for a store those charges had not warmed (measured on the reporter's install: one hour at 3.4 to 3.5 kW into a store at its 55 °C limit), and a charge that left its step leaves a pause in the space run it sat in. Each space run is tried switched off and lower (`_TRIM_SHARES`), each pause run through at the floor. A candidate is kept only where the pair's objective on the model's own walk is lower and the store falls no further under the hot-water requirement, the promise a free re-solve cannot make. An unengaged solve does not run this stage and is byte-identical; its plans hold the same double heating, a finding for R10-COMBI-TANK that this pull request does not act on.
+- **Combi store.** The space plan is not re-solved after the flux exchange. Charges move the store in whole steps, the space side's flux moves with the store, and the rounds need not settle: `_held_round` keeps the round whose store, walked by the model, falls least under the requirement, and of those the cheapest. `_settled_space` then settles the space plan against that hot-water plan. The space plan was solved around the first hot-water plan; the exchange's charges hold the store afterwards; the space runs still carry heat for a store those charges had not warmed (measured on the reporter's install: one hour at 3.4 to 3.5 kW into a store at its 55 °C limit), and a charge that left its step leaves a pause in the space run it sat in. Each space run is tried switched off and lower (`_TRIM_SHARES`), each pause run through at the floor. A candidate is kept only where the pair's objective on the model's own walk is lower and the store falls no further under the hot-water requirement, the promise a free re-solve cannot make. An unengaged solve does not run this stage and is byte-identical; its plans hold the same double heating, a finding for R10-COMBI-TANK that this pull request does not act on.
 - **Duty-switch price** (R10-DUTY-SWITCH-PLANNER-PRICE). `duty_switch.planner_reading` is the reader and the coordinator its one caller: per direction `Direction.p` while `usable`, else 0.0, into `OptimizationConfig.duty_stop_to_space` and `duty_stop_to_dhw`, priced by the start count and by the charge program. The `median_off_s` headroom cut is not built.
 - **`dhw_floor_breach_c`** is published under a block always, and on a solve that plans runs when a cap leaves some step under the pump's floor and the tank falls short.
 - **Tried and dropped, measured.** A store-hold term in the space objective (the space channel carries the store through the hot-water window): 16 % cheaper in the model, L-BFGS-B up to 24 s, and on a stratified combi store heating mode does not raise the top sensor. A hot-water re-plan pass on every priced solve with a separate tank: the same starts and costs on eight golden variants, more solve time.
@@ -156,7 +156,7 @@ Tap temperature inside the window is 47.0 °C or above on every row, base and he
 
 ## Solve time, as built
 
-One machine (2 cores, x86), base → head, wall seconds for one `optimize`. The fourteen golden variants above sum to 15.8 → 15.3: `cycling_cost` 1.04 → 0.20, `everything_on` 3.00 → 3.43, `winter_two_zone_dhw` 1.25 → 1.46, `valve_storage` 4.01 → 4.61, `shoulder` as on_off 0.96 → 1.76. The reporter's install: 0.8 to 3.8 → 1.5 to 1.8 at 0.25 per start, 5.3 to 6.4 → 1.5 to 1.8 at 10. The relaxed solve without the start term converges sooner than the priced one did; the commit stage adds two warm L-BFGS-B runs and one polish; `_settled` adds about twenty walks of the pair at about 3 ms each. `tests/stress.py` passes.
+One machine (2 cores, x86), base → head, wall seconds for one `optimize`. The fourteen golden variants above sum to 15.8 → 15.3: `cycling_cost` 1.04 → 0.20, `everything_on` 3.00 → 3.43, `winter_two_zone_dhw` 1.25 → 1.46, `valve_storage` 4.01 → 4.61, `shoulder` as on_off 0.96 → 1.76. The reporter's install: 0.8 to 3.8 → 1.5 to 1.8 at 0.25 per start, 5.3 to 6.4 → 1.5 to 1.8 at 10. The relaxed solve without the start term converges sooner than the priced one did; the commit stage adds two warm L-BFGS-B runs and one polish; `_settled_space` adds about twenty walks of the pair at about 3 ms each. `tests/stress.py` passes.
 
 ## Notes for the fixer
 

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
