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

**This pass (round 3).** The PR head `9851d39de` merged with `origin/main`
`b6a38f858` (merge commit `fc235999e`; no conflict, no rebase), then one
tests-only commit, `285845eb9`:
- `mutation` was red on one site: `coordinator.py:9041 CMP_BOUND`, the
  convergence gate `settled < INTERNAL_GAINS_MIN_UA_CONFIDENCE`. Round 2 gave it
  a written triage in the body only, which the ratchet does not read. A new
  check in `tests/features.py`, `#2223: a heat-loss level exactly on the
  confidence threshold has converged`, now kills it, and `mutation-autofix`
  records the pin after the push.
- `pr-contract`'s CARRY-AUDIT refused one unrouted body item, the alternatives
  harness's ΔT-part line under `## Figures`. It is routed under
  `## Forward-carry`.

The merge's delta (`git diff --name-only 9851d39de fc235999e`) is nine files:
`.github/workflows/governance.yml`, five delivery rows, and three files under
`tools/audit/seat/`. None is a production file or a file a harness here reads.
The delta from the round-2 head `749f28387` to `9851d39de` adds the bot's
mutation-ledger pins and the `tests/requirements-*.txt` bump (aiohttp
3.14.4 -> 3.14.5), with no production file. Every figure below was re-taken at
this head anyway.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_019amZkY33pUmB8RSwieJrwa

## Head

`285845eb9bbdbdbfaae5db5c44524b9293d99162`. That is `9851d39de` merged with
`origin/main` `b6a38f858` (merge commit `fc235999e`), which is also the merge
base, plus the test commit `285845eb9`. Measured 2026-10-21 (UTC), with
`origin/main` at `b6a38f858`. The base worktree is detached at `b6a38f858`.
Python is `/opt/hpo/venv-ci` (numpy 2.4.6, scipy 1.17.1).

## Mutation proof

There are fifteen runs over the twelve sites the round-2 body listed, plus the
two controls, using the mutation table's own operators (`GUARD_OFF` →
`if False:`, `RETURN_DEL` → `pass`, `CMP_BOUND` flips one comparison's
strictness). Each was applied alone to a detached `git worktree` at `285845eb9`
and driven through `PYTHONPATH=tests/hastub python3 tests/features.py`.

The runner is a worktree this round, not a `git archive` copy, so the #363
`recorded_at` artifact round 2 netted out is absent: the unmutated tree (M00)
and a comment-only null mutant (`accuracy.py:49`, N00) each read
`ALL 4285 FEATURE CHECKS PASSED` (rc=0).

- **M09 `coordinator.py:9041 CMP_BOUND` (`settled <=`), this round's site** →
  `#2223: a heat-loss level exactly on the confidence threshold has converged`
  (`1 of 4285`, rc=1). The detail reads `on the threshold False, one sample
  under False`. The same mutant was also run in place in the worktree before the
  commit, with the same single failure.
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
- M10 `coordinator.py:9044 GUARD_OFF` → `sunny intervals are the aperture
  learner's business, never this one's`.
- M11 `thermal_model.py:1583 CMP_BOUND` → `#2223: the refit's dark gauge is the
  tree's, inclusive at the threshold`, `#2223: the dark gauge is inclusive at
  its own threshold, and unknown is dark`.
- M12 `thermal_model.py:1583 RETURN_DEL` → `9 of 4285`, among them every
  `#2223` sun arm above (`a sunlit window offers the refit no pair at all`,
  `a sunlit interval takes no house heat-loss sample`, `the lower-floor split
  takes a night interval and refuses a sunlit one`, …).

Failing test first, for this round's check: it pins behaviour the fix already
has, so its failing state is M09 above. For the fix itself: at the tests-only
commit `df4266c06`, `tests/features.py` dies before any check runs, with
`TypeError: AccuracySample.__init__() got an unexpected keyword argument
'solar_radiation'` at the new `_rs_rows` fixture.

## Null control

