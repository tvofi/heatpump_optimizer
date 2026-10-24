The heat-loss learners absorb solar-aperture error. The replay nets the modelled
solar term out only to the accuracy of the aperture, and solar gain correlates
with the conductive term through the time of day and the outdoor temperature —
so a mis-set aperture leaves a residual the Newton step settles into the
heat-loss coefficient at a value that looks converged (D2-s3-71: +0.09..+0.25 of
UA per unit of aperture error over six plants; the study's dark-only arm
collapses the spread to 0.0001). Closes #2223, the class `N-confounded-learner`.

**What changed.** Three residual-fed folds and the drift refit take one shared
dark gauge, `HEAT_LOSS_MAX_SOLAR_W_M2 = 50 W/m²` — the threshold
`_fold_internal_gains` already used, which is the RCA's instruction. At that
irradiance the modelled solar gain is 0.30 kW on the shipped aperture product,
under 0.02 K of one half-hour interval's residual against the learner's 1.0 K
rejection.

- `_async_learn_house_heat_loss` and `_async_learn_lower_floor_loss` return
  before their Newton steps on a sunlit interval. The house fold's gate sits
  **after** the open-window CUSUM feed and after `_fold_solar_aperture`, so the
  detector still sees the day's power and sun range (#2241's carry) and the
  aperture learner keeps the daylight.
- `accuracy.heat_loss_refit` records the interval's irradiance on
  `AccuracySample` (declared in `store.DOMAINS`, so `finite_boundary` drives it)
  and refuses a sunlit pair; it pools the interval learner's own relation, so it
  inherits that learner's gate. A sample with no recorded sun reads as no sun,
  the tree's rule for an unknown irradiance, and the loader accepts any value
  its domain declares.
- `_fold_internal_gains` folds only once the heat-loss walk has converged
  (`house_loss_confidence` >= `INTERNAL_GAINS_MIN_UA_CONFIDENCE`, 0.9). One
  residual feeds both learners and the residual's ΔT-proportional part is
  hour-correlated, so an unidentified level would be learned as an hour shape.
  The RCA delegates this decision to the class's fix PR and names two shapes;
  both are measured and neither works (`## Alternatives`).

**Moved, not added.** The coordinator is at zero structure headroom and its
architecture score must not rise. The zone-temperature choice the house fold
made twice and the zone-capacity choice the #36 and #53 folds each spelled out
now answer from one pure helper each, and the house fold's two one-sided dt
guards are one range check. Net: the same line count, and the score improves.

## Head

`b4d0dd974`, merged with `origin/main` `7416f340a` (the merge `96c0678b0` added
`c928f6169`'s first harness; no hunk of this diff conflicts). Base for every
figure: `2dadcdc8c`, the merge base. Measured 2026-10-20. The full feature-suite
run in Figures is at `9d60bbf7d`; `git diff 9d60bbf7d b4d0dd974` is one
docstring and one blank line.

## Mutation proof

Ten mutants, applied one at a time to a worktree of this head
(`9d60bbf7d`) and restored: one deleted guard or flipped comparison per site
`ci_predict` lists. Each was measured with the two instruments that pin the
property — the in-tree companion
(`dev/audit/harnesses/r10_night_folds_learners.py`, production symbols) and a
two-line probe of the two moved pure functions — and each line names the
`tests/features.py` check that asserts the same property. The clean head's
suite is green (Figures).

- S1 the refit's sun guard deleted (`accuracy.py`): `refit.sunlit.pairs=192`
  (head `0`) → `#2223: a sunlit window offers the refit no pair at all`.
- S2 `_learned_zone_temperature`'s two-zone guard off: probe `23.0 23.0` (head
  `23.0 19.0`), and `gains.converged.rel_dev=1.0000` (head `1.9800`) →
  `#2223: a fold's zone is the upper floor in two-zone mode, else the room`.
- S3 its room return deleted: probe `23.0 None` → the same check.
- S4 `_zone_capacity`'s return deleted: probe `None None` and the companion
  raises on `capacity <= 1e-6` → `#2223: and the fold's capacity is that same
  zone's thermal mass`.
- S5 the house fold's sun gate off: `house.sunlit.samples=8` (head `0`) →
  `#2223: a sunlit interval takes no house heat-loss sample`.
- S6 the lower fold's sun gate off: `lower.sunlit.samples=1` (head `0`) →
  `#2223: the lower-floor split takes a night interval and refuses a sunlit one`.
- S7 the gains fold's `settled <` flipped to `>`: `gains.unconverged.rel_dev`
  `0.0990` (head `0.0000`), `gains.converged.rel_dev` `0.0000` (head `1.9800`)
  → `#2223: the hour shape waits for the heat-loss level` and `#2223: and folds
  its hour once the level has converged`.
