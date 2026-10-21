Part of #2238 (D7-s2-01, round 10 D7/s2). The finding: `_observe_frequency` folded every defrost interval into the
kW-per-Hz map while every other learner refused the same interval. Defrost was decided by two divergent predicates:
`_freq_fold_blocked` refuses cooling, distorted draw and pinned-input reasons and never `defrosting`, so the map learned
8 folds over 8 defrost intervals; and `FrequencyWatchdog`'s own contract calls a pump pausing for a defrost "an operating
point at rest", while the caller computed `active` without asking.

The fix gives the fact one owner. `freq_control.defrost_interval` is the predicate, in the module the map and the
watchdog live in, and `_observe_frequency` consults it for both readings: the map's fold and the watchdog's `active`.
A defrost interval is now neither evidence for kW-per-Hz nor evidence about the write path.

Scope note, stated plainly: D7-s2-01's report also names `pump_offline` as a contaminant of the same map. This group's
brief scopes the pull request to defrost, so the offline arm is measured (Figures) and carried, not closed here. It is
the same seam, not a new one.

Two in-seam cleanups pay the coordinator class span. The watchdog's mode guard was a second copy of `_freq_mode`'s
predicate: `source == FREQ_SOURCE_NUMBER and configured == FREQ_MODE_CONTROL and not self._freq_fallback` is exactly
`_freq_mode() == FREQ_MODE_CONTROL`. And `_freq_view` asked "is this install configured" in two spellings
(`mode != "unconfigured"` and `source is not None`, the same fact) while wrapping both ternary values across four lines;
one spelling now answers, and the view no longer re-derives it.

## Head

`fe9038fbe2`, on top of the PR head `f8c523f0` — my `0be6047ca`, the orchestrator's delivery row, a merge of `main`, and
the bot's `ci: pin killed mutants` — branched from `origin/main` `4e5801eb5064`. Every figure below is taken at this head
unless a line names another one; the production figures were measured at `2f8071ef5`, and the production lines are
identical here (the later commits delete a stale ledger pin, record the structure budgets, and add the one features check
the bound sites needed). The PR head `de28f656` named earlier in this body's history is a prior head and no figure is
taken there.

Prepr's closures recordings were skipped (`PREPR_SKIP_CLOSURES=1`) under the coordinator's owner ruling for the rest of
this wave: CI's required `closures` context re-records them and `closures-autofix` repairs an UNDER-SCOPED result, while
the local re-record was the wave's bottleneck. Every other prepr step ran and passed.

## Mutation proof

The mutant deletes the two production terms the fix adds — `not defrosting` from `watch_active` and `or defrosting` from
the map's fold guard — in the working tree, then runs the closure's `tests/features.py` and restores. Measured at
`2f8071ef5`, when the suite held 4261 checks (the bound check below was added later and none of these arms reaches it).
The run ends `EXIT=1`:

```
  FAIL a defrost interval never teaches the frequency map  [the fold would learn a ratio that is not a kW-per-Hz point, and the decile-keyed map is inherited when the user later switches to control]
  FAIL defrost ticks never stand control down  [a defrost is not a write path that stopped listening]

2 of 4261 FEATURE CHECKS FAILED
```

The third added check is the null control and stays green under the mutant: `null control: a non-defrost interval still
folds`. `git status --short` after the restore prints nothing, so the measured tree is the committed head.

### The two bound variants

The mutation job's two added sites are the two variants of `_observe_frequency`'s `CMP_BOUND`, and both survived every
driver (Red checks). One check in `tests/features.py` now feeds each bound its exact input; applied alone in the working
tree and restored, each variant takes the suite from `ALL 4262 FEATURE CHECKS PASSED` to `1 of 4262 FEATURE CHECKS
FAILED`:

| Variant | Edit | Goes red |
|---|---|---|
| `CMP_BOUND` a | `self._commanded_power() > 0.05` -> `>= 0.05` | `the watchdog's two bounds: the floor is exclusive, the minimum inclusive` (`floor -> [True], minimum -> [True]`) |
| `CMP_BOUND` b | `reported >= hz_min` -> `>` | the same check (`floor -> [False], minimum -> [False]`) |

Each failure is that check on the arm the variant flipped; the other arm reads its expected value in both runs. The
ledger row `tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._observe_frequency.CMP_BOUND.e2a6e890.json`
records both.

## Null control

The unmodified tree, the finder's harness, the same 8 intervals (baseline `git archive` of `origin/main`
`4e5801eb5064`): `freq_map_clean_folds=8`, `freq_map_defrost_folds=8`. At the head the clean arm still reads 8 and the
defrost arm reads 0. `tests/features.py` carries the same arms as checks: a `defrosting=False` interval folds, and
without the fix the divergent defrost arm trips the watchdog.

