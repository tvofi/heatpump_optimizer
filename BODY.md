R10-TRUST-RELATIVE. Part of #2252 (the group's `fixes` list is empty, so this pull request names the issue without a closing keyword).

STUDY R10-RESEED found the heat-loss learners' trust region fixed in multiplier units. `learner_newton_step` (`thermal_model.py`) clipped the Newton target to `current +- trust_region`. In UA that is a bound of `base_u * trust_region`: it scales with the configured nameplate, so the walk depended on how one house's UA was split between the settings and the multiplier, and moving the learned value into the settings (a reseed) changed nothing but the step size. Turning the trust region off made the reseed an exact re-parameterisation (ratios 1.0000).

**What changed.** One relative clamp: the bound is now `current * trust_region` (`reach` in `learner_newton_step`), which in UA is `current_u * trust_region` whatever the split. `_LEARNER_TRUST_REGION` keeps its value, 0.5, and its comment in `coordinator.py` now says it is a fraction. Both learners (the house scale and the lower-floor ratio) take the same step, so both change, and neither call site is touched. At `current = 1.0` the bound is the same as before. The EWMA (`alpha`) and the rate limit (`max_step_fraction * current`) were already linear in UA, so the whole step is now invariant to the split.

**What it costs, measured.** The study's paired figures settle the trade-off. On one closed-loop trajectory, the reseeded arm B at the baseline has the head's bound at the reseed: `U * 0.5`, where its multiplier is 1.0. Its bound departs from the head's as its multiplier moves off 1.0 (not measured here). So B/A at the baseline approximates what the fix does to an unreseeded install, paired on one trajectory. An install whose learned value is above its prior (`sz_157`, prior 1.57x too low) gets steps wider in UA: house UA std x1.0457, forecast MAE x1.0632. One below it (`sz_060`) gets narrower ones: UA std x0.5106, forecast MAE x0.8356. The two-zone `tz_157_192` gets UA std x0.8667, forecast MAE x0.8272. On the owner's two stores (open loop, paired), the as-is arm's UA std rises x1.09 (house) and x1.28 / x1.03 (lower), and forecast MAE moves by at most x1.0012. That is the price of the step no longer depending on what the user typed into the settings: the step is now `alpha * trust_region` = `HOUSE_LOSS_ALPHA` 0.02 x `_LEARNER_TRUST_REGION` 0.5 = 1 % of the current UA per saturated sample, whatever the install's settings.

**Alternatives considered.**
- Keep the bound absolute and re-express it in UA (`trust_region * base_u_at_prior`). That needs the prior's UA at the step, a second input carrying the same concept. Not taken.
- Delete `max_step_fraction`. With a relative trust region the per-sample move is at most `alpha * trust_region * current` (0.02 x 0.5 = 1 %), inside the `HOUSE_LOSS_MAX_STEP` = 0.05 (5 %) limit, so at the shipped constants the limit cannot bind. It also could not bind before on production values, since `_apply_*` holds `current >= 0.3` and the old move was at most 0.01 against a limit of 0.015. Deleting it changes both call sites in `coordinator.py`, which the architect note leaves outside this seam, and three in-tree harnesses pass the keyword (`dev/audit/rounds/round10/D14/sweep-N-confounded-learner/enumerate.py`, `dev/audit/rounds/round10/study-reseed/reparam_sites.py`, `dev/audit/rounds/round9/D2/s4/newton_bias.py`). Left in place, with the check that drives it now given a walk wide enough to reach it. Reported to the orchestrator as a separate finding.

## Head

