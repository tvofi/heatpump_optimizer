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

**This pass (fixer, 2026-10-21).** The handoff `b4d0dd974` was 120 commits
behind `main`. Two merges of `origin/main` (`c16e6a417`, then `79a542be2`; no
rebase, no force) bring it current; neither conflicted on a production hunk,
and the learner fix is intact:
`git diff 7416f340a b4d0dd974 -- custom_components` and
`git diff 6961f0663 79a542be2 -- custom_components` carry the same changed
lines. One test commit, `915a6b883`, pins the house fold's dt window at both
bounds, which no check pinned before (`## Unpinned sites`). The prepr refusal
this pass answers was `## Unpinned sites` naming the pre-merge line numbers;
every site below is keyed at this head.

## Head

`79a542be2`, merged with `origin/main` `6961f0663` (also the merge base).
Taken 2026-10-21 (UTC) with `origin/main` at
`0cc148b2f` for the harness and mutation runs and at `6961f0663` for the
final merge. The harness figures and mutants were driven at `c16e6a417` /
`915a6b883` against base `0cc148b2f`; the second merge's delta reaches no file
they read —
`git diff --name-only 0cc148b2f 6961f0663 -- custom_components tests/features.py tests/finite_boundary.py tests/harness.py tests/hastub dev/audit/rounds dev/audit/harnesses`
prints only `dev/audit/harnesses/r10_gate_priority_base.py`, a harness no
figure here runs, and `git diff --name-only c16e6a417 79a542be2 -- custom_components`
prints nothing. The scripts the second merge's files feed were re-run at
`79a542be2` (Figures).

## Mutation proof

Thirteen mutants over the twelve sites `ci_predict` lists, the mutation
table's own operators (`GUARD_OFF` → `if False:`, `RETURN_DEL` → `pass`,
`CMP_BOUND` flips one comparison's strictness), each applied alone to a
detached worktree of `c16e6a417` (`915a6b883` for R05a/R05b/R06) and driven
through `PYTHONPATH=tests/hastub python3 tests/features.py`, whose unmutated
run at both heads is green (Figures). Each line names the checks that went red.

- A01 `accuracy.py:694 GUARD_OFF` — driven through the canonical instrument,
  `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --anchor "custom_components/heatpump_optimizer/accuracy.py:_refit_pair GUARD_OFF 13c5d9a2" --scripts tests/features.py`:
  baseline `rc=0 failed=0`, null control `accuracy.py:49 NULL_COMMENT`
  survived, `killed by tests/features.py`.
- M02 `coordinator.py:1090 GUARD_OFF` → `#2223: a fold's zone is the upper
  floor in two-zone mode, else the room` and `the two-zone fit moves with the
  upper zone's mass and not the house's` (2 of 4283).
- M03 `coordinator.py:1092 RETURN_DEL` → the two `D12-s1-01` seed checks fail,
  then the run dies (`TypeError: unsupported operand type(s) for -:
  'NoneType' and 'float'`, rc=1).
- M04 `coordinator.py:1097 RETURN_DEL` → the run dies in
  `_fold_solar_aperture` (`capacity <= 1e-6` on `None`, rc=1).
- M05a / M05b `coordinator.py:5091 CMP_BOUND*2` — survived the suite at
  `c16e6a417` (rc=0, 4283 passed); at `915a6b883` R05a (`dt_h <= MIN`) fails
  `#2223: the house fold's interval window is inclusive at both bounds`;
  R05b (`dt_h >= MAX`) fails the same check (`{539: 0, 540: 1, 5400: 0,
  5401: 0}`), 1 of 4284 each.
- M06 `coordinator.py:5091 GUARD_OFF` → `D1-s2-04: every cycle-path fence
  surfaces …` fails and the run dies (rc=1); R06 at `915a6b883` reads the
  same (the run dies before reaching the window check).
- M07 `coordinator.py:5157 GUARD_OFF` → `#2223: a sunlit interval takes no house
  heat-loss sample`, `#2223: the sunlit interval is still the aperture
  learner's`, `#2223: the detector is fed the interval even when the heat-loss
  fold refuses it` (3 of 4283).
- M08 `coordinator.py:5251 GUARD_OFF` → `#2223: the lower-floor split takes a
  night interval and refuses a sunlit one` (1 of 4283).
