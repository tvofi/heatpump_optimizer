# Sweep: N-confounded-learner (round 10, PLAN phase D)

Class mechanism: an online estimator absorbs the error of an unmodelled or
mis-modelled covariate into the parameter it learns. Seed finding D2-s3-71
(UA bias +0.094..+0.254 per unit aperture error, n=6). The class is **not in
`dev/audit/config/bugclasses.json`** at this ref (`handoff/audit-r10-register`
@ 9355f107d): status is new/open, not barriered.

## Enumerator

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-N-confounded-learner/enumerate.py`
(output: `D14/sweep-N-confounded-learner/output.txt`).

Seam rule: every function in `custom_components/heatpump_optimizer/*.py` that
folds a model residual (an identifier containing `residual`, or a call to
`learner_newton_step`) into learned state (attribute/subscript assignment, or
a call to `_apply_*` / `_fold_*` / `_clipped_refit_scale`). 13 seams.

| control | result |
|---|---|
| positive: re-finds the D2-s3-71 site `_async_learn_house_heat_loss` | PASS |
| null: clean fixture (EWMA of y, no residual) | PASS, 0 seams |
| perturbation: one added `residual`-fed `self.scale +=` line | PASS, 0 -> 1 |
| probe null: zero covariate error leaves UA at 1.000 | PASS |

Each probe simulates hourly winter days in which the **only** model error is in
the other covariate, closes the loop as the coordinator's replay does, and
asserts the learner under test stays at truth (FAIL = the confound).

## Dispositions

| seam | disposition | evidence |
|---|---|---|
| coordinator.py `_async_learn_house_heat_loss` | instance (finding site) | probe_house_ua 0.925 at aperture error +0.30; 1.000 when sunny intervals (>50 W/m2) are skipped |
| coordinator.py `_async_learn_lower_floor_loss` | instance, beyond finding | same Newton step, same shared residual, no irradiance gate in the method; 0.925 |
| accuracy.py `heat_loss_refit` | instance, beyond finding | real function on solar-contaminated pairs returns 0.937 |
| coordinator.py `_fold_internal_gains` | instance, beyond finding | dark-only, but absorbs UA error by hour (deltaT is hour-correlated): profile max relative deviation 0.82 at +10 % UA error |
| coordinator.py `_fold_solar_aperture` | guarded | demeaned EWMA covariance on modelled Q_solar; probe at +10 % UA error gives 1.003 |
| sysid.py `identify` | guarded | night-gated experiment plus the intercept column G |
| sysid.py `identify_slab` | guarded | same night gate plus `SLAB_INTERCEPT_PRIOR_SD_KW` |
| sysid.py `_lm_solve` | not applicable | solver helper; callers choose the regressors |
| sysid.py `_slab_ua_profile_halfwidth` | not applicable | uncertainty width, not an estimate |
| diagnosis.py `attribute` | not applicable | one-shot diagnostic, nothing persisted |
| drift.py `update` | not applicable | CUSUM statistic, not a parameter |
| flow_lift.py `observe` | not applicable | the bias is the only learned term over the curve and is meant to absorb all curve error |
| price_model.py `observe_day` | not applicable | descriptive price statistics, no physical covariate |

Count: 4 instances (1 judged site + **3 beyond the finding**), 3 guarded, 6 not applicable.

## Proposed barrier

The three heat-loss folds share one residual. Gate the UA and lower-floor folds
(and the `heat_loss_refit` pairs, which would need irradiance recorded in
`AccuracySample`) on the same irradiance threshold `_fold_internal_gains`
uses. `PROBE-BARRIER` shows the sunny gate restores 1.000. Internal gains is
the remaining coupling: it should be fed the residual net of the UA fold's
deltaT-proportional part, or it needs a ridge strong enough that the probe
stays under 5 %. Permanent detector: this enumerator plus the probes as a
`tests/` script, at a few seconds of gate time.

## Limits

These are synthetic closed-loop probes, not owner data. The lower-floor probe
reuses the shared Newton step and tells this seam apart from the house fold
only by the missing gate. The aperture guard was measured on one
deltaT/irradiance correlation shape.
