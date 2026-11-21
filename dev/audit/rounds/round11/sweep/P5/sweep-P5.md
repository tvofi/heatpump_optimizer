# Round 11 class sweep: P5

Class P5 in `dev/audit/config/bugclasses.json` is "a sysid/adoption gate keyed
on a quantity other than the bias it gates". Its status is `barriered`. The
barrier is the R9-P5 sweep in `tests/features.py`: every `HousePlant` field is
fitted or priced by a named sysid width, and three presets are covered,
single- and two-zone. The record names its own gap: "free heat past the
prior's own band ... needs the learned free-heat prior".

Two round-11 survivors:

| finding | shape | site |
|---|---|---|
| D2-s3-10 (verified, medium) | The 95 % adoption interval combines the profile width and the prior width in quadrature. That is conditional on white reading noise. Quantised or larger noise biases UA up while the profile width shrinks, so admitted fits miss their interval: 0.214 at 0.02 C, 1.000 at 0.05 C. | `sysid.slab_ua_adoption_halfwidth`, `_slab_ua_profile_halfwidth` |
| D7-s2-02 (weakened, low) | The intercept is ridged to the configured free-heat prior with `SLAB_INTERCEPT_PRIOR_SD_KW = 0.1`, and the interval widens by one prior width only. Free heat +0.5/+0.8 kW past the prior is admitted at -11.5 % to -21.1 % UA. | `sysid._slab_ua_prior_halfwidth`, `SLAB_INTERCEPT_PRIOR_SD_KW` |

The R9-P5 sweep passes this tree, and it does not cover either survivor or the
two new seams below. `barriered` is therefore `false` for these shapes.

Measured at `handoff/audit-r11-register` @ 28b864af6, detached worktree, venv-ci
Python 3.14.7, Linux x86_64, `OPENBLAS_CORETYPE=Haswell`, BLAS threads pinned to
1. All the figures are counts and ratios.

## Enumerator

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/sweep-P5/enumerate.py [--null | --perturb] [--json PATH]`

The universe is every quantity the sysid fit is **told**. That is every
argument of `SystemIdentification.step` and every field of `HousePlant`. The
enumerator reads the surface by `inspect`, so nothing is listed by hand: 16
seams.

Each seam that enters the heat balance gets one realistic misstatement, where
the true plant or reading differs from what `step` is told. The enumerator then
runs:
- the production night: `arm` / `step` / `_finish` -> `identify_slab`, driven by
  D7-s2's `m2_sysid_plant` protocol on the three `tests/stress.py` BUILDINGS
  presets;
- the coordinator's one gate, `adoption_decision`.

It counts two things per arm:
- **biased_admitted**: nights admitted with |UA bias| above the gate's own bar
  (log 1.10).
- **interval misses**: admitted nights whose |log error| exceeds the half-width
  they were admitted on. The half-width is recovered as
  `(1 - weight) * bar`, from `adoption_decision`'s weight law.

An arm is flagged on any biased_admitted, or on >= 2 misses at a rate above
0.05.

Seams that do not enter the heat balance are printed as `unprobed`, with the
reason:
- `self`, `now`;
- `price` and `price_horizon` (scheduling);
- `learner_samples` (an arming precondition);
- `max_power_kw` (bounds the override; equals the plant's limit);
- `house` (expanded into its fields).

`RESULT tree seams=16 probed=9 flagged=3 biased_admitted_total=3 misses_total=8`:

| seam | injection | cells | admitted | past bar | misses | flag |
|---|---|---|---|---|---|---|
| room_temp | white 0.005 / 0.01 / 0.02 C (12 seeds), quantised 0.1 C | 36/36/36/3 | 20/6/1/0 | 0 | 0/1/1/0 | - |
| outdoor_temp | sensor +1.5 K | 3 | 2 | 0 | 2 | P5 |
| cop | true COP x1.15 of told | 3 | 1 | 1 (0.1285) | 1 | P5 |
| plan_power_kw | pump delivers 0.9 of the told hold | 3 | 2 | 0 | 1 | - |
| house.ua | declared x1.3 | 3 | 2 | 0 | 0 | - |
| house.capacity | true x2 | 3 | 2 | 0 | 0 | - |
| house.gains | free heat +0.8 kW | 3 | 2 | 2 (0.2111) | 2 | P5 |
| house.slab_mass | true x2 | 3 | 1 | 0 | 0 | - |
| house.slab_transfer | true x2 | 3 | 1 | 0 | 0 | - |

**Positive control.**
- **D7-s2-02: re-found.** `house.gains` +0.8 kW admits 2 nights past the bar,
  with worst bias 0.2111. That matches the finder's heavy_old and typical_slab
  +0.8 rows.
- **D2-s3-10: not re-found by the flag rule.** Under production's own drive the
  gate refuses most noisy nights: at 0.02 C, 1 of 36 is admitted. The seam
  shows 2 misses in 27 admitted noisy nights (0.074), one per arm, which is
  below the per-arm rule. D2-s3-10's own harness drives a designed step test on
  the fit's candidate class over 40 seeds a cell, and that is where its misses
  appear (0.214 at 0.02 C, reproduced by the judge). This enumerator lists the
  `room_temp` seam but does not reproduce that finding. Its instance below rests
  on the finder's harness.

**Null control.** `--null` sets every injector to zero, so the told plant is
the true one. It prints `flagged=0 biased_admitted_total=0 misses_total=0` and
exits 0.

**Perturbation.** `--perturb` makes one one-line re-introduction:
`sysid.SLAB_INTERCEPT_PRIOR_SD_KW` 0.1 -> 0.01. This all but removes the
free-heat width that R9-P5 added. It prints
`biased_admitted_total=5 misses_total=14`, up from 3 and 8. The `cop` arm
admits 3 of 3, past the bar at 0.1542.

Narrowing `SLAB_PAIR_PRIOR_LOG_SD` (to 1e-9, 0.01 or 0) **lowers** admissions:
the same width also ridges the fit. So it is not a clean perturbation for this
class. That direction was measured and set aside.

## Disposition of every seam

**Instances at judged sites** (`beyond_finding: false`):

| seam | probe |
|---|---|
| `sysid.slab_ua_adoption_halfwidth` (with `_slab_ua_profile_halfwidth`): the `room_temp` reading-noise model | D2-s3-10: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D2/s3/m5_sysid.py` gives miss rate 0.214 (6 of 28) at 0.02 C and 1.000 at 0.05 C; `--perturb-bar5` gives 0 admitted. This sweep's drive saw 2 misses in 27 admitted. |
| `sysid._slab_ua_prior_halfwidth` / `SLAB_INTERCEPT_PRIOR_SD_KW`: the `house.gains` seam | D7-s2-02: `dev/audit/rounds/round11/D7/s2/m2_sysid_plant.py` gives biased_admitted=3, and `--perturb` gives 0. This sweep: gains +0.8 kW gives 2 past the bar, worst 0.2111. |

