The heat-loss learners absorb solar-aperture error. The replay nets the modelled
solar term out only to the accuracy of the aperture, and solar gain correlates
with the conductive term through the time of day and the outdoor temperature.
So a mis-set aperture leaves a residual that the Newton step settles into the
heat-loss coefficient, at a value that looks converged (D2-s3-71). Closes #2223,
the class `N-confounded-learner`.

**What changed.** Three residual-fed folds and the drift refit share one dark
gauge, `HEAT_LOSS_MAX_SOLAR_W_M2`. It is the threshold `_fold_internal_gains`
already used, as the RCA instructed.

- `_async_learn_house_heat_loss` and `_async_learn_lower_floor_loss` return
  before their Newton steps on a sunlit interval.
  - The house fold's gate sits after the open-window CUSUM feed and after
    `_fold_solar_aperture`. So the detector still sees the day (#2241's carry),
    and the aperture learner keeps the daylight.
- `accuracy.heat_loss_refit` records the interval's irradiance on
  `AccuracySample` and refuses a sunlit pair.
  - The field is declared in `store.DOMAINS`, so `finite_boundary` drives it.
  - A sample with no recorded sun reads as dark, which is the tree's rule for
    an unknown irradiance.
- `_fold_internal_gains` folds only once the heat-loss walk has converged:
  `house_loss_confidence` >= `INTERNAL_GAINS_MIN_UA_CONFIDENCE`.
  - One residual feeds both learners, so an unidentified level would otherwise
    be learned as an hour shape.
  - The RCA's two other shapes are measured under `## Figures`.

The folds spelled out the zone-temperature and zone-capacity choices
separately; each now answers from one pure helper. The house fold's two dt
guards are one range check. Together these pay the coordinator's zero headroom.

This body is re-cut at round 4 (`fixer.md`, "Past three rounds"). Every figure
below was re-taken at the head named under `## Head`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_011pFbVfDES2cn6uah2a5dGa

## Head

`9f0ed12e70c072d7b5b21b53a9345e25b70fd01d`.

It is the PR head `baa01ed85` with three merges and no rebase:
- `origin/main` at `f2fb1b0e9`;
- the bot's pin commit `ac4d62106`;
- `origin/main` at `57f0c9c77`, which is the merge base.

The last merge brought production changes in `coordinator.py` and
`freq_control.py`. So every figure below was taken after it, against base
`57f0c9c77`.

`git merge-tree --write-tree origin/main HEAD` exits 0. Measured on
2026-10-21 (UTC) with `origin/main` at `57f0c9c77`. The base worktree is
detached at `57f0c9c77`. Python is `/opt/hpo/venv-ci`.

## Mutation proof

This round's site is `coordinator.py:9041 CMP_BOUND`. The mutant changes
`or settled < INTERNAL_GAINS_MIN_UA_CONFIDENCE` to `<=`. It was applied in
place at this head's tree, on line 9041, and the run was
`PYTHONPATH=tests/hastub python3 tests/features.py`:
- one check failed, `#2223: a heat-loss level exactly on the confidence
  threshold has converged`;
- the check's detail read `on the threshold False, one sample under False`;
- the run printed `1 of 4289 FEATURE CHECKS FAILED` (rc=1).

`coordinator.py` was then restored, and `git status --short` printed nothing.

`mutation-autofix` drove the same mutant and recorded the pin in commit
`ac4d62106`, file
`tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_internal_gains.CMP_BOUND.c7930f6b.json`.
That file's `reason` line is the instrument's own count.

## Null control

- **The unmutated tree.** The same `tests/features.py` run printed
  `ALL 4289 FEATURE CHECKS PASSED` (rc=0), and the `#2223` threshold check read
  `ok`.
- **That check's own control arm.** It is the same drive at 113 samples, one
  under the moved threshold. It reads unformed both at the head and under the
  mutant (`one sample under False` in both runs).
  - The check encodes a design choice: the gate is inclusive. A level exactly
    on the threshold has converged.
- **The flat-irradiance arm.** The aperture multiplies zero irradiance there,
  so `fixed_arm_spread` reads 0.0000 on P1..P5 (`.flat.g1.00`) at both ends.
- **The companion's dark arms read the same at both ends:**
  `house.dark.samples=8`, `lower.dark.samples=1`, `refit.dark.pairs=192`.
- **The companion's positive gains arm** reads `gains.converged.rel_dev=1.9800`
  at both ends. So the fix stops the confounded arm without stilling a learner
  it should leave alone.
- **The aperture learner.** P1 autumn `solar_scale.learn` reads 1.359 at both
  ends.
- **The no-window vent arms.** The 4 arms ending `.g1.0.ua1.0.vent0x0h` read
  `false_share=0.000` at both ends.

## Figures

Every figure below is at base `57f0c9c77` and head `9f0ed12e7`, taken
on 2026-10-21.
- Each harness ran from the head's copy. For the base run, the base worktree
  was the working directory. Each harness puts `tests` and `custom_components`
  on its path relative to the working directory, so it read the base tree.
- The enumerator resolves its root from its own file, so the base run used the
  base's own copy.
- `OUT` below stands for that end's output directory.

**Finder's harness:** `dev/audit/rounds/round10/study-ident/ident_rolling.py`.
- **Run:** `bash dev/audit/rounds/round10/study-ident/run_q1.sh OUT/q1`.
  - At each end, `grep -c ^rc=0 OUT/q1/rc.log` prints 20.
- **Metric:** `fixed_arm_spread`, from `grep -h fixed_arm_spread OUT/q1/*.out`.
  - It is the report's spread of learned UA across the six fixed-aperture arms
    {0.5, 0.75, 1.0, 1.25, 1.5, 2.0} x truth.
- **Autumn, delivery 1.0:**
  - P0 0.2691 -> 0.0147;
  - P1 0.3790 -> 0.0219;
  - P2 0.1405 -> 0.0074;
  - P3 0.3383 -> 0.0205;
  - P4 0.2383 -> 0.0101;
  - P5 0.2894 -> 0.0168.
- **Delivery 0.6 and 0.4:**
  - P1 at 0.6: 0.3925 -> 0.0218; at 0.4: 0.3962 -> 0.0224;
  - P0 at 0.6: 0.2757 -> 0.0150; at 0.4: 0.2677 -> 0.0154.
- **`indep`** (sun independent of dT by construction):
  - P1 0.3918 -> 0.0230;
  - P2 0.1432 -> 0.0078;
  - P3 0.3432 -> 0.0218;
  - P4 0.2474 -> 0.0116;
  - P5 0.2902 -> 0.0178.
- **P1 autumn `ua_bias`**, from `grep -h P1.autumn.g1.00.ua_bias OUT/q1/*.out`:
  - `fix2.00` +0.2474 -> +0.0157;
  - `learn` -0.0262 -> -0.0001;
  - `learn+gains` -0.0332 -> -0.0111;
  - `none` -0.0900 -> -0.0038.
- **The delivery-shortfall arm moves the other way.**
  - P1 g0.40 `fix1.00` reads +0.4423 -> +0.5833.
  - The study's own dark arm, `P1.autumn.g0.40.ua_bias.dark1.00`, reads
    +0.5946 at both ends.
  - So the head matches the commanded-power replay confound the harness
    documents. It is not a new bias.

**Companion:** `dev/audit/harnesses/r10_night_folds_learners.py`, run as
`PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_night_folds_learners.py`
(rc=0 at both ends). It drives the production symbols, because the sweep's
probes re-implement the learners.

| line | base | head |
|---|---|---|
| `house.sunlit.samples` | 8 | 0 |
| `lower.sunlit.samples` | 1 | 0 |
| `refit.sunlit.pairs` | 192 | 0 |
| `gains.unconverged.rel_dev` | 0.0990 | 0.0000 |
| `gains.converged.rel_dev` | 1.9800 | 1.9800 |

**The sweep's enumerator:**
`dev/audit/rounds/round10/D14/sweep-N-confounded-learner/enumerate.py`, sha1
`9f7e163704501c8e59393b3c93190afb539caa4d`, run with `PYTHONPATH=tests/hastub`.
- **Its SEAM list:** `grep -c ^SEAM OUT/enum.out` prints 13 at each end.
  - `diff <(grep ^SEAM base/enum.out) <(grep ^SEAM head/enum.out)` exits 0.
- **Controls:** its three `CONTROL` lines and `PROBE-NULL` read PASS at both
  ends.
- **Probes at the base:**
  - house FAIL `ua_scale=0.925`;
  - lower FAIL `lower_ratio=0.925 gated=False`;
  - refit FAIL `refit_scale=0.937`;
  - internal-gains FAIL `gains_max_rel_dev=0.820`.
- **Probes at the head:**
  - House FAIL `0.925` and refit FAIL `0.937` are unchanged. Neither probe reads
    the path this diff moves: `_ua_walk` is a re-implementation, and
    `probe_refit` builds samples with no `solar_radiation`.
  - Lower reads PASS `lower_ratio=1.000 gated=True`.
  - `probe_internal_gains` raises `TypeError: 'NoneType' object is not
    iterable` (rc=1). It calls the fold directly at an unconverged level, and
    this diff's convergence gate leaves the profile unformed there. The
    companion's `gains.unconverged` arm measures that property through the
    production path instead.

Every seam the enumerator returns, against its disposition at this head:
- **Closed in this diff (the four instances):**
  - `_async_learn_house_heat_loss`;
  - `_async_learn_lower_floor_loss`;
  - `heat_loss_refit`;
  - `_fold_internal_gains`.

  The companion above measures them.
- **Already guarded:** `_fold_solar_aperture`. It runs a demeaned covariance on
  modelled Q_solar, on sunny intervals only, and this diff leaves its input
  path untouched.
- **Already guarded:** `sysid.identify` and `sysid.identify_slab`, which run the
  night-gated experiment with its intercept column.
- **Not applicable, unchanged and unread by this diff:**
  - `sysid._lm_solve`, a solver helper;
  - `sysid._slab_ua_profile_halfwidth`, an uncertainty width;
  - `diagnosis.attribute`, a one-shot diagnostic;
  - `drift.update`, a CUSUM statistic;
  - `flow_lift.observe`, the curve-bias term, whose job is to absorb curve
    error;
  - `price_model.observe_day`, descriptive price statistics.

**The RCA's two alternative internal-gains shapes:** measured by
`dev/audit/harnesses/r10_night_folds_alternatives.py`, run as
`PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_night_folds_alternatives.py`.
- `cmp base/alt.out head/alt.out` exits 0.
- Its `net_of_ua_part` lines read 0.0000 on both arms.
- Its `ridge*` lines read as follows:
  - the shipped ridge 0.02: 1.0000 / 0.7143;
  - ridge 1.00: 0.0500 / 0.0476.

**Carry controls.**
- `dev/audit/harnesses/r10_vent_bias_window.py` (#2241), run as
  `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_vent_bias_window.py`
  (rc=0 at both ends).
  - **No-window arms.** `grep -c 'g1.0.ua1.0.vent0x0h false_share=0.000' OUT/vent.out`
    prints 4 at each end, of 4 such arms.
  - **300 W/K windows.** `grep vent300x OUT/vent.out | grep -c detect_h=nan`
    prints 0 at each end, of 60 arms (`grep -c vent300x`). So every 300 W/K
    window is detected at both ends.
  - **150 W/K x 4 h windows.** `grep vent150x4h OUT/vent.out | grep -c detect_h=nan`
    prints 6 at the base and 7 at the head, of 20 arms.
  - **What `nan` means.** The harness header defines `detect_h` as "nan: never
    inside the window". It is a missed detection, not a numeric fault.
  - **The one arm that changes.** It is `seed1.onoff.g1.0.ua1.0.vent150x4h`,
    from `grep seed1.onoff.g1.0.ua1.0.vent150x4h OUT/vent.out`: `detect_h=3.75`
    at the base and `detect_h=nan` at the head.
    - At the base, the trip landed in the 4 h window's last quarter-hour. At the
      head it does not land inside the window.
    - The same window at g1.0 ua1.0 already reads `detect_h=nan` at the base on
      both `pi` arms, so this window size sits at the detector's margin.
    - The detector is untouched. The learned UA it compares against moves with
      the learners.
- `dev/audit/harnesses/r10_vent_sun_transient.py` (#2391), run as
  `PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/r10_vent_sun_transient.py`.
  - `cmp base/sun.out head/sun.out` exits 0.
  - Check schedule: bias 0.4 K `[0, 0, 0, 0]`, bias 1.0 K `[0, 20, 0, 0]`.
  - Census schedule: bias 0.4 K `[0, 27, 0, 0]`, bias 1.0 K `[0, 39, 38, 30]`.
  - `grep -c end_tripped=False OUT/sun.out` prints 6 at each end, of 6 lines.
  - So the features check stays at 0.4 K.

**The scoped gate.**
`python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir D`
prints `MODE: SCOPED -- 29 script(s) run, 4 scoped out.`
- `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=57f0c9c77 PYTHONPATH=tests/hastub bash tests/run.sh`
  at this head ended rc=0 with `31 TEST SCRIPT(S) PASSED; 3 SCOPED OUT AND NOT RUN`.
- Among those 31: `ALL 4289 FEATURE CHECKS PASSED`,
  `ALL 106 FINITE BOUNDARY CHECKS PASSED`, `ALL 2382 ENTITY CHECKS PASSED`,
  `ALL 113 STRESS CHECKS PASSED`, `ALL 109 HARNESS HEADER CHECKS PASSED` and
  `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`.

**Structure.** `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`,
with `seam_cut_total 716 <= 716`. No budget is raised.

**Version and claim files.** `env_drift.py --claims-only` ran as a `run_always`
line of that gate. The three-dot diff names no `VERSION`, manifest,
`RELEASE_NOTES.md`, golden or claim file.

**Carry audit.**
`python3 -I tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body BODY.md`
prints `CARRY-AUDIT: 7 finding item(s): 7 routed, 0 unrouted, 0 bad destination(s)`.

## Architecture score

`python3 tools/audit/archscore/score.py --diff origin/main` prints
`Architecture score: dS +0.3110 IMPROVES`:
- `duplication_copies` 41 -> 40;
- `coord_footprint` 2494 -> 2493.

Both come from the two moved pure helpers. No metric rises.

## Alternatives

- **The RCA's two internal-gains shapes.** Both are measured under `## Figures`.
  Both fail.
- **A clock-based night window.** The confound is the measured solar term. A
  clock window would fold an overcast noon and skip a bright evening.
- **A gate only on `dt_h`.** It would not separate a sunlit interval from a dark
  one.
- **Moving the aperture fold above the max-residual guard.** That changes
  another learner's input.
- **A `survivor_triage` record for `coordinator.py:9041 CMP_BOUND`.** The mutant
  can be killed by moving the threshold onto a confidence the learner reaches.
  So a value check was taken instead of a triage.

## Red checks

- **`mutation`.** At `baa01ed85` it read `MUTATION TABLE REFUSED`, with one
  site added by this diff: `coordinator.py:9041 CMP_BOUND`.
  - The killing check landed at `285845eb9`. A ledger pin is written only by
    `mutation-autofix` after a push, so `mutation` reads red at that push until
    the bot commits. The bot drove the site and pushed
    `ac4d62106 ci: pin killed mutants`, which this head merges.
  - The cheaper detector: `tools/pr/ci_predict.py` (`prepr.sh` step 6d) lists
    the site before a push, in seconds. It warns rather than refuses, by design,
    because the bot pins killed mutants (`ci-autofix.md`).
- **`pr-contract`.** At `baa01ed85` CARRY-AUDIT refused one unrouted item: the
  alternatives harness's ΔT-part line under `## Figures`.
  - The PR still carried the round-2 body. The round-3 body, which routed that
    item, never reached the PR.
  - This body routes it under `## Forward-carry`.
  - The cheaper detector is
    `python3 -I tools/audit/carry_audit.py check --body FILE`, which takes
    seconds; this body's result is under `## Figures`.
- **`nightly-status`.** It grades `main`'s nightly run 39563978649
  (`mutation-nightly` and `slow` red there), not this branch. That red is main's
  and is owned by main's nightly lanes. This diff reaches no input those lanes
  read.

## Unpinned sites

`prepr.sh` step 6d (`tools/pr/ci_predict.py --base origin/main`) lists the site
this diff adds: `custom_components/heatpump_optimizer/coordinator.py:9041
CMP_BOUND`.
- It is killed by the value check `#2223: a heat-loss level exactly on the
  confidence threshold has converged` in `tests/features.py`.
- It is pinned by `mutation-autofix` in `ac4d62106`.

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
  a round-10 measurement record, not a gate, and this fix removes its premise.
  Carry: dismissed: record harness, premise removed by the fix
- **The alternatives harness's ΔT-part line** (Figures) records a rejected
  design that was measured to fail. It is not an open defect.
  Carry: dismissed: rejected alternative measured in figures (item 1492c8f9)

## Friction

- fixer.md#2: unclear: step 2 lists "a written triage" among an unpinned
  site's dispositions without saying where it is written. Round 2 wrote one in
  the body, and `prepr.sh` step 7d accepted it. CI's `mutation` ratchet counts
  only `tests/mutation_ledger/` pins and `survivor_triage` records, and it went
  red on that site. Carry: R10-POLICY-FIXER-MD