The harness's `--perturb` arm (patch `_freq_fold_blocked` to refuse defrost) is vacuous at the head: the fold reads the
predicate before the gate, so it reads 8 -> 0 -> 0. It is named because the harness's own reported text did not move.
The finding is still measurable at the head: deleting `or defrosting` alone takes the defrost arm from 0 folds to 8 (the
reviewer's single-term plant; my mutation proof deletes both terms and reads the same 8), and the unmutated control that
separates is the clean arm against the defrost arm. The harness's learner table's `freq_map` column still reads INGEST on
the defrost row for the same reason as `--perturb`: the column asks `_freq_fold_blocked` alone, which this diff
deliberately leaves unchanged.

## Figures

- Baseline `freq_map_clean_folds=8`, `freq_map_defrost_folds=8`, `cop_gate_on_defrost='defrosting'`:
  `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/s2/learner_gates.py`, run from the `git archive` export;
  `sha1sum dev/audit/rounds/round10/D7/s2/learner_gates.py` = `5b77f8743adbc990a2277046e9cdbb83c4d3a537` at both ends.
- Head `freq_map_clean_folds=8`, `freq_map_defrost_folds=0`, `pump_offline.learners_ingesting=1` with `freq_map` =
  INGEST: the same command at the head.
- `class_excess_loc=18299` (budget 18301), `max_class_loc=8541` (8543), `seam_cut_total=718` (719),
  `functions_cc_over_15=31` (31), `max_method_loc=373` (373): `python3 tests/structure.py`; the three improved rows were
  re-recorded by `python3 tests/structure.py --record`, and the ratchet then reads `STRUCTURE RATCHET PASSED`.
- `Architecture score: dS +0.0000 NULL`: `python3 tools/audit/archscore/score.py --diff origin/main`.
- `RESULT disagreeing_cases=0 of 4`: the `_freq_view` payment's null control, a scratch probe at
  `~/hpo-seats/r10s3/r10-freq-defrost/probe_configured.py` over (neither, number only, sensor only, both), run under
  `PYTHONPATH=tests/hastub python3 -I`; it would print a non-zero count if `_freq_mode`'s "unconfigured" and
  `resolve_reading`'s None source ever disagreed.
- `ALL 4261 FEATURE CHECKS PASSED` and `MODE: SCOPED -- 27 script(s) run`: `GATE_SCOPE=auto GOLDEN_MODE=drift
  GATE_JOBS=3 ./tests/run.sh` at `2f8071ef5` (keyed on the mode line, not the count; the gate's own failures are under
  Red checks).
- `ALL 4262 FEATURE CHECKS PASSED`: `PYTHONPATH=tests/hastub python3 tests/features.py` at this head, with the bound
  check added.
- `PIN KILLED: 0 pinned, 2 left unpinned (2 survived)`: `PYTHONPATH=tests/hastub python3 tests/mutation_table.py
  --pin-killed --base origin/main` at `f8c523f0` (18 drivers in play; the comment-only null control survived each).
- `MUTATION TABLE PASSED`, `PIN RE-VERIFICATION: 4 reproduced, 0 not reproduced`, `0 survivor(s) of 4 evaluated = 0.0%,
  cap 20.0%`: `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --scope changed --base origin/main` at this head.
- `ALL 2360 ENTITY CHECKS PASSED`: `PYTHONPATH=tests/hastub python3 tests/entities.py` at this head, after the stale
  ledger row was deleted.
- `1 of 84 OPTIMALITY CHECKS FAILED`, the same check, at the baseline export: `PYTHONPATH=tests/hastub python3
  tests/optimality.py`.
- `8 of 110 STRESS CHECKS FAILED` at the same export, including `shoulder: cheaper than holding the setpoint
  [4.67 vs 3.96]`: `PYTHONPATH=tests/hastub python3 tests/stress.py`. Seven name `origin/main` unresolvable (the export
  has no `.git`, so the solver-work baseline cannot be captured); the eighth is the shoulder check the head also fails,
  with the same numbers. My own run printed a ninth, a memory-record reading (`RSS 3.50 MiB vs recorded 13.70 MiB`) that
  did not reproduce on the reviewer's re-run of the same export; it is not claimed.
- The registry row for `defrost_standoff` passes (`PYTHONPATH=tests/hastub python3 tests/entities.py`). What its shape
  pins is a decision-context read of `*.defrosting`: direct, `bool(...)`, `not` and walrus all hit, as the reviewer
  planted each at `de28f656`. A copy to a local first (`d = signals.defrosting; if d:`) is **not** matched (0 hits on
  the same plant), so the barrier's boundary is named here: it pins the flag's read, not a local derived from it. The
  one other read the rule returns is dispositioned at
  `coordinator.py::HeatPumpOptimizerCoordinator._learning_frozen`, the plant-wide gate that owns the reason string every
  learner is frozen with and which the map deliberately ignores for external heat (#781).

## Architecture score

`dS +0.0000 NULL`, no gate metric rose: `python3 tools/audit/archscore/score.py --diff origin/main`. The first cut read
`coord_footprint 2498 -> 2499` from a `known` local; the payment that replaced it is the view's one `source is not None`
test, which moves no logic statement.

## Unpinned sites

`tools/pr/ci_predict.py --base origin/main` at this head names one key,
`custom_components/heatpump_optimizer/coordinator.py:10563 CMP_BOUND*2`. The diff's three other added sites were pinned by
the bot's `ci: pin killed mutants` at `f8c523f0`, and `mutation_table` re-verified all four here.

- `custom_components/heatpump_optimizer/coordinator.py:10563 CMP_BOUND*2` (`> 0.05` -> `>= 0.05`, `reported >= hz_min` ->
  `>`): killed by a value check. Both variants survived every driver in play before it existed (Red checks), so
  `tests/features.py` gained `the watchdog's two bounds: the floor is exclusive, the minimum inclusive`, which feeds
  0.05 kW and a reading exactly at the entity's minimum; each variant alone fails it (Mutation proof), and the pin is
  `tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._observe_frequency.CMP_BOUND.e2a6e890.json`.
- The three the bot pinned at `f8c523f0`, each killed by `tests/features.py`: `coordinator.py:10555 GUARD_OFF`, the mode
  guard — with it off the watchdog never runs and `persistent divergence stands control down to latch` fails;
  `coordinator.py:10658 GUARD_OFF`, the view's configured guard — with it off a configured view loses `source` and the
  configured-view checks fail, three in the bot's row; and `freq_control.py:78 RETURN_DEL` — the predicate returns None,
  which is not a defrost, and `a defrost interval never teaches the frequency map` fails.

## Red checks

The scoped gate at `2f8071ef5` ends `4 TEST SCRIPT(S) FAILED`; two of the four reds are this branch's and were repaired.
CI's required `mutation` ran red at the PR heads `de28f656` and `f8c523f0` and is answered first below; it passes at
this head (Figures).

- `mutation` (required), red at the PR head `f8c523f0`: `4123 unpinned site(s) against 4126 at the ratchet base
  f639f3b0d, 2 of them added by this diff`, with one survivor-rate breach beside it (`25.0% of mutants survived against a
  cap of 20.0%`). Both additions are the two variants of `coordinator.py:10563 CMP_BOUND*2`.
  `mutation_table --pin-killed` measured both surviving every driver in play (`PIN KILLED: 0 pinned, 2 left unpinned
  (2 survived)`, 18 drivers, comment-only null control surviving each), so this branch adds their killer rather than a
  triage: one check that feeds each bound its exact input, and each variant alone fails it (Mutation proof). Both are
  recorded under `tests/mutation_ledger/killed_by/`, and the refusal and the rate both clear at this head. Cheaper
  detector for the red itself: `tools/pr/ci_predict.py --base origin/main` is source-only and prepr step 6d runs it; the
  pin drive is the instrument for the verdict.

- `tests/optimality.py`, `1 of 84 OPTIMALITY CHECKS FAILED` on `one|summer_negative|shoulder: a recorded claim still
  has a gap`. Not this branch: `_CERT_CLAIMS`' own comment in the script records it as an arm64-only reading (the seat's
  platform reaches the basin at 0.0000 %, CI's linux lane measures ladder +10.55 %, and the gate's platform is the one
  that counts). The baseline export prints the same failure (Figures). Cheaper detector: none; the check is the gate,
  and the comment already names the divergence.
- `tests/stress.py`, `1 of 113 STRESS CHECKS FAILED` on `shoulder: cheaper than holding the setpoint [4.67 vs 3.96]`.
  The baseline export prints the same check with the same numbers (Figures), so it is `main`'s on this platform, not this
  branch's: the diff changes no solver line and the frequency stage never feeds the optimizer (the module's own
  docstring: the map is evidence, not a controller). Cheaper detector: none; this check is the gate that sees it, and
  the red is the solver's platform bias, not a branch regression.
