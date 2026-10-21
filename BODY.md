Part of #2238 (D7-s2-01, round 10 D7/s2). The finding: `_observe_frequency` folded every defrost interval into the
kW-per-Hz map while every other learner refused the same interval. Defrost was decided by two divergent predicates:
`_freq_fold_blocked`, the map's fold gate, refused cooling, distorted draw and pinned-input reasons and never a defrost,
so the map learned 8 folds over 8 defrost intervals; and `FrequencyWatchdog`'s own contract calls a pump pausing for a
defrost "an operating point at rest", while the caller computed `active` without asking.

The fix gives the fact one owner. `freq_control.defrost_interval` is the predicate, in the module the map and the
watchdog live in. The map's fold gate `_freq_fold_blocked` refuses a defrost through it, and the watchdog's `active`
asks the same function. A defrost interval is now neither evidence for kW-per-Hz nor evidence about the write path.

What pays for it, all inside the seam (`_observe_frequency` and `_freq_fold_blocked`, whose only caller it is):

- `_freq_fold_blocked` asks `_cop_fold_blocked` itself instead of repeating its distorted-draw clause. Its own
  docstring already claimed it asked "the same question" as the COP gate; now it does, by calling it. The COP gate
  also owns immersion, so the caller's separate `self._immersion_active` term goes. The truth table is unchanged:
  immersion, distorted draw, cooling or a pinned power reading, plus the new defrost term.
- The watchdog's mode guard was a second copy of `_freq_mode`'s predicate. `source == FREQ_SOURCE_NUMBER and
  configured == FREQ_MODE_CONTROL and not self._freq_fallback` is exactly `_freq_mode() == FREQ_MODE_CONTROL`, because
  `resolve_reading` returns the number source exactly when the number entity is set. The `configured` local goes with it.

The structure ratchet reads the merge base's numbers at this head, so nothing is re-recorded (Figures). The previous
round's `_freq_view` hunk is gone: it sat outside this group's owning seam, and its only line saving was re-wrapping
two ternaries onto one line each, which the fix review measured as `metric-gamed`. `_freq_view` is byte-identical to
the merge base.

Scope note: D7-s2-01's report also names `pump_offline` as a contaminant of the same map. This group's brief scopes
the pull request to defrost, so the offline arm is measured (Figures) and carried, not closed here.

## Head

`25a94521b58dc2423d11258bfc3f08c337640a8a`: the PR head `d0cdac2ef`, a merge of `origin/main` `289426c1fdde`, and `5e8ab1c45`, which
answers the round-2 block (`metric-gamed`, `probe/rev-2527-98e8d4b4`). Every figure below is taken at this head, or at
the merge base `289426c1fdde` where a line says so. Taken 2026-10-21 (`date -u`). `25a94521b` makes the
`defrost_standoff` rule's matcher skip a flag read passed straight to its owner (Figures).

## Mutation proof

Each mutant was applied in its own scratch worktree at `5e8ab1c45`, then `PYTHONPATH=tests/hastub python3
tests/features.py` was run and the worktree restored.

- **m1: both fix terms deleted.** `or defrost_interval(coord._pump_signals.defrosting)` comes out of
  `_freq_fold_blocked`, and the watchdog's `and not defrost_interval(self._pump_signals.defrosting)` line is deleted:

```
  FAIL a defrost interval never teaches the frequency map  [the fold would learn a ratio that is not a kW-per-Hz point, and the decile-keyed map is inherited when the user later switches to control]
  FAIL defrost ticks never stand control down  [a defrost is not a write path that stopped listening]
2 of 4271 FEATURE CHECKS FAILED
```

  The null-control check `null control: a non-defrost interval still folds` stays green under m1.
- **m2: the fold gate's first guard off.** `_freq_fold_blocked`'s `if _cop_fold_blocked(coord) or
  defrost_interval(...)` is replaced by `if False:`. Result: `4 of 4271 FEATURE CHECKS FAILED`: `immersion intervals never teach the map`, `a defrost interval never teaches the frequency map`, `resistive heat never teaches the kW-per-Hz map` and `night mode never teaches the kW-per-Hz map`. So the immersion term the caller dropped is now pinned through the gate.
- **m3: the caller's fold guard off.** `_observe_frequency`'s `if self._measured_power is None or
  _freq_fold_blocked(self):` is replaced by `if False:`. Result: six `FAIL` lines, then `TypeError: float() argument must be a string or a real number, not 'NoneType'` and `EXIT=1` before the summary prints. The six are the immersion, cooling, pinned-power, defrost, resistive-heat and night-mode checks.

## Null control

- **The finding.** The finder's harness on the unmodified merge base reads `freq_map_clean_folds=8` and
  `freq_map_defrost_folds=8`. At this head the clean arm still reads 8 and the defrost arm reads 0, so the change
  separates the two arms only on the defrost arm.