`06bbc1ec61c8f1ea669d2de2fb98393213abeadb`. It merges origin/main `07a09406a1cc97076a6f28581f87f313b322a6b6` (no conflict) into `ebd441f9f`, which is three commits over the first merge base `176851e950a8bea29b0c06f1891b8ce4b83b8836`: `72a653788` (the fix, the new checks and the new harness), `7326bfe2a` (the #193 replay pin follows the relative law) and `ebd441f9f` (`tests/closures.json`: `harness_headers.py` lists the new harness, written by `python3 tools/pr/ci_predict.py --apply-inert`, which `prepr.sh` step 6d asked for). Merge base now `07a09406a1cc97076a6f28581f87f313b322a6b6` (`date -u`: 2026-10-18T21:57Z).

What the main merge reaches: `git diff --name-only 176851e95 07a09406a -- custom_components/heatpump_optimizer/thermal_model.py custom_components/heatpump_optimizer/coordinator.py custom_components/heatpump_optimizer/const.py tests/features.py tests/harness.py tests/profiles.py tests/hastub` prints nothing. Main's production delta is `climate.py`, `entity.py` and `sensor.py` (#2379), which neither harness reads, so the harness figures below carry from `72a653788` unchanged. Structure, the architecture score, the gate scope and `prepr.sh` were re-taken at this head.

Merges with each open pull request sharing a file, by `git merge-tree --write-tree 06bbc1ec61c8f1ea669d2de2fb98393213abeadb <pr-head>` in a checkout with the repository's `.gitattributes` drivers configured. Each has rc 0 and lists no conflict:
- #2368 at `86258e159d6e18b41aa0edafc79c6b8921d5c4dc` (shares `thermal_model.py`, `coordinator.py` and `tests/closures.json`): tree `ab884acc2072eb3ba19b5661796371337c3d5f27`.
- #2391 at `c1b085dba8a51f30d71468178541c74b0501f450` (shares `coordinator.py` and `tests/closures.json`; its hunk in `_async_learn_house_heat_loss` is the vent feed, not the step call): tree `0e53ab84f14f0073176b406b505cd91b1db50122`.
- #2411 at `115541ec634e5d2a880322a718c151feb506337a` (shares `coordinator.py` and `tests/closures.json`): tree `c3262e7584fbe9f6f20a3301cd4256365581b0f8`.

Every production file merges as plain text. The one shared file that does not is `tests/closures.json`. With the driver disabled (`git -c merge.ledgermerge.driver=false merge-tree --write-tree --name-only`), all three report a content conflict there and nowhere else. Each side adds an entry to the `inert_reads` list of `tests/harness_headers.py`, and the `merge=ledgermerge` driver (`tools/merge/ledger_merge.py`) merges that list as a set. GitHub does not run that driver, so whichever of these lands second needs its main merge done locally (fixer.md step 6).

## Mutation proof

Mutant: the fix's production line, `reach = current * trust_region`, replaced by `reach = trust_region` (the absolute bound restored) in the real worktree at `7326bfe2a` (production identical to this head's). Then `PYTHONPATH=tests/hastub python3 tests/features.py` was run in full and the file restored (`git status` clean after). It printed `3 of 4177 FEATURE CHECKS FAILED`, rc 1:
- FAIL `the extracted Newton step leaves the learned scale unchanged` (the real learner through `_async_learn_house_heat_loss`)
- FAIL `the trust region saturates at a fraction of the current estimate`
- FAIL `and a saturated step in UA does not depend on the prior/multiplier split`