- `tests/entities.py`, `1 of 2360 ENTITY CHECKS FAILED`: the `--anchor` self-test refused the stale mutation-ledger pin
  the rewritten `watch_active` line left. Cheaper detector: `tools/pr/ci_predict.py --base origin/main`, which names the
  same pin in about a minute and already runs in `body_push.sh`'s gate — run earlier it catches this before the 90-minute
  gate. Standing cost: already paid; the countermeasure is the instrument that exists, used before the push. Repaired by
  deleting the stale row in this branch and re-running the script (Figures).
- `tests/structure.py`, `3 STRUCTURE BUDGET(S) IMPROVED AND NOT YET RECORDED`: the ratchet refuses an improvement it has
  not recorded. The cheaper detector is the same script run locally, which is what the fixer contract already names; the
  miss was mine, reading its output past the improvement block. Re-recorded in this branch, reason in the commit.
  Nothing cheaper exists, so no countermeasure is owed.

## Forward-carry

- The `pump_offline` arm of D7-s2-01: `_freq_fold_blocked` does not refuse a freeze reason of `pump_offline`, so an
  install whose online flag reads False while its frequency entity still reports a number folds that interval. Same
  seam and same class as this fix, outside this group's stated scope (defrost), measured at the head by the harness's
  `pump_offline` row (`freq_map` = INGEST). A later group's carry lands in
  `dev/programme/rosters/wave-r10-groups.json`; the orchestrator assigns that group, and `#2238` is the open record on
  the Delivery-status table until it does. Carry: #2238

## Friction

`none`