- **This round's check.** It moves the threshold onto
  `house_loss_confidence(114)`, a confidence the learner reaches, because no
  integer sample count lands on 0.9 itself. Its control arm is the same drive
  at 113 samples, which must stay unformed. That arm reads unformed at the head
  and under M09 alike (`one sample under False` in both). The threshold is
  restored in a `finally`, and the suite's other `#2223` gains checks (`and
  folds its hour once the level has converged`, `the hour shape waits for the
  heat-loss level`) pass at the head after it.
  - It encodes a design choice: the gate is inclusive (a level exactly on the
    threshold has converged), matching the `>=` the description states.
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

All figures are at base `b6a38f858` and head `285845eb9`, 2026-10-21. The
base's production tree equals the round-2 base `22615537a`'s
(`git diff --name-only 22615537a b6a38f858 -- custom_components` prints
nothing).
- `cmp` shows the finder's files byte-identical at both ends: `ident_rolling.py`
  and `enumerate.py`.
- The three harnesses this PR adds were run from the head's copies with the
  base worktree as the working directory; each puts `tests` and
  `custom_components` on its path relative to that directory, so it reads the
  base tree. The enumerator resolves its root from its own file, so the base
  run used the base's own copy.

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
  `P1.autumn.g0.40.ua_bias.dark1.00`, reads +0.5946 at both ends. So the head
  matches the commanded-power replay confound the harness documents, not a new
  bias.
- **Attribution:** the remaining spread (0.0219 on P1 against the study's
  dark-only 0.0001) is the 50 W/m² gauge's, by the fix review's perturbation,
  re-run this round:
  - with `HEAT_LOSS_MAX_SOLAR_W_M2` set to 1.0 in a detached worktree at the
    head (`const.py` only), `--plant P1 --scenario autumn` reads
    `fixed_arm_spread=0.0000`;
  - the base with `IDENT_DARK_W_M2=50` reads `ua_bias.dark0.50/1.00/2.00` =
    -0.0062 / +0.0011 / +0.0157, equal to the head's `fix0.50/1.00/2.00`.

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
It prints `gain50_kW=0.2450 dT_halfhour_K=0.0122` at both ends, and the null
control is under `## Null control`.

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

The scoped gate, from
`python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir D`:
- It prints `MODE: SCOPED -- 29 script(s) run, 4 scoped out.`
- `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=b6a38f858 PYTHONPATH=tests/hastub bash tests/run.sh`
  at this head ended rc=0 with `31 TEST SCRIPT(S) PASSED; 3 SCOPED OUT AND NOT RUN`.
- Among those 31: `ALL 4285 FEATURE CHECKS PASSED`,
  `ALL 106 FINITE BOUNDARY CHECKS PASSED`, `ALL 2375 ENTITY CHECKS PASSED`,
  `ALL 113 STRESS CHECKS PASSED`, `ALL 109 HARNESS HEADER CHECKS PASSED` and
  `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`.

Carry audit: `python3 -I tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body BODY.md`
prints `CARRY-AUDIT: 8 finding item(s): 8 routed, 0 unrouted, 0 bad destination(s)`.

Structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`
(`seam_cut_total 716 <= 716`). No budget is raised.

`env_drift.py --claims-only` ran as a `run_always` line of that gate. The
three-dot diff names no `VERSION`, manifest, `RELEASE_NOTES.md`, golden or
claim file.

## Architecture score

`python3 tools/audit/archscore/score.py --diff origin/main` prints
`Architecture score: dS +0.3110 IMPROVES`:
- `duplication_copies` 41 -> 40;
- `coord_footprint` 2494 -> 2493.

Both come from the two moved pure helpers. No metric rises; this round's
commit is tests-only.

## Alternatives

- **The RCA's two internal-gains shapes.** Both are measured under `## Figures`
  and both fail.
- **A clock-based night window.** The confound is the measured solar term, and
  a clock window folds an overcast noon and skips a bright evening.