Failing test first: the new checks in `tests/features.py`, run in this worktree before the production line was written (production = the merge base's), FAILed `the trust region saturates at a fraction of the current estimate` (`target 2.5, bound 3.0`) and `and a saturated step in UA does not depend on the prior/multiplier split` (`UA 0.40199999999999997 at (0.2, 2.0), 0.404 at (0.4, 1.0)`).

## Unpinned sites

- custom_components/heatpump_optimizer/thermal_model.py:1938 CLAMP_DROP (`target = float(np.clip(target, current - reach, current + reach))`, the trust region itself). Expected to be pinned by mutation-autofix, killed by `the trust region saturates at a fraction of the current estimate` and `the trust region saturates symmetrically about the current estimate`. Measured: on a `git archive` of this head with the line replaced by `target = float(target)`, those two checks' expressions, evaluated with the production `learner_newton_step` and the coordinator's constants, read False and False (unclamped target 42.0). On the unmutated archive they read True and True (target 3.0). The site is new only because its text changed: the line it replaces, `current - trust_region`, was the same clamp.

## Null control

- The forward-carried null control: a house whose settings already match the learned values (the `reseeded` arm, current 1.0) shows the same learner variance and forecast error before and after. On the owner's two stores, head/base: house UA std x1.0011 / x1.0012, lower x1.0006 / x1.0000, and forecast MAE x1.0000 on every learner.
- `--learned 1.0` (prior already right): reseeded/as-is ratios 1.0000 at both ends.
- `--trust-region 1e9` (the study's perturbation): ratios 1.0000 at both ends, at both trees, in both harnesses.
- The study's own null plants: at the head, `sz_null` and `tz_null` read B/A 1.0000 on every metric. At the baseline they read 0.9631-1.0005, because the learned value drifts off 1.0 by the reseed day.

## Figures

Rolling-harness figures come from the finder's harness `reseed_rolling.py` from study/r10-reseed at `2c42ba4a0`, run as `$EXPORT/tools/audit/round10/study-reseed/reseed_rolling.py` (sha1 `030df96abe88d7b12132798518bc92e466391d99`). Command (from each tree's root): `PYTHONPATH=tests/hastub python3 $EXPORT/tools/audit/round10/study-reseed/reseed_rolling.py --plant P` (defaults: sigma 0.1, 10 days, reseed day 4, reset day 7, seed 20261014). Base = a `git archive` of `176851e95`, head = a `git archive` of `72a653788` (production identical to this head's). Ratios `ratio_B_over_A.<metric>`, base -> head:
- `sz_157`: house_std 1.0457 -> 1.0000, house_rmse 1.0209 -> 1.0000, fc_mae 1.0632 -> 1.0000 (the finding).
- `sz_060`: 0.5106 / 0.7880 / 0.8356 -> 1.0000 / 1.0000 / 1.0000.
- `tz_157_192`: house_std 0.8667, house_rmse 0.8204, fc_mae 0.8272, lower_std 0.8831 -> 1.0000 on all four.
- `sz_null`: 0.9631 / 0.9627 / 0.9651 -> 1.0000. `tz_null`: 0.9980 / 0.9972 / 0.9996 / 1.0005 -> 1.0000.
- `--trust-region 1e9`, `sz_157` and `tz_157_192`: 1.0000 at both ends on every metric (the perturbation).
- Arm A across trees (`<plant>.A.<metric>`, head/base) is not paired. The optimizer plans with arm A's model, so the closed loop runs a different trajectory at each tree: `sz_null` A reads house_std x1.0126 and fc_mae x0.7295 head/base, although its bound differs only where the scale wanders off 1.0. The paired, within-run ratios above are the measurement. The open-loop bundle harness below is the cross-tree one.

Bundle figures come from `dev/audit/harnesses/r10_trust_relative_bundle.py` (new, sha1 `a8d7fd845bcaca2815d88bbbca75abb032150737`), run on the owner's two diagnostics bundles that carry stores. The bundle path is given on argv and nothing from a bundle is committed. Store 1: learned scale 1.2878, ratio 1.7971. Store 2: 1.5667 / 1.9223. Both two-zone. Command: `PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/r10_trust_relative_bundle.py BUNDLE.json` (4000 samples, sigma 0.1, dT 20 K, dt 0.25 h, seed 2252), at the base export and at this worktree. `ratio_reseeded_over_as_is`, base -> head:
- Store 1: house ua_std 1.0900 -> 1.0000, ua_rmse 1.0935 -> 1.0000, fc_mae 1.0006 -> 1.0000; lower 1.2781 / 1.2818 / 1.0012 -> 1.0000 / 1.0000 / 1.0000.
- Store 2: house 1.0880 / 1.0903 / 1.0006 -> 1.0000; lower 1.0262 / 1.0300 / 1.0000 -> 1.0000.
- Per arm head/base, store 1 / store 2. `as_is` house ua_std x1.0911 / x1.0893, lower x1.2789 / x1.0262, fc_mae at most x1.0012. `zero_evidence` (an install with no evidence) house ua_std x0.9993 / x0.9995, fc_mae x1.0000. `at_min` (current on the 0.3 clamp) house ua_std x0.5635 / x0.5941. `at_max` (on the 3.0 clamp) x1.3108 / x1.0923. fc_mae on every clamp arm within x0.9978-x1.0015. These are the learner at both ends of its input range (fixer.md step 3). On the clamp the step follows the UA, smaller at the floor and larger at the ceiling, and the forecast error does not move.

Class enumeration (fixer.md step 8). Rule: `git grep -nE "clip\(.*, *([A-Za-z_.]+) *- *[A-Za-z_0-9.]+ *, *\1 *\+ *[A-Za-z_0-9.]+" -- custom_components/` (every clamp centred on a current value with a symmetric half-width). It returns two seams, both in `learner_newton_step`:
- `np.clip(target, current - reach, current + reach)`: the trust region, closed in this diff (relative).
- `np.clip(updated, current - max_step, current + max_step)`: the rate limit, already relative (`max_step = current * max_step_fraction`). It is now dominated at the shipped constants, as disclosed above.

Outside that rule: `accuracy.py`'s `_clipped_refit_scale` (the batch refit) clips against the global bounds `HOUSE_HEAT_LOSS_SCALE_MIN/MAX`, not a trust region about the estimate, and is untouched. The `_apply_house_heat_loss_scale` / `_apply_lower_floor_loss_ratio` bounds are global multiplier bounds, a different concept and not a step bound; untouched.

At this head: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED` (rc 0). `python3 tools/audit/archscore/score.py --diff 07a09406a1cc97076a6f28581f87f313b322a6b6` prints `Architecture score: dS +0.0000 NULL`, as it did against `176851e95` at `7326bfe2a`.

Scoped gate: `python3 tests/closure.py select --diff 07a09406a1cc97076a6f28581f87f313b322a6b6` at this head prints `MODE: SCOPED -- 27 script(s) run, 6 scoped out.` (the same mode and count against `176851e95` at `7326bfe2a`). `prepr.sh`'s closures step at `7326bfe2a` ran the scoped scripts and printed `scoped recordings are covered; left to CI: tests/harness_headers.py tests/card.mjs tests/card_drift.mjs tests/stress.py`. At this head it skips (`the diff cannot be scoped, so CI re-records every closure`), because `ebd441f9f` changes `tests/closures.json`. `prepr.sh` at this head exits 0 with `no refusal`. Run locally with `PYTHONPATH=tests/hastub` at `7326bfe2a`, each rc 0: `golden.py` (`NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main`), `edge.py`, `finite_boundary.py`, `boost_drift_replay.py`, `guard_pins.py`, `doc_claims.py`, `entities.py`, `validate.py`, `solar_alignment.py`, `backtest.py`, `wood_advisor.py`, `manual_plan.py`, `debug_collect.py`, `harness_headers.py` (`ALL 109 HARNESS HEADER CHECKS PASSED`), and `tests/structure.py`. `stress.py`, `optimality.py`, `arch_score_head.py`, the card scripts and the rest run in CI. `tests/features.py` in full: at `72a653788` (this head's production tree) `1 of 4177 FEATURE CHECKS FAILED`, the #193 replay pin (`scale 0.9043820750088042`), and at a `git archive` of the base `1 of 4175`, the #363 `recorded_at` archive artifact (fixer.md step 2); no other check differs between the two runs (failure sets compared). `7326bfe2a` changes only that pin, to `0.99 ** 10`; a run at `7326bfe2a` was stopped before completion at 1776 checks, with no FAIL and that pin and the four trust-region checks `ok`. The full run at this head is CI's.

## Architecture score

`dS +0.0000 NULL` (no metric moved).

## Red checks

none (no check has run on this head yet).

## Forward-carry

none. The two carried constraints are discharged above: the null control under `## Null control`, and the re-measure on the bundle stores under `## Figures`. The dominated rate limit is no constraint on a later stage. It goes to the orchestrator as a finding to dispatch, outside this group's seam.

## Friction

none