- M09 `coordinator.py:9041 CMP_BOUND` (`settled <=`) — survives (rc=0); an
  equivalent mutant, triaged under `## Unpinned sites`.
- M10 `coordinator.py:9044 GUARD_OFF` → `sunny intervals are the aperture
  learner's business, never this one's` (1 of 4283).
- M11 `thermal_model.py:1583 CMP_BOUND` → `#2223: the refit's dark gauge is the
  tree's, inclusive at the threshold` and `#2223: the dark gauge is inclusive at
  its own threshold, and unknown is dark` (2 of 4283).
- M12 `thermal_model.py:1583 RETURN_DEL` → 9 of 4283, every `#2223` sun arm among
  them (`a sunlit window offers the refit no pair at all`, `a sunlit interval
  takes no house heat-loss sample`, `the lower-floor split takes a night
  interval and refuses a sunlit one`, `sunny intervals are the aperture
  learner's business, never this one's`, …).

Failing test first: at the tests-only commit `df4266c06`, `tests/features.py`
dies before any check runs — `TypeError: AccuracySample.__init__() got an
unexpected keyword argument 'solar_radiation'` at the new `_rs_rows` fixture.
The window check this pass adds was red first by the same rule: R05a above is
the production line's mutant failing it.

## Null control

The flat-irradiance arm, where the aperture multiplies zero: `fixed_arm_spread`
0.0000 on all five plants at both ends (P1..P5 `.flat.g1.00`, Figures). The
companion's dark arms read identically at both ends: `house.dark.samples=8`,
`lower.dark.samples=1`, `refit.dark.pairs=192`, and the positive gains arm
`gains.converged.rel_dev=1.9800` → the fix stops the confounded arm without
stilling the learners it should leave alone. The aperture learner is untouched:
P1 `.solar_scale.learn` 1.359 at both ends, n=1142, 27.19 samples per day at
the head. For the mutants: the unmutated suite is green at both mutated heads,
and the anchor drive's comment-only null mutant survived.

## Figures

Base `0cc148b2f` (then the merge base) and head `c16e6a417`, 2026-10-21, on a
4-CPU cloud box with the gate and mutants running beside them; every harness
file used is byte-identical at both ends (`cmp` of `ident_rolling.py`,
`enumerate.py` and `r10_vent_bias_window.py`; the three this PR adds are copies
in the base worktree). All re-taken this pass; each equals the previous body's
value except where noted.

Finder's harness `dev/audit/rounds/round10/study-ident/ident_rolling.py`, the
full grid via `dev/audit/rounds/round10/study-ident/run_q1.sh OUTDIR` (20 jobs,
20 `rc=0` lines in `OUTDIR/rc.log` at each end). `fixed_arm_spread` is the
report's own line: the spread of learned UA across the six fixed-aperture arms
{0.5, 0.75, 1.0, 1.25, 1.5, 2.0} x truth, i.e. the bias per unit of aperture
error times 1.5.
- P0 autumn 0.2691 -> 0.0147; P1 0.3790 -> 0.0219; P2 0.1405 -> 0.0074;
  P3 0.3383 -> 0.0205; P4 0.2383 -> 0.0101; P5 0.2894 -> 0.0168 (delivery 1.0).
- P1 autumn at delivery 0.4: 0.3962 -> 0.0224; at 0.6: 0.3925 -> 0.0218.
  P0 at 0.4: 0.2677 -> 0.0154; at 0.6: 0.2757 -> 0.0150.
- The `indep` scenario, whose sun is independent of dT by construction:
  P1 0.3918 -> 0.0230, P2 0.1432 -> 0.0078, P3 0.3432 -> 0.0218,
  P4 0.2474 -> 0.0116, P5 0.2902 -> 0.0178.
- P1 autumn `ua_bias.fix2.00` (model aperture twice the truth): +0.2474 ->
  +0.0157; `.learn` -0.0262 -> -0.0001; `.learn+gains` -0.0332 -> -0.0111;
  `.none` -0.0900 -> -0.0038. The delivery-shortfall arms move the other way
  (P1 g0.4 `fix1.00` +0.4423 -> +0.5833): that arm is the commanded-power replay
  confound the harness documents (`delivery 0.4: fix1.00 ua_bias ~ +1.5`), and
  the study's own dark arm (`P1.autumn.g0.40.ua_bias.dark1.00`) reads +0.5946
  there at the base — the head matches the shape the finder measured, not a new
  bias.