- S8 the gains fold's sun gate off: the companion is unchanged, because
  production reaches that fold only after the house fold's night gate; the
  direct-call check `sunny intervals are the aperture learner's business, never
  this one's` fails.
- S9 the gauge's `>` flipped to `>=`: probe `50.0 -> True` (head `False`) →
  `#2223: the dark gauge is inclusive at its own threshold, and unknown is
  dark`.
- S10 the gauge's return deleted: probe `None None None None`, and the companion
  reads the base's numbers (`house.sunlit.samples=8`, `refit.sunlit.pairs=192`)
  → the same check.

Failing test first: at the tests-only commit `df4266c06`, `tests/features.py`
dies before any check runs — `TypeError: AccuracySample.__init__() got an
unexpected keyword argument 'solar_radiation'` at the new `_rs_rows` fixture.
The same eight behaviour arms, driven against the base tree by a scratch mirror
of the checks (with the gauge stubbed to the base's "nothing is gated"), read
6 FAIL (`house day refuses` on 8 samples, `aperture keeps the day` with
heat-loss samples 8, the detector/fold split, `lower ... day` on 1 sample,
`gains waits for the level` with the profile formed at 8 samples, and the
gauge) and 2 ok (the night arms that must keep working); the refit arm cannot
run at the base at all, which is the field the fix adds.

## Null control

The flat-irradiance arm, where the aperture multiplies zero: `fixed_arm_spread`
0.0000 on all five plants at both ends (P1..P5 `.flat.g1.00`, Figures). The
companion's dark arms read identically at both ends: `house.dark.samples=8`,
`lower.dark.samples=1`, `refit.dark.pairs=192`, and the positive gains arm
1.9800 → the fix stops the confounded arm without stilling the learners it
should leave alone. The aperture learner is untouched: P1 `.solar_scale.learn`
1.359 at both ends, 1142 samples, 27.19 per day.

## Figures

All at `2dadcdc8c` (base) and `b4d0dd974` (head) on 2026-10-20, `load1` 15-90 on
a shared box; every harness file used is byte-identical at both ends (the two
new ones are copies in the base worktree).

Finder's harness `dev/audit/rounds/round10/study-ident/ident_rolling.py`, the
full grid via `dev/audit/rounds/round10/study-ident/run_q1.sh OUTDIR` (20 jobs,
`rc=0` at both ends). `fixed_arm_spread` is the report's own line: the spread of
learned UA across the six fixed-aperture arms {0.5, 0.75, 1.0, 1.25, 1.5, 2.0} x
truth, i.e. the bias per unit of aperture error times 1.5.
- P0 autumn 0.2691 -> 0.0147; P1 0.3790 -> 0.0219; P2 0.1405 -> 0.0074;
  P3 0.3383 -> 0.0205; P4 0.2383 -> 0.0101; P5 0.2894 -> 0.0168 (delivery 1.0).
- P1 autumn at delivery 0.4: 0.3962 -> 0.0224; at 0.6: 0.3925 -> 0.0218.
- The `indep` scenario, whose sun is independent of dT by construction:
  P1 0.3918 -> 0.0230, P2 0.1432 -> 0.0078, P3 0.3432 -> 0.0218,
  P4 0.2474 -> 0.0116, P5 0.2902 -> 0.0178.
- P1 autumn `ua_bias.fix2.00` (model aperture twice the truth): +0.2474 ->
  +0.0157; `.learn` -0.0262 -> -0.0001; `.learn+gains` -0.0332 -> -0.0111;
  `.none` -0.0900 -> -0.0038. The delivery-shortfall arms move the other way
  (P1 g0.4 `fix1.00` +0.4423 -> +0.5833): that arm is the commanded-power replay
  confound the harness documents (`delivery 0.4: fix1.00 ua_bias ~ +1.5`), and
  the study's own night-only arm reads +0.5946 there at the base — the head
  matches the shape the finder measured, not a new bias.

Companion `dev/audit/harnesses/r10_night_folds_learners.py`, command in its
header, because the sweep's probes re-implement the learners and their fixture
predates the irradiance field: base `house.sunlit.samples=8`,
`lower.sunlit.samples=1`, `refit.sunlit.pairs=192`,
`gains.unconverged.rel_dev=0.0990`; head `0`, `0`, `0`, `0.0000`.

The sweep's enumerator
`dev/audit/rounds/round10/D14/sweep-N-confounded-learner/enumerate.py` reads
identically at both ends (4 PROBE FAIL, 3 PASS): its `probe_house_ua` and
`probe_lower_floor` drive a re-implementation (`_ua_walk`), `probe_refit` builds
samples with no irradiance, and `probe_internal_gains` calls the fold directly —
none of them reads the production path this diff moves. `probe_lower_floor`'s
`gated` is a source-text search for the string `solar_radiation` inside the
method, and the gate is now a call to `is_sunlit_interval`.

Every seam the enumerator returns, against its disposition on this head:
- `_async_learn_house_heat_loss`, `_async_learn_lower_floor_loss`,
  `heat_loss_refit`, `_fold_internal_gains` — the four instances, closed in this
  diff (companion, above).
- `_fold_solar_aperture` — already guarded (a demeaned covariance on modelled
  Q_solar, sunny intervals only, and its input path is untouched here).
- `sysid.identify`, `sysid.identify_slab` — already guarded (the night-gated
  experiment with its intercept column).
- `sysid._lm_solve`, `sysid._slab_ua_profile_halfwidth`, `diagnosis.attribute`,
  `drift.update`, `flow_lift.observe`, `price_model.observe_day` — not
  applicable, unchanged and unread by this diff (solver helper, uncertainty
  width, one-shot diagnostic, a CUSUM statistic, the curve-bias term whose job
  is to absorb curve error, and descriptive price statistics).

The two alternatives the RCA named for the internal-gains coupling,
`dev/audit/harnesses/r10_night_folds_alternatives.py`, positive arm = 0.6 kW of
free heat against a 0.3 kW prior, read as `rel_dev` of the learned profile:
- "residual net of the UA fold's ΔT-proportional part": UA arm 0.0000 and
  positive arm 0.0000 — the UA fold attributes the whole residual to ΔT
  (`ΔUA = -e·C/(ΔT·Δt)`), so the net is identically zero and the learner dies.
- "regularise until the probe stays under 5 %": ridge 0.02 (shipped) UA arm
  1.0000 / positive 0.7143; ridge 1.00 UA arm 0.0500 / positive 0.0476 — the
  ridge that meets the bar leaves 6.7 % of the learner's response.
- The shipped design: the companion's `gains.unconverged` 0.0000 and
  `gains.converged` 1.9800.

Carry controls from the roster:
- `dev/audit/harnesses/r10_vent_bias_window.py` (the vent detector, #2241): the
  delivery 1.0 / UA 1.0 / no-window arm `false_share` 0.000 on all four
  seed x loop arms at both ends; wide (300 W/K) planted windows detected on all
  20 arms at every duration at both ends (60/60 RESULT lines finite). `detect_h`
  moves by at most 0.25 h on those arms. One marginal arm changes: the 150 W/K x
  4 h window is detected on 14 of 20 at the base and 13 of 20 at the head
  (`seed1.onoff.g1.0.ua1.0.vent150x4h`, 3.75 h -> never inside the window); the
  detector's text and construction are untouched, and the trigger is the
  learned UA at the trip point moving with the learners.
- `dev/audit/harnesses/r10_vent_sun_transient.py` (#2391's carry, landed here so
  the figure is re-runnable): byte-identical at both ends. Check schedule bias
  0.4 K `[0, 0, 0, 0]`, 1.0 K `[0, 20, 0, 0]`; census schedule bias 0.4 K
  `[0, 27, 0, 0]`, 1.0 K `[0, 39, 38, 30]`; every arm `end_tripped=False`. The
  carry's condition (that this group's aperture fix removes the transient) does
  not hold, so the `tests/features.py` check stays at 0.4 K and the R10-P5
  census keeps its end-state read.

Structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`; the
diff moved `seam_cut_total` 719 -> 717 (recorded in its own commit).

Suite: `PYTHONPATH=tests/hastub python3 tests/features.py` prints
`ALL 4274 FEATURE CHECKS PASSED`.

Boundary and schema: `PYTHONPATH=tests/hastub python3 tests/finite_boundary.py`
prints `ALL 106 FINITE BOUNDARY CHECKS PASSED`, including the stored-field sweep
(`samples/#/solar_radiation` declared and reachable; the loader is caught
drifting from its domain by the sweep's in-domain probe).

## Architecture score

`python3 tools/audit/archscore/score.py --diff 2dadcdc8c` prints
`Architecture score: dS +0.3110 IMPROVES`: `duplication_copies` 41 -> 40 and
`coord_footprint` 2498 -> 2497, both from the two moved pure helpers. No metric
rises, so there is no gate rise to explain.

## Alternatives

The RCA's two internal-gains shapes, measured above. Also considered and not
taken: a clock-based night window (the tree has one in `SysIdConfig`, but the
confound is the *measured* solar term, and a clock window folds an overcast noon
and skips a bright evening); a gate only on the interval's `dt_h`; and moving
the aperture fold above the max-residual guard so the night gate could merge
with it (that changes the aperture learner's input, so it is a different
learner's change, not this one's).

## Red checks

`mutation` is predicted red, and by name: `prepr.sh` step 6d lists twelve
sites the diff adds with no pin, and `mutation` fails on a mutant no pin kills.
Each site is answered under `## Unpinned sites` (eight are killed by a value
check, two by the mutation table's own pins); `mutation-autofix` pins the rest
after the push, as `ci-autofix.md` prescribes. The cheaper detector is step 6d
itself, which prints these twelve before the push; only CI's pin chain says
which survive it.

No other check has reported at this head: the pull request is opened from this
handoff and the reviewer reads its check-runs.

## Unpinned sites

`prepr.sh` step 6d lists twelve sites this diff adds. Each, with its
disposition:
- `custom_components/heatpump_optimizer/accuracy.py:694 GUARD_OFF` — value
  check `#2223: a sunlit window offers the refit no pair at all`.
- `custom_components/heatpump_optimizer/coordinator.py:1085 GUARD_OFF` — value
  check `#2223: a fold's zone is the upper floor in two-zone mode, else the
  room`.
- `custom_components/heatpump_optimizer/coordinator.py:1087 RETURN_DEL` — the
  same value check.
- `custom_components/heatpump_optimizer/coordinator.py:1092 RETURN_DEL` — value
  check `#2223: and the fold's capacity is that same zone's thermal mass`.
- `custom_components/heatpump_optimizer/coordinator.py:5086 CMP_BOUND*2` — the
  merge of the pre-fix pair of sample-hours guards; unpinned before and after
  (`grep -rn 'HOUSE_LOSS_M.._SAMPLE_HOURS' tests/` finds nothing), so
  `mutation-autofix`'s table pins or triages it. No bound changes and no
  interval the pre-fix pair admitted is added.
- `custom_components/heatpump_optimizer/coordinator.py:5086 GUARD_OFF` — the
  same line, the same disposition.
- `custom_components/heatpump_optimizer/coordinator.py:5152 GUARD_OFF` — value
  check `#2223: a sunlit interval takes no house heat-loss sample`.
- `custom_components/heatpump_optimizer/coordinator.py:5246 GUARD_OFF` — value
  check `#2223: the lower-floor split takes a night interval and refuses a
  sunlit one`.
- `custom_components/heatpump_optimizer/coordinator.py:9029 CMP_BOUND` — value
  check `#2223: the hour shape waits for the heat-loss level`.
- `custom_components/heatpump_optimizer/coordinator.py:9032 GUARD_OFF` — value
  check `sunny intervals are the aperture learner's business, never this one's`.
- `custom_components/heatpump_optimizer/thermal_model.py:1583 CMP_BOUND` — value
  check `#2223: the dark gauge is inclusive at its own threshold, and unknown
  is dark`.
- `custom_components/heatpump_optimizer/thermal_model.py:1583 RETURN_DEL` — the
  same value check.

The stale pin `…._fold_internal_gains.GUARD_OFF.47d9953d.json` named the
pre-#2223 guard text; it is deleted in its own commit, and `ci_predict` now
prints `no closures or fast red predicted`.

## Forward-carry

- The class barrier the RCA proposes — a `tests/` script driving every
  residual-fed learner with error only in the other covariate — is the D2
  dimension's step-5 duty and lands in the briefs group, not here (the roster
  carry says so). Its arms must drive the learners together: the gains arm needs
  a converged level and a genuine gain, which is the positive arm the companion
  harness already prints. Carry: R10-BRIEFS-FOLD, whose duty this is at
  `dev/governance/dimensions/D2.md` (group entry in
  `dev/programme/rosters/wave-r10-groups.json`).
- Measured consequence, recorded and not carried: the delivery-shortfall arms
  move (above); they are the commanded-power replay confound, measured by the
  study's own dark arm at the base. Carry: dismissed: measured not defect.
- The marginal 150 W/K x 4 h window loses one of twenty arms (above); the
  detector is not this group's seam, its 300 W/K control holds, and the
  movement follows the learned UA rather than a detector change.
  Carry: dismissed: measured consequence in figures.
- The roster carry's owner-bundle instruction ("report the vent freeze share
  beside the UA figures when the owner's bundle is re-measured") cannot be run
  here: the bundle is owner data held outside the tree. Recorded so the next
  seat that has it runs it. Carry: dismissed: owner data outside tree.

## Friction

none
