R10-TRUST-RELATIVE. Part of #2252 (the group's `fixes` list is empty, so this pull request names the issue without a closing keyword).

STUDY R10-RESEED found the heat-loss learners' trust region fixed in multiplier units. `learner_newton_step` (`thermal_model.py`) clipped the Newton target to `current +- trust_region`. In UA that is a bound of `base_u * trust_region`: it scales with the configured nameplate, so the walk depended on how one house's UA was split between the settings and the multiplier, and moving the learned value into the settings (a reseed) changed nothing but the step size. Turning the trust region off made the reseed an exact re-parameterisation (ratios 1.0000).

**What changed.** One relative clamp: the bound is now `current * trust_region` (`reach` in `learner_newton_step`), which in UA is `current_u * trust_region` whatever the split. `_LEARNER_TRUST_REGION` keeps its value, 0.5, and its comment in `coordinator.py` now says it is a fraction. Both learners (the house scale and the lower-floor ratio) take the same step, so both change, and neither call site is touched. At `current = 1.0` the bound is the same as before. The EWMA (`alpha`) and the rate limit (`max_step_fraction * current`) were already linear in UA, so the whole step is now invariant to the split.

**What it costs, measured.** The study's paired figures settle the trade-off. On one closed-loop trajectory, the reseeded arm B at the baseline has the head's bound at the reseed: `U * 0.5`, where its multiplier is 1.0. Its bound departs from the head's as its multiplier moves off 1.0 (not measured here). So B/A at the baseline approximates what the fix does to an unreseeded install, paired on one trajectory. Re-taken at merge base `768bfc0c3` (see `## Figures`): an install whose learned value is above its prior (`sz_157`, prior 1.57x too low) gets steps wider in UA: house UA std x1.0483, forecast MAE x1.0693. One below it (`sz_060`) gets narrower ones: UA std x0.5106, forecast MAE x0.8259. The two-zone `tz_157_192` gets UA std x0.8667, forecast MAE x0.8272. On the owner's two stores (open loop, paired), the as-is arm's UA std rises x1.09 (house) and x1.28 / x1.03 (lower), and forecast MAE moves by at most x1.0012. That is the price of the step no longer depending on what the user typed into the settings: the step is now `alpha * trust_region` = `HOUSE_LOSS_ALPHA` 0.02 x `_LEARNER_TRUST_REGION` 0.5 = 1 % of the current UA per saturated sample, whatever the install's settings.

**Alternatives considered.**
- Keep the bound absolute and re-express it in UA (`trust_region * base_u_at_prior`). That needs the prior's UA at the step, a second input carrying the same concept. Not taken.
- Delete `max_step_fraction`. With a relative trust region the per-sample move is at most `alpha * trust_region * current` (0.02 x 0.5 = 1 %), inside the `HOUSE_LOSS_MAX_STEP` = 0.05 (5 %) limit, so at the shipped constants the limit cannot bind. It also could not bind before on production values, since `_apply_*` holds `current >= 0.3` and the old move was at most 0.01 against a limit of 0.015. Deleting it changes both call sites in `coordinator.py`, which the architect note leaves outside this seam, and three in-tree harnesses pass the keyword (`dev/audit/rounds/round10/D14/sweep-N-confounded-learner/enumerate.py`, `dev/audit/rounds/round10/study-reseed/reparam_sites.py`, `dev/audit/rounds/round9/D2/s4/newton_bias.py`). Left in place, with the check that drives it now given a walk wide enough to reach it. Reported to the orchestrator as a separate finding.

## Head

`536080c084c3ea201db13860c29bcca577fac5db` merges the authored code head `5337d23ea3f0685786467e7f5734d11e2c4be2b1` and then merges origin/main `1bcc79884` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head, and then adds one commit containing only this PR's own row, `dev/programme/delivery/2435.md`.