Companion `dev/audit/harnesses/r10_night_folds_learners.py`, command in its
header, because the sweep's probes re-implement the learners and their fixture
predates the irradiance field: base `house.sunlit.samples=8`,
`lower.sunlit.samples=1`, `refit.sunlit.pairs=192`,
`gains.unconverged.rel_dev=0.0990`; head `0`, `0`, `0`, `0.0000`.

The sweep's enumerator
`dev/audit/rounds/round10/D14/sweep-N-confounded-learner/enumerate.py`
(sha1 `9f7e163704501c8e59393b3c93190afb539caa4d`, `PYTHONPATH=tests/hastub`).
**Self-correction:** the previous body said it "reads identically at both ends
(4 PROBE FAIL, 3 PASS)". Re-run, it does not, and its SEAM list is what
reads identically (`diff` of the `^SEAM` lines at both ends is empty). Its three
CONTROL lines and `PROBE-NULL` pass at both ends. The probes: base — house
FAIL `ua_scale=0.925`, lower FAIL `lower_ratio=0.925 gated=False`, refit FAIL
`refit_scale=0.937`, internal-gains FAIL `gains_max_rel_dev=0.820`; head —
house FAIL `0.925` and refit FAIL `0.937` unchanged (a re-implementation
`_ua_walk`, and samples built with no irradiance: neither reads the path this
diff moves), lower PASS `lower_ratio=1.000 gated=True` (its `gated` is a
source-text search for `solar_radiation` inside the method), and
`probe_internal_gains` raises `TypeError: 'NoneType' object is not iterable`
(rc=1) — it calls the fold directly at an unconverged level and reads the
profile, which this diff's convergence gate leaves unformed, so the probe's
own premise is what the fix removed; the companion's `gains.unconverged` arm
measures that property through the production path instead.

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
`dev/audit/harnesses/r10_night_folds_alternatives.py` (output identical at both
ends), positive arm = 0.6 kW of free heat against a 0.3 kW prior, read as
`rel_dev` of the learned profile:
- "residual net of the UA fold's ΔT-proportional part":
  `net_of_ua_part.rel_dev=0.0000`, `positive_rel_dev=0.0000` — the UA fold
  attributes the whole residual to ΔT (`ΔUA = -e·C/(ΔT·Δt)`), so the net is
  identically zero and the learner dies.
- "regularise until the probe stays under 5 %": ridge 0.02 (shipped) UA arm
  1.0000 / positive 0.7143; ridge 1.00 UA arm 0.0500 / positive 0.0476 — the
  ridge that meets the bar leaves 6.7 % of the learner's response.
- The shipped design: the companion's `gains.unconverged` 0.0000 and
  `gains.converged` 1.9800.