- **The harness's own learner table.** The `freq_map` column of the `defrost` row reads INGEST at the base and frozen at
  this head (`defrost.learners_ingesting` 2 -> 1). The column asks `_freq_fold_blocked` alone, which now owns the
  refusal. The other rows are unchanged; in particular `clean` stays at 8 ingesting, and `pump_offline` still ingests
  into the map.
- **The structure metric.** The fix review's plant (`ev/plant.diff` on `probe/rev-2527-98e8d4b4`) re-wraps one
  unrelated ternary in `_fetch_tibber_prices` and nothing else. Applied at this head, it moves the ratchet to
  `class_excess_loc=18295`, `max_class_loc=8537`. So the instrument does see a re-wrap. This head, unplanted, reads the
  merge base's `18299` and `8541` exactly, so no re-wrap gain is hidden in it, and none is recorded.

## Figures

- **Finder's harness:** `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/s2/learner_gates.py`. Its
  `shasum` is `5b77f8743adbc990a2277046e9cdbb83c4d3a537` at both ends.
  - Merge base `289426c1fdde`: `freq_map_clean_folds=8`, `freq_map_defrost_folds=8`, `defrost.learners_ingesting=2`,
    `pump_offline.learners_ingesting=1`, `cop_gate_on_defrost='defrosting'`.
  - Head: `freq_map_clean_folds=8`, `freq_map_defrost_folds=0`, `defrost.learners_ingesting=1`,
    `pump_offline.learners_ingesting=1`, `cop_gate_on_defrost='defrosting'`. The head's remaining defrost ingester is
    `defrost_derate`, which learns from defrosts by design.
  - `--perturb` at the head reads `freq_map_defrost_folds=0`. Its patch adds a defrost refusal that
    `_freq_fold_blocked` now already makes, so that arm is vacuous at the head and is named only for completeness.
- **Structure:** `python3 tests/structure.py`, with `tests/structure_budgets.json` byte-identical to main's.
  - Merge base `289426c1fdde`: `class_excess_loc=18299`, `max_class_loc=8541`, `seam_cut_total=718`,
    `STRUCTURE RATCHET PASSED`.
  - This head: the same three numbers, `STRUCTURE RATCHET PASSED`, no improvement line.
  - With the review's plant applied at the head: `class_excess_loc=18295`, `max_class_loc=8537`,
    `2 STRUCTURE BUDGET(S) IMPROVED AND NOT YET RECORDED`. Not committed; `git status --short` was empty after.
- **Architecture score:** `Architecture score: dS +0.0000 NULL`, from `python3 tools/audit/archscore/score.py --diff
  origin/main`.
- **Scope:** `MODE: SCOPED -- 27 script(s) run, 6 scoped out.`, from `python3 tests/closure.py select --diff $(git
  merge-base origin/main HEAD) --workdir "$D"`. Keyed on the mode line, not the count.
  - Run locally from `scope.run`: `tests/features.py`, `tests/entities.py` and `tests/structure.py`.
  - The heavy scripts are left to CI.