**Instances beyond the findings** (`beyond_finding: true`, 2). The probe is
`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/sweep-P5/probe_told.py`.
It exits 1 with `admitted_past_bar=6`. `--null` gives 0 past the bar and 0
misses, and exits 0.

| seam | mechanism | probe rows |
|---|---|---|
| `SystemIdentification.step` `cop` | `step` turns the told electrical power into the fit's heat with `cop` (sysid.py:1778-1782: `power_kw = plan_power_kw * thermal_cop`), so a COP error scales the fitted UA one-for-one. None of the three width terms (profile, intercept prior, slab pair) carries a COP width, and R9-P5's told-quantity check covers `HousePlant` fields only. | COP x1.10: 1 of 2 admitted past the bar (0.1027). x1.15: 1 of 1 (0.1285). x0.85: 2 of 2 (0.2027). |
| `SystemIdentification.step` `outdoor_temp` | UA is heat over (indoor - outdoor), so a sensor offset moves the fitted UA by offset / (21 - outdoor). No width term carries it. | +1.5 K: 2 admitted, 2 interval misses, worst 0.0831 (inside the bar). +2.5 K: 2 of 2 past the bar (0.1410). -2.5 K: 2 misses (0.0997). |

Both probes are noise-free nights on D7-s2's drive with the outdoor at 0 C. The
magnitudes (COP within 10-15 % of the model, an outdoor sensor 1.5-2.5 K off)
were chosen as plausible. Their frequency in installs was not measured.

**Guarded:**

| seam | guard |
|---|---|
| `house.ua` | Fitted, not told: declared x1.3 gives 0 past the bar and 0 misses (the profile width). |
| `house.capacity` | Fitted (the profile). True x2 gives 0 past the bar and 0 misses. |
| `house.slab_mass`, `house.slab_transfer` | `_slab_ua_told_halfwidth` (`SLAB_PAIR_PRIOR_LOG_SD`, the R9-P5 barrier). x2 gives 0 past the bar and 0 misses. |
| `plan_power_kw` | The step and relax phases are driven by the experiment's own override, so a hold the pump under-delivers enters only the settle window. Delivered 0.9 gives 0 past the bar and 1 miss in 2, below the flag rule. The guard is read from `step` (sysid.py:1782); its reach beyond 10 % was not probed. |

**Not applicable:** `self`, `now`, `price`, `price_horizon`, `learner_samples`,
`max_power_kw` and `house`. The reasons are in the enumerator output: none of
them enters the heat balance the fit inverts.

**Other `adopt*` functions in the package.** These were enumerated by AST name
and bar comparisons, and none is a statistical gate:
- `coordinator.async_adopt_heat_loss_refit`: a restore the user requests, gated
  on the drift advisor's offer.
- `coordinator._adopt_system_identification`: the consumer of
  `adoption_decision`.
- `price_model.adopt_model`: a snapshot rollback.
- `boost.adopt_plan` / `adopt_action`, `coordinator.adopt_action`,
  `_adopt_away_override`, `pump_arbiter._adopt`: plan and override adoption, not
  learning.
- `store.admitted`, `wear.admit`: storage and wear bookkeeping.

All are out of the class: none gates a fitted quantity on a width.

## Barrier proposal

Extend R9-P5 in `tests/features.py` from the `HousePlant` fields to the whole
told surface of `step`. That is this enumerator, run as a check: every argument
that enters the heat balance either names the sysid width that prices it or
is on a named not-physical list with its reason.

The fix this asks of production is one width per told multiplicative input:
- a COP width, for example the COP learner's own dispersion where one is
  learned, else a declared log SD;
- an outdoor-sensor width, in K over (indoor - outdoor).

Both enter `slab_ua_adoption_halfwidth`'s quadrature beside the slab pair. The
check is a noise-free drive of 3 presets x 9 seams, about 6 s of gate CPU
without the 12-seed noise arms and about 20 s with them.

D2-s3-10's noise model needs its own pin. The candidate-class harness (m5),
cut to a few seeds, or an errors-in-variables width term would serve. This
drive does not reach it.

## Not done

- These files are untracked. A committer must classify `D14/sweep-P5/`
  (`enumerate.py`, `probe_told.py`, `seams.json`), or `tests/entities.py`
  fails.
- `m5_sysid.py` (D2-s3-10's harness, about 10 min a record) was not re-run on
  this box. The judge's reproduction stands as its probe.
- The COP and outdoor arms use one magnitude grid at outdoor 0 C. A milder
  outdoor shrinks (indoor - outdoor) and enlarges the outdoor-offset bias. That
  was not swept.