`5337d23ea3f0685786467e7f5734d11e2c4be2b1`. It is `ebeda1c0d` plus one bot commit, `5337d23ea` `ci: pin killed mutants` (mutation-autofix job 117935930654), which adds one file, `tests/mutation_ledger/.../thermal_model.py/learner_newton_step.CLAMP_DROP.b43f81ae.json`, and touches no production or test code. `ebeda1c0d` merges origin/main `768bfc0c3` into the authored code head `06bbc1ec6` (an automatic merge by the orchestrator's script, no conflict). `06bbc1ec6` merges origin/main `07a09406a` (no conflict) into `ebd441f9f`, three commits over the first merge base `176851e95`: `72a653788` (the fix, the new checks and the new harness), `7326bfe2a` (the #193 replay pin follows the relative law) and `ebd441f9f` (`tests/closures.json`: `harness_headers.py` lists the new harness, written by `python3 tools/pr/ci_predict.py --apply-inert`).

Merge base `768bfc0c341dc925fbfa6fb8af9c8d057a1500b2`. origin/main's tip at the re-take was `db3293dcb12fc48ae025cd32ef0148476939cfb9` (`date -u`: 2026-10-19T07:21Z). `git diff --name-only 768bfc0c3 db3293dcb -- custom_components tests/features.py tests/closures.json tests/harness.py tests/profiles.py tests/hastub` prints only `tests/closures.json`, so main's newer commits reach none of the production or test code the figures read.

What the last main merge (`07a09406a` to `768bfc0c3`) reaches: it changes `coordinator.py` (the #2391 ventilation CUSUM now fed the interval's heat and sun, with a reference fit), `const.py`, `optimizer.py` and others, and leaves `thermal_model.py` unchanged (`git diff 07a09406a 768bfc0c3 -- custom_components/heatpump_optimizer/thermal_model.py` prints 0 lines). The closed-loop rolling harness drives the coordinator's learners and optimizer, so every one of its figures below was re-taken at this merge base and this head. The base side moved (`sz_157` house_std 1.0457 at `176851e95` to 1.0483 at `768bfc0c3`). The open-loop bundle harness reads only `learner_newton_step`, `coord_mod.HOUSE_LOSS_ALPHA`, `HOUSE_LOSS_MAX_RESIDUAL`, `HOUSE_LOSS_MAX_STEP`, `_LEARNER_TRUST_REGION`, `_house_loss_terms` and the four `const.py` bounds (`grep -oE 'coord_mod\.[A-Za-z_]+'` over the harness lists those five). Over `07a09406a..768bfc0c3`, `git diff ... -- custom_components/heatpump_optimizer/ | grep -E '^[-+]' | grep -cE '_LEARNER_TRUST_REGION|HOUSE_LOSS_|LOWER_FLOOR_LOSS|LOWER_LOSS|HOUSE_HEAT_LOSS_SCALE|ThermalParameters'` prints 0, and the sha1 of `ast.unparse(_house_loss_terms)` is `a278caeb3f942d2eae9dc5fa5ac7fbe701279c6b` at both commits (a printed hash, so the function was found at each). Its figures carry from `72a653788` unchanged.

Merges with each open pull request sharing a file (`gh pr list --state open`, files intersected with this diff's five), by `git merge-tree --write-tree 5337d23ea <pr-head>` in a checkout with the repository's `.gitattributes` drivers configured. Each prints a tree and no conflict:
- #2368 at `87eda8c592e45a07d6388638856888ad113554dd` (shares `thermal_model.py`, `coordinator.py`, `tests/features.py` and `tests/closures.json`): tree `27244e3d640ade284fe5e0bf4216bbd34ba03c37`.
- #2415 at `e584e4f1e2cb1e6fe1be1edff19c62be070b3eb1` (shares `tests/closures.json`): tree `c6056ac8713224b781aaa58b1ec4c1b7970ec613`.

With the driver disabled (`git -c merge.ledgermerge.driver=false merge-tree --write-tree --name-only`), both report a content conflict in `tests/closures.json` and nowhere else; `tools/merge/ledger_merge.py` resolves it by merging `inert_reads.tests/harness_headers.py` as a set. GitHub does not run that driver, so whichever lands second needs its main merge done locally (fixer.md step 6).

## Mutation proof

Mutant: the fix's production line, `reach = current * trust_region`, replaced by `reach = trust_region` (the absolute bound restored) in the real worktree at `5337d23ea`. Then `PYTHONPATH=tests/hastub python3 tests/features.py` was run in full and the file restored (`git status --porcelain` empty after). It printed `3 of 4215 FEATURE CHECKS FAILED`, rc 1:
- FAIL `the extracted Newton step leaves the learned scale unchanged` (`scale 0.8999999999999999`, the real learner through `_async_learn_house_heat_loss`)
- FAIL `the trust region saturates at a fraction of the current estimate` (`target 2.5, bound 3.0`)
- FAIL `and a saturated step in UA does not depend on the prior/multiplier split` (`UA 0.40199999999999997 at (0.2, 2.0), 0.404 at (0.4, 1.0)`)

The unmutated run at `ebeda1c0d` (production and tests identical to `5337d23ea`) prints `ALL 4215 FEATURE CHECKS PASSED` (rc 0), the control.

Failing test first: the new checks in `tests/features.py`, run before the production line was written (production = the first merge base's), FAILed `the trust region saturates at a fraction of the current estimate` (`target 2.5, bound 3.0`) and `and a saturated step in UA does not depend on the prior/multiplier split` (`UA 0.40199999999999997 at (0.2, 2.0), 0.404 at (0.4, 1.0)`). `thermal_model.py`'s fix hunk and those checks are unchanged since.

## Unpinned sites

- custom_components/heatpump_optimizer/thermal_model.py:1938 CLAMP_DROP (`target = float(np.clip(target, current - reach, current + reach))`, the trust region itself). Pinned by mutation-autofix at `5337d23ea`: the `mutation-pins (1)` job 117925381293 printed `pinned custom_components/heatpump_optimizer/thermal_model.py:1938 CLAMP_DROP -- killed by tests/features.py` and `PIN KILLED: 1 pinned, 0 left unpinned`. The site is new only because its text changed: the line it replaces, `current - trust_region`, was the same clamp.

## Null control

- The forward-carried null control: a house whose settings already match the learned values (the `reseeded` arm, current 1.0) shows the same learner variance and forecast error before and after. On the owner's two stores, head/base: house UA std x1.0011 / x1.0012, lower x1.0006 / x1.0000, and forecast MAE x1.0000 on every learner (bundle harness; inputs unchanged since, see `## Head`).
- `--learned 1.0` (prior already right): reseeded/as-is ratios 1.0000 at both ends (bundle harness).
- `--trust-region 1e9` (the study's perturbation): ratios 1.0000 at both trees, in both harnesses; the rolling arm was re-taken at `768bfc0c3` and this head (`## Figures`).
- The study's own null plants, re-taken: at this head `sz_null` and `tz_null` read B/A 1.0000 on every metric. At the merge base they read 0.9626-1.0006, because the learned value drifts off 1.0 by the reseed day.

## Figures

Rolling-harness figures come from the finder's harness `reseed_rolling.py` from study/r10-reseed at `2c42ba4a0`, run as `$EXPORT/tools/audit/round10/study-reseed/reseed_rolling.py` (sha1 `030df96abe88d7b12132798518bc92e466391d99`). Command (from each tree's root): `PYTHONPATH=tests/hastub python3 $EXPORT/tools/audit/round10/study-reseed/reseed_rolling.py --plant P` (defaults: sigma 0.1, 10 days, reseed day 4, reset day 7, seed 20261014), each rc 0. Base = a `git archive` of the merge base `768bfc0c3`, head = this worktree at `ebeda1c0d` (production identical to `5337d23ea`). Ratios `ratio_B_over_A.<metric>_post`, base -> head:
- `sz_157`: house_std 1.0483 -> 1.0000, house_rmse 1.0227 -> 1.0000, fc_mae 1.0693 -> 1.0000 (the finding).
- `sz_060`: 0.5106 / 0.7799 / 0.8259 -> 1.0000 / 1.0000 / 1.0000.
- `tz_157_192`: house_std 0.8667, house_rmse 0.8204, fc_mae 0.8272, lower_std 0.8831, lower_rmse 0.8540 -> 1.0000 on all five.
- `sz_null`: 0.9629 / 0.9626 / 0.9652 -> 1.0000. `tz_null`: 0.9980 / 0.9972 / 0.9989 / 1.0006 (lower_std) -> 1.0000.
- `--trust-region 1e9`, `sz_157` and `tz_157_192`: 1.0000 at both ends on every metric above (the perturbation).
- Arm A across trees (`<plant>.A.<metric>`, head/base) is not paired. The optimizer plans with arm A's model, so the closed loop runs a different trajectory at each tree. The paired, within-run ratios above are the measurement; the open-loop bundle harness below is the cross-tree one.

Bundle figures come from `dev/audit/harnesses/r10_trust_relative_bundle.py` (sha1 `a8d7fd845bcaca2815d88bbbca75abb032150737` at this head), run on the owner's two diagnostics bundles that carry stores, at `176851e95` and `72a653788`. Their inputs are unchanged at this head (`## Head`), so they carry. The bundle path is given on argv and nothing from a bundle is committed. Store 1: learned scale 1.2878, ratio 1.7971. Store 2: 1.5667 / 1.9223. Both two-zone. Command: `PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/r10_trust_relative_bundle.py BUNDLE.json` (4000 samples, sigma 0.1, dT 20 K, dt 0.25 h, seed 2252). `ratio_reseeded_over_as_is`, base -> head:
- Store 1: house ua_std 1.0900 -> 1.0000, ua_rmse 1.0935 -> 1.0000, fc_mae 1.0006 -> 1.0000; lower 1.2781 / 1.2818 / 1.0012 -> 1.0000 / 1.0000 / 1.0000.
- Store 2: house 1.0880 / 1.0903 / 1.0006 -> 1.0000; lower 1.0262 / 1.0300 / 1.0000 -> 1.0000.
- Per arm head/base, store 1 / store 2. `as_is` house ua_std x1.0911 / x1.0893, lower x1.2789 / x1.0262, fc_mae at most x1.0012. `zero_evidence` (an install with no evidence) house ua_std x0.9993 / x0.9995, fc_mae x1.0000. `at_min` (current on the 0.3 clamp) house ua_std x0.5635 / x0.5941. `at_max` (on the 3.0 clamp) x1.3108 / x1.0923. fc_mae on every clamp arm within x0.9978-x1.0015. These are the learner at both ends of its input range (fixer.md step 3). On the clamp the step follows the UA, smaller at the floor and larger at the ceiling, and the forecast error does not move.

Class enumeration (fixer.md step 8). Rule: `git grep -nE "clip\(.*, *([A-Za-z_.]+) *- *[A-Za-z_0-9.]+ *, *\1 *\+ *[A-Za-z_0-9.]+" -- custom_components/` (every clamp centred on a current value with a symmetric half-width). It returns two seams, both in `learner_newton_step`:
- `np.clip(target, current - reach, current + reach)`: the trust region, closed in this diff (relative).
- `np.clip(updated, current - max_step, current + max_step)`: the rate limit, already relative (`max_step = current * max_step_fraction`). It is now dominated at the shipped constants, as disclosed above.

Outside that rule: `accuracy.py`'s `_clipped_refit_scale` (the batch refit) clips against the global bounds `HOUSE_HEAT_LOSS_SCALE_MIN/MAX`, not a trust region about the estimate, and is untouched. The `_apply_house_heat_loss_scale` / `_apply_lower_floor_loss_ratio` bounds are global multiplier bounds, a different concept and not a step bound; untouched. The last main merge added no `np.clip` about a current value (the #2391 hunk removed the vent feed's `np.clip(residual, -VENT_CUSUM_CLIP_C, VENT_CUSUM_CLIP_C)`, a fixed range, into `Cusum`'s `clip`).

At `5337d23ea`: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED` (rc 0). `python3 tools/audit/archscore/score.py --diff 768bfc0c341dc925fbfa6fb8af9c8d057a1500b2` prints `Architecture score: dS +0.0000 NULL`.

Scoped gate: `python3 tests/closure.py select --diff 768bfc0c341dc925fbfa6fb8af9c8d057a1500b2` prints `MODE: SCOPED -- 27 script(s) run, 6 scoped out.` at `ebeda1c0d` and at `5337d23ea`. Run locally with `PYTHONPATH=tests/hastub` at `ebeda1c0d` (production and tests identical to `5337d23ea`), each rc 0: `features.py` (`ALL 4215 FEATURE CHECKS PASSED`), `structure.py`, `golden.py` with `GOLDEN_MODE=drift` (`NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`), `edge.py`, `finite_boundary.py`, `boost_drift_replay.py`, `guard_pins.py`, `doc_claims.py`, `validate.py`, `solar_alignment.py`, `backtest.py`, `wood_advisor.py`, `manual_plan.py`, `debug_collect.py`, `harness_headers.py` (`ALL 109 HARNESS HEADER CHECKS PASSED`), `block_duty.py`, `config_flow_steps.py`, `deployment_shape.py`, `env_drift.py`, `plan_view.py`, and `entities.py` under `env -u BASH_ENV` (`ALL 2349 ENTITY CHECKS PASSED`). `stress.py`, `optimality.py`, `arch_score_head.py`, `typing_ruler.py` and the card scripts run in CI.

## Architecture score

`dS +0.0000 NULL` (no metric moved).

## Red checks

Every failure conclusion across the branch's commits (`commits/<sha>/check-runs` for each of `git rev-list origin/main..ebeda1c0d`; only `ebeda1c0d` had runs):
- `mutation` (job 117925103263, at `ebeda1c0d`): `MUTATION TABLE REFUSED -- 4208 unpinned site(s) against 4208 at the ratchet base 768bfc0c3, 1 of them added by this diff`, the site being `thermal_model.py:1938 CLAMP_DROP`. Cause: the fix rewrote the trust-region clamp's text, so its site key is new and carried no disposition. It is not a vacuous test (the mutant is killed by `tests/features.py`, `## Unpinned sites`) and not a pin broken by the main merge (the head's count, 4208, equals the base's: the one added site replaces the old clamp's, and no other site is added). The cheaper detector exists and fired: `prepr.sh` step 6d listed the site before the push, and the body's `## Unpinned sites` named it. The red is the designed trigger for `mutation-autofix`, which pinned it at `5337d23ea`; its standing cost is one CI round.
- `pr-contract` (job 117925247665, at `ebeda1c0d`): `check mutation is red and ## Red checks does not name it`. Cause: the body was written before any check ran and said `none`, although its own `## Unpinned sites` predicted the `mutation` refusal. A cheaper detector would be static: `policy_lint --pr-body` (or `prepr.sh` step 6d) could require `## Red checks` to name `mutation` whenever step 6d prints a site added unpinned. Its standing cost is one string match per body. It does not exist today; reported to the orchestrator for the root-cause seat, not built here. This body names both.

At `5337d23ea` CI was still running when this body was taken.

## Forward-carry

none. The two carried constraints are discharged above: the null control under `## Null control`, and the re-measure on the bundle stores under `## Figures`. The dominated rate limit is no constraint on a later stage. It goes to the orchestrator as a finding to dispatch, outside this group's seam.

## Friction

none