- **Features:** `ALL 4271 FEATURE CHECKS PASSED`, from `PYTHONPATH=tests/hastub python3 tests/features.py` at `5e8ab1c45`. `git diff --stat 5e8ab1c45 HEAD` names only `tests/entities.py`, so this figure, and the three mutants above (also applied at `5e8ab1c45`), describe this head's production code and checks.
- **Entities:** `ALL 2376 ENTITY CHECKS PASSED`, from `PYTHONPATH=tests/hastub python3 tests/entities.py` at this head. The P2
  registry row `defrost_standoff` passes in it.
  - The row pins a decision-context read of `*.defrosting`: direct, `bool(...)`, `not` and walrus.
  - It does not match a copy to a local first (`d = signals.defrosting; if d:`), so it pins the flag's read, not a
    local derived from it.
  - Both reads this diff adds go through `defrost_interval`. At `5e8ab1c45` the row failed on them (`SEAM
    ['coordinator.py:1012 in _freq_fold_blocked', 'coordinator.py:10565 in
    HeatPumpOptimizerCoordinator._observe_frequency']`), because the matcher's docstring exempted a read handed to
    the owner but its code did not. The earlier head had assigned the answer to a local first, which hid the gap.
    `25a94521b` makes the code match the docstring: a `.defrosting` passed positionally to `defrost_interval`, bare
    or module-qualified, is not a hit.
  - A scratch probe drives the matcher over 9 planted snippets and the real coordinator, run under `python3 -I`
    (`~/hpo-seats/r10s4/r10-freq-defrost/scratch/r3/probe/matcher_probe.py`, from the worktree root). It prints
    `RESULT probe_failures=0` and `coordinator.py hits: 1`, the dispositioned `_learning_frozen`.
  - The same probe against `5e8ab1c45`'s matcher prints `RESULT probe_failures=4` and `coordinator.py hits: 3`.
    That is the null control: the planted direct `if`, `not`, `bool()` and bool-op reads still hit with both
    matchers.
  - The one other read the rule returns is dispositioned at `_learning_frozen`, the plant-wide gate that owns the reason
    string every learner is frozen with (#781).
- **CI predict:** `python3 tools/pr/ci_predict.py --base origin/main` at this head prints `CI PREDICT: no closures or
  fast red predicted against 289426c1fdde` and `2 unpinned site(s) the diff adds` (Unpinned sites).
- **CI's `mutation` at the previous head `d0cdac2ef`** (job 119197763145): `MUTATION TABLE PASSED`,
  `0 survivor(s) of 4 evaluated = 0.0%, cap 20.0%`. That head's production lines differ from this one, so the figure is
  history; this head's mutation verdict is CI's run at this head.

## Architecture score

`dS +0.0000 NULL`: `python3 tools/audit/archscore/score.py --diff origin/main` at this head.

## Unpinned sites

`tools/pr/ci_predict.py --base origin/main` names two sites the diff adds. Each was applied by hand at this head, and
each is killed by `tests/features.py` (Mutation proof). `mutation-autofix` pins them on CI's run.

- `custom_components/heatpump_optimizer/coordinator.py:1012 GUARD_OFF` (`_freq_fold_blocked`'s first guard): m2, `4 of 4271 FEATURE CHECKS FAILED`.
- `custom_components/heatpump_optimizer/coordinator.py:10595 GUARD_OFF` (`_observe_frequency`'s fold guard): m3, six checks failed, then `EXIT=1`.

The four ledger pins on lines this edit replaced or restored were deleted by hand, because `mutation-autofix` never
drops a pin:

- `_freq_view` `GUARD_OFF fa39efbe~2`;
- `_observe_frequency` `CMP_BOUND e2a6e890` and base `BOOLOP b0c65a3c`;
- `_freq_fold_blocked` `GUARD_OFF 26183fd7`.

`ci_predict` then reports no stale pin. The bound check `the watchdog's two bounds: the floor is exclusive, the minimum
inclusive` stays in `tests/features.py` and still feeds both `CMP_BOUND` inputs of `watch_active`.

## Red checks

Every check that concluded `failure` on this pull request's heads, read per commit from the `check-runs` API.
`cancelled` runs were superseded by a newer push and are not reds.

- `nightly-status`, red at every head including `d0cdac2ef`: it grades `main`, not this branch. The cause is the
  nightly `slow` lane's `loop_cpu_ratio` over budget, fixed by the separate `r10-replay-cap` work, and this diff
  touches nothing it reads. Cheaper detector: none owed here.
- `fast (3.14)` (required), red at `3ce0b78f8`: `tests/structure.py` printed `3 STRUCTURE BUDGET(S) IMPROVED AND NOT
  YET RECORDED`. The round-2 record that answered it was voided as `metric-gamed`. At this head the ratchet reads the
  merge base's numbers with main's table and passes, with nothing recorded. Cheaper detector: `python3
  tests/structure.py`, which takes seconds and runs before every push.
- `pr-contract`, red at `3ce0b78f8`: the body did not name `fast (3.14)`. This section names it. Cheaper detector:
  `tools/pr/prepr.sh` on the body, which runs the same check and ran before this handoff.
- `mutation` (required), red at `4f2ac0cac`, `de28f656b`, `f157063b2` and `f8c523f09`: `2 of them added by this diff`
  were unpinned (the two `CMP_BOUND` variants), with the survivor rate over its cap. This branch added their killer,
  the bound check, rather than a triage. CI's `mutation` is green at `3ce0b78f8` and at `d0cdac2ef`. Cheaper detector:
  `tools/pr/ci_predict.py --base origin/main`, source-only and seconds, which prepr step 6d runs.

## Forward-carry

- The `pump_offline` arm of D7-s2-01. `_freq_fold_blocked` does not refuse a freeze reason of `pump_offline`, so an
  install whose online flag reads False while its frequency entity still reports a number folds that interval.
  - Same seam and same class as this fix, but outside this group's stated scope (defrost).
  - Measured at both ends by the harness's `pump_offline` row (`freq_map` = INGEST).
  - The fix review records it as a precondition in `R10-ARCH-SHAPES`'s carry on `handoff/audit-r10-roster`.
  - A later group's carry lands in `dev/programme/rosters/wave-r10-groups.json`, and `#2238` stays the open record on
    the Delivery-status table until a group owns it. Carry: #2238

## Friction

`none`
