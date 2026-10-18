The open-window detector (`_vent_cusum`, read by `_learning_frozen` as "ventilation") folded the heat-loss replay residual against zero, so a model bias the learners had not yet removed read as a window that never closed, and the freeze it raised stopped the learner that would have removed it (D2-s3-72). Closes #2241.

**What changed.** `drift.Cusum` gains an optional tracked reference (`reference_hours`, `clip`): it folds the residual's departure from what the residual normally reads, `level + slope_heat x heat + slope_sun x sun`, fitted by recursive least squares that forget over `VENT_CUSUM_REFERENCE_HOURS` (24 h). The departure is taken before the sample moves the fit; the first sample seeds the level, clipped; both the departure and the fit's move are clipped (the clip moved from the coordinator's feed site into the detector); each coefficient's variance is held at its prior so a regressor that sits still cannot wind up. The coordinator's feed passes the interval's heat input (`previous_power * dt_h`) and sun (`solar_radiation * dt_h / 1000`). A pre-fix payload loads with no reference and re-seeds, so an install latched today releases. `_cop_health_cusum` keeps the zero reference (no keyword set) and persists no fit, so its payload is unchanged. The fit is declared in `store.DOMAINS` (the existing mechanism `tests/finite_boundary.py` enforces): `None` until seeded, covariance cells within the prior variance, which `Cusum.load` enforces; a bad cell drops the whole fit, which re-seeds.

**Why a regression, not a level.** A level alone (the sweep's suggested alternative, tried first at `9b474621f`) left the finder's own harness at 0.156 / 0.154 tripped at delivery 0.4: once the learner absorbs the mean, a delivery bias leaves a residual that scales with the heat put in (night cold, afternoon warm), and an aperture error one that scales with the sun. A window adds loss whatever the power or sun, so it still departs from the fit.

**The cost, measured.** The planted-window harness (below) detects every wide window (300 W/K, 2/8/12 h) at both ends, at the same or +0.25 h latency. The floor rose: a window adding 150 W/K for 4 h is detected in 16 of 20 arms (base 20 of 20) and one adding 100 W/K (the zone's own UA) for 8 h in 0 of 20 (base 17 of 20). Under the P loop the controller raises power while a window is open, and the heat slope absorbs part of it. Measured alternative, not taken: freezing the fit while evidence accumulates (`stat > 0`) raised the aperture arm on the heat-only fit (P0 g0.4 fix2.00: 0.035 against 0.021 without it) -- it re-introduces the zero-reference behaviour for whatever the fit has not yet learned.

**Outside the owning seam.** `drift.py` (the primitive's owner; `np.exp`/`np.isfinite`, so no import line added for LEAF-IMPORTS), `const.py` (`VENT_CUSUM_REFERENCE_HOURS` beside the other `VENT_CUSUM_*`) and `store.py` (two `DOMAINS` rows beside the `vent_cusum` rows, one shorthand, and `REFERENCE_PRIOR_COV` added to the existing `.drift` import line; STORE and RATIO-ANCHOR also list `store.py`). In `coordinator.py`: the `_vent_cusum` construction, the feed call, two comments, and one `.const` import line. The class's line count is unchanged.

## Head

`420f05f95924bbc4bd2b928fe0200dcf41999154` (main-merge catch-ups: 2; the second merges origin/main `c09d61dc9`, which carries R10-LEAF-IMPORTS' moves into `drift.py` and `coordinator.py`). Every figure below except where marked was re-taken at this head after that merge, from a `git archive` of it. Base for the finder's harness and the catch-up verifier: the merge base `c09d61dc9c97`, re-taken there (every RESULT line identical to the fork `6e5753a4a`'s); the planted-window and companion base figures are from the fork `6e5753a4a` (main changed no detector line between the two: `git diff 6e5753a4a c09d61dc9 -- custom_components/heatpump_optimizer/drift.py` touches only the moved `utc_step_starts`).

## Mutation proof

Each mutant applied to a `git archive` of this head, `tests/features.py` run in full (`PYTHONPATH=tests/hastub python3 tests/features.py`). Every run, the unmutated head included, also fails `and the path that proceeds still stamps a resolvable recorded_at (#363)` -- the archive has no git, the known runner artifact (fixer.md step 2); it is excluded from each list.

- M1 departure against zero (`departure = self._clipped(value)` in `Cusum._departure`): FAIL `a steady cold residual from the first sample on is a bias, not a window`, `a detector latched on a bias releases once the bias is its level`, `a glitch on the very first sample seeds the reference clipped, not raw`, `days at one heat input cannot wind any coefficient's variance past its prior`, `R10-P5: each measures from a tracked reference; ...`.
- M2 feed without regressors (`self._vent_cusum.update(now, float(residual), ())`): FAIL `the fourth trips the detector through the real learner`, `a tripped detector freezes every learner with reason ventilation`, `while frozen, cold residuals feed the detector but never the model`.
- M3 raw seed (`self.reference = [value] + ...`): FAIL `a glitch on the very first sample seeds the reference clipped, not raw`.
- M4 no variance cap (the `cov * np.outer(shrink, shrink)` line deleted): FAIL `the fourth trips the detector through the real learner`, `a tripped detector freezes every learner with reason ventilation`, `while frozen, cold residuals feed the detector but never the model`, `the reference survives a store round trip`, `days at one heat input cannot wind any coefficient's variance past its prior`.
- M5 no reference at the construction (`reference_hours=VENT_CUSUM_REFERENCE_HOURS,` deleted): FAIL `a steady cold residual from the first sample on is a bias, not a window`, `a detector latched on a bias releases once the bias is its level`, then `TypeError` at the seed check (rc 1).
- Failing test first (at `b8c01b77e`): that head's `tests/features.py` against the fork's production tree: FAIL `a steady cold residual from the first sample on is a bias, not a window`, `a detector latched on a bias releases once the bias is its level`, then `AttributeError: 'Cusum' object has no attribute 'reference'` (rc 1).

## Unpinned sites

Each site `prepr.sh` step 6d lists, with its disposition (the check named is the one expected to kill it in CI's mutation run):

- custom_components/heatpump_optimizer/drift.py:36 CONST: triage -- the prior's weight (one sample) is a design choice; checks read the constant by name, so none pins its magnitude by design.
- custom_components/heatpump_optimizer/drift.py:155 BOOLOP: pinned by mutation-autofix, killed by `a non-finite residual or regressor feeds nothing, not even the fit`.
- custom_components/heatpump_optimizer/drift.py:155 GUARD_OFF: pinned by mutation-autofix, killed by `a non-finite residual or regressor feeds nothing, not even the fit`.
- custom_components/heatpump_optimizer/drift.py:159 CMP_BOUND: triage -- equivalent: `side` is +1 or -1 by construction, never 0 (line rewritten, logic unchanged from base).
- custom_components/heatpump_optimizer/drift.py:194 GUARD_OFF: pinned by mutation-autofix, killed by `a -0.4 °C step trips at exactly the hand-computed fourth sample` (a zero-referenced detector).
- custom_components/heatpump_optimizer/drift.py:204 RETURN_DEL: pinned by mutation-autofix, killed by `the seeding sample folds nothing, and a fit at its seed round-trips`.
- custom_components/heatpump_optimizer/drift.py:209 CLAMP_DROP: triage -- reachable only with a feed clock running backwards; a negative gap would shrink the covariance, never inflate it.
- custom_components/heatpump_optimizer/drift.py:218 CLAMP_DROP: pinned by mutation-autofix, killed by `the fourth trips the detector through the real learner` (M4's kill set).
- custom_components/heatpump_optimizer/drift.py:226 RETURN_DEL: pinned by mutation-autofix, killed by the #2241 checks (the departure becomes None).
- custom_components/heatpump_optimizer/drift.py:229 GUARD_OFF: pinned by mutation-autofix, killed by `one glitched -10 °C reading cannot trip the detector alone`.
- custom_components/heatpump_optimizer/drift.py:231 CLAMP_DROP*2: pinned by mutation-autofix, killed by `one glitched -10 °C reading cannot trip the detector alone`.
- custom_components/heatpump_optimizer/drift.py:231 RETURN_DEL: pinned by mutation-autofix, killed by `one glitched -10 °C reading cannot trip the detector alone`.
- custom_components/heatpump_optimizer/drift.py:273 GUARD_OFF: pinned by mutation-autofix, killed by `tests/finite_boundary.py`'s `every store the rich seed writes is seeded, and every field it writes is declared in store.DOMAINS`.
- custom_components/heatpump_optimizer/drift.py:284 RETURN_DEL: pinned by mutation-autofix, killed by `the reference survives a store round trip`.
- custom_components/heatpump_optimizer/drift.py:309 CMP_BOUND: pinned by mutation-autofix, killed by `the seeding sample folds nothing, and a fit at its seed round-trips` (a seed's variance is exactly the prior).
- custom_components/heatpump_optimizer/drift.py:319 GUARD_OFF: pinned by mutation-autofix, killed by `a detector latched on a bias releases once the bias is its level` (a payload with no fit).
- custom_components/heatpump_optimizer/drift.py:321 BOOLOP: pinned by mutation-autofix, killed by `a corrupt reference loads as none, to be re-seeded, never as a number`.
- custom_components/heatpump_optimizer/drift.py:321 GUARD_OFF: pinned by mutation-autofix, killed by `a corrupt reference loads as none, to be re-seeded, never as a number`.
- custom_components/heatpump_optimizer/drift.py:324 RETURN_DEL: pinned by mutation-autofix, killed by `a corrupt reference loads as none, to be re-seeded, never as a number`.
- custom_components/heatpump_optimizer/drift.py:330 GUARD_OFF: pinned by mutation-autofix, killed by `a corrupt reference loads as none, ...` (the asymmetric arm).
- custom_components/heatpump_optimizer/drift.py:336 RETURN_DEL: pinned by mutation-autofix, killed by `the reference survives a store round trip`.

## Null control

Delivery 1.0, exact prior, no window: 0.000 tripped at both ends on every harness arm below (the carry's own null). Wide planted window (300 W/K): detected on all 20 arms at both ends (the carry's planted signature).

## Figures

Finder's harness `dev/audit/rounds/round10/study-ident/ident_rolling.py` (sha1 `3755ee80dd71a8d05e2ea2a4c6b317c63fa4ed79`), metric `vent_tripped_share` (share of 15-min intervals with `_vent_cusum.tripped`, freeze patched off), command `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/study-ident/ident_rolling.py --plant P --delivery G`:
- P0 g0.4 fix1.00: base 0.187 -> head 0.000; P1 g0.4 fix1.00: 0.172 -> 0.000 (the finding).
- g0.6 and g1.0, P0 and P1, fix1.00: 0.000 -> 0.000 (null).
- Every arm of P0 at g0.4/0.6/1.0: head 0.000 on all twelve arms (base up to 0.230).
- P1 fix2.00 (model aperture 2x the truth): base 0.210 / 0.134 / 0.191 at g0.4 / 0.6 / 1.0 -> head 0.006 / 0.009 / 0.013; every other P1 arm 0.000 at head. The residual is the aperture class R10-NIGHT-FOLDS (G-ID-1) owns.
- UA bias (`ua_bias.fix1.00`) identical at both ends on every run (P0 g0.4 +0.5174, P1 g0.4 +0.4374): the freeze is patched off in this harness, so learning is unchanged by construction.

Catch-up verifier `dev/audit/rounds/round10/catchup/study/learner_v2.py` (sha1 `055dd816d847e68419daf23760a5b084ca36c052`), production `_learning_frozen` left in place, command `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/catchup/study/learner_v2.py --two-zone`:
- g0.4 share frozen "ventilation": base 0.984 / 0.983 (seeds 1/2) -> head 0.000 / 0.000; learned UA bias +0.1874 / +0.1774 -> +0.5462 / +0.5600 (the learner is no longer stalled; it now absorbs the delivery shortfall as the patched arm did at base).
- g1.0, 0.9, 0.8, 0.6 and UA truth 1.3x/1.6x: 0.000 at both ends.
- ID-01 lines identical at both ends (slope +0.1902 / +0.1456): not this finding.

Planted-window harness `dev/audit/harnesses/r10_vent_bias_window.py` (sha1 `c8d01ade6c79232007d3e60c66343cdef402e556`, new; production `_learning_frozen`, two-zone house, 14 days, 2 seeds, P loop and on/off thermostat, delivery 1.0/0.6/0.4, UA 1.6x, a delivery fault arriving on day 4), command `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_vent_bias_window.py`:
- Worst no-window `false_share` over all arms: base 0.617 -> head 0.027. The head's only non-zero arms are the on/off thermostat with the day-4 fault (0.019-0.030): the fault's onset looks like a window and latches for 6.5-9.0 h (`longest_false_h`), against 18.0-18.25 h unbroken and 0.41-0.46 overall at base.
- Detected windows (`detect_h` finite) out of 20 arms each: 300 W/K x 2 h, x 8 h, x 12 h: 20 -> 20; 150 W/K x 4 h: 20 -> 16; 100 W/K x 8 h: 17 -> 0.
- `held_share` of the 12 h wide window under the P loop: 0.80-1.00 at head (1.00 at base): the fit absorbs part of a long window that the controller answers with power; on/off: 1.00 at both ends.

Companion `dev/audit/harnesses/r10_vent_probe_companion.py` (sha1 `8380dcced34e4f3b13703f48080addddc0e3c3bc`, new), command `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_vent_probe_companion.py`: base `part1_failures=2` (bias 0.10 trips at sample 59, 0.40 at 3), `open_learning_gates=1`, rc 1 -> head `part1_failures=0`, `open_learning_gates=0`, rc 0. Null: bias 0.00 and 0.05 untripped at both ends; planted window (+0.5 K x 4) trips at sample 98 on every arm at both ends.

Class enumeration (fixer.md step 8). Rule: `python3 dev/audit/rounds/round10/D14/sweep-P5/enumerate.py` (sha1 `ddbc518a8bd4d48aee64bfe4d5c4ecfc43b644ea`) prints `SEAMS 14 INSTANCE_CANDIDATES 1` at both ends: it keys an instance on a `.update()` argument naming "residual", which the fix rightly keeps, so it reads flat; the probe `dev/audit/rounds/round10/D14/sweep-P5/probe_vent_bias.py` (sha1 `b05e79c3ea8a58ed8e38a64368875e37e87aa3d8`) builds a bare `Cusum` (the primitive's default, left alone) and reads `PROBE FAIL` at both ends. The companion's part 2 applies the tree's rule instead (every `Cusum` read in `_learning_frozen` sets `reference_hours`). Seams, each with its disposition:
- `_vent_cusum` (construction, feed, `_learning_frozen` "ventilation"): closed in this diff.
- `_cop_health_cusum`: already guarded -- fed a shortfall against its own learned per-bucket baseline, read by no learning freeze (companion `gates_learning=False`).
- `abs(residual) > HOUSE_LOSS_MAX_RESIDUAL` in the house and lower-floor learners, and `accuracy.py`'s `_refit_pair`: already guarded per `dev/audit/rounds/round10/sweep-P5.md` (a per-interval 1.0 K bound, not a latch); untouched.
- `_learning_frozen`'s other returns (external heat, pump signals, defrosting, input health, boost, `_tail_freeze`): not applicable, keyed on measured or commanded state.
- `_adopt_system_identification`, `adoption_decision`: already guarded by the R9-P5 block.
The barrier the sweep proposed lands as the `R10-P5` census in `tests/features.py`: it finds every CUSUM `_learning_frozen` reads from the coordinator's source (refusing if it finds none or loses `_vent_cusum`) and drives each on a live coordinator with a bias up to the learner's 1.0 K rejection -- steady, heat-scaled, sun-scaled -- which must not trip it, and a window on top, which must.

Learner at both ends of its input range (fixer.md step 3): zero evidence -- a fresh detector seeds on its first sample (`a steady cold residual from the first sample on is a bias, not a window`); the clamp -- a bias at the learner's 1.0 K rejection, in all three shapes (`R10-P5` census).

Structure: `python3 tests/structure.py` at this head: `STRUCTURE RATCHET PASSED` (rc 0). Architecture score: `python3 tools/audit/archscore/score.py --diff c09d61dc9c9779e721eb73b1ea402913a52242fb` at this head prints `Architecture score: dS +0.0000 NULL`.

Scoped gate: `python3 tests/closure.py select --diff c09d61dc9c9779e721eb73b1ea402913a52242fb` prints `MODE: SCOPED -- 29 script(s) run, 4 scoped out.` Run locally at this head, each rc 0: `tests/features.py` (`ALL 4171 FEATURE CHECKS PASSED`), `tests/entities.py` (`ALL 2346 ENTITY CHECKS PASSED`, summary line present), `tests/finite_boundary.py` (`ALL 84 FINITE BOUNDARY CHECKS PASSED`), `tests/boost_drift_replay.py` (`ALL 46 BOOST DRIFT CHECKS PASSED`), `tests/structure.py`, `GOLDEN_MODE=drift python3 tests/env_drift.py --all origin/main` (`NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main`; no claim-file change), harness_headers, guard_pins, doc_claims, validate, edge, typing_ruler, deployment_shape, debug_collect, plan_view, block_duty, manual_plan, wood_advisor, solar_alignment, open_meteo, frontend, config_flow_steps, `closure.py selftest`. `stress.py`, `optimality.py`, `backtest.py`, `golden.py`, `arch_score_head.py` and the card scripts are CI's.

## Architecture score

`dS +0.0000 NULL` (no metric moved).

## Red checks

`closures` INERT READS for the two new files under `dev/audit/harnesses/` (`tests/harness_headers.py` opens that directory in a child process only CI's strace sees): recorded in-branch with `closure.write_closures` into `inert_reads["tests/harness_headers.py"]` (`420f05f95`), as R10-LEAF-IMPORTS did; `python3 tools/pr/ci_predict.py` at this head: no closures or fast red predicted.
`tests/finite_boundary.py` went red locally at `98236fdb3` (never pushed): `every store the rich seed writes is seeded, and every field it writes is declared in store.DOMAINS` named the undeclared `vent_cusum/reference` fields; answered in `f7f1af6eb`. The census is itself the cheapest detector for an undeclared stored field; no cheaper one exists.

## Forward-carry

Group `R10-NIGHT-FOLDS` on the roster branch `handoff/audit-r10-roster`: the orchestrator appends the carry (this diff does not touch `dev/programme/rosters/wave-r10-groups.json`). Its night-interval predicate must sit after the `_vent_cusum.update` feed in `_async_learn_house_heat_loss`, or the detector starves by day (it force-releases after `VENT_CUSUM_STARVE_HOURS`) and its fit loses the power and sun range the day spans. Control: `dev/audit/harnesses/r10_vent_bias_window.py` at that group's merge base and head keeps `false_share` 0.000 on the delivery 1.0 / UA 1.0 / no-window arm and `detect_h` finite for the 300 W/K windows on all 20 arms. When the owner's bundle is re-measured, report the vent freeze share beside the UA figures.

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
