R10-DEAD-RATE-LIMIT. Part of #201 (the group's `issues` and `fixes` lists are empty; the orchestrator files and wires the group's issue).

Found by the R10-TRUST-RELATIVE seat (#2435, Forward-carry): the heat-loss learners' rate limit in `learner_newton_step` (`thermal_model.py`), `clip(updated, current +- current * max_step_fraction)` fed `HOUSE_LOSS_MAX_STEP` (0.05) at both call sites in `coordinator.py` (`_async_learn_house_heat_loss` and `_async_learn_lower_floor_loss`), can no longer bind.

**Why it cannot bind, re-derived at the merge base `05c39d3a6`.** The EWMA sets `updated = current + alpha * (target - current)`, and the trust region (relative since #2435) holds `|target - current| <= trust_region * current`. So `|updated - current| <= alpha * trust_region * current` = `HOUSE_LOSS_ALPHA` 0.02 x `_LEARNER_TRUST_REGION` 0.5 = 1 % of the estimate, for every `current > 0`, inside the 5 % clip. Both learners' `current` is held in [0.3, 3.0] by `_apply_house_heat_loss_scale` / `_apply_lower_floor_loss_ratio` (store restores go through them too, and `store.py`'s domain is the same range), so `current > 0` always holds. The new harness measures it over the reachable grid (`## Figures`): 0 binding points at the merge base, with the null controls reading binding where the limit would bind.

It could not bind at reachable states before #2435 either: the old absolute trust region capped a move at 0.01 in multiplier units, against a limit of `0.05 * current >= 0.015` at the 0.3 floor, so it bound only below `current = 0.2`, which the clamps exclude. The harness's `--current-min 0.05 --current-max 0.2` arm reads that binding region at the pre-#2435 base `90557e39e` and nothing at the merge base.

**What changed.**
- `learner_newton_step` loses `max_step_fraction` and the clip. Its docstring states the per-interval bound (`alpha * trust_region` of the estimate) and where it comes from; the comment above the EWMA no longer names a rate limit.
- Both call sites drop the keyword.
- `HOUSE_LOSS_MAX_STEP` stays, at 0.05. It has a second reader the brief did not list: `_reanchor_house_heat_loss_scale`'s threshold gate (`abs(current / anchor - 1.0) <= HOUSE_LOSS_MAX_STEP`), a measured decision (the 30-hop walk) this group does not reopen. Its comment said "A single interval may never move the estimate more than this fraction"; it now says it is the re-anchor threshold and no per-interval limit. It also stays importable from `coordinator` (the facade list in `.claude/workflows/web-decomp-stage.js`, pinned by `tests/entities.py`), so neither of those changes.
- The gate's docstring said the learner "absorbs a small edit in one step anyway", false at either tree (one step moves at most 1 %). It now says the learner's EWMA closes a small edit on its own, `HOUSE_LOSS_ALPHA` of the way to its target per accepted sample. The same claim in the comment above the matching check in `tests/features.py` is corrected alike.
- `docs/how-it-works.md`'s learner table said the scale is "rate-limited"; it now says each sample's move is bounded by a trust region.
- Harnesses passing the keyword: `dev/audit/harnesses/r10_trust_relative_bundle.py`, `dev/audit/rounds/round10/study-reseed/reparam_sites.py`, `dev/audit/rounds/round9/D2/s4/newton_bias.py` (the three the brief names), and a fourth the brief missed, `dev/audit/rounds/round10/D14/sweep-N-confounded-learner/enumerate.py` (`git grep -ln max_step_fraction` over the tree found it). `newton_bias.py`'s `--perturb asym` arm re-implements the pre-#193 step and keeps its own copy of that step's 5 % limit (`_PRE193_MAX_STEP`), so the perturbation still means what its header says.
- `tests/features.py`: `_STEP_KW` and the #1936 oracle drop the keyword. The check that drove the limit with `alpha = 1.0` at `current = 0.1` (an unreachable state) is replaced by two: a saturated sample moves the estimate by exactly `alpha * trust_region` of it at both clamps of both learners and at 1.0, and the step's signature has no argument beyond its trust region and `alpha`.
- New harness `dev/audit/harnesses/r10_dead_rate_limit.py`, listed in `tests/closures.json` as an inert read of `tests/harness_headers.py` (`python3 tools/pr/ci_predict.py --base origin/main --apply-inert`).

**Alternatives considered.**
- Make the limit meaningful: set `HOUSE_LOSS_MAX_STEP` below `alpha * trust_region` (1 %). That slows every learner sample and changes the re-anchor threshold with it (or splits the constant), with no measurement that the learner moves too fast; the only evidence on its speed (STUDY R10-RESEED, #2435) is about its dependence on the prior split, which #2435 closed. Not taken.
- Keep the clip and record a binding state: the brief's other arm. No reachable state binds (`## Figures`), so there is no state to record.
- Keep the parameter with a default and stop passing it: leaves a knob the code advertises and nothing enforces, the defect itself. Not taken.

Behaviour: none. The production step is bit-identical at the shipped constants over the whole reachable grid (the harness's `digest`, equal at the merge base and the head), so no golden can move.

## Head

`d85b8c246cafb2448ed2a2866f78404c3b31c6fc`, one commit over the merge base `05c39d3a6597e02c81f07e771a058da90f8ebb46` (the #2435 merge). origin/main's tip at the re-take was `fb9b3fc1fe16a174476c8571c40b4b7d2d3c089c` (`date -u`: 2026-10-19T10:25Z); `git diff --name-only 05c39d3a6 fb9b3fc1f` prints only `dev/programme/delivery/` rows (2368, 2433, 2440, 2442, 2443), so main's newer commits reach no file this body measures.

## Mutation proof

Each mutant edited `thermal_model.py` in the worktree at the seat's first commit `cdf9b7751` (its `thermal_model.py` and the block below are byte-identical to the head's) and was restored with `git checkout`; `git status --short` was empty after. Instrument: `python3 tools/audit/seat/features_block.py "from heatpump_optimizer.thermal_model import learner_newton_step as _newton" "# While a stale sensor is what feeds the residual"` (the #193 S7 block of `tests/features.py`, 7 checks).
- M2, a clip tighter than `alpha * trust_region` re-added after the EWMA (`updated = float(np.clip(updated, current - current * 0.005, current + current * 0.005))`): `2 of 7 FEATURES BLOCK FAILED`: FAIL `the EWMA is what a saturated sample actually moves the estimate by` and FAIL `a saturated sample moves the estimate by alpha * trust_region of it, at either clamp`.
- M3, the parameter re-added unused (`max_step_fraction: float = 0.05`): `1 of 7 FEATURES BLOCK FAILED`: FAIL `the Newton step takes no rate-limit argument beyond its trust region`.
- M1, the deleted clip itself re-added at 0.05: `ALL 7 FEATURES BLOCK PASSED`. This is the finding, not a gap: no value check can see a clip that never binds, which is why the deletion is pinned by the signature check (M3) and the bound by the value check (M2).
- Unmutated head: `ALL 7 FEATURES BLOCK PASSED`.

Failing test first: the same block, with this head's `tests/features.py` copied into a `git archive` of the merge base, exits 1 on its first step call, `TypeError: learner_newton_step() missing 1 required keyword-only argument: 'max_step_fraction'`.

## Unpinned sites

n/a: the diff deletes the clip's mutation site and adds no clamp, comparison or branch; `updated = float((1.0 - alpha) * current + alpha * target)` is the existing EWMA line, now wrapped in `float()` (it was wrapped by the deleted clip's `float()`). `tools/pr/prepr.sh` at this head prints `the diff adds no unpinned mutation site` (`PRE-PR: d85b8c246cafb2448ed2a2866f78404c3b31c6fc`, rc 0, run with `PREPR_SKIP_CLOSURES=1`); CI's `mutation` check is the authority.

## Null control

- `--alpha 1.0` (an EWMA that outruns the limit): `binds=173200` of 181440 at the pre-#2435 base, the merge base and the head alike, so the instrument sees a limit that binds.
- `--current-min 0.05 --current-max 0.2` (estimates below the clamps): `binds=156444` of 187920 at the pre-#2435 base, `binds=0` at the merge base and the head: the binding state the old absolute trust region had, outside the reachable range.
- `--limit 0.005` (a limit tighter than `alpha * trust_region`): `binds=158586` at the merge base and the head, and there the merge base's production step, which still applies it, prints a different digest (`52a4b217...`) from the head's (`3187402b...`).
- The digest's own control: under `--alpha 1.0` the merge base (limit applied) and the head (limit gone) print different digests (`aab10749...` vs `f114d100...`), so equal digests at the shipped constants mean bit-identical steps, not an instrument that cannot tell.

## Figures

Rule-instrument: `dev/audit/harnesses/r10_dead_rate_limit.py` (sha1 `99b702cb6ed433e9531307f710e49299c6dc4b3c` at this head). It drives the production step over every combination of `current` (28 points across [0.3, 3.0] plus both clamps and 1.0), residual (41 points across +-`HOUSE_LOSS_MAX_RESIDUAL` plus +-50 and +-1e6), delta-T (`HOUSE_LOSS_MIN_DELTA`, 10, 20, 40 K), interval (`HOUSE_LOSS_MIN_SAMPLE_HOURS`, 0.25, 0.5, `HOUSE_LOSS_MAX_SAMPLE_HOURS`), base UA (0.02, 0.15, 0.4) and capacity (2, 10, 30). `binds` counts points where the clip changes `updated` by more than 1e-15; `none` counts points with no step (0 everywhere below). Command, from each tree's root: `PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/r10_dead_rate_limit.py [args]`, each rc 0. Trees: `base` = `git archive 90557e39e` (main before #2435), `mb` = `git archive 05c39d3a6`, `head` = this worktree, clean at `d85b8c246`. Every figure below and in `## Null control` was re-taken in one pass with the harness at that sha1.
- Shipped constants: `binds=0` of `points=181440` at base, mb and head. `max_moved_fraction` 0.033333333333 at base (0.01 / 0.3, the absolute bound at the floor), 0.010000000000 at mb and head (`bound=0.010000000000`).
- `digest` at the shipped constants: `3187402b35f5e993a2e0b090b885338973619521` at mb and at head (the production step bit-identical); `0cd34c4c10ee1c429f313ae8d68b3620a95cb21f` at base (#2435's own change).
- Null controls: in `## Null control`.

The finder's harnesses at both ends (mb and head, the head clean at `d85b8c246`):
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/study-reseed/reparam_sites.py`: rc 0, sha1 of its `RESULT` lines (`grep RESULT | grep -vE 'thread_factor|load1|wall|cpu' | shasum`) `89dcd7a6ebbd...` at both.
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round9/D2/s4/newton_bias.py --perturb none`: `worst_abs_bias=0.0034` at both; `--perturb asym`: `0.4731` at both (the perturbation still raises the bias). rc 1 at both trees on macOS, from the script's last line reading `/proc/vmstat`, after every figure printed.
- `PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/r10_trust_relative_bundle.py BUNDLE.json` on a synthetic bundle (empty config, store 2's learned values from #2435's body: scale 1.5667, ratio 1.9223; not the owner's bundle, which this seat does not hold): rc 0, `RESULT` lines' sha1 `8cf80944bc12...` at both.

Class enumeration (fixer.md step 8). The class is a bound dominated by an earlier bound on the same quantity. Rule 1: `git grep -nE "clip\(.*, *([A-Za-z_.]+) *- *[A-Za-z_0-9.]+ *, *\1 *\+ *[A-Za-z_0-9.]+" -- custom_components/` (every clamp centred on a current value), at head: one seam, `thermal_model.py`'s trust region `np.clip(target, current - reach, current + reach)`, the binding bound, kept. At the merge base it also returns the deleted rate limit, closed in this diff. Rule 2: `git grep -nE "MAX_STEP|max_step" -- custom_components`, at head: `HOUSE_LOSS_MAX_STEP` (the re-anchor gate, above) and `COP_LEARNING_MAX_STEP` in `_fold_measured_cop` (`coordinator.py`). The COP fold's limit is the only bound on its step (no trust region precedes it; the move is `COP_LEARNING_ALPHA * (commanded / measured - 1)` of the scale, and the ratio gates before it are relative to the walking ratio, not to 1.0), so it is not the dominated shape; whether it binds in practice is not measured here.

`python3 tests/structure.py` at the head: `STRUCTURE RATCHET PASSED`, after `--record` of two improved rows, `class_excess_loc` 18302 -> 18301 and `max_class_loc` 8544 -> 8543 (the commit message names them). `python3 tools/audit/archscore/score.py --diff 05c39d3a6597e02c81f07e771a058da90f8ebb46`: `Architecture score: dS +0.0000 NULL`.

Scoped gate: `python3 tests/closure.py select --diff 05c39d3a6597e02c81f07e771a058da90f8ebb46` prints `MODE: SCOPED -- 28 script(s) run, 5 scoped out.` Run locally with `PYTHONPATH=tests/hastub`, each rc 0.
- At the head: `features.py` (`ALL 4220 FEATURE CHECKS PASSED`), `structure.py` (`STRUCTURE RATCHET PASSED`), `harness_headers.py` (`ALL 109 HARNESS HEADER CHECKS PASSED`), `guard_pins.py` (`ALL 50 GUARD PIN CHECKS PASSED`), `doc_claims.py` (`ALL 169 checks PASSED`), `env_drift.py --claims-only 05c39d3a6` (`claims hygiene: ... ok`), `closure.py selftest` (`ALL 124 closure shrink pins PASSED`), `layout.py` (`layout self-test: ok`), `entities.py` (`ALL 2350 ENTITY CHECKS PASSED`).
- At the working tree that became `89b7da4c1` (its diff to the head is three lines of `tests/features.py`, below): `finite_boundary.py` (`ALL 106 FINITE BOUNDARY CHECKS PASSED`), `validate.py` (`NO ISSUES`), `deployment_shape.py`, `typing_ruler.py` (`ALL 12 typing-ruler source checks PASSED`), `edge.py` (`ALL EDGE CASES PASS`), `node tests/md_tables.mjs` (`doc_misrendered_lines=0`), and `golden.py` with `GOLDEN_MODE=drift GOLDEN_REF=05c39d3a6597e02c81f07e771a058da90f8ebb46` (`NO UNCLAIMED DRIFT: 56 scenario(s) checked`, `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`). None of them reads `tests/features.py`.
- The rest of `scope.run` (`stress.py`, `optimality.py`, `backtest.py`, `arch_score_head.py`, `block_duty.py`, `boost_drift_replay.py`, `config_flow_steps.py`, `debug_collect.py`, `manual_plan.py`, `plan_view.py`, `solar_alignment.py`, `wood_advisor.py` and the card scripts) runs in CI; no check-run exists yet, since no pull request carries this head.

Disclosed self-correction: the first full `features.py` run, at `89b7da4c1`, exited 1 with `NameError: name '_f24inspect' is not defined`. A global text replace while writing the new check had also rewritten two unrelated aliases, `_f24_inspect.signature` and `_r9p5_inspect.signature` (three lines). The head restores them; `git diff 05c39d3a6 d85b8c246 -- tests/features.py | grep -i inspect` now prints only the new check's own three lines.

## Architecture score

`dS +0.0000 NULL` (no metric moved).

## Red checks

none: no check has run on this head (no pull request is open for it).

## Forward-carry

none: the finding changes no later stage's work. The dead-limit question for `COP_LEARNING_MAX_STEP` is answered above (not the dominated shape), not carried.

## Friction

- fixer-brief: stale: the group brief says to delete `HOUSE_LOSS_MAX_STEP` and update its pins in `tests/entities.py` and the `web-decomp-stage.js` facade list, but the constant has a second reader, `_reanchor_house_heat_loss_scale`'s threshold gate, so only the argument is deleted and both pins stand; the brief also names the second call site "the reseed path" (it is the lower-floor learner) and three harnesses where `git grep -ln max_step_fraction` finds four (D14 `enumerate.py`). Carry: dev/programme/rosters/wave-r10-groups.json
- fixer-handoff: contradiction: the dispatch says to hand off with `tools/audit/seat/handoff_push.sh` and to make no GitHub writes, but `handoff_push.sh` opens or updates the pull request through `app_push.sh` and `gh pr edit`; this seat pushed `handoff/r10-dead-rate-limit` with `git push` and the body with `tools/audit/seat/body_push.sh` (fixer.md step 6), leaving `handoff_push.sh` to the orchestrator. Carry: dev/governance/roles/orchestrator.md
