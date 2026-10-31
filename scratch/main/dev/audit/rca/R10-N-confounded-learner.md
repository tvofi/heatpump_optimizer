# RCA: an online estimator absorbs a mis-modelled covariate's error

Seat: round-10 root-cause, class `N-confounded-learner` (#2223). R10 has 4 instances (1
judged, 3 beyond the finding), which meets the per-round trigger. Tree:
`handoff/audit-r10-register` at `2c3272eb7`. This seat fixes nothing.

## Root cause

### Cause, reproduced

Three learners fold one shared model residual into one parameter each:

- the house heat-loss fold (`_async_learn_house_heat_loss`);
- the lower-floor fold (`_async_learn_lower_floor_loss`), which uses the same Newton step;
- the drift-time batch refit (`accuracy.heat_loss_refit`).

That residual is the observed minus the modelled room-temperature change. It carries the
error of every term in the model, and the solar term is one of them. Solar gain is
correlated with the conductive term through the time of day and the outdoor temperature.
So when the solar aperture is wrong, the heat-loss parameter takes up the difference and
settles at a biased value that looks converged. The fourth instance runs the other way:
`_fold_internal_gains` is dark-only, but it absorbs UA error hour by hour, because ΔT
correlates with the hour.

The tree already has the remedy, but per learner:

- `sysid.identify` is night-gated and carries an intercept column;
- `_fold_solar_aperture` uses a demeaned covariance;
- `_fold_internal_gains` gates on irradiance.

The UA folds have no such gate.

Reproduced at `2c3272eb7` with
`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-N-confounded-learner/enumerate.py`
(1.78 s):

| line | result |
|---|---|
| `PROBE _async_learn_house_heat_loss` | `ua_scale=0.925` at `aperture_err=+0.30` (truth 1.000), FAIL |
| `PROBE _async_learn_lower_floor_loss` | `lower_ratio=0.925 gated=False`, FAIL |
| `PROBE heat_loss_refit` | `refit_scale=0.937`, FAIL |
| `PROBE _fold_internal_gains` | `gains_max_rel_dev=0.820` at `ua_err=+10%` (truth 0), FAIL |
| `PROBE-GUARD _fold_solar_aperture` | `aperture_scale=1.003`, PASS |
| `PROBE-BARRIER house_ua sunny-gated` | PASS |
| controls | positive, null (`count=0`) and perturbation (`0->1`) all PASS |

The judge row for D2-s3-71 reads *"UA bias slope +0.094..+0.254 per unit aperture error,
n=6"*. Its night-only arm has a spread of at most 0.0001 and its flat-irradiance arm has a
spread of 0.

### Class search

The sweep's seam rule is a function that folds an identifier containing `residual`, or a
`learner_newton_step` result, into learned state. It finds 13 seams:

- 4 instances;
- 3 guarded: `_fold_solar_aperture`, `sysid.identify` and `identify_slab`;
- 6 not applicable: solver helpers, diagnostics, a CUSUM, the flow-lift bias whose job is
  to absorb curve error, and the price statistics.

Source: `dev/audit/rounds/round10/sweep-N-confounded-learner.md`.

Arrival dates (`git log -S`, first commit):

| seam | first commit |
|---|---|
| house heat-loss fold | `ed053e104`, 2026-08-21 |
| lower-floor fold | `75c0299b9`, 2026-08-23 (v3.6.0) |
| internal-gains fold | `2c1647018`, 2026-08-26 (v4.0.0 T4b) |
| `heat_loss_refit` | `bfffcca77`, 2026-10-06, the fix for #1936 |

The last of these was written **by a fix**, after the estimator step below existed. It
reuses the ungated residual pairs.

### Process state: (c) followed and did not produce the intended result

`dev/governance/dimensions/D2.md` step 5 has read the same way since `58a1f2a7a`
(2026-09-02): *"`sysid.identify` bias under white, quantised (0.1 °C) and drifting noise;
the confidence gate versus the bias it admits; the COP and heat-loss learners' clamps."*
The rounds that ran D2 drove that list. Every perturbation in it is **measurement noise or
a clamp**. None of them is a **model error in another regressor**, which is the only input
that moves this class. A noise-only arm leaves an unbiased learner unbiased and a
confounded learner unbiased too. The round-10 identifiability study
(`dev/audit/rounds/round10/study-ident/`) is the first harness that perturbs the aperture
and reads UA.

The #1936 fix went through `fixer.md` and fix review. Neither asks for a covariate-error
arm, so the fix carried the shape into a new learner. That is the same step's unit, one
stage later.

This is not (a): the estimator step existed and was executed. It is not (b): it was
obeyed. Its perturbation set does not contain the cause.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, wall-clock per release.

- **Standing cost.** The sweep's enumerator plus its probes, as a `tests/` script, run in
  1.78 s. At about 18.5 PRs per release (314 PRs over 17 release intervals,
  `v6.7.1..v7.0.0`), with one run charged to every PR, that is 33 s per release.
- **P(recurrence).** 1 instance seam (`heat_loss_refit`) arrived after `v4.0.0`, over 122
  release intervals to `v7.0.0`, so 0.008 per release. The base is small: 13 learner seams
  in total.
- **cost(defect).** The lower bound is the round-9 per-finding fix cost, 4.35 h (#1718:
  21.75 h over 5 findings). That excludes the identifiability study, which found the class.
  The field cost is a converged UA 7.5 % low at a +0.30 aperture error, and every plan is
  sized on that UA.
- **Verdict.** 1/122 x 4.35 h = 0.036 h = 128 s per release, against 33 s. The barrier
  passes by about 4x. The margin is thin, and P rests on a single arrival, so the form
  below keeps the standing cost at the probe set and adds no simulation.

### Countermeasure (a class barrier, proposed; not built by this seat)

It addresses (c): the covariate-error perturbation goes where the noise perturbations
already are, and every new learner is pulled into it.

1. **A `tests/` script made of the sweep's probes.** Each residual-fed learner is driven
   with error **only** in the other covariate, and the script asserts that the learned
   parameter stays within 5 % of truth. It needs:
   - its null control (zero covariate error gives 1.000);
   - the guarded aperture fold as the healthy arm.
2. **A registration arm.** It uses the enumerator's seam rule and refuses a residual-fed
   fold that has neither a probe in the script nor a reasoned not-applicable entry. That is
   what catches the next `heat_loss_refit`. The script must show:
   - red on this tree (4 instances);
   - green once they are gated;
   - perturbation: one added residual-fed line gives `0 -> 1`;
   - non-vacuity: the number of seams read is at least 13.
3. **The fixes** are the sweep's: the UA and lower-floor folds take the irradiance gate
   `_fold_internal_gains` already uses, and `heat_loss_refit` records irradiance per
   sample. The internal-gains coupling needs a decision: feed it the residual net of the
   UA fold's ΔT-proportional part, or regularise it until the probe stays under 5 %. The
   class's fix PR owns that decision, not this seat.

**Brief carry (proposal; the orchestrator delivers it).** D2 step 5 should add *"and under
a model error in the other covariate (solar aperture, UA)"*. `D2.md` is policy, so this
needs tvofi's approval.

## Needs tvofi

1. The D2 step-5 clause above. It addresses (c).
2. A structure-budget raise is not expected. If the gate on two folds needs one, it is
   tvofi's decision, asked before the push.
