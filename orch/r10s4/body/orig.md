The heat-loss learners absorb solar-aperture error. The replay nets the modelled
solar term out only to the accuracy of the aperture, and solar gain correlates
with the conductive term through the time of day and the outdoor temperature,
so a mis-set aperture leaves a residual the Newton step settles into the
heat-loss coefficient at a value that looks converged (D2-s3-71). Closes #2223,
the class `N-confounded-learner`.

**What changed.** Three residual-fed folds and the drift refit take one shared
dark gauge, `HEAT_LOSS_MAX_SOLAR_W_M2 = 50 W/m²`, the threshold
`_fold_internal_gains` already used (the RCA's instruction). At that irradiance
the shipped aperture product (10 m² x 0.7 x 0.7) models 0.245 kW of solar gain,
0.012 K over one half-hour interval at the 10 kWh/K room mass, under 0.02 K
against the learner's 1.0 K rejection.

- `_async_learn_house_heat_loss` and `_async_learn_lower_floor_loss` return
  before their Newton steps on a sunlit interval. The house fold's gate sits
  after the open-window CUSUM feed and after `_fold_solar_aperture`, so the
  detector still sees the day (#2241's carry) and the aperture learner keeps
  the daylight.
- `accuracy.heat_loss_refit` records the interval's irradiance on
  `AccuracySample` (declared in `store.DOMAINS`, so `finite_boundary` drives it)
  and refuses a sunlit pair. A sample with no recorded sun reads as dark, the
  tree's rule for an unknown irradiance.
- `_fold_internal_gains` folds only once the heat-loss walk has converged
  (`house_loss_confidence` >= `INTERNAL_GAINS_MIN_UA_CONFIDENCE`, 0.9): one
  residual feeds both learners, so an unidentified level would be learned as
  an hour shape. The RCA's two other shapes are measured under `## Figures`.

The zone-temperature and zone-capacity choices the folds spelled out
separately now answer from one pure helper each, and the house fold's two dt
guards are one range check, which pays the coordinator's zero headroom.

**This pass (round 2).** The PR head `829ea7c72` merged with `origin/main`
`22615537a` (no conflict, no rebase), then one commit, `749f28387`:
- The const.py comment's solar figure, 0.30 kW, is corrected to the
  production value, 0.245 kW.
- `r10_night_folds_learners.py`'s header expected `gains.unconverged ~1.0`
  at the baseline. It now says `> 0`, matching what the base measures.
- The review's blocking item, the D2 step-5 gains-arm precondition, is carried
  to R10-BRIEFS-FOLD (`## Forward-carry`).

The merge's delta (`git diff --name-only 3688cf259 22615537a`) touches only
`.github/workflows/governance.yml`, `dev/governance/roles/orchestrator.md`, two
delivery rows, `tools/audit/seat/*` and `tools/policy/budget_raise_gate.py`.
None of these is a production file or a file a harness here reads. Every figure
below was re-taken at this head anyway.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_018ePRJcytqKbuXunJxs3HqE

## Head

`749f283877d13a5975217218aed3a7f129d319ac`. That is `829ea7c72` merged with
`origin/main` `22615537a` (merge commit `37db099b8`), which is also the merge
base, plus the correction commit `749f28387`. Measured 2026-10-21 (UTC), with
`origin/main` at `22615537a`. The base worktree is detached at `22615537a`.
Python is `/opt/hpo/venv-ci`.

## Mutation proof

There are thirteen mutants over the twelve sites `ci_predict` lists at this
head, using the mutation table's own operators (`GUARD_OFF` → `if False:`,
`RETURN_DEL` → `pass`, `CMP_BOUND` flips one comparison's strictness). Each was
applied alone to a `git archive` copy of `749f28387` and driven through
`PYTHONPATH=tests/hastub python3 tests/features.py`.

The runner has its own failure. The unmutated copy (M00) and a comment-only
null mutant (`accuracy.py:49`, N00) each read `1 of 4284 FEATURE CHECKS FAILED`,
and the failing check is `the path that proceeds still stamps a resolvable
recorded_at (#363)`. That is the git-archive runner artifact fixer.md step 2
names, so a kill below is counted only on a check beyond it. The same suite in
the worktree reads `ALL 4284 FEATURE CHECKS PASSED` (the scoped gate, Figures).

- A01 `accuracy.py:694 GUARD_OFF` → `#2223: the refit's dark gauge is the tree's,
  inclusive at the threshold`, `#2223: a sunlit window offers the refit no pair
  at all`, `#2223: a half-sunny window folds only its dark half`.
- M02 `coordinator.py:1090 GUARD_OFF` → `#2223: a fold's zone is the upper floor
  in two-zone mode, else the room`, `the two-zone fit moves with the upper
  zone's mass and not the house's`.
- M03 `coordinator.py:1092 RETURN_DEL` → the two `D12-s1-01` seed checks fail,
  then the run dies with `TypeError: unsupported operand type(s) for -:
  'NoneType' and 'float'` (rc=1).
- M04 `coordinator.py:1097 RETURN_DEL` → the run dies with `TypeError: '<=' not
  supported between instances of 'NoneType' and 'float'` (rc=1).
- M05a `coordinator.py:5091 CMP_BOUND` (`dt_h <= MIN`) → `#2223: the house
  fold's interval window is inclusive at both bounds`
  (`{539: 0, 540: 0, 5400: 1, 5401: 0}`).
- M05b `coordinator.py:5091 CMP_BOUND` (`dt_h >= MAX`) → the same check
  (`{539: 0, 540: 1, 5400: 0, 5401: 0}`).
- M06 `coordinator.py:5091 GUARD_OFF` → `D1-s2-04: every cycle-path fence
  surfaces its persistent failure …`, then the run dies with `AttributeError:
  'NoneType' object has no attribute 'dhw_temp_trajectory'` (rc=1).
- M07 `coordinator.py:5157 GUARD_OFF` → `#2223: a sunlit interval takes no house
  heat-loss sample`, `#2223: the sunlit interval is still the aperture
  learner's`, `#2223: the detector is fed the interval even when the heat-loss
  fold refuses it`.
- M08 `coordinator.py:5251 GUARD_OFF` → `#2223: the lower-floor split takes a
  night interval and refuses a sunlit one`.
- M09 `coordinator.py:9041 CMP_BOUND` (`settled <=`) → survives. Only the runner
  artifact fails (`1 of 4284`). It is an equivalent mutant, triaged under
  `## Unpinned sites`.
- M10 `coordinator.py:9044 GUARD_OFF` → `sunny intervals are the aperture
  learner's business, never this one's`.
- M11 `thermal_model.py:1583 CMP_BOUND` → `#2223: the refit's dark gauge is the
  tree's, inclusive at the threshold`, `#2223: the dark gauge is inclusive at
  its own threshold, and unknown is dark`.
- M12 `thermal_model.py:1583 RETURN_DEL` → 9 checks beyond the artifact, among
  them every `#2223` sun arm above (`a sunlit window offers the refit no pair at
  all`, `a sunlit interval takes no house heat-loss sample`, `the lower-floor
  split takes a night interval and refuses a sunlit one`, …).

Failing test first: at the tests-only commit `df4266c06`, `tests/features.py`
dies before any check runs, with `TypeError: AccuracySample.__init__() got an
unexpected keyword argument 'solar_radiation'` at the new `_rs_rows` fixture.

## Null control

- **The flat-irradiance arm.** The aperture multiplies zero there, and
  `fixed_arm_spread` reads 0.0000 on P1..P5 (`.flat.g1.00`) at both ends.
- **The companion's dark arms.** These read the same at both ends:
  `house.dark.samples=8`, `lower.dark.samples=1`, `refit.dark.pairs=192`.
- **The companion's positive gains arm.** `gains.converged.rel_dev=1.9800` at
  both ends. So the fix stops the confounded arm without stilling the learners
  it should leave alone.
- **The aperture learner.** P1 `.solar_scale.learn` reads 1.359 at both ends.
- **The mutants.** M00 and N00 above.
- **The solar figure.** The same production call with `window_area` doubled to
  20 m² reads 0.4900 kW, so the instrument moves with the aperture product.

## Figures

All figures are at base `22615537a` and head `749f28387`, 2026-10-21.
- `cmp` shows the finder's files byte-identical at both ends: `ident_rolling.py`,
  `enumerate.py` and `r10_vent_bias_window.py`.
- The three harnesses this PR adds were run as copies in the base worktree.

Finder's harness: `dev/audit/rounds/round10/study-ident/ident_rolling.py`.
- **Run:** the full grid, `bash dev/audit/rounds/round10/study-ident/run_q1.sh OUTDIR`.
  That is 20 jobs, and `OUTDIR/rc.log` holds 20 `rc=0` lines at each end.
- **Metric:** `fixed_arm_spread` is the report's own line. It is the spread of
  learned UA across the six fixed-aperture arms {0.5, 0.75, 1.0, 1.25, 1.5, 2.0}
  x truth.
- **Autumn, delivery 1.0:** P0 0.2691 -> 0.0147; P1 0.3790 -> 0.0219;
  P2 0.1405 -> 0.0074; P3 0.3383 -> 0.0205; P4 0.2383 -> 0.0101;
  P5 0.2894 -> 0.0168.
- **Delivery 0.4 and 0.6:** P1 at 0.4: 0.3962 -> 0.0224; at 0.6: 0.3925 -> 0.0218.
  P0 at 0.4: 0.2677 -> 0.0154; at 0.6: 0.2757 -> 0.0150.
- **`indep`** (sun independent of dT by construction): P1 0.3918 -> 0.0230,
  P2 0.1432 -> 0.0078, P3 0.3432 -> 0.0218, P4 0.2474 -> 0.0116,
  P5 0.2902 -> 0.0178.
- **P1 autumn ua_bias:** `ua_bias.fix2.00` +0.2474 -> +0.0157; `.learn`
  -0.0262 -> -0.0001; `.learn+gains` -0.0332 -> -0.0111; `.none`
  -0.0900 -> -0.0038.
- **The delivery-shortfall arm moves the other way.** P1 g0.4 `fix1.00` reads
  +0.4423 -> +0.5833. The study's own dark arm,
  `P1.autumn.g0.40.ua_bias.dark1.00`, reads +0.5946 at the base. So the head
  matches the commanded-power replay confound the harness documents, not a new
  bias.
- **Attribution:** the residual spread (0.0219 on P1 against the study's
  dark-only 0.0001) is the 50 W/m² gauge's, by the fix review's perturbation:
  - with the gauge at 1 W/m², the head reads P1 autumn spread 0.0000;
  - the base's study dark arm at `IDENT_DARK_W_M2=50` equals the head's
    fixed arms.

  The RCA prescribes that threshold.

Companion `dev/audit/harnesses/r10_night_folds_learners.py`, with the command
in its header. It goes through the production symbols because the sweep's
probes re-implement the learners.

| line | base | head |
|---|---|---|
| `house.sunlit.samples` | 8 | 0 |
| `lower.sunlit.samples` | 1 | 0 |
| `refit.sunlit.pairs` | 192 | 0 |
| `gains.unconverged.rel_dev` | 0.0990 | 0.0000 |
| `gains.converged.rel_dev` | 1.9800 | 1.9800 |

The modelled solar gain at the gauge comes from this command:
`PYTHONPATH=tests/hastub:custom_components python3 -c "from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters; p=ThermalParameters(); g=ThermalModel(p).compute_solar_gain(50.0); print(g, g*0.5/p.room_thermal_mass)"`.
It prints `gain50_kW=0.2450 dT_halfhour_K=0.0122`, and the null control is
under `## Null control`.

The sweep's enumerator is
`dev/audit/rounds/round10/D14/sweep-N-confounded-learner/enumerate.py`
(sha1 `9f7e163704501c8e59393b3c93190afb539caa4d`, `PYTHONPATH=tests/hastub`).
- **Its SEAM list:** 13 lines, identical at both ends
  (`diff <(grep ^SEAM head) <(grep ^SEAM base)` exits 0).
- **Controls:** its three CONTROL lines and `PROBE-NULL` pass at both ends.
- **Probes at the base:**
  - house FAIL `ua_scale=0.925`;
  - lower FAIL `lower_ratio=0.925 gated=False`;
  - refit FAIL `refit_scale=0.937`;
  - internal-gains FAIL `gains_max_rel_dev=0.820`.
- **Probes at the head:** house FAIL `0.925` and refit FAIL `0.937`, unchanged.
  - Neither probe reads the path this diff moves: `_ua_walk` is a
    re-implementation, and `probe_refit` builds samples with no
    `solar_radiation`.
  - Lower reads PASS `lower_ratio=1.000 gated=True`.
  - `probe_internal_gains` raises `TypeError: 'NoneType' object is not
    iterable` (rc=1). It calls the fold directly at an unconverged level, which
    this diff's convergence gate leaves unformed. The companion's
    `gains.unconverged` arm measures that property through the production path
    instead.

Every seam the enumerator returns, against its disposition at this head:
- **Closed in this diff (the four instances):** `_async_learn_house_heat_loss`,
  `_async_learn_lower_floor_loss`, `heat_loss_refit`, `_fold_internal_gains`.
  The companion above measures them.
- **Already guarded:** `_fold_solar_aperture` (a demeaned covariance on modelled
  Q_solar, sunny intervals only, and its input path is untouched).
- **Already guarded:** `sysid.identify` and `sysid.identify_slab` (the
  night-gated experiment with its intercept column).
- **Not applicable, unchanged and unread by this diff:**
  - `sysid._lm_solve`, a solver helper;
  - `sysid._slab_ua_profile_halfwidth`, an uncertainty width;
  - `diagnosis.attribute`, a one-shot diagnostic;
  - `drift.update`, a CUSUM statistic;
  - `flow_lift.observe`, the curve-bias term, whose job is to absorb curve
    error;
  - `price_model.observe_day`, descriptive price statistics.

The RCA's two alternative internal-gains shapes are measured by
`dev/audit/harnesses/r10_night_folds_alternatives.py`. Its output is identical
at both ends (`cmp`).
- **Residual net of the UA fold's ΔT part:** `net_of_ua_part.rel_dev=0.0000`
  and `net_of_ua_part.positive_rel_dev=0.0000`. The UA fold attributes the whole
  residual to ΔT, so the learner dies.
- **Regularise:** the shipped ridge 0.02 reads 1.0000 / 0.7143. Ridge 1.00 meets
  the 5 % bar at 0.0500, but its positive arm is 0.0476: it leaves 6.7 % of the
  learner's response.

Carry controls:
- `dev/audit/harnesses/r10_vent_bias_window.py` (#2241). The command is in its
  header. The tally rule: no-window arms end `.g1.0.ua1.0.vent0x0h`, and a
  window counts as detected where `detect_h` is finite.
  - The 4 no-window arms read `false_share` 0.000 at both ends.
  - The 300 W/K windows are detected on 60 of 60 at both ends; `detect_h`
    moves by at most 0.25 h.
  - The 150 W/K x 4 h window is detected on 14 of 20 at the base and 13 of 20
    at the head. The one change is `seed1.onoff.g1.0.ua1.0.vent150x4h`,
    3.75 h -> nan. The detector is untouched; the learned UA at the trip point
    moves with the learners.
- `dev/audit/harnesses/r10_vent_sun_transient.py` (#2391), command
  `PYTHONPATH=tests/hastub:custom_components python3 …`. Its output is
  identical at both ends (`cmp`).
  - Check schedule: bias 0.4 K `[0, 0, 0, 0]`, bias 1.0 K `[0, 20, 0, 0]`.
  - Census schedule: bias 0.4 K `[0, 27, 0, 0]`, bias 1.0 K `[0, 39, 38, 30]`.
  - Every arm reads `end_tripped=False`.
  - So the features check stays at 0.4 K.

M09 triage, the command:
`PYTHONPATH=tests/hastub:custom_components python3 -c "from heatpump_optimizer.coordinator import house_loss_confidence as h, INTERNAL_GAINS_MIN_UA_CONFIDENCE as t; print([n for n in range(100000) if h(n) == t], h(113) < t < h(114))"`.
- It prints `[] True`.
- The null control uses `t=h(114)` as the threshold and prints `[114]`.

The scoped gate, from
`python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir D`:
- It prints `MODE: SCOPED -- 29 script(s) run, 4 scoped out.`
- `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=22615537a PYTHONPATH=tests/hastub bash tests/run.sh`
  at this head ended rc=0 with `31 TEST SCRIPT(S) PASSED; 3 SCOPED OUT AND NOT RUN`.
- Among those 31: `ALL 4284 FEATURE CHECKS PASSED`,
  `ALL 106 FINITE BOUNDARY CHECKS PASSED`, `ALL 2375 ENTITY CHECKS PASSED`,
  `ALL 113 STRESS CHECKS PASSED`, `ALL 109 HARNESS HEADER CHECKS PASSED` and
  `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`.

Structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`
(`seam_cut_total 716 <= 716`). No budget is raised.

`env_drift.py --claims-only` ran as a `run_always` line of that gate. The
three-dot diff names no `VERSION`, manifest, `RELEASE_NOTES.md`, golden or
claim file.

## Architecture score

`python3 tools/audit/archscore/score.py --diff 22615537a` prints
`Architecture score: dS +0.3110 IMPROVES`:
- `duplication_copies` 41 -> 40;
- `coord_footprint` 2494 -> 2493.

Both come from the two moved pure helpers. No metric rises.

## Alternatives

- **The RCA's two internal-gains shapes.** Both are measured under `## Figures`
  and both fail.
- **A clock-based night window.** The confound is the measured solar term, and
  a clock window folds an overcast noon and skips a bright evening.
- **A gate only on `dt_h`.** Not taken.
- **Moving the aperture fold above the max-residual guard.** That changes
  another learner's input.
- **A triage for the two `CMP_BOUND` mutants at `coordinator.py:5091`.** A
  value check was taken instead, because both are killable (fixer step 17).

## Red checks

`mutation`: at the PR's previous head it read
`MUTATION TABLE REFUSED … 13 of them added by this diff`. Those are the
thirteen mutants over the twelve sites under `## Unpinned sites`.
- Twelve are killed by a named check in this head's suite, measured above.
- One (M09) is an equivalent mutant with a written triage.
- `mutation-autofix` records the killed ones' pins after the push
  (`ci-autofix.md`).
- The cheaper detector is `prepr.sh` step 6d, which lists the sites before the
  push. Only CI's pin chain records them.

`nightly-status` grades `main`, not this branch: its red is main's replay
status. This diff reaches no replay-status input.

No other check was red at the previous head (the fix review's check-runs read).

## Unpinned sites

`prepr.sh` step 6d lists twelve sites this diff adds, keyed at this head.
- `custom_components/heatpump_optimizer/accuracy.py:694 GUARD_OFF` — value
  check `#2223: a sunlit window offers the refit no pair at all` (A01).
- `custom_components/heatpump_optimizer/coordinator.py:1090 GUARD_OFF` — value
  check `#2223: a fold's zone is the upper floor in two-zone mode, else the
  room` (M02).
- `custom_components/heatpump_optimizer/coordinator.py:1092 RETURN_DEL` — killed
  by `tests/features.py` (M03: the `D12-s1-01` seed checks, then rc=1).
- `custom_components/heatpump_optimizer/coordinator.py:1097 RETURN_DEL` — killed
  by `tests/features.py` (M04: rc=1 on the `None` capacity).
- `custom_components/heatpump_optimizer/coordinator.py:5091 CMP_BOUND*2` — value
  check `#2223: the house fold's interval window is inclusive at both bounds`
  (M05a, M05b).
- `custom_components/heatpump_optimizer/coordinator.py:5091 GUARD_OFF` — killed
  by `tests/features.py` (M06).
- `custom_components/heatpump_optimizer/coordinator.py:5157 GUARD_OFF` — value
  check `#2223: a sunlit interval takes no house heat-loss sample` (M07).
- `custom_components/heatpump_optimizer/coordinator.py:5251 GUARD_OFF` — value
  check `#2223: the lower-floor split takes a night interval and refuses a
  sunlit one` (M08).
- `custom_components/heatpump_optimizer/coordinator.py:9041 CMP_BOUND` — written
  triage, equivalent mutant. `settled` is `house_loss_confidence(n)` of an
  integer sample count, `1 - 0.98**n`. That is monotone in `n` and never equals
  `INTERNAL_GAINS_MIN_UA_CONFIDENCE` (0.9), so `<` and `<=` admit the same
  counts. The command and its null control are under `## Figures`; M09
  survives, as the triage predicts.
- `custom_components/heatpump_optimizer/coordinator.py:9044 GUARD_OFF` — value
  check `sunny intervals are the aperture learner's business, never this one's`
  (M10).
- `custom_components/heatpump_optimizer/thermal_model.py:1583 CMP_BOUND` — value
  check `#2223: the dark gauge is inclusive at its own threshold, and unknown is
  dark` (M11).
- `custom_components/heatpump_optimizer/thermal_model.py:1583 RETURN_DEL` — the
  same value check, with the other `#2223` sun arms (M12).

## Forward-carry

- **The D2 step-5 gains-arm precondition.** A probe of the internal-gains
  learner must run at a converged heat-loss level with a genuine gain, and the
  class barrier must drive the learners together.
  - Its control: `r10_night_folds_learners.py` `gains.converged.rel_dev` > 0.05
    with `gains.unconverged.rel_dev` 0.0000.
  - Carried to R10-BRIEFS-FOLD's `carry` list in
    `dev/programme/rosters/wave-r10-groups.json` on `handoff/audit-r10-roster`
    at SHA `617ce13160e73d82720330f1200a3e6e38ce0526`.
  - Verify with
    `git show 617ce13160e73d82720330f1200a3e6e38ce0526:dev/programme/rosters/wave-r10-groups.json | grep -c "drive the learners together"`.

  Carry: R10-BRIEFS-FOLD
- **The delivery-shortfall arms move** (Figures). They are the commanded-power
  replay confound, measured by the study's own dark arm at the base.
  Carry: dismissed: measured not defect
- **The marginal 150 W/K x 4 h window loses one of twenty arms** (Figures). The
  detector is not this group's seam, and its 300 W/K control holds.
  Carry: dismissed: measured consequence in figures
- **The roster carry's owner-bundle instruction cannot be run here.** The
  bundle is owner data held outside the tree.
  Carry: dismissed: owner data outside tree
- **The sweep enumerator's `probe_internal_gains` now raises** (Figures). It is
  a round-10 measurement record, not a gate, and its premise is what this fix
  removes. Carry: dismissed: record harness, premise removed by the fix

## Friction

none