- **A gate only on `dt_h`.** Not taken.
- **Moving the aperture fold above the max-residual guard.** That changes
  another learner's input.
- **A `survivor_triage` record for `coordinator.py:9041 CMP_BOUND`.** The site
  is equivalent under production inputs (`1 - 0.98**n` never equals 0.9 for an
  integer `n`), but the mutant is killable by moving the threshold onto a
  reachable confidence, so a value check was taken instead of a triage.

## Red checks

- **`mutation`.** At `9851d39de` it read `MUTATION TABLE REFUSED -- 4092
  unpinned site(s) against 4097 at the ratchet base 929275e8a, 1 of them added
  by this diff`. That site is `coordinator.py:9041 CMP_BOUND`. It is fixed at
  this head: the new check kills it (M09), and `mutation-autofix` records the
  pin after the push (`ci-autofix.md`).
  - Root cause: round 2 disposed of the site with a triage written in the body
    alone. `prepr.sh` step 7d accepts that, but the ratchet counts only a
    ledger `killed_by` pin or a `survivor_triage` record, and reads no body.
  - The cheaper detector exists and ran: `tools/pr/ci_predict.py` (prepr step
    6d) listed the site before the round-2 push, at a cost of seconds. It warns
    rather than refuses, by design, because the bot pins killed mutants. It
    cannot tell a body-only triage from a recorded one. The gap is under
    `## Friction`.
- **`pr-contract`.** At `9851d39de` CARRY-AUDIT read 6 items, 5 routed and 1
  unrouted: the alternatives harness's ΔT-part line under `## Figures`, which
  opened with a LEAD word. It is fixed in this body: the item is routed under
  `## Forward-carry`. The cheaper detector is
  `python3 -I tools/audit/carry_audit.py check --body FILE`, which takes
  seconds; this body passes it (`## Figures`).
- **`nightly-status`.** It grades `main`, not this branch: its red is main's
  nightly-lane status. This diff reaches no input the nightly lanes read.

## Unpinned sites

`prepr.sh` step 6d (`tools/pr/ci_predict.py --base origin/main`) lists one site
this diff adds, keyed at this head.
- `custom_components/heatpump_optimizer/coordinator.py:9041 CMP_BOUND` —
  killed by the value check `#2223: a heat-loss level exactly on the confidence
  threshold has converged` in `tests/features.py` (M09); pinned by
  `mutation-autofix` after the push.

The other eleven sites round 2 listed are pinned in
`tests/mutation_ledger/killed_by/` by the bot's commit `906c7a731`, and each is
re-killed at this head under `## Mutation proof`.

## Forward-carry

- **The D2 step-5 gains-arm precondition.** A probe of the internal-gains
  learner must run at a converged heat-loss level with a genuine gain, and the
  class barrier must drive the learners together.
  - Its control: `r10_night_folds_learners.py` `gains.converged.rel_dev` > 0.05
    with `gains.unconverged.rel_dev` 0.0000.
  - Carried to R10-BRIEFS-FOLD's `carry` list in
    `dev/programme/rosters/wave-r10-groups.json` on `handoff/audit-r10-roster`.
  - Verify with
    `git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json | grep -c "drive the learners together"`.

  Carry: R10-BRIEFS-FOLD
- **The delivery-shortfall arms move** (Figures). They are the commanded-power
  replay confound, measured by the study's own dark arm at both ends.
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
- **The alternatives harness's ΔT-part line** (Figures) records a rejected
  design measured to fail, not an open defect.
  Carry: dismissed: rejected alternative measured in figures (item 1492c8f9)

## Friction

- fixer.md#2: unclear: step 2 lists "a written triage" among an unpinned
  site's dispositions without saying where it is written. Round 2 wrote it in
  the body, `prepr.sh` step 7d accepted it, and CI's `mutation` ratchet, which
  counts only `tests/mutation_ledger/` pins and `survivor_triage` records, went
  red on it at `9851d39de`. Carry: R10-POLICY-FIXER-MD