Carry controls from the roster:
- `dev/audit/harnesses/r10_vent_bias_window.py` (the vent detector, #2241),
  tallied by rule — no-window arms are `.g1.0.ua1.0.vent0x0h`, a window is
  detected when `detect_h` is finite: the no-window arms read `false_share`
  0.000 on all 4 at both ends; the 300 W/K windows are detected on 60 of 60
  arms at both ends; `detect_h` moves by at most 0.25 h on them. One marginal
  arm changes: the 150 W/K x 4 h window is detected on 14 of 20 at the base and
  13 of 20 at the head (`seed1.onoff.g1.0.ua1.0.vent150x4h`, 3.75 h -> never);
  the detector's text and construction are untouched, and the trigger is the
  learned UA at the trip point moving with the learners.
- `dev/audit/harnesses/r10_vent_sun_transient.py` (#2391's carry): output
  identical at both ends. Check schedule bias 0.4 K `[0, 0, 0, 0]`, 1.0 K
  `[0, 20, 0, 0]`; census schedule bias 0.4 K `[0, 27, 0, 0]`, 1.0 K
  `[0, 39, 38, 30]`; every arm `end_tripped=False`. The carry's condition (that
  this group's aperture fix removes the transient) does not hold, so the
  `tests/features.py` check stays at 0.4 K and the R10-P5 census keeps its
  end-state read.

The scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir D`
prints `MODE: SCOPED -- 29 script(s) run, 4 scoped out.` at both merged heads
(their `scope.run` files are identical). Every script it names but
`tests/stress.py` (left to CI, fixer step 5), plus `run.sh`'s `run_always`
lines (`env_drift.py --claims-only`, `closure.py selftest`, `layout.py`), ran
at `c16e6a417` with `PYTHONPATH=tests/hastub` and `GOLDEN_MODE=drift`: 31 of
31 `rc=0`, among them `ALL 4283 FEATURE CHECKS PASSED`,
`ALL 106 FINITE BOUNDARY CHECKS PASSED` (the stored-field sweep drives
`samples/#/solar_radiation`), `NO STALE FIXTURE: 56 committed fixture(s)`
(`golden.py`) and `ALL 2363 ENTITY CHECKS PASSED`
(`env -u BASH_ENV python3 tests/entities.py`). At `915a6b883`:
`ALL 4284 FEATURE CHECKS PASSED`. At `79a542be2`, the scripts the second
merge's files feed: `ALL 124 closure shrink pins PASSED`,
`STRUCTURE RATCHET PASSED`, `ALL 2375 ENTITY CHECKS PASSED`,
`ALL 109 HARNESS HEADER CHECKS PASSED`.

Structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`
at `79a542be2`. The first merge's ledger driver combined `seam_cut_total`
as 719 + both deltas = 716 (this diff's 719 -> 717 and main's own); no budget
is raised.

## Architecture score

`python3 tools/audit/archscore/score.py --diff 6961f0663` prints
`Architecture score: dS +0.3110 IMPROVES`: `duplication_copies` 41 -> 40 and
`coord_footprint` 2494 -> 2493, both from the two moved pure helpers. No metric
rises, so there is no gate rise to explain.

## Alternatives

The RCA's two internal-gains shapes, measured above. Also considered and not
taken: a clock-based night window (the tree has one in `SysIdConfig`, but the
confound is the *measured* solar term, and a clock window folds an overcast noon
and skips a bright evening); a gate only on the interval's `dt_h`; and moving
the aperture fold above the max-residual guard so the night gate could merge
with it (that changes the aperture learner's input, so it is a different
learner's change, not this one's). For the two surviving `CMP_BOUND` mutants
at `coordinator.py:5091`, a value check was taken over a triage: both are
killable, and a triage on a killable mutant moves a metric without improving
the code (fixer step 17).

## Red checks

`mutation` is predicted red, and by name: `prepr.sh` step 6d lists twelve sites
the diff adds with no ledger pin, and `mutation` fails on a mutant no pin
kills. Each site is answered under `## Unpinned sites` — eleven are killed by a
named check in this head's suite (measured above), and one is an equivalent
mutant with a written triage; `mutation-autofix` records the killed ones'
pins after the push, as `ci-autofix.md` prescribes. The cheaper detector is
step 6d itself, which prints the sites before the push; only CI's pin chain
records them.

`nightly-status` is `main`'s, not this branch's: the replay `loop_cpu_ratio`
budget, which the orchestrator's brief for this pass reads as red on `main`
independently of this branch; this diff touches no replay file. The orchestrator carries
it to R10-REPLAY-CAP; that group is not yet in `dev/programme/rosters/` at
this head, so this body names it and writes no `Carry:` line for it.

No other check has reported at this head: the pull request is opened from this
handoff and the reviewer reads its check-runs.

## Unpinned sites

`prepr.sh` step 6d lists twelve sites this diff adds, keyed at `79a542be2`.
Each, with its disposition (the mutant runs are under `## Mutation proof`):
- `custom_components/heatpump_optimizer/accuracy.py:694 GUARD_OFF` — value
  check `#2223: a sunlit window offers the refit no pair at all`; the anchor
  drive records `killed by tests/features.py` (A01); `mutation-autofix` pins it.
- `custom_components/heatpump_optimizer/coordinator.py:1090 GUARD_OFF` — value
  check `#2223: a fold's zone is the upper floor in two-zone mode, else the
  room` (M02).
- `custom_components/heatpump_optimizer/coordinator.py:1092 RETURN_DEL` — killed
  by `tests/features.py` (M03: rc=1, `D12-s1-01` seed checks, then the run
  dies on the `None` zone temperature).
- `custom_components/heatpump_optimizer/coordinator.py:1097 RETURN_DEL` — killed
  by `tests/features.py` (M04: rc=1, the run dies on the `None` capacity).
- `custom_components/heatpump_optimizer/coordinator.py:5091 CMP_BOUND*2` — value
  check `#2223: the house fold's interval window is inclusive at both bounds`,
  added in `915a6b883` (R05a, R05b).
- `custom_components/heatpump_optimizer/coordinator.py:5091 GUARD_OFF` — killed
  by `tests/features.py` (M06; R06 at `915a6b883`).
- `custom_components/heatpump_optimizer/coordinator.py:5157 GUARD_OFF` — value
  check `#2223: a sunlit interval takes no house heat-loss sample` (M07).
- `custom_components/heatpump_optimizer/coordinator.py:5251 GUARD_OFF` — value
  check `#2223: the lower-floor split takes a night interval and refuses a
  sunlit one` (M08).
- `custom_components/heatpump_optimizer/coordinator.py:9041 CMP_BOUND` — written
  triage, equivalent mutant: `settled` is `house_loss_confidence(n)` of an
  integer sample count, `1 - 0.98**n`, which is monotone in `n` and never equals
  `INTERNAL_GAINS_MIN_UA_CONFIDENCE` (0.9), so `<` and `<=` admit the same
  counts. Re-run:
  `PYTHONPATH=tests/hastub:custom_components python3 -c "from heatpump_optimizer.coordinator import house_loss_confidence as h, INTERNAL_GAINS_MIN_UA_CONFIDENCE as t; print([n for n in range(100000) if h(n) == t], h(113) < t < h(114))"`
  prints `[] True` (null control: the same list with `t=h(114)` as the
  threshold prints `[114]`, so the search finds an equal count when one exists). M09 survives the suite, as the triage predicts.
- `custom_components/heatpump_optimizer/coordinator.py:9044 GUARD_OFF` — value
  check `sunny intervals are the aperture learner's business, never this one's`
  (M10).
- `custom_components/heatpump_optimizer/thermal_model.py:1583 CMP_BOUND` — value
  check `#2223: the dark gauge is inclusive at its own threshold, and unknown is
  dark` (M11).
- `custom_components/heatpump_optimizer/thermal_model.py:1583 RETURN_DEL` — the
  same value check, with eight more (M12).

The stale pin `…._fold_internal_gains.GUARD_OFF.47d9953d.json` named the
pre-#2223 guard text; it is deleted in its own commit, and `ci_predict` prints
`no closures or fast red predicted` at this head.

## Forward-carry

- The class barrier the RCA proposes — a `tests/` script driving every
  residual-fed learner with error only in the other covariate — is the D2
  dimension's step-5 duty and lands in the briefs group, not here (the roster
  carry says so). Its arms must drive the learners together: the gains arm needs
  a converged level and a genuine gain, which is the positive arm the companion
  harness already prints. It lands at `dev/governance/dimensions/D2.md`, the
  group entry in `dev/programme/rosters/wave-r10-groups.json`.
  Carry: R10-BRIEFS-FOLD
- Measured consequence, recorded and not carried: the delivery-shortfall arms
  move (Figures); they are the commanded-power replay confound, measured by the
  study's own dark arm at the base. Carry: dismissed: measured not defect
- The marginal 150 W/K x 4 h window loses one of twenty arms (Figures); the
  detector is not this group's seam, its 300 W/K control holds, and the
  movement follows the learned UA rather than a detector change.
  Carry: dismissed: measured consequence in figures
- The roster carry's owner-bundle instruction ("report the vent freeze share
  beside the UA figures when the owner's bundle is re-measured") cannot be run
  here: the bundle is owner data held outside the tree. Carry: dismissed: owner data outside tree
- The sweep enumerator's `probe_internal_gains` now raises at this head
  (Figures): it is a round-10 measurement record, not a gate, and its premise
  (an unconverged fold forms a profile) is what this fix removes.
  Carry: dismissed: record harness, premise removed by the fix

## Friction

none
