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

`0be6047ca`, branched from `origin/main` `4e5801eb5064`; every figure below is taken at this head unless a line says
another one. The evidence head is `2f8071ef5`: the two commits above it delete the stale mutation-ledger row and record
the structure budgets, so every production line those figures measured is identical here.

Prepr's closures recordings were skipped (`PREPR_SKIP_CLOSURES=1`) under the coordinator's owner ruling for the rest of
this wave: CI's required `closures` context re-records them and `closures-autofix` repairs an UNDER-SCOPED result, while
the local re-record was the wave's bottleneck. Every other prepr step ran and passed.

## Mutation proof

The mutant deletes the two production terms the fix adds — `not defrosting` from `watch_active` and `or defrosting` from
the map's fold guard — in the working tree, then runs the closure's `tests/features.py` and restores. The run ends
`EXIT=1`:

```
  FAIL a defrost interval never teaches the frequency map  [the fold would learn a ratio that is not a kW-per-Hz point, and the decile-keyed map is inherited when the user later switches to control]
  FAIL defrost ticks never stand control down  [a defrost is not a write path that stopped listening]

2 of 4261 FEATURE CHECKS FAILED
```

The third added check is the null control and stays green under the mutant: `null control: a non-defrost interval still
folds`. `git status --short` after the restore prints nothing, so the measured tree is the committed head.

## Null control

The unmodified tree, the finder's harness, the same 8 intervals (baseline `git archive` of `origin/main`
`4e5801eb5064`): `freq_map_clean_folds=8`, `freq_map_defrost_folds=8`. At the head the clean arm still reads 8 and the
defrost arm reads 0. `tests/features.py` carries the same arms as checks: a `defrosting=False` interval folds, and
without the fix the divergent defrost arm trips the watchdog.

The harness's `--perturb` arm (patch `_freq_fold_blocked` to refuse defrost) no longer separates at the head: the fold
reads the predicate before the gate, so 8 -> 0 -> 0. That is the route the fix took, named here because the harness's
reported text did not move. The control that separates at the head is the clean arm against the defrost arm. Its
learner table's `freq_map` column still reads INGEST on the defrost row for the same reason: the column asks
`_freq_fold_blocked` alone, which this diff deliberately leaves unchanged.

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
- `ALL 2360 ENTITY CHECKS PASSED`: `PYTHONPATH=tests/hastub python3 tests/entities.py` at this head, after the stale
  ledger row was deleted.
- `1 of 84 OPTIMALITY CHECKS FAILED`, the same check, at the baseline export: `PYTHONPATH=tests/hastub python3
  tests/optimality.py`.
- `9 of 110 STRESS CHECKS FAILED` at the same export, including `shoulder: cheaper than holding the setpoint
  [4.67 vs 3.96]`: `PYTHONPATH=tests/hastub python3 tests/stress.py`. Eight of the nine are the export having no `.git`
  (seven name `origin/main` unresolvable for the solver-work baseline, one the memory record); the ninth is the shoulder
  check the head also fails, with the same numbers.
- `P2 owners: defrost_standoff is decided only by its owner or a dispositioned site, its owner exists, no disposition
  is stale, the rule is live`: `PYTHONPATH=tests/hastub python3 tests/entities.py`. The fact's one other
  decision-context read of the flag is dispositioned at
  `coordinator.py::HeatPumpOptimizerCoordinator._learning_frozen`, the plant-wide gate that owns the reason string every
  learner is frozen with and which the map deliberately ignores for external heat (#781).

## Architecture score

`dS +0.0000 NULL`, no gate metric rose: `python3 tools/audit/archscore/score.py --diff origin/main`. The first cut read
`coord_footprint 2498 -> 2499` from a `known` local; the payment that replaced it is the view's one `source is not None`
test, which moves no logic statement.

## Unpinned sites

`tools/pr/ci_predict.py --base origin/main` names four sites the diff adds; the lane pins the three a driver kills.

- `custom_components/heatpump_optimizer/coordinator.py:10555 GUARD_OFF` on `if self._freq_mode() == FREQ_MODE_CONTROL:` —
  pinned by `mutation-autofix`: with the guard off the watchdog never runs, and `persistent divergence stands control
  down to latch` fails.
- `custom_components/heatpump_optimizer/coordinator.py:10679 GUARD_OFF` on `if source is not None:` (the view's
  `source` key) — pinned by `mutation-autofix`: with it off the unconfigured view gains `source: None`, and `an
  unconfigured view gains no key, so the published unconfigured dict is unchanged` fails.
- `custom_components/heatpump_optimizer/freq_control.py:78 RETURN_DEL` on `return bool(defrosting)` — pinned by
  `mutation-autofix`: the predicate then returns None, which is not a defrost, and `a defrost interval never teaches the
  frequency map` fails (Mutation proof).
- `custom_components/heatpump_optimizer/coordinator.py:10563 CMP_BOUND*2` (`> 0.05` -> `>= 0.05`, `reported >= hz_min` ->
  `>`): triaged, not pinned. Both flips move the verdict only for an interval exactly on a bound, and the three checks
  that drive this line feed it 0.0 and 2.0 kW and 10, 45 and 90 Hz against a 20 Hz minimum (`tests/features.py`,
  `_p8s_watch`'s idle and below-range arms and the defrost arms); none sits on a bound. The added `not defrosting` term
  is killed by the defrost check (Mutation proof), and the lane would pin the flips if any driver separated them.

## Red checks

The scoped gate at `2f8071ef5` ends `4 TEST SCRIPT(S) FAILED`; the two commits after it are the repairs, and two of the
four reds are this branch's. No check is expected to be red in CI at this head.

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
